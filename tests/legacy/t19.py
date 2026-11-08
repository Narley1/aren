import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w,h,name in [(420,800,'k_menu_phone.png'),(1280,800,'k_menu_desk.png')]:
            pg = await b.new_page(viewport={'width':w,'height':h}, device_scale_factor=2 if w<500 else 1)
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://'+os.path.abspath('test.html'))
            await pg.wait_for_timeout(1200)
            print(name, await pg.evaluate("document.fonts.check('700 20px \"Pixelify Sans\"')"), errs)
            await pg.screenshot(path=name)
            await pg.close()
        await b.close()
asyncio.run(main())
