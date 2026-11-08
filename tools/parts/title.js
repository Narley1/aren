/* ---------------- title screen ---------------- */
const TT = {bgKey:'', bg:null, fg:null, clouds:null, leaves:[], birds:[], t:0, logo:null};
const hexA = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
function titleLayout(){
  const horizon = Math.round(VH*.64), forestY = Math.round(VH*.70), meadowY = Math.round(VH*.76);
  const k = Math.max(2, Math.min(4, Math.floor(VH/88)));
  return {horizon, forestY, meadowY, k, heroX:Math.round(VW*.5), heroY:Math.round(VH*.9)};
}
function buildTitleBg(){
  const L = titleLayout(), c = cnv(VW, VH), g = c.getContext('2d'), id = g.createImageData(VW, VH), a = id.data;
  const put = (x, y, col) => { if (x < 0 || y < 0 || x >= VW || y >= VH) return; const i = (y*VW + x)*4; a[i] = col[0]; a[i + 1] = col[1]; a[i + 2] = col[2]; a[i + 3] = 255; };
  /* sky: dithered bands, deep blue to pale horizon */
  const SKY = ['#2e64c4', '#3b78d6', '#4d8fe2', '#64a8ec', '#82c0f2', '#a7d6f6', '#cbe8f8', '#e6f5fa'].map(hexA);
  for (let y = 0; y < L.forestY + 4; y++) for (let x = 0; x < VW; x++){
    const t = Math.min(1, y/L.horizon), v = t*(SKY.length - 1) + BAYER4[(y & 3)*4 + (x & 3)]*.9;
    put(x, y, SKY[Math.max(0, Math.min(SKY.length - 1, Math.round(v)))]);
  }
  /* far mountains: snowy ridge, lit from the left */
  const ridge = (x, base, amp, sc, seed) => base - amp*(vnoise(x/sc + seed, seed)*.75 + vnoise(x/(sc*.35) + seed*2, seed + 3)*.25);
  const M1 = {l:hexA('#b4c0e6'), d:hexA('#8d9bd0'), s:hexA('#f2f6ff'), sd:hexA('#cdd8f2')};
  const M2 = {l:hexA('#7f99cf'), d:hexA('#6178b6'), s:hexA('#e4ecfb'), sd:hexA('#b3c3e8')};
  for (const [M, base, amp, sc, seed, snow] of [[M1, L.horizon + 2, VH*.26, 70, 11, .62], [M2, L.horizon + 6, VH*.17, 46, 27, .7]]){
    for (let x = 0; x < VW; x++){
      const top = Math.round(ridge(x, base, amp, sc, seed)), next = ridge(x + 1, base, amp, sc, seed);
      const lit = next < top + .2, peakH = base - top;
      for (let y = Math.max(0, top); y < L.forestY + 4; y++){
        const depth = y - top, snowLine = peakH*(1 - snow) + BAYER4[(y & 3)*4 + (x & 3)]*3;
        const isSnow = depth < snowLine && peakH > amp*.45;
        put(x, y, isSnow ? (lit ? M.s : M.sd) : (lit ? M.l : M.d));
      }
    }
  }
  /* forest line: rounded canopies with a sunny top edge */
  const FD = hexA('#2f6e3c'), FM = hexA('#3f8a44'), FL = hexA('#5aa84c'), FH = hexA('#86cf62');
  for (let x = -6; x < VW + 6; x += 5){
    const r = 5 + h2(x, 9)*4, cy = L.forestY - 1 + h2(x, 3)*3;
    for (let y = Math.floor(cy - r); y < L.meadowY + 2; y++) for (let xx = Math.floor(x - r); xx <= x + r; xx++){
      const dx = xx - x, dy = y - cy;
      if (dy < 0 && dx*dx + dy*dy > r*r) continue;
      const lit = dy < 0 ? (-dx*.6 - dy) / r : -1;
      put(xx, y, lit > .75 ? FH : lit > .25 ? FL : y > cy + 2 ? FD : FM);
    }
  }
  /* meadow: bright grass, lighter rise where Aren stands */
  const G1 = hexA('#6fc64c'), G2 = hexA('#5fb444'), G3 = hexA('#86d862'), GD = hexA('#4c9e3c');
  for (let y = L.meadowY; y < VH; y++) for (let x = 0; x < VW; x++){
    const t = (y - L.meadowY)/(VH - L.meadowY), b = BAYER4[(y & 3)*4 + (x & 3)];
    let col = t + b*.5 < .18 ? G2 : G1;
    const hx = (x - L.heroX)/(VW*.34), hy = (y - L.heroY)/(VH*.12);
    if (hx*hx + hy*hy < 1 + b*.15) col = G3;
    if (h2(x*3 + 1, y*5) < .02) col = GD;
    put(x, y, col);
  }
  for (let y = L.meadowY; y < L.meadowY + 2; y++) for (let x = 0; x < VW; x++) if ((x + y) % 3) put(x, y, GD);
  g.putImageData(id, 0, 0);
  /* tufts and flowers */
  const fg = cnv(VW, VH), f = fg.getContext('2d');
  const px = (gc, x, y, col) => { gc.fillStyle = col; gc.fillRect(x, y, 1, 1); };
  for (let i = 0; i < VW*1.2; i++){
    const x = (h2(i, 71)*VW) | 0, y = (L.meadowY + 4 + h2(i, 13)*(VH - L.meadowY - 6)) | 0;
    px(g, x, y, '#3f8e3a'); px(g, x - 1, y - 1, '#4c9e3c'); px(g, x + 1, y - 2, '#8ed866');
  }
  const FL_COLS = [['#ffffff', '#f2b632'], ['#ffe04a', '#e88a16'], ['#ff8ab8', '#fff0a0'], ['#9ccaff', '#ffffff']];
  for (let i = 0; i < VW*.5; i++){
    const x = (h2(i, 31)*VW) | 0, y = (L.meadowY + 6 + h2(i, 57)*(VH - L.meadowY - 14)) | 0, C = FL_COLS[(h2(i, 5)*4) | 0];
    px(g, x, y + 1, '#3a843a'); px(g, x - 1, y, C[0]); px(g, x + 1, y, C[0]); px(g, x, y - 1, C[0]); px(g, x, y, C[1]);
  }
  /* front flower bank along the bottom edge */
  for (let x = -4; x < VW + 4; x += 3){
    const y = VH - 3 - (h2(x, 2)*5 | 0);
    for (let yy = y; yy < VH; yy++){ px(f, x, yy, '#3f8e3a'); px(f, x + 1, yy, '#4c9e3c'); }
    const C = FL_COLS[x % 2 ? 0 : (h2(x, 8) < .5 ? 0 : 1)];
    px(f, x - 1, y - 1, C[0]); px(f, x + 1, y - 1, C[0]); px(f, x, y - 2, C[0]); px(f, x, y, C[0]); px(f, x, y - 1, C[1]);
  }
  TT.bg = c; TT.fg = fg;
}
function makeCloud(w, h, seed){
  const c = cnv(w, h), g = c.getContext('2d'), blobs = [];
  for (let i = 0; i < 6; i++){ const bx = w*(.15 + .7*h2(seed, i)), r = h*(.28 + .22*h2(i, seed)); blobs.push([bx, h - r - 2, r]); }
  blobs.push([w*.5, h*.55, h*.42]);
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
    let inside = false, top = false;
    for (const [bx, by, r] of blobs){ const d = Math.hypot(x - bx, y - by); if (d < r){ inside = true; if (y < by - r*.35 && x < bx) top = true; } }
    if (!inside || y > h - 3) continue;
    g.fillStyle = y > h - 6 ? '#cfe6f6' : y > h - 9 ? '#e7f4fb' : '#ffffff'; g.fillRect(x, y, 1, 1);
  }
  for (let x = 0; x < w; x++) for (let y = h - 1; y >= 0; y--){
    const p = g.getImageData(x, y, 1, 1).data; if (p[3]){ g.fillStyle = '#a9cfeb'; g.fillRect(x, y + 1, 1, 1); break; }
  }
  return c;
}
const LEAF_FR = [
  (() => { const c = cnv(5, 4), g = c.getContext('2d'); const P = (x, y, col) => { g.fillStyle = col; g.fillRect(x, y, 1, 1); };
    for (const [x, y] of [[1, 0], [2, 0], [0, 1], [1, 1], [2, 1], [3, 1], [1, 2], [2, 2], [3, 2], [4, 2], [3, 3]]) P(x, y, '#5fbf4a');
    P(1, 1, '#9ae272'); P(2, 2, '#3f8e3a'); P(3, 2, '#3f8e3a'); P(4, 3, '#2f6e2c'); return c; })(),
  (() => { const c = cnv(5, 4), g = c.getContext('2d'); g.fillStyle = '#4fa840'; g.fillRect(0, 2, 5, 1); g.fillStyle = '#86d662'; g.fillRect(1, 1, 3, 1); return c; })()
];
function titleInit(){
  const key = VW + 'x' + VH;
  if (TT.bgKey === key) return;
  TT.bgKey = key; buildTitleBg();
  if (!TT.clouds) TT.clouds = [makeCloud(70, 28, 3), makeCloud(54, 22, 9), makeCloud(90, 32, 17), makeCloud(40, 16, 23)];
  TT.leaves = Array.from({length:Math.round(VW/22)}, (_, i) => ({x:Math.random()*VW, y:Math.random()*VH, s:6 + Math.random()*10, ph:Math.random()*6, r:Math.random()*6}));
  TT.birds = Array.from({length:3}, (_, i) => ({x:-20 - i*45, y:VH*(.12 + i*.07), v:9 + i*2, ph:i}));
}
function renderTitle(dt){
  titleInit();
  TT.t += dt; const t = TT.t, L = titleLayout();
  ctx.drawImage(TT.bg, 0, 0, VW, L.horizon - VH*.2, 0, 0, VW, L.horizon - VH*.2);
  /* sun with dithered halo, top left */
  const sx = VW*.12, sy = VH*.1;
  ctx.globalAlpha = .18; pixCircle(sx, sy, VH*.16, '#fff6c8'); ctx.globalAlpha = .28; pixCircle(sx, sy, VH*.1, '#fff6c8'); ctx.globalAlpha = 1;
  pixCircle(sx, sy, VH*.055, '#fffbe6');
  /* clouds drifting behind the mountains */
  const cl = [[0, .08, 3.2], [1, .22, 4.6], [2, .36, 2.4], [3, .5, 6], [0, .3, 3.8]];
  cl.forEach(([i, yf, v], n) => { const c = TT.clouds[i], span = VW + c.width; const x = ((n*span*.37 + t*v) % span) - c.width; ctx.drawImage(c, Math.round(x), Math.round(VH*yf)); });
  /* birds */
  for (const b of TT.birds){
    b.x += b.v*dt; if (b.x > VW + 10){ b.x = -15 - Math.random()*40; b.y = VH*(.08 + Math.random()*.3); }
    const up = Math.floor(t*6 + b.ph) % 2, X = Math.round(b.x), Y = Math.round(b.y + Math.sin(t*2 + b.ph)*2);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(X, Y, 1, 1);
    if (up){ ctx.fillRect(X - 2, Y - 2, 1, 1); ctx.fillRect(X - 1, Y - 1, 1, 1); ctx.fillRect(X + 1, Y - 1, 1, 1); ctx.fillRect(X + 2, Y - 2, 1, 1); }
    else { ctx.fillRect(X - 2, Y, 1, 1); ctx.fillRect(X - 1, Y, 1, 1); ctx.fillRect(X + 1, Y, 1, 1); ctx.fillRect(X + 2, Y, 1, 1); }
    ctx.fillStyle = '#5a6a8a'; ctx.fillRect(X, Y + 1, 1, 1);
  }
  /* mountains, forest and meadow (lower part of the cached background) */
  const cut = Math.round(L.horizon - VH*.2);
  ctx.drawImage(TT.bg, 0, cut, VW, VH - cut, 0, cut, VW, VH - cut);
  /* goblins peeking from the forest edge */
  const gob = ET.goblin.dirs.down, gobS = ET.goblin.dirs.side;
  for (const [xf, dir, ph] of [[.12, 'side', 0], [.86, 'left', 1.7]]){
    const peek = Math.max(0, Math.sin(t*.7 + ph)), fr = (dir === 'left' ? ET.goblin.dirs.left : gobS)[0].n;
    const x = Math.round(VW*xf - fr.width/2), y = Math.round(L.meadowY - fr.height*.55 - peek*4);
    ctx.drawImage(fr, x, y);
  }
  /* bushes hiding the goblins' feet */
  ctx.fillStyle = '#3f8a44';
  for (const xf of [.12, .86]) for (let i = -2; i <= 2; i++) pixCircle(VW*xf + i*4, L.meadowY + 1, 4, i % 2 ? '#4fa34a' : '#3f8a44');
  /* Aren on the rise, sword raised */
  const k = L.k, H = HERO.down[0], bob = Math.floor(t*1.6) % 2;
  const hx = Math.round(L.heroX - H.width*k/2), hy = Math.round(L.heroY - H.height*k + bob*k*0);
  ctx.globalAlpha = .3; ctx.fillStyle = '#1a3a1a';
  for (let i = 0; i < 3; i++){ const w = H.width*k*(.75 - i*.12); ctx.fillRect(Math.round(L.heroX - w/2), Math.round(L.heroY - k*2 + i), Math.round(w), 1); }
  ctx.globalAlpha = 1;
  ctx.save(); ctx.translate(hx + 13.5*k, hy + 18.5*k - bob); ctx.scale(k, k);
  drawSword(0, 0, -1.05 + Math.sin(t*1.2)*.04, false); ctx.restore();
  ctx.drawImage(H, 0, 0, H.width, H.height - 6, hx, hy - bob, H.width*k, (H.height - 6)*k);
  ctx.drawImage(H, 0, H.height - 6, H.width, 6, hx, hy + (H.height - 6)*k, H.width*k, 6*k);
  /* sword glint */
  const gl = (t*.5) % 3;
  if (gl < .35){
    const a = -1.05, bx = hx + 13.5*k + Math.cos(a)*16*k, by = hy + 18.5*k - bob + Math.sin(a)*16*k, s = Math.round((1 - Math.abs(gl - .17)/.17)*3*k/2 + 1);
    ctx.fillStyle = '#ffffff'; ctx.fillRect(Math.round(bx - s), Math.round(by), s*2 + 1, 1); ctx.fillRect(Math.round(bx), Math.round(by - s), 1, s*2 + 1);
  }
  ctx.drawImage(TT.fg, 0, 0);
  /* falling leaves */
  for (const l of TT.leaves){
    l.y += l.s*dt; l.x += (-6 + Math.sin(t*1.3 + l.ph)*10)*dt; l.r += dt*3;
    if (l.y > VH + 6 || l.x < -8){ l.y = -6; l.x = Math.random()*VW*1.2; }
    ctx.drawImage(LEAF_FR[Math.floor(l.r) % 2], Math.round(l.x), Math.round(l.y));
  }
  /* soft sun shafts */
  ctx.globalCompositeOperation = 'lighter';
  for (let i = 0; i < 3; i++){
    const x0 = VW*(.05 + i*.18) + Math.sin(t*.3 + i)*4, w = VW*.06;
    ctx.globalAlpha = .045 + .02*Math.sin(t*.8 + i*2); ctx.fillStyle = '#fff3c0';
    ctx.beginPath(); ctx.moveTo(x0, 0); ctx.lineTo(x0 + w, 0); ctx.lineTo(x0 + w + VH*.55, VH); ctx.lineTo(x0 + VH*.55, VH); ctx.closePath(); ctx.fill();
  }
  ctx.globalCompositeOperation = 'source-over'; ctx.globalAlpha = 1;
}
/* logo: gold pixel lettering over a sword, with a red ribbon */
function buildLogo(){
  const W = 168, H = 82, out = cnv(W, H), g = out.getContext('2d');
  const crisp = (draw, w, h, fill) => {
    const c = cnv(w, h), cg = c.getContext('2d'); draw(cg);
    const id = cg.getImageData(0, 0, w, h), d = id.data;
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
      const i = (y*w + x)*4; if (d[i + 3] < 120){ d[i + 3] = 0; continue; }
      const col = fill(x, y); d[i] = col[0]; d[i + 1] = col[1]; d[i + 2] = col[2]; d[i + 3] = 255;
    }
    cg.putImageData(id, 0, 0); return c;
  };
  /* sword behind the letters */
  const sw = cnv(W, H), s = sw.getContext('2d'), P = (x, y, w, h, col) => { s.fillStyle = col; s.fillRect(x, y, w, h); };
  const Y = 36;
  P(26, Y - 2, 130, 5, '#dfe8f0'); P(26, Y - 2, 130, 1, '#ffffff'); P(26, Y + 2, 130, 1, '#8fa2b4'); P(28, Y, 120, 1, '#b4c4d4');
  for (let i = 0; i < 6; i++) P(156 + i, Y - 2 + Math.ceil(i/2), 1, 5 - Math.ceil(i/2)*2, i < 3 ? '#ffffff' : '#dfe8f0');
  P(20, Y - 9, 6, 19, '#f2c14e'); P(20, Y - 9, 2, 19, '#fff2a0'); P(25, Y - 9, 1, 19, '#a8781c'); P(21, Y - 1, 4, 3, '#4fa3ff'); P(22, Y - 1, 1, 1, '#d6ecff');
  P(18, Y - 11, 10, 3, '#f2c14e'); P(18, Y + 9, 10, 3, '#f2c14e'); P(18, Y - 11, 10, 1, '#fff2a0'); P(18, Y + 11, 10, 1, '#a8781c');
  P(6, Y - 2, 14, 5, '#7a4a26'); for (let x = 7; x < 20; x += 3) P(x, Y - 2, 1, 5, '#5a3418'); P(6, Y - 2, 14, 1, '#a0683a');
  P(1, Y - 3, 6, 7, '#f2c14e'); P(1, Y - 3, 6, 1, '#fff2a0'); P(1, Y + 3, 6, 1, '#a8781c');
  outlineC(sw, '#1c2430');
  g.drawImage(sw, 0, 0);
  /* two leaves on the hilt */
  const lf = LEAF_FR[0];
  g.drawImage(lf, 8, Y - 12, 7, 6); g.save(); g.translate(16, Y + 15); g.scale(-1, 1); g.drawImage(lf, -7, -6, 7, 6); g.restore();
  /* letters */
  const GOLD = ['#fff7c8', '#ffe27a', '#f2c14e', '#e8a12a', '#c8701c', '#9a4a14'].map(hexA);
  const txt = crisp(cg => { cg.font = '700 46px "Pixelify Sans", monospace'; cg.textAlign = 'center'; cg.textBaseline = 'alphabetic'; cg.fillText('AREN', W/2 + 6, 54); }, W, H,
    (x, y) => { const t = Math.max(0, Math.min(1, (y - 20)/34)); return GOLD[Math.max(0, Math.min(5, Math.floor(t*6 + BAYER4[(y & 3)*4 + (x & 3)]*.6)))]; });
  outlineC(txt, '#4a1e08'); outlineC(txt, '#2a1006');
  g.drawImage(tintC(txt, '#1a0a04'), 2, 3);
  g.drawImage(txt, 0, 0);
  /* ribbon with subtitle */
  const rb = cnv(W, H), r = rb.getContext('2d'), RP = (x, y, w, h, col) => { r.fillStyle = col; r.fillRect(x, y, w, h); };
  const ry = 62, rx0 = 30, rx1 = 144;
  RP(rx0 - 12, ry + 3, 14, 11, '#9a2a20'); RP(rx1 - 2, ry + 3, 14, 11, '#9a2a20');
  r.clearRect(rx0 - 12, ry + 6, 3, 5); r.clearRect(rx1 + 9, ry + 6, 3, 5);
  RP(rx0 - 2, ry + 11, 4, 3, '#5e1610'); RP(rx1 - 2, ry + 11, 4, 3, '#5e1610');
  RP(rx0, ry, rx1 - rx0, 13, '#c8392b'); RP(rx0, ry, rx1 - rx0, 1, '#e8644a'); RP(rx0, ry + 12, rx1 - rx0, 1, '#8e2219');
  outlineC(rb, '#2a0806');
  g.drawImage(rb, 0, 0);
  const sub = crisp(cg => { cg.font = '600 11px "Pixelify Sans", monospace'; cg.textAlign = 'center'; cg.textBaseline = 'alphabetic'; cg.fillText('o Guardião do Bosque', W/2 + 3, ry + 10); }, W, H, () => hexA('#fff1d6'));
  g.drawImage(tintC(sub, '#5e1610'), 1, 1); g.drawImage(sub, 0, 0);
  return out;
}
function placeLogo(){
  const lc = $('#logo'); if (!TT.logo) return;
  const r = app.getBoundingClientRect(), sMax = Math.min(r.width*.92/TT.logo.width, r.height*.3/TT.logo.height, 5);
  const s = Math.max(1, sMax >= 2 ? Math.floor(sMax) : sMax);
  lc.style.width = Math.round(TT.logo.width*s) + 'px'; lc.style.height = Math.round(TT.logo.height*s) + 'px';
}
function initLogo(){
  const make = () => {
    TT.logo = buildLogo(); const lc = $('#logo'); lc.width = TT.logo.width; lc.height = TT.logo.height;
    lc.getContext('2d').drawImage(TT.logo, 0, 0); placeLogo();
  };
  make();
  try { document.fonts.load('700 46px "Pixelify Sans"').then(() => document.fonts.load('600 11px "Pixelify Sans"')).then(make, () => {}); } catch {}
}
addEventListener('resize', placeLogo);
