import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(800)
        await pg.click('#startBtn')
        await pg.evaluate("() => { const d=__d(); d.P.maxHp=40; d.P.hp=40; for (let i=0;i<10;i++) d.spawn('goblin', Math.random()*6.28, 30+Math.random()*30); }")
        for _ in range(40):
            await pg.wait_for_timeout(250)
            if await pg.evaluate("__d().state") == 'levelup': break
        await pg.wait_for_timeout(500)
        await pg.screenshot(path='l_levelup.png')
        print('state', await pg.evaluate("__d().state"), await pg.evaluate("__d().G.lvl"))
        await pg.keyboard.press('1')
        await pg.wait_for_timeout(300)
        print('after pick', await pg.evaluate("__d().state"), await pg.evaluate("JSON.stringify(__d().W)"))
        # shuriken tiers + fire
        await pg.evaluate("""() => { const d=__d(); d.W.boom=3; d.W.fire=4; d.P.inv=99; d.G.bmCd=0; d.G.frCd=0;
           for (let i=0;i<14;i++) d.spawn(['goblin','hobgoblin','orc'][i%3], Math.random()*6.28, 50+Math.random()*40); }""")
        await pg.wait_for_timeout(700)
        await pg.evaluate("() => { const d=__d(); d.fireExplosion(d.P.x+30, d.P.y-30, 28); }")
        await pg.wait_for_timeout(120)
        await pg.screenshot(path='l_play.png')
        print(errs[:4])
        await b.close()
asyncio.run(main())
