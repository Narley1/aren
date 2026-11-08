import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn'); await pg.wait_for_timeout(500)
        print('state after start:', await pg.evaluate("__d().state"), '| toast:', await pg.evaluate("document.querySelector('#toast .t1').textContent"))
        r = await pg.evaluate("""() => { const d=__d(); d.P.hp = 4; d.ITEMS.push({x:d.P.x, y:d.P.y, kind:'life', t:0}); __u(1/60);
          const after = __d().P.hp; const q = __d(); q.ITEMS.push({x:q.P.x+30, y:q.P.y, kind:'life', t:0}); q.ITEMS.push({x:q.P.x-30, y:q.P.y, kind:'apple', t:0}); return {before:4, after}; }""")
        print('heal pickup:', r)
        await pg.evaluate("() => { document.getElementById('toast').classList.remove('show'); }")
        await pg.wait_for_timeout(300)
        print(await pg.evaluate("JSON.stringify([innerWidth, innerHeight, __d().ITEMS.map(i=>i.kind)])"))
        await pg.screenshot(path='h_items.png', clip={'x':120,'y':330,'width':180,'height':130})
        print(errs)
        await b.close()
asyncio.run(main())
