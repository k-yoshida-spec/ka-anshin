"""PPの本文とノートを抽出して JSON にする（差分の基準）。
  python3 tools/ppt_extract.py <資料.pptx> [出力.json]   出力省略時は標準出力
"""
import json, sys, pathlib
from pptx import Presentation
from pptx.util import Emu

def shape_texts(sh):
    out = []
    if sh.shape_type == 6 and hasattr(sh, 'shapes'):          # グループ
        for s in sh.shapes: out += shape_texts(s)
    if getattr(sh, 'has_table', False) and sh.has_table:
        for row in sh.table.rows:
            cells = [c.text.strip().replace('\n', ' ') for c in row.cells]
            if any(cells): out.append(' | '.join(cells))
    if getattr(sh, 'has_text_frame', False) and sh.has_text_frame:
        for p in sh.text_frame.paragraphs:
            t = p.text.replace('\v', ' ').strip()
            if t: out.append(t)
    return out

def extract(path):
    prs = Presentation(path)
    slides = []
    for i, s in enumerate(prs.slides, 1):
        shapes = sorted(s.shapes, key=lambda x: ((x.top or Emu(0)), (x.left or Emu(0))))
        texts = []
        for sh in shapes: texts += shape_texts(sh)
        notes = []
        if s.has_notes_slide:
            notes = [l.strip() for l in s.notes_slide.notes_text_frame.text.splitlines() if l.strip()]
        slides.append({'no': i, 'title': texts[0] if texts else '', 'texts': texts, 'notes': notes})
    return {'file': pathlib.Path(path).name, 'slides': slides}

if __name__ == '__main__':
    d = extract(sys.argv[1])
    s = json.dumps(d, ensure_ascii=False, indent=1)
    if len(sys.argv) > 2: pathlib.Path(sys.argv[2]).write_text(s + '\n', encoding='utf-8'); print(f"{len(d['slides'])}枚を抽出 → {sys.argv[2]}")
    else: print(s)
