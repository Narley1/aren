/* ================= 16-bit environment ================= */
const hexRGB = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
const GP = {
  g1:hexRGB('#72cc52'), g2:hexRGB('#64bc48'), gL:hexRGB('#98e070'), gD:hexRGB('#4c9e3c'), gDD:hexRGB('#3a843a'),
  t1:hexRGB('#4fa840'), t2:hexRGB('#5cb646'), tD:hexRGB('#3a8a36'), tL:hexRGB('#7cd25a'),
  d1:hexRGB('#e6c890'), d2:hexRGB('#d8b47a'), dD:hexRGB('#be9660'), dL:hexRGB('#f4e2b4'), dE:hexRGB('#a87e4a'), dE2:hexRGB('#c69c64')
};
function dirtN(x, y){ return vnoise(x/110 + 100, y/110 + 100)*.78 + vnoise(x/26 + 40, y/26 + 40)*.22; }
function tallN(x, y){ return vnoise(x/64 + 300, y/64 + 300)*.85 + vnoise(x/14 + 9, y/14 + 9)*.15; }
const DIRT_T = .665, TALL_T = .64;

function stamp(w, h, draw){ const c = cnv(w, h); draw(painter(c)); return c; }
const STAMPS = {
  tuft: stamp(5, 4, p => { p.px(0, 1, '#4c9e3c'); p.px(1, 2, '#4c9e3c'); p.px(2, 0, '#3a843a'); p.px(2, 1, '#4c9e3c'); p.px(2, 2, '#4c9e3c'); p.px(3, 2, '#4c9e3c'); p.px(4, 1, '#4c9e3c'); p.rect(1, 3, 3, 1, '#3a843a'); p.px(0, 0, '#98e070'); p.px(4, 0, '#98e070'); }),
  tuft2: stamp(4, 3, p => { p.px(0, 0, '#98e070'); p.px(1, 1, '#4c9e3c'); p.px(2, 0, '#4c9e3c'); p.px(3, 1, '#98e070'); p.rect(1, 2, 2, 1, '#3a843a'); }),
  clover: stamp(4, 3, p => { p.px(1, 0, '#a6e87c'); p.px(0, 1, '#a6e87c'); p.px(2, 1, '#a6e87c'); p.px(1, 1, '#5eb24a'); p.px(1, 2, '#3a843a'); p.px(3, 2, '#86d662'); }),
  fW: stamp(3, 4, p => { p.px(1, 0, '#ffffff'); p.px(0, 1, '#ffffff'); p.px(2, 1, '#ffffff'); p.px(1, 2, '#ffffff'); p.px(1, 1, '#f2b632'); p.px(1, 3, '#3a843a'); }),
  fP: stamp(3, 4, p => { p.px(1, 0, '#ffb0d0'); p.px(0, 1, '#ffb0d0'); p.px(2, 1, '#ff8ab8'); p.px(1, 2, '#ff8ab8'); p.px(1, 1, '#fff0a0'); p.px(1, 3, '#3a843a'); }),
  fY: stamp(3, 3, p => { p.px(0, 0, '#fff07a'); p.px(2, 0, '#fff07a'); p.px(1, 1, '#f2a516'); p.px(0, 2, '#fff07a'); p.px(2, 2, '#ffd84a'); }),
  fB: stamp(3, 4, p => { p.px(1, 0, '#9ccaff'); p.px(0, 1, '#9ccaff'); p.px(2, 1, '#6aa0f0'); p.px(1, 2, '#6aa0f0'); p.px(1, 1, '#ffffff'); p.px(1, 3, '#3a843a'); }),
  peb: stamp(4, 3, p => { p.rect(0, 2, 4, 1, '#4c9e3c'); p.rect(0, 0, 3, 2, '#9aa2ae'); p.px(0, 0, '#d6dce4'); p.px(2, 1, '#6c7480'); }),
  dpeb: stamp(3, 2, p => { p.rect(0, 0, 2, 1, '#cbb488'); p.px(0, 0, '#f6ead0'); p.rect(0, 1, 3, 1, '#a88454'); }),
  crack: stamp(5, 3, p => { p.px(0, 0, '#be9660'); p.px(1, 1, '#be9660'); p.px(2, 1, '#be9660'); p.px(3, 2, '#be9660'); p.px(2, 0, '#f4e2b4'); }),
  tall: stamp(7, 7, p => {
    const B = [[0, 6, 1, 2], [1, 6, 2, 0], [3, 6, 3, 1], [4, 6, 5, 0], [6, 6, 6, 2]];
    for (const [x0, y0, x1, y1] of B){ p.line(x0, y0, x1, y1, '#3a8a36'); p.px(x1, y1, '#7cd25a'); }
    p.rect(1, 6, 5, 1, '#2f7430');
  })
};
const GCH = 128, gCache = new Map();
function groundChunk(i, j){
  const key = i*100003 + j;
  let c = gCache.get(key);
  if (c){ gCache.delete(key); gCache.set(key, c); return c; }
  c = cnv(GCH, GCH); const g = c.getContext('2d'), id = g.createImageData(GCH, GCH), a = id.data;
  const ox = i*GCH, oy = j*GCH;
  for (let y = 0; y < GCH; y++) for (let x = 0; x < GCH; x++){
    const wx = ox + x, wy = oy + y, n = dirtN(wx, wy), h = h2(wx*3 + 11, wy*7 + 5);
    let col;
    if (n > DIRT_T){
      if (n < DIRT_T + .012) col = (h < .5) ? GP.dE : GP.dE2;
      else if (n < DIRT_T + .02) col = GP.dD;
      else {
        col = (vnoise(wx/18 + 7, wy/18 + 3)*.65 + vnoise(wx/7 + 2, wy/7 + 9)*.35 + (h - .5)*.12) > .6 ? GP.d2 : GP.d1;
        if (h < .035) col = GP.dD; else if (h < .07) col = GP.dL;
      }
    } else if (n > DIRT_T - .016){
      col = n > DIRT_T - .007 ? GP.gDD : ((h < .5) ? GP.gD : GP.gDD);
    } else {
      const t = tallN(wx, wy);
      if (t > TALL_T){
        const stripe = ((wx + ((wy >> 1) * 2)) % 5);
        col = t < TALL_T + .015 ? GP.gD : stripe === 0 ? GP.tD : stripe === 2 ? GP.t2 : GP.t1;
        if (h < .04) col = GP.tL;
      } else {
        const m = vnoise(wx/34 + 50, wy/34 + 80) + (h - .5)*.08;
        col = m > .52 ? GP.g1 : GP.g2;
        if (h < .018) col = GP.gL; else if (h < .036) col = GP.gD;
      }
    }
    const k = (y*GCH + x)*4; a[k] = col[0]; a[k + 1] = col[1]; a[k + 2] = col[2]; a[k + 3] = 255;
  }
  g.putImageData(id, 0, 0);
  const SG = 8;
  for (let gy = Math.floor((oy - 8)/SG); gy <= Math.floor((oy + GCH)/SG); gy++) for (let gx = Math.floor((ox - 8)/SG); gx <= Math.floor((ox + GCH)/SG); gx++){
    const r = h2(gx*13 + 7, gy*17 + 3), sx = gx*SG + Math.floor(h2(gx, gy + 51)*6), sy = gy*SG + Math.floor(h2(gx + 77, gy)*6);
    const n = dirtN(sx + 2, sy + 2);
    let st = null;
    if (n > DIRT_T + .03){ if (r < .07) st = STAMPS.dpeb; else if (r < .1) st = STAMPS.crack; }
    else if (n < DIRT_T - .03){
      const t = tallN(sx + 3, sy + 3);
      if (t > TALL_T + .02){ if (r < .75) st = STAMPS.tall; }
      else if (r < .13) st = STAMPS.tuft; else if (r < .2) st = STAMPS.tuft2; else if (r < .24) st = STAMPS.clover;
      else if (r < .29){
        const fk = vnoise(sx/90 + 500, sy/90 + 500);
        st = fk < .35 ? STAMPS.fW : fk < .55 ? STAMPS.fY : fk < .75 ? STAMPS.fP : STAMPS.fB;
      } else if (r < .3) st = STAMPS.peb;
    }
    if (st) g.drawImage(st, sx - ox, sy - oy);
  }
  /* flower patches: clusters of the same flower */
  for (let gy = Math.floor((oy - 24)/48); gy <= Math.floor((oy + GCH)/48); gy++) for (let gx = Math.floor((ox - 24)/48); gx <= Math.floor((ox + GCH)/48); gx++){
    if (h2(gx*5 + 1, gy*9 + 2) > .18) continue;
    const px0 = gx*48 + 12 + h2(gx, gy + 3)*20, py0 = gy*48 + 12 + h2(gx + 3, gy)*20;
    if (dirtN(px0, py0) > DIRT_T - .05 || tallN(px0, py0) > TALL_T) continue;
    const kind = [STAMPS.fW, STAMPS.fP, STAMPS.fY, STAMPS.fB][Math.floor(h2(gx + 9, gy + 9)*4)];
    for (let k = 0; k < 7; k++){
      const ax = px0 + (h2(gx*31 + k, gy) - .5)*22, ay = py0 + (h2(gx, gy*31 + k) - .5)*16;
      g.drawImage(kind, Math.round(ax - ox), Math.round(ay - oy));
    }
  }
  gCache.set(key, c);
  if (gCache.size > 56) gCache.delete(gCache.keys().next().value);
  return c;
}

