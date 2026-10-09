"""Inspect exactly the public allowlist; report locations, never matching values."""
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "personal-home-path": re.compile(r"(?i)[a-z]:[\\/]+users[\\/]+[^\s\\/\"']+"),
    "openai-secret": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}"),
    "github-secret": re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{30,})"),
    "jwt": re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{15,}"),
    "private-key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "bearer-secret": re.compile(r"(?i)bearer\s+[A-Za-z0-9_.-]{24,}"),
    "assigned-credential": re.compile(r'''(?i)["']?(?:access_token|refresh_token|password|api_key)["']?\s*[:=]\s*["'][^"']{12,}["']'''),
}
BLOCKED = {"auth.json", ".env", "settings.json", "config.toml"}


def public_files():
    members = json.loads((ROOT / "release-files.json").read_text(encoding="utf-8"))
    if len(members) != len(set(members)):
        raise ValueError("Duplicate public member")
    for member in members:
        path = Path(member)
        if path.is_absolute() or ".." in path.parts or path.name in BLOCKED:
            raise ValueError("Unsafe public member")
        target = ROOT / path
        if target.is_symlink() or not target.is_file():
            raise ValueError("Missing or linked public member: " + member)
    return members


def inspect_text(text, name):
    return [f"{name}: {rule}" for rule, pattern in PATTERNS.items() if pattern.search(text)]


def main():
    members = public_files()
    failures = []
    for member in members:
        path = ROOT / member
        if path.suffix == ".pdf":
            import pymupdf
            with pymupdf.open(path) as pdf:
                text = json.dumps(pdf.metadata) + "\n" + "\n".join(page.get_text() for page in pdf)
        elif path.suffix == ".png":
            from PIL import Image
            with Image.open(path) as img:
                text = json.dumps(img.info)
        else:
            text = path.read_text(encoding="utf-8-sig")
        failures.extend(inspect_text(text, member))
    if (ROOT / ".git").exists():
        tracked = subprocess.check_output(["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0")
        extra = set(tracked) - set(members) - {""}
        failures.extend("Tracked outside public allowlist: " + p for p in sorted(extra))
    if failures:
        print("\n".join(failures))
        return 1
    print(f"PASS: {len(members)} allowlisted public files; no configured privacy patterns found.")
    print("Scope: source/PDF text/image metadata. Review image pixels and Git history separately.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
