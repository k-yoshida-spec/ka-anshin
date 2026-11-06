"""Aページのビルド。
  python3 tools/build.py [--lang ja] [--base https://.../]
入力 : src/template.html（レイアウト）＋ content/a.<lang>.json か content/a.json（文章）＋ assets/img（画像）
出力 : dist/index.html（単体ページ） dist/ka-anshin.js（Wixカスタムエレメント） dist/img/*
"""
import json,re,sys,shutil,pathlib,argparse,os
ROOT=pathlib.Path(__file__).resolve().parent.parent
ap=argparse.ArgumentParser(); ap.add_argument('--lang',default='ja'); ap.add_argument('--base',default=os.environ.get('KA_BASE',''))
A=ap.parse_args()
IMG={'FACE':'owl-face.webp','FULL':'owl-full.webp','MARK':'owl-mark.webp','AKI':'photo-imaizumi.jpg','KAORU':'photo-yoshida.webp'}
for i in range(1,7): IMG[f'S{i}']=f'story-{i}.webp'
for c in ['rabbit','bear','fox','cat','dog']: IMG[c.upper()+'_FACE']=f'{c}-face.webp'; IMG[c.upper()+'_FULL']=f'{c}-full.webp'

tpl=(ROOT/'src/template.html').read_text(encoding='utf-8')
cf=ROOT/f'content/a.{A.lang}.json'
if not cf.exists(): cf=ROOT/'content/a.json'
text=json.loads(cf.read_text(encoding='utf-8'))
errs=[]
def tr(m):
    k=m.group(1)
    if k not in text: errs.append('文章データに無いキー: '+k); return ''
    if not str(text[k]).strip(): errs.append('空の文章: '+k)
    return str(text[k])
lpf=ROOT/'content/lps.json'
LPC=json.loads(lpf.read_text(encoding='utf-8')) if lpf.exists() else []
tpl=tpl.replace('⟦@LP_CATALOG⟧',json.dumps(LPC,ensure_ascii=False))
page=re.sub('⟦([^⟧]+)⟧',tr,tpl)
unused={k for k in set(text)-set(re.findall('⟦([^⟧]+)⟧',tpl)) if not k.startswith('meta.')}
if unused: print('注意: テンプレートで使われていないキー', sorted(unused)[:20])
left=[x for x in re.findall(r'\{\{([A-Z_0-9]+)\}\}',page) if x not in IMG]
if left: errs.append('未処理の差し込み記号: '+', '.join(set(left)))
if errs: print('\n'.join(errs)); sys.exit(1)

D=ROOT/'dist'; shutil.rmtree(D,ignore_errors=True); (D/'img').mkdir(parents=True)
for f in (ROOT/'assets/img').iterdir(): shutil.copy(f,D/'img'/f.name)

# 1) 単体ページ（相対パス）
std=page
for k,f in IMG.items(): std=std.replace('{{'+k+'}}','img/'+f)
L=std.splitlines(True); si=next(i for i,l in enumerate(L) if l.lstrip().startswith('<style'))
desc=text.get('meta.description','')
html=('<!doctype html>\n<html lang="'+A.lang+'">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n'
      +''.join(L[:si])+(f'<meta name="description" content="{desc}">\n' if desc else '')+'</head>\n<body>\n'
      +L[si]+'.proto{display:none!important}\n\n'+''.join(L[si+1:])+'\n</body>\n</html>\n')
(D/'index.html').write_text(html,encoding='utf-8')

# 2) Wixカスタムエレメント
s0=page.index('<style>')+7; s1=page.index('</style>')
sc0=page.index('<script>',s1)+8; sc1=page.rindex('</script>')
css,markup,script=page[s0:s1],page[s1+8:sc0-8],page[sc0:sc1]
css=(':host{display:block;width:100%}\n.kroot{display:block}\n\n.proto{display:none!important}\n'
     +re.sub(r'(^|\n)body(?=[.:{\s])',r'\1.kroot',css.replace(':root{','.kroot{',1)))
markup='\n'+markup+'\n\n'
for k,f in IMG.items():
    markup=markup.replace('{{'+k+'}}','%%B%%img/'+f)
    for q in '"\'': script=script.replace(q+'{{'+k+'}}'+q,'KA_B+"img/'+f+'"')
old="$('#inq').addEventListener('submit',e=>{e.preventDefault();$('#sent').hidden=false;});"
assert script.count(old)==1,'フォーム送信部分が見つかりません'
script=script.replace(old,(ROOT/'src/ce_submit.js').read_text(encoding='utf-8'))
hdr=(ROOT/'src/ce_header.js').read_text(encoding='utf-8')
base=json.dumps(A.base)
out=(hdr+'const KA_B=(document.currentScript&&document.currentScript.src)?new URL("./",document.currentScript.src).href:'+base+';\n'
     +'const CSS='+json.dumps(css,ensure_ascii=False)+';\n'
     +'const HTML='+json.dumps(markup,ensure_ascii=False)+'.split("%%B%%").join(KA_B);\n'
     +'const FONT="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@600;700&display=swap";\n'
     +'function run(document,R){\n'+script+'\n}\n'+(ROOT/'src/ce_footer.js').read_text(encoding='utf-8'))
(D/'ka-anshin.js').write_text(out,encoding='utf-8')
(D/'test-ce.html').write_text('<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><style>body{margin:0;font-family:sans-serif}</style></head><body><ka-anshin></ka-anshin><script src="ka-anshin.js"></script></body></html>\n',encoding='utf-8')
# 3) 検索向けの構造化データ（Wix のページ設定「構造化データ」に貼る）
ld={'@context':'https://schema.org','@type':'ItemList','name':text.get('meta.title','職場のメンタルヘルス対策（ストレスチェック・研修・カウンセリング）｜新潟のK&Aプロジェクト'),
    'itemListElement':[{'@type':'ListItem','position':i+1,'item':{'@type':'Service','name':c['title'],'description':c['text'],'url':c['url'],
        'serviceType':c['stage'],'areaServed':'新潟県','provider':{'@type':'Organization','name':'合同会社K&Aプロジェクト','url':'https://www.ak-analytics.jp/'}}}
        for i,c in enumerate([c for c in LPC if c['published']])]}
(D/'seo-jsonld.json').write_text(json.dumps(ld,ensure_ascii=False,indent=1)+'\n',encoding='utf-8')
print('ok', {p.name:p.stat().st_size for p in D.iterdir() if p.is_file()})
