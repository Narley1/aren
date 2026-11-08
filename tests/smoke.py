#!/usr/bin/env python3
"""Smoke test + determinism probe for Aren, o Guardião do Bosque.

Self-contained: copies src/bosque-do-enxame.html into a temp dir, injects a hook
that exposes the game's internals as window.__t (and a seeded Math.random), then
drives the game headless with Playwright/Chromium.

Runs:
  stress  -- title -> start -> ~620 s with an invulnerable hero and every power
             maxed (relics included), boss intro/fight, forced victory, back to
             title, then 3 restart cycles (play 30 s, die, game-over screen, title).
  normal  -- 120 s with a simple kiting bot (hero can die).
  races   -- die / win and restart immediately: the stale game-over screen must
             not pop over the new run; keys are cleared on blur.

Usage:
  python3 tests/smoke.py                    # run everything, exit 1 on failure
  python3 tests/smoke.py --src other.html   # test another copy of the game
  python3 tests/smoke.py --json out.json    # also dump the numbers (for diffs)
  python3 tests/smoke.py --compare a.json b.json   # determinism diff of two dumps

The 'det' section of the JSON (seeded runs: kills, xp, level, hp at t=120 s, and
the stress run's end state) must be identical between two versions of the code
that are supposed to behave the same (e.g. refactors such as the BAL object).
"""
import argparse, asyncio, json, os, re, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(ROOT, 'src', 'bosque-do-enxame.html')

# Injected right before the closing `})();` of the game's IIFE, so it sees the
# closure's variables. Only names that exist in every version are referenced.
HOOK = r'''
window.__seed = s => { let a = s >>> 0; Math.random = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
window.__t = {
  get G(){ return G; }, get P(){ return P; }, get W(){ return W; }, get E(){ return E; }, get FX(){ return FX; },
  get B(){ return B; }, get EB(){ return EB; }, get GEMS(){ return GEMS; }, get ITEMS(){ return ITEMS; }, get NUMS(){ return NUMS; },
  get state(){ return state; }, set state(v){ state = v; }, get J(){ return J; }, set J(v){ J = v; },
  keys, update, start, goTitle, togglePause, gameOver, victory, hurt, ambUpdate, hud, render, openLevelUp, startBoss,
  pick(i){ lvlOpenedAt = -1e9; chooseLevel(i); }
};
'''

def build_hooked(src, outdir, audio=True):
    s = open(src, encoding='utf-8').read()
    i = s.rfind('})();\n</script>')
    if i < 0:
        raise SystemExit('could not find the end of the game IIFE in ' + src)
    s = s[:i] + HOOK + s[i:]
    if not audio:
        # SFX throttles use AudioContext.currentTime (wall clock) before calling
        # Math.random, so audio must be off for a reproducible seeded run.
        j = s.find('<script>')
        s = s[:j] + '<script>window.AudioContext = undefined; window.webkitAudioContext = undefined;</script>\n' + s[j:]
    s = '<meta charset="utf-8">\n' + s  # the source has no charset; the build adds it
    path = os.path.join(outdir, 'hooked-audio.html' if audio else 'hooked-noaudio.html')
    open(path, 'w', encoding='utf-8').write(s)
    fdir = os.path.join(os.path.dirname(src), 'font')
    if os.path.isdir(fdir) and not os.path.isdir(os.path.join(outdir, 'font')):
        shutil.copytree(fdir, os.path.join(outdir, 'font'))
    return path

