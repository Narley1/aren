import asyncio, os
from playwright.async_api import async_playwright
INIT = """
const oc = AudioNode.prototype.connect;
AudioNode.prototype.connect = function(t, ...r){
  if (t instanceof AudioDestinationNode && !window.__an){ const an = this.context.createAnalyser(); an.fftSize = 2048; oc.call(this, an); window.__an = an; }
  return oc.call(this, t, ...r);
};
window.__level = () => { const an = window.__an; if (!an) return -1; const d = new Float32Array(an.fftSize); an.getFloatTimeDomainData(d); let m = 0; for (const v of d) m = Math.max(m, Math.abs(v)); return m; };
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(viewport={'width':420,'height':800})
        await pg.add_init_script(INIT)
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)+' '+(e.stack or '')[:300]))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        async def peak(ms):
            mx = 0
            for _ in range(ms//50):
                await pg.wait_for_timeout(50); mx = max(mx, await pg.evaluate("__level()"))
            return round(mx, 3)
        print('calm music', await peak(3000))
        for name, js in [('demon', "__d().SFX.giggle('demon')"), ('succubus', "__d().SFX.giggle('succubus')"), ('hex', "__d().SFX.hex()"),
                         ('roar', "__d().SFX.roar({force:true})"), ('breath', "__d().SFX.fireBreath(1.4)"), ('rattle', "__d().SFX.rattle()"), ('thud', "__d().SFX.thud()"), ('death', "__d().SFX.dragonDeath()")]:
            await pg.evaluate("__d().SFX.setMusic(false)")
            await pg.wait_for_timeout(1500)
            await pg.evaluate(js)
            print(name, await peak(1600))
        await pg.evaluate("__d().SFX.setMusic(true)")
        await pg.evaluate("() => { const d=__d(); d.G.t = 300; for (let i=0;i<40;i++) d.spawn('goblin', Math.random()*6.28, 60); }")
        print('combat music', await peak(4000))
        await pg.evaluate("() => { const d=__d(); d.G.t = 599.5; d.P.maxHp = 99; d.P.hp = 99; d.P.inv = 999; }")
        await pg.wait_for_timeout(7000)
        print('boss music', await peak(4000), await pg.evaluate("__d().G.boss && __d().G.boss.phase"))
        print(errs[:5])
        await b.close()
asyncio.run(main())
