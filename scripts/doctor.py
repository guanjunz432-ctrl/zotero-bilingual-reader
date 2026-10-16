"""Shareable diagnostics: booleans and versions, never paths, titles or accounts."""
import importlib.metadata
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from settings import load_settings, font_directory


def main():
    checks = {}
    try:
        config = load_settings()
        for key in ("node_path", "python_path", "codex_path"):
            checks[key + "_exists"] = Path(config[key]).is_file()
    except (ValueError, OSError, KeyError, RuntimeError):
        checks["configured"] = False
    for name in ("simsun.ttc", "arial.ttf", "seguisym.ttf"):
        checks["font_" + name] = (font_directory() / name).is_file()
    for package in ("PyMuPDF", "reportlab", "pillow"):
        try:
            checks[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            checks[package] = False
    print(json.dumps(checks, indent=2))
    return int(any(value is False for value in checks.values()))


if __name__ == "__main__":
    raise SystemExit(main())
