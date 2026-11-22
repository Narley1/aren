#!/usr/bin/env python3
"""Monta os atlas de tiles do chão (16x16) a partir da arte do jogo HTML: a paleta do chão (GP) e os carimbos
(tufos, trevos, flores, pedrinhas, capim alto...) exportados por tools/export_sprites.py.

O chão do HTML não tem peças prontas: cada pixel sai de um ruído (grama com manchas, capim alto listrado,
trilhas de terra com borda escura). Aqui as mesmas regras de cor viram peças de tile para o TileSet do Godot,
com "terrain sets" no modo Match Corners: cada canto do tile é Grama, Capim alto ou Terra, e o Godot (ou o
gerador do campo) escolhe a peça cujos cantos combinam — as bordas se encaixam sozinhas.

Saídas:
  assets/tiles/chao.png       atlas do terreno: 3 tiles cheios x 4 variações + transições grama/terra e
                              grama/capim (14 combinações de cantos x 2 variações cada)
  assets/tiles/detalhes.png   atlas de detalhes transparentes (tufos, trevos, flores, canteiros, pedrinhas, rachaduras)
  assets/tiles/tiles.json     o que é cada tile: cantos, terreno, probabilidade; tipo do detalhe
                              (lido por tools/build_resources.gd, que monta assets/tiles/chao.tres)

Cores "marcadoras": a grama base é pintada com g1, a terra base com d1 e o capim alto com t1. O shader do chão
(assets/shaders/chao.gdshader) troca essas três cores pelas manchas (g1/g2, d1/d2) e listras do capim usando a
posição no mundo, então não aparece emenda entre tiles. Sem o shader, o tile mostra só a cor base.

    python3 tools/make_tileset.py
"""
import json, math, os, random
from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPR = os.path.join(ROOT, 'assets', 'sprites')
OUT = os.path.join(ROOT, 'assets', 'tiles')
T = 16                       # tamanho do tile
GRASS, TALL, DIRT = 0, 1, 2  # terrenos do terrain set 0
COLS = 16                    # colunas do atlas do terreno

pal = {k: tuple(int(v[i:i + 2], 16) for i in (1, 3, 5)) + (255,) for k, v in json.load(open(os.path.join(SPR, 'ground_palette.json'))).items()}
stamps = {k: Image.open(os.path.join(SPR, 'stamp_%s.png' % k)).convert('RGBA')
          for k in ['tall', 'tuft', 'tuft2', 'clover', 'fW', 'fP', 'fY', 'fB', 'peb', 'dpeb', 'crack']}


def hsh(*a):
    """hash inteiro -> [0, 1) (determinístico entre execuções)"""
    n = 0x811C9DC5
    for v in a:
        n = ((n ^ (v & 0xFFFFFFFF)) * 0x01000193) & 0xFFFFFFFF
        n ^= n >> 13
        n = (n * 0x5BD1E995) & 0xFFFFFFFF
    n ^= n >> 15
    return n / 4294967296.0


def vnoise(x, y, seed):
    xi, yi = math.floor(x), math.floor(y)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a, b = hsh(xi, yi, seed), hsh(xi + 1, yi, seed)
    c, d = hsh(xi, yi + 1, seed), hsh(xi + 1, yi + 1, seed)
    return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


def field(corners, var, x, y):
    """Campo 0..1 dentro do tile: bilinear dos cantos (1 = terreno de cima) + ruído que some nas bordas, para
    que tiles vizinhos sempre se encontrem no mesmo ponto (sem emenda)."""
    tl, tr, bl, br = corners
    u, v = (x + 0.5) / T, (y + 0.5) / T
    f = tl * (1 - u) * (1 - v) + tr * u * (1 - v) + bl * (1 - u) * v + br * u * v
    w = math.sin(math.pi * u) * math.sin(math.pi * v)
    n = vnoise(x / 4.0, y / 4.0, 101 + var * 7 + sum(c << i for i, c in enumerate(corners)) * 31) - 0.5
    f += n * 0.42 * w
    if corners in ((1, 0, 0, 1), (0, 1, 1, 0)):   # diagonal: uma variação liga o terreno, a outra separa
        f += (0.1 if var == 0 else -0.1) * w
    return f


def grass_px(img, x, y, h):
    img.putpixel((x, y), pal['gL'] if h < 0.018 else pal['gD'] if h < 0.036 else pal['g1'])


