"""Aren — Opção A (s=1, ~17×28 px com contorno) e Opção B (s=2, ~32×54 px, o dobro de detalhe).

O desenho é feito em "unidades A" (o quadro base de 24×30 un). Na Opção B tudo vale 2 px, as silhuetas em
grade são ampliadas com EPX (contorno liso) e pintadas de novo com volume, e os detalhes finos (olhos com
brilho, mechas de 1 px, fivela, costuras, sola da bota) são desenhados em pixel de verdade.

Todos os quadros de Aren têm o mesmo tamanho de tela (A 40×36, B 80×72) e o mesmo ponto do pé (origem),
para trocar de animação sem pular: A (20, 31), B (40, 62).
"""
from __future__ import annotations

import math
import numpy as np
from pixel import Canvas, Pen, line_pts, mask_rect, round_corners
from paleta import RAMPAS as R, CONTORNO

BASE_W, BASE_H = 24, 30
PAD_X, PAD_Y = 8, 4                     # o quadro base fica nesta posição dentro da tela (un)
CANVAS = {1: (40, 36), 2: (80, 72)}
ORIGIN = {1: (20, 31), 2: (40, 62)}     # pé (meio da linha de baixo do contorno das botas)


def V(pose, key, s, default=0):
    v = pose.get(key, default)
    if isinstance(v, tuple) and len(v) == 2 and not isinstance(v[0], tuple):
        v = v[s - 1]
    return v


# ------------------------------------------------------------------ cabeça (grade 14 un de largura)
HEAD = {
    'down': [
        ".....HHH......",
        "...HHHHHH.H...",
        "..HHHHHHHHHH..",
        ".HHHHHHHHHHHH.",
        ".HHHHHHHHHHHH.",
        "HHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHH",
        "HHHHSHHHHHSHHH",
        "HHHSSSHSHSSSHH",
        "HHSSSSSSSSSSHH",
        "HHSSSSSSSSSSHH",
        "HHSSSSSSSSSSHH",
        ".HSSSSSSSSSSH.",
        "..SSSSSSSSSS..",
        "...SSSSSSSS...",
    ],
    'up': [
        ".....HHH......",
        "...HHHHHH.H...",
        "..HHHHHHHHHH..",
        ".HHHHHHHHHHHH.",
        ".HHHHHHHHHHHH.",
        "HHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHH",
        "HHHHHHHHHHHHHH",
        "SHHHHHHHHHHHHS",
        ".HHHHHHHHHHHH.",
        "..HHHHHHHHHH..",
        "...SSSSSSSS...",
    ],
    'side': [
        "....HHH.......",
        "..HHHHHHH.....",
        ".HHHHHHHHHH...",
        "HHHHHHHHHHHH..",
        "HHHHHHHHHHHHH.",
        "HHHHHHHHHHHHH.",
        "HHHHHHHHHSHHHH",
        "HHHHHHHHSSSSHS",
        "HHHHHHHSSSSSSS",
        "HHHHHSSSSSSSSSS",
        "HHHHSSSSSSSSSS.",
        ".HHHSSSSSSSSS..",
        "..HHSSSSSSSSS..",
        "...HSSSSSSSS...",
        "....SSSSSSS....",
    ],
}

# mechas: linhas escuras entre os tufos ('d') e brilhos ('l'), em un relativas à cabeça
STRANDS = {
    'down': {'d': [[(4, 2), (3, 3), (3, 4)], [(7, 2), (7, 3), (6, 4)], [(10, 3), (10, 4), (11, 5)],
                   [(1, 5), (1, 6)], [(12, 6), (12, 7)], [(5, 6), (5, 7)], [(8, 6), (9, 7)]],
             'l': [[(5, 1), (4, 1)], [(2, 4), (2, 3)], [(8, 1)]]},
    'up':   {'d': [[(4, 2), (3, 3), (3, 4)], [(7, 2), (7, 3), (6, 4)], [(10, 3), (10, 4), (11, 5)],
                   [(3, 6), (4, 7), (4, 8)], [(7, 6), (7, 7), (8, 8)], [(10, 7), (10, 8), (11, 9)],
                   [(2, 10), (2, 11)], [(6, 10), (5, 11)], [(9, 11), (9, 12)]],
             'l': [[(5, 1), (4, 1)], [(2, 4), (2, 3)], [(8, 1)]]},
    'side': {'d': [[(5, 1), (4, 2), (4, 3)], [(8, 2), (8, 3), (7, 4)], [(10, 4), (11, 5)],
                   [(2, 5), (2, 6), (3, 7)], [(5, 6), (6, 7), (6, 8)], [(1, 9), (2, 10)]],
             'l': [[(4, 0), (5, 0)], [(2, 2), (1, 3)], [(7, 1)]]},
}