/* ---------- props ---------- */
const LEAF = ['#2a6e34', '#3f9a45', '#5fbb4c', '#92dc62'];
const TREE16 = (() => {
  const c = cnv(36, 44), p = painter(c);
  // trunk + roots
  p.rect(14, 26, 8, 15, '#7a4a26'); p.rect(14, 26, 2, 15, '#9a6236'); p.rect(20, 26, 2, 15, '#5a3418');
  p.rect(12, 38, 12, 3, '#7a4a26'); p.px(11, 40, '#7a4a26'); p.px(24, 40, '#5a3418'); p.rect(12, 38, 2, 1, '#9a6236');
  p.px(17, 31, '#5a3418'); p.px(18, 32, '#5a3418'); p.px(16, 35, '#5a3418');
  p.rect(14, 26, 8, 3, '#3e2412');
  // canopy clumps back-to-front
  const cl = [[11, 9, 7, 6], [25, 9, 7, 6], [18, 7, 9, 7], [7, 17, 6.5, 6], [29, 17, 6.5, 6], [18, 15, 11, 8], [12, 22, 7, 5], [24, 22, 7, 5], [18, 23, 8, 5]];
  for (const [x, y, rx, ry] of cl) p.sell(x, y, rx, ry, LEAF);
  for (const [x, y] of [[12, 5], [20, 3], [8, 13], [16, 11], [26, 6], [22, 13], [10, 19], [19, 19]]){ p.rect(x, y, 2, 1, '#c0f08a'); p.px(x, y + 1, '#92dc62'); }
  for (const [x, y] of [[27, 20], [15, 25], [30, 14], [6, 21]]) p.px(x, y, '#1f5a2a');
  return outlineC(c, '#163a20');
})();
const BUSH = (berries) => { const c = cnv(20, 15), p = painter(c);
  for (const [x, y, rx, ry] of [[6, 8, 5, 4.5], [14, 8, 5, 4.5], [10, 6, 6, 5], [10, 10, 7, 3.6]]) p.sell(x, y, rx, ry, ['#2a6e34', '#3f9a45', '#5cb84a', '#8ed860']);
  if (berries) for (const [x, y] of [[6, 7], [12, 5], [15, 9], [9, 10]]){ p.px(x, y, '#e8383a'); p.px(x, y - 1, '#ffb0a0'); }
  else for (const [x, y] of [[7, 4], [12, 3]]) p.rect(x, y, 2, 1, '#b4ec80');
  return outlineC(c, '#163a20'); };
