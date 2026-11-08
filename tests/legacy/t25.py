import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn'); await pg.wait_for_timeout(2000)
        await pg.evaluate("() => { const d=__d(); d.G.need=99999; d.fireExplosion(d.P.x+28, d.P.y-20, 28); }")
        for i,ms in enumerate([60,120,160]):
            await pg.wait_for_timeout(ms); await pg.screenshot(path=f'x{i}.png', clip={'x':150,'y':260,'width':200,'height':170})
        print(errs)
        await b.close()
asyncio.run(main())
