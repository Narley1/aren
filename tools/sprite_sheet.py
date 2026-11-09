#!/usr/bin/env python3
"""Folha de contato de todos os sprites do jogo, ampliados em escala inteira, sobre fundo escuro e claro.

Carrega src/bosque-do-enxame.html no Chromium headless (sem iniciar a partida), pega os sprites que o
próprio jogo gera (herói, inimigos, chefes, ícones) e desenha tudo numa imagem PNG para revisão.
Nada no jogo é alterado: o gancho que expõe os sprites só existe na cópia temporária.

    python3 tools/sprite_sheet.py --out /tmp/sprites.png            # 3x
    python3 tools/sprite_sheet.py --out /tmp/s.png --zoom 5 --only hero,paladin,lich,icons
"""
import argparse, asyncio, base64, os, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'bosque-do-enxame.html')
NAMES = ['HERO', 'ET', 'ICONS', 'palArt', 'lichArt', 'BONE_SPR', 'GBLADE', 'dragonSprite']
HOOK = '\nwindow.__SPR = (() => { const o = {};\n' + ''.join(
    f'  try {{ o.{n} = {n}; }} catch {{}}\n' for n in NAMES) + '  return o; })();\n'

COLLECT = r"""([zoom, only]) => {
  const S = window.__SPR, want = k => !only || only.includes(k), items = [];
  const cv = x => x && (x.n || x);                       // EFrame -> canvas
  if (want('hero') && S.HERO) for (const d of ['down', 'side', 'up']) items.push(['hero ' + d, S.HERO[d]]);
  if (S.ET) for (const k in S.ET){
    if (!want(k) || k === 'paladin' || k === 'lich' || k === 'dragon') continue;
    const dirs = S.ET[k].dirs || {}; const d = dirs.down || dirs.all; if (d) items.push([k, d.map(cv)]);
    if (dirs.side) items.push([k + ' side', dirs.side.map(cv)]);
  }
  if (want('paladin') && S.palArt){ const a = S.palArt(); items.push(['paladin', Object.values(a.fr).map(p => cv(p[0]))]); items.push(['paladin spirit', a.spirit]); }
  if (want('lich') && S.lichArt){ const a = S.lichArt(); items.push(['lich', Object.values(a.fr).map(p => cv(p[0]))]); }
  if (want('dragon') && S.dragonSprite){ try { items.push(['dragon', [S.dragonSprite(0, 1), S.dragonSprite(1, 1)]]); } catch {} }
  if (want('icons') && S.ICONS) items.push(['icons', Object.values(S.ICONS).map(i => i.spr)]);
  if (want('bone') && S.BONE_SPR) items.push(['bone', [S.BONE_SPR]]);
  const pad = 8, lab = 16, grounds = ['#2b4a26', '#e9e3cf'];
  let W = 0, H = pad;
  const rows = items.map(([name, frames]) => { frames = frames.filter(Boolean);
    const w = frames.reduce((s, f) => s + f.width*zoom + pad, pad), h = Math.max(...frames.map(f => f.height))*zoom;
    W = Math.max(W, w); const r = {name, frames, y: H, h}; H += lab + h + pad; return r; });
  const out = document.createElement('canvas'); out.width = W*2 + pad; out.height = H;
  const g = out.getContext('2d'); g.imageSmoothingEnabled = false;
  g.fillStyle = '#13202a'; g.fillRect(0, 0, out.width, out.height);
  grounds.forEach((col, gi) => {
    const ox = gi*(W + pad); g.fillStyle = col; g.fillRect(ox, 0, W, H);
    for (const r of rows){
      g.fillStyle = gi ? '#13202a' : '#f6f1e3'; g.font = '12px monospace'; g.fillText(r.name + '  (' + r.frames.map(f => f.width + 'x' + f.height)[0] + ')', ox + pad, r.y + 12);
      let x = ox + pad; for (const f of r.frames){ g.drawImage(f, x, r.y + lab + (r.h - f.height*zoom), f.width*zoom, f.height*zoom); x += f.width*zoom + pad; }
    }
  });
  return {url: out.toDataURL('image/png'), count: rows.reduce((s, r) => s + r.frames.length, 0), names: rows.map(r => r.name)};
}"""


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True)
    ap.add_argument('--zoom', type=int, default=3)
    ap.add_argument('--only', help='hero, nomes de inimigos (goblin, orc...), paladin, lich, dragon, icons, bone')
    a = ap.parse_args()
    from playwright.async_api import async_playwright
    s = open(SRC, encoding='utf-8').read()
    i = s.rfind('})();\n</script>')
    if i < 0:
        raise SystemExit('não achei o fim do IIFE do jogo')
    s = '<meta charset="utf-8"><style>[hidden]{display:none!important}</style>\n' + s[:i] + HOOK + s[i:]
    tmp = tempfile.mkdtemp(prefix='spr-'); p = os.path.join(tmp, 'g.html')
    open(p, 'w', encoding='utf-8').write(s)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + p); await pg.wait_for_timeout(800)
        r = await pg.evaluate(COLLECT, [a.zoom, a.only.split(',') if a.only else None])
        await b.close()
    if errs:
        print('avisos da página:', errs[:3])
    open(a.out, 'wb').write(base64.b64decode(r['url'].split(',', 1)[1]))
    print(f"gravado {a.out}: {r['count']} quadros em {len(r['names'])} linhas ({', '.join(r['names'])})")


if __name__ == '__main__':
    asyncio.run(main())
