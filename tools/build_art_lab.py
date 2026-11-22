#!/usr/bin/env python3
"""Laboratório de Arte do Aren: página única (fragmento HTML, sem <head>) para o Narley ver e dar nota à arte nova.

    python3 tools/arte/gerar_arte.py                       # antes: gera assets/sprites/novo/
    python3 tools/build_art_lab.py --out /caminho/laboratorio-arte.html

Mostra cada animação tocando num <canvas> (sem suavização, zoom inteiro) sobre a grama do jogo, com
Antes (arte atual, vinda do HTML) | Opção A | Opção B na mesma escala de mundo, e uma cena "em jogo"
(Aren + 3 goblins). As notas vão para a coleção `arte_r1` da capacidade `db` do artifact
(window.claude.use("db")); fora do visualizador ficam só no navegador (localStorage), com um aviso.
Todas as imagens vão embutidas como data URI.
"""
from __future__ import annotations

import argparse
import base64
import datetime
import io
import json
import os
import subprocess

from PIL import Image

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOVO = os.path.join(ROOT, 'assets', 'sprites', 'novo')
OLD = os.path.join(ROOT, 'assets', 'sprites')
STORE = 'arte_r1'
TAGS = ['Gostei', 'Refazer', 'Muito escuro', 'Muito claro', 'Pequeno demais', 'Grande demais', 'Não combina']


def uri(path=None, im=None):
    if im is not None:
        b = io.BytesIO()
        im.save(b, format='PNG')
        data = b.getvalue()
    else:
        with open(path, 'rb') as fh:
            data = fh.read()
    return 'data:image/png;base64,' + base64.b64encode(data).decode()


def git_rev():
    try:
        return subprocess.check_output(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], text=True).strip()
    except Exception:
        return '?'


