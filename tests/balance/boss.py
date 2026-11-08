#!/usr/bin/env python3
"""Dragon fight in isolation: jumps to just before the dragon with a fixed build and lets the bot fight it.

    python3 tests/balance/boss.py                 # default cases, current src
    python3 tests/balance/boss.py --src old.html

Each case: build (power levels), max hp (half hearts), god (hp refilled every step),
mode (bot movement: 'agg' closes in while the dragon is stunned, 'kite' never does).
Reports fight length, hp left, damage share per power and the seal share.
"""
import argparse, asyncio, json, os, subprocess, sys, tempfile
from playwright.async_api import async_playwright

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(D))
BOT = open(os.path.join(D, 'bot.js')).read()
MID = {'sword': 3, 'boom': 4, 'orb': 2, 'fire': 4, 'boots': 2, 'heart': 3, 'holy': 2, 'storm': 1}
LOW = {'sword': 2, 'boom': 3, 'fire': 3, 'orb': 1, 'heart': 1, 'holy': 1}
MAX = {'sword': 5, 'boom': 5, 'orb': 5, 'fire': 5, 'boots': 5, 'magnet': 5, 'heart': 5, 'holy': 3, 'storm': 3}
CASES = [
    ('mid god agg', 1, MID, 16, True, 'agg'), ('mid god agg', 2, MID, 16, True, 'agg'), ('mid god agg', 3, MID, 16, True, 'agg'),
    ('mid god kite', 1, MID, 16, True, 'kite'), ('mid god kite', 2, MID, 16, True, 'kite'),
    ('mid real agg', 1, MID, 16, False, 'agg'), ('mid real agg', 2, MID, 16, False, 'agg'), ('mid real kite', 1, MID, 16, False, 'kite'),
    ('low god agg', 1, LOW, 12, True, 'agg'),
    ('max god agg', 1, MAX, 20, True, 'agg'), ('max god kite', 1, MAX, 20, True, 'kite'),
    ('sword-only god agg', 1, {'sword': 5, 'heart': 5}, 20, True, 'agg'),
]
JS = """(args) => {
  const [W, hp, god, maxT, dt] = args; const d0 = __d();
  Object.assign(d0.W, W); d0.P.maxHp = hp; d0.P.hp = hp; d0.G.need = 1e9;
  const T0 = (d0.BOSSES ? d0.BOSSES.find(b => b.id === 'dragon').t : d0.BOSS_T) - 1;
  __skipTo(T0); d0.G.lvl = 30;
  const log = [];
  for (let i = 0; i < maxT/dt; i++){
    const d = __d();
    if (d.state === 'levelup') __botPick();
    if (__d().state !== 'play') break;
    __botMove(dt);
    if (god) d.P.hp = d.P.maxHp;
    __u(dt);
    const dd = __d(), b = dd.G.boss && dd.G.boss.e;
    if (b && Math.floor((dd.G.t - T0)/15) !== Math.floor((dd.G.t - T0 - dt)/15)) log.push([Math.round(dd.G.t - T0), Math.round(b.hp), dd.P.hp]);
    if (dd.state !== 'play' && dd.state !== 'levelup') break;
  }
  const d = __d(), b = d.G.boss && d.G.boss.e;
  return {state:d.state, fight: d.G.boss ? d.G.boss.t - 5.4 : null, bossHp: b ? Math.round(Math.max(0, b.hp)) : null, max: b ? b.d.hp : null,
    phase: d.G.boss && d.G.boss.phase, log, hurt: __ST.hurt, boss: __ST.boss, seals: __ST.sealHits, title: document.querySelector('#overTitle').textContent};
}"""

async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--src', default=os.path.join(ROOT, 'src', 'bosque-do-enxame.html'))
    ap.add_argument('--json')
    ap.add_argument('--dt', type=float, default=1/30)
    a = ap.parse_args()
    tmp = tempfile.mkdtemp(prefix='aren-boss-'); sim = os.path.join(tmp, 'sim.html')
    subprocess.run([sys.executable, os.path.join(D, 'patch.py'), a.src, sim], check=True, stdout=subprocess.DEVNULL)
    res = []
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name, seed, W, hp, god, mode in CASES:
            pg = await b.new_page(viewport={'width': 420, 'height': 800})
            await pg.add_init_script(BOT)
            await pg.goto(f'file://{sim}?seed={seed}&policy=prio&mode={mode}')
            await pg.wait_for_timeout(200)
            await pg.evaluate("() => __start()")
            r = await pg.evaluate(JS, [W, hp, god, 600, a.dt])
            r.update(case=name, seed=seed)
            tot = sum(r['boss'].values()) or 1
            share = ' '.join(f"{k} {v/tot*100:.0f}%" for k, v in sorted(r['boss'].items(), key=lambda x: -x[1]))
            res_t = 'WON' if r['title'] == 'Vitória!' else ('died' if r['state'] == 'over' else 'timeout')
            print(f"{name:20s} s{seed} {res_t:7s} fight {r['fight'] or 0:5.0f}s  hp left {r['bossHp']}/{r['max']}  seals {r['seals']}  | {share}", flush=True)
            res.append(r); await pg.close()
        await b.close()
    if a.json: json.dump(res, open(a.json, 'w'))

asyncio.run(main())
