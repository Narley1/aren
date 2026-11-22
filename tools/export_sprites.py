#!/usr/bin/env python3
"""Exporta os sprites do jogo HTML (Aren, o Guardião do Bosque) para PNG em escala 1x, pixel por pixel.

O jogo HTML desenha todos os sprites em código (canvas). Este script carrega o arquivo do jogo no Chromium
headless (Playwright), injeta um gancho no fim do IIFE (só numa cópia temporária; o original não muda), pega
os canvases que o próprio jogo gera e grava cada conjunto como uma tira horizontal de quadros do mesmo tamanho.

Saídas (relativas à raiz deste repositório):
  assets/sprites/*.png        tiras de quadros (herói, goblin, espada, joias, corações, carimbos do chão, árvores,
                              nuvem, dígitos de dano...)
  assets/sprites/sprites.json manifesto: nome -> {file, w, h, n, ...}
  assets/font/digitos.png     dígitos 3x5 dos números de dano (fonte de imagem)
  assets/sprites/ground_palette.json  paleta do chão do HTML (GP), usada por tools/make_tileset.py
  tests/ref/html_numbers.json   números do BAL/ET/xpNeed lidos do HTML (o teste compara com Bal.gd)

Os quadros "virado para a esquerda", o clarão branco e o contorno dourado não são exportados: no Godot a esquerda é
o lado espelhado (flip_h) e o clarão/contorno vêm de um shader (assets/shaders/inimigo.gdshader).

    python3 tools/export_sprites.py                         # lê ../aren/src/bosque-do-enxame.html
    python3 tools/export_sprites.py --src /caminho/jogo.html
"""
import argparse, asyncio, base64, json, os, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.normpath(os.path.join(ROOT, '..', 'aren', 'src', 'bosque-do-enxame.html'))

HOOK = r'''
window.__EXP = {
  HERO, ET, SWORDS, SWORD_N, GEM_G, GEM_B, GEM_R, HEART_ROWS, mk, STAMPS, PROP_TYPES, shadow, GCH, GP, buildCloud,
  BAL, xpNeed, isPickLevel, TT: typeof TT !== 'undefined' ? TT : null, buildLogo, DIG
};
'''

