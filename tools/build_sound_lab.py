#!/usr/bin/env python3
"""Gera o Laboratório de Som: uma página para ouvir, comparar e avaliar cada som do jogo.

A página usa o MESMO módulo SFX de src/bosque-do-enxame.html (copiado no build, com ganchos de teste
só na cópia), o catálogo tools/sound_catalog.json e os volumes medidos por tools/sfx_levels.py.
Também embute o módulo de som da rodada anterior (commit BEFORE_REV, como SFX_OLD), para os botões
"Antes" e "Agora" dos sons com 'estado' no catálogo. Rodada 5: as notas vão para a coleção STORE
(`avaliacoes_r5`) do armazenamento `db` do artifact; a nota anterior de cada som aparece só para leitura,
vinda de PREV_STORE (`avaliacoes_r4`) ou, se o som não tiver nota lá, das rodadas antes dela
(OLDER_STORES: `avaliacoes_r3`, `avaliacoes_r2`, depois `avaliacoes` da rodada 1). Nada é gravado nessas coleções antigas.
O commit "Antes" e as coleções podem ser trocados por opções (--before, --store, --prev-store).
A saída é um fragmento HTML (sem doctype): o publicador do artifact põe o cabeçalho.

    python3 tools/build_sound_lab.py --out /caminho/laboratorio-som.html
    python3 tools/build_sound_lab.py --out lab.html --levels /tmp/levels.json   # reaproveita medição
    python3 tools/build_sound_lab.py --out lab.html --levels l.json --levels-old antes.json
    python3 tools/build_sound_lab.py --out lab.html --before 9e732e4 --store avaliacoes_r5 --prev-store avaliacoes_r4
"""
import argparse, asyncio, datetime, json, os, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sfx_levels  # noqa: E402

ROOT = sfx_levels.ROOT

# Proposed mix (only heard in the lab; the game does not change until the owner approves):
LOUD_CAP_DB = 6.0       # effects more than this above the fire explosion come down to it
BIG_MOMENT_CAP_DB = 8.0 # dragon arrival, rage and death may stay a little louder
BIG_MOMENTS = {'roarIntro', 'roarRage', 'dragonDeath'}
WARN_FLOOR_DB = -8.0    # attack warnings (and the bow, heard all the time) come up to this
WARN_IDS = {'scrape', 'windup', 'jump', 'zapWarn', 'chainCharge', 'bow'}
# Round 5 defaults (each can be overridden on the command line)
ROUND = 5
BEFORE_REV = '9e732e4'       # "Antes": the game as the owner heard it in round 4
STORE = 'avaliacoes_r5'      # this round's ratings
PREV_STORE = 'avaliacoes_r4' # previous round's notes, shown read-only under each row
OLDER_STORES = [('avaliacoes_r3', 3), ('avaliacoes_r2', 2), ('avaliacoes', 1)]   # fallbacks, newest first (round 1 = 'avaliacoes')
DECIDED = {'windup'}         # volume proposals the owner already answered ("igual"): no Proposta button
# round-1 "silent moment" rows -> the sounds that answer them (for the round-1 fallback note)
R1_MAP = {'x_hurt': ['hurt'], 'x_gem': ['gem'], 'x_heart': ['heart', 'heart2'], 'x_lvl': ['lvlSmall'], 'x_sword': ['sword', 'sword5'],
          'x_boom': ['boomThrow'], 'x_fire': ['fireCast'], 'x_wisp': ['wisp'], 'x_storm': ['storm'], 'x_holy': ['holy'],
          'x_arrow': ['elfArrow'], 'x_wfire': ['wyvernFire'], 'x_elite': ['elite'], 'x_lowhp': ['lowHp'], 'x_ui': ['ui', 'uiPick'],
          'x_pause': ['pauseOpen', 'pauseClose'], 'x_stinger': ['win_sfx', 'lose_sfx'], 'x_kill': None}   # None: every kill_* row


def proposals(levels):
    ref = levels['explode']['rms150_db']
    out = {}
    for k, v in levels.items():
        if v['group'] == 'musica':
            continue
        rel = v['rms150_db'] - ref
        g, why = 0.0, ''
        cap = BIG_MOMENT_CAP_DB if k in BIG_MOMENTS else LOUD_CAP_DB
        if rel > cap:
            g, why = cap - rel, f'Fica {fmt(rel)} dB acima da explosão de fogo; a proposta deixa em {fmt(cap)}.'
        elif k in WARN_IDS and rel < WARN_FLOOR_DB and k not in DECIDED:
            g, why = WARN_FLOOR_DB - rel, (f'Fica {fmt(rel)} dB abaixo da explosão; some no meio da luta. '
                                           f'A proposta sobe para {fmt(WARN_FLOOR_DB)}.')
        g = round(g*2)/2
        if abs(g) >= 1:
            out[k] = {'db': g, 'why': why}
    return out


def fmt(v):
    s = f'{v:+.1f}' if v else '0'
    return s.replace('.', ',').replace('-', '−')


def calls_js(cat):
    lines = []
    for g in cat['groups']:
        for s in g['sounds']:
            if s.get('call'):
                lines.append(f"  {json.dumps(s['id'])}: S => {s['call']},")
    return '{\n' + '\n'.join(lines) + '\n}'


def git(*a):
    try:
        return subprocess.check_output(['git', '-C', ROOT, *a], text=True).strip()
    except Exception:
        return '?'


