"""Tela de pixels para desenhar sprites em código (sem suavização, sem bibliotecas além de numpy/Pillow).

Cada pixel guarda uma cor RGBA e um "material" (nome da rampa de cores). O material serve para o contorno
colorido: o contorno de fora pega a cor de contorno do material vizinho, como no estilo Minish Cap.

Ferramentas principais:
- `mask_*`: máscaras (numpy bool) de elipse, retângulo, polígono, linha e grade de caracteres.
- `Canvas.shade(mask, rampa, ...)`: pinta a máscara com volume (luz de cima à esquerda). O volume vem de um
  "travesseiro" calculado pela distância até a borda da máscara, então serve para qualquer forma.
- `Canvas.fill(mask, cor)`, `Canvas.px(x, y, cor)`, `Canvas.stamp(grade, paleta, x, y)`.
- `Canvas.outline(...)`: contorno de 1 px com cor por material (mais claro em cima/esquerda, mais escuro
  embaixo/direita).
Tudo é determinístico: sem sorteios.
"""
from __future__ import annotations

import math
import numpy as np
from PIL import Image


def hexrgb(h: str) -> tuple:
    h = h.lstrip('#')
    if len(h) == 6:
        return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), 255)
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), int(h[6:8], 16))


# ---------------------------------------------------------------- máscaras

def mask_ellipse(w, h, cx, cy, rx, ry):
    """Elipse cheia com centro (cx, cy) em coordenadas de pixel (centro do pixel = x+0.5)."""
    yy, xx = np.mgrid[0:h, 0:w]
    dx = (xx + 0.5 - cx) / max(rx, 0.01)
    dy = (yy + 0.5 - cy) / max(ry, 0.01)
    return dx * dx + dy * dy <= 1.0


def mask_rect(w, h, x0, y0, x1, y1):
    """Retângulo de x0..x1-1, y0..y1-1."""
    m = np.zeros((h, w), bool)
    m[max(0, y0):max(0, y1), max(0, x0):max(0, x1)] = True
    return m