def _strand_line(pen, pts, x0, y0, col, hair, s):
    """Na Opção A, pixels; na B, linha fina de 1 px ligando os pontos (centros das un)."""
    c = pen.c
    if s == 1:
        for x, y in pts:
            X, Y = pen.X(x0 + x), pen.Y(y0 + y)
            if c.inside(X, Y) and hair[Y, X]:
                c.px(X, Y, col, 'cabelo')
        return
    P = [(pen.X(x0 + x) + (1 if i == 0 else 0), pen.Y(y0 + y) + (0 if i == 0 else 1)) for i, (x, y) in enumerate(pts)]
    if len(P) == 1:
        P = P + [(P[0][0] + 1, P[0][1])]
    lit = R['cabelo'][3] if col == R['cabelo'][1] else None
    for (ax, ay), (bx, by) in zip(P, P[1:]):
        for X, Y in line_pts(ax, ay, bx, by):
            if c.inside(X, Y) and hair[Y, X]:
                c.px(X, Y, col, 'cabelo')
                if lit and c.inside(X + 1, Y) and hair[Y, X + 1] and c.get(X + 1, Y) != col:
                    c.px(X + 1, Y, lit, 'cabelo')


def _eye(pen, ax, ay, view, state, s, mirror=False):
    """Olho em (ax, ay) un. A: 1×2 px. B: 2×4 px com brilho branco."""
    e = R['olho']
    c = pen.c
    X, Y = pen.X(ax), pen.Y(ay)
    if s == 1:
        if state == 'hurt':
            c.px(X - 1, Y, e[1]); c.px(X, Y + 1, e[1]); c.px(X + 1, Y, e[1])
        elif state == 'blink':
            c.px(X, Y + 1, e[1])
        else:
            c.px(X, Y, e[1]); c.px(X, Y + 1, e[2])
        return
    if state == 'hurt':      # >< apertado
        d = -1 if mirror else 1
        for i, (dx, dy) in enumerate(((0, 0), (1, 1), (0, 2))):
            c.px(X + (dx if not mirror else 1 - dx), Y + dy, e[1])
    elif state == 'blink':
        c.px(X, Y + 2, e[1]); c.px(X + 1, Y + 2, e[1]); c.px(X - (1 if not mirror else -2), Y + 1, R['pele'][1])
    else:
        hx = 0 if not mirror else 1
        c.px(X, Y - 1, e[0]); c.px(X + 1, Y - 1, e[0])          # cílio/sombra de cima
        c.px(X, Y, e[1]); c.px(X + 1, Y, e[1])
        c.px(X, Y + 1, e[1]); c.px(X + 1, Y + 1, e[2])
        c.px(X, Y + 2, e[2]); c.px(X + 1, Y + 2, e[2])
        c.px(X + hx, Y, e[3])                                    # brilho


