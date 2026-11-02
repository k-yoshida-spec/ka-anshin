"""サイトの文章（content/a.json）の「変更前 → 変更後」一覧を Markdown 表で出す（PR本文・薫さんの確認用）。
  python3 tools/content_diff.py [比較元 git ref、既定 origin/main]
"""
import json, sys, subprocess, pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
ref = sys.argv[1] if len(sys.argv) > 1 else 'origin/main'
old = json.loads(subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:content/a.json'], capture_output=True, check=True).stdout.decode('utf-8'))
new = json.loads((ROOT / 'content/a.json').read_text(encoding='utf-8'))
cut = lambda s, n=140: (s if len(s) <= n else s[:n] + '…').replace('|', '／').replace('\n', ' ')
rows = [(k, old.get(k), new.get(k)) for k in list(new) + [k for k in old if k not in new] if old.get(k) != new.get(k)]
if rows:
    print(f'文章の変更：{len(rows)}か所\n\n| 場所（キー） | 変更前 | 変更後 |\n|---|---|---|')
    for k, o, n in rows: print(f"| `{k}` | {cut(o) if o is not None else '（追加）'} | {cut(n) if n is not None else '（削除）'} |")
else:
    print('文章（content/a.json）の変更なし')

# 文章データ以外（料金の金額・リンク・レイアウト）は src/template.html にある。変わった行も出す。
import difflib, re
ot = subprocess.run(['git', '-C', str(ROOT), 'show', f'{ref}:src/template.html'], capture_output=True, check=True).stdout.decode('utf-8').splitlines()
nt = (ROOT / 'src/template.html').read_text(encoding='utf-8').splitlines()
d = [l for l in difflib.unified_diff(ot, nt, lineterm='', n=0) if l[:1] in '+-' and l[:3] not in ('+++', '---')]
if d:
    print(f'\nテンプレート（金額・リンク・レイアウト等）の変更：{len(d)}行\n\n```diff')
    for l in d[:60]: print(l[:200])
    print('```')

