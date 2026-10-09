import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bilingual_reader import page_list, output_folder, TranslationFormatError
from layout_reader import parse_layout
from settings import cloud_environment, SAFE_CONFIG
import pymupdf as fitz
from layout_reader import raster_text_bounds


class PublicBackendTests(unittest.TestCase):
    def test_short_ocr_box_expands_to_complete_word_without_axis(self):
        chart=fitz.open();p=chart.new_page(width=200,height=100)
        p.insert_text((20,25),'Response',fontsize=11)
        p.draw_line((20,40),(170,40),color=(0,0,0))
        raster=fitz.open();page=raster.new_page(width=200,height=100)
        page.insert_image(page.rect,stream=p.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes('png'))
        box=fitz.Rect(20,16,57,27)
        result=raster_text_bounds(box,{'color':'#000000','bgcolor':'#ffffff'},page)
        self.assertGreater(result.x1,62)
        self.assertLess(result.y1,35)
        raster.close();chart.close()

    def test_page_ranges_are_bounded_before_expansion(self):
        self.assertEqual(page_list("1,3-4", 4), [1, 3, 4])
        for spec in ("0", "3-1", "1-999999999", "1,x", "1,"):
            with self.assertRaises(ValueError):
                page_list(spec, 4)

    def test_environment_drops_credentials_and_provider_overrides(self):
        with tempfile.TemporaryDirectory() as tmp, patch.dict(os.environ, {
            "ZBR_DATA_DIR": tmp, "OPENAI_API_KEY": "dummy",
            "GITHUB_TOKEN": "dummy", "CODEX_CONFIG": '{"danger":true}',
            "CODEX_HOME": "unrelated-profile", "APP_SERVER_LOGS": "unrelated-logs",
        }):
            env = cloud_environment({"codex_path": "codex-test.exe"})
            for key in ("OPENAI_API_KEY", "GITHUB_TOKEN", "APP_SERVER_LOGS"):
                self.assertNotIn(key, env)
            self.assertEqual(env["CODEX_HOME"], str(Path(tmp) / "codex-profile"))
            self.assertEqual(json.loads(env["CODEX_CONFIG"]), SAFE_CONFIG)
            self.assertEqual(env["INITIAL_AGENT_MODE"], "read-only")

    def test_cache_name_does_not_include_source_title(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "private-title.pdf"
            source.write_bytes(b"synthetic fixture")
            self.assertNotIn("private-title", output_folder(source).name)

    def test_layout_rejects_missing_ids_duplicate_ids_and_bad_geometry(self):
        geometry = {"regions": [{"id": "t1"}]}
        good = {"page": 1, "translations": [{"id": "t1", "zh": "示例"}], "raster": []}
        self.assertEqual(parse_layout(json.dumps(good), 1, geometry), good)
        missing = copy.deepcopy(good)
        missing["translations"] = []
        duplicate = copy.deepcopy(good)
        duplicate["translations"] *= 2
        bounds = copy.deepcopy(good)
        bounds["raster"] = [{"en": "Example", "zh": "示例", "bbox": [0, 0, 1001, 10]}]
        for data in (missing, duplicate, bounds):
            with self.assertRaises(TranslationFormatError):
                parse_layout(json.dumps(data), 1, geometry)


if __name__ == "__main__":
    unittest.main()
