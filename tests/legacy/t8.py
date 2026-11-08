import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        for build in ["{sword:6, orb:3, storm:2, holy:1, fire:3}", "{sword:8, orb:6, storm:5, holy:5, fire:6, boom:6, meteor:5}"]:
            r = await pg.evaluate("""(b) => { const d=__d(); d.G.t=599.9; Object.assign(d.W, b); d.P.maxHp=20; d.P.hp=20; d.G.boss=null;
              let out=null;
              for (let i=0;i<60*900;i++){ const dd=__d(); dd.P.inv=5; const e=dd.G.boss&&dd.G.boss.e;
                if (e && e.bs.seals){ const z=e.bs.seals.find(z=>!z.lit); if(z){dd.P.x=z.x; dd.P.y=z.y;} }
                __u(1/60); if (dd.state!=='play'){ out=(dd.G.t-600).toFixed(0)+'s fight'; break; } }
              return out || ('alive hp '+Math.round(__d().G.boss.e.hp)); }""", __import__('json').loads(build.replace("{","{\"").replace(":", "\":").replace(", ", ", \"")))
            print(build, r)
            await pg.evaluate("() => { document.getElementById('startBtn').click(); }")
            await pg.click('#againBtn') if False else None
            await pg.evaluate("() => { document.getElementById('againBtn').click(); }")
        print(errs)
        await b.close()
asyncio.run(main())
