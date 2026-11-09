#!/usr/bin/env python3
"""Performance benchmark for Aren, o Guardião do Bosque (headless Chromium).

Builds an instrumented copy of src/bosque-do-enxame.html (internals exposed,
Math.random seeded, requestAnimationFrame wrapped to time each frame), then for
each scenario fast-forwards the simulation (update only, no render) with an
invulnerable hero and a fixed power schedule, and measures:

  bench  -- N synchronous update+render steps: average / p95 ms of update (U)
            and render (R), plus canvas call counts per frame (--calls)
  raf    -- the real requestAnimationFrame loop for a few seconds: FPS and the
            JS time spent per frame

at CPU throttle 1x and 4x (Chrome DevTools CPU throttling via CDP).

Scenarios: early (30 s), mid (300 s), late (840 s, all powers maxed incl.
relics and the Etapa 4 powers), boss (dragon fight, ~912 s), paladin (5:12) and
lich (10:15) (Etapa 5 mid-boss fights, boss held in phase 2). (Before Etapa 3 late was 540 s and the boss
came at 600 s; numbers in CHANGELOG for Etapa 2 use those times.)

Usage:
  python3 tests/perf.py                       # all scenarios, table on stdout
  python3 tests/perf.py late mid --throttle 4 # subset
  python3 tests/perf.py --json out.json       # raw numbers
  python3 tests/perf.py --calls               # also count fillRect/drawImage/...
  python3 tests/perf.py --boot                # boot time (script start -> end of script)
  python3 tests/perf.py late --pause          # also JS per frame while paused

Numbers from headless Chromium on a desktop CPU are only a proxy for a phone;
use them to compare versions on the same machine, not as absolute targets.
"""
import argparse, asyncio, json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_SRC = os.path.join(ROOT, 'src', 'bosque-do-enxame.html')

PRE = r'''<meta charset="utf-8">
<style>[hidden]{display:none!important}</style>
<script>
window.__t0 = performance.now();
window.AudioContext = undefined; window.webkitAudioContext = undefined;
(() => { const raf = window.requestAnimationFrame.bind(window);
  window.__fr = null; window.__halt = /[?&]halt/.test(location.search);  // ?halt: no frame runs until the harness says so
  window.requestAnimationFrame = cb => raf(function w(t){
    if (window.__halt) return raf(w);
    const t0 = performance.now(); cb(t); if (window.__fr) window.__fr.push(performance.now() - t0);
  });
})();
</script>
'''

HOOK = r'''
window.__tBoot = performance.now();
window.__seed = s => { let a = s >>> 0; Math.random = () => { a = (a + 0x6D2B79F5) >>> 0; let t = a; t = Math.imul(t ^ (t >>> 15), t | 1); t ^= t + Math.imul(t ^ (t >>> 7), t | 61); return ((t ^ (t >>> 14)) >>> 0) / 4294967296; }; };
window.__d = () => ({G, P, W, E, B, EB, GEMS, ITEMS, FX, NUMS, MARKS, CURSES, DECALS, BURNS, state, keys, ctx});
window.__set = s => { state = s; };
window.__u = update; window.__r = render; window.__amb = ambUpdate; window.__start = start;
'''

