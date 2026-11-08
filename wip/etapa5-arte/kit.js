function mk(rows, pal){
  const h = rows.length, w = rows[0].length, c = document.createElement('canvas');
  c.width = w; c.height = h; const g = c.getContext('2d');
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
    const k = rows[y][x]; if (k !== '.' && pal[k]) { g.fillStyle = pal[k]; g.fillRect(x, y, 1, 1); }
  }
  return c;
}
const OUT = '#1c1622';

/* ================= 16-bit sprite kit ================= */
function cnv(w, h){ const c = document.createElement('canvas'); c.width = w; c.height = h; return c; }
function painter(c){
  const g = c.getContext('2d');
  const o = {
    g,
    px(x, y, col){ if (!col) return; g.fillStyle = col; g.fillRect(Math.round(x), Math.round(y), 1, 1); },
    rect(x, y, w, h, col){ if (!col || w <= 0 || h <= 0) return; g.fillStyle = col; g.fillRect(Math.round(x), Math.round(y), Math.round(w), Math.round(h)); },
    ell(cx, cy, rx, ry, col){
      g.fillStyle = col;
      for (let y = Math.floor(cy - ry); y <= Math.ceil(cy + ry); y++) for (let x = Math.floor(cx - rx); x <= Math.ceil(cx + rx); x++){
        const dx = (x + .5 - cx)/rx, dy = (y + .5 - cy)/ry; if (dx*dx + dy*dy <= 1) g.fillRect(x, y, 1, 1);
      }
    },
    /* volumetric ellipse lit from top-left: cols = [dark, mid, light, highlight] */
    sell(cx, cy, rx, ry, cols, bias = 0){
      for (let y = Math.floor(cy - ry); y <= Math.ceil(cy + ry); y++) for (let x = Math.floor(cx - rx); x <= Math.ceil(cx + rx); x++){
        const dx = (x + .5 - cx)/rx, dy = (y + .5 - cy)/ry, d = dx*dx + dy*dy; if (d > 1) continue;
        const l = (-dx*.55 - dy*.75) + (1 - d)*.35 + bias;
        const col = l > .62 ? cols[3] : l > .12 ? cols[2] : l > -.38 ? cols[1] : cols[0];
        g.fillStyle = col; g.fillRect(x, y, 1, 1);
      }
    },
    poly(pts, col){
      g.fillStyle = col;
      let y0 = Infinity, y1 = -Infinity; for (const p of pts){ y0 = Math.min(y0, p[1]); y1 = Math.max(y1, p[1]); }
      for (let y = Math.floor(y0); y <= Math.ceil(y1); y++){
        const yc = y + .5, xs = [];
        for (let i = 0; i < pts.length; i++){
          const a = pts[i], b = pts[(i + 1) % pts.length];
          if ((a[1] <= yc && b[1] > yc) || (b[1] <= yc && a[1] > yc)) xs.push(a[0] + (yc - a[1])/(b[1] - a[1])*(b[0] - a[0]));
        }
        xs.sort((p, q) => p - q);
        for (let i = 0; i + 1 < xs.length; i += 2){ const xa = Math.round(xs[i]), xb = Math.round(xs[i + 1]); if (xb > xa) g.fillRect(xa, y, xb - xa, 1); }
      }
    },
    line(x0, y0, x1, y1, col){
      g.fillStyle = col; const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)) | 0;
      for (let i = 0; i <= n; i++){ const t = n ? i/n : 0; g.fillRect(Math.round(x0 + (x1 - x0)*t), Math.round(y0 + (y1 - y0)*t), 1, 1); }
    }
  };
  return o;
}
/* add a 1px outline around the silhouette */
function outlineC(c, col){
  const w = c.width, h = c.height, g = c.getContext('2d'), id = g.getImageData(0, 0, w, h), a = id.data;
  const on = (x, y) => x >= 0 && y >= 0 && x < w && y < h && a[(y*w + x)*4 + 3] > 0;
  const mark = [];
  for (let y = 0; y < h; y++) for (let x = 0; x < w; x++){
    if (on(x, y)) continue;
    if (on(x - 1, y) || on(x + 1, y) || on(x, y - 1) || on(x, y + 1)) mark.push(x, y);
  }
  g.fillStyle = col; for (let i = 0; i < mark.length; i += 2) g.fillRect(mark[i], mark[i + 1], 1, 1);
  return c;
}
function flipC(c){ const d = cnv(c.width, c.height), g = d.getContext('2d'); g.translate(c.width, 0); g.scale(-1, 1); g.drawImage(c, 0, 0); return d; }
function tintC(c, col){ const d = cnv(c.width, c.height), g = d.getContext('2d'); g.drawImage(c, 0, 0); g.globalCompositeOperation = 'source-in'; g.fillStyle = col; g.fillRect(0, 0, d.width, d.height); return d; }
// enemy frame: normal sprite + white (hit), gold (elite outline) and blue (stunned) copies, tinted on
// first use (or in idle time, see warmIdle) instead of all at boot
class EFrame {
  constructor(n){ this.n = n; this._w = this._g = this._b = null; }
  get w(){ return this._w || (this._w = tintC(this.n, '#ffffff')); }
  get g(){ return this._g || (this._g = tintC(this.n, '#ffd94a')); }
  get b(){ return this._b || (this._b = tintC(this.n, '#9fe6ff')); }
}

