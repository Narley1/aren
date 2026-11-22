"""Efeitos em pixel (sem borrão): faísca do golpe, arco do corte, nuvem da morte, poeira do passo e brilho da joia.

Cada função devolve uma lista de Canvas (quadros) do mesmo tamanho, com o centro do efeito no meio do quadro.
`s` = 1 (Opção A) ou 2 (Opção B). Tudo calculado por pixel inteiro, determinístico.
"""
from __future__ import annotations

import math
import numpy as np
from pixel import Canvas, mask_ellipse, hexrgb
from paleta import RAMPAS as R

F = R['faisca']
CT = R['corte']
FU = R['fumaca']
PO = R['poeira']
BR = R['brilho']


def _ray(c, cx, cy, ang, r0, r1, cols, width=1):
    """Raio de r0 a r1 no ângulo `ang`: cor cols[0] perto do centro → cols[-1] na ponta."""
    a = math.radians(ang)
    n = max(1, int(r1 - r0))
    for i in range(n + 1):
        r = r0 + (r1 - r0) * i / n
        x = cx + math.cos(a) * r
        y = cy + math.sin(a) * r
        col = cols[min(len(cols) - 1, int(i / (n + 1) * len(cols)))]
        c.px(math.floor(x), math.floor(y), col, 'fx')
        if width > 1:
            c.px(math.floor(x - math.sin(a) * 0.9), math.floor(y + math.cos(a) * 0.9), col, 'fx')


def hit_spark(s=1):
    """Faísca de acerto: 4 quadros, estrela que abre e se quebra em fagulhas."""
    n = 13 * s
    cx = cy = n / 2
    fr = []
    # 0: núcleo branco + cruz curta
    c = Canvas(n, n)
    m = mask_ellipse(n, n, cx, cy, 1.6 * s, 1.6 * s)
    c.fill(mask_ellipse(n, n, cx, cy, 2.4 * s, 2.4 * s), F[2], 'fx')
    c.fill(m, F[3], 'fx')
    for ang in (0, 90, 180, 270):
        _ray(c, cx, cy, ang, 2 * s, 4 * s, [F[3], F[2], F[1]], width=s)
    fr.append(c)
    # 1: estrela grande de 8 pontas (as retas mais longas)
    c = Canvas(n, n)
    c.fill(mask_ellipse(n, n, cx, cy, 2.0 * s, 2.0 * s), F[3], 'fx')
    for ang in (0, 90, 180, 270):
        _ray(c, cx, cy, ang, 1 * s, 6 * s, [F[3], F[3], F[2], F[1], F[0]], width=s)
    for ang in (45, 135, 225, 315):
        _ray(c, cx, cy, ang, 1 * s, 4 * s, [F[3], F[2], F[1]], width=1)
    fr.append(c)
    # 2: miolo apagando, raios soltos do centro
    c = Canvas(n, n)
    for ang in (0, 90, 180, 270):
        _ray(c, cx, cy, ang, 3 * s, 6 * s, [F[2], F[1], F[0]], width=s)
    for ang in (45, 135, 225, 315):
        _ray(c, cx, cy, ang, 3 * s, 5 * s, [F[1], F[0]])
    c.fill(mask_ellipse(n, n, cx, cy, 1.0 * s, 1.0 * s), F[2], 'fx')
    fr.append(c)
    # 3: fagulhas
    c = Canvas(n, n)
    for ang in (20, 110, 200, 290, 65, 245):
        a = math.radians(ang)
        r = 5.5 * s
        x, y = cx + math.cos(a) * r, cy + math.sin(a) * r
        c.px(math.floor(x), math.floor(y), F[1], 'fx')
        if s == 2:
            c.px(math.floor(x) + 1, math.floor(y), F[0], 'fx')
            c.px(math.floor(x), math.floor(y) + 1, F[0], 'fx')
    fr.append(c)
    return fr


def slash(direction_deg, s=1, sweep=144, frames=5):
    """Arco do corte da espada (smear): crescente que varre `sweep` graus no sentido horário, centrado em
    `direction_deg` (0 = direita, 90 = baixo). Quadro 44×44 (A) / 88×88 (B); centro = centro de Aren."""
    n = 44 * s
    cx = cy = n / 2
    r_out = 17.5 * s
    yy, xx = np.mgrid[0:n, 0:n]
    dx = xx + 0.5 - cx
    dy = yy + 0.5 - cy
    rr = np.hypot(dx, dy)
    th = np.degrees(np.arctan2(dy, dx))
    start = direction_deg - sweep / 2
    rel = (th - start) % 360           # 0 no começo do golpe, cresce no sentido horário
    t = rel / sweep                    # 0..1 dentro do arco
    inarc = rel <= sweep
    # janelas visíveis (ponta da frente, cauda) por quadro, em t
    win = [(0.0, 0.3), (0.0, 0.65), (0.1, 1.0), (0.55, 1.0), (0.8, 1.0)][:frames]
    fr = []
    for k, (t0, t1) in enumerate(win):
        c = Canvas(n, n)
        head = t1
        # espessura: máxima perto da ponta da frente, afinando na cauda
        u = np.clip((t - t0) / max(0.01, (head - t0)), 0, 1)   # 0 na cauda, 1 na ponta
        thick = (1.5 + 6.0 * np.sin(np.clip(u, 0, 1) ** 0.8 * math.pi * 0.62)) * s
        if k >= 3:
            thick = thick * (0.6 if k == 3 else 0.35)
        r_in = r_out - thick
        band = inarc & (t >= t0) & (t <= t1) & (rr <= r_out) & (rr >= r_in)
        if k == 4:
            # se desfaz: só pixels alternados
            band &= ((xx + yy) % 2 == 0)
        # cor: borda de fora branca, depois azul-claro, por dentro azul; a cauda escurece
        q = (rr - r_in) / np.maximum(thick, 0.01)      # 0 dentro, 1 fora
        idx = np.where(q > 0.78, 3, np.where(q > 0.45, 2, np.where(q > 0.18, 1, 0)))
        idx = idx - np.where(u < 0.25, 1, 0) - (1 if k >= 3 else 0)
        idx = np.clip(idx, 0, 3)
        for j in range(4):
            mk = band & (idx == j)
            if mk.any():
                c.fill(mk, CT[j], 'fx')
        # brilho na ponta da frente (quadros 0 e 1)
        if k <= 1:
            a = math.radians(start + head * sweep)
            for r in np.arange(r_out - 4 * s, r_out + 0.5, 0.5):
                c.px(math.floor(cx + math.cos(a) * r), math.floor(cy + math.sin(a) * r), CT[3], 'fx')
        fr.append(c)
    return fr


