#!/usr/bin/env python3
"""Smoke test + determinism probe for Aren, o Guardião do Bosque.

Self-contained: copies src/bosque-do-enxame.html into a temp dir, injects a hook
that exposes the game's internals as window.__t (and a seeded Math.random), then
drives the game headless with Playwright/Chromium.

Runs:
  stress  -- title -> start -> ~920 s with an invulnerable hero and every power
             maxed (relics given at 300/600 s), guardians at 5:00 and 10:00, dragon
             intro/fight at 15:00, forced victory, back to title, then 3 restart
             cycles (play 30 s, die, game-over screen, title).
  milestones -- Paladino (5:00) and Lich (10:00): spawn at their time with bar and
             title card, phase 2 at 50%, death drops the relic after the collapse
             (not offered before pickup, offered after), lich skeletons and strike
             circles; the run clock is held while a mid-boss lives (no flee since
             09/11/2026), resumes after its death, and the game-over panel then
             shows the real time too; boss hp values.
  normal  -- 120 s with a simple kiting bot (hero can die).
  races   -- die / win and restart immediately: the stale game-over screen must
             not pop over the new run; keys are cleared on blur.
  ux      -- AZERTY (e.code), audio suspended when the tab is hidden, wake-lock
             race, pause dialog (role, focus trap, inert HUD), HUD button focus.

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
  keys, update, start, goTitle, togglePause, gameOver, victory, hurt, ambUpdate, hud, render, openLevelUp, startBoss, renderGear,
  pick(i){ lvlOpenedAt = -1e9; chooseLevel(i); },
  // newer names (Etapa 3); undefined in older versions
  get BOSSES(){ return typeof BOSSES !== 'undefined' ? BOSSES : null; },
  get avail(){ return typeof available === 'function' ? available : null; },
  get lvlOpts(){ return lvlOpts; },
  // Etapa 4
  get BAL(){ return typeof BAL !== 'undefined' ? BAL : null; },
  get UPG(){ return typeof UPG !== 'undefined' ? UPG : null; },
  // Etapa 5
  get ZAPS(){ return typeof ZAPS !== 'undefined' ? ZAPS : null; },
  get CORPSES(){ return typeof CORPSES !== 'undefined' ? CORPSES : null; },
  get lichStart(){ return typeof lichStart === 'function' ? lichStart : null; },
  // ambient butterflies/leaves live across runs and are topped up with Math.random by the title screen between
  // evaluates (how many frames ran depends on machine load), so the seeded runs start from an empty set
  clearAmb(){ if (typeof AMB !== 'undefined'){ AMB.bf.length = 0; AMB.lv.length = 0; AMB.t = 0; AMB.step = 0; } }
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
    # the source is a fragment: the build (and the artifact shell) add the charset and this rule
    s = '<meta charset="utf-8">\n<style>[hidden]{display:none!important}</style>\n' + s
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
  T.start(); T.clearAmb();
  const DT = 1/30;
  let maxE = 0, maxFX = 0, maxB = 0, maxEB = 0, maxGEMS = 0, maxITEMS = 0, maxNUMS = 0, picks = 0, nan = 0, steps = 0;
  let at120 = null, bossSeen = false, fightSeen = false, forced = false;
  for (const k of ['sword','boom','orb','fire','boots','magnet','hammer','thorns','bow','gauntlets','grimoire']) if (k in T.W) T.W[k] = 5;
  let guards = 0;
  for (; steps < 1100*30; steps++){
    T.P.inv = 5; T.P.hp = T.P.maxHp;
    if (T.G.t >= 300) T.W.holy = 3;
    if (T.G.t >= 600) T.W.storm = 3;
    if (T.G.guard) guards = Math.max(guards, T.G.guard.length);
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
    if (bo && bo.phase === 'fight' && T.G.t > 915 && bo.e && bo.e.hp > 1){ bo.e.hp = 1; forced = true; }
    if (T.state === 'over') break;
  }
  const bo = T.G.boss;
  Object.assign(out, {steps, t: +T.G.t.toFixed(3), state: T.state, bossSeen, guards, mi: T.G.mi, fightSeen, forced, bossPhase: bo && bo.phase,
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
  T.start(); T.clearAmb();
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

MILESTONES = r'''
(seed) => {
  const T = window.__t, r = {};
  window.__seed(seed);
  T.start();
  if (!T.BOSSES) return {skipped: true};
  T.P.inv = 1e9;
  const step = (n, f) => { for (let i = 0; i < n; i++){ T.update(1/30); if (T.G.pending) T.G.pending = 0; if (T.state !== 'play') T.state = 'play'; if (f && f()) return true; } return false; };
  r.holyBefore = T.avail().includes('holy');
  T.G.t = 299.5;
  step(30);
  const g = T.G.guard[0];
  r.guard = g ? {type: g.type, mb: g.mb, hp: Math.round(g.hp), relic: g.relic, t: +T.G.t.toFixed(2), born: +g.born.toFixed(2)} : null;
  r.hpBal = {paladin: T.BAL.paladin.hp, lich: T.BAL.lich.hp};
  r.barShown = (T.hud(), !document.querySelector('#bossBar').hidden);
  r.heldHud = {cls: document.querySelector('#timer').classList.contains('held'), label: document.querySelector('#hold').hidden ? null : document.querySelector('#hold').textContent, timer: document.querySelector('#timer').textContent};
  const clk0 = {t: T.G.t, rt: T.G.rt};
  r.barName = document.querySelector('#bossName').textContent;
  r.card = document.querySelector('#bossCard').hidden ? null : document.querySelector('#bossCard b').textContent;
  // spawning while the boss lives: count spawns over 20 s
  let spawnedCalm = 0;
  for (let i = 0; i < 20*30; i++){ const n = T.E.length; T.update(1/30); spawnedCalm += Math.max(0, T.E.length - n); if (T.G.pending) T.G.pending = 0; }
  r.spawnedCalm = spawnedCalm;
  r.clockHeld = {dt: +(T.G.t - clk0.t).toFixed(4), drt: +(T.G.rt - clk0.rt).toFixed(2), mi: T.G.mi};
  if (!g || !g.m) return r;
  // phase 2: damage stops at the threshold, the transition is invulnerable, then phase 2
  step(30*6, () => g.m.st === 'walk' || g.m.st === 'recover');
  g.hp = g.max*.5;
  step(3, () => g.m.st === 'trans');
  r.p2 = {ph: g.m.ph, st: g.m.st, untouch: g.untouch, info: (T.hud(), document.querySelector('#bossInfo').textContent)};
  step(30*3, () => g.m.st !== 'trans');
  r.p2after = {st: g.m.st, untouch: g.untouch};
  // death: the relic drops when the collapse ends, not before
  g.hp = 1;
  for (let i = 0; i < 90 && !g.dead; i++){ for (const e of T.E) if (e !== g) e.dead = true; g.x = T.P.x + 14; g.y = T.P.y; g.untouch = false; g.m.st = 'recover'; T.update(1/30); }
  r.guardDead = g.dead; r.guardsLeft = T.G.guard.length;
  const tDeath = T.G.t;
  r.corpse = T.CORPSES.length; r.relicAtDeath = T.ITEMS.some(it => it.kind === 'relic');
  T.P.x += 200;   // stay away so the relic is not picked up yet
  step(30*2.2);
  r.clockResumed = {dt: +(T.G.t - tDeath).toFixed(2), held: (T.hud(), document.querySelector('#timer').classList.contains('held')), label: !document.querySelector('#hold').hidden};
  const rel = T.ITEMS.find(it => it.kind === 'relic');
  r.relicDropped = rel ? rel.rk : null;
  r.holyAfterDropNotPicked = T.avail().includes('holy');
  if (rel){ T.P.x = rel.x; T.P.y = rel.y; T.update(1/30); }
  r.holyLevel = T.W.holy;
  r.holyAvailAfter = T.avail().includes('holy');
  r.relicGone = !T.ITEMS.some(it => it.kind === 'relic');
  // the lich at 10:00: spawns, summons skeletons that climb out of the ground, phase 2, death drops the storm relic
  T.G.t = 599.5; step(30);
  const l = T.G.guard[0];
  r.lich = l ? {mb: l.mb, relic: l.relic, hp: Math.round(l.hp), name: (T.hud(), document.querySelector('#bossName').textContent)} : null;
  if (l){
    step(30*6, () => l.m.st === 'float');
    T.lichStart(l, 'summon');
    step(30*2, () => T.E.some(e => e.type === 'skeleton'));
    const sk = T.E.filter(e => e.type === 'skeleton');
    r.skeletons = {n: sk.length, rising: sk.some(e => e.rise > 0)};
    step(30*2);
    r.skeletonsWalk = T.E.filter(e => e.type === 'skeleton' && e.rise <= 0).length;
    T.lichStart(l, 'rain'); step(30*1);
    r.zaps = T.ZAPS.length;
    l.hp = l.max*.5; step(30*4, () => l.m.ph === 2 && l.m.st === 'trans');
    r.lichP2 = l.m.ph;
    step(30*3, () => l.m.st !== 'trans');
    l.hp = 1;
    for (let i = 0; i < 90 && !l.dead; i++){ for (const e of T.E) if (e !== l) e.dead = true; l.x = T.P.x + 14; l.y = T.P.y; l.untouch = false; l.m.st = 'tired'; l.m.t = 0; l.alpha = 1; T.update(1/30); }
    T.P.x += 200; step(30*2.2);
    r.lichRelic = (T.ITEMS.find(it => it.kind === 'relic') || {}).rk || null;
  }
  // a boss kept alive for 250 real s (the old flee limit was 240) never leaves and the clock stays at 5:00;
  // dying there shows 5:00 survived plus the real time on the game-over panel
  T.start(); T.P.inv = 1e9; T.G.t = 299.5; step(30*2);
  const f = T.G.guard[0];
  if (f){
    const t0 = T.G.t, rt0 = T.G.rt;
    for (let i = 0; i < 250*15; i++){ f.hp = f.max; T.update(1/15); if (T.G.pending) T.G.pending = 0; if (T.state !== 'play') T.state = 'play'; }
    r.noFlee = {alive: !f.dead && T.G.guard.includes(f), dt: +(T.G.t - t0).toFixed(4), drt: +(T.G.rt - rt0).toFixed(1), mi: T.G.mi, relic: T.ITEMS.some(it => it.kind === 'relic'), lich: T.E.some(e => e.type === 'lich')};
    T.P.inv = 0; T.hurt(999);
    const rr = document.querySelector('#rReal');
    r.overTimes = {state: T.state, time: document.querySelector('#rTime').textContent, real: rr.hidden ? null : rr.textContent};
  }
  T.goTitle();
  return r;
}
'''

# Etapa 4 powers: each new weapon alone (plus the starting sword) must kill more than the sword alone in 40 s,
# the weapon cap must hide new weapons once full, and level-up cards must show the style pill.
POWERS = r'''
(seed) => {
  const T = window.__t, out = {kills: {}, seen: {}};
  if (!T.BAL || !T.BAL.pick || !T.BAL.pick.maxWeapons) return {skipped: true};
  for (const k of ['none', 'hammer', 'thorns', 'bow']){
    window.__seed(seed); T.start();
    if (k !== 'none') T.W[k] = 5;
    let seen = false;
    for (let i = 0; i < 40*30; i++){
      T.P.inv = 5; T.P.x = 0; T.P.y = 0; T.update(1/30); T.G.pending = 0;
      if (T.B.some(b => b.k === k) || (k === 'thorns' && T.G.thPulse > 0)) seen = true;
      if (i % 15 === 0) T.render(1/30);
    }
    out.kills[k] = T.G.kills; out.seen[k] = seen;
  }
  T.start();
  const ws = Object.keys(T.UPG).filter(k => T.UPG[k].kind === 'weapon');
  for (const k of ws.slice(0, T.BAL.pick.maxWeapons)) T.W[k] = Math.max(1, T.W[k]);
  out.capNewOffered = T.avail().filter(k => T.UPG[k].kind === 'weapon' && !T.W[k]);
  T.W[ws[ws.length - 1]] = 0; T.W[ws[1]] = 0;
  out.belowCapNewOffered = T.avail().filter(k => T.UPG[k].kind === 'weapon' && !T.W[k]).length;
  T.G.pending = 1; T.openLevelUp();
  const cards = [...document.querySelectorAll('#choices .choice')];
  out.cards = cards.length; out.cardsWithStyle = cards.filter(c => c.querySelector('.sty')).length;
  T.pick(0);
  out.powerList = document.querySelectorAll('#powerList .pw').length; out.upgCount = Object.keys(T.UPG).length;
  T.goTitle();
  return out;
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

UX = r'''
async () => {
  const T = window.__t, r = {}, $ = q => document.querySelector(q), wait = ms => new Promise(res => setTimeout(res, ms));
  // AZERTY: physical W (key 'z') moves up
  T.start();
  dispatchEvent(new KeyboardEvent('keydown', {key: 'z', code: 'KeyW'}));
  r.azertyDown = !!T.keys.w;
  dispatchEvent(new KeyboardEvent('keyup', {key: 'z', code: 'KeyW'}));
  r.azertyUp = !T.keys.w;
  // audio: suspended whenever the tab is hidden, in any state
  const calls = [];
  const sus = AudioContext.prototype.suspend, res = AudioContext.prototype.resume;
  AudioContext.prototype.suspend = function(){ calls.push('suspend'); return sus.call(this); };
  AudioContext.prototype.resume = function(){ calls.push('resume'); return res.call(this); };
  T.goTitle(); calls.length = 0;
  Object.defineProperty(document, 'hidden', {configurable: true, get: () => true});
  document.dispatchEvent(new Event('visibilitychange'));
  r.menuHiddenSuspends = calls.at(-1) === 'suspend';
  Object.defineProperty(document, 'hidden', {configurable: true, get: () => false});
  document.dispatchEvent(new Event('visibilitychange'));
  r.menuVisibleResumes = calls.at(-1) === 'resume';
  AudioContext.prototype.suspend = sus; AudioContext.prototype.resume = res;
  // wake lock granted after the run was paused must be released
  const lock = {released: false, release(){ this.released = true; return Promise.resolve(); }, addEventListener(){}};
  Object.defineProperty(navigator, 'wakeLock', {configurable: true, value: {request: () => new Promise(ok => setTimeout(() => ok(lock), 100))}});
  T.start(); T.togglePause();
  await wait(250);
  r.wakeLockReleased = lock.released;
  T.togglePause();
  // pause dialog: semantics, HUD inert
  T.togglePause();
  const pnl = $('#pauseScreen .panel');
  r.pauseDialog = pnl.getAttribute('role') === 'dialog' && pnl.getAttribute('aria-modal') === 'true';
  r.hudInert = $('#hud').inert === true;
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
            res['milestones'] = await pg.evaluate(MILESTONES, seed + 2)
            res['powers'] = await pg.evaluate(POWERS, seed + 3)
            await pg.evaluate('() => window.__t.goTitle()')
            res['normal'] = await pg.evaluate(NORMAL, seed + 1)
            await pg.evaluate('() => window.__t.goTitle()')
            res['races'] = await pg.evaluate(RACES)
            # stuck keys: hold W, blur the window -> key must be released and the game paused
            await pg.keyboard.down('w')
            await pg.evaluate('() => window.dispatchEvent(new Event("blur"))')
            res['blur'] = await pg.evaluate('() => ({w: !!window.__t.keys.w, state: window.__t.state})')
            await pg.keyboard.up('w')
            await pg.evaluate('() => window.__t.goTitle()')
            ux = await pg.evaluate(UX)
            # focus trap: Tab never leaves the pause panel
            inside = []
            for _ in range(5):
                await pg.keyboard.press('Tab')
                inside.append(await pg.evaluate('() => !!document.activeElement.closest("#pauseScreen")'))
            ux['tabTrapped'] = all(inside)
            await pg.keyboard.press('Escape')
            # HUD button clicked with the mouse loses focus; Enter afterwards must not toggle it again
            await pg.click('#musicBtn')
            m1 = await pg.evaluate('() => document.querySelector("#musicBtn").getAttribute("aria-pressed")')
            ux['hudBlurred'] = await pg.evaluate('() => document.activeElement !== document.querySelector("#musicBtn")')
            await pg.keyboard.press('Enter')
            ux['enterNoToggle'] = m1 == await pg.evaluate('() => document.querySelector("#musicBtn").getAttribute("aria-pressed")')
            await pg.click('#musicBtn')
            res['ux'] = ux
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
    m = r.get('milestones') or {}
    if not m.get('skipped'):
        g = m.get('guard') or {}
        ok('paladin: spawns at 5:00 (relic holy), boss bar + title card with its name', g.get('mb') == 'paladin' and g.get('relic') == 'holy' and abs(g.get('born', 0) - 300) < .1 and m.get('barShown') and m.get('barName') == 'Paladino Possuído' and m.get('card') == 'Paladino Possuído', json.dumps({k: m.get(k) for k in ('guard', 'barName', 'card')}))
        ok('paladin: phase 2 at 50% (invulnerable transition, HUD says it, then vulnerable again)', (m.get('p2') or {}).get('ph') == 2 and m['p2']['untouch'] and m['p2']['info'] == 'Invulnerável' and m.get('p2after', {}).get('untouch') is False, json.dumps({k: m.get(k) for k in ('p2', 'p2after')}))
        ok('paladin: death -> collapse, relic drops after it; not offered before pickup', m.get('guardDead') and m.get('corpse') == 1 and not m.get('relicAtDeath') and m.get('relicDropped') == 'holy' and not m.get('holyBefore') and not m.get('holyAfterDropNotPicked'), json.dumps({k: m.get(k) for k in ('guardDead', 'corpse', 'relicAtDeath', 'relicDropped')}))
        ok('milestones: picking the relic grants level 1 and opens it to picks', m.get('holyLevel') == 1 and m.get('holyAvailAfter') and m.get('relicGone'), json.dumps(m))
        ok('lich: spawns at 10:00 with the bar, summons rising skeletons, strike circles, phase 2, drops the storm relic', (m.get('lich') or {}).get('name') == 'Lich Ancião' and (m.get('skeletons') or {}).get('n', 0) >= 3 and m['skeletons']['rising'] and m.get('skeletonsWalk', 0) >= 3 and m.get('zaps', 0) >= 5 and m.get('lichP2') == 2 and m.get('lichRelic') == 'storm', json.dumps({k: m.get(k) for k in ('lich', 'skeletons', 'skeletonsWalk', 'zaps', 'lichP2', 'lichRelic')}))
        ch, cr, hh = m.get('clockHeld') or {}, m.get('clockResumed') or {}, m.get('heldHud') or {}
        ok('run clock held while the paladin lives (20 s: G.t still, real time runs, next boss not due), HUD shows it', ch.get('dt') == 0 and abs(ch.get('drt', 0) - 20) < .1 and ch.get('mi') == 1 and hh.get('cls') and hh.get('label') == 'Derrote o chefe!' and hh.get('timer') == '5:00', json.dumps({'clockHeld': ch, 'heldHud': hh}))
        ok('run clock resumes after the boss dies (HUD back to normal)', abs(cr.get('dt', 0) - 2.2) < .1 and not cr.get('held') and not cr.get('label'), json.dumps(cr))
        nf, ot = m.get('noFlee') or {}, m.get('overTimes') or {}
        ok('boss kept alive 250 s does not flee: clock stays, no lich, no relic', nf.get('alive') and nf.get('dt') == 0 and nf.get('drt', 0) >= 249 and nf.get('mi') == 1 and not nf.get('lich') and not nf.get('relic'), json.dumps(nf))
        ok('death during the fight: panel shows 5:00 survived and the real time', ot.get('state') == 'over' and ot.get('time') == '5:00' and (ot.get('real') or '').startswith('Tempo real: 9:'), json.dumps(ot))
        hb = m.get('hpBal') or {}
        ok('boss hp +25%: paladin 2875, lich 9500 (spawned with it)', hb.get('paladin') == 2875 and hb.get('lich') == 9500 and (m.get('guard') or {}).get('hp') == 2875 and (m.get('lich') or {}).get('hp') == 9500, json.dumps({'hpBal': hb, 'pal': (m.get('guard') or {}).get('hp'), 'lich': (m.get('lich') or {}).get('hp')}))
        ok('stress: both mid-bosses spawned (mi reached 3)', s.get('mi') == 3, f"mi={s.get('mi')} guards={s.get('guards')}")
    pw = r.get('powers') or {}
    if not pw.get('skipped'):
        kl = pw['kills']
        for k in ('hammer', 'thorns', 'bow'):
            ok(f'power {k}: works alone (more kills than the sword alone, effect seen)', kl[k] > kl['none'] and pw['seen'][k], json.dumps(pw['kills']))
        ok('weapon cap: no new weapon offered when full, offered again below the cap', not pw['capNewOffered'] and pw['belowCapNewOffered'] > 0, json.dumps(pw['capNewOffered']))
        ok('level-up cards show the style pill; power list complete', pw['cards'] > 0 and pw['cards'] == pw['cardsWithStyle'] and pw['powerList'] == pw['upgCount'], json.dumps({k: pw[k] for k in ('cards', 'cardsWithStyle', 'powerList', 'upgCount')}))
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
    u = r['ux']
    ok('AZERTY: KeyW code moves up', u['azertyDown'] and u['azertyUp'])
    ok('audio suspended when hidden in menu, resumed when visible', u['menuHiddenSuspends'] and u['menuVisibleResumes'])
    ok('wake lock granted after pause is released', u['wakeLockReleased'])
    ok('pause panel is a modal dialog, HUD inert', u['pauseDialog'] and u['hudInert'])
    ok('Tab stays inside the pause panel', u['tabTrapped'])
    ok('mouse-clicked HUD button loses focus, Enter does not re-toggle', u['hudBlurred'] and u['enterNoToggle'])
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
