// Injected before the page scripts: seeded Math.random + bot (pick policy + movement).
// URL params: seed, policy (prio|sword|orb|defense|balanced|random|melee|ranged|hybrid), mode (agg|kite)
(() => {
  const Q = new URLSearchParams(location.search);
  const seed = (window.__SEED = Number(Q.get('seed') || 1));
  let s = seed * 2654435761 % 4294967296 || 1;
  Math.random = () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  const policy = Q.get('policy') || 'prio', mode = Q.get('mode') || 'agg';
  // Style policies (Etapa 4): 'melee' takes only melee weapons, the Manoplas and defensive passives, 'ranged' only
  // ranged weapons, the Grimório and defensive passives; when none of the 3 options fits, they fall back to the
  // tail of the list (counted in __BOT.off). Names a version does not have are simply never offered.
  const STYLE = {
    melee:  {ok:['hammer','thorns','sword','gauntlets','holy','heart','boots','magnet'], tail:['orb','grimoire','storm','fire','boom','bow']},
    ranged: {ok:['bow','fire','boom','grimoire','storm','heart','boots','magnet'], tail:['orb','gauntlets','holy','sword','thorns','hammer']},
    // hybrid: alternates melee and ranged weapons (plus the hybrid Fogo-fátuo) and both style passives
    hybrid: {ok:['hammer','bow','orb','thorns','fire','gauntlets','grimoire','boom','holy','storm','sword','heart','boots','magnet'], tail:[]},
  };
  const PRIO = {
    melee: STYLE.melee.ok.concat(STYLE.melee.tail), ranged: STYLE.ranged.ok.concat(STYLE.ranged.tail), hybrid: STYLE.hybrid.ok,
    prio:     ['fire','boom','orb','bow','hammer','thorns','holy','storm','meteor','sword','grimoire','gauntlets','heart','boots','magnet'],
    sword:    ['sword','holy','heart','boots','orb','boom','fire','storm','meteor','magnet'],
    orb:      ['orb','boom','sword','holy','storm','meteor','fire','heart','boots','magnet'],
    defense:  ['heart','boots','sword','orb','boom','fire','holy','storm','meteor','magnet'],
    // spreads levels: lowest current level first (ties broken by this order)
    balanced: ['holy','storm','boom','fire','orb','sword','heart','magnet','boots','meteor'],
  };
  // the bot's own RNG for random picks, so pick choices do not shift the game's random stream differently per policy
  let r2 = seed * 7919 + 13;
  const rnd = () => { r2 = (r2 * 1103515245 + 12345) % 2147483648; return r2 / 2147483648; };
  window.__BOT = {policy, mode, picks:[], off:0, circA: rnd()*6.28};
  const rank = (pr, k) => { const i = pr.indexOf(k); return i < 0 ? 999 : i; };
  window.__botPick = () => {
    const d = __d(); const o = d.lvlOpts; if (!o.length) return;
    let i = 0;
    if (policy === 'random') i = Math.floor(rnd()*o.length);
    else if (policy === 'balanced'){
      const pr = PRIO.balanced, sc = k => d.W[k]*20 + pr.indexOf(k);
      for (let j = 1; j < o.length; j++) if (sc(o[j]) < sc(o[i])) i = j;
    } else {
      const pr = PRIO[policy];
      for (let j = 1; j < o.length; j++) if (rank(pr, o[j]) < rank(pr, o[i])) i = j;
    }
    if (STYLE[policy] && STYLE[policy].tail.includes(o[i])) __BOT.off++;
    __BOT.picks.push({t:+d.G.t.toFixed(1), lvl:d.G.lvl, opts:o.slice(), took:o[i]});
    __pick(i);
  };
  window.__botMove = (dt) => {
    const d = __d(), P = d.P, bot = __BOT, kite = mode === 'kite';
    let fx = 0, fy = 0, danger = 0;
    const boss = d.G.boss && d.G.boss.e;
    const lw = d.W.sword, el = 1 + (lw - 1)*1.75, B = d.BAL || {}, ga = 1 + (d.W.gauntlets || 0)*((B.gauntlets || {}).area || 0);
    // melee reach for the 'agg' (close-range) mode: sword, or most of the thorn aura / hammer ring when owned (Etapa 4)
    let swR = (17 + el*2.3 + (d.W.holy ? 8 : 0))*ga;
    if (d.W.thorns && B.thorns) swR = Math.max(swR, (B.thorns.rBase + d.W.thorns*B.thorns.rPerLvl)*ga*.85);
    if (d.W.hammer && B.hammer) swR = Math.max(swR, (B.hammer.rBase + d.W.hammer*B.hammer.rPerLvl)*ga*.6);
    const low = P.hp <= P.maxHp*.35;
    let near = null, nd = 1e9, crowd = 0;
    for (const e of d.E){
      if (e.dead || e.d.boss || e.d.mid) continue;
      const dx = P.x - e.x, dy = P.y - e.y, dist = Math.hypot(dx, dy) || 1;
      if (dist < nd){ nd = dist; near = e; }
      if (dist > 110) continue;
      if (dist < 45) crowd++;
      // the cautious bot keeps a wider berth (never walks into melee on purpose)
      // (it lets enemies walk into the sword, steps back early and never advances on them)
      const inner = e.d.r + (kite ? 6 : 7) + (low ? 10 : 0);
      if (dist < inner + 6){ const w = 4*(inner + 6 - dist)/6 + 1; fx += dx/dist*w; fy += dy/dist*w; danger += w; }
      else if (kite && dist > 60) continue;
      else { const w = .25*(e.d.r + 10)**2/(dist*dist) * (e.elite || e.guard ? 3 : 1) * (e.d.spd > 40 ? 1.5 : 1); fx += dx/dist*w; fy += dy/dist*w; danger += w*.3; }
    }
    if (!kite && near && !low && crowd < 7){
      const want = swR + near.d.r - 3;
      if (nd > want){ const w = Math.min(1.5, (nd - want)/20 + .4); fx -= (P.x - near.x)/nd*w; fy -= (P.y - near.y)/nd*w; }
    }
    // enemy projectiles: dodge perpendicular if predicted to pass close
    for (const b of d.EB){
      const rx = b.x - P.x, ry = b.y - (P.y - 10), vv = b.vx*b.vx + b.vy*b.vy;
      const tc = Math.max(0, Math.min(.7, -(rx*b.vx + ry*b.vy)/(vv || 1)));
      const cx = rx + b.vx*tc, cy = ry + b.vy*tc, cd = Math.hypot(cx, cy);
      if (cd < 16){ const w = 3*(1 - cd/16) + .5; const l = cd || 1; fx -= cx/l*w; fy -= cy/l*w; danger += w; }
    }
    for (const z of d.CURSES.concat(d.MARKS)){
      const dx = P.x - z.x, dy = P.y - z.y, dist = Math.hypot(dx, dy) || 1;
      if (dist < z.r + 10){ const w = 4; fx += dx/dist*w; fy += dy/dist*w; danger += w; }
    }
    // boss: keep distance from dragon body and dive target; go to seals; close in while it is stunned (melee window)
    if (boss){
      const dx = P.x - boss.x, dy = (P.y - 10) - (boss.y - 26), dist = Math.hypot(dx, dy) || 1;
      const s = boss.bs;
      if (s.stun > .4 && !kite){ const w = dist > swR + 10 ? 2 : 0; fx -= dx/dist*w; fy -= dy/dist*w; }
      else if (!boss.untouch && dist < 60){ fx += dx/dist*3; fy += dy/dist*3; danger += 3; }
      if (s.st === 'dive' && s.t > 1.6){ const ex = P.x - s.sx, ey = P.y - s.sy, ed = Math.hypot(ex, ey) || 1; if (ed < 45){ fx += ex/ed*6; fy += ey/ed*6; danger += 6; } }
      if (s.seals){
        let best = null, bd = 1e9;
        for (const z of s.seals){ if (z.lit) continue; const dd = Math.hypot(z.x - P.x, z.y - P.y); if (dd < bd){ bd = dd; best = z; } }
        if (best){ const k = bd < 6 ? 0 : 2.5; fx += (best.x - P.x)/(bd||1)*k; fy += (best.y - P.y)/(bd||1)*k; if (bd < 9 && danger < 2){ fx *= .1; fy *= .1; } }
      }
    }
    // mid-bosses (Etapa 5): step out of every telegraph; close-range builds go in during the boss's recovery
    // (and chase the lich), ranged builds keep 70-130 px
    for (const z of (d.ZAPS || [])){
      if (z.t < 0 || z.done) continue;
      const dx = P.x - z.x, dy = (P.y - z.y)/.75, dist = Math.hypot(dx, dy) || 1;
      if (dist < z.R + 9){ const w = 5; fx += dx/dist*w; fy += dy/dist*w; danger += w; }
    }
    const mb = d.G.guard.find(e => e.m && !e.dead);
    if (mb){
      const m = mb.m, B = d.BAL[mb.mb], dx = P.x - mb.x, dy = P.y - mb.y, dist = Math.hypot(dx, dy) || 1;
      const away = (ox, oy, w) => { const ex = P.x - ox, ey = P.y - oy, l = Math.hypot(ex, ey) || 1; fx += ex/l*w; fy += ey/l*w; danger += w; };
      const inG = (ox, oy, R) => { const ex = P.x - ox, ey = (P.y - oy)/.75; return ex*ex + ey*ey < R*R; };
      const W_ = d.W, close = policy === 'melee' || policy === 'sword' || (W_.hammer || 0) + (W_.thorns || 0) + (W_.holy ? 2 : 0) + (W_.sword >= 4 ? 1 : 0) > (W_.boom || 0) + (W_.bow || 0) + (W_.fire || 0) + (W_.storm || 0);
      let busy = false;
      if (mb.mb === 'paladin'){
        if (m.st === 'charge0' || m.st === 'charge'){
          const ca = Math.cos(m.a), sa = Math.sin(m.a), ox = m.st === 'charge' ? mb.x : m.ox, oy = m.st === 'charge' ? mb.y : m.oy, left = B.charge.len - (m.dd || 0);
          const al = (P.x - ox)*ca + (P.y - oy)*sa, pp = (P.x - ox)*-sa + (P.y - oy)*ca;
          if (al > -14 && al < left + 14 && Math.abs(pp) < B.charge.w + 10){ const sg = pp >= 0 ? 1 : -1; fx += -sa*sg*7; fy += ca*sg*7; danger += 7; }
          busy = true;
        } else if ((m.st === 'spin0' || m.st === 'spin') && inG(mb.x, mb.y, B.spin.R + 9)){ away(mb.x, mb.y, 7); busy = true; }
        else if (m.st === 'leap' && inG(m.tx, m.ty, B.leap.R + 10)){ away(m.tx, m.ty, 7); busy = true; }
        else if (m.st === 'leap0'){ away(mb.x, mb.y, 2); busy = true; }
        else if (m.st === 'intro' && mb.z > 0 && inG(mb.x, mb.y, B.intro.R + 10)){ away(mb.x, mb.y, 7); busy = true; }
        if (!busy){
          const open = m.st === 'recover';
          if (close && open){ const want = swR + B.r - 6; if (dist > want){ fx -= dx/dist*2; fy -= dy/dist*2; } }
          else if (dist < (close ? 34 : 50)) away(mb.x, mb.y, close ? 2.5 : 3);
          else if (!close && dist > 95){ fx -= dx/dist*1.2; fy -= dy/dist*1.2; }
        }
      } else {
        if (m.st === 'chain0'){
          const gx = mb.x + (mb.fc > 0 ? -14 : 14), gy = mb.y - 60, ca = Math.cos(m.a), sa = Math.sin(m.a);
          const al = (P.x - gx)*ca + (P.y - 10 - gy)*sa;
          const forks = m.ph === 2 ? [0, -B.chain.fork, B.chain.fork] : [0];
          for (const o of forks){ const c2 = Math.cos(m.a + o), s2 = Math.sin(m.a + o), pp = (P.x - gx)*-s2 + (P.y - 10 - gy)*c2, a2 = (P.x - gx)*c2 + (P.y - 10 - gy)*s2;
            if (a2 > 0 && a2 < B.chain.len && Math.abs(pp) < B.chain.w + 9 && m.t > B.chain.charge*.4){ const sg = pp >= 0 ? 1 : -1; fx += -s2*sg*6; fy += c2*sg*6; danger += 6; busy = true; } }
          void al;
        }
        if (!busy && !mb.untouch){
          if (close){ const want = Math.max(24, swR*.8 + B.r - 4); if (dist > want){ const w = m.st === 'tired' ? 2.2 : 1.4; fx -= dx/dist*w; fy -= dy/dist*w; } else if (dist < 20 && m.st !== 'tired') away(mb.x, mb.y, 2); }
          else if (dist < 50) away(mb.x, mb.y, 2); else if (dist > 95){ fx -= dx/dist*1.2; fy -= dy/dist*1.2; }
        }
      }
    }
    // items (relics and crystals always, hearts when hurt)
    for (const it of d.ITEMS){
      if (it.kind !== 'up' && it.kind !== 'relic' && P.hp >= P.maxHp) continue;
      const dx = it.x - P.x, dy = it.y - P.y, dist = Math.hypot(dx, dy) || 1;
      const R = it.kind === 'relic' ? 400 : 140;
      if (dist < R){ const w = (it.kind === 'relic' ? 2.5 : .9) / (1 + danger); fx += dx/dist*w; fy += dy/dist*w; }
    }
    // gems: drift toward the nearest gem when it is safe (a human picks them up)
    if (danger < 1.5){
      let g = null, gd = 90*90;
      for (const q of d.GEMS){ const dd = (q.x - P.x)**2 + (q.y - P.y)**2; if (dd < gd){ gd = dd; g = q; } }
      if (g){ const l = Math.sqrt(gd) || 1, w = .7/(1 + danger); fx += (g.x - P.x)/l*w; fy += (g.y - P.y)/l*w; }
    }
    // circle-kite drift
    bot.circA += dt * .45;
    const drift = boss ? .25 : kite ? .35 : .6;
    fx += Math.cos(bot.circA)*drift; fy += Math.sin(bot.circA)*drift;
    // tangential component to avoid backing into crowds
    const tx = -fy, ty = fx; fx += tx*.35; fy += ty*.35;
    const l = Math.hypot(fx, fy);
    // the cautious bot walks slowly when nothing threatens it (a human does not run circles at full speed)
    const m = kite ? Math.min(1, Math.max(.4, l*.8)) : 1;
    if (l < .05) __mv(0, 0); else __mv(fx/l*m, fy/l*m);
  };
})();
