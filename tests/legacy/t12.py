import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        await pg.evaluate("""() => { const d=__d(); d.P.maxHp=40; d.P.hp=40; d.P.inv=0; d.W.sword=3;
          d.spawn('orc', 0, 34); d.spawn('succubus', 3.4, 40); d.spawn('elf', 1.9, 60); d.spawn('goblin', 4.4, 26); }""")
        # freeze RAF-driven updates by stepping manually: set state to pause-like
        await pg.evaluate("() => { const d=__d(); d.E.forEach(e=>{e.d.__spd=e.d.spd}); }")
        shots = []
        for i in range(6):
            await pg.evaluate("() => { const d=__d(); d.P.inv=0; d.P.hp=40; }")
            await pg.wait_for_timeout(70)
            await pg.screenshot(path=f'z{i}.png', clip={'x':90,'y':250,'width':240,'height':300})
        await b.close()
asyncio.run(main())