def build_data():
    man = json.load(open(os.path.join(NOVO, 'novo.json'), encoding='utf-8'))
    imgs = {}
    for fn in sorted(os.listdir(NOVO)):
        if fn.endswith('.png'):
            imgs[fn[:-4]] = uri(os.path.join(NOVO, fn))
    for k in ('hero_down', 'hero_up', 'hero_side', 'goblin_down', 'goblin_up', 'goblin_side', 'sword'):
        imgs['old_' + k] = uri(os.path.join(OLD, k + '.png'))
    chao = Image.open(os.path.join(ROOT, 'assets', 'tiles', 'chao.png')).convert('RGBA')
    imgs['grama'] = uri(im=chao.crop((0, 0, 64, 16)))      # 4 variações de grama (16×16)

    P = man['personagens']
    E = man['efeitos']
    DIRS = [('baixo', 'down'), ('cima', 'up'), ('lado', 'side'), ('esquerda', 'side')]

    def char_track(char, opt, anim, flip=False, label=None):
        e = P[char][opt]
        a = e['animacoes'][anim]
        w, h = e['quadro']
        return {'label': label or ('Opção ' + opt), 'key': opt, 'img': a['arquivo'][:-4],
                'frames': [[k * w, 0, w, h] for k in range(a['quadros'])], 'ox': e['origem'][0], 'oy': e['origem'][1],
                'px': 1 / e['escala'], 'flip': flip, 'fps': a['fps']}

    def old_track(kind, d, n, flip=False, note=None):
        if kind == 'hero':
            w, h, ox, oy = 18, 24, 9, 24
        else:
            w, h, ox, oy = 22, 22, 11, 21
        t = {'label': 'Antes', 'key': 'antes', 'img': f'old_{kind}_{d}', 'frames': [[k * w, 0, w, h] for k in range(n)],
             'ox': ox, 'oy': oy, 'px': 1, 'flip': flip, 'fps': 9}
        if note:
            t['note'] = note
        return t

    def fx_frames(opt, name, row=0):
        f = E[opt][name]
        w, h = f['quadro']
        return {'img': f['arquivo'][:-4], 'frames': [[k * w, row * h, w, h] for k in range(f['quadros'])],
                'ox': f['origem'][0], 'oy': f['origem'][1], 'px': 1 / (1 if opt == 'A' else 2), 'fps': f['fps']}

    SLASH_ROW = {'baixo': 2, 'cima': 6, 'lado': 0, 'esquerda': 0}   # esquerda = lado espelhado (o golpe gira ao contrário)
    items = []

    def aren_item(iid, title, desc, anim, old_n=1, old_note=None, slash=False, views=DIRS, box=(40, 36, 20, 31)):
        variants = {}
        for nome, d in views:
            an = anim if anim == 'cair' else f'{anim}_{"lado" if nome == "esquerda" else nome}'
            flip = nome == 'esquerda'
            tr = [old_track('hero', d, old_n, flip, old_note)] if old_n else []
            for opt in ('A', 'B'):
                t = char_track('aren', opt, an, flip)
                if slash:
                    o = fx_frames(opt, 'corte', SLASH_ROW[nome])
                    o['at'] = [0, -11]
                    o['toggle'] = 'arco'
                    o['offset'] = 1          # o arco começa no 2º quadro do ataque (quando a espada desce)
                    o['flip'] = flip
                    t['over'] = o
                tr.append(t)
            variants[nome] = tr
        items.append({'id': iid, 'grupo': 'Aren', 'title': title, 'desc': desc, 'box': box, 'variants': variants})

    aren_item('aren_parado', 'Aren parado (respirando)',
              '4 quadros: os ombros e a cabeça descem 1 pixel, o cachecol balança. Antes ele ficava parado no quadro 1 da caminhada.',
              'parado', old_n=1)
    aren_item('aren_andar', 'Aren andando',
              '8 quadros por direção (antes eram 4): perna levanta, corpo sobe e desce, braços balançam, cachecol voa de lado.',
              'andar', old_n=4)
    aren_item('aren_atacar', 'Aren atacando com a espada',
              '6 quadros: prepara, corta, acompanha o golpe e volta. O arco azul é o efeito de corte novo (dá para desligar). '
              'Hoje a espada gira sozinha em volta do Aren, sem pose de ataque.',
              'atacar', old_n=1, old_note='não existia', slash=True, box=(44, 44, 22, 34))
    aren_item('aren_dano', 'Aren levando dano',
              '2 quadros: susto (olhos apertados, recua) e volta. O clarão branco continua vindo do shader do jogo.',
              'dano', old_n=1, old_note='não existia')
    aren_item('aren_cair', 'Aren caindo (fim de jogo)',
              '6 quadros: cambaleia, ajoelha e cai de bruços. Hoje o jogo só mostra o painel "Aren caiu".',
              'cair', old_n=1, old_note='não existia', views=[('lado', 'side')])

    GDIRS = DIRS

    def gob_item(iid, title, desc, anim, old_n=4, old_note=None, views=GDIRS, single=False):
        variants = {}
        for nome, d in views:
            flip = nome == 'esquerda'
            an = anim if single else f'{anim}_{"lado" if nome == "esquerda" else nome}'
            tr = [old_track('goblin', d, old_n, flip, old_note)]
            for opt in ('A', 'B'):
                tr.append(char_track('goblin', opt, an, flip))
            variants[nome] = tr
        items.append({'id': iid, 'grupo': 'Goblin', 'title': title, 'desc': desc, 'box': (32, 28, 16, 25),
                      'variants': variants})

    gob_item('goblin_andar', 'Goblin andando', '6 quadros por direção (antes eram 4), com a faquinha na mão.', 'andar')
    gob_item('goblin_provocar', 'Goblin provocando',
             '4 quadros: pula, ri de boca aberta e balança a faca. Para dar variedade quando ele está parado ou perto.',
             'provocar', old_n=1, old_note='não existia', views=[('baixo', 'down')], single=True)
    # dano: clarão branco + pose de susto
    variants = {}
    for nome, d, k in (('lado', 'side', 0), ('baixo', 'down', 1), ('esquerda', 'side', 0)):
        flip = nome == 'esquerda'
        tr = [old_track('goblin', d, 1, flip, 'clarão do shader')]
        for opt in ('A', 'B'):
            e = P['goblin'][opt]
            w, h = e['quadro']
            dano = e['animacoes'][f'dano_{"baixo" if nome == "baixo" else "lado"}']['arquivo'][:-4]
            cl = e['animacoes']['clarao']['arquivo'][:-4]
            tr.append({'label': 'Opção ' + opt, 'key': opt, 'img': None, 'seq': [[cl, k * w, 0, w, h], [dano, 0, 0, w, h],
                                                                                   [dano, 0, 0, w, h]],
                       'ox': e['origem'][0], 'oy': e['origem'][1], 'px': 1 / e['escala'], 'flip': flip, 'fps': 8})
        variants[nome] = tr
    items.append({'id': 'goblin_dano', 'grupo': 'Goblin', 'title': 'Goblin levando dano',
                  'desc': '1 quadro de clarão branco (contorno mantido) + a pose de susto. Hoje o clarão é o goblin todo branco por shader.',
                  'box': (32, 28, 16, 25), 'variants': variants})
    gob_item('goblin_morrer', 'Goblin morrendo',
             '6 quadros: pula de susto, achata e some numa nuvem de fumaça. Hoje ele some com partículas soltas.',
             'morrer', old_n=1, old_note='partículas', views=[('baixo', 'down')], single=True)

    def fx_item(iid, title, desc, name, rows=None):
        variants = {}
        for vname, row in (rows or [('—', 0)]):
            tr = []
            for opt in ('A', 'B'):
                f = fx_frames(opt, name, row)
                f.update({'label': 'Opção ' + opt, 'key': opt, 'flip': False})
                tr.append(f)
            variants[vname] = tr
        f = E['A'][name]
        w, h = f['quadro']
        items.append({'id': iid, 'grupo': 'Efeitos', 'title': title, 'desc': desc,
                      'box': (w, h, f['origem'][0], f['origem'][1]), 'variants': variants})

    fx_item('fx_faisca', 'Faísca do acerto', '4 quadros: estrela que abre e se quebra em fagulhas (no inimigo atingido).', 'faisca')
    fx_item('fx_corte', 'Arco do corte (espada)',
            '5 quadros, 8 direções: o "borrão" da lâmina, branco na borda e azul por dentro, afinando na cauda.',
            'corte', rows=[(f'{d}°', i) for i, d in enumerate(E['A']['corte']['direcoes'])])
    fx_item('fx_fumaca', 'Nuvem da morte', '5 quadros: abre, incha, se divide em bolinhas e some.', 'fumaca')
    fx_item('fx_poeira', 'Poeira do passo', '3 quadros pequenos: nasce no pé e se espalha.', 'poeira')
    fx_item('fx_brilho', 'Brilho da joia', '5 quadros: estrela de 4 pontas que pisca e solta pontinhos.', 'brilho')

    meta = {'commit': git_rev(), 'data': datetime.date.today().strftime('%d/%m/%Y'), 'store': STORE, 'tags': TAGS}
    return {'meta': meta, 'img': imgs, 'items': items, 'man': man}


