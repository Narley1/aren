import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.goto('file://'+__import__('os').path.abspath('test.html'))
        await pg.wait_for_timeout(800)
        await pg.screenshot(path='s0.png')
        await pg.click('#startBtn')
        await pg.evaluate("""() => { const d = __d(); d.G.t = 598; d.W.storm = 5; d.W.meteor = 5; d.W.holy = 5; d.W.sword = 8; d.W.fire=6; d.W.orb=6; d.W.boom=6; d.P.maxHp = 20; d.P.hp = 20; }""")
        await pg.wait_for_timeout(9000)
        await pg.screenshot(path='s1.png')
        info = await pg.evaluate("""() => { const d = __d(); const e = d.G.boss && d.G.boss.e; return {phase: d.G.boss && d.G.boss.phase, E: d.E.length, hp: e && e.hp, st: e && e.bs.st, state: d.state}; }""")
        print('after intro', info)
        # simulate fight with invulnerable player
        log = await pg.evaluate("""() => {
          const out = []; const d0 = __d(); const seen = new Set();
          for (let i=0;i<60*120;i++){
            const d = __d(); d.P.inv = 5;
            const e = d.G.boss.e; if (!e) break;
            if (e.bs.seals){ const z = e.bs.seals.find(z => !z.lit); if (z){ d.P.x = z.x; d.P.y = z.y; } }
            seen.add(e.bs.st);
            __u(1/60);
            if (d.state !== 'play') { out.push('state '+d.state+' at '+i); break; }
            if (i % 600 === 0) out.push(`${i/60}s hp=${Math.round(e.hp)} st=${e.bs.st} EB=${d.EB.length} marks=${d.MARKS.length} stun=${e.bs.stun.toFixed(1)} enr=${e.bs.enraged}`);
          }
          out.push('states seen: '+[...seen].join(','));
          return out;
        }""")
        print('\n'.join(log))
        await pg.screenshot(path='s2.png')
        print('ERRORS', errs[:10])
        await b.close()
asyncio.run(main())
