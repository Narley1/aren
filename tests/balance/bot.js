// Injected before the page scripts: seeded Math.random + bot (pick policy + movement).
// URL params: seed, policy (prio|sword|orb|defense|balanced|random), mode (agg|kite)
(() => {
  const Q = new URLSearchParams(location.search);
  const seed = (window.__SEED = Number(Q.get('seed') || 1));
  let s = seed * 2654435761 % 4294967296 || 1;
  Math.random = () => { s ^= s << 13; s >>>= 0; s ^= s >> 17; s ^= s << 5; s >>>= 0; return s / 4294967296; };
  const policy = Q.get('policy') || 'prio', mode = Q.get('mode') || 'agg';
  const PRIO = {
    prio:     ['fire','boom','orb','holy','storm','meteor','sword','heart','boots','magnet'],
    sword:    ['sword','holy','heart','boots','orb','boom','fire','storm','meteor','magnet'],
    orb:      ['orb','boom','sword','holy','storm','meteor','fire','heart','boots','magnet'],
    defense:  ['heart','boots','sword','orb','boom','fire','holy','storm','meteor','magnet'],
    // spreads levels: lowest current level first (ties broken by this order)
    balanced: ['holy','storm','boom','fire','orb','sword','heart','magnet','boots','meteor'],
  };
  // the bot's own RNG for random picks, so pick choices do not shift the game's random stream differently per policy
  let r2 = seed * 7919 + 13;
  const rnd = () => { r2 = (r2 * 1103515245 + 12345) % 2147483648; return r2 / 2147483648; };
  window.__BOT = {policy, mode, picks:[], circA: rnd()*6.28};
  window.__botPick = () => {
    const d = __d(); const o = d.lvlOpts; if (!o.length) return;
    let i = 0;
    if (policy === 'random') i = Math.floor(rnd()*o.length);
    else if (policy === 'balanced'){
      const pr = PRIO.balanced, sc = k => d.W[k]*20 + pr.indexOf(k);
      for (let j = 1; j < o.length; j++) if (sc(o[j]) < sc(o[i])) i = j;
    } else {
      const pr = PRIO[policy];
      for (let j = 1; j < o.length; j++) if (pr.indexOf(o[j]) < pr.indexOf(o[i])) i = j;
    }
    __BOT.picks.push({t:+d.G.t.toFixed(1), lvl:d.G.lvl, opts:o.slice(), took:o[i]});
    __pick(i);
  };
  window.__botMove = (dt) => {
    const d = __d(), P = d.P, bot = __BOT, kite = mode === 'kite';
    let fx = 0, fy = 0, danger = 0;
    const boss = d.G.boss && d.G.boss.e;
    const lw = d.W.sword, el = 1 + (lw - 1)*1.75, swR = 17 + el*2.3 + (d.W.holy ? 8 : 0);
    const low = P.hp <= P.maxHp*.35;
    let near = null, nd = 1e9, crowd = 0;
    for (const e of d.E){
      if (e.dead || e.d.boss) continue;
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