def paint(img, ox, oy, upper, corners, var, seed):
    """Pinta um tile (cantos 1 = `upper`, 0 = grama) com as regras de cor do chão do HTML."""
    fv = {}
    for y in range(T):
        for x in range(T):
            h = hsh(x, y, seed)
            f = field(corners, var, x, y) if upper is not None else 0.0
            fv[x, y] = f
            px = (ox + x, oy + y)
            if upper == DIRT and f >= 0.5:
                if f < 0.56:   c = pal['dE'] if h < 0.5 else pal['dE2']       # borda escura da trilha
                elif f < 0.62: c = pal['dD']
                else:          c = pal['dD'] if h < 0.035 else pal['dL'] if h < 0.07 else pal['d1']
            elif upper == DIRT and f >= 0.38:                                  # grama escurecida na beira
                c = pal['gDD'] if f >= 0.44 else (pal['gD'] if h < 0.5 else pal['gDD'])
            elif upper == TALL and f >= 0.5:
                c = pal['gD'] if f < 0.56 else (pal['tL'] if h < 0.04 else pal['t1'])
            else:
                c = pal['gL'] if h < 0.018 else pal['gD'] if h < 0.036 else pal['g1']
            img.putpixel(px, c)
    if upper == TALL:   # tufos de capim alto onde o tile é todo capim (como os carimbos 'tall' do HTML)
        st = stamps['tall']
        for q in range(6):
            if hsh(q, seed, 5) > 0.85:
                continue
            sx = int(hsh(q, seed, 6) * (T - st.width + 1))
            sy = int(hsh(q, seed, 7) * (T - st.height + 1))
            if all(fv[sx + i, sy + j] >= 0.62 for i in range(st.width) for j in range(st.height) if st.getpixel((i, j))[3]):
                img.alpha_composite(st, (ox + sx, oy + sy))


def main():
    os.makedirs(OUT, exist_ok=True)
    tiles = []   # {x, y, corners [tl, tr, bl, br] (ids de terreno), terrain, probability}
    combos = [c for c in ((a, b, cc, d) for a in (0, 1) for b in (0, 1) for cc in (0, 1) for d in (0, 1)) if 0 < sum(c) < 4]
    items = []
    for t, upper in ((GRASS, None), (TALL, TALL), (DIRT, DIRT)):
        for v in range(4):
            items.append((upper, (1, 1, 1, 1) if upper is not None else (0, 0, 0, 0), v, t, 1.0 if v == 0 else 0.6))
    for upper in (DIRT, TALL):
        for c in combos:
            for v in range(2):
                items.append((upper, c, v, upper if sum(c) >= 2 else GRASS, 1.0))
    rows = (len(items) + COLS - 1) // COLS
    img = Image.new('RGBA', (COLS * T, rows * T), (0, 0, 0, 0))
    for i, (upper, c, v, terrain, prob) in enumerate(items):
        ax, ay = i % COLS, i // COLS
        paint(img, ax * T, ay * T, upper, c, v, i * 977 + 13)
        corners = [upper if k else GRASS for k in c] if upper is not None else [GRASS] * 4
        tiles.append({'x': ax, 'y': ay, 'corners': corners, 'terrain': terrain, 'probability': prob})
    img.save(os.path.join(OUT, 'chao.png'))

    # detalhes: carimbos do HTML sobre fundo transparente, com o "tipo" que o gerador usa para escolher
    dec = []
    rnd = random.Random(7)
    grass_w = [('tuft', 0.13), ('tuft2', 0.07), ('clover', 0.04), ('fW', 0.0125), ('fY', 0.0125), ('fP', 0.0125), ('fB', 0.0125), ('peb', 0.01)]

    def pick():
        r = rnd.random() * sum(w for _, w in grass_w)
        for k, w in grass_w:
            r -= w
            if r <= 0:
                return k
        return 'tuft'

    def place(canvas, ox, oy, names, spread=True):
        used = []
        for k in names:
            st = stamps[k]
            for _ in range(20):
                x = rnd.randint(1, T - st.width - 1)
                y = rnd.randint(1, T - st.height - 1)
                if not spread or all(abs(x - a) > 4 or abs(y - b) > 3 for a, b in used):
                    break
            used.append((x, y))
            canvas.alpha_composite(st, (ox + x, oy + y))

    sets = []
    for i in range(24):
        sets.append(('grama', [pick() for _ in range(1 if rnd.random() < 0.7 else 2)]))
    for f in ('fW', 'fY', 'fP', 'fB'):
        for i in range(3):
            sets.append(('flores_' + f, [f] * rnd.randint(3, 4)))
    for i in range(6):
        sets.append(('terra', ['dpeb' if rnd.random() < 0.7 else 'crack']))
    drows = (len(sets) + COLS - 1) // COLS
    dimg = Image.new('RGBA', (COLS * T, drows * T), (0, 0, 0, 0))
    for i, (kind, names) in enumerate(sets):
        ax, ay = i % COLS, i // COLS
        place(dimg, ax * T, ay * T, names)
        dec.append({'x': ax, 'y': ay, 'tipo': kind})
    dimg.save(os.path.join(OUT, 'detalhes.png'))
    json.dump({'tile': T, 'terrains': ['Grama', 'Capim alto', 'Terra'], 'chao': tiles, 'detalhes': dec},
              open(os.path.join(OUT, 'tiles.json'), 'w'), indent=1)
    print('%d tiles de terreno, %d detalhes em %s' % (len(tiles), len(dec), OUT))


if __name__ == '__main__':
    main()
