#!/usr/bin/env python3
"""Report for run.py results.  python3 tests/balance/analyze.py a.json [b.json ...] [--detail]"""
import json, statistics as st, sys
from collections import defaultdict

args = [a for a in sys.argv[1:] if not a.startswith('--')]
detail = '--detail' in sys.argv

def q(xs, p):
    xs = sorted(xs)
    if not xs: return float('nan')
    k = (len(xs) - 1) * p; i = int(k); j = min(i + 1, len(xs) - 1)
    return xs[i] + (xs[j] - xs[i]) * (k - i)

def end_t(r): return r['t']
def won(r): return r['title'] == 'Vitória!'

for f in args:
    data = json.load(open(f)); runs = data['runs']
    print(f'== {f}  ({len(runs)} runs, dt={data.get("dt")})')
    by = defaultdict(list)
    for r in runs: by[r['mode']].append(r)
    for mode, rs in by.items():
        ts = [end_t(r) for r in rs]
        print(f'-- mode {mode}: n={len(rs)}')
        print(f'   end time  min {min(ts):.0f}  p25 {q(ts,.25):.0f}  median {q(ts,.5):.0f}  p75 {q(ts,.75):.0f}  max {max(ts):.0f}')
        for T in (300, 360, 480, 600, 750, 900):
            print(f'   reached {T:4d}s: {sum(t >= T for t in ts)/len(rs)*100:5.1f}%', end='')
        print(f'   victory: {sum(won(r) for r in rs)/len(rs)*100:.1f}%')
        # level timeline
        def lvl_at(r, T):
            ss = [s for s in r['samples'] if s['t'] <= T]
            return ss[-1]['lvl'] if ss and r['t'] >= T else None
        for T in (60, 120, 180, 300, 450, 600, 900):
            ls = [x for x in (lvl_at(r, T) for r in rs) if x]
            if ls: print(f'   lvl@{T}: {st.median(ls):.0f}', end='')
        l20 = [next((s['t'] for s in r['samples'] if s['lvl'] >= 20), None) for r in rs]
        l20 = [x for x in l20 if x]
        print(f'   lvl20 at median {st.median(l20):.0f}s (n={len(l20)})' if l20 else '   lvl20 never')
        # picks
        pts = [[p['t'] for p in r['picks']] for r in rs]
        gaps = [b - a for p in pts for a, b in zip([0] + p, p)]
        npk = [len(p) for p in pts]
        firsts = [st.median([p[i] for p in pts if len(p) > i]) for i in range(max(npk)) if sum(len(p) > i for p in pts) >= len(pts)/2]
        print(f'   picks/run median {st.median(npk)}; gap median {st.median(gaps):.0f}s p75 {q(gaps,.75):.0f}s; pick times (median): ' + ' '.join(f'{x:.0f}' for x in firsts))
        gl = [[p['lvl'] for p in r['picks']] for r in rs]
        print('   pick levels (first run):', gl[0][:16])
        # damage share
        tot = defaultdict(float); mx = []
        for r in rs:
            e = r['ST']['eff']; s = sum(e.values()) or 1
            for k, v in e.items(): tot[k] += v / s / len(rs)
            if r['policy'] in ('random', 'balanced', 'prio'): mx.append(max(e.values()) / s)
        print('   damage share (avg of runs): ' + ' '.join(f'{k} {v*100:.0f}%' for k, v in sorted(tot.items(), key=lambda x: -x[1])))
        if mx: print(f'   top-power share in mixed builds (prio/random/balanced): median {st.median(mx)*100:.0f}%  max {max(mx)*100:.0f}%')
        # per policy
        pol = defaultdict(list)
        for r in rs: pol[r['policy']].append(r)
        for p, prs in pol.items():
            pts2 = sorted(round(end_t(r)) for r in prs)
            e = defaultdict(float)
            for r in prs:
                s = sum(r['ST']['eff'].values()) or 1
                for k, v in r['ST']['eff'].items(): e[k] += v / s / len(prs)
            top = ' '.join(f'{k}{v*100:.0f}' for k, v in sorted(e.items(), key=lambda x: -x[1])[:4])
            print(f'     {p:9s} end {pts2}  dmg {top}')
        # hurt causes
        hc = defaultdict(float)
        for r in rs:
            for k, v in r['ST']['hurt'].items(): hc[k] += v / len(rs)
        print('   hurt/run: ' + ' '.join(f'{k} {v:.1f}' for k, v in sorted(hc.items(), key=lambda x: -x[1])[:10]))
        # bosses
        bf = [r for r in rs if r['boss'] and r['boss']['phase'] in ('fight', 'won')]
        if bf:
            for r in bf:
                b = r['ST']['boss']; s = sum(b.values()) or 1
                print(f"   dragon: seed {r['seed']} {r['policy']:8s} {'WON' if won(r) else 'died'} fight {r['boss']['t'] - 5.4:.0f}s "
                      f"hp left {r['boss']['hp'] and max(0, r['boss']['hp']):.0f}/{r['boss']['max']} seal share {b.get('seal', 0)/s*100:.0f}% "
                      f"seals {r['ST']['sealHits']} lvl {r['lvl']} W {{{', '.join(f'{k}:{v}' for k, v in r['W'].items() if v)}}}")
        gk = [r for r in rs if r['ST'].get('items', {}).get('relic')]
        if any('guard' in r['ST'] for r in rs):
            print(f"   relics picked up per run: {sum(r['ST']['items'].get('relic', 0) for r in rs)/len(rs):.2f}")
        if detail:
            for r in rs:
                print(f"     seed {r['seed']} {r['policy']} end {r['t']:.0f} lvl {r['lvl']} W {{{', '.join(f'{k}:{v}' for k, v in r['W'].items() if v)}}} picks " +
                      ' '.join(f"{p['t']:.0f}:{p['took']}" for p in r['picks']))
                for w0 in range(0, int(r['t']) + 1, 60):
                    ss = [s for s in r['samples'] if w0 < s['t'] <= w0 + 60]
                    if not ss: continue
                    dps = sum(s['dmg'] for s in ss)/len(ss); inc = sum(s['inc'] for s in ss)/len(ss)
                    print(f"        {w0:4d} lvl {ss[-1]['lvl']:2d} hp {ss[-1]['hp']:2d}/{ss[-1]['max']:2d} n {ss[-1]['n']:3d} alive {ss[-1]['alive']:6d} dps {dps:6.0f} inc {inc:6.0f} hurt {sum(s['hurt'] for s in ss):3d} gems {ss[-1]['gems']}")
    print()
