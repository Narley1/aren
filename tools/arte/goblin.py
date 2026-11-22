"""Goblin — Opção A (s=1, ~22×21 px com contorno) e Opção B (s=2, ~40×42 px, o dobro de detalhe).

Mesma identidade do goblin do HTML: pele verde, orelhas grandes abertas, olhos amarelos, dentes, tanga marrom
e uma faquinha. Quadro A 32×28 com o pé em (16, 25); B 64×56 com o pé em (32, 50).
"""
from __future__ import annotations

import math
from pixel import Canvas, Pen, line_pts, round_corners
from paleta import RAMPAS as R, CONTORNO

PAD_X, PAD_Y = 6, 5
CANVAS = {1: (32, 28), 2: (64, 56)}
ORIGIN = {1: (16, 25), 2: (32, 50)}
G = R['goblin']

HEAD_FRONT = [
    "......GGGGGGGG......",
    "....GGGGGGGGGGGG....",
    "...GGGGGGGGGGGGGG...",
    "EE.GGGGGGGGGGGGGG.EE",
    ".EEGGGGGGGGGGGGGGEE.",
    "..EGGGGGGGGGGGGGGE..",
    "...GGGGGGGGGGGGGG...",
    "....GGGGGGGGGGGG....",
    ".....GGGGGGGGGG.....",
    "......GGGGGGGG......",
]
HEAD = {
    'down': HEAD_FRONT,
    'up': HEAD_FRONT,
    'side': [
        "......GGGGGG........",
        "....GGGGGGGGGG......",
        "EEE.GGGGGGGGGGG.....",
        ".EEEGGGGGGGGGGGG....",
        "...EEGGGGGGGGGGGGG..",
        "....EGGGGGGGGGGGGGG.",
        ".....GGGGGGGGGGGGG..",
        ".....GGGGGGGGGGGG...",
        "......GGGGGGGGGG....",
        ".......GGGGGGGG.....",
    ],
}

BODY = {
    'down': [
        "..GGGG..",
        ".GGGGGG.",
        ".GGGGGG.",
        ".GGGGGG.",
    ],
    'side': [
        "..GGGG..",
        ".GGGGGG.",
        ".GGGGGG.",
        "..GGGGG.",
    ],
}
BODY['up'] = BODY['down']


def V(pose, key, s, default=0):
    v = pose.get(key, default)
    if isinstance(v, tuple):
        v = v[s - 1]
    return v


def knife(pen, hx, hy, ang, s):
    c = pen.c
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    X0, Y0 = pen.X(hx), pen.Y(hy)
    m = R['metal']
    # cabo
    for X, Y in line_pts(X0 - dx * s, Y0 - dy * s, X0, Y0):
        c.px(X, Y, R['madeira'][2], 'madeira')
    L = 3 * s + (1 if s == 2 else 0)
    pts = line_pts(X0 + dx, Y0 + dy, X0 + dx * L, Y0 + dy * L)
    for i, (X, Y) in enumerate(pts):
        c.px(X, Y, m[3] if i < len(pts) - 1 else m[4], 'metal')
        if s == 2 and i < len(pts) - 1:
            ox, oy = (1, 0) if abs(dy) > abs(dx) else (0, 1)
            c.px(X + ox, Y + oy, m[2], 'metal')