# One synchronous evaluate per simulation: requestAnimationFrame cannot interleave,
# so the run is fully deterministic once Math.random is seeded.
STRESS = r'''
(seed) => {
  const T = window.__t, out = {errors: []};
  window.__seed(seed);
  T.start();
  const DT = 1/30;
  let maxE = 0, maxFX = 0, maxB = 0, maxEB = 0, maxGEMS = 0, maxITEMS = 0, maxNUMS = 0, picks = 0, nan = 0, steps = 0;
  let at120 = null, bossSeen = false, fightSeen = false, forced = false;
  for (const k of ['sword','boom','orb','fire','boots','magnet']) T.W[k] = 5;
  for (; steps < 700*30; steps++){
    T.P.inv = 5; T.P.hp = T.P.maxHp;
    if (T.G.t >= 300) for (const k of ['holy','storm','meteor']) T.W[k] = 3;
    T.update(DT); T.ambUpdate(DT);
    if (steps % 10 === 0) T.hud();
    if (steps % 15 === 0) T.render(DT);
    if (T.state === 'play' && T.G.pending > 0) T.openLevelUp();
    if (T.state === 'levelup'){ T.pick(0); picks++; }
    maxE = Math.max(maxE, T.E.length); maxFX = Math.max(maxFX, T.FX.length); maxB = Math.max(maxB, T.B.length);
    maxEB = Math.max(maxEB, T.EB.length); maxGEMS = Math.max(maxGEMS, T.GEMS.length); maxITEMS = Math.max(maxITEMS, T.ITEMS.length); maxNUMS = Math.max(maxNUMS, T.NUMS.length);
    if (!isFinite(T.P.x) || !isFinite(T.P.y)) nan++;
    for (const e of T.E) if (!isFinite(e.x) || !isFinite(e.y) || Number.isNaN(e.hp)) { nan++; break; }
    if (!at120 && T.G.t >= 120) at120 = {kills: T.G.kills, xp: T.G.xp, lvl: T.G.lvl, gems: T.G.gems, E: T.E.length};
    const bo = T.G.boss;
    if (bo){ bossSeen = true; if (bo.phase === 'fight') fightSeen = true; }
    if (bo && bo.phase === 'fight' && T.G.t > 615 && bo.e && bo.e.hp > 1){ bo.e.hp = 1; forced = true; }
    if (T.state === 'over') break;
  }
  const bo = T.G.boss;
  Object.assign(out, {steps, t: +T.G.t.toFixed(3), state: T.state, bossSeen, fightSeen, forced, bossPhase: bo && bo.phase,
    kills: T.G.kills, lvl: T.G.lvl, xp: T.G.xp, gems: T.G.gems, ups: T.G.ups, picks, nan, at120,
    max: {E: maxE, FX: maxFX, B: maxB, EB: maxEB, GEMS: maxGEMS, ITEMS: maxITEMS, NUMS: maxNUMS},
    W: Object.assign({}, T.W)});
  return out;
}
'''

NORMAL = r'''
(seed) => {
  const T = window.__t;
  window.__seed(seed);
  T.start();
  const DT = 1/30, K = T.keys;
  let picks = 0, died = null, at120 = null, maxE = 0, nan = 0;
  for (let i = 0; i < 125*30; i++){
    // kiting bot: step away from enemies about to touch, sidestep projectiles, otherwise hold ground
    let fx = 0, fy = 0;
    for (const e of T.E){ const dx = T.P.x - e.x, dy = T.P.y - e.y, d2 = dx*dx + dy*dy; if (d2 < 20*20 && d2 > 0){ fx += dx/d2; fy += dy/d2; } }
    for (const b of T.EB){ const dx = T.P.x - b.x, dy = T.P.y - b.y, d2 = dx*dx + dy*dy; if (d2 < 50*50 && d2 > 0){ fx += 2*dx/d2; fy += 2*dy/d2; } }
    for (const it of T.ITEMS){ const dx = it.x - T.P.x, dy = it.y - T.P.y, d2 = dx*dx + dy*dy; if (d2 < 60*60 && d2 > 0){ fx += .5*dx/d2; fy += .5*dy/d2; } }
    // nothing within 60 px: walk toward the nearest enemy so the sword gets work
    let near = null, nd = 1e9;
    for (const e of T.E){ const d = Math.hypot(e.x - T.P.x, e.y - T.P.y); if (d < nd){ nd = d; near = e; } }
    if (near && nd > 60 && fx === 0 && fy === 0){ fx = (near.x - T.P.x)/nd; fy = (near.y - T.P.y)/nd; }
    const m = Math.hypot(fx, fy);
    K.a = m > 1e-4 && fx/m < -.38; K.d = m > 1e-4 && fx/m > .38; K.w = m > 1e-4 && fy/m < -.38; K.s = m > 1e-4 && fy/m > .38;
    T.update(DT); T.ambUpdate(DT);
    if (i % 10 === 0) T.hud();
    if (i % 15 === 0) T.render(DT);
    if (T.state === 'play' && T.G.pending > 0) T.openLevelUp();
    if (T.state === 'levelup'){ T.pick(0); picks++; }
    maxE = Math.max(maxE, T.E.length);
    if (!isFinite(T.P.x) || !isFinite(T.P.y)) nan++;
    if (!at120 && T.G.t >= 120) at120 = {kills: T.G.kills, xp: T.G.xp, lvl: T.G.lvl, hp: T.P.hp, gems: T.G.gems, x: +T.P.x.toFixed(4), y: +T.P.y.toFixed(4)};
    if (T.state === 'over'){ died = +T.G.t.toFixed(3); break; }
  }
  for (const k in K) K[k] = false;
  return {died, at120, picks, maxE, nan, end: {t: +T.G.t.toFixed(3), kills: T.G.kills, xp: T.G.xp, lvl: T.G.lvl, hp: T.P.hp, gems: T.G.gems, W: Object.assign({}, T.W)}};
}
'''

