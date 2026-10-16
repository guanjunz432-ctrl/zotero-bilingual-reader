"""Transport and shared helpers. Cloud inference; no local model weights."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from settings import ROOT, data_dir



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
