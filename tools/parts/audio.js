/* ---------------- sound ---------------- */
const SFX = (() => {
  let ac = null, master, sfxDry, sfxWet, musDry, musWet, rev, noiseBuf, VW8 = null;
  let on = true, musicOn = true;
  try { on = localStorage.getItem('bosque-enxame-som') !== '0'; musicOn = localStorage.getItem('bosque-enxame-musica') !== '0'; } catch {}
  const last = {};
  const curve = k => { const n = 1024, c = new Float32Array(n); for (let i = 0; i < n; i++){ const x = i/n*2 - 1; c[i] = (1 + k)*x/(1 + k*Math.abs(x)); } return c; };
  function impulse(sec, decay){
    const len = Math.floor(ac.sampleRate*sec), b = ac.createBuffer(2, len, ac.sampleRate);
    for (let ch = 0; ch < 2; ch++){ const d = b.getChannelData(ch); for (let i = 0; i < len; i++) d[i] = (Math.random()*2 - 1)*Math.pow(1 - i/len, decay); }
    return b;
  }
  function init(){
    if (ac){ if (ac.state === 'suspended') ac.resume().catch(() => {}); return; }
    try { ac = new (window.AudioContext || window.webkitAudioContext)(); } catch { ac = null; return; }
    master = ac.createGain(); master.gain.value = .9;
    const comp = ac.createDynamicsCompressor(); comp.threshold.value = -14; comp.ratio.value = 5; comp.attack.value = .004; comp.release.value = .25;
    master.connect(comp); comp.connect(ac.destination);
    rev = ac.createConvolver(); rev.buffer = impulse(2.8, 2.6); rev.connect(master);
    sfxDry = ac.createGain(); sfxDry.gain.value = on ? .8 : 0; sfxDry.connect(master);
    sfxWet = ac.createGain(); sfxWet.gain.value = on ? .8 : 0; sfxWet.connect(rev);
    musDry = ac.createGain(); musDry.gain.value = musicOn ? .34 : 0; musDry.connect(master);
    musWet = ac.createGain(); musWet.gain.value = musicOn ? .34 : 0; musWet.connect(rev);
    noiseBuf = ac.createBuffer(1, ac.sampleRate*2, ac.sampleRate);
    const d = noiseBuf.getChannelData(0); for (let i = 0; i < d.length; i++) d[i] = Math.random()*2 - 1;
    const n = 48, re = new Float32Array(n), im = new Float32Array(n);
    for (let k = 1; k < n; k++) im[k] = Math.pow(k, -1.15)*(k % 2 ? 1 : .8);
    VW8 = ac.createPeriodicWave(re, im);
    setInterval(musicTick, 40);
  }
  const ready = (key, cd, force) => {
    if (!ac || !on || ac.state !== 'running') return false;
    const t = ac.currentTime; if (!force && last[key] && t - last[key] < cd) return false; last[key] = t; return true;
  };
  const G_ = v => { const g = ac.createGain(); g.gain.value = v; return g; };
  const filt = (type, f, q, gain) => { const b = ac.createBiquadFilter(); b.type = type; b.frequency.value = f; if (q) b.Q.value = q; if (gain !== undefined) b.gain.value = gain; return b; };
  const env = (g, t0, a, peak, dur) => { g.gain.setValueAtTime(.0001, t0); g.gain.exponentialRampToValueAtTime(Math.max(.0002, peak), t0 + a); g.gain.exponentialRampToValueAtTime(.0001, t0 + Math.max(a + .01, dur)); };
  const noise = (t0, dur) => { const n = ac.createBufferSource(); n.buffer = noiseBuf; n.start(t0, Math.random()*1.5); n.stop(t0 + dur + .05); return n; };
  const route = (node, wet, dry = sfxDry, wetBus = sfxWet) => { node.connect(dry); if (wet){ const w = G_(wet); node.connect(w); w.connect(wetBus); } };

  /* ---------- voice: glottal source + formants ---------- */
  const VOW = {
    a:[[730, 1, 90], [1090, .55, 110], [2440, .3, 160], [3400, .12, 200]],
    e:[[530, 1, 70], [1840, .5, 100], [2480, .35, 150], [3500, .12, 200]],
    i:[[300, 1, 50], [2300, .5, 100], [3000, .38, 140], [3700, .15, 200]],
    o:[[570, 1, 80], [840, .6, 90], [2410, .2, 160], [3300, .08, 200]],
    u:[[300, 1, 60], [870, .4, 90], [2240, .12, 150], [3200, .05, 200]]
  };
  function formants(dest, t, v0, v1, shift, morph){
    const inp = G_(1), A = VOW[v0], B = VOW[v1 || v0];
    for (let k = 0; k < 4; k++){
      const bp = filt('bandpass', A[k][0]*shift, A[k][0]/A[k][2]);
      if (v1){ bp.frequency.setValueAtTime(A[k][0]*shift, t); bp.frequency.linearRampToValueAtTime(B[k][0]*shift, t + morph); }
      const g = G_(A[k][1]*4); inp.connect(bp); bp.connect(g); g.connect(dest);
    }
    return inp;
  }
  function syl(dest, t, o){
    const {f0, f1 = f0*.9, dur = .12, vow = 'a', vow2, morph = .06, asp = .04, aspAmp = .5, amp = 1, vib = 0, vibR = 6, shift = 1, breath = .1} = o;
    const fb = formants(dest, t, vow, vow2, shift, morph);
    const tv = t + asp;
    const src = ac.createOscillator(); src.setPeriodicWave(VW8);
    src.frequency.setValueAtTime(f0, tv); src.frequency.exponentialRampToValueAtTime(f1, tv + dur);
    if (vib){ const l = ac.createOscillator(), lg = G_(f0*vib); l.frequency.value = vibR; l.connect(lg); lg.connect(src.frequency); l.start(tv); l.stop(tv + dur + .1); }
    const g = ac.createGain(); g.gain.setValueAtTime(.0001, tv); g.gain.exponentialRampToValueAtTime(amp, tv + .018); g.gain.setValueAtTime(amp, tv + dur*.45); g.gain.exponentialRampToValueAtTime(.0001, tv + dur);
    src.connect(g); g.connect(fb); src.start(tv); src.stop(tv + dur + .05);
    const n = noise(t, asp + dur), ng = ac.createGain();
    ng.gain.setValueAtTime(.0001, t); ng.gain.exponentialRampToValueAtTime(aspAmp, t + Math.max(.01, asp*.6)); ng.gain.exponentialRampToValueAtTime(Math.max(.0002, breath*amp), tv + .02); ng.gain.exponentialRampToValueAtTime(.0001, tv + dur);
    const hp = filt('highpass', 500); n.connect(hp); hp.connect(ng); ng.connect(fb);
  }

  /* ---------- DEMON: deep, distorted "MUAH-HA-HA-HA-HA" ---------- */
  function demonLaugh(){
    if (!ready('demon', 4.5)) return;
    const t0 = ac.currentTime + .03, bus = G_(.55);
    const ws = ac.createWaveShaper(); ws.curve = curve(5); ws.oversample = '2x';
    const lp = filt('lowpass', 2600, .7);
    const rm = ac.createGain(); rm.gain.value = 0; const car = ac.createOscillator(); car.frequency.value = 47; const cg = G_(1); car.connect(cg); cg.connect(rm.gain); car.start(t0); car.stop(t0 + 2);
    bus.connect(ws); ws.connect(lp); bus.connect(rm); const rmg = G_(.6); rm.connect(rmg); rmg.connect(lp);
    route(lp, .45);
    const base = 88 + Math.random()*10, sh = .8;
    syl(bus, t0, {f0:base*1.05, f1:base*1.3, dur:.34, vow:'u', vow2:'a', morph:.12, asp:.01, aspAmp:.05, amp:.9, vib:.02, vibR:5, shift:sh, breath:.12});
    const seq = [1.32, 1.22, 1.13, 1.03, .94, .85];
    seq.forEach((m, i) => syl(bus, t0 + .44 + i*.17, {f0:base*m, f1:base*m*.84, dur:.12, vow:'a', asp:.05, aspAmp:.7, amp:.95 - i*.1, shift:sh, breath:.2}));
    const sub = ac.createOscillator(); sub.type = 'sine'; sub.frequency.setValueAtTime(base/2, t0); sub.frequency.linearRampToValueAtTime(base*.4, t0 + 1.5);
    const sg = ac.createGain(); env(sg, t0, .08, .35, 1.55); sub.connect(sg); route(sg, .2); sub.start(t0); sub.stop(t0 + 1.6);
    const n = noise(t0 + 1.4, .5), nl = filt('lowpass', 500), ng = ac.createGain(); env(ng, t0 + 1.4, .05, .3, .5); n.connect(nl); nl.connect(ng); route(ng, .4);
  }
  /* ---------- SUCCUBUS: breathy feminine "hi-hi-hi-hi... mmm" + sparkle ---------- */
  function succubusLaugh(){
    if (!ready('succ', 3)) return;
    const t0 = ac.currentTime + .03, bus = G_(.42), hs = filt('highshelf', 3000, 0, 4);
    const dl = ac.createDelay(); dl.delayTime.value = .15; const fbk = G_(.28); bus.connect(hs); hs.connect(dl); dl.connect(fbk); fbk.connect(dl);
    route(hs, .5); const dlo = G_(.35); dl.connect(dlo); route(dlo, .5);
    const base = 340 + Math.random()*40, seq = [1.02, 1.14, 1.22, 1.18, 1.08, .98];
    seq.forEach((m, i) => syl(bus, t0 + i*.112, {f0:base*m*1.04, f1:base*m*.94, dur:.07, vow:i === 0 ? 'e' : 'i', asp:.035, aspAmp:.9, amp:[.55, .65, .7, .66, .58, .45][i], vib:.012, vibR:8, shift:1.14, breath:.45}));
    syl(bus, t0 + .74, {f0:base*.92, f1:base*.7, dur:.48, vow:'u', vow2:'e', morph:.3, asp:.06, aspAmp:.35, amp:.32, vib:.02, vibR:5, shift:1.1, breath:.3});
    [1568, 1976, 2349, 2794, 3136].forEach((f, i) => {
      const t = t0 + .05 + i*.08, o = ac.createOscillator(), g = ac.createGain(); o.type = 'sine'; o.frequency.value = f;
      env(g, t, .004, .07, .5); o.connect(g); route(g, .9); o.start(t); o.stop(t + .55);
    });
  }
  /* curse circle bursting */
  function hex(){
    if (!ready('hex', .3)) return;
    const t = ac.currentTime + .01, n = noise(t, .6), bp = filt('bandpass', 600, 3), g = ac.createGain();
    bp.frequency.setValueAtTime(400, t); bp.frequency.exponentialRampToValueAtTime(3200, t + .25); env(g, t, .02, .4, .5); n.connect(bp); bp.connect(g); route(g, .6);
    for (const f of [587, 740, 880]){ const o = ac.createOscillator(), og = ac.createGain(); o.type = 'triangle'; o.frequency.setValueAtTime(f*1.5, t); o.frequency.exponentialRampToValueAtTime(f, t + .3); env(og, t, .01, .12, .7); o.connect(og); route(og, .7); o.start(t); o.stop(t + .75); }
  }

  /* ---------- SKELETON DRAGON: hollow bone roar, jaw clatter, ghost wail ---------- */
  function boneKnock(t, f, amp, dest){
    const o = ac.createOscillator(), g = ac.createGain(); o.type = 'triangle'; o.frequency.setValueAtTime(f*1.25, t); o.frequency.exponentialRampToValueAtTime(f, t + .02);
    env(g, t, .002, amp, .07); o.connect(g); g.connect(dest); o.start(t); o.stop(t + .1);
    const n = noise(t, .02), bp = filt('bandpass', f*3, 4), ng = ac.createGain(); env(ng, t, .001, amp*.8, .025); n.connect(bp); bp.connect(ng); ng.connect(dest);
  }
  function clatter(t0, count, span, amp){ const d = G_(1); route(d, .4); for (let i = 0; i < count; i++) boneKnock(t0 + (i/count)*span + Math.random()*.02, [520, 640, 760, 900, 1100][(Math.random()*5) | 0], amp*(1 - i/count*.5), d); }
  function wail(t, len, f, amp){
    const out = ac.createGain(); env(out, t, len*.35, amp, len); const bp = filt('bandpass', f*1.5, 1.2); out.connect(bp); route(bp, .9);
    for (const dt of [0, 7]){ const o = ac.createOscillator(); o.type = 'sine'; o.detune.value = dt*2;
      o.frequency.setValueAtTime(f, t); o.frequency.linearRampToValueAtTime(f*1.12, t + len*.3); o.frequency.exponentialRampToValueAtTime(f*.62, t + len);
      const l = ac.createOscillator(), lg = G_(f*.025); l.frequency.value = 4.3; l.connect(lg); lg.connect(o.frequency); l.start(t); l.stop(t + len + .1);
      o.connect(out); o.start(t); o.stop(t + len + .1); }
  }
  function roar({len = 1.2, pitch = 1, vol = .9, force = false} = {}){
    if (!ready('roar', .45, force)) return;
    const t = ac.currentTime + .02;
    clatter(t, 7, .22, .35);
    const out = ac.createGain(); env(out, t + .15, .1, vol, len);
    const comb = ac.createDelay(); comb.delayTime.value = .0065/pitch; const cfb = G_(.62); const cl = filt('lowpass', 1800);
    out.connect(comb); comb.connect(cfb); cfb.connect(cl); cl.connect(comb);
    const mix = G_(1); out.connect(mix); comb.connect(mix);
    const lp = filt('lowpass', 900, 3); lp.frequency.setValueAtTime(500, t); lp.frequency.linearRampToValueAtTime(1600, t + len*.3); lp.frequency.exponentialRampToValueAtTime(300, t + len);
    mix.connect(lp); route(lp, .6);
    const ws = ac.createWaveShaper(); ws.curve = curve(12); ws.connect(out);
    for (const dt of [-22, 0, 17]){
      const o = ac.createOscillator(); o.type = 'sawtooth'; o.detune.value = dt;
      o.frequency.setValueAtTime(58*pitch, t + .15); o.frequency.linearRampToValueAtTime(110*pitch, t + .15 + len*.25); o.frequency.exponentialRampToValueAtTime(38*pitch, t + len);
      const am = ac.createGain(); am.gain.value = .5; const l = ac.createOscillator(), lg = G_(.45); l.frequency.value = 29; l.connect(lg); lg.connect(am.gain); l.start(t); l.stop(t + len + .2);
      o.connect(am); am.connect(ws); o.start(t + .15); o.stop(t + len + .2);
    }
    const n = noise(t + .15, len), bp = filt('bandpass', 700, .8), ng = ac.createGain(); env(ng, t + .15, .06, .6, len*.9);
    bp.frequency.setValueAtTime(450, t); bp.frequency.linearRampToValueAtTime(1300, t + len*.3); bp.frequency.linearRampToValueAtTime(380, t + len);
    n.connect(bp); bp.connect(ng); ng.connect(out);
    wail(t + .2, len*1.1, 470*Math.sqrt(pitch), .1*vol);
  }
  function fireBreath(len = 1.4){
    if (!ready('breath', .5)) return;
    const t = ac.currentTime + .01, n = noise(t, len), lp = filt('lowpass', 900, 1), g = ac.createGain();
    lp.frequency.setValueAtTime(2600, t); lp.frequency.exponentialRampToValueAtTime(500, t + len);
    env(g, t, .08, .6, len); n.connect(lp); lp.connect(g); route(g, .5);
    wail(t, len, 620, .09);
    for (let i = 0; i < 10; i++){ const tt = t + Math.random()*len, c = noise(tt, .015), ch = filt('highpass', 2500), cg = ac.createGain(); env(cg, tt, .001, .25, .02); c.connect(ch); ch.connect(cg); route(cg, .2); }
  }
  function whoosh(len = 2.2){
    if (!ready('whoosh', .5)) return;
    const t = ac.currentTime + .01, n = noise(t, len), bp = filt('bandpass', 400, 2.5), g = ac.createGain();
    for (let i = 0; i < 4; i++){ const tt = t + i*len/4; bp.frequency.setValueAtTime(260, tt); bp.frequency.exponentialRampToValueAtTime(1400, tt + len/8); bp.frequency.exponentialRampToValueAtTime(260, tt + len/4); }
    env(g, t, .2, .5, len); n.connect(bp); bp.connect(g); route(g, .4);
    wail(t + .3, len*.8, 380, .06);
  }
  function thud(){
    if (!ready('thud', .2)) return;
    const t = ac.currentTime + .01, o = ac.createOscillator(), g = ac.createGain();
    o.type = 'sine'; o.frequency.setValueAtTime(90, t); o.frequency.exponentialRampToValueAtTime(26, t + .5);
    env(g, t, .005, 1, .6); o.connect(g); route(g, .3); o.start(t); o.stop(t + .65);
    const n = noise(t, .35), lp = filt('lowpass', 700), ng = ac.createGain(); env(ng, t, .005, .6, .35); n.connect(lp); lp.connect(ng); route(ng, .3);
    clatter(t + .08, 12, .7, .3);
  }
  function rattle(){ if (!ready('rattle', .25)) return; clatter(ac.currentTime + .01, 16, .6, .4); }
  function dragonDeath(){
    if (!ac || !on) return;
    roar({len:3, pitch:.5, vol:1, force:true});
    const t = ac.currentTime + .4; wail(t, 3.2, 520, .14); clatter(t + 1.2, 40, 2.2, .45);
  }
  function giggle(kind){ if (kind === 'succubus') succubusLaugh(); else demonLaugh(); }

  /* ================= MUSIC: ocarina, flute, lute ================= */
  const mtof = m => 440*Math.pow(2, (m - 69)/12);
  const NN = {C:0, 'C#':1, Db:1, D:2, 'D#':3, Eb:3, E:4, F:5, 'F#':6, Gb:6, G:7, 'G#':8, Ab:8, A:9, 'A#':10, Bb:10, B:11};
  const midi = s => { const m = s.match(/^([A-G][#b]?)(\d)$/); return 12*(+m[2] + 1) + NN[m[1]]; };
  function ocarina(t, m, dur, vel){
    const f = mtof(m), out = ac.createGain(), lp = filt('lowpass', 3400, .5);
    out.gain.setValueAtTime(.0001, t); out.gain.exponentialRampToValueAtTime(vel*.5, t + .045); out.gain.exponentialRampToValueAtTime(vel*.4, t + .16);
    out.gain.setValueAtTime(vel*.4, t + Math.max(.17, dur)); out.gain.exponentialRampToValueAtTime(.0001, t + dur + .14);
    const l = ac.createOscillator(), vd = ac.createGain(); l.frequency.value = 5.3; vd.gain.setValueAtTime(0, t); vd.gain.linearRampToValueAtTime(0, t + .22); vd.gain.linearRampToValueAtTime(f*.007, t + .5); l.connect(vd);
    for (const [type, mul, amp] of [['sine', 1, 1], ['triangle', 1, .16], ['sine', 2, .05]]){ const o = ac.createOscillator(), g = G_(amp); o.type = type; o.frequency.value = f*mul; vd.connect(o.frequency); o.connect(g); g.connect(out); o.start(t); o.stop(t + dur + .2); }
    l.start(t); l.stop(t + dur + .2);
    const n = noise(t, .07), bp = filt('bandpass', f*2, 3), ng = ac.createGain(); env(ng, t, .005, vel*.09, .07); n.connect(bp); bp.connect(ng); ng.connect(out);
    out.connect(lp); route(lp, .4, musDry, musWet);
  }
  function flute(t, m, dur, vel, trem){
    const f = mtof(m), out = ac.createGain(), atk = .12;
    out.gain.setValueAtTime(.0001, t); out.gain.exponentialRampToValueAtTime(vel*.32, t + atk);
    out.gain.setValueAtTime(vel*.32, t + Math.max(atk + .01, dur)); out.gain.exponentialRampToValueAtTime(.0001, t + dur + .25);
    const l = ac.createOscillator(), vd = G_(f*(trem ? .02 : .005)); l.frequency.value = trem ? 7 : 4.8; l.connect(vd);
    for (const [mul, amp] of [[1, 1], [2, .22], [3, .06]]){ const o = ac.createOscillator(), g = G_(amp); o.type = 'sine'; o.frequency.value = f*mul; vd.connect(o.frequency); o.connect(g); g.connect(out); o.start(t); o.stop(t + dur + .3); }
    l.start(t); l.stop(t + dur + .3);
    const n = noise(t, dur + .25), bp = filt('bandpass', f*1.02, 1.6), ng = G_(vel*.05); n.connect(bp); bp.connect(ng); ng.connect(out);
    route(out, .5, musDry, musWet);
  }
  const KS = {};
  function ksBuf(m){
    if (KS[m]) return KS[m];
    const sr = ac.sampleRate, N = Math.max(2, Math.round(sr/mtof(m))), len = Math.floor(sr*1.9), b = ac.createBuffer(1, len, sr), d = b.getChannelData(0);
    const ring = new Float32Array(N); for (let i = 0; i < N; i++) ring[i] = Math.random()*2 - 1;
    for (let p = 0; p < 2; p++) for (let i = 1; i < N; i++) ring[i] = ring[i]*.55 + ring[i - 1]*.45;
    const dec = .9965 - Math.max(0, m - 55)*.00035; let idx = 0, mx = 0;
    for (let i = 0; i < len; i++){ const a = ring[idx], nb = ring[(idx + 1) % N]; d[i] = a; mx = Math.max(mx, Math.abs(a)); ring[idx] = (a + nb)*.5*dec; idx = (idx + 1) % N; }
    for (let i = 0; i < len; i++) d[i] /= (mx || 1);
    return KS[m] = b;
  }
  function lute(t, m, vel, pan = 0){
    const s = ac.createBufferSource(); s.buffer = ksBuf(m);
    const body = filt('peaking', 230, 1.2, 6), lp = filt('lowpass', 3800, .6), g = G_(vel*.42), p = ac.createStereoPanner ? ac.createStereoPanner() : null;
    s.connect(body); body.connect(lp); lp.connect(g);
    let o = g; if (p){ p.pan.value = pan; g.connect(p); o = p; }
    route(o, .25, musDry, musWet); s.start(t); s.stop(t + 1.9);
  }
  function drum(t, k){
    const P = {low:[100, 46, .3, .85, 380], mid:[170, 95, .16, .45, 1100], soft:[170, 95, .12, .22, 1100], boom:[66, 30, .75, 1, 220]}[k];
    const o = ac.createOscillator(), g = ac.createGain(); o.type = 'sine'; o.frequency.setValueAtTime(P[0], t); o.frequency.exponentialRampToValueAtTime(P[1], t + P[2]);
    env(g, t, .003, P[3], P[2] + .05); o.connect(g); route(g, .2, musDry, musWet); o.start(t); o.stop(t + P[2] + .1);
    const n = noise(t, .06), bp = filt('bandpass', P[4], 1.2), ng = ac.createGain(); env(ng, t, .002, P[3]*.3, .06); n.connect(bp); bp.connect(ng); route(ng, .2, musDry, musWet);
  }
  let drone = null;
  function droneStart(t){
    if (drone) return;
    const out = ac.createGain(); out.gain.setValueAtTime(.0001, t); out.gain.exponentialRampToValueAtTime(.16, t + 2.5);
    const lp = filt('lowpass', 260, 3), l = ac.createOscillator(), lg = G_(120); l.frequency.value = .13; l.connect(lg); lg.connect(lp.frequency); l.start(t);
    const os = [38, 45, 50].map((m, i) => { const o = ac.createOscillator(); o.type = 'sawtooth'; o.frequency.value = mtof(m); o.detune.value = (i - 1)*6; o.connect(lp); o.start(t); return o; });
    lp.connect(out); route(out, .5, musDry, musWet);
    drone = {out, os:[...os, l]};
  }
  function droneStop(t){
    if (!drone) return; const d = drone; drone = null;
    d.out.gain.cancelScheduledValues(t); d.out.gain.setValueAtTime(Math.max(.0001, d.out.gain.value), t); d.out.gain.exponentialRampToValueAtTime(.0001, t + 1.5);
    for (const o of d.os) o.stop(t + 1.6);
  }
  const CH = {D:[50, 54, 57], G:[43, 47, 50], Bm:[47, 50, 54], A:[45, 49, 52], 'F#m':[42, 45, 49], Dm:[50, 53, 57], C:[48, 52, 55], Bb:[46, 50, 53], Eb:[51, 55, 58], Em:[52, 55, 59]};
  const mel = bars => bars.map(b => { const out = {}; let st = 0; for (const [n, beats] of b){ if (n !== 'r') out[st] = [midi(n), beats*4]; st += Math.round(beats*4); } return out; });
  const SONGS = {
    calm:{bpm:84, chords:['D', 'G', 'Bm', 'A', 'D', 'G', 'A', 'D', 'G', 'A', 'F#m', 'Bm', 'G', 'A', 'D', 'D'], lute:'arp8', flute:'pad', drum:null,
      mel:mel([
        [['F#5', 1], ['A5', 1], ['D6', 2]], [['B5', 1.5], ['A5', .5], ['G5', 2]], [['F#5', 1], ['E5', 1], ['D5', 1], ['F#5', 1]], [['E5', 3], ['r', 1]],
        [['F#5', 1], ['A5', 1], ['D6', 1.5], ['E6', .5]], [['D6', 1], ['B5', 1], ['G5', 2]], [['A5', 1], ['G5', .5], ['F#5', .5], ['E5', 1], ['C#5', 1]], [['D5', 3], ['r', 1]],
        [['B4', 1], ['D5', 1], ['G5', 2]], [['A5', 1.5], ['G5', .5], ['E5', 2]], [['F#5', 1], ['A5', 1], ['C#6', 1], ['A5', 1]], [['B5', 3], ['r', 1]],
        [['G5', 1], ['B5', 1], ['D6', 1], ['B5', 1]], [['C#6', 1], ['B5', .5], ['A5', .5], ['E5', 2]], [['F#5', 1], ['E5', .5], ['D5', .5], ['A4', 1], ['D5', 1]], [['D5', 3], ['r', 1]]])},
    combat:{bpm:104, chords:['Dm', 'C', 'Bb', 'A', 'Dm', 'C', 'Bb', 'A'], lute:'arp16', flute:'double', drum:'combat',
      mel:mel([
        [['D5', .5], ['F5', .5], ['A5', 1], ['G5', .5], ['F5', .5], ['E5', 1]], [['C5', .5], ['E5', .5], ['G5', 1], ['F5', .5], ['E5', .5], ['D5', 1]],
        [['D5', .5], ['F5', .5], ['Bb5', 1], ['A5', .5], ['G5', .5], ['F5', 1]], [['E5', 1], ['C#5', 1], ['A4', 2]],
        [['A5', 1], ['D6', 1], ['C6', .5], ['Bb5', .5], ['A5', 1]], [['G5', 1], ['C6', 1], ['Bb5', .5], ['A5', .5], ['G5', 1]],
        [['F5', 1], ['Bb5', 1], ['A5', .5], ['G5', .5], ['F5', .5], ['E5', .5]], [['E5', 2], ['C#5', 1], ['E5', 1]]])},
    boss:{bpm:112, chords:['Dm', 'Eb', 'Dm', 'Eb', 'Bb', 'A', 'Dm', 'A'], lute:'trem', flute:'low', drum:'boss', drone:true,
      mel:mel([
        [['D5', 1], ['Eb5', 1], ['D5', .5], ['C5', .5], ['D5', 1]], [['G5', 1.5], ['F5', .5], ['Eb5', 2]],
        [['A5', 1], ['G5', .5], ['F5', .5], ['Eb5', 1], ['D5', 1]], [['Eb5', 1], ['G5', 1], ['Bb5', 2]],
        [['D6', 1], ['C6', .5], ['Bb5', .5], ['A5', 1], ['G5', 1]], [['A5', 2], ['C#6', 1], ['E6', 1]],
        [['D6', 1.5], ['C6', .5], ['Bb5', 1], ['A5', 1]], [['A5', 3], ['r', 1]]])}
  };
  SONGS.boss2 = Object.assign({}, SONGS.boss, {bpm:132, drum:'boss2'});
  const DRUMS = {combat:{0:'low', 6:'mid', 8:'low', 12:'mid', 14:'soft'}, boss:{0:'boom', 3:'mid', 6:'mid', 8:'low', 10:'mid', 12:'low', 14:'mid'},
    boss2:{0:'boom', 2:'soft', 3:'mid', 4:'low', 6:'mid', 8:'boom', 10:'mid', 11:'soft', 12:'low', 14:'mid', 15:'soft'}};
  const M = {mood:null, next:0, step:0, bar:0, song:null, fn:null, hold:0};
  function setMood(m, t){
    M.mood = m; M.bar = 0; M.song = SONGS[m] || null;
    if (M.song && M.song.drone) droneStart(t); else droneStop(t);
  }
  function playStep(t){
    const S = M.song, s = M.step, bi = M.bar % S.chords.length, ch = CH[S.chords[bi]], spb = 60/S.bpm/4;
    const [r, th, fi] = ch;
    const mb = S.mel[M.bar % S.mel.length], mn = mb[s];
    if (mn) ocarina(t, mn[0], mn[1]*spb*.92, M.mood === 'calm' ? .72 : .82);
    if (S.lute === 'arp8'){ if (s % 2 === 0){ const seq = [r, fi, r + 12, th + 12, fi + 12, th + 12, r + 12, fi]; lute(t, seq[s/2], s % 8 === 0 ? .9 : .6, (s % 4 ? .25 : -.25)); } }
    else if (S.lute === 'arp16'){ const seq = [r, fi, r + 12, fi, th + 12, fi, r + 12, fi]; lute(t, seq[s % 8], s % 4 === 0 ? .85 : .45, s % 2 ? .3 : -.3); if (s === 0) lute(t, r - 12, .7); }
    else if (S.lute === 'trem'){ lute(t, s % 2 ? fi + 12 : r + 12, s % 4 === 0 ? .7 : .35, s % 2 ? .35 : -.35); if (s === 0 || s === 8) lute(t, r - 12, .9); }
    if (S.flute === 'pad' && s === 0){
      if (M.bar % 16 >= 8) flute(t, th + 24, 16*spb*.95, .55);
      else if (M.bar % 4 === 3) flute(t, fi + 12, 16*spb*.9, .45);
    } else if (S.flute === 'double'){ if (mn) flute(t, mn[0] - 12, mn[1]*spb*.9, .38); }
    else if (S.flute === 'low' && s === 0) flute(t, r + 12, 16*spb*.98, .6, true);
    if (S.drum){ const k = DRUMS[S.drum][s]; if (k) drum(t, k); }
  }
  function musicTick(){
    if (!ac || ac.state !== 'running') return;
    const now = ac.currentTime;
    if (M.next < now) M.next = now + .05;
    while (M.next < now + .3){
      const want = M.fn ? M.fn() : 'calm';
      if (M.step === 0 && want !== M.mood){
        const urgent = !M.mood || want === 'silent' || M.mood === 'silent' || want.startsWith('boss') || M.mood.startsWith('boss');
        if (urgent || M.bar % 4 === 0) setMood(want, M.next);
      }
      const bpm = M.song ? M.song.bpm : 90;
      if (M.song && musicOn) playStep(M.next);
      M.next += 60/bpm/4; M.step = (M.step + 1) % 16; if (M.step === 0) M.bar++;
    }
  }
  function stinger(kind){
    if (!ac || !musicOn || ac.state !== 'running') return;
    const t = ac.currentTime + .1;
    if (kind === 'win'){
      [['D5', 0], ['F#5', .14], ['A5', .28], ['D6', .42]].forEach(([n, d]) => ocarina(t + d, midi(n), .16, .85));
      ocarina(t + .6, midi('A5'), .35, .85); ocarina(t + 1, midi('D6'), 1.4, .9);
      for (const n of ['D3', 'A3', 'D4', 'F#4', 'A4']) lute(t + .6 + Math.random()*.05, midi(n), .7);
      flute(t + .6, midi('F#5'), 1.8, .5);
    } else {
      [['A5', 0, .5], ['G5', .5, .5], ['F5', 1, .5], ['E5', 1.5, .5], ['D5', 2, 1.8]].forEach(([n, d, l]) => flute(t + d, midi(n), l, .55));
      lute(t + 2, midi('D3'), .8); lute(t + 2.05, midi('A3'), .6); lute(t + 2.1, midi('F4'), .5);
    }
  }
  function setOn(v){ on = v; try { localStorage.setItem('bosque-enxame-som', v ? '1' : '0'); } catch {} if (sfxDry){ sfxDry.gain.value = v ? .8 : 0; sfxWet.gain.value = v ? .8 : 0; } }
  function setMusic(v){ musicOn = v; try { localStorage.setItem('bosque-enxame-musica', v ? '1' : '0'); } catch {} if (musDry){ musDry.gain.value = v ? .34 : 0; musWet.gain.value = v ? .34 : 0; } }
  function pause(p){ if (!ac) return; if (p) ac.suspend().catch(() => {}); else ac.resume().catch(() => {}); }
  function moodFn(fn){ M.fn = fn; }
  return {init, roar, fireBreath, whoosh, thud, rattle, giggle, hex, dragonDeath, stinger, setOn, setMusic, pause, moodFn,
    get on(){ return on; }, get music(){ return musicOn; }};
})();

