import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w,h,dsf,tag in [(420,800,2,'p'),(1280,800,1,'d')]:
            pg = await b.new_page(viewport={'width':w,'height':h}, device_scale_factor=dsf)
            errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
            await pg.goto('file://'+os.path.abspath('test.html'))
            await pg.wait_for_timeout(1500)
            for tt in [8.0]:
                await pg.evaluate(f"() => {{ __TT.t = {tt}; }}"); await pg.wait_for_timeout(40)
                await pg.screenshot(path=f'nap_{tag}_{tt}.png')
            print(tag, errs[:3])
            await pg.close()
        await b.close()
asyncio.run(main())
