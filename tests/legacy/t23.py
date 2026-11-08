import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(600)
        await pg.click('#startBtn')
        await pg.evaluate("""() => { const d=__d(); d.G.need = 99999; d.W.boom=3; d.W.fire=4; d.W.orb=2; d.P.maxHp=12; d.P.hp=12; d.P.inv=99; d.G.bmCd=0; d.G.frCd=0; d.renderGear();
           for (let i=0;i<16;i++) d.spawn(['goblin','hobgoblin','orc','demon'][i%4], Math.random()*6.28, 45+Math.random()*45); }""")
        for i in range(5):
            await pg.wait_for_timeout(260)
            await pg.screenshot(path=f'm{i}.png', clip={'x':40,'y':180,'width':340,'height':440})
        # shuriken sheet
        await pg.evaluate("""() => { const d=__d(); const o=document.createElement('canvas'); o.width=420;o.height=150; o.style.cssText='position:fixed;left:0;top:0;z-index:99;background:#6cc24a'; document.body.appendChild(o);
          const g=o.getContext('2d'); g.imageSmoothingEnabled=false; let x=6; for (const t of [0,1,2]) for (const f of [0,4]){ const c=d.SHUR[t][f]; g.drawImage(c,x,10,c.width*5,c.height*5); x+=c.width*5+4; if (x>380) break; } }""")
        await pg.screenshot(path='m_sheet.png', clip={'x':0,'y':0,'width':420,'height':150})
        print(errs[:4])
        await b.close()
asyncio.run(main())