HELPERS = r'''
// Etapa 5: a living mid-boss is held in phase 2 (spirit, faster attacks) and never dies, so its effects stay on screen
window.__keepAlive = () => { const d = __d(); d.P.hp = d.P.maxHp; d.G.need = 1e12; d.G.pending = 0;
  for (const e of (d.G.guard || [])) if (e.m && e.m.st !== 'intro' && e.hp > e.max*.45 || e.m && e.hp < e.max*.3) e.hp = e.max*.45; };
window.__steer = i => { const k = __d().keys; for (const q of ['w','a','s','d']) k[q] = false;
  const m = [['d'],['d','s'],['s'],['s','a'],['a'],['a','w'],['w'],['w','d']][Math.floor(i/150) % 8]; for (const q of m) k[q] = true; };
// since 09/11/2026 a living mid-boss holds the run clock (G.t), so fast-forward by real time (G.t + G.hold); a mid-boss
// whose fight is not the scenario's (spawned more than 60 s before T) is removed at once, without its relic
window.__ff = (T, sched) => { let i = 0, maxE = 0;
  while (__d().G.t + (__d().G.hold || 0) < T){
    const d = __d();
    for (const e of (d.G.guard || []).slice()) if (T - e.born > 60){ e.dead = true; d.G.guard.splice(d.G.guard.indexOf(e), 1); }
    for (const [t, lv] of sched) if (d.G.t >= t) Object.assign(d.W, lv);
    __keepAlive(); __steer(i++); __u(1/60); __amb(1/60);
    if (__d().state !== 'play') return 'state ' + __d().state;
    maxE = Math.max(maxE, __d().E.length);
  }
  return {t: +__d().G.t.toFixed(2), maxE, steps: i};
};
window.__counts = () => { const d = __d(); const o = {}; for (const k of ['E','B','EB','FX','GEMS','NUMS','ITEMS','CURSES','BURNS','DECALS']) o[k] = d[k].length; return o; };
window.__bench = (N, calls) => {
  const U = [], R = [], acc = {}, cnt = {fillRect: 0, drawImage: 0, fillStyle: 0, globalAlpha: 0};
  const c = __d().ctx, proto = CanvasRenderingContext2D.prototype;
  if (calls){
    const fr = proto.fillRect, di = proto.drawImage, dFS = Object.getOwnPropertyDescriptor(proto, 'fillStyle'), dGA = Object.getOwnPropertyDescriptor(proto, 'globalAlpha');
    c.fillRect = function(){ cnt.fillRect++; return fr.apply(this, arguments); };
    c.drawImage = function(){ cnt.drawImage++; return di.apply(this, arguments); };
    Object.defineProperty(c, 'fillStyle', {set(v){ cnt.fillStyle++; dFS.set.call(this, v); }, get(){ return dFS.get.call(this); }, configurable: true});
    Object.defineProperty(c, 'globalAlpha', {set(v){ cnt.globalAlpha++; dGA.set.call(this, v); }, get(){ return dGA.get.call(this); }, configurable: true});
  }
  for (let i = 0; i < N; i++){
    __keepAlive(); __steer(i);
    const t0 = performance.now(); __u(1/60); __amb(1/60); const t1 = performance.now(); __r(1/60); const t2 = performance.now();
    U.push(t1 - t0); R.push(t2 - t1);
    const k = __counts(); for (const q in k) acc[q] = (acc[q] || 0) + k[q];
  }
  if (calls){ delete c.fillRect; delete c.drawImage; delete c.fillStyle; delete c.globalAlpha; }
  for (const q in acc) acc[q] = Math.round(acc[q]/N);
  const s = a => { const b = [...a].sort((x, y) => x - y); return {avg: +(a.reduce((x, y) => x + y, 0)/a.length).toFixed(3), p95: +b[Math.floor(b.length*.95)].toFixed(3), max: +b[b.length - 1].toFixed(3)}; };
  const per = {}; if (calls) for (const q in cnt) per[q] = Math.round(cnt[q]/N);
  return {U: s(U), R: s(R), counts: acc, calls: per};
};
0;
'''

SCHED_EARLY = [(0, {'sword': 2, 'boom': 1})]
SCHED_MID = SCHED_EARLY + [(120, {'sword': 3, 'boom': 2, 'orb': 2, 'fire': 2}), (240, {'sword': 5, 'boom': 4, 'orb': 4, 'fire': 4, 'boots': 2, 'magnet': 2})]
# Etapa 4: the new powers are maxed too (older versions just ignore the extra W keys), more than the 5-weapon cap allows: worst case
SCHED_LATE = SCHED_MID + [(300, {'holy': 1}), (450, {'holy': 3, 'boom': 5, 'orb': 5, 'fire': 5, 'boots': 5, 'magnet': 5,
                                                   'hammer': 5, 'thorns': 5, 'bow': 5, 'gauntlets': 5, 'grimoire': 5}), (600, {'storm': 2}), (700, {'storm': 3})]
SCEN = {'early': (30, SCHED_EARLY), 'mid': (300, SCHED_MID), 'late': (840, SCHED_LATE), 'boss': (912, SCHED_LATE),
        # Etapa 5 mid-bosses (fight in phase 2): Paladino at 5:12 with the mid build, Lich at 10:15 with the late build
        'paladin': (312, SCHED_MID), 'lich': (615, SCHED_LATE)}


def build(src, outdir):
    s = open(src, encoding='utf-8').read()
    i = s.rfind('})();\n</script>')
    if i < 0:
        raise SystemExit('could not find the end of the game IIFE in ' + src)
    s = PRE + s[:i] + HOOK + s[i:]
    path = os.path.join(outdir, 'perf.html')
    open(path, 'w', encoding='utf-8').write(s)
    fdir = os.path.join(os.path.dirname(os.path.abspath(src)), 'font')
    if os.path.isdir(fdir) and not os.path.isdir(os.path.join(outdir, 'font')):
        shutil.copytree(fdir, os.path.join(outdir, 'font'))
    return path


