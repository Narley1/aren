import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w,h,dsf,name in [(420,800,2,'ti_phone.png'),(1280,800,1,'ti_desk.png')]:
            pg = await b.new_page(viewport={'width':w,'height':h}, device_scale_factor=dsf)
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
            await pg.goto('file://'+os.path.abspath('test.html'))
            await pg.wait_for_timeout(2200)
            await pg.screenshot(path=name)
            print(name, errs)
            if w == 420:
                await pg.click('#howBtn'); await pg.wait_for_timeout(300); await pg.screenshot(path='ti_how.png')
                await pg.click('#backBtn'); await pg.wait_for_timeout(200)
                await pg.mouse.click(210, 400); await pg.wait_for_timeout(600)
                print('after tap:', await pg.evaluate("document.getElementById('hud').hidden ? 'title' : 'playing'"), errs)
            await pg.close()
        await b.close()
asyncio.run(main())