def _cloud(n_w, n_h, puffs, ramp, s, outline=None):
    """Nuvem: união de bolinhas pintadas com volume (luz de cima à esquerda)."""
    c = Canvas(n_w, n_h)
    m = np.zeros((n_h, n_w), bool)
    for (x, y, r) in puffs:
        m |= mask_ellipse(n_w, n_h, x * s, y * s, r * s, r * s)
    if not m.any():
        return c
    c.shade(m, ramp, 'fumaca', radius=1.6 * s, base=len(ramp) - 1, hilite=False, step=0.22)
    if outline:
        c.outline({'fumaca': outline}, default=outline)
    return c


def poof(s=1):
    """Nuvem de fumaça da morte: 5 quadros (abre, incha, se divide, bolinhas, some)."""
    W, H = 26, 22
    seq = [
        [(13, 13, 3.5), (11, 11.5, 2.5), (15.5, 12, 2.5)],
        [(9, 13, 4.5), (17, 13, 4.5), (13, 9.5, 5), (13, 15, 4)],
        [(7, 13, 4), (19, 13, 4), (11, 7.5, 3.8), (16, 7, 3.6), (13, 16, 3.5), (13, 11.5, 3.5)],
        [(5, 12, 2.8), (21, 12, 2.8), (10, 5, 2.5), (17, 4.5, 2.4), (13, 17, 2.2)],
        [(4, 11, 1.4), (22, 11, 1.4), (10, 3, 1.2), (18, 2.5, 1.2), (13, 18, 1.0)],
    ]
    out = []
    for k, puffs in enumerate(seq):
        c = _cloud(W * s, H * s, puffs, FU, s, outline='#3a3a5a')
        out.append(c)
    return out


def step_dust(s=1):
    """Poeira do passo: 3 quadros pequenos (10×6 A), nasce no pé e se espalha para os lados."""
    W, H = 12, 7
    seq = [
        [(4.5, 4.8, 1.7), (7.5, 4.8, 1.7), (6, 3.8, 1.5)],
        [(3, 4.2, 2.2), (9, 4.2, 2.2), (6, 3.2, 1.4)],
        [(1.6, 3.6, 1.3), (10.4, 3.6, 1.3), (6, 2.0, 0.8)],
    ]
    return [_cloud(W * s, H * s, p, PO, s, outline='#6a5038') for p in seq]


def gem_sparkle(s=1):
    """Brilho ao pegar joia: estrela de 4 pontas que pisca e solta pontinhos (5 quadros, 13×13 A)."""
    n = 13 * s
    cx = cy = n / 2
    out = []
    specs = [(1, 0, 0), (2.5, 1, 0), (5.5, 2, 1), (4, 1.5, 0), (0, 0, 2)]
    for k, (L, core, dots) in enumerate(specs):
        c = Canvas(n, n)
        if L:
            for ang in (0, 90, 180, 270):
                _ray(c, cx, cy, ang, 0, L * s, [BR[3], BR[2], BR[1], BR[0]], width=1)
            if core >= 1:
                c.fill(mask_ellipse(n, n, cx, cy, core * s * 0.8, core * s * 0.8), BR[3], 'fx')
            if core >= 2:
                for ang in (45, 135, 225, 315):
                    _ray(c, cx, cy, ang, 1 * s, 2.5 * s, [BR[2], BR[1]])
        if dots:
            for ang in (45, 135, 225, 315) if dots == 1 else (20, 110, 200, 290):
                a = math.radians(ang)
                r = (4.2 if dots == 1 else 5.5) * s
                c.px(math.floor(cx + math.cos(a) * r), math.floor(cy + math.sin(a) * r),
                     BR[2] if dots == 1 else BR[1], 'fx')
        if k == 0:
            c.px(math.floor(cx), math.floor(cy), BR[3], 'fx')
        out.append(c)
    return out


# ---------------------------------------------------------------- versões antigas (para o Antes/Agora)
# O jogo atual faz estes efeitos com partículas sem textura (CPUParticles2D) e um arco calculado num shader;
# no laboratório o "Antes" desses efeitos é desenhado em JavaScript imitando o jogo.
