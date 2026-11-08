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

/* ---------- humanoid builder: 4 walk frames x down/up/side ---------- */
function humanoid(S, dir, f){
  const c = cnv(S.W, S.H), p = painter(c);
  const cx = S.W >> 1;
  const bob = (f % 2 === 1) ? -1 : 0;
  const footY = S.H - 2, legTop = footY - S.legH + 1;
  const bodyBot = legTop - 1, bodyTop = bodyBot - S.bodyH - S.skirtH + 1;
  const hy = bodyTop - S.headH + bob + (S.headDrop || 0);
  const by = bodyTop + bob;
  const side = dir === 'side', back = dir === 'up';
  const hw = side ? S.headW - 2 : S.headW;
  const hx = side ? cx - (hw >> 1) - 1 : cx - (hw >> 1);
  const bw = side ? S.bodyW - 2 : S.bodyW, bx = cx - (bw >> 1);

  /* --- tail (behind everything) --- */
  if (S.tail){
    const t = S.tail, sw = [0, 1, 0, -1][f];
    if (side){ p.line(bx, by + S.bodyH, bx - 3, by + S.bodyH - 2 + sw, t[0]); p.rect(bx - 5, by + S.bodyH - 4 + sw, 2, 2, t[1]); p.px(bx - 4, by + S.bodyH - 5 + sw, t[1]); }
    else if (back){ p.line(cx, by + S.bodyH, cx + 2 + sw, by + S.bodyH + 3, t[0]); p.rect(cx + 2 + sw, by + S.bodyH + 3, 2, 2, t[1]); }
    else { p.line(bx + bw, by + S.bodyH, bx + bw + 2, by + S.bodyH - 3 + sw, t[0]); p.rect(bx + bw + 2, by + S.bodyH - 5 + sw, 2, 2, t[1]); p.px(bx + bw + 3, by + S.bodyH - 6 + sw, t[1]); }
  }
  /* --- elf long hair falls behind shoulders --- */
  if (S.hairStyle === 'long' && !side && back){
    p.rect(hx + 1, hy + 6, hw - 2, S.headH - 2, S.hair[1]);
  }
  /* --- far arm (side) --- */
  const armSw = [1, 0, -1, 0][f];
  if (side){
    const ax = cx - 1 - armSw;
    p.rect(ax, by + 1, 2, 3, S.cloth[0]); p.rect(ax, by + 4, 2, 1, S.skin[0]);
  }
  /* --- legs --- */
  const leg = (x, top, len, colA, colB, toe) => {
    p.rect(x, top, 2, len - 2, colA); p.rect(x, top + len - 2, 2, 2, colB);
    if (toe) p.px(x + (toe > 0 ? 2 : -1), top + len - 1, colB);
  };
  const L = S.legH;
  if (side){
    const pants = S.pants || S.skin, boots = S.boots;
    if (f === 0 || f === 2){
      const nearFwd = f === 0;
      leg(nearFwd ? cx - 4 : cx + 1, legTop, L, pants[0], boots[0], -1);           // far leg (darker)
      leg(nearFwd ? cx + 1 : cx - 4, legTop, L, pants[1] || pants[0], boots[1] || boots[0], 1);
    } else {
      leg(cx - 2, legTop - 1, L + 1, pants[0], boots[0], 0);
      leg(cx - 1, legTop - 1, L + 1, pants[1] || pants[0], boots[1] || boots[0], 1);
    }
  } else {
    const pants = S.pants || S.skin, boots = S.boots;
    const lift = [0, 1, 0, 0][f], liftR = [0, 0, 0, 1][f];
    leg(cx - 3, legTop, L - lift, pants[1] || pants[0], boots[1] || boots[0], 0);
    leg(cx + 1, legTop, L - liftR, pants[0], boots[0], 0);
  }
  /* --- body --- */
  const [cMid, cLight, cDark] = S.cloth;
  p.rect(bx, by, bw, S.bodyH, cMid);
  p.rect(bx, by, 1, S.bodyH, cLight);
  p.rect(bx + bw - 1, by, 1, S.bodyH, cDark);
  if (S.chest && !back && !side) S.chest(p, bx, by, bw, S.bodyH, cx);
  if (S.belt){ p.rect(bx, by + S.bodyH - 1, bw, 1, S.belt[0]); if (!back) p.px(side ? bx + bw - 2 : cx - 1, by + S.bodyH - 1, S.belt[1]); }
  if (S.skirtH){
    const sy = by + S.bodyH;
    p.rect(bx - 1, sy, bw + 2, S.skirtH, cMid);
    p.rect(bx - 1, sy + S.skirtH - 1, bw + 2, 1, cDark);
    for (let x = bx; x < bx + bw; x += 3) p.px(x, sy + S.skirtH - 1, cMid);
  }
  /* --- arms --- */
  if (!side){
    const ly = [0, 1, 0, -1][f], ry = -ly;
    const arm = (x, dy, shade) => {
      p.rect(x, by + 1 + dy, 2, 3, shade ? cDark : cMid); p.px(x, by + 1 + dy, shade ? cMid : cLight);
      p.rect(x, by + 4 + dy, 2, 1, shade ? S.skin[1] || S.skin[0] : S.skin[0]);
    };
    arm(bx - 2, ly, false); arm(bx + bw, ry, true);
    if (S.pads){ p.rect(bx - 2, by, 3, 2, S.pads[0]); p.rect(bx + bw - 1, by, 3, 2, S.pads[1]); p.px(bx - 2, by, S.pads[2]); }
  } else {
    const ax = cx - 1 + armSw;
    p.rect(ax, by + 1, 2, 3, cLight); p.px(ax + 1, by + 3, cMid);
    p.rect(ax + (armSw > 0 ? 1 : 0), by + 4, 2, 1, S.skin[0]);
    if (S.pads){ p.rect(cx - 2, by, 4, 2, S.pads[0]); p.px(cx - 2, by, S.pads[2]); }
  }
  /* --- scarf / collar --- */
  if (S.scarf){
    const [s0, s1] = S.scarf;
    if (side){
      p.rect(bx, by, bw, 1, s0);
      const fl = f % 2;
      p.rect(bx - 3, by + fl, 3, 1, s0); p.px(bx - 4, by + fl + 1, s1); p.px(bx - 3, by + fl + 1, s1);
    } else {
      p.rect(bx, by, bw, 1, s0); p.px(bx + bw - 1, by, s1);
      if (back){ p.rect(cx - 2, by + 1, 2, 2, s0); p.px(cx - 1, by + 3, s1); p.px(cx - 2, by + 3 - (f % 2), s1); }
      else { p.rect(bx + 1, by + 1, 1, 2, s0); p.px(bx + 1, by + 3, s1); }
    }
  }
  /* --- weapon --- */
  if (S.weapon){
    const hand = side ? [cx - 1 + armSw + 1, by + 4] : [bx + bw, by + 4 - [0, 1, 0, -1][f]];
    if (!back) S.weapon(p, hand[0], hand[1], dir);
  }
  /* --- head --- */
  const [k0, kD, kL] = S.skin;
  const headRows = S.headH;
  // base skin shape with rounded corners
  p.rect(hx + 1, hy, hw - 2, headRows, k0);
  p.rect(hx, hy + 1, hw, headRows - 2, k0);
  // shading
  if (!side){ p.rect(hx + hw - 1, hy + 2, 1, headRows - 4, kD); p.rect(hx + 2, hy + headRows - 1, hw - 4, 1, kD); }
  else { p.rect(hx + 1, hy + headRows - 1, hw - 3, 1, kD); }
  if (kL){ p.px(hx + 2, hy + 1, kL); p.px(hx + 1, hy + 2, kL); }
  // ears
  if (S.ears){
    const e = S.ears, ey = hy + (S.earY ?? 5);
    if (side){ p.px(hx + 3, ey, kD); p.px(hx + 3, ey + 1, kD); if (e === 'long' || e === 'elf'){ p.px(hx + 2, ey - 1, k0); p.px(hx + 1, ey - 2, k0); p.px(hx + 2, ey - 2, kD); } }
    else {
      const both = (fn) => { fn(1); fn(-1); };
      if (e === 'long') both(s => { const bx0 = s > 0 ? hx + hw : hx - 1; for (let i = 0; i < 3; i++){ p.px(bx0 + s*i, ey - (i >> 1), i ? k0 : kD); p.px(bx0 + s*i, ey + 1 - (i >> 1), kD); } p.px(bx0 + s*3, ey - 2, k0); });
      else if (e === 'elf') both(s => { const bx0 = s > 0 ? hx + hw : hx - 1; p.px(bx0, ey, k0); p.px(bx0, ey + 1, kD); p.px(bx0 + s, ey - 1, k0); p.px(bx0 + s, ey - 2, k0); p.px(bx0 + s, ey, kD); });
      else if (e === 'human') both(s => { const bx0 = s > 0 ? hx + hw : hx - 1; p.px(bx0, ey + 1, kD); p.px(bx0, ey + 2, kD); });
    }
  }
  // face
  if (!back){
    const eyeY = hy + (S.eyeY ?? 6);
    const eyes = side ? [hx + hw - 3] : [cx - 3, cx + 2];
    for (const ex of eyes){
      if (S.eyeWhite){ p.px(ex, eyeY, S.eyeWhite); p.px(ex, eyeY + 1, S.eye); if (!side) p.px(ex + (ex < cx ? 1 : -1), eyeY + 1, S.eye); }
      else { p.px(ex, eyeY, S.eye); p.px(ex, eyeY + 1, S.eye); }
    }
    if (S.glint){ for (const ex of eyes) p.px(ex, eyeY, S.glint); }
    if (S.blush){ if (side) p.px(hx + hw - 4, eyeY + 2, S.blush); else { p.px(cx - 4, eyeY + 2, S.blush); p.px(cx + 3, eyeY + 2, S.blush); } }
    if (S.mouth){ if (side) p.px(hx + hw - 2, eyeY + 3, S.mouth); else p.rect(cx - 1, eyeY + 3, 2, 1, S.mouth); }
    if (S.tusks){ if (side) { p.px(hx + hw - 2, eyeY + 3, S.tusks); p.px(hx + hw - 2, eyeY + 2, S.tusks); } else { p.px(cx - 2, eyeY + 2, S.tusks); p.px(cx - 2, eyeY + 3, S.tusks); p.px(cx + 1, eyeY + 2, S.tusks); p.px(cx + 1, eyeY + 3, S.tusks); } }
    if (side && S.nose) p.px(hx + hw, hy + (S.eyeY ?? 6) + 1, k0);
  }
  // hair / headgear
  const [h0, hD, hL] = S.hair || [];
  if (S.hairStyle === 'hero'){
    if (back){
      p.rect(hx + 1, hy, hw - 2, headRows - 1, h0); p.rect(hx, hy + 1, hw, headRows - 3, h0);
      p.rect(hx + hw - 1, hy + 2, 1, headRows - 4, hD); p.rect(hx + 2, hy + headRows - 2, hw - 4, 1, hD);
      p.rect(hx + 2, hy + 1, 3, 1, hL); p.px(hx + 1, hy + 2, hL);
      p.px(cx, hy - 1, h0); p.px(cx + 1, hy - 1, hD);
      for (let x = hx + 2; x < hx + hw - 2; x += 2) p.px(x, hy + headRows - 1, h0);
    } else if (side){
      p.rect(hx + 1, hy, hw - 2, 4, h0); p.rect(hx, hy + 1, 5, headRows - 3, h0);
      p.px(hx + hw - 1, hy + 2, h0); p.px(hx + hw - 2, hy + 4, h0); p.px(hx + hw - 4, hy + 4, h0); p.px(hx + 5, hy + 4, h0);
      p.rect(hx + 2, hy + 1, 4, 1, hL); p.px(hx + 1, hy + 2, hL);
      p.rect(hx, hy + headRows - 3, 3, 1, hD); p.px(hx + 4, hy + 5, hD);
      p.px(hx + 3, hy - 1, h0); p.px(hx + 4, hy - 1, hD);
      p.px(hx + 3, hy + 6, kD); p.px(hx + 3, hy + 7, kD);
    } else {
      p.rect(hx + 1, hy, hw - 2, 4, h0); p.rect(hx, hy + 1, hw, 3, h0);
      p.rect(hx, hy + 4, 2, 4, h0); p.rect(hx + hw - 2, hy + 4, 2, 4, hD);
      const fr = [1, 1, 0, 1, 1, 0, 1, 1, 0, 1];
      for (let i = 0; i < hw - 4; i++) if (fr[i]) p.px(hx + 2 + i, hy + 4, i > (hw >> 1) ? hD : h0);
      p.rect(hx + 2, hy + 1, 4, 1, hL); p.px(hx + 1, hy + 2, hL); p.px(hx + 6, hy + 1, hL);
      p.rect(hx + hw - 3, hy + 2, 2, 2, hD);
      p.px(cx - 1, hy - 1, h0); p.px(cx, hy - 1, h0); p.px(cx, hy - 2, h0);
    }
  } else if (S.hairStyle === 'long'){
    if (back){
      p.rect(hx + 1, hy, hw - 2, headRows + 1, h0); p.rect(hx, hy + 1, hw, headRows, h0);
      p.rect(hx + hw - 2, hy + 2, 2, headRows, hD); p.rect(hx + 2, hy + 1, 3, 1, hL); p.px(hx + 1, hy + 2, hL);
      p.rect(cx - 1, hy + 3, 1, headRows - 2, hD); p.rect(hx + 1, hy + headRows, hw - 2, 1, hD);
    } else if (side){
      p.rect(hx + 1, hy, hw - 2, 3, h0); p.rect(hx, hy + 1, 3, headRows + 1, h0); p.px(hx + 3, hy + 3, h0);
      p.px(hx + hw - 2, hy + 3, h0); p.rect(hx + 1, hy + headRows - 1, 2, 2, hD); p.rect(hx + 2, hy + 1, 4, 1, hL);
    } else {
      p.rect(hx + 1, hy, hw - 2, 3, h0); p.rect(hx, hy + 1, hw, 2, h0);
      p.rect(hx, hy + 3, 2, headRows - 1, h0); p.rect(hx + hw - 2, hy + 3, 2, headRows - 1, hD);
      p.px(cx - 1, hy + 3, h0); p.px(cx, hy + 3, hD);
      p.rect(hx + 2, hy + 1, 4, 1, hL); p.px(hx + 1, hy + 2, hL);
    }
  } else if (S.hairStyle === 'helmet'){
    const [m0, mD, mL] = S.helmet;
    if (side){
      p.rect(hx + 1, hy - 1, hw - 2, 5, m0); p.rect(hx, hy, hw, 3, m0); p.rect(hx, hy + 3, 4, 3, m0);
      p.rect(hx, hy + 4, hw, 1, mD); p.rect(hx + 2, hy, 4, 1, mL); p.px(hx + 5, hy + 2, mD);
    } else {
      p.rect(hx + 1, hy - 1, hw - 2, 5, m0); p.rect(hx, hy, hw, 4, m0);
      p.rect(hx, hy + 4, hw, 1, mD); p.rect(hx + 2, hy, 4, 1, mL); p.px(hx + 1, hy + 1, mL);
      p.rect(hx + hw - 2, hy + 1, 1, 3, mD);
      if (!back){ p.rect(cx - 1, hy + 5, 1, 2, mD); p.px(cx - 1, hy + 5, m0); }
      p.px(cx - 1, hy + 2, mD); p.px(cx, hy - 2, S.plume || m0); p.px(cx - 1, hy - 2, S.plume || m0);
    }
  } else if (S.hairStyle === 'tuft'){
    const top = side ? hx + 3 : cx - 2;
    p.px(top, hy - 1, h0); p.px(top + 1, hy - 1, h0); p.px(top + 1, hy - 2, h0); p.px(top + 2, hy - 1, hD);
    if (back){ p.rect(hx + 2, hy + 1, hw - 4, 1, kD); }
  }
  if (S.horns){
    const [n0, nD] = S.horns;
    const horn = (x, s) => { p.px(x, hy, n0); p.px(x, hy - 1, n0); p.px(x - s, hy - 2, n0); p.px(x - s, hy - 3, nD); p.px(x + s * 0, hy - 1, n0); p.px(x - s*2, hy - 4, nD); };
    if (side){ horn(hx + 4, 1); }
    else { horn(hx + 2, 1); horn(hx + hw - 3, -1); }
  }
  if (S.extra) S.extra(p, {dir, f, hx, hy, hw, bx, by, bw, cx});
  return outlineC(c, S.outline);
}
function buildWalker(S){
  const out = {};
  for (const dir of ['down', 'up', 'side']) out[dir] = [0, 1, 2, 3].map(f => humanoid(S, dir, f));
  out.left = out.side.map(flipC);
  return out;
}

