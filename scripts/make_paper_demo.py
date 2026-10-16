"""Export genuine, already-generated Green et al. pages; never invent translations.

Run after backend/layout_reader.py has translated source pages 1,4,7.
Only pages 1 and 4 are redistributed: no third-party map basemaps.
"""
import argparse
import hashlib
import json
from pathlib import Path

import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA256 = 'a3d298713e944f645a2d357e16e70cb617f132e97a791a6b4cc96813976fd375'


def main(layout):
    manifest = json.loads((layout / 'manifest.json').read_text(encoding='utf-8'))
    qa = json.loads((layout / 'layout-qa.json').read_text(encoding='utf-8'))
    if manifest['sha256'] != SOURCE_SHA256:
        raise ValueError('This exporter is only licensed/documented for the specified paper.')
    if qa['render_failed_pages'] or not {1, 4}.issubset(manifest['completed_pages']):
        raise ValueError('Generate and inspect pages 1 and 4 before exporting.')
    assets = ROOT / 'docs/assets'
    with fitz.open(layout / '原版式中英对照.pdf') as source:
        out = fitz.open()
        for page in (1, 4):
            index = manifest['requested_pages'].index(page)
            out.insert_pdf(source, from_page=index, to_page=index)
        out.set_toc([[1, 'Green et al. (2017), source page 1', 1],
                     [1, 'Green et al. (2017), source page 4 / Figure 2', 2]])
        out.set_metadata({
            'title': 'Green et al. (2017) - actual bilingual output, pages 1 and 4',
            'author': 'Green et al.; AI Chinese translation by Zotero Bilingual Reader',
            'subject': 'Source: https://doi.org/10.5194/nhess-17-1-2017; CC BY 3.0. '
                       'Modified: AI Chinese translation and side-by-side layout. Not endorsed by authors.',
        })
        target = assets / 'paper-bilingual-sample.pdf'
        out.save(target, garbage=4, deflate=True)
        page = out[1]
        page.get_pixmap(matrix=fitz.Matrix(2, 2)).save(assets / 'paper-page-04.png')
        # Identical corresponding page areas, taken from this output PDF.
        # Source Figure 2 sits in the top-right column of original page 4.
        w = (page.rect.width - 14) / 2
        clips = [fitz.Rect(300, 88, w-20, 302),
                 fitz.Rect(w+14+300, 88, 2*w+14-20, 302)]
        from PIL import Image
        pictures = []
        for clip in clips:
            pix = page.get_pixmap(clip=clip, matrix=fitz.Matrix(3, 3))
            pictures.append(Image.frombytes('RGB', (pix.width, pix.height), pix.samples))
        paired = Image.new('RGB', (sum(p.width for p in pictures)+24, max(p.height for p in pictures)), 'white')
        paired.paste(pictures[0], (0, 0)); paired.paste(pictures[1], (pictures[0].width+24, 0))
        paired.save(assets / 'paper-figure-02.png')
        out.close()
    print('Exported actual pages and figure crop; SHA256:', hashlib.sha256(target.read_bytes()).hexdigest())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--layout', type=Path, required=True)
    main(parser.parse_args().layout)
