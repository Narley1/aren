#!/usr/bin/env python3
"""Gera o Laboratório de Som: uma página para ouvir, comparar e avaliar cada som do jogo.

A página usa o MESMO módulo SFX de src/bosque-do-enxame.html (copiado no build, com ganchos de teste
só na cópia), o catálogo tools/sound_catalog.json e os volumes medidos por tools/sfx_levels.py.
As notas e comentários vão para o armazenamento `db` do artifact (coleção `avaliacoes`), onde o
Claude lê depois. A saída é um fragmento HTML (sem doctype): o publicador do artifact põe o cabeçalho.

    python3 tools/build_sound_lab.py --out /caminho/laboratorio-som.html
    python3 tools/build_sound_lab.py --out lab.html --levels /tmp/levels.json   # reaproveita medição
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
MUSIC_DB = -6.0         # default music level in the proposed mix (the page has a slider)


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
        elif k in WARN_IDS and rel < WARN_FLOOR_DB:
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


def build(out_path, levels_path=None):
    cat = sfx_levels.load_catalog()
    if levels_path:
        with open(levels_path, encoding='utf-8') as f:
            levels = json.load(f)
    else:
        levels = asyncio.run(sfx_levels.measure())
    missing = [s['id'] for _, s in sfx_levels.items(cat) if s['id'] not in levels]
    if missing:
        raise SystemExit('erro: medição sem estes ids (rode sfx_levels.py de novo): ' + ', '.join(missing))
    mod = sfx_levels.extract_sfx(open(sfx_levels.SRC, encoding='utf-8').read())
    data = {
        'groups': cat['groups'], 'mudos': cat['mudos'], 'levels': levels, 'proposals': proposals(levels),
        'ref': levels['explode']['rms150_db'], 'musicDb': MUSIC_DB,
        'meta': {'commit': git('rev-parse', '--short', 'HEAD'), 'date': datetime.date.today().strftime('%d/%m/%Y')},
    }
    js_data = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    html = (TEMPLATE.replace('%DATA%', js_data).replace('%CALLS%', calls_js(cat))
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
@media (max-width:760px){
  .snd,.mudo{grid-template-columns:1fr}
  .status{margin-left:0}
  h1{font-size:25px}
}
@media (prefers-reduced-motion:no-preference){ .btn.playing{animation:blink .5s steps(2) infinite} @keyframes blink{50%{filter:brightness(1.25)}} }
</style>

<div class="wrap">
  <h1>Laboratório de Som do Aren</h1>
  <p class="lead">Todos os sons e músicas do jogo, tocados pelo mesmo código do jogo. Ouça cada um, dê uma nota e escreva o que mudar. Suas respostas ficam guardadas e eu leio depois para fazer os ajustes.</p>
  <p class="small" id="meta"></p>
</div>

<div class="bar" role="region" aria-label="Controles">
  <div class="bar-in">
    <button class="btn" id="stopAll" type="button"><span class="sq"></span>Parar tudo</button>
    <label><input type="checkbox" id="backing"> Ouvir os efeitos com a música de combate</label>
    <label>Música no mix proposto <input type="range" id="musDb" min="-15" max="0" step="1"> <span class="mono" id="musDbV"></span></label>
    <span class="status" id="status" data-s="wait"><span class="dot"></span><span id="statusT">Conectando ao armazenamento…</span></span>
  </div>
</div>

<div class="wrap">
  <h2>O que a auditoria encontrou</h2>
  <div class="finds" id="finds"></div>

  <h2>Cena de teste</h2>
  <div class="scene">
    <p>Doze segundos de luta: música de combate, fogo, arco, martelo, demônio, súcubo, relâmpago e subir de nível. Toque com o mix atual e com o proposto e diga qual ficou melhor.</p>
    <div class="row-btns">
      <button class="btn" type="button" id="sceneNow"><span class="tri"></span>Mix atual</button>
      <button class="btn alt" type="button" id="scenePro"><span class="tri"></span>Mix proposto</button>
    </div>
    <div class="pref" id="scenePref"></div>
    <textarea id="sceneTxt" rows="2" placeholder="O que você achou da cena? (opcional)"></textarea>
    <div class="saved" id="sceneSaved"></div>
  </div>

  <div id="groups"></div>

  <h2>Momentos sem som</h2>
  <p class="small" style="margin-bottom:10px">Coisas que acontecem no jogo e hoje não fazem nenhum som. Marque quais precisam de um.</p>
  <div class="group" id="mudos"></div>

  <footer id="foot"></footer>
</div>

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
const L = DATA.levels, P = DATA.proposals, REF = DATA.ref;
const TAGS = ['Alto demais', 'Baixo demais', 'Irritante', 'Gostei', 'Não combina', 'Refazer'];
const NEED = [['urgente', 'Sim, importante'], ['sim', 'Sim'], ['nao', 'Não precisa']];

/* ---------- audio ---------- */
let mood = 'silent', musK = Math.pow(10, DATA.musicDb/20), musDbNow = DATA.musicDb, playingBtn = null, playTimer = 0, sceneTimers = [];
SFX.moodFn(() => mood);
function audioOn(){ SFX.init(); SFX.pause(false); }
function setMood(m){ mood = m; SFX.__now(m); }
function stopAll(){ for (const t of sceneTimers) clearTimeout(t); sceneTimers = []; setMood($('#backing').checked ? 'combat' : 'silent'); SFX.__mus(1); markPlaying(null); musicRow = null; }
function markPlaying(btn, secs){
  if (playingBtn) playingBtn.classList.remove('playing'); clearTimeout(playTimer); playingBtn = btn;
  if (btn){ btn.classList.add('playing'); if (secs) playTimer = setTimeout(() => { btn.classList.remove('playing'); if (playingBtn === btn) playingBtn = null; }, secs*1000); }
}
let musicRow = null;
function playSound(s, proposed, btn){
  audioOn();
  if (s.mood){                      // music track: toggles
    const key = s.id + (proposed ? '+' : '');
    if (musicRow === key){ stopAll(); return; }
    musicRow = key; setMood(s.mood); SFX.__mus(proposed ? musK : 1); markPlaying(btn); return;
  }
  if (musicRow){ musicRow = null; setMood($('#backing').checked ? 'combat' : 'silent'); }
  SFX.__mus(proposed ? musK : 1);
  const k = proposed && P[s.id] ? Math.pow(10, P[s.id].db/20) : 1;
  const go = () => { SFX.__clr(); SFX.__play(() => CALLS[s.id](SFX), k); markPlaying(btn, Math.max(.6, (L[s.id] || {}).len_s || 1)); };
  if (SFX.__st() === 'running') go(); else setTimeout(go, 120);   // first click: let the context start
}
const SCENE = [[.8,'explode'],[1.5,'bow'],[1.9,'bow'],[2.4,'slam'],[3.2,'explode'],[3.6,'bow'],[4.3,'demon'],[6.0,'levelup'],[7.1,'hex'],[7.6,'succubus'],[9.0,'bolt'],[9.6,'explode'],[10.1,'bow'],[11.0,'enhance']];
function playScene(proposed, btn){
  audioOn(); stopAll(); musicRow = null; SFX.__clr();
  setMood('combat'); SFX.__mus(proposed ? musK : 1); markPlaying(btn, 13);
  for (const [t, id] of SCENE){
    const k = proposed && P[id] ? Math.pow(10, P[id].db/20) : 1;
    sceneTimers.push(setTimeout(() => SFX.__play(() => CALLS[id](SFX), k), t*1000));
  }
  sceneTimers.push(setTimeout(() => { setMood($('#backing').checked ? 'combat' : 'silent'); SFX.__mus(1); }, 13000));
}

/* ---------- ratings store (db capability) ---------- */
const ST = {}, rows = {}, Q = {};
let db = null;
const LS = 'aren-lab-rascunho';
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
      try { await db.collection('avaliacoes').doc(id).set(Object.assign({}, ST[id])); rows[id]?.saved('Salvo'); status('ok', 'Notas guardadas'); }
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
  db.collection('avaliacoes').onSnapshot(snap => {
    if (!snap.metadata.fromCache){ clearTimeout(timer); if ($('#status').dataset.s !== 'saving') status('ok', 'Notas guardadas'); }
    for (const d of snap.docs){
      const q = Q[d.id]; if (q && (q.busy || q.dirty)) continue;
      ST[d.id] = Object.assign({}, d.data()); rows[d.id]?.sync();
    }
    draft();
  }, e => { clearTimeout(timer); status('err', 'Armazenamento indisponível (' + (e && e.code || 'erro') + ')'); });
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
function meter(id){
  const v = L[id]; if (!v) return el('div');
  const lo = -50, hi = -8, x = Math.max(0, Math.min(1, (v.rms150_db - lo)/(hi - lo)));
  const rel = v.rms150_db - REF, music = v.group === 'musica';
  const k = music ? '' : (rel > 6 ? 'hi' : rel < -8 ? 'lo' : 'ok');
  const word = music ? 'música' : (k === 'hi' ? 'muito alto' : k === 'lo' ? 'baixo' : 'na faixa');
  const m = el('div', {class: 'meter', 'data-k': k, role: 'img', 'aria-label': `Volume ${dbs(v.rms150_db)} dB; a marca dourada é a explosão de fogo`});
  m.append(el('i', {style: `width:${(x*100).toFixed(1)}%`}), el('u', {style: `left:calc(${(((REF - lo)/(hi - lo))*100).toFixed(1)}% - 1px)`}));
  const box = el('div', {class: 'lvl'}, [
    el('div', {class: 'small mono', text: `pico ${dbs(v.peak_db)} · volume ${dbs(v.rms150_db)} dBFS`}), m,
    music ? el('span', {class: 'chip ok', text: `média ${dbs(v.rms_db)} dBFS`}) : el('span', {class: 'chip ' + k, text: `${num(rel)} dB vs explosão · ${word}`})]);
  if (P[id]) box.append(el('p', {class: 'why', text: `Proposta: ${num(P[id].db)} dB. ${P[id].why}`}));
  if (music) box.append(el('p', {class: 'why', text: 'Proposta: música mais baixa no mix (ajuste no controle acima).'}));
  return box;
}

function soundRow(g, s){
  const id = s.id, bus = !!g.music;
  const r = stars(id), t = tagChips(id), c = comment(id, 'O que mudar? (opcional)');
  const hasPro = bus || !!P[id];
  const pref = hasPro ? choice(id, 'pref', [['atual', 'Atual'], ['proposta', 'Proposta'], ['igual', 'Tanto faz']], 'Prefiro:') : null;
  const bNow = el('button', {class: 'btn', type: 'button', onclick: e => playSound(s, false, e.currentTarget)}, [el('span', {class: 'tri'}), bus ? 'Tocar' : 'Atual']);
  const plays = el('div', {class: 'plays'}, [bNow]);
  if (hasPro) plays.append(el('button', {class: 'btn alt', type: 'button', onclick: e => playSound(s, true, e.currentTarget)},
    [el('span', {class: 'tri'}), bus ? 'No mix proposto' : 'Proposta ' + num(P[id].db) + ' dB']));
  const saved = el('div', {class: 'saved'});
  const row = el('article', {class: 'snd', id: 's-' + id}, [
    el('div', {class: 'who'}, [el('h3', {text: s.nome}), el('p', {text: s.quando}), plays]),
    meter(id),
    el('div', {class: 'rate'}, [r.box, t.box, pref && pref.box, c.box, saved])]);
  rows[id] = {sync: () => { r.sync(); t.sync(); c.sync(); pref && pref.sync(); row.classList.toggle('has-note', !!(ST[id] && (ST[id].nota || (ST[id].tags || []).length || ST[id].comentario))); },
              saved: m => { saved.textContent = m; }};
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

/* ---------- findings (numbers come from the measurement) ---------- */
function findings(){
  const g = id => L[id] ? L[id].rms150_db - REF : 0;
  const musAvg = ['m_calm', 'm_combat', 'm_bossM', 'm_boss'].map(k => L[k].rms_db);
  const loud = Object.keys(L).filter(k => L[k].group !== 'musica' && g(k) > 6).sort((a, b) => g(b) - g(a));
  const name = id => { for (const gr of DATA.groups) for (const s of gr.sounds) if (s.id === id) return s.nome; return id; };
  const F = [
    ['Mixagem', 'A música cobre os efeitos', `A música toca com volume médio entre <b>${dbs(Math.min(...musAvg))}</b> e <b>${dbs(Math.max(...musAvg))} dBFS</b>. A explosão de fogo, que é a referência dos efeitos, chega a ${dbs(L.explode.rms150_db)} no ponto mais alto. O arco, que toca o tempo todo, fica em <b>${dbs(L.bow.rms150_db)}</b>.`],
    ['Volume', 'Sons antigos muito mais altos que os novos', `${loud.length} efeitos passam de 6 dB acima da explosão. Os piores: ${loud.slice(0, 4).map(k => `<b>${name(k)}</b> (${num(g(k))})`).join(', ')}. A morte do dragão chega a pico de ${dbs(L.dragonDeath.peak_db)} dBFS, perto do máximo. A risada do demônio é o som alto que mais se repete.`],
    ['Silêncio', `${DATA.mudos.length} momentos sem nenhum som`, 'Aren levar dano, inimigo morrer, pegar joia ou coração, golpe da Espada, Shuriken, flecha dos elfos, botões e pausa. O jogo depende só da música e de poucos efeitos para dar retorno.'],
    ['Acessibilidade', 'Todo aviso sonoro tem sinal na tela', `Os ataques dos chefes e do dragão têm marcação visual, então ninguém depende do som para desviar. Alguns avisos são baixos demais para ajudar quem ouve: escudo raspando ${num(g('scrape'))} dB, salto ${num(g('jump'))} dB.`],
    ['Variação', 'Sons repetidos sempre iguais', 'O arco e as explosões tocam sempre na mesma altura. Uma variação pequena e aleatória a cada disparo deixa o som menos cansativo.'],
    ['Controles', 'Só liga e desliga', 'Música e Efeitos só ligam ou desligam, sem volume separado. Com a Música desligada, a vitória e a derrota ficam mudas.'],
  ];
  $('#finds').append(...F.map(([tag, h, p]) => { const d = el('div', {class: 'find'}, [el('span', {class: 'tag', text: tag}), el('h3', {text: h})]); const pp = el('p'); pp.innerHTML = p; d.append(pp); return d; }));
}

/* ---------- build page ---------- */
$('#meta').textContent = `Código de som copiado do jogo no commit ${DATA.meta.commit} (${DATA.meta.date}). Use fones ou caixa de som num volume confortável; a primeira vez que você tocar algo o navegador libera o áudio.`;
findings();
for (const g of DATA.groups){
  const sec = el('section', {}, [el('h2', {text: g.nome})]);
  const box = el('div', {class: 'group'});
  for (const s of g.sounds) box.append(soundRow(g, s));
  sec.append(box); $('#groups').append(sec);
}
for (const m of DATA.mudos) $('#mudos').append(mudoRow(m));
// scene preference + comment
{
  const id = 'cena', ch = choice(id, 'pref', [['atual', 'Atual'], ['proposta', 'Proposta'], ['igual', 'Tanto faz']], 'Qual ficou melhor?');
  $('#scenePref').replaceWith(ch.box);
  const ta = $('#sceneTxt');
  ta.addEventListener('input', () => { (ST[id] || (ST[id] = {})).comentario = ta.value; saveSoon(id); });
  rows[id] = {sync: () => { ch.sync(); if (document.activeElement !== ta) ta.value = (ST[id] || {}).comentario || ''; const mv = (ST[id] || {}).musicaDb; if (typeof mv === 'number' && document.activeElement !== $('#musDb')) setMusDb(mv, false); },
              saved: t => { $('#sceneSaved').textContent = t; }};
}
function setMusDb(v, store){
  musDbNow = v; musK = Math.pow(10, v/20); $('#musDb').value = String(v); $('#musDbV').textContent = (v === 0 ? '0' : '−' + Math.abs(v)) + ' dB';
  if (store){ (ST.cena || (ST.cena = {})).musicaDb = v; saveSoon('cena'); }
}
setMusDb(DATA.musicDb, false);
rows.cena.sync();
$('#musDb').addEventListener('input', e => { setMusDb(+e.target.value, true); if (musicRow && musicRow.endsWith('+')) SFX.__mus(musK); });
$('#sceneNow').addEventListener('click', e => playScene(false, e.currentTarget));
$('#scenePro').addEventListener('click', e => playScene(true, e.currentTarget));
$('#stopAll').addEventListener('click', () => { audioOn(); stopAll(); });
$('#backing').addEventListener('change', e => { audioOn(); if (!musicRow){ setMood(e.target.checked ? 'combat' : 'silent'); SFX.__mus(1); } });
$('#foot').innerHTML = `<p>Volumes medidos com <span class="mono">tools/sfx_levels.py</span>: cada som tocado sozinho pelo mixer do jogo. "Volume" é o trecho de 150 ms mais alto; a marca dourada na barra é a explosão da Magia de Fogo.</p><p>A proposta segue três regras: efeitos mais de 6 dB acima da explosão descem para 6 (8 para a chegada, a fúria e a morte do dragão); avisos de ataque e o arco que ficam mais de 8 dB abaixo sobem para −8; a música desce ${Math.abs(DATA.musicDb)} dB. Nada disso muda o jogo até você aprovar.</p>`;
connect();
</script>
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--out', required=True, help='arquivo HTML de saída')
    ap.add_argument('--levels', help='JSON de tools/sfx_levels.py --json (senão mede agora)')
    a = ap.parse_args()
    d = build(a.out, a.levels)
    print(f"gravado {a.out}: {sum(len(g['sounds']) for g in d['groups'])} sons, {len(d['mudos'])} momentos sem som, "
          f"{len(d['proposals'])} propostas de volume")
    for k, v in d['proposals'].items():
        print(f"  {k:12s} {v['db']:+5.1f} dB")


if __name__ == '__main__':
    main()