def mask_poly(w, h, pts):
    """Polígono cheio (regra par-ímpar, amostrando no centro do pixel)."""
    m = np.zeros((h, w), bool)
    n = len(pts)
    for y in range(h):
        py = y + 0.5
        xs = []
        for i in range(n):
            x1, y1 = pts[i]
            x2, y2 = pts[(i + 1) % n]
            if (y1 <= py < y2) or (y2 <= py < y1):
                xs.append(x1 + (py - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        for a, b in zip(xs[0::2], xs[1::2]):
            for x in range(w):
                if a <= x + 0.5 < b:
                    m[y, x] = True
    return m


def line_pts(x0, y0, x1, y1):
    """Bresenham inteiro."""
    x0, y0, x1, y1 = int(round(x0)), int(round(y0)), int(round(x1)), int(round(y1))
    pts = []
    dx, dy = abs(x1 - x0), -abs(y1 - y0)
    sx, sy = (1 if x0 < x1 else -1), (1 if y0 < y1 else -1)
    err = dx + dy
    while True:
        pts.append((x0, y0))
        if x0 == x1 and y0 == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x0 += sx
        if e2 <= dx:
            err += dx
            y0 += sy
    return pts


def mask_line(w, h, x0, y0, x1, y1, thick=1):
    m = np.zeros((h, w), bool)
    for x, y in line_pts(x0, y0, x1, y1):
        for oy in range(thick):
            for ox in range(thick):
                xx, yy = x + ox - (thick - 1) // 2, y + oy - (thick - 1) // 2
                if 0 <= xx < w and 0 <= yy < h:
                    m[yy, xx] = True
    return m


def mask_grid(w, h, rows, x, y, chars=None):
    """Máscara a partir de uma grade de texto: qualquer caractere diferente de '.' (ou só os de `chars`)."""
    m = np.zeros((h, w), bool)
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch == '.' or ch == ' ':
                continue
            if chars is not None and ch not in chars:
                continue
            xx, yy = x + i, y + j
            if 0 <= xx < w and 0 <= yy < h:
                m[yy, xx] = True
    return m


def dist_inside(mask):
    """Distância (chanfro 3-4, em pixels) de cada pixel da máscara até o lado de fora."""
    h, w = mask.shape
    INF = 10 ** 6
    d = np.where(mask, INF, 0).astype(np.int64)
    # bordas da tela contam como fora
    for y in range(h):
        for x in range(w):
            if d[y, x] == 0:
                continue
            best = d[y, x]
            for dx, dy, c in ((-1, 0, 3), (0, -1, 3), (-1, -1, 4), (1, -1, 4)):
                xx, yy = x + dx, y + dy
                v = d[yy, xx] + c if (0 <= xx < w and 0 <= yy < h) else c
                if v < best:
                    best = v
            d[y, x] = best
    for y in range(h - 1, -1, -1):
        for x in range(w - 1, -1, -1):
            if d[y, x] == 0:
                continue
            best = d[y, x]
            for dx, dy, c in ((1, 0, 3), (0, 1, 3), (1, 1, 4), (-1, 1, 4)):
                xx, yy = x + dx, y + dy
                v = d[yy, xx] + c if (0 <= xx < w and 0 <= yy < h) else c
                if v < best:
                    best = v
            d[y, x] = best
    return d / 3.0


# ---------------------------------------------------------------- tela

class Canvas:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.rgba = np.zeros((h, w, 4), np.uint8)
        self.mat = np.full((h, w), '', dtype=object)

    # --- básicos
    def inside(self, x, y):
        return 0 <= x < self.w and 0 <= y < self.h

    def px(self, x, y, col, mat=None):
        x, y = int(x), int(y)
        if not self.inside(x, y):
            return
        if col is None:
            self.rgba[y, x] = (0, 0, 0, 0)
            self.mat[y, x] = ''
            return
        self.rgba[y, x] = hexrgb(col) if isinstance(col, str) else col
        if mat is not None:
            self.mat[y, x] = mat
        elif self.mat[y, x] == '':
            self.mat[y, x] = '?'

    def get(self, x, y):
        if not self.inside(x, y):
            return None
        a = self.rgba[y, x]
        return None if a[3] == 0 else '#%02x%02x%02x' % tuple(a[:3])

    def opaque(self):
        return self.rgba[:, :, 3] > 0

    def fill(self, mask, col, mat=None):
        c = hexrgb(col)
        self.rgba[mask] = c
        if mat is not None:
            self.mat[mask] = mat

    def clear(self, mask):
        self.rgba[mask] = (0, 0, 0, 0)
        self.mat[mask] = ''

    def stamp(self, rows, pal, x, y, mats=None):
        """Grade de texto: cada caractere vira a cor de `pal` (None apaga). `mats` dá o material por caractere."""
        for j, row in enumerate(rows):
            for i, ch in enumerate(row):
                if ch in '. ':
                    continue
                col = pal[ch]
                m = (mats or {}).get(ch) if mats else None
                if isinstance(col, tuple) and len(col) == 2 and isinstance(col[1], str) and col[0] is not None \
                        and isinstance(col[0], str):
                    col, m = col
                self.px(x + i, y + j, col, m)

    # --- volume
    def shade(self, mask, ramp, mat=None, light=(-0.55, -0.75), radius=None, bias=0.0, levels=None,
              hilite=True, sep=None, flat=0.0, base=None, step=0.17):
        """Pinta `mask` com a rampa (escuro → claro) com volume de travesseiro e luz de cima à esquerda.

        radius: quantos px a borda leva para "subir" (padrão: metade da menor espessura, até 6).
        bias: soma ao brilho (-1..1). hilite: usa o último tom só no ponto mais iluminado.
        sep: cor para uma linha de separação de 1 px onde a máscara encosta em pixels já pintados (borda
             interna, embaixo/direita), ou None.
        flat: mistura com um degradê simples de cima para baixo (0 = só volume).
        """
        if not mask.any():
            return
        d = dist_inside(mask)
        if radius is None:
            radius = max(1.5, min(6.0, d.max() * 0.9))
        t = np.clip(d / radius, 0, 1)
        hgt = np.sqrt(np.clip(1 - (1 - t) ** 2, 0, 1))
        gy, gx = np.gradient(hgt)
        nz = np.full_like(hgt, 0.55)
        nx, ny = -gx, -gy
        ln = math.sqrt(light[0] ** 2 + light[1] ** 2 + 0.6 ** 2)
        lx, ly, lz = light[0] / ln, light[1] / ln, 0.6 / ln
        nl = np.sqrt(nx * nx + ny * ny + nz * nz)
        dot = (nx * lx + ny * ly + nz * lz) / nl
        # degradê vertical: a parte de baixo da forma fica mais escura
        ys = np.where(mask.any(axis=1))[0]
        y0, y1 = ys.min(), ys.max() + 1
        yy = np.mgrid[0:self.h, 0:self.w][0]
        vert = 1 - 2 * (yy + 0.5 - y0) / max(1, (y1 - y0))   # +1 em cima, -1 embaixo
        b = dot * (1 - flat) + vert * flat * 0.6 + bias
        n = len(ramp)
        use_hi = hilite and n >= 4
        if base is None:
            base = n - 2 if use_hi else n - 1
        top = n - 2 if use_hi else n - 1
        if levels is None:
            idx = base + np.floor((b - 0.545) / step + 0.5).astype(int)
            idx = np.clip(idx, 0, top)
        else:
            idx = np.zeros_like(b, int)
            for k, th in enumerate(levels):
                idx[b >= th] = k + 1
            idx = np.clip(idx, 0, n - 1)
        if use_hi:
            peak = b[mask].max()
            idx[(b >= peak - 0.04) & (b > 0.75) & mask] = n - 1
        prev = self.opaque().copy()
        for k in range(n):
            mk = mask & (idx == k)
            if mk.any():
                self.fill(mk, ramp[k], mat)
        if sep:
            self.separate(mask, prev, sep, mat)

    def separate(self, mask, prev, col, mat=None, sides='all'):
        """Linha de 1 px na borda de `mask` onde ela fica por cima de pixels que já existiam (`prev`)."""
        h, w = mask.shape
        edge = np.zeros_like(mask)
        dirs = {'all': ((1, 0), (-1, 0), (0, 1), (0, -1)), 'down': ((0, 1),), 'up': ((0, -1),),
                'lr': ((1, 0), (-1, 0)), 'dr': ((1, 0), (0, 1)), 'dlr': ((1, 0), (-1, 0), (0, 1)),
                'l': ((-1, 0),), 'r': ((1, 0),), 'dl': ((-1, 0), (0, 1))}[sides]
        for dx, dy in dirs:
            sh = np.zeros_like(mask)
            # pixel vizinho (x+dx, y+dy) fora da máscara mas já pintado
            src = (~mask) & prev
            if dx == 1:
                sh[:, :-1] = src[:, 1:]
            elif dx == -1:
                sh[:, 1:] = src[:, :-1]
            elif dy == 1:
                sh[:-1, :] = src[1:, :]
            elif dy == -1:
                sh[1:, :] = src[:-1, :]
            edge |= mask & sh
        self.fill(edge, col, mat)

    # --- contorno
    def outline(self, outl, default='#2a1820', light_tone=None, diag=False, inner_lr=False):
        """Contorno de 1 px por fora. `outl` mapeia material → cor (ou (cor_luz, cor_sombra)).

        A cor vem do vizinho de dentro (preferindo o de cima/esquerda para decidir o lado da luz).
        Com diag=True, cantos diagonais também recebem contorno (silhueta mais "cheia").
        """
        op = self.opaque()
        h, w = op.shape
        new = []
        for y in range(h):
            for x in range(w):
                if op[y, x]:
                    continue
                nb = []
                for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)) + (((1, 1), (-1, 1), (1, -1), (-1, -1)) if diag else ()):
                    xx, yy = x + dx, y + dy
                    if 0 <= xx < w and 0 <= yy < h and op[yy, xx]:
                        nb.append((dx, dy, self.mat[yy, xx]))
                if not nb:
                    continue
                dx, dy, m = nb[0]
                c = outl.get(m, default)
                if isinstance(c, tuple):
                    # lado da luz (o pixel de fora está em cima/esquerda da forma) usa o tom mais claro
                    lit = any(ddx > 0 or ddy > 0 for ddx, ddy, _ in nb if (ddx, ddy) in ((1, 0), (0, 1))) and \
                        not any((ddx, ddy) in ((-1, 0), (0, -1)) for ddx, ddy, _ in nb)
                    c = c[0] if lit else c[1]
                new.append((x, y, c, m))
        for x, y, c, m in new:
            self.px(x, y, c, 'outline:' + m)

    # --- utilidades
    def flipped(self):
        c = Canvas(self.w, self.h)
        c.rgba = self.rgba[:, ::-1].copy()
        c.mat = self.mat[:, ::-1].copy()
        return c

    def shifted(self, dx, dy):
        c = Canvas(self.w, self.h)
        for y in range(self.h):
            for x in range(self.w):
                if self.rgba[y, x, 3]:
                    c.rgba_set(x + dx, y + dy, self.rgba[y, x], self.mat[y, x])
        return c

    def rgba_set(self, x, y, v, m):
        if self.inside(x, y):
            self.rgba[y, x] = v
            self.mat[y, x] = m

    def paste(self, other, ox, oy):
        for y in range(other.h):
            for x in range(other.w):
                if other.rgba[y, x, 3]:
                    self.rgba_set(x + ox, y + oy, other.rgba[y, x], other.mat[y, x])

    def tinted(self, col, keep_outline=True):
        """Cópia com todos os pixels de uma cor (ex.: clarão branco), mantendo o contorno se pedido."""
        c = Canvas(self.w, self.h)
        c.rgba = self.rgba.copy()
        c.mat = self.mat.copy()
        rgb = hexrgb(col)
        for y in range(self.h):
            for x in range(self.w):
                if c.rgba[y, x, 3] and not (keep_outline and str(c.mat[y, x]).startswith('outline')):
                    c.rgba[y, x] = rgb
        return c

    def image(self):
        return Image.fromarray(self.rgba, 'RGBA')

    def bbox(self):
        op = self.opaque()
        if not op.any():
            return None
        ys = np.where(op.any(axis=1))[0]
        xs = np.where(op.any(axis=0))[0]
        return xs.min(), ys.min(), xs.max() + 1, ys.max() + 1


