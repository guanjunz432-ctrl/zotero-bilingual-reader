"""Run Python tests with the backend import path, without cloud access."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), pattern="test_*.py")
raise SystemExit(not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful())