function gridSprite(def, dir, f){
  const V = def[dir === 'left' ? 'side' : dir], up = V.rows, LG = def.legs;
  const W = Math.max(...up.map(r => r.length)) + 2;
  const legH = LG.pr + LG.br;
  const H = up.length + legH + 3;
  const c = cnv(W, H), g = c.getContext('2d');
  const pal = def.pal;
  const put = (x, y, ch) => { const col = pal[ch]; if (!col) return; g.fillStyle = col; g.fillRect(x, y, 1, 1); };
  const bob = (f % 2 === 1) ? 1 : 0;
  const oy = 2 - bob, ox = 1;
  const side = dir === 'side' || dir === 'left';
  const legTop = 2 + up.length;
  /* legs (behind body) */
  const leg = (x, top, bottom, a, b, toe) => {
    for (let y = top; y <= bottom; y++){
      const boot = y > bottom - LG.br;
      for (let k = 0; k < LG.w; k++) put(ox + x + k, y, boot ? (k === LG.w - 1 ? LG.bs : LG.b) : (k === LG.w - 1 ? LG.ps : LG.p));
    }
    if (toe) put(ox + x + (toe > 0 ? LG.w : -1), bottom, LG.b);
  };
  const bottom = legTop + legH - 1;
  if (!side){
    const top = legTop - bob;
    leg(LG.xL, top, bottom - (f === 1 ? 1 : 0), 0, 0, 0);
    leg(LG.xR, top, bottom - (f === 3 ? 1 : 0), 0, 0, 0);
  } else {
    const c0 = LG.xs, sp = LG.spread || 2, L = legH;
    const slant = (sgn, isFar) => {
      for (let k = 0; k < L; k++){
        const y = legTop + k, off = Math.round(k/(L - 1)*sp)*sgn, boot = k >= L - LG.br;
        for (let q = 0; q < LG.w; q++){
          const ch = boot ? (isFar || q === LG.w - 1 ? LG.bs : LG.b) : (isFar || q === LG.w - 1 ? LG.ps : LG.p);
          put(ox + c0 + off + q, y, ch);
        }
        if (k === L - 1) put(ox + c0 + off + LG.w, y, isFar ? LG.bs : LG.b);
      }
    };
    if (f === 0){ slant(-1, true); slant(1, false); }
    else if (f === 2){ slant(1, true); slant(-1, false); }
    else {
      const top = legTop - 1;
      for (let y = top; y <= bottom; y++){ const boot = y > bottom - LG.br; for (let q = 0; q < LG.w; q++){ put(ox + c0 - 1 + q, y, boot ? LG.bs : LG.ps); put(ox + c0 + q, y, boot ? (q === LG.w - 1 ? LG.bs : LG.b) : (q === LG.w - 1 ? LG.ps : LG.p)); } }
      put(ox + c0 + LG.w, bottom, LG.b);
    }
  }
  /* upper body */
  for (let y = 0; y < up.length; y++){ const row = up[y]; for (let x = 0; x < row.length; x++) if (row[x] !== '.') put(ox + x, oy + y, row[x]); }
  /* swinging near arm for side views */
  if (side && V.arm){
    const A = V.arm, dx = [-1, 0, 1, 0][f];
    for (let y = 0; y < A.rows.length; y++) for (let x = 0; x < A.rows[y].length; x++) if (A.rows[y][x] !== '.') put(ox + A.x + x + dx, oy + A.y + y, A.rows[y][x]);
  }
  /* front-view hand bob */
  if (!side && V.hands){
    for (const [hx, hy, ch, ph] of V.hands){ const d = [0, ph, 0, -ph][f]; if (d) { put(ox + hx, oy + hy + d, ch); } }
  }
  outlineC(c, def.outline);
  return dir === 'left' ? flipC(c) : c;
}
function buildGrid(def){
  const out = {};
  for (const dir of ['down', 'up', 'side', 'left']) out[dir] = [0, 1, 2, 3].map(f => gridSprite(def, dir, f));
  return out;
}
