import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        r = await pg.evaluate("""() => {
          const errs = [];
          for (let run=0; run<6; run++){
            const d = __d(); d.G.t = 0;
            for (let i=0;i<60*120;i++){
              const dd = __d(); dd.P.inv = 5; dd.P.x += 0.6;
              try { __u(1/60); } catch(e){ errs.push(dd.G.t.toFixed(1)+' '+e.stack.split('\\n').slice(0,3).join(' | ')); break; }
            }
          }
          return errs;
        }""")
        print(r)
        await b.close()
asyncio.run(main())
