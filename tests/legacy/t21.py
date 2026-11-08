import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':1280,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('dist/index.html'))
        await pg.wait_for_timeout(1200)
        await pg.click('#startBtn'); await pg.wait_for_timeout(1500)
        print('file:// playing:', await pg.evaluate("!document.getElementById('hud').hidden"), errs)
        await b.close()
asyncio.run(main())
