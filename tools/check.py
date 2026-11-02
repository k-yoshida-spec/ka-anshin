"""公開前チェック。問題があれば終了コード1で公開を止める。
  python3 tools/check.py   （dist/ を検査。スクリーンショットは shots/ へ）
"""
import asyncio,sys,threading,http.server,functools,pathlib
from playwright.async_api import async_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent; D=ROOT/'dist'; S=ROOT/'shots'; S.mkdir(exist_ok=True)
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
H=functools.partial(Q,directory=str(D))
srv=http.server.ThreadingHTTPServer(('127.0.0.1',0),H); threading.Thread(target=srv.serve_forever,daemon=True).start()
U=f'http://127.0.0.1:{srv.server_address[1]}/'
bad=[]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (1280,390):
      pg=await b.new_page(viewport={'width':w,'height':900}); errs=[]
      pg.on('pageerror',lambda e:errs.append(str(e)))
      await pg.route('**/fonts.googleapis.com/**',lambda r:r.abort()); await pg.route('**/fonts.gstatic.com/**',lambda r:r.abort())
      await pg.goto(U+'index.html'); await pg.wait_for_timeout(800)
      await pg.add_style_tag(content='header{position:static!important}')
      ids=await pg.eval_on_selector_all('[data-go]','e=>[...new Set(e.map(x=>x.dataset.go))]')
      for g in ids:
        await pg.evaluate("g=>[...document.querySelectorAll('[data-go]')].find(e=>e.dataset.go===g).click()",g); await pg.wait_for_timeout(400)
        ov=await pg.evaluate('document.documentElement.scrollWidth-innerWidth')
        if ov>1: bad.append(f'{w}px {g}: 横にはみ出し {ov}px')
        broken=await pg.evaluate('[...document.images].filter(i=>i.complete&&i.offsetParent&&!i.naturalWidth).map(i=>i.src.slice(-40))')
        if broken: bad.append(f'{w}px {g}: 画像が表示されない {broken}')
        await pg.screenshot(path=str(S/f'{g}_{w}.png'),full_page=True)
      bad.extend(f'{w}px JSエラー: {e}' for e in errs); await pg.close()
    pg=await b.new_page(viewport={'width':1280,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U+'test-ce.html'); await pg.wait_for_timeout(1500)
    h=await pg.evaluate("parseInt(document.querySelector('ka-anshin').style.height)||0")
    if h<1000: bad.append(f'カスタムエレメントの高さが不足 {h}px')
    broken=await pg.evaluate("[...document.querySelector('ka-anshin').shadowRoot.querySelectorAll('img')].filter(i=>i.complete&&i.offsetParent&&!i.naturalWidth).length")
    if broken: bad.append(f'カスタムエレメント: 表示されない画像 {broken}件')
    bad.extend(f'カスタムエレメント JSエラー: {e}' for e in errs)
    await b.close()
asyncio.run(main())
print('\n'.join(bad) if bad else 'チェック合格'); sys.exit(1 if bad else 0)