/* ---------- weapons ---------- */
const WPN = {
  dagger(p, x, y){ p.rect(x, y - 1, 2, 2, '#6e3f1e'); p.rect(x + 1, y - 4, 1, 3, '#dfe6ee'); p.px(x + 1, y - 5, '#ffffff'); },
  axe(p, x, y){ p.rect(x + 1, y - 6, 1, 8, '#7a4a26'); p.rect(x + 2, y - 7, 2, 4, '#aeb8c4'); p.px(x + 3, y - 7, '#e8eef4'); p.px(x + 3, y - 4, '#6c7684'); },
  cleaver(p, x, y){ p.rect(x + 1, y - 1, 1, 3, '#5a3418'); p.rect(x, y - 7, 4, 6, '#9aa6b4'); p.rect(x, y - 7, 4, 1, '#e8eef4'); p.rect(x + 3, y - 6, 1, 5, '#5f6a78'); p.px(x + 1, y - 4, '#7c8794'); },
  bow(p, x, y, dir){
    if (dir === 'side'){ p.line(x + 2, y - 6, x + 3, y - 3, '#8a5328'); p.line(x + 3, y - 3, x + 3, y + 1, '#8a5328'); p.line(x + 3, y + 1, x + 2, y + 4, '#8a5328'); p.line(x + 2, y - 6, x + 2, y + 4, '#d9d2ff'); return; }
    p.line(x + 1, y - 6, x + 3, y - 3, '#8a5328'); p.line(x + 3, y - 3, x + 3, y + 1, '#8a5328'); p.line(x + 3, y + 1, x + 1, y + 4, '#8a5328'); p.line(x + 1, y - 6, x + 1, y + 4, '#d9d2ff');
  },
  claws(p, x, y){ p.px(x, y + 1, '#f2ead8'); p.px(x + 1, y + 1, '#f2ead8'); }
};