def build(out_path, levels_path=None, old_levels_path=None, before_rev=None, store=None, prev_store=None):
    before_rev, store, prev_store = before_rev or BEFORE_REV, store or STORE, prev_store or PREV_STORE
    cat = sfx_levels.load_catalog()
    if levels_path:
        with open(levels_path, encoding='utf-8') as f:
            levels = json.load(f)
    else:
        levels = asyncio.run(sfx_levels.measure())
    missing = [s['id'] for _, s in sfx_levels.items(cat) if s['id'] not in levels]
    if missing:
        raise SystemExit('erro: medição sem estes ids (rode sfx_levels.py de novo): ' + ', '.join(missing))
    old_src = sfx_levels.git_src(before_rev)
    before = {s['id'] for _, s in sfx_levels.items(cat) if s.get('estado') in ('refeito', 'volume')} | {'explode'}
    if old_levels_path:
        with open(old_levels_path, encoding='utf-8') as f:
            old_levels = json.load(f)
    else:
        old_levels = asyncio.run(sfx_levels.measure(before, old_src))
    r1map = {}
    for k, v in R1_MAP.items():
        for sid in (v if v is not None else [s['id'] for _, s in sfx_levels.items(cat) if s['id'].startswith('kill_')]):
            r1map[sid] = k
    mod = sfx_levels.extract_sfx(open(sfx_levels.SRC, encoding='utf-8').read())
    old = sfx_levels.extract_sfx(old_src).replace('const SFX = (() => {', 'const SFX_OLD = (() => {', 1)
    data = {
        'groups': cat['groups'], 'mudos': cat['mudos'], 'levels': levels, 'proposals': proposals(levels),
        'ref': levels['explode']['rms150_db'], 'levelsOld': old_levels, 'refOld': old_levels['explode']['rms150_db'],
        'before': sorted(i for _, x in sfx_levels.items(cat) if x.get('estado') in ('refeito', 'volume') for i in [x['id']]),
        'r1map': r1map, 'store': store, 'prev': [[prev_store, ROUND - 1]] + [[n, r] for n, r in OLDER_STORES if n != prev_store], 'round': ROUND,
        'meta': {'commit': git('rev-parse', '--short', 'HEAD'), 'before': before_rev, 'date': datetime.date.today().strftime('%d/%m/%Y')},
    }
    js_data = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    html = (TEMPLATE.replace('%DATA%', js_data).replace('%CALLS%', calls_js(cat))
                    .replace('%MODULE_OLD%', old.replace('</script', '<\\/script'))
                    .replace('%MODULE%', mod.replace('</script', '<\\/script')))
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(html)
    return data


