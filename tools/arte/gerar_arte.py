#!/usr/bin/env python3
"""Gera a arte nova (rodada 1) em assets/sprites/novo/: folhas PNG, manifesto novo.json e SpriteFrames da Opção A.

    python3 tools/arte/gerar_arte.py                # tudo
    python3 tools/arte/gerar_arte.py --preview DIR  # também salva folhas ampliadas para revisão em DIR

Determinístico: rodar duas vezes dá os mesmos bytes. Não mexe na arte que o jogo usa hoje (assets/sprites/*.png).
"""
from __future__ import annotations

import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from PIL import Image  # noqa: E402
import aren  # noqa: E402
import goblin  # noqa: E402
import efeitos  # noqa: E402
from pixel import sheet  # noqa: E402
import preview  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(HERE))
OUT = os.path.join(ROOT, 'assets', 'sprites', 'novo')

LOOP = {'parado', 'andar', 'provocar'}
SLASH_DIRS = [0, 45, 90, 135, 180, 225, 270, 315]


def save_png(im, path):
    # sem metadados variáveis: bytes iguais a cada execução
    im.save(path, format='PNG', optimize=False)


def build():
    os.makedirs(OUT, exist_ok=True)
    man = {'versao': 1, 'personagens': {}, 'efeitos': {}}
    sheets = {}   # nome do arquivo -> lista de quadros (Canvas) para previews

    def add_char(char, opt, s, anims, fps, origin, size):
        entry = man['personagens'].setdefault(char, {}).setdefault(opt, {
            'escala': s, 'quadro': list(size), 'origem': list(origin), 'animacoes': {}})
        for name, frames in anims.items():
            fn = f'{char}_{opt.lower()}_{name}.png'
            save_png(sheet(frames), os.path.join(OUT, fn))
            sheets[fn] = frames
            entry['animacoes'][name] = {
                'arquivo': fn, 'quadros': len(frames), 'fps': fps.get(name, 10),
                'loop': name.split('_')[0] in LOOP,
                'espelhar_para_esquerda': name.endswith('_lado'),
            }

    for opt, s in (('A', 1), ('B', 2)):
        a, f = aren.animations(s)
        add_char('aren', opt, s, a, f, aren.ORIGIN[s], aren.CANVAS[s])
        g, gf = goblin.animations(s)
        g['morrer'] = goblin.death(s, efeitos.poof(s)[:4])
        gf['morrer'] = 12
        add_char('goblin', opt, s, g, gf, goblin.ORIGIN[s], goblin.CANVAS[s])

        fx = man['efeitos'].setdefault(opt, {})
        simples = {
            'faisca': (efeitos.hit_spark(s), 20, 'acerto no inimigo'),
            'fumaca': (efeitos.poof(s), 14, 'nuvem da morte'),
            'poeira': (efeitos.step_dust(s), 12, 'poeira do passo'),
            'brilho': (efeitos.gem_sparkle(s), 16, 'pegar joia'),
        }
        for name, (frames, fps, desc) in simples.items():
            fn = f'fx_{opt.lower()}_{name}.png'
            save_png(sheet(frames), os.path.join(OUT, fn))
            sheets[fn] = frames
            w, h = frames[0].w, frames[0].h
            fx[name] = {'arquivo': fn, 'quadros': len(frames), 'fps': fps, 'quadro': [w, h],
                        'origem': [w // 2, h // 2] if name != 'poeira' else [w // 2, h - 2], 'uso': desc}
        # corte: uma linha por direção (0° = direita, sentido horário)
        rows = [efeitos.slash(d, s) for d in SLASH_DIRS]
        w, h = rows[0][0].w, rows[0][0].h
        big = Image.new('RGBA', (w * len(rows[0]), h * len(rows)), (0, 0, 0, 0))
        for j, fr in enumerate(rows):
            big.paste(sheet(fr), (0, j * h))
        fn = f'fx_{opt.lower()}_corte.png'
        save_png(big, os.path.join(OUT, fn))
        sheets[fn] = rows[2]
        fx['corte'] = {'arquivo': fn, 'quadros': len(rows[0]), 'fps': 14, 'quadro': [w, h], 'origem': [w // 2, h // 2],
                       'linhas': len(rows), 'direcoes': SLASH_DIRS,
                       'uso': 'arco do golpe da espada; linha = direção do golpe (0° direita, 90° baixo)'}

    with open(os.path.join(OUT, 'novo.json'), 'w', encoding='utf-8') as fh:
        json.dump(man, fh, ensure_ascii=False, indent=1, sort_keys=True)
        fh.write('\n')
    write_spriteframes(man)
    return man, sheets


def write_spriteframes(man):
    """SpriteFrames (.tres) da Opção A para Aren e goblin, prontos para um AnimatedSprite2D."""
    for char in ('aren', 'goblin'):
        e = man['personagens'][char]['A']
        w, h = e['quadro']
        ext, subs, anims = [], [], []
        for i, (name, a) in enumerate(sorted(e['animacoes'].items())):
            eid = f'{i + 1}_{name}'
            ext.append(f'[ext_resource type="Texture2D" path="res://assets/sprites/novo/{a["arquivo"]}" id="{eid}"]')
            frames = []
            for k in range(a['quadros']):
                sid = f'AtlasTexture_{name}_{k}'
                subs.append(f'[sub_resource type="AtlasTexture" id="{sid}"]\natlas = ExtResource("{eid}")\n'
                            f'region = Rect2({k * w}, 0, {w}, {h})\n')
                frames.append('{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % sid)
            anims.append('{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %.1f\n}'
                         % (', '.join(frames), 'true' if a['loop'] else 'false', name, float(a['fps'])))
        txt = '[gd_resource type="SpriteFrames" format=3]\n\n' + '\n'.join(ext) + '\n\n' + '\n'.join(subs) + \
              '\n[resource]\nanimations = [%s]\n' % ', '.join(anims)
        with open(os.path.join(OUT, f'{char}_a.tres'), 'w', encoding='utf-8') as fh:
            fh.write(txt)


def write_previews(sheets, d):
    os.makedirs(d, exist_ok=True)
    groups = {}
    for fn, frames in sheets.items():
        key = fn.split('_')[0] + '_' + fn.split('_')[1]
        groups.setdefault(key, []).append([f.image() for f in frames])
    for key, rows in groups.items():
        z = 6 if key.endswith('_a') else 3
        preview.both(rows, zoom=z).save(os.path.join(d, f'folha_{key}.png'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--preview', help='pasta para folhas ampliadas de revisão')
    args = ap.parse_args()
    man, sheets = build()
    n = sum(len(a['animacoes']) for c in man['personagens'].values() for a in c.values())
    print(f'{len(sheets)} folhas em {os.path.relpath(OUT, ROOT)} ({n} animações de personagem)')
    if args.preview:
        write_previews(sheets, args.preview)
        print('previews em', args.preview)


if __name__ == '__main__':
    main()