/* ---------- specs ---------- */
const HERO_SPEC = {
  W:16, H:24, headW:12, headH:11, bodyW:8, bodyH:4, skirtH:2, legH:3,
  skin:['#f8cca0', '#dc9a6c', '#fff0d8'], eye:'#22182a', glint:null, blush:'#f29a86',
  hair:['#a05a2c', '#6e3818', '#d88a4a'], hairStyle:'hero',
  cloth:['#3f86dc', '#78b4f0', '#2a5aa6'], belt:['#6e3f1e', '#f2c14e'], scarf:['#e8503a', '#a82e22'],
  pants:['#e9dcc0', '#c8b896'], boots:['#7a4422', '#5a2e16'], outline:'#2a1820'
};
const ENEMY_SPECS = {
  goblin: {W:18, H:20, headW:10, headH:9, bodyW:6, bodyH:3, skirtH:1, legH:2,
    skin:['#86c83e', '#58922a', '#b8ec78'], eye:'#2a1a08', eyeWhite:'#ffe14a', ears:'long', earY:4, eyeY:5,
    hairStyle:'tuft', hair:['#4f3a22', '#2e2214'], cloth:['#8a5a2b', '#ad7a42', '#5e3b1a'], belt:['#3e2a14', '#c9a43a'],
    pants:['#58922a', '#477a20'], boots:['#3e2a14', '#2e1e0e'], mouth:'#3a1a10', weapon:WPN.dagger, outline:'#1c2a10'},
  hobgoblin: {W:18, H:24, headW:10, headH:9, bodyW:8, bodyH:5, skirtH:1, legH:3,
    skin:['#e08040', '#a6522a', '#f6b07a'], eye:'#2a0a08', eyeWhite:'#ffffff', ears:'long', earY:5, eyeY:6,
    hairStyle:'helmet', helmet:['#8d98a6', '#555f6c', '#d2dae2'], plume:'#c83a2a',
    cloth:['#6c7a89', '#97a6b6', '#46515e'], belt:['#4a2e18', '#d8b24a'], pants:['#5a3a22', '#46301c'], boots:['#3a2618', '#2a1a10'],
    chest:(p, x, y, w, h) => { for (let yy = y + 1; yy < y + h - 1; yy++) for (let xx = x + 1; xx < x + w - 1; xx++) if ((xx + yy) % 2) p.px(xx, yy, '#7f8d9c'); },
    weapon:WPN.axe, outline:'#2a1610'},
  elf: {W:18, H:25, headW:10, headH:10, bodyW:6, bodyH:6, skirtH:2, legH:3,
    skin:['#6a5e8c', '#463c66', '#8e82b2'], eye:'#ff5ad1', glint:'#ffd0f0', ears:'elf', earY:5, eyeY:6,
    hair:['#efeaff', '#b4a8dc', '#ffffff'], hairStyle:'long',
    cloth:['#3a2458', '#5a3c86', '#221438'], belt:['#1a0e2a', '#ff5ad1'], pants:['#2a1a40', '#1e1230'], boots:['#1a0e2a', '#120a1e'],
    chest:(p, x, y, w, h, cx) => { p.line(cx - 1, y + 1, cx - 1, y + h - 2, '#7a52b0'); },
    weapon:WPN.bow, outline:'#140a22'},
  orc: {W:22, H:28, headW:12, headH:10, bodyW:12, bodyH:7, skirtH:2, legH:4,
    skin:['#6a8a3c', '#455e26', '#94b45e'], eye:'#2a0806', eyeWhite:'#ff4a2a', ears:'human', earY:4, eyeY:5, tusks:'#f6eedc',
    hairStyle:'tuft', hair:['#1e1a14', '#0e0c08'], cloth:['#5a4436', '#7a5e4a', '#3a2a20'], belt:['#2a1c12', '#c9a43a'],
    pants:['#3a2a20', '#2e2018'], boots:['#2a1c12', '#1c120a'], pads:['#8d98a6', '#5f6a78', '#d2dae2'],
    chest:(p, x, y, w, h, cx) => { p.line(x + 1, y + 1, x + w - 2, y + h - 2, '#2a1c12'); p.px(cx, y + 3, '#c9a43a'); },
    weapon:WPN.cleaver, outline:'#1a1410'},
  demon: {W:20, H:27, headW:10, headH:9, bodyW:8, bodyH:5, skirtH:1, legH:4, headDrop:0,
    skin:['#d0343e', '#8e1e2a', '#ff7a6a'], eye:'#2a0806', eyeWhite:'#ffd23a', ears:'elf', earY:4, eyeY:5, mouth:'#3a0810',
    horns:['#eadfc4', '#a8987a'], tail:['#8e1e2a', '#d0343e'],
    cloth:['#2b1627', '#4a2442', '#170b15'], belt:['#170b15', '#ffd23a'], pants:['#d0343e', '#a8283a'], boots:['#3a1018', '#2a0a10'],
    chest:(p, x, y, w, h, cx) => { p.rect(x, y, w, 2, '#d0343e'); p.px(x + w - 1, y, '#8e1e2a'); p.px(x + w - 1, y + 1, '#8e1e2a'); },
    weapon:WPN.claws, outline:'#1c0810'}
};

