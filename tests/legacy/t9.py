import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('c:'+m.text) if m.type=='error' and 'ERR_TUNNEL' not in m.text else None)
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(1200)
        await pg.screenshot(path='g_menu.png')
        await pg.click('#startBtn')
        await pg.keyboard.down('d'); await pg.wait_for_timeout(1500); await pg.keyboard.up('d')
        await pg.keyboard.down('s'); await pg.wait_for_timeout(1000); await pg.keyboard.up('s')
        await pg.wait_for_timeout(6000)
        await pg.screenshot(path='g_early.png')
        await pg.evaluate("""() => { const d=__d(); d.P.maxHp=40; d.P.hp=40; d.W.orb=2; d.W.boom=2;
           for (const k of ['goblin','gargoyle','hobgoblin','elf','orc','demon','wyvern']) for (let i=0;i<3;i++) d.spawn(k, Math.random()*6.28, 60+Math.random()*50, i===0&&k==='orc'); }""")
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path='g_mid.png')
        await pg.evaluate("() => { const d=__d(); d.G.t=599.8; d.P.hp=40; }")
        await pg.wait_for_timeout(8000)
        await pg.screenshot(path='g_boss.png')
        print(errs[:5])
        await b.close()
asyncio.run(main())
