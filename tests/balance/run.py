#!/usr/bin/env python3
"""Balance simulator: plays whole runs with a bot, many seeds, in headless Chromium.

    python3 tests/balance/run.py --out /tmp/after.json                  # default matrix
    python3 tests/balance/run.py --src old.html --seeds 1-6 --modes kite --policies prio,random --out x.json
    python3 tests/balance/analyze.py /tmp/after.json                    # report

Each run: instrumented copy (patch.py) + bot.js (seeded Math.random, pick policy,
movement mode 'agg' = walks into sword range, 'kite' = cautious, never closes to melee).
The simulation steps update() directly at --dt (default 1/30 s) inside the page: no
rendering, no requestAnimationFrame. A run ends on death, victory or --max seconds.
The bot is not a human: use the numbers to compare versions, not as the real difficulty.
"""
import argparse, asyncio, json, os, subprocess, sys, tempfile, time
from playwright.async_api import async_playwright

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(D))
BOT = open(os.path.join(D, 'bot.js')).read()

CHUNK = """(args) => {
  const [secs, dt, maxT] = args; const out = [];
  for (let i = 0; i < secs/dt; i++){
    if (__d().state === 'levelup') __botPick();
    if (__d().state !== 'play') break;
    __botMove(dt);
    __u(dt);
    const d = __d();
    if (Math.floor(d.G.t/5) !== Math.floor((d.G.t - dt)/5)){
      const S = window.__ST;
      let alive = 0; for (const e of d.E) if (!e.dead && !e.d.boss) alive += Math.max(0, e.hp);
      out.push({t:Math.round(d.G.t), lvl:d.G.lvl, hp:d.P.hp, max:d.P.maxHp, n:d.E.length, alive:Math.round(alive),
        dmg:Math.round(S.secDmg/5), inc:Math.round(S.secSpawnHp/5), hurt:S.secHurt, kills:d.G.kills, gems:d.GEMS.length,
        bossHp: d.G.boss && d.G.boss.e ? Math.round(d.G.boss.e.hp) : null});
      S.secDmg = 0; S.secSpawnHp = 0; S.secHurt = 0;
    }
    if (d.state === 'levelup') __botPick();
    if (__d().state !== 'play') break;
    if (d.G.t > maxT) break;
  }
  const d = __d();
  return {samples:out, state:d.state, t:d.G.t};
}"""

FINAL = """() => { const d = __d(), G = d.G; return {state:d.state, t:G.t, lvl:G.lvl, kills:G.kills, ups:G.ups, gems:G.gems, W:d.W,
  boss: G.boss ? {phase:G.boss.phase, t:G.boss.t, hp: G.boss.e ? G.boss.e.hp : null, max: G.boss.e ? G.boss.e.d.hp : null} : null,
  ST: {raw:__ST.raw, eff:__ST.eff, boss:__ST.boss, guard:__ST.guard, hurt:__ST.hurt, items:__ST.items, spawnN:__ST.spawnN, sealHits:__ST.sealHits},
  picks: __BOT.picks, title: document.querySelector('#overTitle').textContent}; }"""

async def one(b, sim, seed, policy, mode, dt, maxT):
    pg = await b.new_page(viewport={'width': 420, 'height': 800})
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.add_init_script(BOT)
    await pg.goto(f'file://{sim}?seed={seed}&policy={policy}&mode={mode}')
    await pg.wait_for_timeout(200)
    await pg.evaluate("() => __start()")
    samples = []; t0 = time.time()
    while True:
        r = await pg.evaluate(CHUNK, [30, dt, maxT])
        samples += r['samples']
        if r['state'] not in ('play', 'levelup') or r['t'] > maxT: break
    fin = await pg.evaluate(FINAL)
    fin.update(seed=seed, policy=policy, mode=mode, errs=errs[:3], wall=round(time.time() - t0), samples=samples)
    await pg.close()
    return fin

def rng(spec):
    out = []
    for part in spec.split(','):
        if '-' in part: a, b = part.split('-'); out += range(int(a), int(b) + 1)
        else: out.append(int(part))
    return out

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=os.path.join(ROOT, 'src', 'bosque-do-enxame.html'))
    ap.add_argument('--out', required=True)
    ap.add_argument('--seeds', default='1-4')
    ap.add_argument('--modes', default='kite,agg')
    ap.add_argument('--policies', default='prio,random,balanced,sword,orb,defense')
    ap.add_argument('--dt', type=float, default=1/30)
    ap.add_argument('--max', type=float, default=1200)
    ap.add_argument('--par', type=int, default=int(os.environ.get('PAR', '2')))
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix='aren-bal-')
    sim = os.path.join(tmp, 'sim.html')
    subprocess.run([sys.executable, os.path.join(D, 'patch.py'), a.src, sim], check=True)
    runs = [(s, p, m) for m in a.modes.split(',') for p in a.policies.split(',') for s in rng(a.seeds)]
    async with async_playwright() as p:
        b = await p.chromium.launch()
        sem = asyncio.Semaphore(a.par)
        async def guard(r):
            async with sem:
                res = await one(b, sim, r[0], r[1], r[2], a.dt, a.max)
                bo = res['boss']
                print(f"{r} {res['state']} t={res['t']:.0f} {res['title']!r} lvl={res['lvl']} picks={len(res['picks'])} "
                      f"boss={bo and bo['phase']} wall={res['wall']}s {res['errs'] or ''}", flush=True)
                return res
        res = await asyncio.gather(*[guard(r) for r in runs])
        await b.close()
    json.dump({'src': a.src, 'dt': a.dt, 'runs': res}, open(a.out, 'w'))

asyncio.run(main())
