"""Write local executable paths only. Never inspect authentication storage."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from settings import data_dir


def configure(node):
    vendor = ROOT / "node_modules/@openai"
    candidates = list(vendor.glob("codex*/vendor/*/bin/codex.exe"))
    if not candidates:
        raise RuntimeError("Codex Windows binary missing; check npm optional dependencies and CPU support.")
    python = ROOT / ".venv/Scripts/pythonw.exe"
    if not python.is_file():
        raise RuntimeError("Run setup.ps1 to create the Python environment.")
    config = {"root": str(ROOT), "python_path": str(python),
              "node_path": str(Path(node).resolve()), "codex_path": str(candidates[0].resolve())}
    base = data_dir()
    base.mkdir(parents=True, exist_ok=True)
    (base / "settings.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    print("Local backend configuration saved (no credentials).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--node", required=True)
    configure(parser.parse_args().node)
