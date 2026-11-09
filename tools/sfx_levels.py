#!/usr/bin/env python3
"""Mede o volume de cada som do jogo passando pelo mixer real (master + compressor).

Extrai o módulo `SFX` de src/bosque-do-enxame.html, toca cada item de tools/sound_catalog.json
num OfflineAudioContext (Chromium headless via Playwright) e imprime pico, RMS e duração.
Nada no jogo é alterado: os ganchos de teste (__sched/__now) só existem na cópia em memória.

    python3 tools/sfx_levels.py                      # tabela
    python3 tools/sfx_levels.py --json /tmp/l.json   # também grava JSON (usado pelo laboratório)
    python3 tools/sfx_levels.py --only bow,explode   # só alguns ids
    python3 tools/sfx_levels.py --rev 01c5ba5        # mede uma versão antiga do jogo (git)

Leitura dos números (dBFS, 0 = máximo digital):
  pico      maior amostra; acima de -6 o som está perto de estourar
  rms150    RMS da janela de 150 ms mais alta: o "quão alto parece" de um efeito curto
  rms       RMS médio do trecho audível: usado para comparar as músicas
  nós       quantos nós de áudio o som cria (custo de CPU por disparo)
Referência dos efeitos: a explosão da Magia de Fogo (id explode).
"""
import argparse, asyncio, json, math, os, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src', 'bosque-do-enxame.html')
CATALOG = os.path.join(ROOT, 'tools', 'sound_catalog.json')

# test hooks injected into the in-memory copy of the SFX module only
HOOKS = r"""
  // --- test hooks (tools/sfx_levels.py, tools/build_sound_lab.py); not part of the game build ---
  function __sched(m, secs){ setMood(m, .05); M.step = 0; M.bar = 0; M.next = .05;
    while (M.next < secs){ if (M.song && musicOn) playStep(M.next); const bpm = M.song ? M.song.bpm : 90; M.next += 60/bpm/4; M.step = (M.step + 1) % 16; if (M.step === 0) M.bar++; } }
  function __now(m){ M.fn = () => m; if (!ac) return; const t = ac.currentTime + .06; M.step = 0; M.bar = 0; M.next = t; setMood(m, t); }
  let __kv = 1;   // gain applied by route() while __play runs one sound (A/B of a proposed level)
  function __play(fn, k){ __kv = k || 1; try { fn(); } finally { __kv = 1; } }
  function __mus(k){ if (musDry){ const v = musicOn ? (typeof MUS === 'number' ? MUS : .34)*k : 0; musDry.gain.value = v; musWet.gain.value = v; } }
  function __st(){ return ac ? ac.state : 'none'; }
  function __clr(){ for (const k in last) delete last[k]; }
"""
ROUTE_OLD = 'const route = (node, wet, dry = sfxDry, wetBus = sfxWet) => { node.connect(dry);'
ROUTE_NEW = ('const route = (node, wet, dry = sfxDry, wetBus = sfxWet) => { '
             'if (__kv !== 1){ const kk = G_(__kv); node.connect(kk); node = kk; } node.connect(dry);')


def extract_sfx(src_text):
    """Return the SFX module source with the test hooks added (asserts every anchor is found once)."""
    a = src_text.index('const SFX = (() => {')
    b = src_text.index('})();', a) + len('})();')
    mod = src_text[a:b]
    anchor = '  function moodFn(fn){ M.fn = fn; }'
    ret = '  return {init,'
    for k in (anchor, ret, ROUTE_OLD):
        if mod.count(k) != 1:
            raise SystemExit(f'erro: o módulo SFX mudou de forma (âncora não encontrada uma vez): {k[:40]}')
    mod = (mod.replace(anchor, anchor + HOOKS).replace(ROUTE_OLD, ROUTE_NEW)
              .replace(ret, '  return {__sched, __now, __play, __mus, __st, __clr, init,'))
    return mod


def git_src(rev):
    import subprocess
    return subprocess.check_output(['git', '-C', ROOT, 'show', f'{rev}:src/bosque-do-enxame.html'], text=True)


def load_catalog():
    with open(CATALOG, encoding='utf-8') as f:
        return json.load(f)


def items(cat, only=None):
    for g in cat['groups']:
        for s in g['sounds']:
            if only and s['id'] not in only:
                continue
            yield g, s