async def scenario(p, url, name, throttles, N, rafsec, seed, calls, pause=False):
    b = await p.chromium.launch()
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
    pg = await ctx.new_page()
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    cdp = await ctx.new_cdp_session(pg)
    await pg.goto(url + '?halt')
    await pg.wait_for_timeout(300)
    await pg.evaluate(HELPERS)
    await pg.evaluate(f"__halt = true; __seed({seed}); __start();")
    T, sched = SCEN[name]
    out = {'scenario': name}
    if name == 'boss':
        out['ff'] = [await pg.evaluate("([T, s]) => __ff(T, s)", [860, sched])]
        await pg.evaluate("__d().G.t = 899.9")
        out['ff'].append(await pg.evaluate("([T, s]) => __ff(T, s)", [T, sched]))
    else:
        out['ff'] = await pg.evaluate("([T, s]) => __ff(T, s)", [T, sched])
    # snapshot of the state so each throttle level starts from the same frame
    out['res'] = {}
    for thr in throttles:
        await cdp.send('Emulation.setCPUThrottlingRate', {'rate': thr})
        await pg.evaluate("__bench(60, false)")
        bench = await pg.evaluate("([n, c]) => __bench(n, c)", [N, calls])
        await pg.evaluate("window.__fr = []; window.__ka = setInterval(__keepAlive, 30); window.__rafT = []; const g = window.__gen = (window.__gen || 0) + 1;"
                          "(function f(t){ if (window.__gen !== g) return; __rafT.push(t); requestAnimationFrame(f); })(performance.now()); __halt = false;")
        await pg.wait_for_timeout(rafsec * 1000)
        raf = await pg.evaluate("""() => { __halt = true; window.__gen++; clearInterval(__ka);
          const t = __rafT, fr = [...__fr].sort((a, b) => a - b); window.__fr = null;
          return {fps: +(1000*(t.length - 1)/(t[t.length - 1] - t[0])).toFixed(1),
                  jsAvg: +(fr.reduce((a, b) => a + b, 0)/fr.length).toFixed(2), jsP95: +fr[Math.floor(fr.length*.95)].toFixed(2), state: __d().state}; }""")
        if raf['state'] != 'play':
            await pg.evaluate("__set('play')")
        out['res'][str(thr)] = {'bench': bench, 'raf': raf}
    if pause:
        # paused: JS per rAF frame with the game frozen behind the pause panel
        await pg.evaluate("__set('pause'); window.__fr = []; __halt = false;")
        await pg.wait_for_timeout(2000)
        out['pause_js'] = await pg.evaluate("() => { __halt = true; const f = __fr; window.__fr = null; return +(f.reduce((a, b) => a + b, 0)/f.length).toFixed(3); }")
        print(f"{name:6s} paused: {out['pause_js']} ms JS per frame (CPU {throttles[-1]}x)")
    out['errs'] = errs[:5]
    await b.close()
    return out


async def boot(p, url, runs=3):
    res = {}
    b = await p.chromium.launch()
    ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=3, is_mobile=True, has_touch=True)
    for thr in (1, 4):
        v = []
        for _ in range(runs):
            pg = await ctx.new_page()
            cdp = await ctx.new_cdp_session(pg)
            await cdp.send('Emulation.setCPUThrottlingRate', {'rate': thr})
            await pg.goto(url)
            await pg.wait_for_timeout(400)
            v.append(await pg.evaluate("+(__tBoot - __t0).toFixed(1)"))
            await pg.close()
        res[str(thr)] = sorted(v)[len(v)//2]
    await b.close()
    return res


async def main(a):
    from playwright.async_api import async_playwright
    tmp = tempfile.mkdtemp(prefix='aren-perf-')
    url = 'file://' + build(a.src, tmp)
    out = {'src': os.path.abspath(a.src), 'scen': []}
    async with async_playwright() as p:
        if a.boot:
            out['boot_ms'] = await boot(p, url)
            print('boot (script start -> end of script), median of 3:', out['boot_ms'])
        for n in a.scenarios:
            r = await scenario(p, url, n, a.throttle, a.n, a.raf, a.seed, a.calls, a.pause)
            out['scen'].append(r)
            for thr, x in r['res'].items():
                bb, rf = x['bench'], x['raf']
                line = f"{n:6s} {thr}x  bench U {bb['U']['avg']:6.2f} R {bb['R']['avg']:6.2f} (p95 {bb['R']['p95']:6.2f})  raf {rf['fps']:5.1f} fps js {rf['jsAvg']:6.2f} ms (p95 {rf['jsP95']:6.2f})"
                if a.calls:
                    line += '  ' + ' '.join(f"{k}={v}" for k, v in bb['calls'].items())
                print(line, ' counts', bb['counts'], ' errs' if r['errs'] else '', r['errs'] or '')
                sys.stdout.flush()
    shutil.rmtree(tmp, ignore_errors=True)
    if a.json:
        json.dump(out, open(a.json, 'w'), indent=1)


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('scenarios', nargs='*', default=['early', 'mid', 'late', 'boss', 'paladin', 'lich'])
    ap.add_argument('--src', default=DEFAULT_SRC)
    ap.add_argument('--throttle', type=int, nargs='+', default=[1, 4])
    ap.add_argument('-n', type=int, default=600, help='bench frames')
    ap.add_argument('--raf', type=int, default=5, help='seconds of real rAF loop per throttle level')
    ap.add_argument('--seed', type=int, default=777)
    ap.add_argument('--calls', action='store_true')
    ap.add_argument('--boot', action='store_true')
    ap.add_argument('--pause', action='store_true', help='also measure JS per frame while paused')
    ap.add_argument('--json')
    a = ap.parse_args()
    for s in a.scenarios:
        if s not in SCEN:
            raise SystemExit('unknown scenario ' + s)
    asyncio.run(main(a))
