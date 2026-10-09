"""Transport and shared helpers. Cloud inference; no local model weights."""
from __future__ import annotations

import hashlib
import json
import queue
import re
import subprocess
import threading
import time
from pathlib import Path

from settings import ROOT, VERSION, cloud_environment, data_dir, load_settings

NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)


class TranslationFormatError(ValueError):
    """A cloud response failed the structural completeness checks."""


def save_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def output_folder(pdf, output_base=None):
    pdf = Path(pdf).resolve()
    with pdf.open("rb") as handle:
        digest = hashlib.file_digest(handle, "sha256").hexdigest()
    # Hash-only cache names avoid exposing paper titles in diagnostic paths.
    return (Path(output_base) if output_base else data_dir() / "outputs") / digest[:24]


def page_list(spec, total):
    if not spec.strip():
        return list(range(1, total + 1))
    if not re.fullmatch(r"\s*\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*\s*", spec):
        raise ValueError("页码格式应为 1-2 或 1,3-5。")
    pages = set()
    for part in spec.split(","):
        values = [int(v) for v in part.split("-")]
        a, b = (values[0], values[-1])
        if not 1 <= a <= b <= total:
            raise ValueError(f"页码须在 1-{total} 之间，范围不能倒序。")
        pages.update(range(a, b + 1))
    return sorted(pages)


class ACP:
    def __init__(self, cwd):
        settings = load_settings()
        self.process = subprocess.Popen(
            [settings["node_path"], str(ROOT / "node_modules/@agentclientprotocol/codex-acp/dist/index.js")],
            cwd=cwd, env=cloud_environment(settings), stdin=subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
            encoding="utf-8", creationflags=NO_WINDOW,
        )
        self.incoming, self.counter, self.parts = queue.Queue(), 0, []

        def read():
            try:
                for line in self.process.stdout:
                    if line.strip():
                        self.incoming.put(json.loads(line))
            except (ValueError, OSError):
                self.incoming.put({"transport_error": True})
            finally:
                self.incoming.put({"transport_error": True})

        def drain():
            for _ in self.process.stderr:
                pass  # Never store adapter diagnostics or account responses.

        threading.Thread(target=read, daemon=True).start()
        threading.Thread(target=drain, daemon=True).start()
        try:
            self.rpc("initialize", {"protocolVersion": 1, "clientCapabilities": {},
                     "clientInfo": {"name": "zotero-bilingual-reader", "version": VERSION}}, timeout=45)
        except Exception:
            self.close()
            raise

    def write(self, obj):
        self.process.stdin.write(json.dumps(obj, ensure_ascii=False) + "\n")
        self.process.stdin.flush()

    def rpc(self, method, params, timeout=600):
        self.counter += 1
        current = self.counter
        self.write({"jsonrpc": "2.0", "id": current, "method": method, "params": params})
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                obj = self.incoming.get(timeout=max(.1, deadline - time.monotonic()))
            except queue.Empty:
                raise TimeoutError("云端响应超时；已完成页面保留。") from None
            if "transport_error" in obj:
                raise RuntimeError("云端连接已结束；请检查登录、网络和后端安装。")
            if obj.get("method") == "session/update":
                update = obj.get("params", {}).get("update", {})
                if update.get("sessionUpdate") == "agent_message_chunk":
                    content = update.get("content", {})
                    if content.get("type") == "text":
                        self.parts.append(content.get("text", ""))
                if update.get("sessionUpdate") == "tool_call":
                    raise RuntimeError("翻译会话请求了工具，已中止。请报告此错误（无需附带文献或账号数据）。")
            if obj.get("method") and "id" in obj:
                if obj["method"] == "session/request_permission":
                    self.write({"jsonrpc": "2.0", "id": obj["id"], "result": {"outcome": {"outcome": "cancelled"}}})
                else:
                    self.write({"jsonrpc": "2.0", "id": obj["id"], "error": {
                        "code": -32601, "message": "Translation client denies tools and file access"}})
            if obj.get("id") == current and not obj.get("method"):
                if "error" in obj:
                    # Raw upstream errors may include user/account-specific details.
                    code = obj["error"].get("code", "unknown")
                    raise RuntimeError(f"云端请求未完成（代码 {code}）；请运行 login.ps1 检查登录及额度。")
                return obj["result"]
        raise TimeoutError("云端响应超时；已完成页面保留。")

    def close(self):
        if self.process.poll() is not None:
            return
        try:
            self.process.stdin.close()
            self.process.wait(timeout=8)
        except (OSError, subprocess.TimeoutExpired):
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
