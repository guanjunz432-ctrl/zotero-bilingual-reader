"""Delegate login to the official CLI, without reading or copying any token."""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from settings import cloud_environment, load_settings, data_dir

parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--status", action="store_true")
group.add_argument("--logout", action="store_true")
args = parser.parse_args()
settings = load_settings()
command = [settings["codex_path"], "logout" if args.logout else "login"]
if args.status:
    command.append("status")
env = cloud_environment(settings)
env.pop("NO_BROWSER", None)
raise SystemExit(subprocess.call(command, env=env, cwd=data_dir()))
