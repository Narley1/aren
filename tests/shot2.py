import asyncio, os, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':int(sys.argv[3]) if len(sys.argv)>3 else 1400,'height':int(sys.argv[4]) if len(sys.argv)>4 else 1900})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        u=sys.argv[1]; await pg.goto('file://'+os.path.abspath(u.split('?')[0])+('?'+u.split('?')[1] if '?' in u else ''))
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path=sys.argv[2])
        print(await pg.title(), errs)
        await b.close()
asyncio.run(main())
