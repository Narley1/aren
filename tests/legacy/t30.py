import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn'); await pg.wait_for_timeout(300)
        r = await pg.evaluate("""() => {
          const d = __d(); d.G.need = 1e9; d.W.sword = 0; d.W.fire = 3; d.P.inv = 99; d.G.frCd = 0;
          for (let i=0;i<4;i++) d.spawn('orc', -0.5, 55);
          const es = __d().E.slice(); for (const e of es){ e.hp = 5000; }
          const log = []; let prev = es.map(e => e.hp);
          for (let i=0;i<60*3;i++){ __u(1/60);
            const now = es.map(e => e.hp); const dd = now.map((v,k) => prev[k]-v).filter(x => x > 0);
            if (dd.length) log.push(`${(i/60).toFixed(2)}s burns=${__d().BURNS.length} dmg=[${dd.map(x=>x.toFixed(1)).join(',')}]`);
            prev = now; if (i === 40) __d().G.frCd = 99; }
          return {n:es.length, dist:es.map(e => Math.hypot(e.x-__d().P.x, e.y-__d().P.y).toFixed(0)), log};
        }""")
        print(r['n'], r['dist']); print('\n'.join(r['log'])); print(errs)
        await b.close()
asyncio.run(main())
