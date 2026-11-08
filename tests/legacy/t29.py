import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:200]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""() => {
          const d = __d(); d.G.need = 1e9; d.W.sword = 0; d.W.fire = 3; d.P.inv = 99; d.G.frCd = 0; d.renderGear();
          // a tough dummy pack standing still, 50px away
          for (let i=0;i<4;i++) d.spawn('orc', -0.5, 55);
          for (const e of __d().E){ e.hp = 5000; e.d = Object.assign({}, e.d, {spd:0}); }
          const tgt = __d().E[0], out = []; let firstBurn = -1, burnEnd = -1, last = tgt.hp;
          for (let i=0;i<60*4;i++){ __u(1/60); const D = __d();
            if (D.BURNS.length && firstBurn < 0) firstBurn = i;
            if (firstBurn >= 0 && !D.BURNS.length && burnEnd < 0) burnEnd = i;
            if (tgt.hp < last){ out.push(`${(i/60).toFixed(2)}s -${(last - tgt.hp).toFixed(1)}`); last = tgt.hp; }
            if (i === 70) D.G.frCd = 99; }
          return {firstBurn:(firstBurn/60).toFixed(2), burnEnd:(burnEnd/60).toFixed(2), hits:out};
        }""")
        print(r)
        await pg.evaluate("() => { const d=__d(); d.G.frCd = 0; }")
        await pg.wait_for_timeout(900)
        await pg.screenshot(path='burn.png', clip={'x':60,'y':250,'width':300,'height':260})
        print(errs[:3])
        await b.close()
asyncio.run(main())
