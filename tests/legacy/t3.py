import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+str(e.stack)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        await pg.evaluate("() => { const d = __d(); d.G.t = 599.5; d.P.maxHp=20; d.P.hp=20; }")
        await pg.wait_for_timeout(7000)
        print(await pg.evaluate("() => { const d = __d(); return [d.G.dark, d.G.boss && d.G.boss.phase, d.state, d.G.t] }"))
        await pg.screenshot(path='s3.png')
        print(errs)
        await b.close()
asyncio.run(main())