def head(pen, view, x0, y0, state=None):
    c, s = pen.c, pen.s
    rows = HEAD[view]
    hair = pen.grid(rows, x0, y0, 'H')
    skin = pen.grid(rows, x0, y0, 'S')
    c.shade(skin, R['pele'][:3], 'pele', radius=2.5 * s)
    c.shade(hair, R['cabelo'], 'cabelo', radius=3.2 * s, bias=-0.05, step=0.2, base=2)
    st = STRANDS[view]
    for line in st['d']:
        _strand_line(pen, line, x0, y0, R['cabelo'][1], hair, s)
    for line in st['l']:
        _strand_line(pen, line[:1], x0, y0, R['cabelo'][4], hair, s)
        if len(line) > 1:
            _strand_line(pen, line[1:], x0, y0, R['cabelo'][3], hair, s)
    P = R['pele']
    if view == 'down':
        # sombra do cabelo na testa (linha logo abaixo da franja)
        for x in range(c.w):
            for y in range(c.h - 1):
                if hair[y, x] and skin[y + 1, x] and y < pen.Y(y0 + 10):
                    c.px(x, y + 1, P[1], 'pele')
        _eye(pen, x0 + 4, y0 + 10, view, state, s)
        _eye(pen, x0 + 9 - (0.5 if s == 2 else 0), y0 + 10, view, state, s, mirror=True)
        if s == 1:
            pen.dot(x0 + 3, y0 + 12, R['bochecha'][0]); pen.dot(x0 + 10, y0 + 12, R['bochecha'][0])
            pen.dot(x0 + 6, y0 + 13, P[1]); pen.dot(x0 + 7, y0 + 13, P[1])
        else:
            for dx in (0, 1):
                pen.dot(x0 + 2.5, y0 + 12.5, R['bochecha'][0], dx=dx)
                pen.dot(x0 + 10, y0 + 12.5, R['bochecha'][0], dx=dx)
            if state == 'hurt':
                for dx in range(3):
                    pen.dot(x0 + 6, y0 + 13, R['boca'][1], dx=dx)
                pen.dot(x0 + 6, y0 + 13.5, R['boca'][2], dx=1)
            else:
                pen.dot(x0 + 6, y0 + 13, P[0], dx=1); pen.dot(x0 + 6, y0 + 13, P[1], dx=2)
            pen.dot(x0 + 6.5, y0 + 11.5, P[1], dx=1)   # nariz (sombra)
    elif view == 'side':
        _eye(pen, x0 + 10, y0 + 9, view, state, s)
        if s == 1:
            pen.dot(x0 + 9, y0 + 11, R['bochecha'][0])
            pen.dot(x0 + 12, y0 + 12, P[1])
            pen.dot(x0 + 6, y0 + 10, P[1]); pen.dot(x0 + 6, y0 + 11, P[1]); pen.dot(x0 + 7, y0 + 11, P[1])
        else:
            pen.dot(x0 + 8.5, y0 + 11.5, R['bochecha'][0]); pen.dot(x0 + 8.5, y0 + 11.5, R['bochecha'][0], dx=1)
            pen.dot(x0 + 12, y0 + 12.5, P[0]); pen.dot(x0 + 12, y0 + 12.5, P[1], dx=1)
            # orelha com dobra
            for dy in range(4):
                pen.dot(x0 + 6, y0 + 9.5, P[1] if dy in (0, 3) else P[2], 'pele', dy=dy)
                pen.dot(x0 + 6.5, y0 + 9.5, P[0] if dy in (1, 2) else P[1], 'pele', dy=dy)
            pen.dot(x0 + 13.5, y0 + 10.5, P[1], dy=1)   # sombra do nariz
    return hair | skin


# ------------------------------------------------------------------ corpo
TORSO = {
    'down': [
        "..TTTTTTTT..",
        ".TTTTTTTTTT.",
        ".TTTTTTTTTT.",
        ".TTTTTTTTTT.",
        ".TTTTTTTTTT.",
        "TTTTTTTTTTTT",
        "TTTTTTTTTTTT",
    ],
    'side': [
        "..TTTTTT..",
        "..TTTTTTT.",
        "..TTTTTTT.",
        "..TTTTTTT.",
        "..TTTTTTT.",
        ".TTTTTTTT.",
        ".TTTTTTTT.",
    ],
}
TORSO['up'] = TORSO['down']


