import asyncio, os
from playwright.async_api import async_playwright
STEP = """(cond) => { for (let i=0;i<60*60;i++){ const d=__d(); d.P.inv=5; __u(1/60); const e=d.G.boss&&d.G.boss.e; if (e && new Function('e','d','return '+cond)(e,d)) return i; } return -1; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        await pg.evaluate("() => { const d = __d(); d.G.t = 599; d.W.sword=6; d.W.orb=3; d.W.storm=2; d.P.maxHp=20; d.P.hp=20; }")
        # freeze real loop by pausing state? Use rAF still running; stepping manually is ok.
        await pg.wait_for_timeout(4500)
        await pg.screenshot(path='b_intro.png')
        print('seals', await pg.evaluate(STEP, "e.bs.seals && e.bs.seals[0]"))
        await pg.screenshot(path='b_seals.png')
        print('breath', await pg.evaluate(STEP, "e.bs.st==='breath' && e.bs.t>0.5 && e.bs.t<0.9"))
        await pg.screenshot(path='b_breath.png')
        print('rings', await pg.evaluate(STEP, "e.bs.st==='rings' && e.bs.k>=2"))
        await pg.screenshot(path='b_rings.png')
        print(errs)
        await b.close()
asyncio.run(main())
