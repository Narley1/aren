import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.click('#startBtn')
        await pg.evaluate("() => { const d = __d(); d.G.t = 599.9; }")
        await pg.wait_for_timeout(5000)
        r = await pg.evaluate("""() => { const d=__d(); const c=document.getElementById('c'); const g=c.getContext('2d'); const px=g.getImageData(2,2,1,1).data; 
          const g2=document.createElement('canvas').getContext('2d'); const gr=g2.createRadialGradient(5,5,1,5,5,10); gr.addColorStop(0,'rgba(0,0,0,0.5)'); gr.addColorStop(1,'rgba(0,0,0,0.5)'); g2.fillStyle=gr; g2.fillRect(0,0,10,10);
          return {dark:d.G.dark, px:[...px], test:[...g2.getImageData(1,1,1,1).data], fs: typeof gr}; }""")
        print(r)
        await b.close()
asyncio.run(main())
