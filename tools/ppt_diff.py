"""前回反映したPP（ppt/last.json）と新しいPPの差分を、スライドごとに Markdown で出す。
  python3 tools/ppt_diff.py ppt/last.json <新しい.json>
"""
import json, sys, difflib
a = json.load(open(sys.argv[1], encoding='utf-8')); b = json.load(open(sys.argv[2], encoding='utf-8'))
A = {s['no']: s for s in a['slides']}; B = {s['no']: s for s in b['slides']}
out = []
for no in sorted(set(A) | set(B)):
    sa, sb = A.get(no), B.get(no)
    if not sa: out.append(f"### スライド{no}（追加）「{sb['title']}」\n" + '\n'.join('+ ' + t for t in sb['texts'] + sb['notes'])); continue
    if not sb: out.append(f"### スライド{no}（削除）「{sa['title']}」"); continue
    lines = []
    for part, la, lb in (('本文', sa['texts'], sb['texts']), ('ノート', sa['notes'], sb['notes'])):
        d = [l for l in difflib.ndiff(la, lb) if l[:2] in ('- ', '+ ')]
        if d: lines.append(f"**{part}**\n" + '\n'.join(d))
    if lines: out.append(f"### スライド{no}「{sb['title']}」\n" + '\n\n'.join(lines))
print('\n\n'.join(out) if out else '変更なし（前回反映したPPと本文・ノートが同じです）')
