"""Deterministic XPI: explicit member list, no runtime state or credentials."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED

ROOT = Path(__file__).resolve().parents[1]
MEMBERS = ("bootstrap.js", "bridge.js", "manifest.json", "LICENSE")


def public_bytes(path):
    if path.suffix in (".pdf", ".png"):
        return path.read_bytes()
    return path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").encode("utf-8")


def build():
    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    dist = ROOT / "dist"
    dist.mkdir(exist_ok=True)
    target = dist / f"zotero-bilingual-reader-{version}.xpi"
    # Stored entries avoid byte differences between zlib implementations.
    with ZipFile(target, "w", compression=ZIP_STORED) as archive:
        for member in MEMBERS:
            info = ZipInfo(member, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.external_attr = 0o644 << 16
            path = ROOT / member if member == "LICENSE" else ROOT / "addon" / member
            archive.writestr(info, public_bytes(path))
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    (dist / "SHA256SUMS.txt").write_text(f"{digest}  {target.name}\n", encoding="ascii")
    print(f"Built {target.name} ({len(MEMBERS)} allowlisted files)")
    return target


if __name__ == "__main__":
    build()
