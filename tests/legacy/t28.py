import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn'); await pg.wait_for_timeout(500)
        await pg.evaluate("() => __hurt(999)")
        await pg.wait_for_timeout(1500)
        print('state', await pg.evaluate("__d().state"), 'shake', await pg.evaluate("__d().G.shake"))
        frac = await pg.evaluate("""async () => { const c = document.getElementById('c'), g = c.getContext('2d');
          const A = g.getImageData(0,0,c.width,c.height).data; await new Promise(r => setTimeout(r, 150));
          const Bd = g.getImageData(0,0,c.width,c.height).data; let d = 0; for (let i=0;i<A.length;i+=4) if (A[i]!==Bd[i]||A[i+1]!==Bd[i+1]||A[i+2]!==Bd[i+2]) d++; return d/(A.length/4); }""")
        print('fraction of pixels changed between frames: %.3f' % frac, errs)
        await b.close()
asyncio.run(main())