def torso(pen, view, by):
    c, s = pen.c, pen.s
    rows = TORSO[view]
    x0 = 6 if view != 'side' else 7
    y0 = by + 15
    m = pen.grid(rows, x0, y0, 'T')
    c.shade(m, R['tunica'], 'tunica', radius=3 * s)
    t, cou, ouro = R['tunica'], R['couro'], R['ouro']
    # barra da túnica
    hem_y = pen.Y(y0 + len(rows)) - 1
    for x in range(c.w):
        if m[hem_y, x]:
            c.px(x, hem_y, t[1], 'tunica')
            if s == 2 and m[hem_y - 1, x]:
                c.px(x, hem_y - 1, t[2] if c.get(x, hem_y - 1) != t[3] else t[2], 'tunica')
    if view != 'side':
        for fx in (4, 8):     # dobras da saia
            pen.dot(x0 + fx, y0 + 6, t[0], 'tunica'); pen.dot(x0 + fx, y0 + 5, t[1], 'tunica')
            if s == 2:
                pen.dot(x0 + fx, y0 + 5, t[1], 'tunica', dy=-1)
                pen.dot(x0 + fx, y0 + 6, t[0], 'tunica', dy=1)
                pen.dot(x0 + fx, y0 + 5, t[3], 'tunica', dx=-1)
    # cinto
    yb = y0 + 4
    Yb0, Yb1 = pen.Y(yb), pen.Y(yb + 1)
    for x in range(c.w):
        if m[Yb0, x]:
            for Y in range(Yb0, Yb1):
                if s == 1:
                    col = cou[2] if x < pen.X(12) else cou[1]
                else:
                    col = (cou[3] if Y == Yb0 else cou[1]) if x < pen.X(12) else (cou[2] if Y == Yb0 else cou[0])
                c.px(x, Y, col, 'couro')
    if view == 'down':
        if s == 1:
            pen.dot(11, yb, ouro[3], 'ouro'); pen.dot(12, yb, ouro[2], 'ouro')
            pen.dot(11, yb + 1, ouro[1], 'ouro'); pen.dot(12, yb + 1, ouro[0], 'ouro')
            pen.dot(9, yb + 1, cou[1], 'couro'); pen.dot(9, yb + 2, cou[2], 'couro')
        else:
            X, Y = pen.X(11), pen.Y(yb) - 1
            buckle = ["oooo", "oDDo", "oDDo", "oooo"]
            for j, row in enumerate(buckle):
                for i, ch in enumerate(row):
                    col = (ouro[3] if (i + j) < 2 else ouro[2] if i < 3 and j < 3 else ouro[1]) if ch == 'o' else cou[0]
                    c.px(X + i, Y + j, col, 'ouro')
            # bolsinha no cinto
            for j in range(4):
                for i in range(3):
                    col = cou[3] if (i == 0 and j < 3) else cou[1] if j == 3 or i == 2 else cou[2]
                    c.px(pen.X(8) + i, pen.Y(yb + 1) + j, col, 'couro')
            c.px(pen.X(8) + 1, pen.Y(yb + 1) + 1, ouro[2], 'ouro')
    elif view == 'side':
        pen.block(x0 + 6, yb, ouro[2], 'ouro', h=1)
        pen.dot(x0 + 6, yb + 1, ouro[0], 'ouro')
        if s == 2:
            pen.dot(x0 + 6, yb, ouro[3], 'ouro')
            pen.dot(x0 + 6, yb, cou[0], 'couro', dx=1, dy=1)
        pen.block(x0 + 2, yb + 1, cou[2], 'couro', h=2)
        if s == 2:
            pen.dot(x0 + 2, yb + 1, cou[3], 'couro')
            pen.dot(x0 + 2, yb + 1, ouro[2], 'ouro', dx=1, dy=1)
    elif view == 'up':
        if s == 2:
            for i in range(0, c.w, 1):
                pass
    return m


