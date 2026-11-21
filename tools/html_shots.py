#!/usr/bin/env python3
"""Capturas de referência do jogo HTML nos mesmos momentos das capturas do Godot (tools/shots.sh):
tela inicial, partida semeada aos ~25 s com Aren parado (no meio de um golpe da espada), pausa e fim de jogo,
em 390x844 e 1366x768. Usa o gancho de testes do próprio HTML (tests/smoke.py do repositório HTML).

    python3 tools/html_shots.py --aren ../aren --out /pasta/de/saida
"""
import argparse, asyncio, os, sys, tempfile


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--aren', default=os.path.join(os.path.dirname(__file__), '..', '..', 'aren'))
    ap.add_argument('--out', default='/tmp/aren-shots')
    a = ap.parse_args()
    sys.path.insert(0, os.path.join(a.aren, 'tests'))
    from smoke import HOOK
    from playwright.async_api import async_playwright
    s = open(os.path.join(a.aren, 'src', 'bosque-do-enxame.html'), encoding='utf-8').read()
    i = s.rfind('})();\n</script>')
    # cabeçalho como o do build (body sem margem), áudio desligado
    s = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
         '<style>[hidden]{display:none!important}body{margin:0}</style>\n' + s[:i] + HOOK + s[i:])
    j = s.find('<script>')
    s = s[:j] + '<script>window.AudioContext=undefined;window.webkitAudioContext=undefined;</script>\n' + s[j:]
    p = os.path.join(tempfile.mkdtemp(), 'g.html'); open(p, 'w', encoding='utf-8').write(s)
    os.makedirs(a.out, exist_ok=True)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for (w, h) in [(390, 844), (1366, 768)]:
            pg = await b.new_page(viewport={'width': w, 'height': h}, device_scale_factor=1)
            await pg.goto('file://' + p); await pg.wait_for_timeout(1200)
            await pg.screenshot(path=f'{a.out}/html_start_{w}x{h}.png')
            # cartas de nível suprimidas (G.pending = 0): a Etapa 1 do Godot ainda não tem cartas
            await pg.evaluate('''() => { const T = window.__t; window.__seed(7); T.clearAmb(); T.start(); T.P.inv = 1e9;
              for (let i = 0; i < 60*25; i++){ T.update(1/60); T.G.pending = 0; }
              for (let i = 0; i < 120; i++){ if (T.G.swing && T.G.swing.t/T.G.swing.dur > 0.45) break; T.update(1/60); T.G.pending = 0; }
              T.state = 'over'; T.hud(); T.render(1/60); }''')
            await pg.wait_for_timeout(100)
            await pg.screenshot(path=f'{a.out}/html_play_{w}x{h}.png')
            await pg.evaluate('() => { window.__t.state = "play"; window.__t.togglePause(); }'); await pg.wait_for_timeout(300)
            await pg.screenshot(path=f'{a.out}/html_pause_{w}x{h}.png')
            await pg.evaluate('() => { const T = window.__t; T.togglePause(); T.P.inv = 0; T.hurt(999); }'); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{a.out}/html_over_{w}x{h}.png')
            await pg.close()
        await b.close()
    print('capturas do HTML em', a.out)

asyncio.run(main())