/* ---------- flyers ---------- */
function gargoyleSprite(flap){
  const W = 24, H = 22, c = cnv(W, H), p = painter(c), L = (a, b) => a + (b - a)*(1 - flap)/2;
  const ST = ['#4e4c5a', '#7a7886', '#a3a1ad', '#c9c7d1'], MEM = '#5f5478', MEM2 = '#463d5e', RIB = '#2e2838';
  for (const s of [-1, 1]){
    const sh = [12 + s*3, 9], el = [12 + s*7, L(3, 11)], tip = [12 + s*11, L(1, 16)], lo = [12 + s*9, L(14, 18)], in_ = [12 + s*4, 14];
    p.poly([sh, el, tip, lo, in_], MEM);
    p.poly([el, lo, in_], MEM2);
    p.line(sh[0], sh[1], el[0], el[1], RIB); p.line(el[0], el[1], tip[0], tip[1], RIB); p.line(el[0], el[1], lo[0], lo[1], RIB);
    p.px(tip[0], tip[1], '#8f8d99');
  }
  p.sell(12, 13, 4.2, 4.6, ST);
  p.rect(9, 17, 2, 3, ST[1]); p.rect(13, 17, 2, 3, ST[0]); p.px(8, 19, ST[2]); p.px(15, 19, ST[1]);
  p.sell(12, 7.5, 4, 3.6, ST);
  p.px(9, 4, ST[2]); p.px(8, 3, ST[2]); p.px(8, 2, ST[3]); p.px(15, 4, ST[1]); p.px(16, 3, ST[1]); p.px(16, 2, ST[2]);
  p.rect(10, 7, 1, 1, '#ff3b3b'); p.rect(13, 7, 1, 1, '#ff3b3b'); p.px(10, 6, '#ffb0a0'); p.px(13, 6, '#ffb0a0');
  p.rect(11, 9, 2, 1, ST[0]); p.px(11, 10, '#e8e4f0'); p.px(12, 10, '#e8e4f0');
  p.px(10, 13, ST[0]); p.px(13, 14, ST[0]); p.px(11, 15, ST[0]);
  return outlineC(c, '#191720');
}
function wyvernSprite(flap){
  const W = 36, H = 33, c = cnv(W, H), p = painter(c), L = (a, b) => a + (b - a)*(1 - flap)/2;
  const SC = ['#1e6a56', '#2f9478', '#46b896', '#7ee0bc'], BL = '#e8b46a', BLD = '#c08844', MEM = '#cf6d3a', MEMD = '#9c4a26', RIB = '#2a4a3c';
  for (const s of [-1, 1]){
    const sh = [18 + s*3, 12], el = [18 + s*10, L(3, 14)], tip = [18 + s*17, L(1, 24)];
    const f1 = [18 + s*16, L(13, 27)], f2 = [18 + s*11, L(19, 26)], in_ = [18 + s*4, 19];
    p.poly([sh, el, tip, f1, f2, in_], MEM);
    p.poly([el, f1, f2, in_], MEMD);
    p.line(sh[0], sh[1], el[0], el[1], SC[1]); p.line(sh[0], sh[1] + 1, el[0], el[1] + 1, SC[0]);
    p.line(el[0], el[1], tip[0], tip[1], RIB); p.line(el[0], el[1], f1[0], f1[1], RIB); p.line(el[0], el[1], f2[0], f2[1], RIB);
    p.px(el[0], el[1] - 1, '#f2ead8');
  }
  // tail
  const tail = [[18, 22], [19, 25], [20, 28], [19, 30]];
  for (let i = 0; i < tail.length - 1; i++){ p.line(tail[i][0], tail[i][1], tail[i + 1][0], tail[i + 1][1], SC[1]); p.line(tail[i][0] + 1, tail[i][1], tail[i + 1][0] + 1, tail[i + 1][1], SC[0]); }
  p.poly([[17, 30], [21, 29], [19, 32]], MEM);
  // body
  p.sell(18, 16, 4.6, 6.4, SC);
  p.rect(17, 13, 2, 8, BL); p.px(18, 13, BLD); for (let y = 14; y < 21; y += 2) p.px(17, y, BLD);
  p.rect(14, 20, 2, 2, SC[1]); p.rect(20, 20, 2, 2, SC[0]); p.px(13, 22, '#f2ead8'); p.px(22, 22, '#f2ead8');
  // neck + head
  p.rect(17, 7, 2, 4, SC[1]); p.px(18, 8, SC[0]);
  p.sell(18, 5.5, 3.6, 3.2, SC);
  p.px(15, 2, '#f2ead8'); p.px(14, 1, '#f2ead8'); p.px(21, 2, '#c8bea4'); p.px(22, 1, '#c8bea4');
  p.px(16, 5, '#ffcc33'); p.px(20, 5, '#ffcc33'); p.px(16, 4, '#fff2a0');
  p.rect(17, 8, 2, 1, SC[0]); p.px(17, 9, '#ffffff'); p.px(18, 9, '#ffffff');
  for (const [x, y] of [[18, 11], [18, 13], [18, 15]]) p.px(x, y - 2, SC[3]);
  return outlineC(c, '#12201c');
}