AFTER_VICTORY = r'''
async () => {
  const T = window.__t, r = {};
  await new Promise(res => setTimeout(res, 1300));
  r.overShown = !document.querySelector('#overScreen').hidden;
  r.overTitle = document.querySelector('#overTitle').textContent;
  T.goTitle();
  r.titleShown = !document.querySelector('#titleScreen').hidden && T.state === 'menu';
  r.cycles = [];
  for (let c = 0; c < 3; c++){
    T.start();
    const s = {startState: T.state, boss: T.G.boss, dark: T.G.dark, t0: T.G.t, E0: T.E.length, overHidden: document.querySelector('#overScreen').hidden, bossBarHidden: document.querySelector('#bossBar').hidden};
    for (let i = 0; i < 30*30; i++){ T.P.inv = 5; T.update(1/30); if (T.state === 'play' && T.G.pending > 0) T.openLevelUp(); if (T.state === 'levelup') T.pick(0); }
    s.t30 = +T.G.t.toFixed(2); s.E30 = T.E.length; s.kills = T.G.kills; s.state30 = T.state;
    T.P.inv = 0; T.hurt(999); s.dead = T.state;
    await new Promise(res => setTimeout(res, 800));
    s.overShown = !document.querySelector('#overScreen').hidden;
    T.goTitle(); s.title = T.state;
    r.cycles.push(s);
  }
  return r;
}
'''

RACES = r'''
async () => {
  const T = window.__t, r = {};
  // die, restart at once: the 500 ms game-over timeout must not show the panel over the new run
  T.start(); T.P.inv = 0; T.hurt(999); T.start();
  await new Promise(res => setTimeout(res, 800));
  r.deathRace = {state: T.state, overVisible: !document.querySelector('#overScreen').hidden};
  // same for victory (900 ms) followed by goTitle
  T.start(); T.victory(); T.goTitle();
  await new Promise(res => setTimeout(res, 1200));
  r.victoryRace = {state: T.state, overVisible: !document.querySelector('#overScreen').hidden};
  T.start();
  return r;
}
'''

async def run(src, seed):
    from playwright.async_api import async_playwright
    tmp = tempfile.mkdtemp(prefix='aren-smoke-')
    res = {'src': os.path.abspath(src), 'seed': seed}
    try:
        page_path = build_hooked(src, tmp)
        async with async_playwright() as p:
            b = await p.chromium.launch()
            pg = await b.new_page(viewport={'width': 900, 'height': 700})
            errs = []
            pg.on('pageerror', lambda e: errs.append('pageerror: ' + str(e)))
            pg.on('console', lambda m: errs.append('console.error: ' + m.text) if m.type == 'error' else None)
            await pg.goto('file://' + page_path)
            await pg.wait_for_timeout(700)
            res['stress'] = await pg.evaluate(STRESS, seed)
            res['afterVictory'] = await pg.evaluate(AFTER_VICTORY)
            await pg.evaluate('() => window.__t.goTitle()')
            res['normal'] = await pg.evaluate(NORMAL, seed + 1)
            await pg.evaluate('() => window.__t.goTitle()')
            res['races'] = await pg.evaluate(RACES)
            # stuck keys: hold W, blur the window -> key must be released and the game paused
            await pg.keyboard.down('w')
            await pg.evaluate('() => window.dispatchEvent(new Event("blur"))')
            res['blur'] = await pg.evaluate('() => ({w: !!window.__t.keys.w, state: window.__t.state})')
            await pg.keyboard.up('w')
            # determinism pass: fresh page, audio off, same seeds
            pg2 = await b.new_page(viewport={'width': 900, 'height': 700})
            pg2.on('pageerror', lambda e: errs.append('pageerror (det): ' + str(e)))
            pg2.on('console', lambda m: errs.append('console.error (det): ' + m.text) if m.type == 'error' else None)
            await pg2.goto('file://' + build_hooked(src, tmp, audio=False))
            await pg2.wait_for_timeout(700)
            ds = await pg2.evaluate(STRESS, seed)
            await pg2.evaluate('() => window.__t.goTitle()')
            dn = await pg2.evaluate(NORMAL, seed + 1)
            res['errors'] = errs
            await b.close()
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    res['det'] = {'stress_at120': ds['at120'], 'stress_end': {k: ds[k] for k in ('t', 'kills', 'lvl', 'xp', 'gems', 'ups', 'picks', 'max')},
                  'normal_at120': dn['at120'], 'normal_died': dn['died'], 'normal_end': dn['end']}
    return res

