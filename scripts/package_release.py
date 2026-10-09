"""Release ZIP contains only the reviewed public allowlist; no working directories."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_STORED

from build import build, public_bytes
from privacy_check import ROOT, public_files, main as check_privacy


def main():
    if check_privacy():
        raise SystemExit("Privacy checks failed")
    xpi = build()
    version = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))["version"]
    source = ROOT / "dist" / f"zotero-bilingual-reader-{version}-source.zip"
    with ZipFile(source, "w", compression=ZIP_STORED) as archive:
        for member in public_files():
            info = ZipInfo(member, (2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_STORED
            info.external_attr = 0o644 << 16
            archive.writestr(info, public_bytes(ROOT / member))
    sums = "".join(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}\n" for path in (xpi, source))
    (ROOT / "dist/SHA256SUMS.txt").write_text(sums, encoding="ascii")
    print(f"Packaged {source.name} from {len(public_files())} allowlisted files")


if __name__ == "__main__":
    main()
