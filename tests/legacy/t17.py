import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(1000)
        await pg.screenshot(path='j_menu.png')
        await pg.click('#startBtn')
        await pg.keyboard.down('d'); await pg.wait_for_timeout(900); await pg.keyboard.up('d')
        await pg.evaluate("""() => { const d=__d(); d.P.maxHp=40; d.P.hp=40; d.W.orb=2; d.W.sword=3;
          for (const k of ['goblin','hobgoblin','orc','elf','demon','succubus']) for (let i=0;i<2;i++) d.spawn(k, Math.random()*6.28, 45+Math.random()*40, i===0&&k==='goblin'); }""")
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path='j_play.png')
        r = await pg.evaluate("""() => { for (let i=0;i<60*400;i++){ const d=__d(); d.P.inv=5; d.P.hp=40; d.P.x += Math.cos(i/300); d.P.y += Math.sin(i/410);
            const e=d.G.boss&&d.G.boss.e; if (e && e.bs.seals){ const z=e.bs.seals.find(z=>!z.lit); if(z){d.P.x=z.x;d.P.y=z.y;} }
            if (i===0) d.G.t = 560; __u(1/60); if (d.state!=='play') return 'ended '+d.G.t.toFixed(0); } return 'alive '+__d().G.t.toFixed(0); }""")
        print(r, errs[:4])
        await b.close()
asyncio.run(main())
