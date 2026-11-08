import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('c:'+m.text) if m.type=='error' and 'ERR_' not in m.text else None)
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(800)
        await pg.screenshot(path='h_menu.png')
        await pg.click('#startBtn')
        r = await pg.evaluate("""async () => { const S=__d().SFX; await new Promise(r=>setTimeout(r,300));
          S.roar({force:true}); S.fireBreath(); S.whoosh(); S.thud(); S.rattle(); S.giggle('demon'); S.giggle('succubus'); return 'sfx ok'; }""")
        print(r)
        await pg.evaluate("""() => { const d=__d(); d.P.maxHp=40; d.P.hp=40; d.W.orb=3; d.W.sword=3;
           for (const k of ['goblin','orc','elf','succubus','demon','succubus']) for (let i=0;i<2;i++) d.spawn(k, Math.random()*6.28, 45+Math.random()*30); }""")
        for i in range(4):
            await pg.wait_for_timeout(330)
            await pg.screenshot(path=f'h_play{i}.png')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path='h_play_late.png')
        await pg.evaluate("() => { const d=__d(); d.G.t=599.8; d.P.hp=40; d.P.inv=99; }")
        await pg.wait_for_timeout(9000)
        await pg.screenshot(path='h_boss.png')
        print(errs[:5])
        await b.close()
asyncio.run(main())
