import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:400]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        r = await pg.evaluate("""() => { const d0=__d(); d0.G.t = 120; Object.assign(d0.W,{orb:4,boom:3,fire:3,storm:2,holy:2,meteor:2});
          for (let i=0;i<60*500;i++){ const d=__d(); d.P.inv=5; d.P.hp=40;
            d.P.x += Math.cos(i/300)*1.1; d.P.y += Math.sin(i/410)*1.1;
            const e=d.G.boss&&d.G.boss.e; if (e && e.bs.seals){ const z=e.bs.seals.find(z=>!z.lit); if(z){d.P.x=z.x;d.P.y=z.y;} }
            __u(1/60); if (d.state!=='play') return 'ended at '+d.G.t.toFixed(0)+' kills '+d.G.kills; }
          return 'still playing t='+__d().G.t.toFixed(0); }""")
        print(r, errs[:4])
        await b.close()
asyncio.run(main())