const BUSH_A = BUSH(false), BUSH_B = BUSH(true);
const ROCK16 = (() => { const c = cnv(16, 12), p = painter(c);
  p.sell(8, 6.5, 6.5, 4.8, ['#5c6270', '#8a92a0', '#b0b8c4', '#dde2ea']);
  p.px(9, 6, '#5c6270'); p.px(10, 7, '#5c6270'); p.px(5, 8, '#6c7380');
  p.rect(3, 10, 3, 1, '#4c9e3c'); p.px(12, 10, '#98e070');
  return outlineC(c, '#22262e'); })();
const STUMP = (() => { const c = cnv(14, 11), p = painter(c);
  p.rect(2, 3, 10, 6, '#7a4a26'); p.rect(2, 3, 2, 6, '#9a6236'); p.rect(10, 3, 2, 6, '#5a3418'); p.rect(1, 8, 12, 2, '#7a4a26');
  p.ell(7, 3, 5, 2, '#d8b07a'); p.ell(7, 3, 3, 1.2, '#b8894e'); p.px(7, 3, '#d8b07a');
  return outlineC(c, '#2a1810'); })();
const PROP_TYPES = {
  tree:{img:TREE16, ox:18, oy:41, sh:26},
  bush:{img:BUSH_A, ox:10, oy:13, sh:16},
  bushB:{img:BUSH_B, ox:10, oy:13, sh:16},
  rock:{img:ROCK16, ox:8, oy:10, sh:13},
  stump:{img:STUMP, ox:7, oy:9, sh:12}
};
function propsIn(x0, y0, x1, y1, out){
  const PG = 44;
  for (let by = Math.floor(y0/PG); by <= Math.floor(y1/PG); by++) for (let bx = Math.floor(x0/PG); bx <= Math.floor(x1/PG); bx++){
    const r = h2(bx*7 + 3, by*13 + 1);
    if (r > .34) continue;
    const x = bx*PG + 8 + h2(bx, by + 99)*28, y = by*PG + 8 + h2(bx + 55, by)*28;
    if (Math.abs(x) < 40 && Math.abs(y) < 40) continue;
    const n = dirtN(x, y);
    let k;
    if (n > DIRT_T - .04){ if (r < .06) k = 'rock'; else continue; }
    else k = r < .13 ? 'tree' : r < .22 ? 'bush' : r < .26 ? 'bushB' : r < .30 ? 'rock' : 'stump';
    out.push({y, k:'prop', x, t:PROP_TYPES[k]});
  }
}
