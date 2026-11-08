import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for run in range(20):
            pg = await b.new_page(viewport={'width':420,'height':800})
            errs=[]; pg.on('pageerror', lambda e: errs.append('PE '+str(e))); pg.on('console', lambda m: errs.append(m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
            await pg.goto('file://'+os.path.abspath('test.html'))
            await pg.click('#startBtn')
            await pg.evaluate("() => { const d = __d(); d.G.t = 599.5; d.P.maxHp=20; d.P.hp=20; }")
            await pg.wait_for_timeout(1500)
            print(run, errs[:2])
            await pg.close()
        await b.close()
asyncio.run(main())
