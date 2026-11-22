"""Folha de revisão: quadros ampliados sobre grama e sobre fundo escuro (para olhar com calma)."""
from __future__ import annotations

from PIL import Image, ImageDraw

GRAMA = (0x72, 0xcc, 0x52, 255)
ESCURO = (0x1a, 0x1c, 0x2c, 255)


def contact(rows, zoom=6, gap=2, bg=GRAMA, label_h=0):
    """rows: lista de listas de Image (cada linha uma animação). Retorna uma Image ampliada."""
    cw = max(sum(im.width + gap for im in r) for r in rows if r)
    ch = sum(max(im.height for im in r) + gap for r in rows if r)
    out = Image.new('RGBA', (cw, ch), bg)
    y = 0
    for r in rows:
        if not r:
            continue
        x = 0
        for im in r:
            out.alpha_composite(im, (x, y))
            x += im.width + gap
        y += max(im.height for im in r) + gap
    return out.resize((out.width * zoom, out.height * zoom), Image.NEAREST)


def both(rows, zoom=6, gap=2):
    a = contact(rows, zoom, gap, GRAMA)
    b = contact(rows, zoom, gap, ESCURO)
    out = Image.new('RGBA', (a.width + b.width + 8 * zoom, a.height), (40, 40, 40, 255))
    out.paste(a, (0, 0))
    out.paste(b, (a.width + 8 * zoom, 0))
    return out
