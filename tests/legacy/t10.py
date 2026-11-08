import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        r = await pg.evaluate("""() => {
          let t0 = performance.now(); for (let i=0;i<10;i++) groundChunk(500+i, 900); const chunk = (performance.now()-t0)/10;
          const d=__d(); d.G.t = 200; let worst=0, tot=0, n=0;
          for (let i=0;i<60*60;i++){ const dd=__d(); dd.P.inv=5; dd.P.x += 1.1; const a=performance.now(); __u(1/60); const t=performance.now()-a; worst=Math.max(worst,t); tot+=t; n++; if (dd.state!=='play') break; }
          return {chunk, avg: tot/n, worst, enemies: __d().E.length};
        }""")
        print(r, errs[:3])
        await b.close()
asyncio.run(main())
