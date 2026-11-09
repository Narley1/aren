#!/usr/bin/env python3
"""Gera os ícones do site (dist/icons/*.png) e a imagem de compartilhamento (dist/og-image.png).

Carrega src/bosque-do-enxame.html no Chromium headless (sem iniciar a partida), com um gancho dentro do IIFE
que expõe o herói, os inimigos e o chão do próprio jogo (como tests/smoke.py e tools/sprite_sheet.py), e
desenha os ícones a partir deles. Nada no jogo é alterado: o gancho só existe numa cópia temporária.

    python3 tools/gen_assets.py                    # grava em ./dist
    python3 tools/gen_assets.py --out /tmp/d       # grava em /tmp/d/icons e /tmp/d/og-image.png
    python3 tools/gen_assets.py --from-main        # não desenha: copia os ícones publicados no branch main

Se o desenho falhar (sem Playwright/Chromium, por exemplo), use --from-main ou --fallback-main (tenta desenhar
e, se der erro, copia do main). Copiar do main lê origin/main (rode `git fetch` antes) e nunca escreve no main.
"""
import argparse, asyncio, base64, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'bosque-do-enxame.html')
FILES = {'i512': 'icons/icon-512.png', 'i192': 'icons/icon-192.png', 'm512': 'icons/maskable-512.png',
         'apple': 'icons/apple-touch-icon.png', 'fav': 'icons/favicon-32.png', 'og': 'og-image.png'}
HOOK = ('\nwindow.__GA = {HERO, ET, GCH, groundChunk, dirtN, tallN, DIRT_T, TALL_T};\n')

JS = r"""
async () => {
  const D = window.__GA, H = D.HERO.down[0], ET = D.ET, dirtN = D.dirtN, tallN = D.tallN, DIRT_T = D.DIRT_T, TALL_T = D.TALL_T;
  await document.fonts.load('700 120px "Pixelify Sans"'); await document.fonts.load('600 40px "Pixelify Sans"');
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.imageSmoothingEnabled = false; return [c, g]; };
  // find a grassy 48x48 window
  let gx = 0, gy = 0;
  outer: for (let y = -400; y < 400; y += 16) for (let x = -400; x < 400; x += 16){
    let ok = true;
    for (let yy = 0; yy <= 48 && ok; yy += 6) for (let xx = 0; xx <= 48 && ok; xx += 6) if (dirtN(x + xx, y + yy) > DIRT_T - .06 || tallN(x + xx, y + yy) > TALL_T - .02) ok = false;
    if (ok){ gx = x; gy = y; break outer; }
  }
  const ground = (g, wx, wy, ww, wh, k) => {
    for (let j = Math.floor(wy/D.GCH); j <= Math.floor((wy + wh)/D.GCH); j++) for (let i = Math.floor(wx/D.GCH); i <= Math.floor((wx + ww)/D.GCH); i++)
      g.drawImage(D.groundChunk(i, j), (i*D.GCH - wx)*k, (j*D.GCH - wy)*k, D.GCH*k, D.GCH*k);
  };
  const shadowE = (g, cx, cy, rx, ry) => { g.fillStyle = 'rgba(16,40,22,.38)'; g.beginPath(); g.ellipse(cx, cy, rx, ry, 0, 0, Math.PI*2); g.fill(); };
  const icon = (size, heroFrac, bg) => {
    const [c, g] = mk(size, size);
    const k = Math.max(1, Math.floor(size*heroFrac/H.height));
    if (bg){ const area = size/k; ground(g, gx, gy, area, area, k); const v = g.createRadialGradient(size/2, size/2, size*.2, size/2, size/2, size*.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(8,20,16,.45)'); g.fillStyle = v; g.fillRect(0, 0, size, size); }
    const hw = H.width*k, hh = H.height*k, x = Math.round((size - hw)/2), y = Math.round((size - hh)/2 + k*.5);
    if (bg) shadowE(g, size/2, y + hh - k*1.2, hw*.36, k*1.6);
    g.drawImage(H, x, y, hw, hh);
    return c.toDataURL('image/png');
  };
  const fav = (() => { const [c, g] = mk(32, 32); const k = 2, cropH = 15; g.drawImage(H, 0, 0, H.width, cropH, Math.round((32 - H.width*k)/2), 1, H.width*k, cropH*k); return c.toDataURL('image/png'); })();
  // OG image
  const [o, og] = mk(1200, 630), K = 4, WW = 300, WH = 158;
  const ox = gx - 120, oy = gy - 60;
  ground(og, ox, oy, WW, WH, K);
  const S = (img, wx, wy, k = K) => og.drawImage(img, Math.round((wx - ox)*K - img.width*k/2), Math.round((wy - oy)*K - img.height*k), img.width*k, img.height*k);
  const hxw = ox + 78, hyw = oy + 92;
  const foes = [['goblin', -36, -6], ['goblin', 30, -16], ['hobgoblin', -22, 30], ['orc', 46, 34], ['demon', -58, 22], ['goblin', 14, 44], ['elf', -8, -40]];
  const fly = [['succubus', 52, -46], ['gargoyle', -56, -44]];
  const list = [];
  for (const [k, dx, dy] of foes){ const d = ET[k], face = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'left' : 'side') : (dy > 0 ? 'up' : 'down'); list.push({y:hyw + dy, img:d.dirs[face][(dx + dy + 64) % 4].n, x:hxw + dx}); }
  list.push({y:hyw, img:H, x:hxw});
  list.sort((a, b) => a.y - b.y);
  for (const it of list){ shadowE(og, (it.x - ox)*K, (it.y - oy)*K - 2, it.img.width*K*.3, K*1.6); S(it.img, it.x, it.y); }
  for (const [k, dx, dy] of fly){ const d = ET[k]; S(d.dirs.all[1].n, hxw + dx, hyw + dy - 6); }
  // sword slash: pixel crescent
  { const cx0 = hxw - ox, cy0 = hyw - 9 - oy;
    for (let a = -1.25; a <= .55; a += .02){ const q = (a + 1.25)/1.8;
      for (let r = 17 - q*4; r <= 19; r += .5){ const x = Math.round((cx0 + Math.cos(a)*r)*2)/2, y = Math.round((cy0 + Math.sin(a)*r)*2)/2;
        og.fillStyle = r > 18.4 ? '#5fa8f0' : q > .55 ? '#ffffff' : '#bfe6ff'; og.globalAlpha = .35 + q*.65; og.fillRect(x*K, y*K, K/2, K/2); } }
    og.globalAlpha = 1; }
  // title panel
  const px = 640, py = 150, pw = 520, ph = 330;
  og.fillStyle = 'rgba(9,16,22,.55)'; og.fillRect(px + 14, py + 14, pw, ph);
  og.fillStyle = '#1b3a4c'; og.fillRect(px, py, pw, ph);
  og.strokeStyle = '#f2c14e'; og.lineWidth = 10; og.strokeRect(px + 5, py + 5, pw - 10, ph - 10);
  og.strokeStyle = '#a8781c'; og.lineWidth = 5; og.strokeRect(px + 15, py + 15, pw - 30, ph - 30);
  og.textBaseline = 'alphabetic';
  og.fillStyle = '#a9c6d2'; og.font = '600 26px "Pixelify Sans"'; og.fillText('SOBREVIVÊNCIA · PIXEL 2D', px + 44, py + 72);
  og.font = '700 150px "Pixelify Sans"'; og.fillStyle = '#0b1218'; og.fillText('Aren', px + 50, py + 212); og.fillStyle = '#f2c14e'; og.fillText('Aren', px + 42, py + 204);
  og.font = '600 40px "Pixelify Sans"'; og.fillStyle = '#0b1218'; og.fillText('o Guardião do Bosque', px + 47, py + 266); og.fillStyle = '#f6f1e3'; og.fillText('o Guardião do Bosque', px + 44, py + 263);
  og.font = '600 26px "Pixelify Sans"'; og.fillStyle = '#8ad65a'; og.fillText('Jogue grátis no navegador', px + 44, py + 306);
  return {i512:icon(512, .7, true), i192:icon(192, .7, true), m512:icon(512, .5, true), apple:icon(180, .66, true), fav, og:o.toDataURL('image/png'), at:[gx, gy]};
}
"""


