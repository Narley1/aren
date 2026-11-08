#!/usr/bin/env python3
"""Builds an instrumented copy of the game for the balance simulator.

    python3 tests/balance/patch.py SRC OUT.html

- wraps hit(), holyStrike(), spawn() and applyItem() to count damage per power
  (effective damage = hp actually removed), seal damage, enemy hp spawned and items
  picked up, in window.__ST;
- tags the current damage source (window.__S) at the start of each weapon block in
  update() and the cause of each hurt() (window.__H);
- removes the requestAnimationFrame kick-off so nothing runs on its own, and exposes
  __d() (internals), __u(dt) (one update step + level-up), __start(), __mv(x, y)
  (virtual joystick), __pick(i) and __skipTo(t).

Anchors that are missing in a given version are reported and skipped, so the same
script works on older and newer copies of the game (only the tagging gets coarser).
"""
import re, sys

src, out = sys.argv[1], sys.argv[2]
s = open(src, encoding='utf-8').read()
missing = []

def rep(old, new, need=True):
    global s
    n = s.count(old)
    if n != 1:
        if need: raise SystemExit(f'anchor not found exactly once ({n}): {old[:70]!r}')
        missing.append(old[:50]); return
    s = s.replace(old, new)

def wrap(fn_sig_re, name, body):
    """rename `function name(` to `function __name0(` and add a wrapper before it"""
    global s
    m = re.search(fn_sig_re, s)
    if not m: raise SystemExit('function not found: ' + name)
    s = s[:m.start()] + body + '\n' + s[m.start():].replace(f'function {name}(', f'function __{name}0(', 1)

wrap(r'function hit\(e, dmg, nx, ny, kb = 70\)\{', 'hit',
     "function hit(e, dmg, nx, ny, kb){ const st = window.__ST, h0 = e.dead ? 0 : Math.max(0, e.hp), src = window.__S || '?';"
     " st.raw[src] = (st.raw[src]||0) + dmg; __hit0(e, dmg, nx, ny, kb); const eff = h0 - Math.max(0, e.hp);"
     " if (eff > 0){ st.eff[src] = (st.eff[src]||0) + eff; st.secDmg += eff; if (e.d.boss) st.boss[src] = (st.boss[src]||0) + eff;"
     " else if (e.guard) st.guard[src] = (st.guard[src]||0) + eff; } }")
wrap(r'function holyStrike\(e\)\{', 'holyStrike',
     "function holyStrike(e){ const h0 = Math.max(0, e.hp); __holyStrike0(e); const st = window.__ST; st.boss.seal = (st.boss.seal||0) + h0 - Math.max(0, e.hp); st.sealHits++; }")
wrap(r'function spawn\(type, ang, dist, elite\)\{', 'spawn',
     "function spawn(...a){ const n = E.length; __spawn0(...a); const st = window.__ST; if (st && state === 'play' && E.length > n){ const e = E[E.length - 1]; st.secSpawnHp += e.hp; st.spawnN[e.type] = (st.spawnN[e.type]||0) + 1; } }")
wrap(r'function applyItem\(kind', 'applyItem',
     "function applyItem(kind, ...r){ const st = window.__ST; st.items[kind] = (st.items[kind]||0) + 1; return __applyItem0(kind, ...r); }")

# damage source tags
rep("  // sword\n  G.swCd -= dt;", "  // sword\n  window.__S='sword'; G.swCd -= dt;")
rep("  // boomerang\n", "  // boomerang\n  window.__S='boom';\n")
rep("  // fire\n  if (W.fire){", "  // fire\n  window.__S='fire'; if (W.fire){")
rep("  // storm staff\n", "  // storm staff\n  window.__S='storm';\n")
rep("  // meteors\n", "  // meteors\n  window.__S='meteor';\n", need=False)
rep("  // orbs\n  ORBS.length = 0;", "  // orbs\n  window.__S='orb'; ORBS.length = 0;")
rep("  // player projectiles\n  for (const b of B){\n", "  // player projectiles\n  for (const b of B){\n    window.__S = b.k === 'wave' ? 'holy' : b.k;\n")
rep("  for (const z of BURNS){\n    z.t += dt; z.tick -= dt;", "  window.__S='fire'; for (const z of BURNS){\n    z.t += dt; z.tick -= dt;")
# hurt causes
rep("function hurt(n){\n  if (P.inv > 0) return;", "function hurt(n){\n  if (P.inv > 0) return;\n  { const st = window.__ST, h = window.__H || '?'; st.hurt[h] = (st.hurt[h]||0) + n; st.secHurt += n; window.__H = '?'; }")
rep("< 34) hurt(2);", "< 34){ window.__H='bossbody'; hurt(2); }", need=False)
rep("< 30) hurt(3);", "< 30){ window.__H='dive'; hurt(3); }", need=False)
rep("if (dist < d.r + 4) hurt(d.dmg);", "if (dist < d.r + 4){ window.__H = (e.guard ? 'guard:' : '') + e.type + (e.elite ? '*' : ''); hurt(d.dmg); }")
rep("b.dead = true; hurt(b.dmg); }", "b.dead = true; window.__H = b.k; hurt(b.dmg); }")
rep("P.slow = 2.6; hurt(1);", "P.slow = 2.6; window.__H='curse'; hurt(1);")
rep("< m.r + 2) hurt(2);", "< m.r + 2){ window.__H='bones'; hurt(2); }", need=False)

HOOK = r"""window.__ST = {raw:{}, eff:{}, boss:{}, guard:{}, hurt:{}, items:{}, spawnN:{}, secDmg:0, secHurt:0, secSpawnHp:0, sealHits:0};
window.__d = () => ({G, P, W, E, B, EB, ITEMS, CURSES, MARKS, GEMS, state, UPG, ET, lvlOpts, pickOptions, available, enhanceable,
  BOSSES: typeof BOSSES !== 'undefined' ? BOSSES : null, BOSS_T: typeof BOSS_T !== 'undefined' ? BOSS_T : null});
window.__u = dt => { if (state === 'play'){ update(dt); if (state === 'play' && G.pending > 0) openLevelUp(); } return state; };
window.__start = () => { start(); };
window.__mv = (ix, iy) => { J = (ix || iy) ? {id:-1, ox:0, oy:0, x:ix*40, y:iy*40} : null; };
window.__pick = i => { lvlOpenedAt = -1e9; chooseLevel(i); };
/* jump to time t; milestones before t count as done (newer versions keep the next one in G.mi) */
window.__skipTo = t => { G.t = t; if (typeof BOSSES !== 'undefined' && 'mi' in G){ G.mi = BOSSES.findIndex(b => b.t > t); if (G.mi < 0) G.mi = BOSSES.length; } };
"""
i = s.rfind('requestAnimationFrame(frame);\n})();')
if i < 0: raise SystemExit('end of IIFE not found')
s = s[:i] + HOOK + s[i + len('requestAnimationFrame(frame);\n'):]
s = '<meta charset="utf-8">\n<style>[hidden]{display:none!important}</style>\n' + s
open(out, 'w', encoding='utf-8').write(s)
print('patched', out, len(s), 'missing (skipped):', missing)