def face(pen, view, x0, y0, st, s, mouth_open=0):
    c = pen.c
    Y, Yw = R['olho_gob'], R['dente']
    b = R['boca']
    if view == 'down':
        if st == 'hurt':
            for ex, d in ((5, 1), (11, -1)):
                for k in range(2 * s):
                    c.px(pen.X(x0 + ex) + (k if d > 0 else 2 * s - 1 - k), pen.Y(y0 + 5) + (k % 2 if s == 1 else k // 2),
                         G[0], 'goblin')
        else:
            for ex, mir in ((5, False), (11, True)):
                pen.block(x0 + ex, y0 + 5, Y[2], 'olho_gob', w=2, h=1)
                pen.block(x0 + ex, y0 + 6, Y[1], 'olho_gob', w=2, h=1)
                # pupila
                px_ = x0 + ex + (1 if not mir else 0)
                pen.block(px_, y0 + 5, b[0], 'boca', w=1, h=1 if s == 1 else 1.5)
                if s == 2:
                    pen.dot(x0 + ex + (0 if not mir else 1.5), y0 + 5, Y[3], 'olho_gob')
                # sobrancelha brava
                bx0 = x0 + ex - (0 if not mir else 0)
                if s == 1:
                    pen.dot(x0 + ex + (0 if not mir else 1), y0 + 4, G[1], 'goblin')
                    pen.dot(x0 + ex + (1 if not mir else 0), y0 + 4, G[0], 'goblin')
                else:
                    for k in range(4):
                        X = pen.X(x0 + ex) + (k if not mir else 3 - k)
                        c.px(X, pen.Y(y0 + 4) + (k // 2), G[0] if k >= 2 else G[1], 'goblin')
        # nariz
        pen.dot(x0 + 8.5, y0 + 7, G[1], 'goblin'); pen.dot(x0 + 8.5, y0 + 7, G[4], 'goblin', dx=-1, dy=-1)
        # boca com dentes
        mw = 6
        my = y0 + 8
        for k in range(mw):
            pen.block(x0 + 6 + k, my, b[1], 'boca')
        if mouth_open:
            for k in range(mw - 2):
                pen.block(x0 + 7 + k, my + 0.5 if s == 2 else my, b[2] if s == 2 else b[1], 'boca')
        pen.block(x0 + 6, my, Yw[1], 'dente'); pen.block(x0 + 11, my, Yw[1], 'dente')
        if s == 2:
            pen.dot(x0 + 6, my, Yw[0], 'dente', dx=1, dy=1); pen.dot(x0 + 11, my, Yw[0], 'dente', dx=0, dy=1)
            pen.dot(x0 + 8, my, Yw[1], 'dente'); pen.dot(x0 + 9, my, Yw[1], 'dente', dx=1)
        # parte de dentro das orelhas
        for ex, ey in ((0, 4), (1, 5), (17, 4), (16, 5)):
            pen.dot(x0 + ex, y0 + ey, G[1], 'goblin')
            if s == 2:
                pen.dot(x0 + ex, y0 + ey, G[2], 'goblin', dx=1)
    elif view == 'side':
        if st == 'hurt':
            pen.dot(x0 + 12, y0 + 4, G[0]); pen.dot(x0 + 13, y0 + 5, G[0]); pen.dot(x0 + 12, y0 + 6, G[0])
        else:
            pen.block(x0 + 12, y0 + 4, Y[2], 'olho_gob', w=2, h=1)
            pen.block(x0 + 12, y0 + 5, Y[1], 'olho_gob', w=2, h=1)
            pen.block(x0 + 13, y0 + 4, b[0], 'boca', w=1, h=1 if s == 1 else 1.5)
            if s == 2:
                pen.dot(x0 + 12, y0 + 4, Y[3], 'olho_gob')
            pen.dot(x0 + 11, y0 + 3, G[0], 'goblin'); pen.dot(x0 + 12, y0 + 3, G[1], 'goblin')
            pen.dot(x0 + 13, y0 + 3, G[0], 'goblin')
        # nariz pontudo
        pen.block(x0 + 17, y0 + 5, G[3], 'goblin'); pen.block(x0 + 17, y0 + 6, G[2], 'goblin')
        if s == 2:
            pen.dot(x0 + 18, y0 + 5.5, G[2], 'goblin')
        my = y0 + 7
        for k in range(4):
            pen.block(x0 + 12 + k, my, b[1], 'boca')
        if mouth_open:
            pen.block(x0 + 13, my + 1, b[2], 'boca', w=2)
        pen.block(x0 + 15, my, Yw[1], 'dente')
        if s == 2:
            pen.dot(x0 + 15, my, Yw[0], 'dente', dy=1)
        for ex, ey in ((0, 2), (1, 3), (2, 3), (3, 4)):
            pen.dot(x0 + ex, y0 + ey, G[1], 'goblin')
    else:
        for ex, ey in ((0, 4), (1, 5), (17, 4), (16, 5)):
            pen.dot(x0 + ex, y0 + ey, G[2], 'goblin')


def draw(view, pose=None, s=1):
    pose = pose or {}
    W, H = CANVAS[s]
    c = Canvas(W, H)
    pen = Pen(c, s, PAD_X * s, PAD_Y * s)
    by = V(pose, 'bob', s)
    hy = by + V(pose, 'hy', s)
    sq = pose.get('squash', 0)
    st = pose.get('face')
    t = R['tanga']
    # --- pernas (curtas, com faixas marrons nos pés)
    for key, bx in (('lf', 6), ('rf', 11)) if view != 'side' else (('rf', 8), ('lf', 9)):
        dx, lift = pose.get(key, (0, 0))
        x = bx + dx
        foot = 19 - lift
        back = view == 'side' and key == 'rf'
        top = by + 16
        if foot - 1 - top > 0:
            pen.cyl(x, top, 2, foot - 1 - top, G, 'goblin', base=3 - back)
        pen.cyl(x, foot - 1, 2 if view != 'side' else 3, 2, t, 'tanga', base=2 - back, cap=1)
        if s == 2:
            pen.dot(x, foot, t[0], 'tanga', dx=0, dy=1)
            for i in range(4 if view != 'side' else 6):
                pen.dot(x, foot + 1, t[0], 'tanga', dx=i, dy=-1)
    # --- braço de trás (side)
    ka = pose.get('knife', None)
    if view == 'side':
        pen.cyl(8 - V(pose, 'la', s), by + 12, 1.5, 3, G, 'goblin', base=2)
    # --- corpo
    body = pen.grid(BODY[view], 6, by + 12, 'G')
    c.shade(body, G, 'goblin', radius=2.5 * s, base=3, bias=-0.05)
    # barriga mais clara na frente
    if view == 'down':
        pen.dot(9, by + 13.5, G[4], 'goblin')
        if s == 2:
            pen.dot(9, by + 13.5, G[4], 'goblin', dx=1)
    # --- tanga
    tg = {'down': ["TTTTTTTT", ".TTTTTT.", "..TT.TT."],
          'up': ["TTTTTTTT", ".TTTTTT.", ".TTTTTT."],
          'side': [".TTTTTTT", ".TTTTTT.", "..TTTT.."]}[view]
    tm = pen.grid(tg, 6, by + 15, 'T')
    c.shade(tm, t, 'tanga', radius=1.5 * s, base=2)
    for X in range(c.w):   # cordão
        Yc = pen.Y(by + 15)
        if tm[Yc, X]:
            c.px(X, Yc, R['ouro'][1] if (X % 3 == 0 and s == 2) else t[4] if s == 2 else t[3], 'tanga')
    # --- braços da frente
    arms_up = pose.get('arms_up', 0)
    if view != 'side':
        la, ra = V(pose, 'la', s), V(pose, 'ra', s)
        pen.cyl(4.5, by + 12 + la - arms_up, 1.5, 3, G, 'goblin', base=3)
        pen.cyl(14, by + 12 + ra - arms_up, 1.5, 3, G, 'goblin', base=2)
        pen.block(4.5, by + 15 + la - arms_up, G[2], 'goblin', w=1.5)
        pen.block(14, by + 15 + ra - arms_up, G[1], 'goblin', w=1.5)
    # --- cabeça
    x0, y0 = 1, hy + 2 + sq
    rows = HEAD[view]
    if sq:
        rows = rows[:3] + rows[4:] if sq == 1 else rows[:2] + rows[3:4] + rows[5:]
        y0 = hy + 2 + sq
    head = pen.grid(rows, x0 - 1, y0, 'G')
    ears = pen.grid(rows, x0 - 1, y0, 'E')
    c.shade(ears, G, 'goblin', radius=1.5 * s, base=3, bias=-0.05)
    c.shade(head, G, 'goblin', radius=3.2 * s, base=3, bias=-0.07)
    # topete
    if view != 'side':
        pen.dot(x0 + 8.5, y0 - 1, G[1], 'goblin')
        pen.dot(x0 + 9, y0 - 1.5 if s == 2 else y0 - 1, G[2], 'goblin')
    else:
        pen.dot(x0 + 7, y0 - 1, G[1], 'goblin')
    # pintas na careca (B)
    if s == 2:
        for (sx, sy) in ((6, 1.5), (11, 2), (7, 3)) if view != 'side' else ((7, 1.5), (10, 2.5)):
            pen.dot(x0 + sx, y0 + sy, G[2], 'goblin')
    face(pen, view, x0, y0, st, s, pose.get('mouth', 0))
    # --- faca
    if ka is not None:
        hx, hyk, ang = ka
        knife(pen, hx, by + hyk, ang, s)
        pen.block(hx - 0.5, by + hyk - 0.5, G[3], 'goblin', w=1.5, h=1.5)
    if view == 'side':
        ra = V(pose, 'ra', s)
        tmp = Canvas(W, H)
        tp = Pen(tmp, s, PAD_X * s, PAD_Y * s)
        tp.cyl(10 + ra, by + 12, 1.5, 3, G, 'goblin', base=3)
        tp.block(10 + ra, by + 15, G[2], 'goblin', w=1.5)
        if ka is None:
            knife(tp, 10.5 + ra, by + 15, -20, s)
        if s == 2:
            round_corners(tmp)
        tmp.outline(CONTORNO)
        c.paste(tmp, 0, 0)
    elif ka is None and view == 'down':
        knife(pen, 15, by + 15 + V(pose, 'ra', s) - arms_up, -80, s)
    elif ka is None and view == 'up':
        knife(pen, 5, by + 15 + V(pose, 'la', s), -80, s)
    if s == 2:
        round_corners(c)
    c.outline(CONTORNO)
    return c


def _walk(view, i):
    if view == 'side':
        p = i / 6 * 2 * math.pi
        fx = 2 * math.cos(p)
        return {'lf': (round(fx * 2) / 2, max(0.0, math.sin(p)) * 1.5),
                'rf': (round(-fx * 2) / 2, max(0.0, -math.sin(p)) * 1.5),
                'bob': round(-abs(math.sin(p)) * 2) / 2, 'ra': round(-fx * 0.5 * 2) / 2, 'la': round(fx * 0.5 * 2) / 2}
    lift = [0, 1, 1.5, 0, 0, 0][i]
    lr = [0, 0, 0, 0, 1, 1.5][i] if False else [0, 0, 0, 0, 1, 1.5][i]
    L = [1, 1.5, 0, 0, 0, 0][i]
    Rr = [0, 0, 0, 1, 1.5, 0][i]
    bob = [-0.5, -1, 0, -0.5, -1, 0][i]
    a = [-0.5, -1, 0, 0.5, 1, 0][i]
    return {'lf': (0, L), 'rf': (0, Rr), 'bob': bob, 'la': a, 'ra': -a}


def animations(s):
    out, fps = {}, {}
    for view, nome in (('down', 'baixo'), ('up', 'cima'), ('side', 'lado')):
        out['andar_' + nome] = [draw(view, _walk(view, i), s) for i in range(6)]
        fps['andar_' + nome] = 10
    # provocação: pula, ri de boca aberta e balança a faca
    taunt = [
        {'bob': 0, 'mouth': 0},
        {'bob': -1, 'mouth': 1, 'arms_up': 1, 'knife': (15.5, 12, -100)},
        {'bob': -2, 'mouth': 1, 'arms_up': 2, 'knife': (15.5, 11, -60)},
        {'bob': 0, 'mouth': 1, 'squash': 1},
    ]
    out['provocar'] = [draw('down', p, s) for p in taunt]
    fps['provocar'] = 6
    out['dano_lado'] = [draw('side', {'face': 'hurt', 'bob': -1, 'mouth': 1, 'ra': -1}, s)]
    out['dano_baixo'] = [draw('down', {'face': 'hurt', 'bob': -1, 'mouth': 1, 'arms_up': 1}, s)]
    out['clarao'] = [out['dano_lado'][0].tinted('#ffffff'), out['dano_baixo'][0].tinted('#ffffff')]
    fps['dano_lado'] = fps['dano_baixo'] = fps['clarao'] = 8
    return out, fps


def death(s, puff_frames):
    """Morte: pula de susto, achata e some numa nuvem de fumaça (quadros da nuvem vêm de efeitos.poof)."""
    W, H = CANVAS[s]
    ox, oy = ORIGIN[s]
    fr = [draw('down', {'face': 'hurt', 'bob': -2, 'mouth': 1, 'arms_up': 2}, s),
          draw('down', {'face': 'hurt', 'bob': 1, 'squash': 1, 'mouth': 1}, s)]
    flat = draw('down', {'face': 'hurt', 'bob': 2, 'squash': 2, 'mouth': 1}, s)
    for k, pf in enumerate(puff_frames):
        c = Canvas(W, H)
        if k == 0:
            c.paste(flat, 0, 0)
        px = ox - pf.w // 2
        py = oy - pf.h + 2 * s
        c.paste(pf, px, py)
        fr.append(c)
    return fr
