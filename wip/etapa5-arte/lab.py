import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':1400,'height':900})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: errs.append(m.text))
        await pg.goto('file:///tmp/claude-0/-home-claude/6697085c-6d8e-5033-81f8-34a42603a3f2/scratchpad/stage5/art/lab.html?z=' + (sys.argv[2] if len(sys.argv) > 2 else '4'))
        await pg.wait_for_timeout(300); await pg.screenshot(path=sys.argv[1]); print(errs)
        await b.close()
asyncio.run(main())
