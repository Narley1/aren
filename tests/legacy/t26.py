import asyncio, os
from playwright.async_api import async_playwright
PICK = "() => { const o = performance.now; performance.now = () => o.call(performance) + 1e6; __d().chooseLevel(0); performance.now = o; }"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800}, device_scale_factor=2)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn'); await pg.wait_for_timeout(600)
        await pg.screenshot(path='n_start.png')
        print('start state', await pg.evaluate("__d().state"))
        await pg.wait_for_timeout(400); await pg.keyboard.press('1'); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='n_play.png')
        r = await pg.evaluate("""() => {
          const log = []; const o = performance.now;
          for (let i=0;i<60*640;i++){
            const d=__d(); d.P.inv=5; d.P.hp = d.P.maxHp;
            d.P.x += Math.cos(i/300)*1.1; d.P.y += Math.sin(i/410)*1.1;
            const e=d.G.boss&&d.G.boss.e; if (e && e.bs.seals){ const z=e.bs.seals.find(z=>!z.lit); if(z){d.P.x=z.x;d.P.y=z.y;} }
            if (d.state === 'levelup'){ log.push(`pick Nv${d.G.lvl} @ ${Math.floor(d.G.t/60)}:${String(Math.floor(d.G.t%60)).padStart(2,'0')}`); performance.now = () => o.call(performance) + 1e6; d.chooseLevel(0); performance.now = o; continue; }
            __u(1/60);
            if (__d().state === 'over') break;
          }
          const d=__d(); log.push(`end t=${d.G.t.toFixed(0)} lvl=${d.G.lvl} kills=${d.G.kills} W=${JSON.stringify(d.W)}`);
          return log;
        }""")
        print('\n'.join(r)); print(errs[:4])
        await b.close()
asyncio.run(main())