def sheet(frames, pad=0):
    """Junta quadros (Canvas ou Image, mesmo tamanho) numa tira horizontal."""
    ims = [f.image() if isinstance(f, Canvas) else f for f in frames]
    w, h = ims[0].size
    out = Image.new('RGBA', (len(ims) * (w + pad) - pad if ims else 0, h), (0, 0, 0, 0))
    for i, im in enumerate(ims):
        out.paste(im, (i * (w + pad), 0))
    return out


def mix(c1, c2, t):
    a, b = hexrgb(c1), hexrgb(c2)
    return '#%02x%02x%02x' % tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3))


def epx(mask):
    """Scale2x (EPX) de uma máscara booleana: dobra o tamanho suavizando as escadinhas da silhueta."""
    h, w = mask.shape
    p = np.pad(mask, 1, constant_values=False)
    A = p[0:h, 1:w + 1]      # cima
    B = p[1:h + 1, 2:w + 2]  # direita
    C = p[1:h + 1, 0:w]      # esquerda
    D = p[2:h + 2, 1:w + 1]  # baixo
    P = mask
    e0 = np.where((C == A) & (C != D) & (A != B), A, P)
    e1 = np.where((A == B) & (A != C) & (B != D), B, P)
    e2 = np.where((D == C) & (D != B) & (C != A), C, P)
    e3 = np.where((B == D) & (B != A) & (D != C), D, P)
    out = np.zeros((h * 2, w * 2), bool)
    out[0::2, 0::2] = e0
    out[0::2, 1::2] = e1
    out[1::2, 0::2] = e2
    out[1::2, 1::2] = e3
    return out