TEMPLATE = r"""<title>Laboratório de Som do Aren</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&family=IBM+Plex+Mono:wght@500&family=Pixelify+Sans:wght@500;700&display=swap">
<style>
/* Layout: the game's own panel look (navy, gold pixel borders, hard shadows); one column of sound rows under a sticky control bar */
:root{
  color-scheme: dark;
  --bg:#13202a; --panel:#1b3a4c; --panel2:#16303f; --line:#2f5a70; --shadow:#0b1218;
  --gold:#f2c14e; --leaf:#8ad65a; --sky:#7fd8ff; --danger:#ef7a5a; --ink:#f6f1e3; --mute:#a9c6d2;
  --display:"Pixelify Sans", ui-monospace, "Courier New", monospace;
  --body:"Atkinson Hyperlegible", system-ui, -apple-system, "Segoe UI", sans-serif;
  --mono:"IBM Plex Mono", ui-monospace, "SFMono-Regular", Menlo, monospace;
}
*{box-sizing:border-box}
body{background:var(--bg);color:var(--ink);font-family:var(--body);font-size:15px;line-height:1.5}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--panel2)}
.wrap{max-width:980px;margin:0 auto;padding-block:20px 48px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1,h2,h3{font-family:var(--display);font-weight:700;text-wrap:balance;margin:0}
h1{font-size:30px;color:var(--gold);letter-spacing:.02em;text-shadow:2px 2px 0 var(--shadow)}
h2{font-size:21px;color:var(--gold);margin-top:34px;margin-bottom:10px;text-shadow:2px 2px 0 var(--shadow)}
h3{font-size:16px}
p{margin:0}
.lead{max-width:66ch;margin-top:8px;color:var(--ink)}
.small{font-size:13px;color:var(--mute)}
.mono{font-family:var(--mono);font-variant-numeric:tabular-nums}
button{font:inherit;color:inherit}
.btn{font-family:var(--display);font-weight:500;font-size:14px;background:var(--panel);color:var(--ink);border:2px solid var(--gold);
  padding:5px 11px;cursor:pointer;box-shadow:2px 2px 0 var(--shadow);display:inline-flex;align-items:center;gap:6px;white-space:nowrap;min-height:34px}
.btn:hover{background:#21465b}
.btn:active{transform:translate(1px,1px);box-shadow:1px 1px 0 var(--shadow)}
.btn.alt{border-color:var(--sky)}
.btn[aria-pressed="true"]{background:var(--gold);color:#1a1a12}
.btn.alt[aria-pressed="true"]{background:var(--sky);color:#0d2230}
.btn.playing{background:var(--leaf);color:#13240a;border-color:var(--leaf)}
:focus-visible{outline:3px solid var(--leaf);outline-offset:2px}
.tri{width:0;height:0;border-left:8px solid currentColor;border-top:5px solid transparent;border-bottom:5px solid transparent}
.sq{width:9px;height:9px;background:currentColor}

/* sticky control bar */
.bar{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--panel2);border-bottom:2px solid var(--line);margin-top:16px}
.bar-in{max-width:980px;margin:0 auto;padding-block:9px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px));
  display:flex;flex-wrap:wrap;gap:8px 16px;align-items:center}
.bar label{display:inline-flex;align-items:center;gap:8px;font-size:14px}
.bar input[type=range]{width:120px;accent-color:var(--gold)}
.status{margin-left:auto;font-size:13px;display:inline-flex;align-items:center;gap:7px;color:var(--mute)}
.dot{width:10px;height:10px;background:var(--mute);display:inline-block}
.status[data-s="ok"] .dot{background:var(--leaf)} .status[data-s="saving"] .dot{background:var(--gold)}
.status[data-s="off"] .dot,.status[data-s="err"] .dot{background:var(--danger)}

/* findings */
.finds{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:12px}
.find{background:var(--panel);border:2px solid var(--line);padding:12px 14px;min-width:0}
.find h3{color:var(--ink);margin-bottom:4px}
.find .tag{font-family:var(--display);font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--gold)}
.find p{font-size:14px;color:var(--mute)}
.find b{color:var(--ink)}

/* scene */
.scene{background:var(--panel);border:2px solid var(--gold);box-shadow:3px 3px 0 var(--shadow);padding:14px;display:grid;gap:10px}
.scene .row-btns{display:flex;flex-wrap:wrap;gap:8px}

/* sound rows */
.group{display:grid;gap:8px}
.snd{background:var(--panel);border:2px solid var(--line);padding:10px 12px;display:grid;gap:8px 14px;
  grid-template-columns:minmax(0,1.25fr) minmax(0,1fr) minmax(0,1.1fr);align-items:start}
.snd.has-note{border-color:#3f7290}
.who h3{font-family:var(--body);font-weight:700;font-size:15px}
.who p{font-size:13px;color:var(--mute)}
.plays{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}
.lvl{min-width:0}
.meter{position:relative;height:12px;background:var(--panel2);border:2px solid var(--line);margin-top:4px}
.meter i{position:absolute;left:0;top:0;bottom:0;background:var(--mute)}
.meter[data-k="hi"] i{background:var(--danger)} .meter[data-k="lo"] i{background:var(--sky)} .meter[data-k="ok"] i{background:var(--leaf)}
.meter u{position:absolute;top:-5px;bottom:-5px;width:2px;background:var(--gold)}
.chip{display:inline-block;font-family:var(--display);font-size:12px;padding:1px 6px;border:2px solid currentColor;margin-top:6px}
.chip.hi{color:var(--danger)} .chip.lo{color:var(--sky)} .chip.ok{color:var(--leaf)}
.why{font-size:12.5px;color:var(--mute);margin-top:4px}
.rate{display:grid;gap:6px;min-width:0}
.stars{display:flex;gap:4px;flex-wrap:wrap}
.stars .btn{min-width:34px;justify-content:center;padding:4px 0}
.tags{display:flex;gap:4px;flex-wrap:wrap}
.tags .btn{font-size:12px;padding:2px 7px;min-height:28px;border-width:2px}
.pref{display:flex;gap:4px;flex-wrap:wrap;align-items:center;font-size:12.5px;color:var(--mute)}
.pref .btn{font-size:12px;padding:2px 7px;min-height:28px}
textarea{width:100%;font:inherit;font-size:14px;color:var(--ink);background:var(--panel2);border:2px solid var(--line);padding:6px 8px;resize:vertical;min-height:38px}
textarea::placeholder{color:#7f9aa6}
.saved{font-size:12px;color:var(--mute);min-height:1em}
.mudo{grid-template-columns:minmax(0,1.25fr) minmax(0,2.1fr)}
footer{margin-top:40px;font-size:13px;color:var(--mute);display:grid;gap:6px;max-width:72ch}
.badge{display:inline-block;font-family:var(--display);font-size:12px;letter-spacing:.04em;padding:0 6px;border:2px solid currentColor;margin-left:6px;vertical-align:2px;white-space:nowrap}
.badge.refeito{color:var(--gold)} .badge.novo{color:var(--leaf)} .badge.volume{color:var(--sky)}
.prev{font-size:12.5px;color:var(--mute);border-left:3px solid var(--line);padding:2px 0 2px 8px;overflow-wrap:anywhere}
.prev b{color:var(--ink);font-weight:700}
.was{font-size:12.5px;color:var(--mute);margin-top:4px}
.filter{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:14px}
@media (max-width:760px){
  .snd,.mudo{grid-template-columns:1fr}
  .status{margin-left:0}
  h1{font-size:25px}
}
@media (prefers-reduced-motion:no-preference){ .btn.playing{animation:blink .5s steps(2) infinite} @keyframes blink{50%{filter:brightness(1.25)}} }
</style>

<div class="wrap">
  <h1>Laboratório de Som do Aren · rodada 5</h1>
  <p class="lead">Fiz os ajustes que você pediu na rodada 4 e o último lote dos monstros: orc, elfo e esqueleto agora também fazem barulho quando estão perto de Aren. Com isso, <b>todos os monstros têm som de presença</b>. Cada som que mudou tem <b>Antes</b> (a versão da rodada 4) e <b>Agora</b>. Os sons novos só têm <b>Agora</b>. Use <b>Só o que mudou</b> para ver só eles.</p>
  <p class="small" id="meta"></p>
</div>

<div class="bar" role="region" aria-label="Controles">
  <div class="bar-in">
    <button class="btn" id="stopAll" type="button"><span class="sq"></span>Parar tudo</button>
    <label><input type="checkbox" id="backing"> Ouvir os efeitos com a música de combate</label>
    <span class="filter" role="group" aria-label="Mostrar">Mostrar:
      <button class="btn alt" type="button" data-f="todos" aria-pressed="true">Todos</button>
      <button class="btn alt" type="button" data-f="mudou" aria-pressed="false">Só o que mudou</button>
    </span>
    <span class="status" id="status" data-s="wait"><span class="dot"></span><span id="statusT">Conectando ao armazenamento…</span></span>
  </div>
</div>

<div class="wrap">
  <h2>O que mudou nesta rodada</h2>
  <div class="finds" id="finds"></div>

  <h2>Cena de teste</h2>
  <div class="scene">
    <p>Treze segundos de luta: música de combate, espada, fogo, arco, martelo, goblins, gárgula, hobgoblin, orc, elfo, esqueleto, demônio, súcubo e serpe por perto, inimigos morrendo, joias, flecha de elfo, risadas, relâmpago, Cajado da Tempestade, dano e subir de nível. <b>Antes</b> toca como estava na rodada 4 (sem as vozes novas); <b>Agora</b> toca tudo como está hoje.</p>
    <div class="row-btns">
      <button class="btn" type="button" id="sceneOld"><span class="tri"></span>Antes</button>
      <button class="btn alt" type="button" id="sceneNew"><span class="tri"></span>Agora</button>
    </div>
    <div class="pref" id="scenePref"></div>
    <textarea id="sceneTxt" rows="2" placeholder="O que você achou da cena? (opcional)"></textarea>
    <div class="prev" id="scenePrev" hidden></div>
    <div class="saved" id="sceneSaved"></div>
  </div>

  <div id="groups"></div>

  <section id="mudosSec" hidden>
    <h2>Momentos sem som</h2>
    <p class="small" style="margin-bottom:10px">Coisas que acontecem no jogo e ainda não fazem nenhum som. Marque quais precisam de um.</p>
    <div class="group" id="mudos"></div>
  </section>

  <footer id="foot"></footer>
</div>

<script>
%MODULE_OLD%
</script>
<script>
%MODULE%
</script>
<script>
const DATA = %DATA%;
const CALLS = %CALLS%;
const $ = s => document.querySelector(s);
const el = (tag, attrs = {}, kids = []) => { const e = document.createElement(tag); for (const [k, v] of Object.entries(attrs)){ if (k === 'text') e.textContent = v; else if (k === 'class') e.className = v; else if (k.startsWith('on')) e.addEventListener(k.slice(2), v); else e.setAttribute(k, v); } for (const c of [].concat(kids)) if (c) e.append(c); return e; };
const num = v => (Math.abs(v) < .05 ? '0' : (v > 0 ? '+' : '−') + Math.abs(v).toFixed(1)).replace('.', ',');
const dbs = v => (v < 0 ? '−' : '') + Math.abs(v).toFixed(1).replace('.', ',');
const L = DATA.levels, LO = DATA.levelsOld, P = DATA.proposals, REF = DATA.ref, REFO = DATA.refOld, BEFORE = new Set(DATA.before);
const ESTADO = {refeito: 'Refeito', novo: 'Novo', volume: 'Volume ajustado'};
const TAGS = ['Alto demais', 'Baixo demais', 'Irritante', 'Gostei', 'Não combina', 'Refazer'];
const NEED = [['urgente', 'Sim, importante'], ['sim', 'Sim'], ['nao', 'Não precisa']];
const NEEDTXT = {urgente: 'Sim, importante', sim: 'Sim', nao: 'Não precisa'};
const SOUND = {}; for (const g of DATA.groups) for (const s of g.sounds) SOUND[s.id] = Object.assign({group: g}, s);
const nameOf = id => (SOUND[id] || {}).nome || id;

/* ---------- audio: two modules, SFX (agora) and SFX_OLD (antes, commit DATA.meta.before) ---------- */
let mood = 'silent', moodOld = 'silent', playingBtn = null, playTimer = 0, sceneTimers = [], musicRow = null;
SFX.moodFn(() => mood); SFX_OLD.moodFn(() => moodOld);
function audioOn(old){ SFX.init(); SFX.pause(false); if (old){ SFX_OLD.init(); SFX_OLD.pause(false); } }
function setMood(m){ mood = m; SFX.__now(m); }
function setMoodOld(m){ moodOld = m; if (SFX_OLD.__st() !== 'none') SFX_OLD.__now(m); }
const backMood = () => $('#backing').checked ? 'combat' : 'silent';
function stopAll(){ for (const t of sceneTimers) clearTimeout(t); sceneTimers = []; setMood(backMood()); setMoodOld('silent'); markPlaying(null); musicRow = null; }
function markPlaying(btn, secs){
  if (playingBtn) playingBtn.classList.remove('playing'); clearTimeout(playTimer); playingBtn = btn;
  if (btn){ btn.classList.add('playing'); if (secs) playTimer = setTimeout(() => { btn.classList.remove('playing'); if (playingBtn === btn) playingBtn = null; }, secs*1000); }
}
// ver: 'old' (antes), 'new' (agora) or 'pro' (agora with a proposed volume)
function playSound(s, ver, btn){
  const old = ver === 'old', M = old ? SFX_OLD : SFX; audioOn(old);
  if (s.mood){                                 // music track: toggles
    const key = s.id + ver;
    if (musicRow === key){ stopAll(); return; }
    for (const t of sceneTimers) clearTimeout(t); sceneTimers = [];
    setMood('silent'); setMoodOld('silent'); musicRow = key;
    const go = () => { if (old) setMoodOld(s.mood); else setMood(s.mood); };
    if (M.__st() === 'running') go(); else setTimeout(go, 150);
    markPlaying(btn); return;
  }
  if (musicRow){ musicRow = null; setMood(backMood()); setMoodOld('silent'); }
  const k = ver === 'pro' && P[s.id] ? Math.pow(10, P[s.id].db/20) : 1;
  const len = Math.max(.6, ((old ? LO : L)[s.id] || {}).len_s || 1);
  const go = () => { M.__clr(); try { M.__play(() => CALLS[s.id](M), k); } catch (e) { console.warn(e); } markPlaying(btn, len); };
  if (M.__st() === 'running') go(); else setTimeout(go, 150);   // first click: let the context start
}
const SCENE = [[.3,'v_goblin'],[.5,'sword'],[.8,'explode'],[.9,'kill_goblin'],[1.1,'gem'],[1.25,'gem'],[1.5,'bow'],[1.6,'v_orc'],[1.9,'kill_orc'],[2.0,'bow'],[2.1,'gem'],[2.4,'slam'],
  [2.6,'v_gargoyle2'],[2.9,'sword'],[3.2,'explode'],[3.3,'kill_hobgoblin'],[3.6,'bow'],[3.75,'kill_gargoyle'],[3.9,'elfArrow'],[4.6,'v_elf'],[4.3,'demon'],[4.9,'hurt'],[5.4,'gem'],[5.55,'gem'],
  [5.8,'v_hobgoblin2'],[6.3,'levelup'],[6.6,'v_succubus'],[7.0,'succubus'],[7.4,'v_demon'],[8.15,'hex'],[8.6,'v_skeleton'],[9.0,'bolt'],[9.6,'explode'],[9.7,'kill_demon'],[10.1,'bow'],
  [10.2,'v_wyvern'],[10.4,'storm'],[11.2,'enhance'],[11.5,'kill_wyvern'],[11.8,'heart']];
function playScene(old, btn){
  audioOn(old); stopAll(); const M = old ? SFX_OLD : SFX; M.__clr();
  setMood(old ? 'silent' : 'combat'); if (old) setMoodOld('combat');
  markPlaying(btn, 13.5);
  for (const [t, id] of SCENE){
    if (old && SOUND[id] && SOUND[id].estado === 'novo') continue;       // did not exist before
    sceneTimers.push(setTimeout(() => { try { M.__play(() => CALLS[id](M), 1); } catch (e) {} }, t*1000));
  }
  sceneTimers.push(setTimeout(() => { setMood(backMood()); setMoodOld('silent'); }, 13500));
}

/* ---------- ratings store (db capability): this round in DATA.store; earlier rounds (DATA.prev: [collection, round],
   newest first) are only read, never written ---------- */
const ST = {}, PREV = {}, rows = {}, Q = {};
for (const [name] of DATA.prev) PREV[name] = {};
let db = null;
const LS = 'aren-lab-r' + DATA.round + '-rascunho';
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
      try { await db.collection(DATA.store).doc(id).set(Object.assign({}, ST[id])); rows[id]?.saved('Salvo'); status('ok', 'Notas guardadas'); }
      catch (e){ rows[id]?.saved('Não foi possível salvar agora'); status('err', 'Erro ao salvar: ' + (e && e.code || 'desconhecido')); break; }
    }
    q.busy = false;
  })();
}
let saveTimers = {};
function saveSoon(id){ clearTimeout(saveTimers[id]); saveTimers[id] = setTimeout(() => save(id), 700); }
async function connect(){
  try { db = window.claude && window.claude.use ? await window.claude.use('db') : null; } catch { db = null; }
  if (!db){ status('off', 'Sem armazenamento aqui: as notas ficam só neste navegador'); return; }
  const timer = setTimeout(() => status('wait', 'O armazenamento está demorando a responder'), 10000);
  db.collection(DATA.store).onSnapshot(snap => {
    if (!snap.metadata.fromCache){ clearTimeout(timer); if ($('#status').dataset.s !== 'saving') status('ok', 'Notas guardadas'); }
    for (const d of snap.docs){
      const q = Q[d.id]; if (q && (q.busy || q.dirty)) continue;
      ST[d.id] = Object.assign({}, d.data()); rows[d.id]?.sync();
    }
    draft();
  }, e => { clearTimeout(timer); status('err', 'Armazenamento indisponível (' + (e && e.code || 'erro') + ')'); });
  for (const [name] of DATA.prev){ const T = PREV[name];
    try { db.collection(name).onSnapshot(snap => { for (const d of snap.docs) T[d.id] = Object.assign({}, d.data()); for (const id in rows) rows[id].prev?.(); }, () => {}); } catch {}
  }
}

/* ---------- UI pieces ---------- */
function stars(id){
  const box = el('div', {class: 'stars', role: 'group', 'aria-label': 'Nota de 1 a 5'});
  const btns = [1, 2, 3, 4, 5].map(n => el('button', {class: 'btn', type: 'button', 'aria-pressed': 'false', 'aria-label': 'Nota ' + n, text: String(n),
    onclick: () => { const st = ST[id] || (ST[id] = {}); st.nota = st.nota === n ? null : n; sync(); save(id); }}));
  box.append(...btns);
  const sync = () => btns.forEach((b, i) => b.setAttribute('aria-pressed', String((ST[id] || {}).nota === i + 1)));
  return {box, sync};
}
function tagChips(id){
  const box = el('div', {class: 'tags', role: 'group', 'aria-label': 'Marcadores'});
  const btns = TAGS.map(t => el('button', {class: 'btn alt', type: 'button', 'aria-pressed': 'false', text: t,
    onclick: () => { const st = ST[id] || (ST[id] = {}); const s = new Set(st.tags || []); s.has(t) ? s.delete(t) : s.add(t); st.tags = [...s]; sync(); save(id); }}));
  box.append(...btns);
  const sync = () => btns.forEach((b, i) => b.setAttribute('aria-pressed', String(((ST[id] || {}).tags || []).includes(TAGS[i]))));
  return {box, sync};
}
function choice(id, field, opts, label){
  const box = el('div', {class: 'pref', role: 'group', 'aria-label': label}, [el('span', {text: label})]);
  const btns = opts.map(([v, t]) => el('button', {class: 'btn', type: 'button', 'aria-pressed': 'false', text: t,
    onclick: () => { const st = ST[id] || (ST[id] = {}); st[field] = st[field] === v ? null : v; sync(); save(id); }}));
  box.append(...btns);
  const sync = () => btns.forEach((b, i) => b.setAttribute('aria-pressed', String((ST[id] || {})[field] === opts[i][0])));
  return {box, sync};
}
function comment(id, ph){
  const ta = el('textarea', {rows: '1', placeholder: ph, id: 'c-' + id, 'aria-label': 'Comentário'});
  ta.addEventListener('input', () => { (ST[id] || (ST[id] = {})).comentario = ta.value; saveSoon(id); });
  const sync = () => { if (document.activeElement !== ta) ta.value = (ST[id] || {}).comentario || ''; };
  return {box: ta, sync};
}
// what he said before (read-only): the newest earlier round that has a note for this sound (round 1 also maps its
// "silent moment" rows to the sounds that answer them)
const PREFTXT = {antes: 'preferiu o Antes', agora: 'preferiu o Agora', igual: 'tanto faz', proposta: 'preferiu a proposta', atual: 'preferiu o atual'};
const hasNote = r => r && (r.nota || (r.tags || []).length || r.comentario || r.pref || r.prefVol || r.precisa);
function prevText(id){
  let r = null, label = '';
  for (const [name, n] of DATA.prev){
    const src = n === 1 ? DATA.r1map[id] || id : id; r = PREV[name][src];
    label = n === 1 && DATA.r1map[id] ? 'Na rodada 1 (momento sem som): ' : `Sua nota na rodada ${n}: `;
    if (hasNote(r)) break;
  }
  if (!hasNote(r)) return null;
  const parts = [];
  if (r.precisa) parts.push('precisa de som: ' + (NEEDTXT[r.precisa] || r.precisa));
  if (r.nota) parts.push('nota ' + r.nota);
  if ((r.tags || []).length) parts.push(r.tags.join(', '));
  if (r.pref) parts.push(PREFTXT[r.pref] || r.pref);
  if (r.prefVol) parts.push('volume: ' + (r.prefVol === 'proposta' ? 'a proposta' : r.prefVol === 'atual' ? 'o atual' : 'tanto faz'));
  const p = el('div', {class: 'prev'}, [el('b', {text: label}), parts.join(' · ')]);
  if (r.comentario) p.append(el('span', {text: (parts.length ? ' · ' : '') + '“' + r.comentario + '”'}));
  return p;
}
function band(id){
  const rel = L[id].rms150_db - REF, lo = id.startsWith('v_') ? -12 : -10;   // presence voices are meant to be quiet (-12..-6)
  return rel > 6 ? 'hi' : rel < lo ? 'lo' : 'ok';
}
function meter(id){
  const v = L[id]; if (!v) return el('div');
  const lo = -50, hi = -8, x = Math.max(0, Math.min(1, (v.rms150_db - lo)/(hi - lo)));
  const rel = v.rms150_db - REF, music = v.group === 'musica';
  const k = music ? '' : band(id);
  const word = music ? 'música' : (k === 'hi' ? 'muito alto' : k === 'lo' ? 'baixo' : 'na faixa');
  const m = el('div', {class: 'meter', 'data-k': k, role: 'img', 'aria-label': `Volume ${dbs(v.rms150_db)} dB; a marca dourada é a explosão de fogo`});
  m.append(el('i', {style: `width:${(x*100).toFixed(1)}%`}), el('u', {style: `left:calc(${(((REF - lo)/(hi - lo))*100).toFixed(1)}% - 1px)`}));
  const box = el('div', {class: 'lvl'}, [
    el('div', {class: 'small mono', text: `pico ${dbs(v.peak_db)} · volume ${dbs(v.rms150_db)} dBFS · ${v.nodes} nós`}), m,
    music ? el('span', {class: 'chip ok', text: `média ${dbs(v.rms_db)} dBFS`}) : el('span', {class: 'chip ' + k, text: `${num(rel)} dB vs explosão · ${word}`})]);
  const o = LO[id];
  if (o && BEFORE.has(id)) box.append(el('p', {class: 'was', text: music ? `Antes: média ${dbs(o.rms_db)} dBFS (${num(v.rms_db - o.rms_db)} dB agora)`
    : `Antes: ${num(o.rms150_db - REFO)} dB vs a explosão antiga · ${dbs(o.len_s)} s`.replace(' · −', ' · ')}));
  if (P[id]) box.append(el('p', {class: 'why', text: `Proposta: ${num(P[id].db)} dB. ${P[id].why}`}));
  return box;
}

function soundRow(g, s){
  const id = s.id, isMusic = !!s.mood, hasOld = BEFORE.has(id), hasPro = !!P[id];
  const r = stars(id), t = tagChips(id), c = comment(id, 'O que mudar? (opcional)');
  const pref = hasOld ? choice(id, 'pref', [['antes', 'Antes'], ['agora', 'Agora'], ['igual', 'Tanto faz']], 'Prefiro:') : null;
  const prefVol = hasPro ? choice(id, 'prefVol', [['atual', 'Volume atual'], ['proposta', 'Proposta'], ['igual', 'Tanto faz']], 'Volume:') : null;
  const plays = el('div', {class: 'plays'});
  if (hasOld) plays.append(el('button', {class: 'btn', type: 'button', onclick: e => playSound(s, 'old', e.currentTarget)}, [el('span', {class: 'tri'}), 'Antes']));
  plays.append(el('button', {class: 'btn alt', type: 'button', onclick: e => playSound(s, 'new', e.currentTarget)}, [el('span', {class: 'tri'}), hasOld ? 'Agora' : (isMusic ? 'Tocar' : 'Agora')]));
  if (hasPro) plays.append(el('button', {class: 'btn alt', type: 'button', onclick: e => playSound(s, 'pro', e.currentTarget)}, [el('span', {class: 'tri'}), 'Proposta ' + num(P[id].db) + ' dB']));
  const saved = el('div', {class: 'saved'}), prevBox = el('div');
  const h = el('h3', {text: s.nome}); if (s.estado) h.append(el('span', {class: 'badge ' + s.estado, text: ESTADO[s.estado] || s.estado}));
  const row = el('article', {class: 'snd', id: 's-' + id, 'data-mudou': s.estado ? '1' : '0'}, [
    el('div', {class: 'who'}, [h, el('p', {text: s.quando}), plays]),
    meter(id),
    el('div', {class: 'rate'}, [r.box, t.box, pref && pref.box, prefVol && prefVol.box, c.box, prevBox, saved])]);
  rows[id] = {sync: () => { r.sync(); t.sync(); c.sync(); pref && pref.sync(); prefVol && prefVol.sync(); row.classList.toggle('has-note', !!(ST[id] && (ST[id].nota || (ST[id].tags || []).length || ST[id].comentario))); },
              saved: m => { saved.textContent = m; }, prev: () => { prevBox.replaceChildren(...[prevText(id)].filter(Boolean)); }};
  rows[id].sync();
  return row;
}
function mudoRow(m){
  const id = m.id, ch = choice(id, 'precisa', NEED, 'Precisa de som?'), c = comment(id, 'Que tipo de som? (opcional)'), saved = el('div', {class: 'saved'});
  const row = el('article', {class: 'snd mudo'}, [el('div', {class: 'who'}, [el('h3', {text: m.nome}), el('p', {text: m.quando})]),
    el('div', {class: 'rate'}, [ch.box, c.box, saved])]);
  rows[id] = {sync: () => { ch.sync(); c.sync(); }, saved: t => { saved.textContent = t; }};
  rows[id].sync();
  return row;
}

/* ---------- findings: what changed in round 5 (numbers from the measurements) ---------- */
function findings(){
  const rel = id => L[id].rms150_db - REF, relO = id => LO[id].rms150_db - REFO, all = Object.values(SOUND).filter(s => !s.mood);
  const cnt = k => Object.values(SOUND).filter(s => s.estado === k).length;
  const loud = all.filter(s => P[s.id] && P[s.id].db < 0).sort((a, b) => rel(b.id) - rel(a.id));   // same rule as the Proposta buttons
  const NEW = ['v_orc', 'v_elf', 'v_skeleton'].filter(id => L[id]), vr = NEW.map(rel), vn = Math.max(...NEW.map(id => L[id].nodes));
  const was = (id, t) => LO[id] ? `${t} (${num(relO(id))} → <b>${num(rel(id))} dB</b>)` : `${t} (<b>${num(rel(id))} dB</b>)`;
  const F = [
    ['Rodada 5', `${cnt('refeito')} refeitos, ${cnt('volume')} com volume novo, ${cnt('novo')} sons novos`, `Mudei só o que você pediu na rodada 4; o que você aprovou (a cena, a morte da serpe A, a risada da súcubo, o rosnado do hobgoblin, as asas e o suspiro da súcubo, as asas da serpe) ficou igual. A opção B da morte da serpe saiu (você escolheu a A). Use <b>Só o que mudou</b> no topo para ver só os sons desta rodada.`],
    ['Monstros · último lote', 'Orc, elfo e esqueleto por perto', NEW.length ? `Orc: bufada pesada pelo nariz com um grunhido gutural grave, mais grave e com mais ar que o rosnado do hobgoblin. Elfo: grito de batalha curto e agudo ("hah!" ou "hy-ah!"), raro porque há muitos elfos, e nunca em cima da flecha (espera ela terminar). Esqueleto: ossinhos chacoalhando, secos e agudos, e a mandíbula batendo "clac-clac". Ficam baixos, entre <b>${num(Math.min(...vr))}</b> e <b>${num(Math.max(...vr))} dB</b> em relação à explosão, com até ${vn} nós de áudio. Agora <b>todos os monstros</b> têm som de presença.` : ''],
    ['Refeitos', 'O que você marcou', `${was('v_wyvern', 'Serpe por perto')}: o grasnido "kraa-ak" saiu; são só as asas que você aprovou, de 2 a 4 batidas, ora mais rápidas, ora mais lentas (toque várias vezes).`],
    ['Vida baixa', 'Feita para aparecer em alto-falante pequeno', `${was('lowHp', 'Vida baixa')}. Pela terceira vez "baixo demais": subir o volume não resolvia porque a batida era quase toda grave (abaixo de 200 Hz), que caixinha de notebook e de celular mal toca e a música cobre. Agora cada batida tem também um toque abafado (como um nó de dedo na madeira) e um tom uma oitava acima; a parte acima de 500 Hz ficou cerca de 16 dB mais forte. Continua uma batida suave. Teste no celular, se puder.`],
    ['Limite', loud.length ? 'Sons que ainda passam do limite' : 'Nenhum som acima do limite', loud.length ? `${loud.map(s => `<b>${s.nome}</b> (${num(rel(s.id))} dB)`).join(', ')}. Não mexi neles porque você não pediu; o botão <b>Proposta</b> mostra como ficaria mais baixo.` : 'Todos os efeitos estão no máximo 6 dB acima da explosão (8 para chegadas e fúria de chefe).'],
  ];
  $('#finds').append(...F.map(([tag, h, p]) => { const d = el('div', {class: 'find'}, [el('span', {class: 'tag', text: tag}), el('h3', {text: h})]); const pp = el('p'); pp.innerHTML = p; d.append(pp); return d; }));
}

/* ---------- build page ---------- */
$('#meta').textContent = `Agora: código de som do jogo no commit ${DATA.meta.commit}. Antes: commit ${DATA.meta.before} (a versão da rodada ${DATA.round - 1}). Gerado em ${DATA.meta.date}. Use fones ou caixa de som num volume confortável.`;
findings();
for (const g of DATA.groups){
  const sec = el('section', {}, [el('h2', {text: g.nome})]);
  const box = el('div', {class: 'group'});
  for (const s of g.sounds) box.append(soundRow(g, s));
  sec.append(box); $('#groups').append(sec);
}
if (DATA.mudos.length){ $('#mudosSec').hidden = false; for (const m of DATA.mudos) $('#mudos').append(mudoRow(m)); }
{
  const id = 'cena', ch = choice(id, 'pref', [['antes', 'Antes'], ['agora', 'Agora'], ['igual', 'Tanto faz']], 'Qual ficou melhor?');
  $('#scenePref').replaceWith(ch.box);
  const ta = $('#sceneTxt');
  ta.addEventListener('input', () => { (ST[id] || (ST[id] = {})).comentario = ta.value; saveSoon(id); });
  rows[id] = {sync: () => { ch.sync(); if (document.activeElement !== ta) ta.value = (ST[id] || {}).comentario || ''; },
              saved: t => { $('#sceneSaved').textContent = t; },
              prev: () => { let r = null, n = 0; for (const [name, k] of DATA.prev){ r = PREV[name].cena; n = k; if (r && (r.pref || r.comentario)) break; } const box = $('#scenePrev'); if (!r || !(r.pref || r.comentario)) { box.hidden = true; return; }
                const pt = r.pref === 'proposta' ? 'o mix proposto' : r.pref === 'atual' ? 'o mix atual' : r.pref === 'antes' ? 'o Antes' : r.pref === 'agora' ? 'o Agora' : 'tanto faz';
                box.hidden = false; box.replaceChildren(el('b', {text: `Na rodada ${n}: `}), (r.pref ? (r.pref === 'igual' ? 'tanto faz' : 'preferiu ' + pt) : '') + (r.comentario ? (r.pref ? ' · ' : '') + '“' + r.comentario + '”' : '')); }};
}
rows.cena.sync();
for (const b of document.querySelectorAll('[data-f]')) b.addEventListener('click', () => {
  const only = b.dataset.f === 'mudou';
  for (const x of document.querySelectorAll('[data-f]')) x.setAttribute('aria-pressed', String(x === b));
  for (const r of document.querySelectorAll('article.snd[data-mudou]')) r.hidden = only && r.dataset.mudou !== '1';
  for (const sec of document.querySelectorAll('#groups section')) sec.hidden = ![...sec.querySelectorAll('article.snd')].some(r => !r.hidden);
});
$('#sceneOld').addEventListener('click', e => playScene(true, e.currentTarget));
$('#sceneNew').addEventListener('click', e => playScene(false, e.currentTarget));
$('#stopAll').addEventListener('click', () => { audioOn(false); stopAll(); });
$('#backing').addEventListener('change', e => { audioOn(false); if (!musicRow) setMood(backMood()); });
$('#foot').innerHTML = `<p>Volumes medidos com <span class="mono">tools/sfx_levels.py</span>: cada som tocado sozinho pelo mixer do jogo. "Volume" é o trecho de 150 ms mais alto; a marca dourada na barra é a explosão da Magia de Fogo. "Nós" é quantas peças de áudio o som cria (custo para o celular).</p><p>O botão <b>Proposta</b> só aparece onde ainda vale a regra da rodada 1 e você ainda não respondeu: efeitos mais de 6 dB acima da explosão descem para 6 (8 para a chegada, a fúria e a morte do dragão); avisos de ataque mais de 8 dB abaixo sobem para −8. Nada disso muda o jogo até você aprovar.</p><p>Eu não ouço os sons: desenhei cada um pela síntese e conferi com medições. Quem decide se ficou bom é você.</p>`;
connect();
</script>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True, help='arquivo HTML de saída')
    ap.add_argument('--levels', help='JSON de tools/sfx_levels.py --json (senão mede agora)')
    ap.add_argument('--levels-old', help='JSON da medição do commit "Antes" (senão mede agora; só os sons com estado)')
    ap.add_argument('--before', default=BEFORE_REV, help=f'commit do "Antes" (padrão {BEFORE_REV})')
    ap.add_argument('--store', default=STORE, help=f'coleção onde as notas desta rodada são gravadas (padrão {STORE})')
    ap.add_argument('--prev-store', default=PREV_STORE, help=f'coleção da rodada anterior, só leitura (padrão {PREV_STORE})')
    a = ap.parse_args()
    d = build(a.out, a.levels, a.levels_old, a.before, a.store, a.prev_store)
    print(f"gravado {a.out}: {sum(len(g['sounds']) for g in d['groups'])} sons, {len(d['mudos'])} momentos sem som, "
          f"{len(d['proposals'])} propostas de volume")
    for k, v in d['proposals'].items():
        print(f"  {k:12s} {v['db']:+5.1f} dB")


if __name__ == '__main__':
    main()
