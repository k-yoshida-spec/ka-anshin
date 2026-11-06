"""LPの一覧（ka-lp の catalog.json）から、Aページ用の写し content/lps.json を作る。
  python3 tools/sync_lps.py [../ka-lp/catalog.json]
content/ の変更なので、反映には更新リスト＋承認が必要（check_update_record.py）。
Aページのカードは、この写しをもとに行き先を決め、写しにあって A に無いサービスはカードを自動で足す。
"""
import json, pathlib, sys
ROOT = pathlib.Path(__file__).resolve().parent.parent
src = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ROOT.parent / 'ka-lp' / 'catalog.json')
cat = json.loads(src.read_text(encoding='utf-8'))
out = []
for x in cat['lps']:
    out.append({'name': x['name'], 'no': x['no'], 'stage': x['stage'], 'title': x['title'], 'text': x['text'],
                'catch': x.get('catch', ''), 'chara': x.get('image', 'owl-full.webp').split('-')[0],
                'for': x.get('for', []), 'url': cat['url_pattern'].format(name=x['name']), 'published': bool(x.get('published'))})
p = ROOT / 'content' / 'lps.json'
p.write_text(json.dumps(out, ensure_ascii=False, indent=1) + '\n', encoding='utf-8')
print(f'{len(out)}件 → {p.relative_to(ROOT)}（公開済み {sum(o["published"] for o in out)}件）')