async def draw(src, out):
    from playwright.async_api import async_playwright
    s = open(src, encoding='utf-8').read()
    i = s.rfind('})();\n</script>')
    if i < 0:
        raise RuntimeError('não achei o fim do IIFE do jogo')
    s = '<meta charset="utf-8"><style>[hidden]{display:none!important}</style>\n' + s[:i] + HOOK + s[i:]
    tmp = tempfile.mkdtemp(prefix='ga-'); p = os.path.join(tmp, 'g.html')
    open(p, 'w', encoding='utf-8').write(s)
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        pg = await b.new_page(viewport={'width': 420, 'height': 800})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + p)
        await pg.wait_for_timeout(800)
        r = await pg.evaluate(JS)
        await b.close()
    for k, rel in FILES.items():
        open(os.path.join(out, rel), 'wb').write(base64.b64decode(r[k].split(',', 1)[1]))
    print('ícones desenhados; grama em', r['at'], ('avisos da página: ' + '; '.join(errs[:3])) if errs else '')


def from_main(out):
    for rel in FILES.values():
        try:
            data = subprocess.run(['git', '-C', ROOT, 'show', 'origin/main:' + rel], check=True, capture_output=True).stdout
        except subprocess.CalledProcessError as e:
            raise SystemExit(f'ERRO: não consegui ler {rel} do origin/main (rode git fetch): {e.stderr.decode().strip()}')
        open(os.path.join(out, rel), 'wb').write(data)
    print('ícones copiados do origin/main')


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=SRC)
    ap.add_argument('--out', default='dist', help='pasta do build (padrão: ./dist)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('--from-main', action='store_true', help='copiar os ícones do origin/main em vez de desenhar')
    g.add_argument('--fallback-main', action='store_true', help='desenhar; se falhar, copiar do origin/main')
    a = ap.parse_args()
    os.makedirs(os.path.join(a.out, 'icons'), exist_ok=True)
    if a.from_main:
        return from_main(a.out)
    try:
        asyncio.run(draw(a.src, a.out))
    except Exception as e:
        if not a.fallback_main:
            raise SystemExit(f'ERRO ao desenhar os ícones: {e}\nUse --fallback-main ou --from-main para copiar os do main.')
        print('aviso: desenho falhou (' + str(e).splitlines()[0] + '); copiando do main', file=sys.stderr)
        from_main(a.out)


if __name__ == '__main__':
    main()