class Pen:
    """Desenha em unidades da Opção A (1 un = `s` px) dentro de uma tela maior, com deslocamento (ox, oy) em px.

    As silhuetas em grade são ampliadas com EPX quando s=2 (contorno mais liso, não só pixels dobrados);
    os detalhes finos são colocados em px de verdade com `dot`.
    """

    def __init__(self, c, s=1, ox=0, oy=0):
        self.c, self.s, self.ox, self.oy = c, s, ox, oy

    def X(self, x):
        return self.ox + int(math.floor(x * self.s + 0.5))

    def Y(self, y):
        return self.oy + int(math.floor(y * self.s + 0.5))

    def grid(self, rows, x, y, chars=None):
        s = self.s
        gw = max(len(r) for r in rows)
        m = mask_grid(gw, len(rows), rows, 0, 0, chars)
        if s == 2:
            m = epx(m)
        out = np.zeros((self.c.h, self.c.w), bool)
        X, Y = self.X(x), self.Y(y)
        hh, ww = m.shape
        for j in range(hh):
            yy = Y + j
            if not (0 <= yy < self.c.h):
                continue
            for i in range(ww):
                xx = X + i
                if m[j, i] and 0 <= xx < self.c.w:
                    out[yy, xx] = True
        return out

    def rect(self, x, y, w, h):
        return mask_rect(self.c.w, self.c.h, self.X(x), self.Y(y), self.X(x + w), self.Y(y + h))

    def dot(self, ax, ay, col, mat=None, dx=0, dy=0):
        self.c.px(self.X(ax) + dx, self.Y(ay) + dy, col, mat)

    def block(self, ax, ay, col, mat=None, w=1, h=1):
        """Bloco de w×h unidades (s·w × s·h px)."""
        for j in range(self.Y(ay), self.Y(ay + h)):
            for i in range(self.X(ax), self.X(ax + w)):
                self.c.px(i, j, col, mat)

    def cyl(self, x, y, w, h, ramp, mat, base, flip=False, cap=None):
        """Peça cilíndrica vertical (braço, perna, bota): coluna da esquerda clara, da direita escura."""
        X0, X1, Y0, Y1 = self.X(x), self.X(x + w), self.Y(y), self.Y(y + h)
        n = X1 - X0
        for i in range(n):
            k = i if not flip else n - 1 - i
            if n == 1:
                t = base
            elif k == 0:
                t = base + 1
            elif k == n - 1:
                t = base - 1
            else:
                t = base
            t = max(0, min(len(ramp) - 1, t))
            for j in range(Y0, Y1):
                tt = t
                if cap is not None and j == Y0:
                    tt = min(len(ramp) - 1, t + cap)
                self.c.px(X0 + i, j, ramp[tt], mat)


def round_corners(c, passes=1, protect=('metal', 'madeira', 'ouro', 'fx')):
    """Tira o pixel de quina da silhueta (vizinhos de cima e da esquerda vazios, etc.): cantos arredondados."""
    for _ in range(passes):
        op = c.opaque()
        h, w = op.shape
        p = np.pad(op, 1, constant_values=False)
        up, dn = p[0:h, 1:w + 1], p[2:h + 2, 1:w + 1]
        lf, rt = p[1:h + 1, 0:w], p[1:h + 1, 2:w + 2]
        n4 = up.astype(int) + dn + lf + rt
        corner = op & (n4 == 2) & ((~up & ~lf) | (~up & ~rt) | (~dn & ~lf) | (~dn & ~rt))
        keep = np.isin(c.mat, list(protect))
        c.clear(corner & ~keep)
