import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        r = await pg.evaluate("""() => {
          const log = []; let ups = 0, lifes = 0, picks = 0; const seenItems = new Set();
          for (let i=0;i<60*640;i++){
            const d=__d(); d.P.inv=5; d.P.hp = d.P.maxHp;
            d.P.x += Math.cos(i/300)*1.1; d.P.y += Math.sin(i/410)*1.1;
            const e=d.G.boss&&d.G.boss.e; if (e && e.bs.seals){ const z=e.bs.seals.find(z=>!z.lit); if(z){d.P.x=z.x;d.P.y=z.y;} }
            for (const it of d.ITEMS) if (!seenItems.has(it)){ seenItems.add(it); if (it.kind==='up') ups++; else lifes++; }
            __u(1/60);
            if (d.state === 'levelup'){ picks++; window.performance.now; d.chooseLevel && (()=>{})(); }
            if (__d().state === 'levelup'){ const st = __d(); /* bypass 350ms guard */ st.G.__t = 0; }
            if (__d().state === 'levelup'){ document.querySelector('#choice0'); }
            if (__d().state === 'levelup'){ const o = performance.now; performance.now = () => o.call(performance) + 1e6; __d().chooseLevel(0); performance.now = o; }
            if (i % (60*60) === 0) log.push(`${(i/60/60)|0}min lvl=${d.G.lvl} kills=${d.G.kills} W=${Object.values(d.W).join('')}`);
            if (__d().state === 'over') { log.push('over at '+d.G.t.toFixed(0)); break; }
          }
          const d=__d(); log.push(`end lvl=${d.G.lvl} kills=${d.G.kills} picks=${picks} upDrops=${ups} heartDrops=${lifes} W=${JSON.stringify(d.W)}`);
          return log;
        }""")
        print('\n'.join(r)); print(errs[:4])
        await b.close()
asyncio.run(main())
