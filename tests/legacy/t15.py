import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        pg.on('console', lambda m: errs.append('c:'+m.text) if m.type=='error' and 'ERR_' not in m.text else None)
        t0 = await pg.evaluate("performance.now()")
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(1500)
        print('load ms', await pg.evaluate("performance.now()"))
        await pg.screenshot(path='i_menu.png')
        await pg.click('#startBtn')
        await pg.keyboard.down('d'); await pg.wait_for_timeout(1200); await pg.keyboard.up('d')
        await pg.evaluate("""() => { const d=__d(); d.P.maxHp=40; d.P.hp=40; d.W.orb=3; d.W.sword=3; d.W.boom=2;
          for (const k of ['goblin','hobgoblin','orc','elf','succubus','demon','gargoyle','wyvern']) for (let i=0;i<2;i++) d.spawn(k, Math.random()*6.28, 50+Math.random()*40, i===0&&k==='hobgoblin'); }""")
        await pg.wait_for_timeout(2200)
        await pg.screenshot(path='i_play.png')
        r = await pg.evaluate("""() => { let worst=0,tot=0,n=0; for (let i=0;i<600;i++){ const d=__d(); d.P.inv=5; d.P.hp=40; d.P.x+=1.2; const a=performance.now(); __u(1/60); const t=performance.now()-a; tot+=t; n++; worst=Math.max(worst,t);} return [tot/n, worst]; }""")
        print('frame avg/worst', r)
        await pg.evaluate("() => { const d=__d(); d.G.t=599.8; d.P.hp=40; }")
        await pg.wait_for_timeout(7000)
        await pg.evaluate("""() => { for (let i=0;i<60*12;i++){ const d=__d(); d.P.inv=5; d.P.hp=40; __u(1/60); const e=d.G.boss&&d.G.boss.e; if (e && e.bs.st==='spiral' && e.bs.t>1) return; } }""")
        await pg.evaluate("() => { __d().P.inv = 0; }")
        await pg.screenshot(path='i_boss.png')
        print(errs[:5])
        await b.close()
asyncio.run(main())
