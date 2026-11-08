import asyncio, os, subprocess, time, json
from playwright.async_api import async_playwright
srv = subprocess.Popen(['python3','-m','http.server','8765','--bind','127.0.0.1'], cwd='dist', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(1)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':420,'height':800}, device_scale_factor=2)
        pg = await ctx.new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.on('console', lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        bad=[]; pg.on('response', lambda r: bad.append((r.status, r.url)) if r.status >= 400 else None)
        await pg.goto('http://127.0.0.1:8765/')
        await pg.wait_for_timeout(1500)
        info = await pg.evaluate("""async () => {
          const reg = await navigator.serviceWorker.ready;
          const m = await (await fetch('manifest.webmanifest')).json();
          const icons = await Promise.all(m.icons.map(async i => (await fetch(i.src)).status));
          return {sw: !!reg.active, manifestName: m.name, icons, title: document.title, font: document.fonts.check('700 20px "Pixelify Sans"'),
                  fsVisible: !document.getElementById('fsBtn').hidden, h1: document.querySelector('h1').textContent};
        }""")
        print(json.dumps(info, ensure_ascii=False))
        await pg.reload(); await pg.wait_for_timeout(800)
        print('controlled after reload:', await pg.evaluate("!!navigator.serviceWorker.controller"))
        await pg.click('#startBtn'); await pg.wait_for_timeout(2500)
        await pg.screenshot(path='web_play.png')
        print('state after start:', await pg.evaluate("document.getElementById('hud').hidden ? 'menu' : 'playing'"))
        await ctx.set_offline(True)
        srv.terminate(); time.sleep(.5)
        await pg.reload(); await pg.wait_for_timeout(1500)
        print('offline reload title:', await pg.title(), '| start button present:', await pg.evaluate("!!document.getElementById('startBtn')"))
        await pg.click('#startBtn'); await pg.wait_for_timeout(1500)
        print('offline playing:', await pg.evaluate("!document.getElementById('hud').hidden"))
        print('errors:', errs[:5], 'bad responses:', bad[:5])
        await b.close()
try:
    asyncio.run(main())
finally:
    srv.terminate()
