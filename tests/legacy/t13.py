import asyncio, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':900,'height':520})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.evaluate("""() => { const o=document.createElement('canvas'); o.width=900;o.height=520; o.style.cssText='position:fixed;inset:0;z-index:99;background:#6cc24a'; document.body.appendChild(o);
          const g=o.getContext('2d'); g.imageSmoothingEnabled=false; const Z=5; let x=6;
          const ET=__d().ET;
          for (const dir of ['down','up','side']) for (const f of [0,1]){ const n=ET.orc.dirs[dir][f].n; g.drawImage(n,x,6,n.width*Z,n.height*Z); x+=n.width*Z+6; }
          x=6; for (const f of [0,2]){ const n=ET.succubus.dirs.all[f].n; g.drawImage(n,x,230+0,n.width*Z,n.height*Z); x+=n.width*Z+8; }
          for (const f of [0,2]){ const n=ET.elf.dirs.down[f].n; g.drawImage(n,x,230,n.width*Z,n.height*Z); x+=n.width*Z+8; }
        }""")
        await pg.screenshot(path='orc.png')
        print(errs)
        await b.close()
asyncio.run(main())
