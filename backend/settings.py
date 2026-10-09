"""Application paths and restrictive, isolated Codex configuration (no credentials)."""
from __future__ import annotations

import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.1.0-beta.1"


def data_dir():
    base = os.environ.get("ZBR_DATA_DIR")
    return Path(base) if base else Path(os.environ.get("LOCALAPPDATA", Path.home() / ".local/share")) / "ZoteroBilingualReader"


def load_settings():
    path = data_dir() / "settings.json"
    if not path.exists():
        raise RuntimeError("请先运行 setup.ps1 完成后端安装，然后运行 login.ps1 登录。")
    return json.loads(path.read_text(encoding="utf-8-sig"))


SAFE_CONFIG = {
    "sandbox_mode": "read-only",
    "approval_policy": "untrusted",
    "web_search": "disabled",
    "mcp_servers": {},
    "project_doc_max_bytes": 0,
    "features": {
        "shell_tool": False, "unified_exec": False,
        "apply_patch_freeform": False, "multi_agent": False,
        "apps": False, "remote_plugin": False, "hooks": False,
        "memories": False, "shell_snapshot": False,
    },
}


def cloud_environment(settings):
    # Do not pass API keys, inherited model-provider overrides or logging options.
    allowed = {"path", "systemroot", "windir", "temp", "tmp", "userprofile",
               "appdata", "localappdata", "programfiles", "programfiles(x86)",
               "comspec", "home", "https_proxy", "http_proxy", "no_proxy"}
    env = {k: v for k, v in os.environ.items() if k.lower() in allowed}
    profile = data_dir() / "codex-profile"
    profile.mkdir(parents=True, exist_ok=True)
    env.update(CODEX_HOME=str(profile), INITIAL_AGENT_MODE="read-only",
               NO_BROWSER="1", CODEX_CONFIG=json.dumps(SAFE_CONFIG))
    # The dedicated official CLI owns login and token refresh. This application
    # never opens, copies, exports or parses its authentication storage.
    env["CODEX_PATH"] = settings["codex_path"]
    return env


def font_directory():
    return Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts"