def checks(r):
    s, a, n, rc = r['stress'], r['afterVictory'], r['normal'], r['races']
    c = []
    def ok(name, cond, info=''):
        c.append((name, bool(cond), info))
    ok('no console/page errors', not r['errors'], '; '.join(r['errors'][:5]))
    ok('stress: reached boss fight', s['bossSeen'] and s['fightSeen'])
    ok('stress: victory reached (state over, boss won)', s['state'] == 'over' and s['bossPhase'] == 'won', f"state={s['state']} phase={s['bossPhase']} t={s['t']}")
    ok('stress: no NaN positions', s['nan'] == 0)
    ok('stress: entity counts sane', s['max']['E'] <= 300 and s['max']['GEMS'] <= 450 and s['max']['NUMS'] <= 80 and s['max']['FX'] < 20000, json.dumps(s['max']))
    ok('victory: game-over panel shown', a['overShown'] and a['overTitle'] == 'Vitória!')
    ok('victory: back to title', a['titleShown'])
    for i, cy in enumerate(a['cycles']):
        ok(f'restart {i+1}: clean start', cy['startState'] == 'play' and cy['boss'] is None and cy['dark'] == 0 and cy['t0'] == 0 and cy['E0'] == 0 and cy['overHidden'] and cy['bossBarHidden'], json.dumps(cy))
        ok(f'restart {i+1}: played 30 s, died, panel, title', cy['state30'] == 'play' and cy['dead'] == 'over' and cy['overShown'] and cy['title'] == 'menu')
    ok('normal: reached 120 s or died legitimately', n['at120'] is not None or n['died'] is not None, json.dumps(n['at120']))
    ok('normal: no NaN', n['nan'] == 0)
    ok('race: death then restart keeps panel hidden', rc['deathRace']['state'] == 'play' and not rc['deathRace']['overVisible'], json.dumps(rc['deathRace']))
    ok('race: victory then title keeps panel hidden', rc['victoryRace']['state'] == 'menu' and not rc['victoryRace']['overVisible'], json.dumps(rc['victoryRace']))
    ok('blur: keys released and game paused', not r['blur']['w'] and r['blur']['state'] == 'pause', json.dumps(r['blur']))
    return c

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--seed', type=int, default=12345)
    ap.add_argument('--json')
    ap.add_argument('--compare', nargs=2, metavar=('A', 'B'))
    a = ap.parse_args()
    if a.compare:
        x, y = (json.load(open(f))['det'] for f in a.compare)
        same = x == y
        print('determinism:', 'IDENTICAL' if same else 'DIFFERENT')
        if not same:
            for k in x:
                if x[k] != y.get(k): print(' ', k, '\n    A:', x[k], '\n    B:', y.get(k))
        sys.exit(0 if same else 1)
    r = asyncio.run(run(a.src, a.seed))
    if a.json:
        json.dump(r, open(a.json, 'w'), indent=1, ensure_ascii=False)
    s, n = r['stress'], r['normal']
    print(f"stress: t={s['t']} state={s['state']} boss={s['bossPhase']} kills={s['kills']} lvl={s['lvl']} picks={s['picks']} max={s['max']}")
    print(f"normal: died={n['died']} at120={n['at120']} picks={n['picks']} maxE={n['maxE']}")
    print(f"det (seeded, audio off): normal@120={r['det']['normal_at120']} died={r['det']['normal_died']} stress_end={r['det']['stress_end']}")
    fails = 0
    for name, good, info in checks(r):
        print(('PASS ' if good else 'FAIL ') + name + ('' if good or not info else '  -> ' + info))
        fails += not good
    print(f'{fails} failure(s)')
    sys.exit(1 if fails else 0)

if __name__ == '__main__':
    main()