COLLECT = r"""async () => {
  const X = window.__EXP, out = {}, nums = {};
  const url = c => c.toDataURL('image/png');
  // a strip: frames side by side, all frames must share one size (the game anchors by width/height)
  // pad = transparent border around each frame (room for the shader outline of elite enemies)
  function strip(name, frames, extra, pad = 0){
    const w0 = frames[0].width, h0 = frames[0].height, w = w0 + 2*pad, h = h0 + 2*pad;
    for (const f of frames) if (f.width !== w0 || f.height !== h0) throw new Error(name + ': quadros de tamanhos diferentes');
    const c = document.createElement('canvas'); c.width = w*frames.length; c.height = h;
    const g = c.getContext('2d'); g.imageSmoothingEnabled = false;
    frames.forEach((f, i) => g.drawImage(f, i*w + pad, pad));
    out[name] = Object.assign({w, h, n: frames.length, png: url(c)}, pad ? {pad} : {}, extra || {});
  }
  // Aren: 3 directions x 4 walk frames (left = side mirrored: flip_h in Godot)
  for (const d of ['down', 'up', 'side']) strip('hero_' + d, X.HERO[d]);
  // goblin: normal frames per direction (hit flash and elite outline come from a shader in Godot)
  const gob = X.ET.goblin;
  for (const d of ['down', 'up', 'side']) strip('goblin_' + d, gob.dirs[d].map(f => f.n), null, 1);
  // sword: the 48 pre-rotated sprites (index k = angle k/48 turn), R = half size (drawn at x - R, y - R);
  // in Godot they are the 48 frames of the "girar" animation in assets/sprites/espada.tres
  const set = X.SWORDS.n, rot = [];
  for (let k = 0; k < X.SWORD_N; k++) rot.push(set.get(k));
  strip('sword', rot, {R: set.R});
  // cloud shadow (drawn at alpha .12, drifting)
  strip('cloud', [X.buildCloud()]);
  let digits = null;
  // damage digits: white 3x5 glyphs in 4x5 cells (image font; the shadow is the Label's shadow)
  { const c = document.createElement('canvas'); c.width = 40; c.height = 5; const g = c.getContext('2d'); g.fillStyle = '#ffffff';
    X.DIG.forEach((p, d) => { for (let j = 0; j < 15; j++) if (p[j] === '1') g.fillRect(d*4 + (j % 3), (j/3) | 0, 1, 1); });
    digits = url(c); }
  strip('gem_g', [X.GEM_G]); strip('gem_b', [X.GEM_B]); strip('gem_r', [X.GEM_R]);
  // HUD hearts, same recipe as heartImg() (it only keeps data URLs)
  const heart = cols => X.mk(X.HEART_ROWS.map(r => r.split('').map((ch, x) => (ch === 'r' || ch === 'w') && x >= cols ? 'k' : ch).join('')),
    {o:'#170d12', r:'#ef4a4a', w:'#ffd0d0', k:'#4a2a33'});
  strip('heart_full', [heart(9)]); strip('heart_half', [heart(4)]); strip('heart_empty', [heart(0)]);
  // ground stamps (decals baked into the ground chunks)
  for (const k in X.STAMPS) strip('stamp_' + k, [X.STAMPS[k]]);
  // props with their sway frames and anchors (ox, oy) and shadow width (sh)
  for (const k in X.PROP_TYPES){ const t = X.PROP_TYPES[k]; strip('prop_' + k, t.fr, {ox: t.ox, oy: t.oy, sh: t.sh}); }
  // shadows: hero (12), goblin (w*.75) and props
  const widths = new Set([12, Math.max(4, Math.round(gob.w*.75))]);
  for (const k in X.PROP_TYPES) widths.add(Math.max(4, Math.round(X.PROP_TYPES[k].sh)));
  for (const w of widths) strip('shadow_' + w, [X.shadow(w)]);
  // title logo (needs the Pixelify font: wait for it, then build it the game's way)
  try { await document.fonts.load('700 46px "Pixelify Sans"'); await document.fonts.load('600 11px "Pixelify Sans"'); } catch (e) {}
  try { strip('logo', [X.buildLogo()]); } catch (e) { out.__logoError = String(e); }
  // ground palette (GP) for the tileset tool
  const pal = {}; for (const k in X.GP){ const c = X.GP[k]; pal[k] = '#' + [c[0], c[1], c[2]].map(v => v.toString(16).padStart(2, '0')).join(''); }
  // numbers the Godot Bal autoload must match
  const B = X.BAL;
  nums.hero = B.hero; nums.sword = B.sword; nums.xp = B.xp; nums.spawn = B.spawn; nums.horde = B.horde; nums.elite = B.elite;
  nums.hpScaleT = B.hpScaleT; nums.hpScaleQ = B.hpScaleQ; nums.drops = B.drops; nums.weights = B.weights;
  const g = X.ET.goblin; nums.goblin = {hp: g.hp, spd: g.spd, dmg: g.dmg, r: g.r, sc: g.sc, gem: g.gem, w: g.w, h: g.h};
  nums.xpNeed = []; for (let L = 1; L <= 30; L++) nums.xpNeed.push(X.xpNeed(L));
  nums.pickLevels = []; for (let L = 2; L <= 30; L++) if (X.isPickLevel(L)) nums.pickLevels.push(L);
  nums.swordN = X.SWORD_N; nums.GCH = X.GCH; nums.DIG = X.DIG;
  return {out, pal, nums, digits};
}"""


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--src', default=DEFAULT_SRC, help='arquivo do jogo HTML (padrão: ../aren/src/bosque-do-enxame.html)')
    ap.add_argument('--out', default=os.path.join(ROOT, 'assets', 'sprites'))
    ap.add_argument('--ref', default=os.path.join(ROOT, 'tests', 'ref'))
    a = ap.parse_args()
    from playwright.async_api import async_playwright
    s = open(a.src, encoding='utf-8').read()
    i = s.rfind('})();\n</script>')
    if i < 0:
        raise SystemExit('não achei o fim do IIFE do jogo em ' + a.src)
    # the game file is a fragment: add the head the build/artifact shell would add
    s = '<!doctype html><meta charset="utf-8"><style>[hidden]{display:none!important}</style>\n' + s[:i] + HOOK + s[i:]
    tmp = tempfile.mkdtemp(prefix='aren-exp-'); p = os.path.join(tmp, 'g.html')
    open(p, 'w', encoding='utf-8').write(s)
    async with async_playwright() as pw:
        b = await pw.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://' + p); await pg.wait_for_timeout(600)
        r = await pg.evaluate(COLLECT)
        await b.close()
    if errs:
        print('avisos da página:', errs[:3])
    os.makedirs(a.out, exist_ok=True); os.makedirs(a.ref, exist_ok=True)
    out = r['out']
    if '__logoError' in out:
        print('logo não exportado:', out.pop('__logoError'))
    manifest = {}
    for name, d in sorted(out.items()):
        fn = name + '.png'
        open(os.path.join(a.out, fn), 'wb').write(base64.b64decode(d.pop('png').split(',', 1)[1]))
        manifest[name] = dict(file=fn, **d)
    json.dump(manifest, open(os.path.join(a.out, 'sprites.json'), 'w'), indent=1, sort_keys=True)
    json.dump(r['pal'], open(os.path.join(a.out, 'ground_palette.json'), 'w'), indent=1, sort_keys=True)
    # fonte de imagem dos números de dano (importada pelo Godot como FontFile: digitos.png.import)
    open(os.path.join(ROOT, 'assets', 'font', 'digitos.png'), 'wb').write(base64.b64decode(r['digits'].split(',', 1)[1]))
    json.dump(r['nums'], open(os.path.join(a.ref, 'html_numbers.json'), 'w'), indent=1, sort_keys=True)
    print(f'{len(manifest)} sprites e ground_palette.json em {a.out}; html_numbers.json em {a.ref}')


if __name__ == '__main__':
    asyncio.run(main())
