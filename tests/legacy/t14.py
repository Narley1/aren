import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        await pg.evaluate("() => { const d=__d(); d.G.t=599.9; d.P.maxHp=40; d.P.hp=40; }")
        await pg.wait_for_timeout(6500)
        r = await pg.evaluate("""() => { for (let i=0;i<60*20;i++){ const d=__d(); d.P.inv=5; d.P.hp=40; __u(1/60); const e=d.G.boss&&d.G.boss.e; if (e && e.bs.st==='breath' && e.bs.t>1.2) return i; } return -1; }""")
        await pg.evaluate("() => { __d().P.inv = 0; }")
        await pg.screenshot(path='h_boss2.png')
        # full fight sim for errors
        r2 = await pg.evaluate("""() => { for (let i=0;i<60*400;i++){ const d=__d(); d.P.inv=5; d.P.hp=40; const e=d.G.boss.e; if (e && e.bs.seals){ const z=e.bs.seals.find(z=>!z.lit); if(z){d.P.x=z.x;d.P.y=z.y;} } __u(1/60); if (d.state!=='play') return 'ended '+(i/60).toFixed(0)+'s'; } return 'alive'; }""")
        print(r, r2, errs[:3])
        await b.close()
asyncio.run(main())