PAGE = r'''<title>Laboratório de Arte do Aren</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=Pixelify+Sans:wght@500;700&display=swap">
<style>
/* Mesmo visual do Laboratório de Som: painéis azul-marinho, bordas douradas de pixel, sombras duras */
:root{
  color-scheme: dark;
  --bg:#13202a; --panel:#1b3a4c; --panel2:#16303f; --line:#2f5a70; --shadow:#0b1218;
  --gold:#f2c14e; --leaf:#8ad65a; --sky:#7fd8ff; --danger:#ef7a5a; --ink:#f6f1e3; --mute:#a9c6d2;
  --display:"Pixelify Sans", ui-monospace, "Courier New", monospace;
  --body:"Atkinson Hyperlegible", system-ui, -apple-system, "Segoe UI", sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0;background:var(--bg)}
body{color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5;overflow-x:hidden}
.wrap{max-width:1180px;margin:0 auto;padding:18px 16px 60px}
h1,h2,h3{font-family:var(--display);font-weight:700;margin:0;text-wrap:balance}
h1{font-size:30px;color:var(--gold);letter-spacing:.02em;text-shadow:2px 2px 0 var(--shadow)}
h2{font-size:22px;color:var(--gold);margin:34px 0 10px;text-shadow:2px 2px 0 var(--shadow)}
h3{font-size:17px}
p{margin:6px 0}
.lead{max-width:70ch}
.small{font-size:13px;color:var(--mute)}
button{font:inherit;color:inherit}
.btn{font-family:var(--display);font-weight:500;font-size:14px;background:var(--panel);color:var(--ink);border:2px solid var(--gold);
  padding:4px 10px;cursor:pointer;box-shadow:2px 2px 0 var(--shadow);display:inline-flex;align-items:center;gap:6px;white-space:nowrap;min-height:34px}
.btn:hover{background:#21465b}
.btn:active{transform:translate(1px,1px);box-shadow:1px 1px 0 var(--shadow)}
.btn.alt{border-color:var(--sky)}
.btn[aria-pressed="true"]{background:var(--gold);color:#1a1a12}
.btn.alt[aria-pressed="true"]{background:var(--sky);color:#0d2230}
:focus-visible{outline:3px solid var(--leaf);outline-offset:2px}
.bar{position:sticky;top:0;z-index:5;background:var(--panel2);border-bottom:2px solid var(--line);margin:16px -16px 0;padding:8px 16px;
  display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center}
.grp{display:inline-flex;gap:4px;align-items:center;flex-wrap:wrap}
.grp>span{font-size:13px;color:var(--mute);margin-right:2px}
.status{margin-left:auto;font-size:13px;display:inline-flex;align-items:center;gap:7px;color:var(--mute)}
.dot{width:10px;height:10px;background:var(--mute);display:inline-block}
.status[data-s="ok"] .dot{background:var(--leaf)} .status[data-s="saving"] .dot{background:var(--gold)}
.status[data-s="off"] .dot,.status[data-s="err"] .dot{background:var(--danger)}
.banner{display:none;margin-top:12px;background:#3a2320;border:2px solid var(--danger);padding:8px 12px;font-size:14px}
.banner.on{display:block}
.card{background:var(--panel);border:2px solid var(--line);box-shadow:3px 3px 0 var(--shadow);padding:12px 14px;margin-top:14px;min-width:0}
.card.gold{border-color:var(--gold)}
.card.has-note{border-color:#3f7290}
.head{display:flex;flex-wrap:wrap;gap:6px 12px;align-items:baseline;justify-content:space-between}
.desc{color:var(--mute);font-size:14px;max-width:80ch}
.stage{display:flex;flex-wrap:wrap;gap:10px;margin-top:10px;align-items:flex-end}
figure{margin:0;display:grid;gap:4px;justify-items:start;max-width:100%}
figcaption{font-family:var(--display);font-size:13px;color:var(--gold)}
figcaption .n{color:var(--mute);font-family:var(--body);font-size:12px;margin-left:4px}
canvas{display:block;image-rendering:pixelated;image-rendering:crisp-edges;border:2px solid var(--shadow);max-width:none}
.scroller{max-width:100%;overflow-x:auto}
.ctrl{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;margin-top:10px}
.ctrl label{font-size:13px;color:var(--mute);display:inline-flex;gap:6px;align-items:center}
.ctrl input[type=range]{width:110px;accent-color:var(--gold)}
.fr{font-family:var(--display);font-size:13px;color:var(--mute);min-width:62px}
.rate{display:grid;gap:8px;margin-top:12px;border-top:2px dashed var(--line);padding-top:10px}
.rate .row{display:flex;flex-wrap:wrap;gap:4px;align-items:center}
.rate .row>span{font-size:13px;color:var(--mute);margin-right:4px}
.rate .btn{font-size:13px;padding:2px 8px;min-height:30px}
textarea{width:100%;font:inherit;font-size:14px;color:var(--ink);background:var(--panel2);border:2px solid var(--line);padding:6px 8px;resize:vertical;min-height:40px}
.saved{font-size:12px;color:var(--mute);min-height:1em}
.choice{display:flex;flex-wrap:wrap;gap:8px;margin-top:10px}
.choice .btn{font-size:15px;min-height:40px;padding:6px 14px}
.opts{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px;margin-top:12px}
.opt{background:var(--panel2);border:2px solid var(--line);padding:10px 12px}
.opt h3{color:var(--gold)}
.opt ul{margin:6px 0 0;padding-left:18px;font-size:14px}
.warn{color:var(--danger)}
footer{margin-top:40px;font-size:13px;color:var(--mute);display:grid;gap:6px;max-width:80ch}
</style>

<div class="wrap">
<header>
  <h1>Laboratório de Arte do Aren</h1>
  <p class="lead">Rodada 1 da arte nova da versão Godot: <b>Aren</b> e o <b>goblin</b> no estilo Minish Cap, mais detalhado
  (mais tons, mais quadros, ataques e efeitos novos). Cada animação toca ao lado da arte de hoje. São duas opções de tamanho:
  <b>A</b> (mesmo tamanho de hoje) e <b>B</b> (o dobro de detalhe). Dê nota, marque etiquetas e escreva o que mudar.
  O jogo continua com a arte antiga até você aprovar.</p>
  <p class="small" id="meta"></p>
  <div class="banner" id="banner">As notas <b>não estão sendo salvas</b> aqui (o armazenamento do artifact não está disponível).
  Elas ficam só neste navegador. Abra a página pelo link do Claude para salvar.</div>
</header>

<div class="bar" role="toolbar" aria-label="Controles gerais">
  <div class="grp" role="group" aria-label="Zoom das animações"><span>Zoom</span>
    <button class="btn" data-zoom="2" type="button">2×</button><button class="btn" data-zoom="4" type="button">4×</button><button class="btn" data-zoom="6" type="button">6×</button></div>
  <div class="grp"><button class="btn alt" id="allPlay" type="button" aria-pressed="true">Tocar tudo</button></div>
  <label class="grp small"><input type="checkbox" id="bBig"> Ver a Opção B com o pixel do mesmo tamanho</label>
  <span class="status" id="status" data-s="wait" aria-live="polite"><span class="dot"></span><span id="statusT">Conectando…</span></span>
</div>

<section>
  <h2>Em jogo</h2>
  <div class="card gold">
    <div class="head"><h3>Aren + 3 goblins, no tamanho do jogo</h3>
      <div class="grp" role="group" aria-label="Escala da cena"><span>Escala da tela</span>
        <button class="btn alt" data-mscale="2" type="button">2×</button><button class="btn alt" data-mscale="4" type="button">4×</button></div></div>
    <p class="desc">Aqui 1 pixel do mundo vale 2 (ou 4) pixels da tela, como no celular e no computador. Assim dá para julgar
    o tamanho e se dá para ler os personagens no meio da grama, não só o desenho ampliado. Na Opção B o mundo teria o dobro de
    pixels: os personagens ficam do mesmo tamanho na tela, mas com o dobro de detalhe, e o chão (aqui o de hoje, por isso
    parece miúdo) teria que ser redesenhado.</p>
    <div class="stage" id="mock"></div>
    <div class="rate" id="rate-em_jogo"></div>
  </div>
  <div class="card gold" id="sizeCard">
    <h3>Qual tamanho você prefere?</h3>
    <div class="opts">
      <div class="opt"><h3>Opção A: mesmo tamanho de mundo</h3><ul>
        <li>Aren com uns 17×28 pixels (hoje 18×24), goblin com uns 22×21 (hoje 18×18).</li>
        <li>Mais tons, contorno colorido e mais quadros, no mesmo espaço.</li>
        <li>Entra no jogo sem mudar mais nada (chão, árvores e câmera ficam como estão).</li></ul></div>
      <div class="opt"><h3>Opção B: o dobro de detalhe</h3><ul>
        <li>Aren com uns 32×54 pixels, goblin com uns 40×42, desenhados no dobro da resolução.</li>
        <li>Olhos com brilho, mechas finas, fivela, costuras, sola da bota.</li>
        <li class="warn">Exige dobrar a resolução do mundo: chão, árvores, arbustos, pedras, joias, corações, espada e os
        outros inimigos teriam que ser refeitos no mesmo nível. É bem mais trabalho, em várias rodadas.</li></ul></div>
    </div>
    <div class="choice" role="group" aria-label="Escolha de tamanho">
      <button class="btn" type="button" data-size="A" aria-pressed="false">Prefiro a Opção A</button>
      <button class="btn" type="button" data-size="B" aria-pressed="false">Prefiro a Opção B</button>
    </div>
    <p class="saved" id="sizeSaved"></p>
  </div>
</section>

<div id="groups"></div>

<footer>
  <p><b>Como foi feito:</b> tudo é desenhado por código (Python, sem gerador de imagem), em <code>tools/arte/</code> do branch
  <code>godot</code>, e sai em folhas PNG em <code>assets/sprites/novo/</code>. As cores partem das do jogo (cabelo castanho,
  túnica azul, cachecol vermelho; goblin verde de olhos amarelos) com tons a mais para dar volume, luz de cima à esquerda.</p>
  <p><b>O que ainda acho fraco:</b> a vista de lado do Aren (o braço e a cabeça ainda são duros), a caminhada de frente do
  goblin (o movimento das pernas é pequeno), e a Opção B ainda nasce da A (contorno ampliado e repintado), então em algumas
  partes parece "A ampliada com detalhes", não um desenho novo do zero.</p>
  <p id="foot"></p>
</footer>
</div>

<script>
const DATA = __DATA__;
const $ = (q, r = document) => r.querySelector(q);
const $$ = (q, r = document) => [...r.querySelectorAll(q)];
function el(tag, attrs = {}, kids = []){
  const e = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs)){
    if (k === 'text') e.textContent = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v);
  }
  for (const c of [].concat(kids)) if (c != null) e.append(c);
  return e;
}
$('#meta').textContent = `Gerado em ${DATA.meta.data} · branch godot @ ${DATA.meta.commit} · notas na coleção ${DATA.meta.store}`;

/* ---------- imagens ---------- */
const IMG = {};
function loadAll(){
  return Promise.all(Object.entries(DATA.img).map(([k, src]) => new Promise(res => {
    const im = new Image(); im.onload = () => { IMG[k] = im; res(); }; im.onerror = () => res(); im.src = src;
  })));
}
function nos(ctx){ ctx.imageSmoothingEnabled = false; return ctx; }
let ZOOM = innerWidth < 600 ? 2 : 4;   // no celular, 2× deixa Antes/A/B lado a lado
try { const z = +localStorage.getItem('aren-arte-zoom'); if ([2, 4, 6].includes(z)) ZOOM = z; } catch {}
let BBIG = false;

function grass(ctx, w, h, scale, ox = 0, oy = 0){
  const g = IMG.grama; if (!g) { ctx.fillStyle = '#72cc52'; ctx.fillRect(0, 0, w, h); return; }
  const t = 16 * scale;
  for (let y = -((oy % t) + t) % t, j = 0; y < h; y += t, j++)
    for (let x = -((ox % t) + t) % t, i = 0; x < w; x += t, i++){
      const v = ((i * 7 + j * 13) % 9) < 6 ? 0 : 1 + ((i + j) % 3);
      ctx.drawImage(g, v * 16, 0, 16, 16, x, y, t, t);
    }
}

/* ---------- tocadores ---------- */
const players = [];
let PLAY_ALL = true;
function frameList(t){
  if (t.seq) return t.seq.map(s => ({img: s[0], r: s.slice(1)}));
  return t.frames.map(r => ({img: t.img, r}));
}
function drawTrack(ctx, t, i, box, zoom, big){
  const px = t.px * (big && t.key === 'B' ? 2 : 1);
  const s = zoom * px;
  const fl = frameList(t), f = fl[i % fl.length], im = IMG[f.img];
  if (!im) return;
  const [sx, sy, sw, sh] = f.r;
  const bx = box[2] * zoom * (big && t.key === 'B' ? 2 : 1), by = box[3] * zoom * (big && t.key === 'B' ? 2 : 1);
  const dx = Math.round(bx - t.ox * s), dy = Math.round(by - t.oy * s);
  if (t.flip){
    ctx.save(); ctx.translate(Math.round(bx * 2), 0); ctx.scale(-1, 1);
    ctx.drawImage(im, sx, sy, sw, sh, dx, dy, sw * s, sh * s); ctx.restore();
  } else ctx.drawImage(im, sx, sy, sw, sh, dx, dy, sw * s, sh * s);
}
function drawOver(ctx, o, i, box, zoom, big){
  const j = i - (o.offset || 0); if (j < 0 || j >= o.frames.length) return;
  const k = big ? 2 : 1, s = zoom * o.px * k;
  const fr = o.frames[j], im = IMG[o.img]; if (!im) return;
  const cx = Math.round((box[2] + o.at[0]) * zoom * k), cy = (box[3] + o.at[1]) * zoom * k;
  ctx.save();
  if (o.flip){ ctx.translate(cx * 2, 0); ctx.scale(-1, 1); }
  ctx.drawImage(im, fr[0], fr[1], fr[2], fr[3], Math.round(cx - o.ox * s), Math.round(cy - o.oy * s), fr[2] * s, fr[3] * s);
  ctx.restore();
}

function makePlayer(item){
  const card = el('div', {class: 'card', id: 'item-' + item.id});
  const vnames = Object.keys(item.variants);
  const st = {item, v: vnames[0], i: 0, playing: true, fps: null, acc: 0, arco: true, canv: []};
  const head = el('div', {class: 'head'}, [el('h3', {text: item.title})]);
  if (vnames.length > 1){
    const g = el('div', {class: 'grp', role: 'group', 'aria-label': 'Direção'}, [el('span', {text: item.grupo === 'Efeitos' ? 'Direção' : 'Vista'})]);
    for (const v of vnames){
      g.append(el('button', {class: 'btn alt', type: 'button', 'aria-pressed': String(v === st.v), text: v,
        onclick: e => { st.v = v; $$('button', g).forEach(b => b.setAttribute('aria-pressed', String(b === e.currentTarget))); build(); }}));
    }
    head.append(g);
  }
  card.append(head, el('p', {class: 'desc', text: item.desc}));
  const stage = el('div', {class: 'stage'});
  card.append(el('div', {class: 'scroller'}, stage));
  const fpsIn = el('input', {type: 'range', min: '2', max: '24', step: '1', 'aria-label': 'Quadros por segundo'});
  const fpsOut = el('span', {class: 'fr'});
  const frOut = el('span', {class: 'fr', 'aria-live': 'off'});
  const playB = el('button', {class: 'btn', type: 'button', text: 'Pausar', onclick: () => { st.playing = !st.playing; sync(); }});
  const prev = el('button', {class: 'btn', type: 'button', 'aria-label': 'Quadro anterior', text: '◀ quadro', onclick: () => { st.playing = false; st.i = (st.i + st.n() - 1) % st.n(); sync(); draw(); }});
  const next = el('button', {class: 'btn', type: 'button', 'aria-label': 'Próximo quadro', text: 'quadro ▶', onclick: () => { st.playing = false; st.i = (st.i + 1) % st.n(); sync(); draw(); }});
  fpsIn.addEventListener('input', () => { st.fps = +fpsIn.value; sync(); });
  const ctrl = el('div', {class: 'ctrl'}, [playB, prev, next, el('label', {}, ['Velocidade', fpsIn]), fpsOut, frOut]);
  const hasOver = item.variants[st.v].some(t => t.over);
  if (hasOver){
    const cb = el('input', {type: 'checkbox', checked: ''});
    cb.addEventListener('change', () => { st.arco = cb.checked; draw(); });
    ctrl.append(el('label', {}, [cb, 'mostrar o arco do corte']));
  }
  card.append(ctrl);
  card.append(el('div', {class: 'rate', id: 'rate-' + item.id}));
  st.tracks = () => item.variants[st.v];
  st.n = () => Math.max(...st.tracks().filter(t => t.key !== 'antes').map(t => frameList(t).length));
  function sync(){
    playB.textContent = st.playing ? 'Pausar' : 'Tocar';
    playB.setAttribute('aria-pressed', String(!st.playing));
    const f = st.fps || st.tracks().find(t => t.key === 'A').fps;
    fpsIn.value = f; fpsOut.textContent = f + ' q/s';
    frOut.textContent = `quadro ${st.i % st.n() + 1}/${st.n()}`;
  }
  function build(){
    stage.textContent = ''; st.canv = [];
    const box = item.box;
    for (const t of st.tracks()){
      const k = BBIG && t.key === 'B' ? 2 : 1;
      const c = el('canvas', {width: String(box[0] * ZOOM * k), height: String(box[1] * ZOOM * k), 'aria-label': `${item.title}: ${t.label}`, role: 'img'});
      const nq = frameList(t).length, q = nq + (nq === 1 ? ' quadro' : ' quadros');
      const n = t.key === 'antes' && t.note ? t.note : q;
      stage.append(el('figure', {}, [c, el('figcaption', {}, [t.label, el('span', {class: 'n', text: n})])]));
      st.canv.push([c, t]);
    }
    st.i = 0; sync(); draw();
  }
  function draw(){
    for (const [c, t] of st.canv){
      const ctx = nos(c.getContext('2d'));
      const big = BBIG && t.key === 'B';
      grass(ctx, c.width, c.height, ZOOM);
      drawTrack(ctx, t, st.i, item.box, ZOOM, BBIG);
      if (t.over && st.arco) drawOver(ctx, t.over, st.i % frameList(t).length, item.box, ZOOM, big);
    }
    frOut.textContent = `quadro ${st.i % st.n() + 1}/${st.n()}`;
  }
  st.tick = dt => {
    if (!st.playing || !PLAY_ALL) return;
    const f = st.fps || st.tracks().find(t => t.key === 'A').fps;
    st.acc += dt;
    const step = 1 / f;
    let moved = false;
    while (st.acc >= step){ st.acc -= step; st.i = (st.i + 1) % 840; moved = true; }
    if (moved) draw();
  };
  st.build = build; st.draw = draw; st.sync = sync;
  players.push(st);
  build();
  return card;
}

/* ---------- cena "em jogo" ---------- */
const MOCK = {scale: 2, views: []};
try { const s = +localStorage.getItem('aren-arte-mscale'); if (s === 2 || s === 4) MOCK.scale = s; } catch {}
function rng(seed){ let s = seed >>> 0; return () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; }
function makeMockView(kind){
  const c = el('canvas', {role: 'img', 'aria-label': 'Cena em jogo: ' + kind});
  const label = {antes: 'Antes (arte de hoje)', A: 'Opção A', B: 'Opção B'}[kind];
  const fig = el('figure', {}, [c, el('figcaption', {text: label})]);
  const v = {kind, c, fig, W: 150, H: 110, t: 0, r: rng(7)};
  v.reset = () => {
    v.aren = {x: v.W / 2, y: v.H / 2 + 6, dir: 'side', flip: false, vx: 12, anim: 0, atk: -1, cd: 0.6, target: null, step: 0};
    v.gobs = [0, 1, 2].map(k => spawn(v, k));
    v.fx = [];
  };
  return v;
}
function spawn(v, k){
  const a = (k * 2.1 + v.r() * 1.2) % (Math.PI * 2);
  const R = Math.max(v.W, v.H) * 0.55;
  return {x: v.W / 2 + Math.cos(a) * R, y: v.H / 2 + Math.sin(a) * R * 0.8, hp: 2, flash: 0, dead: -1, anim: v.r() * 6, kb: [0, 0], wait: 0};
}
function dir4(dx, dy){ return Math.abs(dx) > Math.abs(dy) ? (dx < 0 ? 'left' : 'right') : (dy < 0 ? 'up' : 'down'); }
const M = DATA.man;
function charAnim(kind, char, anim){
  const e = M.personagens[char][kind]; const a = e.animacoes[anim];
  return {img: a.arquivo.replace('.png', ''), w: e.quadro[0], h: e.quadro[1], ox: e.origem[0], oy: e.origem[1], n: a.quadros, px: 1 / e.escala, fps: a.fps};
}
function blit(ctx, v, A, i, x, y, flip, white){
  const S = MOCK.scale, s = S * A.px, im = IMG[A.img]; if (!im) return;
  const fi = Math.floor(i) % A.n, row = A.row || 0;
  const X = Math.round(x * S), Y = Math.round(y * S);
  const dx = X - Math.round(A.ox * s), dy = Y - Math.round(A.oy * s);
  ctx.save();
  if (flip){ ctx.translate(X * 2, 0); ctx.scale(-1, 1); }
  ctx.drawImage(im, fi * A.w, row * A.h, A.w, A.h, dx, dy, A.w * s, A.h * s);
  ctx.restore();
}
function mockStep(v, dt){
  const P = v.aren;
  P.cd -= dt;
  // alvo: goblin vivo mais perto
  let best = null, bd = 1e9;
  for (const g of v.gobs){ if (g.dead >= 0) continue; const d = Math.hypot(g.x - P.x, g.y - (P.y - 4)); if (d < bd){ bd = d; best = g; } }
  if (P.atk >= 0){
    const was = P.atk; P.atk += dt * 14;
    if (was < 1 && P.atk >= 1 && v.kind !== 'antes') v.fx.push({k: 'corte', x: P.x, y: P.y - 11, t: 0, row: P.slashRow, flip: P.flip && P.dir === 'side'});
    if (P.atk >= 3 && !P.hit && P.target){
      P.hit = true; const g = P.target;
      if (g.dead < 0 && Math.hypot(g.x - P.x, g.y - P.y) < 30){
        g.hp--; g.flash = 0.12; const a = Math.atan2(g.y - P.y, g.x - P.x); g.kb = [Math.cos(a) * 40, Math.sin(a) * 40];
        v.fx.push({k: 'faisca', x: g.x, y: g.y - 8, t: 0});
        if (g.hp <= 0){ g.dead = 0; }
      }
    }
    if (P.atk >= 6){ P.atk = -1; P.cd = 0.45; }
  } else if (best && bd < 24 && P.cd <= 0){
    P.atk = 0; P.hit = false; P.target = best;
    const dx = best.x - P.x, dy = best.y - P.y; const d4 = dir4(dx, dy);
    P.dir = d4 === 'up' ? 'up' : d4 === 'down' ? 'down' : 'side'; P.flip = d4 === 'left';
    P.slashDir = (Math.round(Math.atan2(dy, dx) / (Math.PI / 4)) + 8) % 8;
    P.slashRow = P.dir === 'down' ? 2 : P.dir === 'up' ? 6 : 0;
  } else {
    // passeia de um lado para o outro
    P.x += P.vx * dt;
    if (P.x > v.W * 0.62){ P.vx = -Math.abs(P.vx); }
    if (P.x < v.W * 0.38){ P.vx = Math.abs(P.vx); }
    P.dir = 'side'; P.flip = P.vx < 0;
    const before = Math.floor(P.anim); P.anim += dt * (v.kind === 'antes' ? 9 : 12);
    const f = Math.floor(P.anim) % (v.kind === 'antes' ? 4 : 8);
    if (Math.floor(P.anim) !== before && (f === 0 || f === 4) && v.kind !== 'antes') v.fx.push({k: 'poeira', x: P.x - (P.flip ? -3 : 3), y: P.y, t: 0});
  }
  for (const g of v.gobs){
    if (g.dead >= 0){
      g.dead += dt;
      if (g.dead > 0.5 && !g.gem){ g.gem = true; v.fx.push({k: 'brilho', x: g.x, y: g.y - 4, t: 0}); }
      if (g.dead > 1.6){ Object.assign(g, spawn(v, Math.floor(v.r() * 3))); g.gem = false; }
      continue;
    }
    g.flash = Math.max(0, g.flash - dt);
    g.x += g.kb[0] * dt; g.y += g.kb[1] * dt; g.kb = g.kb.map(k => k * Math.pow(0.02, dt));
    const dx = P.x - g.x, dy = P.y - g.y, d = Math.hypot(dx, dy);
    if (d > 15){ g.x += dx / d * 16 * dt; g.y += dy / d * 16 * dt; g.anim += dt * 10; g.taunt = 0; }
    else { g.taunt = (g.taunt || 0) + dt; }
    g.face = dir4(dx, dy);
  }
  for (const f of v.fx) f.t += dt;
  v.fx = v.fx.filter(f => f.t < 0.6);
}
function mockDraw(v){
  const S = MOCK.scale, c = v.c, ctx = nos(c.getContext('2d'));
  const kind = v.kind;
  grass(ctx, c.width, c.height, kind === 'B' ? S / 2 : S);
  const P = v.aren, ents = [];
  ents.push({y: P.y, draw: () => {
    if (kind === 'antes'){
      const d = P.dir === 'side' ? 'side' : P.dir;
      const A = {img: 'old_hero_' + d, w: 18, h: 24, ox: 9, oy: 24, n: 4, px: 1};
      blit(ctx, v, A, P.atk >= 0 ? 0 : P.anim, P.x, P.y, P.flip);
      if (P.atk >= 0){ // espada antiga girando
        const sw = {img: 'old_sword', w: 45, h: 45, ox: 22, oy: 22, n: 48, px: 1};
        const a0 = P.slashDir * Math.PI / 4 - 1.25 + Math.min(1, P.atk / 6) * 2.5;
        const idx = ((Math.round(a0 / (Math.PI * 2) * 48) % 48) + 48) % 48;
        blit(ctx, v, sw, idx, P.x + Math.cos(a0) * 10, P.y - 10 + Math.sin(a0) * 10, false);
      }
    } else {
      const nm = {down: 'baixo', up: 'cima', side: 'lado'}[P.dir];
      const A = P.atk >= 0 ? charAnim(kind, 'aren', 'atacar_' + nm) : charAnim(kind, 'aren', 'andar_lado');
      blit(ctx, v, A, P.atk >= 0 ? P.atk : P.anim, P.x, P.y, P.flip);
    }
  }});
  for (const g of v.gobs){
    ents.push({y: g.y, draw: () => {
      const side = g.face === 'left' || g.face === 'right', flip = g.face === 'left';
      if (kind === 'antes'){
        if (g.dead >= 0){
          if (g.dead < 0.4){ ctx.fillStyle = '#e8f0d0'; for (let k = 0; k < 8; k++){ const a = k * 0.785, r = 2 + g.dead * 30;
            ctx.fillRect(Math.round((g.x + Math.cos(a) * r) * S), Math.round((g.y - 8 + Math.sin(a) * r) * S), S, S); } }
          return;
        }
        const d = side ? 'side' : g.face;
        const A = {img: 'old_goblin_' + d, w: 22, h: 22, ox: 11, oy: 21, n: 4, px: 1};
        blit(ctx, v, A, g.anim, g.x, g.y, flip);
        return;
      }
      if (g.dead >= 0){
        const A = charAnim(kind, 'goblin', 'morrer');
        if (g.dead * A.fps < A.n) blit(ctx, v, A, g.dead * A.fps, g.x, g.y, false);
        return;
      }
      let A;
      if (g.flash > 0){ A = Object.assign(charAnim(kind, 'goblin', 'clarao'), {}); blit(ctx, v, A, side ? 0 : 1, g.x, g.y, flip); return; }
      if (g.taunt > 0.3){ A = charAnim(kind, 'goblin', 'provocar'); blit(ctx, v, A, g.taunt * A.fps, g.x, g.y, false); return; }
      A = charAnim(kind, 'goblin', 'andar_' + (side ? 'lado' : g.face === 'up' ? 'cima' : 'baixo'));
      blit(ctx, v, A, g.anim, g.x, g.y, flip);
    }});
  }
  ents.sort((a, b) => a.y - b.y).forEach(e => e.draw());
  if (kind !== 'antes'){
    for (const f of v.fx){
      const e = M.efeitos[kind][f.k];
      const A = {img: e.arquivo.replace('.png', ''), w: e.quadro[0], h: e.quadro[1], ox: e.origem[0], oy: e.origem[1], n: e.quadros, px: kind === 'B' ? 0.5 : 1, row: f.row || 0};
      const i = f.t * e.fps; if (i < A.n) blit(ctx, v, A, i, f.x, f.y, !!f.flip);
    }
  } else {
    for (const f of v.fx){ if (f.k !== 'faisca') continue; ctx.fillStyle = '#fff6c0';
      for (let k = 0; k < 5; k++){ const a = k * 1.25, r = 1 + f.t * 40; if (f.t < 0.25) ctx.fillRect(Math.round((f.x + Math.cos(a) * r) * S), Math.round((f.y + Math.sin(a) * r) * S), S, S); } }
  }
}
function mockLayout(){
  const host = $('#mock'); const avail = Math.max(200, host.clientWidth || 340);
  const S = MOCK.scale;
  // três lado a lado se couber, senão um embaixo do outro
  let per = Math.floor((avail - 24) / 3);
  if (per < 150 * S * 0.8) per = avail;
  const W = Math.max(80, Math.min(200, Math.floor((per - 6) / S)));
  const H = Math.round(W * 0.72);
  for (const v of MOCK.views){
    v.W = W; v.H = H; v.c.width = W * S; v.c.height = H * S; v.reset();
  }
  $$('[data-mscale]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.mscale === S)));
}
function initMock(){
  const host = $('#mock');
  MOCK.views = ['antes', 'A', 'B'].map(makeMockView);
  for (const v of MOCK.views) host.append(v.fig);
  mockLayout();
  $$('[data-mscale]').forEach(b => b.addEventListener('click', () => { MOCK.scale = +b.dataset.mscale; try { localStorage.setItem('aren-arte-mscale', MOCK.scale); } catch {} mockLayout(); }));
  let rt; addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(mockLayout, 150); });
}

/* ---------- notas (capacidade db; coleção arte_r1) ---------- */
const ST = {}, Q = {}, rows = {};
let db = null;
const LS = 'aren-arte-r1-rascunho';
try { Object.assign(ST, JSON.parse(localStorage.getItem(LS) || '{}')); } catch {}
function draft(){ try { localStorage.setItem(LS, JSON.stringify(ST)); } catch {} }
function status(s, t){ const e = $('#status'); e.dataset.s = s; $('#statusT').textContent = t; }
function save(id){
  ST[id] = Object.assign({}, ST[id], {atualizado: new Date().toISOString()}); draft(); rows[id]?.saved('Salvando…');
  if (!db){ rows[id]?.saved('Guardado só neste navegador'); return; }
  const q = Q[id] || (Q[id] = {busy: false, dirty: false}); q.dirty = true; if (q.busy) return;
  (async () => {
    q.busy = true; status('saving', 'Salvando…');
    while (q.dirty){
      q.dirty = false;
      try { await db.collection(DATA.meta.store).doc(id).set(Object.assign({}, ST[id])); rows[id]?.saved('Salvo'); status('ok', 'Notas guardadas'); }
      catch (e){ rows[id]?.saved('Não foi possível salvar agora'); status('err', 'Erro ao salvar: ' + (e && e.code || 'desconhecido')); break; }
    }
    q.busy = false;
  })();
}
const saveTimers = {};
function saveSoon(id){
  const q = Q[id] || (Q[id] = {busy: false, dirty: false}); q.pend = true;
  clearTimeout(saveTimers[id]); saveTimers[id] = setTimeout(() => { q.pend = false; save(id); }, 700);
}
let subscribed = false;
async function connect(){
  try { db = window.claude && window.claude.use ? await window.claude.use('db') : null; } catch { db = null; }
  if (!db){ status('off', 'Sem armazenamento: notas só neste navegador'); $('#banner').classList.add('on'); return; }
  if (subscribed) return; subscribed = true;
  const timer = setTimeout(() => status('wait', 'O armazenamento está demorando a responder'), 10000);
  try {
    db.collection(DATA.meta.store).onSnapshot(snap => {
      if (!snap.metadata || !snap.metadata.fromCache){ clearTimeout(timer); if ($('#status').dataset.s !== 'saving') status('ok', 'Notas guardadas'); }
      for (const d of snap.docs){
        const q = Q[d.id]; if (q && (q.busy || q.dirty || q.pend)) continue;
        ST[d.id] = Object.assign({}, d.data()); rows[d.id]?.sync();
      }
      draft();
    }, e => { clearTimeout(timer); status('err', 'Armazenamento indisponível (' + (e && e.code || 'erro') + ')'); });
  } catch (e){ status('err', 'Armazenamento indisponível'); }
}
function rating(id, host){
  const st = () => ST[id] || (ST[id] = {});
  const stars = [1, 2, 3, 4, 5].map(n => el('button', {class: 'btn', type: 'button', 'aria-pressed': 'false', 'aria-label': 'Nota ' + n, text: String(n),
    onclick: () => { const s = st(); s.nota = s.nota === n ? null : n; sync(); save(id); }}));
  const tags = DATA.meta.tags.map(t => el('button', {class: 'btn alt', type: 'button', 'aria-pressed': 'false', text: t,
    onclick: () => { const s = st(); const a = new Set(s.tags || []); a.has(t) ? a.delete(t) : a.add(t); s.tags = [...a]; sync(); save(id); }}));
  const ta = el('textarea', {rows: '2', placeholder: 'O que mudar? (opcional)', 'aria-label': 'Comentário'});
  ta.addEventListener('input', () => { st().comentario = ta.value; saveSoon(id); });
  const sv = el('p', {class: 'saved'});
  host.append(el('div', {class: 'row', role: 'group', 'aria-label': 'Nota'}, [el('span', {text: 'Nota'}), ...stars]),
    el('div', {class: 'row', role: 'group', 'aria-label': 'Etiquetas'}, [el('span', {text: 'Etiquetas'}), ...tags]), ta, sv);
  function sync(){
    const s = ST[id] || {};
    stars.forEach((b, k) => b.setAttribute('aria-pressed', String(s.nota === k + 1)));
    tags.forEach(b => b.setAttribute('aria-pressed', String((s.tags || []).includes(b.textContent))));
    if (document.activeElement !== ta) ta.value = s.comentario || '';
    host.closest('.card')?.classList.toggle('has-note', !!(s.nota || (s.tags || []).length || s.comentario));
  }
  rows[id] = {sync, saved: t => { sv.textContent = t; }};
  sync();
}
function sizeChoice(){
  const btns = $$('[data-size]');
  function sync(){ const e = (ST.tamanho || {}).escolha; btns.forEach(b => b.setAttribute('aria-pressed', String(b.dataset.size === e))); }
  btns.forEach(b => b.addEventListener('click', () => {
    const s = ST.tamanho || (ST.tamanho = {}); s.escolha = s.escolha === b.dataset.size ? null : b.dataset.size; sync(); save('tamanho');
  }));
  rows.tamanho = {sync, saved: t => { $('#sizeSaved').textContent = t; }};
  sync();
}

/* ---------- montagem ---------- */
function buildGroups(){
  const host = $('#groups');
  const groups = {};
  for (const it of DATA.items) (groups[it.grupo] || (groups[it.grupo] = [])).push(it);
  const intro = {Aren: 'Antes = sprite de hoje (vindo do jogo HTML). A e B na mesma escala de mundo: B tem o dobro de pixels no mesmo tamanho.',
    Goblin: 'Mesma identidade: pele verde, orelhonas, olhos amarelos, dentes, tanga e faquinha.',
    Efeitos: 'Efeitos desenhados em pixel (folhas de quadros), para usar em AnimatedSprite2D ou como textura de partícula. Hoje o jogo faz faísca, poeira e brilho com partículas soltas de 1–2 px, sem desenho.'};
  for (const [g, list] of Object.entries(groups)){
    host.append(el('h2', {text: g}), el('p', {class: 'small', text: intro[g] || ''}));
    for (const it of list){ host.append(makePlayer(it)); rating(it.id, $('#rate-' + it.id)); }
  }
}
function setZoom(z){
  ZOOM = z; try { localStorage.setItem('aren-arte-zoom', z); } catch {}
  $$('[data-zoom]').forEach(b => b.setAttribute('aria-pressed', String(+b.dataset.zoom === z)));
  players.forEach(p => p.build());
}
async function main(){
  await loadAll();
  initMock();
  buildGroups();
  rating('em_jogo', $('#rate-em_jogo'));
  sizeChoice();
  $$('[data-zoom]').forEach(b => b.addEventListener('click', () => setZoom(+b.dataset.zoom)));
  setZoom(ZOOM);
  $('#allPlay').addEventListener('click', e => { PLAY_ALL = !PLAY_ALL; e.currentTarget.setAttribute('aria-pressed', String(PLAY_ALL)); e.currentTarget.textContent = PLAY_ALL ? 'Tocar tudo' : 'Tudo pausado'; });
  $('#bBig').addEventListener('change', e => { BBIG = e.target.checked; players.forEach(p => p.build()); });
  $('#foot').textContent = `Notas: coleção ${DATA.meta.store} (um documento por item: nota, etiquetas, comentário; e "tamanho" com a escolha A ou B).`;
  let last = performance.now();
  function loop(now){
    const dt = Math.min(0.1, (now - last) / 1000); last = now;
    for (const p of players) p.tick(dt);
    if (PLAY_ALL) for (const v of MOCK.views){ mockStep(v, dt); mockDraw(v); }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
  window.__lab = {players, MOCK, ST};
  connect();
}
main();
</script>
'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    data = build_data()
    html = PAGE.replace('__DATA__', json.dumps(data, ensure_ascii=False, separators=(',', ':')))
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, 'w', encoding='utf-8') as fh:
        fh.write(html)
    print(f'{args.out}: {len(html) / 1e6:.2f} MB, {len(data["items"])} itens')


if __name__ == '__main__':
    main()
