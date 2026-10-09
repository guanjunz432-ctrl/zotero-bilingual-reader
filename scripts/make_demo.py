"""Self-authored synthetic fixture; prepared translations test layout, not AI quality."""
import json
import sys
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))
from layout_reader import extract_geometry, write_aligned_pdf
from bilingual_reader import save_json


def main():
    assets = ROOT / "docs/assets"
    assets.mkdir(parents=True, exist_ok=True)
    work = ROOT / "dist/demo-work"
    work.mkdir(parents=True, exist_ok=True)
    source = assets / "synthetic-example.pdf"
    doc = fitz.open()
    page = doc.new_page(width=595, height=620)
    items = [
        ("Bilingual reading, in context", "在原文语境中进行双语阅读", (42, 55), 23),
        ("SYNTHETIC EXAMPLE / NOT RESEARCH DATA", "自制示例 / 非科研数据", (42, 83), 10),
        ("Abstract", "摘要", (42, 124), 15),
        ("This demonstration keeps the English page beside a Chinese layout.\nThe example is self-authored and contains no personal library data.",
         "本演示将英文原页与中文排版并列展示。\n示例为自行编写，不包含任何个人文献库数据。", (42, 150), 11),
        ("Figure labels are part of reading", "图中文字也是阅读的一部分", (42, 212), 15),
        ("Figure 1. A synthetic curve illustrates label placement only.\nThe numbers do not represent an experiment or a scientific result.",
         "图 1. 自制曲线仅用于演示图中文字的排版位置。\n图中数字不代表实验数据或科研结果。", (42, 476), 11),
        ("Review before reuse", "使用前请核对", (42, 539), 15),
        ("Prepared translations demonstrate typesetting, not model accuracy.\nCheck formulas, values and label masks against the source page.",
         "预置译文用于演示排版，不代表模型准确率。\n请对照原页核对公式、数值与图中文字的覆盖位置。", (42, 565), 11),
    ]
    for en, zh, xy, size in items:
        page.insert_text(xy, en, fontsize=size, fontname="helv", color=(.10, .18, .24))
    figure = fitz.open()
    chart = figure.new_page(width=495, height=220)
    chart.draw_rect(chart.rect, fill=(.95,.97,.98), color=None)
    chart.draw_line((55,175),(455,175),color=(.3,.4,.5))
    chart.draw_line((55,175),(55,25),color=(.3,.4,.5))
    chart.draw_polyline([(55,150),(125,132),(195,145),(265,96),(335,74),(405,40)],color=(.07,.46,.54),width=2)
    chart.insert_text((18,19),"Response",fontsize=11)
    chart.insert_text((215,203),"Time (days)",fontsize=11)
    chart.insert_text((335,145),"Example curve",fontsize=11)
    for x, value in ((55,"0"),(195,"2"),(335,"4")):
        chart.insert_text((x,189),value,fontsize=9)
    target = fitz.Rect(50,236,545,456)
    page.insert_image(target, stream=chart.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes("png"))
    geometry = extract_geometry(page)
    mapping = {en.replace("\n", " "): zh for en, zh, xy, size in items}
    translated = []
    for region in geometry["regions"]:
        text = region["en"].replace("\n", " ")
        translated.append({"id": region["id"], "zh": mapping[text]})
    raster = []
    labels = {"Response": "响应", "Time (days)": "时间（天）", "Example curve": "示例曲线"}
    for block in chart.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["text"] not in labels:
                    continue
                box = fitz.Rect(span["bbox"]) + (50,236,50,236)
                raster.append({"en":span["text"],"zh":labels[span["text"]],
                    "bbox":[box.x0/595*1000,box.y0/620*1000,box.x1/595*1000,box.y1/620*1000],
                    "color":"#000000","bgcolor":"#f2f7fa","angle":0,"lines":1})
    doc.set_metadata({"title":"Synthetic bilingual reading example", "author":"Zotero Bilingual Reader contributors"})
    doc.save(source)
    doc.close()
    figure.close()
    save_json(work / "page-0001.json", {"geometry":geometry,"translations":translated,"raster":raster})
    manifest={"source_path":str(source),"source_name":"Synthetic example", "requested_pages":[1],"completed_pages":[1],"total_pages":1}
    result=write_aligned_pdf(work,manifest,output_path=assets/"synthetic-bilingual.pdf")
    with fitz.open(result) as output:
        output[0].get_pixmap(matrix=fitz.Matrix(1.35,1.35)).save(assets/"demo.png")
        assert "在原文语境" in output[0].get_text()
    print("Synthetic fixture and prepared-translation layout demo built.")


if __name__ == "__main__":
    main()