PAGE = """<meta charset="utf-8"><script>
try { localStorage.setItem('bosque-enxame-som', '1'); localStorage.setItem('bosque-enxame-musica', '1'); } catch {}
window.setInterval = () => 0;   // no real-time music clock: music is scheduled explicitly with __sched
window.__secs = 4; window.__nodes = 0;
class FakeAC extends OfflineAudioContext {
  constructor(){ super(2, Math.ceil(48000*window.__secs), 48000); }
  get state(){ return 'running'; } resume(){ return Promise.resolve(); } suspend(){ return Promise.resolve(); }
}
for (const k of Object.getOwnPropertyNames(BaseAudioContext.prototype)) if (/^create/.test(k)) {
  const f = BaseAudioContext.prototype[k];
  FakeAC.prototype[k] = function(...a){ window.__nodes++; return f.apply(this, a); };
}
window.__acs = [];
window.AudioContext = function(){ const c = new FakeAC(); window.__acs.push(c); return c; };
</script><script>
%MODULE%
window.__SFX = SFX;
</script>"""

MEASURE = """async ([call, mood, secs]) => {
  window.__secs = secs; const S = window.__SFX; S.init(); const ac = window.__acs[0];
  const base = window.__nodes;
  if (mood) S.__sched(mood, secs - .2); else new Function('S', call)(S);
  const nodes = window.__nodes - base;
  const buf = await ac.startRendering(); const L = buf.getChannelData(0), R = buf.getChannelData(1), sr = buf.sampleRate;
  let pk = 0, last = 0, first = -1, sum = 0;
  for (let i = 0; i < L.length; i++){ const v = Math.max(Math.abs(L[i]), Math.abs(R[i])); if (v > pk) pk = v; if (v > 1e-3){ last = i; if (first < 0) first = i; } }
  const W = Math.floor(sr*.15); let best = 0, acc = 0;
  for (let i = 0; i < L.length; i++){ const e = (L[i]*L[i] + R[i]*R[i])/2; acc += e; if (i >= W){ const j = i - W; acc -= (L[j]*L[j] + R[j]*R[j])/2; } if (acc > best) best = acc; if (first >= 0 && i >= first && i <= last) sum += e; }
  const n = Math.max(1, last - Math.max(0, first) + 1);
  return {peak: pk, rms150: Math.sqrt(best/W), rms: Math.sqrt(sum/n), len: last/sr, nodes};
}"""


def db(v):
    return round(20*math.log10(max(v, 1e-9)), 1)


async def measure(only=None, src_text=None):
    """Measure the catalog sounds (only = set of ids). src_text: another version of the game (e.g. from git) instead of SRC."""
    from playwright.async_api import async_playwright
    cat = load_catalog()
    mod = extract_sfx(src_text if src_text is not None else open(SRC, encoding='utf-8').read())
    tmp = tempfile.mkdtemp(prefix='sfxlv-')
    page_path = os.path.join(tmp, 'm.html')
    with open(page_path, 'w', encoding='utf-8') as f:
        f.write(PAGE.replace('%MODULE%', mod))
    out = {}
    async with async_playwright() as pw:
        b = await pw.chromium.launch()
        for g, s in items(cat, only):
            pg = await b.new_page(); errs = []
            pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + page_path)
            secs = s.get('secs', 3)
            r = await pg.evaluate(MEASURE, [s.get('call'), s.get('mood'), secs])
            await pg.close()
            if errs:
                raise SystemExit(f"erro em {s['id']}: {errs[0]}")
            out[s['id']] = {'peak_db': db(r['peak']), 'rms150_db': db(r['rms150']), 'rms_db': db(r['rms']),
                            'len_s': round(r['len'], 2), 'nodes': r['nodes'], 'group': g['id']}
        await b.close()
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--json', help='grava os números neste arquivo JSON')
    ap.add_argument('--only', help='ids separados por vírgula')
    ap.add_argument('--rev', help='mede o jogo deste commit do git (ids que não existem nele dão erro: use --only)')
    a = ap.parse_args()
    only = set(a.only.split(',')) if a.only else None
    src = git_src(a.rev) if a.rev else None
    res = asyncio.run(measure(only, src))
    ref = res.get('explode', {}).get('rms150_db')
    print(f"{'id':14s} {'pico':>7s} {'rms150':>7s} {'rms':>7s} {'dur.':>6s} {'nós':>5s}" + ('  vs explosão' if ref is not None else ''))
    for k, v in res.items():
        rel = f"  {v['rms150_db'] - ref:+5.1f}" if ref is not None else ''
        print(f"{k:14s} {v['peak_db']:7.1f} {v['rms150_db']:7.1f} {v['rms_db']:7.1f} {v['len_s']:5.2f}s {v['nodes']:5d}{rel}")
    if a.json:
        with open(a.json, 'w', encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=1)
        print('gravado em', a.json)


if __name__ == '__main__':
    main()