def scarf(pen, view, by, ph):
    c, s = pen.c, pen.s
    r = R['cachecol']
    y = by + 15
    def B(x, yy, col):
        pen.block(x, yy, col, 'cachecol')
    if view in ('down', 'up'):
        for x in range(8, 16):
            B(x, y, r[2] if x < 13 else r[1])
        for x in range(7, 17):
            B(x, y + 1, r[1] if x in (7, 16) else r[2])
        B(9, y, r[3])
        if view == 'down':
            B(10, y, r[3]); B(8, y + 1, r[3]); B(16, y + 1, r[0])
            B(9, y + 2, r[2]); B(10, y + 2, r[1]); B(9, y + 3, r[1])
            B(9 - (ph % 2 == 1), y + 4, r[0])
        else:
            B(11, y + 2, r[2]); B(12, y + 2, r[1])
            sw = [0, 1, 1, 0][ph % 4]
            B(11 - sw, y + 3, r[2]); B(12 + sw, y + 3, r[1])
            B(11 - sw, y + 4, r[1]); B(12 + sw, y + 4, r[0])
        if s == 2:
            # dobra do tecido: linha escura no meio do cachecol e brilho em cima
            for X in range(pen.X(8), pen.X(16)):
                if c.get(X, pen.Y(y + 1)) in (r[2],):
                    c.px(X, pen.Y(y + 1), r[1] if X % 5 else r[0], 'cachecol')
            for X in range(pen.X(8) + 1, pen.X(12)):
                c.px(X, pen.Y(y), r[3], 'cachecol')
    else:
        for x in range(9, 16):
            B(x, y, r[2] if x < 13 else r[1])
            B(x, y + 1, r[2] if x < 14 else r[1])
        B(10, y, r[3]); B(11, y, r[3])
        tail = [
            [(8, 0), (7, 1), (6, 1), (5, 2)],
            [(8, 0), (7, 0), (6, 1), (5, 1)],
            [(8, 1), (7, 1), (6, 2), (5, 2)],
            [(8, 1), (7, 2), (6, 2), (5, 3)],
        ][ph % 4]
        for i, (tx, ty) in enumerate(tail):
            B(tx, y + ty, r[2] if i < 2 else r[1])
            B(tx, y + ty + 1, r[1] if i < 2 else r[0])
        if s == 2:
            for X in range(pen.X(9), pen.X(15)):
                c.px(X, pen.Y(y + 1), r[1] if (X // 3) % 2 else r[2], 'cachecol')
            # franja na ponta
            tx, ty = tail[-1]
            pen.dot(tx, y + ty + 2, r[0], 'cachecol'); pen.dot(tx, y + ty + 2, r[1], 'cachecol', dx=1, dy=-1)


def arm(pen, x, y, length=4, dark=False, side=False):
    t, p = R['tunica'], R['pele']
    pen.cyl(x, y, 2, length, t, 'tunica', base=1 if dark else 2)
    if pen.s == 2:   # punho da manga
        for i in range(4):
            pen.dot(x, y + length, t[0] if dark else t[1], 'tunica', dx=i, dy=-1)
    pen.cyl(x, y + length, 2, 1 if side else 2, p, 'pele', base=1 if dark else 2)
    if pen.s == 2 and not side:
        pen.dot(x, y + length + 2, p[1], 'pele', dx=1, dy=-1)


def legs(pen, view, pose, by):
    s = pen.s
    cal, cou = R['calca'], R['couro']
    top = by + 22
    if view in ('down', 'up'):
        for key, base_x in (('lf', 8), ('rf', 13)):
            dx, lift = pose.get(key, (0, 0))
            x = base_x + dx
            foot = 26 - lift
            plen = foot - 2 - top
            if plen > 0:
                pen.cyl(x, top, 3, plen, cal, 'calca', base=2)
            pen.cyl(x, foot - 2, 3, 3, cou, 'couro', base=2, cap=1)
            if s == 2:
                # dobra da bota e sola
                for i in range(6):
                    pen.dot(x, foot - 2, cou[4] if i < 3 else cou[3], 'couro', dx=i)
                    pen.dot(x, foot - 2, cou[1], 'couro', dx=i, dy=1)
                    pen.dot(x, foot + 1, cou[0], 'couro', dx=i, dy=-1)
                if view == 'down':
                    pen.dot(x, foot, cou[3], 'couro', dx=1, dy=0)
            elif view == 'down':
                pen.dot(x + 1, foot, cou[1], 'couro'); pen.dot(x + 2, foot, cou[0], 'couro')
    else:
        kneel = pose.get('kneel', 0)
        for key, back in (('rf', True), ('lf', False)):
            dx, lift = pose.get(key, (0, 0))
            x = 10 + dx
            foot = 26 - lift
            k = 1 if back else 0
            plen = foot - 1 - top
            if plen > 0:
                pen.cyl(x, top, 2, plen, cal, 'calca', base=2 - k)
            pen.cyl(x, foot - 2, 2, 1, cou, 'couro', base=3 - k)
            pen.cyl(x, foot - 1, 3, 2, cou, 'couro', base=2 - k)
            pen.dot(x, foot - 1, cou[4 - k], 'couro')
            if s == 2:
                for i in range(6):
                    pen.dot(x, foot + 1, cou[0], 'couro', dx=i, dy=-1)
                pen.dot(x + 2.5, foot - 1, None, dx=1)   # bico arredondado
                pen.dot(x, foot - 2, cou[4 - k], 'couro', dx=1)


# ------------------------------------------------------------------ espada na mão
def sword(pen, hx, hy, ang, length=9):
    """Espada saindo da mão (hx, hy) un no ângulo `ang` (graus; 0 = direita, 90 = baixo)."""
    c, s = pen.c, pen.s
    m = R['metal']
    a = math.radians(ang)
    dx, dy = math.cos(a), math.sin(a)
    X0, Y0 = pen.X(hx) + (s // 2), pen.Y(hy) + (s // 2)
    L = length * s
    grip = 2 * s
    # cabo
    for X, Y in line_pts(X0 - dx * grip, Y0 - dy * grip, X0, Y0):
        c.px(X, Y, R['madeira'][2], 'madeira')
    # guarda
    gx, gy = -dy, dx
    for k in range(-s - 1, s + 2):
        c.px(int(round(X0 + gx * k + dx)), int(round(Y0 + gy * k + dy)), R['ouro'][2] if k <= 0 else R['ouro'][1], 'ouro')
    # lâmina (B: 2 px de largura, fio claro)
    pts = line_pts(X0 + dx * 2, Y0 + dy * 2, X0 + dx * L, Y0 + dy * L)
    for i, (X, Y) in enumerate(pts):
        c.px(X, Y, m[3], 'metal')
        if s == 2:
            ox, oy = (1, 0) if abs(dy) > abs(dx) else (0, 1)
            c.px(X + ox, Y + oy, m[2], 'metal')
    X, Y = pts[-1]
    c.px(X, Y, m[4], 'metal')


# ------------------------------------------------------------------ montagem
def draw(view, pose=None, s=1):
    pose = pose or {}
    W, H = CANVAS[s]
    c = Canvas(W, H)
    pen = Pen(c, s, PAD_X * s, PAD_Y * s)
    by = V(pose, 'bob', s)
    sh = by + V(pose, 'sh', s)          # ombros/cabeça (respiração)
    hy = sh + V(pose, 'hy', s)
    bx = V(pose, 'bx', s)               # inclinação do corpo (side)
    st = pose.get('face')
    ph = pose.get('scarf', 0)
    if bx:
        pen = Pen(c, s, PAD_X * s, PAD_Y * s)
    if pose.get('sword_behind'):
        _sword_arm(pen, pose, sh)
    if view == 'side':
        if not pose.get('no_back_arm'):
            la = V(pose, 'la', s)
            arm(pen, 10 - la + bx, sh + 16, 4, dark=True, side=True)
        legs(pen, view, pose, by)
        pt = Pen(c, s, PAD_X * s + int(round(bx * s)), PAD_Y * s)
        torso(pt, view, by)
        scarf(Pen(c, s, PAD_X * s + int(round(bx * s)), PAD_Y * s), view, sh, ph)
        head(Pen(c, s, PAD_X * s + int(round(V(pose, 'hx', s) * s)), PAD_Y * s), view, 6 + bx, hy + 1, st)
        if pose.get('sword') is None and not pose.get('no_front_arm'):
            ra = V(pose, 'ra', s)
            tmp = Canvas(W, H)
            arm(Pen(tmp, s, PAD_X * s, PAD_Y * s), 12 + ra + bx, sh + 16, 4, side=True)
            if s == 2:
                round_corners(tmp)
            tmp.outline(CONTORNO)
            c.paste(tmp, 0, 0)
    else:
        legs(pen, view, pose, by)
        if view == 'up' and pose.get('sword') is not None and not pose.get('sword_behind'):
            _sword_arm(pen, pose, sh)
        torso(pen, view, by)
        la, ra = V(pose, 'la', s), V(pose, 'ra', s)
        if not pose.get('no_arms'):
            if pose.get('arms_up'):
                arm(pen, 5, sh + 13 + la, 3)
                arm(pen, 17, sh + 13 + ra, 3, dark=True)
            else:
                arm(pen, 5, sh + 16 + la, 4)
                if pose.get('sword') is None:
                    arm(pen, 17, sh + 16 + ra, 4, dark=True)
        scarf(pen, view, sh, ph)
        head(pen, view, 5, hy + 1, st)
    if pose.get('sword') is not None and view != 'up' and not pose.get('sword_behind'):
        _sword_arm(pen, pose, sh)
    if s == 2:
        round_corners(c)
    c.outline(CONTORNO)
    return c


def _sword_arm(pen, pose, sh):
    """Braço da espada: do ombro até a mão, e a espada no ângulo pedido."""
    s = pen.s
    ang, reach = pose['sword']
    if pose.get('view') == 'side' or pose.get('_view') == 'side':
        pass
    sx, sy = pose.get('shoulder', (13, 16))
    a = math.radians(ang)
    hx, hy = sx + math.cos(a) * reach, sh + sy + math.sin(a) * reach
    c = pen.c
    t = R['tunica']
    for X, Y in line_pts(pen.X(sx), pen.Y(sh + sy), pen.X(hx), pen.Y(hy)):
        for oy in range(s + 1):
            for ox in range(s + 1):
                c.px(X + ox, Y + oy, t[2] if oy == 0 else t[1], 'tunica')
    sword(pen, hx, hy, ang, length=pose.get('blade', 9))
    p = R['pele']
    pen.block(hx, hy, p[2], 'pele')
    if s == 2:
        pen.dot(hx, hy, p[1], 'pele', dx=1, dy=1)


def rot90cw(c):
    """Gira o quadro 90° no sentido horário (sem perda: só reordena pixels)."""
    n = Canvas(c.h, c.w)
    n.rgba = np.rot90(c.rgba, k=-1).copy()
    n.mat = np.rot90(c.mat, k=-1).copy()
    return n


# ------------------------------------------------------------------ animações
def _walk_down(i, s):
    lift = [0, 1, 1.5, 1, 0, 0, 0, 0]
    L = lift[i]
    Rr = lift[(i + 4) % 8]
    bob = [0, -0.5, -1, -0.5, 0, -0.5, -1, -0.5][i]
    arm_ = [0, -0.5, -1, -0.5, 0, 0.5, 1, 0.5][i]
    return {'lf': (0, L), 'rf': (0, Rr), 'bob': bob, 'la': arm_, 'ra': -arm_, 'scarf': i // 2}


def _walk_side(i, s):
    p = i / 8 * 2 * math.pi
    fx = 3 * math.cos(p)
    lf = (round(fx * 2) / 2, max(0.0, math.sin(p)) * 1.5)
    rf = (round(-fx * 2) / 2, max(0.0, -math.sin(p)) * 1.5)
    bob = -abs(math.sin(p))
    return {'lf': lf, 'rf': rf, 'bob': round(bob * 2) / 2, 'ra': round(-fx * 0.7 * 2) / 2,
            'la': round(fx * 0.5 * 2) / 2, 'scarf': i}


IDLE_SH = {1: [0, 0, 1, 1], 2: [0, 0.5, 1, 0.5]}


def animations(s):
    """Retorna {nome: [Canvas...]} e fps sugerido."""
    out = {}
    fps = {}
    for view in ('down', 'up', 'side'):
        nome = {'down': 'baixo', 'up': 'cima', 'side': 'lado'}[view]
        out['parado_' + nome] = [draw(view, {'sh': IDLE_SH[s][i], 'scarf': (i // 2) if view != 'side' else i}, s)
                                 for i in range(4)]
        fps['parado_' + nome] = 4
        fn = _walk_side if view == 'side' else _walk_down
        out['andar_' + nome] = [draw(view, fn(i, s), s) for i in range(8)]
        fps['andar_' + nome] = 12
    if True:
        out.update(_attacks(s))
        for k in ('atacar_baixo', 'atacar_cima', 'atacar_lado'):
            fps[k] = 14
        for view, nome in (('down', 'baixo'), ('up', 'cima'), ('side', 'lado')):
            out['dano_' + nome] = [
                draw(view, {'face': 'hurt', 'bob': -1, 'arms_up': view != 'side', 'hx': -1 if view == 'side' else 0,
                            'bx': -1 if view == 'side' else 0, 'scarf': 1}, s),
                draw(view, {'face': 'hurt', 'bob': 0, 'scarf': 2}, s),
            ]
            fps['dano_' + nome] = 8
        out['cair'] = _death(s)
        fps['cair'] = 8
    return out, fps


def _attacks(s):
    out = {}
    # lado (virado para a direita): prepara atrás da cabeça, corta para a frente e para baixo, volta
    side = [
        {'sword': (-155, 3), 'shoulder': (10, 16), 'bx': -1, 'lf': (1, 0), 'rf': (-1, 0), 'scarf': 0, 'blade': 8,
         'sword_behind': True},
        {'sword': (-60, 4), 'shoulder': (12, 16), 'bx': 0, 'lf': (2, 0), 'rf': (-2, 0), 'scarf': 1},
        {'sword': (0, 4), 'shoulder': (13, 16), 'bx': 1, 'bob': 0.5, 'lf': (3, 0), 'rf': (-2, 0), 'scarf': 2},
        {'sword': (60, 4), 'shoulder': (13, 17), 'bx': 1, 'bob': 1, 'lf': (3, 0), 'rf': (-2, 0), 'scarf': 3},
        {'sword': (75, 3), 'shoulder': (12, 17), 'bx': 1, 'bob': 0.5, 'lf': (2, 0), 'rf': (-1, 0), 'scarf': 0},
        {'sword': (85, 3), 'shoulder': (12, 17), 'bx': 0, 'bob': 0, 'lf': (1, 0), 'rf': (-1, 0), 'scarf': 1},
    ]
    out['atacar_lado'] = [draw('side', dict(p, no_front_arm=True), s) for p in side]
    down = [
        {'sword': (-45, 3), 'shoulder': (17, 16), 'scarf': 0, 'blade': 8},
        {'sword': (10, 4), 'shoulder': (17, 16), 'scarf': 1},
        {'sword': (90, 4), 'shoulder': (15, 17), 'bob': 0.5, 'scarf': 2},
        {'sword': (160, 4), 'shoulder': (13, 17), 'bob': 1, 'scarf': 3},
        {'sword': (140, 3), 'shoulder': (14, 17), 'bob': 0.5, 'scarf': 0},
        {'sword': (110, 3), 'shoulder': (16, 17), 'bob': 0, 'scarf': 1},
    ]
    out['atacar_baixo'] = [draw('down', p, s) for p in down]
    up = [
        {'sword': (165, 3), 'shoulder': (7, 16), 'scarf': 0, 'blade': 8},
        {'sword': (-150, 4), 'shoulder': (7, 16), 'scarf': 1},
        {'sword': (-90, 4), 'shoulder': (10, 15), 'bob': 0.5, 'scarf': 2},
        {'sword': (-30, 4), 'shoulder': (15, 16), 'bob': 1, 'scarf': 3},
        {'sword': (-10, 3), 'shoulder': (16, 16), 'bob': 0.5, 'scarf': 0},
        {'sword': (20, 3), 'shoulder': (17, 16), 'bob': 0, 'scarf': 1},
    ]
    out['atacar_cima'] = [draw('up', p, s) for p in up]
    return out


def _death(s):
    W, H = CANVAS[s]
    fr = []
    fr.append(draw('side', {'face': 'hurt', 'bx': -1, 'hx': -1, 'bob': -1, 'lf': (1, 0), 'rf': (-1, 0), 'scarf': 1}, s))
    fr.append(draw('side', {'face': 'hurt', 'bob': 1.5, 'lf': (2, 0), 'rf': (-1, 0), 'scarf': 2}, s))
    fr.append(draw('side', {'face': 'blink', 'bob': 3, 'hx': 1, 'bx': 1, 'lf': (3, 0), 'rf': (-1, 0), 'scarf': 3,
                            'no_back_arm': True}, s))
    # deitado de bruços: o quadro de lado girado 90° (cabeça para a direita)
    lying = draw('side', {'face': 'blink', 'scarf': 0}, s)
    ox, oy = ORIGIN[s]
    for k, lift in enumerate((2, 0, 0)):
        r = rot90cw(lying)
        bb = r.bbox()
        c = Canvas(W, H)
        # costas para cima, corpo apoiado no chão (oy) e centrado no x da origem
        dx = ox - (bb[0] + bb[2]) // 2
        dy = oy - bb[3] + 1 - lift * s
        c.paste(r, dx, dy)
        if k == 2:
            # olhos fechados: já vem do 'blink'; escurece um pouco o lado de baixo (encostado no chão)
            pass
        fr.append(c)
    return fr
