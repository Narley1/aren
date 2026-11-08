import asyncio, os, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':1200,'height':1320})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath(sys.argv[1]))
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=sys.argv[2], full_page=True)
        print(errs)
        await b.close()
asyncio.run(main())
