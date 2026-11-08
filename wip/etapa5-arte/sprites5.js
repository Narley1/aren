/* ================= Etapa 5 bosses: Paladino Possuído, Lich Ancião ================= */
/* Possessed paladin: hollow plate armour (tarnished steel, gold trim), tattered crimson cape and plume,
   kite shield on the image right (flipped to face Aren). Poses: 'walk' (f = 0..3), 'brace' (shield forward,
   crouched: charge), 'raise' (sword arm up: spin wind-up, blades), 'crouch' (knees bent: before a leap / after
   landing), 'spin' (arms out). The greatsword is a separate pre-rotated sprite (PAL_SWORD) drawn at PAL_HAND[pose]. */
const PAL_W = 46, PAL_H = 60;
const PAL_HAND = {walk:[9, 37], brace:[13, 36], raise:[11, 13], crouch:[12, 41], spin:[6, 32]};
function paladinBody(pose, f){
  const c = cnv(PAL_W, PAL_H), p = painter(c);
  const ST = ['#373c4a', '#5e6676', '#959eae', '#d2d9e3'], TN = '#6a6250', TD = '#4a4438';
  const GD = ['#5e3e10', '#a07018', '#d6a636', '#f6dc78'], CP = ['#2a0c1a', '#48182c', '#6c2840'];
  const HOL = '#110916', WIS = '#6a3a9a', LTH = '#3a2416';
  const walk = pose === 'walk', low = pose === 'brace' ? 3 : pose === 'crouch' ? 4 : 0;
  const bob = walk && (f === 1 || f === 3) ? 1 : 0, Y = low + bob;   // upper body drop
  const sway = walk ? [0, 1, 0, -1][f] : pose === 'brace' ? 2 : 0;
  /* cape (behind): from the shoulders to a ragged hem */
  const hem = 50 - Math.min(low, 2);
  p.poly([[13, 21 + Y], [33, 21 + Y], [37 + sway, hem - 4], [9 + sway, hem - 4]], CP[1]);
  for (let x = 9; x <= 37; x++){
    const d = Math.round(h2(x*7, 3)*4), yy = hem - 4 + d + (x % 3 === 0 ? 2 : 0);
    p.rect(x + sway, hem - 4, 1, yy - hem + 5, CP[1]);
    if (x % 4 === 1) p.rect(x + sway, hem - 7, 1, yy - hem + 6, CP[0]);
  }
  p.rect(11, 24 + Y, 3, 18, CP[2]); p.rect(33, 24 + Y, 2, 16, CP[0]);
  /* legs: greaves, knee cops, sabatons */
  const legTop = 41 + Y, footY = 55;
  const lift = walk ? [[0, 0], [2, 0], [0, 0], [0, 2]][f] : [0, 0];
  const legX = pose === 'crouch' || pose === 'brace' ? [14, 27] : [16, 26];
  for (let i = 0; i < 2; i++){
    const x = legX[i], bot = footY - lift[i], top = legTop;
    p.rect(x, top, 5, bot - top - 2, ST[1]); p.rect(x, top, 2, bot - top - 2, ST[2]); p.rect(x + 4, top, 1, bot - top - 2, ST[0]);
    p.px(x + 1, top + 1, ST[3]);
    const ky = top + Math.round((bot - top)*.35);
    p.sell(x + 2.5, ky, 3.2, 2.2, ST); p.px(x + 2, ky - 1, GD[3]);
    p.rect(x - (i ? 0 : 1), bot - 2, 6 + 1, 3, ST[1]); p.rect(x - (i ? 0 : 1), bot - 2, 7, 1, ST[2]); p.px(i ? x + 6 : x - 1, bot, ST[0]);
    p.rect(x + 1, ky + 3, 3, 1, HOL);
  }
  /* faulds (plated skirt) with gold hem */
  p.poly([[14, 35 + Y], [32, 35 + Y], [34, 42 + Y], [12, 42 + Y]], ST[1]);
  for (const x of [17, 21, 25, 29]) p.rect(x, 36 + Y, 1, 6, ST[0]);
  p.rect(13, 41 + Y, 20, 1, GD[1]); p.rect(14, 36 + Y, 18, 1, ST[2]);
  p.rect(14, 34 + Y, 18, 2, LTH); p.rect(22, 34 + Y, 3, 2, GD[2]); p.px(23, 34 + Y, GD[3]);
  /* breastplate */
  p.sell(23, 27 + Y, 9.5, 9, ST);
  p.rect(14, 33 + Y, 18, 2, ST[1]);
  for (let x = 16; x <= 30; x++){ const yy = 20 + Y + Math.round(Math.abs(x - 23)*.35); p.px(x, yy, GD[2]); }
  p.rect(23, 23 + Y, 1, 7, GD[1]); p.rect(20, 25 + Y, 7, 1, GD[1]); p.px(23, 25 + Y, GD[3]); p.px(22, 24 + Y, GD[2]);
  p.px(18, 30 + Y, TN); p.px(27, 22 + Y, TN); p.px(28, 29 + Y, TD); p.px(19, 23 + Y, TN);
  p.rect(15, 31 + Y, 16, 1, ST[0]);
  /* hollow joints with a violet glint */
  p.rect(13, 28 + Y, 2, 4, HOL); p.rect(31, 28 + Y, 2, 4, HOL); p.px(13, 30 + Y, WIS); p.px(32, 29 + Y, WIS);
  /* sword arm (image left) */
  const H = PAL_HAND[pose] || PAL_HAND.walk, hx = H[0], hy = H[1] + (pose === 'walk' ? Y : 0);
  const shx = 12, shy = 24 + Y;
  const armSeg = (x0, y0, x1, y1) => { const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0)) | 0;
    for (let i = 0; i <= n; i++){ const t = n ? i/n : 0, x = Math.round(x0 + (x1 - x0)*t), y = Math.round(y0 + (y1 - y0)*t);
      p.rect(x - 2, y - 1, 4, 3, ST[1]); p.px(x - 2, y - 1, ST[2]); p.px(x + 1, y + 1, ST[0]); } };
  const elx = Math.round((shx + hx)/2) - (pose === 'raise' ? 3 : 1), ely = Math.round((shy + hy)/2) + (pose === 'raise' ? 0 : 1);
  armSeg(shx, shy, elx, ely); armSeg(elx, ely, hx, hy);
  p.sell(elx, ely, 2, 2, ST);
  p.rect(hx - 2, hy - 2, 5, 4, ST[1]); p.rect(hx - 2, hy - 2, 5, 1, ST[2]); p.px(hx + 2, hy + 1, ST[0]); p.px(hx - 1, hy, HOL); p.px(hx + 1, hy, HOL);
  /* pauldrons */
  for (const [cx, s] of [[13, -1], [33, 1]]){
    p.sell(cx, 22 + Y, 6.5, 5, ST);
    p.sell(cx + s, 25 + Y, 5.5, 2.6, ST, -.2);
    for (let i = -5; i <= 5; i++) p.px(cx + i, 26 + Y + Math.round((i*i)/12) - (Math.abs(i) > 4 ? 1 : 0), GD[i < 0 ? 2 : 1]);
    p.px(cx - 2*s, 19 + Y, ST[3]); p.px(cx + 3*s, 23 + Y, TN);
  }
  /* great helm: rounded top, visor slit (eyes are drawn at run time), breaths, gold crest and band */
  const hy0 = 5 + Y;
  p.sell(23, hy0 + 6, 7.5, 7, ST);
  p.rect(16, hy0 + 6, 15, 8, ST[1]); p.rect(16, hy0 + 6, 3, 8, ST[2]); p.rect(29, hy0 + 6, 2, 8, ST[0]);
  p.rect(17, hy0 + 14, 13, 2, ST[1]); p.rect(17, hy0 + 15, 13, 1, ST[0]);
  p.rect(17, hy0 + 7, 13, 2, HOL);
  p.rect(23, hy0, 1, 15, GD[2]); p.px(23, hy0, GD[3]); p.rect(16, hy0 + 5, 15, 1, GD[1]); p.px(18, hy0 + 5, GD[3]);
  for (const x of [19, 21, 25, 27]) p.rect(x, hy0 + 11, 1, 2, HOL);
  p.px(20, hy0 + 3, ST[3]); p.px(19, hy0 + 4, ST[3]); p.px(27, hy0 + 12, TN);
  /* tattered plume, swept back */
  const pw = walk ? [0, 1, 0, -1][f] : 0;
  for (let i = 0; i < 9; i++){ const x = 23 + i, y = hy0 - 2 + Math.round(i*i/14) + (i > 4 ? pw : 0);
    p.rect(x, y, 1, 3 + (i > 5 ? 1 : 0), i % 3 === 2 ? CP[0] : CP[2]); }
  p.px(31, hy0 + 5 + pw, CP[1]); p.px(32, hy0 + 6 + pw, CP[0]); p.rect(22, hy0 - 2, 3, 2, CP[2]);
  /* kite shield (image right; centred and lowered while bracing) */
  const sx = pose === 'brace' ? -9 : pose === 'spin' ? 4 : 0, sy = (pose === 'brace' ? 1 : 0) + Y;
  const S = (x, y) => [x + sx, y + sy];
  p.poly([S(29, 23), S(43, 23), S(43, 36), S(36, 52), S(29, 36)], GD[1]);
  p.poly([S(31, 25), S(41, 25), S(41, 36), S(36, 49), S(31, 36)], ST[1]);
  p.poly([S(31, 25), S(36, 25), S(36, 48), S(31, 36)], ST[2]);
  p.rect(30 + sx, 23 + sy, 13, 1, GD[2]); p.px(29 + sx, 23 + sy, GD[3]); p.px(30 + sx, 24 + sy, GD[3]);
  p.rect(35 + sx, 27 + sy, 2, 17, GD[1]); p.rect(32 + sx, 31 + sy, 8, 2, GD[1]); p.px(35 + sx, 27 + sy, GD[3]); p.px(32 + sx, 31 + sy, GD[2]);
  p.px(39 + sx, 28 + sy, TN); p.px(33 + sx, 40 + sy, TD); p.px(38 + sx, 38 + sy, TN); p.px(40 + sx, 34 + sy, TD);
  p.line(38 + sx, 26 + sy, 40 + sx, 30 + sy, ST[0]);
  return outlineC(c, '#14101a');
}
/* greatsword: pommel, grip, gold crossguard, long tarnished blade with a violet fuller; pivot = grip */
function greatswordBase(){
  const c = cnv(36, 11), p = painter(c), Y = 2;
  p.rect(1, Y + 2, 3, 3, '#d6a636'); p.px(1, Y + 2, '#f6dc78'); p.px(3, Y + 4, '#5e3e10');
  p.rect(4, Y + 2, 5, 3, '#4a2c18'); p.px(5, Y + 2, '#7a4a26'); p.px(7, Y + 2, '#7a4a26'); p.rect(4, Y + 4, 5, 1, '#2a1a10');
  p.rect(9, Y - 1, 2, 9, '#a07018'); p.rect(9, Y - 1, 1, 9, '#d6a636'); p.px(9, Y - 1, '#f6dc78'); p.px(10, Y + 3, '#8a4ab8');
  p.rect(11, Y + 1, 21, 5, '#959eae'); p.rect(11, Y + 1, 21, 1, '#d2d9e3'); p.rect(11, Y + 5, 21, 1, '#5e6676');
  p.rect(12, Y + 3, 16, 1, '#6a3a9a'); p.px(14, Y + 3, '#b884e8'); p.px(20, Y + 3, '#b884e8');
  p.rect(32, Y + 2, 2, 3, '#959eae'); p.px(34, Y + 3, '#d2d9e3'); p.px(32, Y + 1, '#d2d9e3');
  p.px(17, Y + 5, '#6a6250'); p.px(25, Y + 1, '#6a6250');
  return outlineC(c, '#14101a');
}
/* the evil spirit that wears the armour: a hooded wraith with long arms, tail of mist (drawn translucent) */
function spiritSprite(f){
  const c = cnv(34, 36), p = painter(c), w = f ? 1 : 0;
  const V = ['#2a1240', '#4a2070', '#7a3ab0', '#b884e8'];
  p.poly([[17, 2], [25, 9], [27, 20], [22, 33 + w], [17, 28], [12, 33 - w], [7, 20], [9, 9]], V[1]);
  p.poly([[17, 2], [25, 9], [24, 18], [17, 14], [10, 18], [9, 9]], V[2]);
  p.sell(17, 10, 5, 5, [V[0], V[0], V[1], V[2]]);
  p.rect(14, 10, 2, 1, '#e8ffd0'); p.rect(19, 10, 2, 1, '#e8ffd0'); p.px(14, 11, '#9dff6a'); p.px(20, 11, '#9dff6a');
  p.rect(15, 13, 4, 1, V[0]); p.px(16, 14, V[0]);
  for (const s of [-1, 1]){
    p.line(17 + s*7, 15, 17 + s*13, 20 - w*s, V[2]); p.line(17 + s*13, 20 - w*s, 17 + s*15, 25, V[1]);
    p.px(17 + s*15, 26, V[3]); p.px(17 + s*16, 25, V[3]); p.px(17 + s*14, 27, V[3]);
  }
  p.px(12, 30, V[2]); p.px(22, 30, V[2]); p.px(17, 31 + w, V[1]);
  return outlineC(c, '#1a0828');
}
/* spectral blade (Lâminas fantasmas): pre-rotated like the hero's sword */
function ghostBladeBase(){
  const c = cnv(23, 9), p = painter(c);
  p.rect(1, 3, 3, 3, '#7a3ab0'); p.rect(4, 1, 2, 7, '#b884e8'); p.px(4, 1, '#ffffff');
  p.rect(6, 3, 13, 3, '#c8b8ff'); p.rect(6, 3, 13, 1, '#ffffff'); p.rect(6, 5, 13, 1, '#7a5ae0'); p.rect(7, 4, 10, 1, '#e8ddff');
  p.px(19, 4, '#ffffff'); p.px(20, 4, '#e8ddff'); p.px(19, 3, '#e8ddff');
  return outlineC(c, '#3a1468');
}

/* Elder lich: skull under a hood and a bone-and-gold crown, deep purple robe with teal runes, tattered hem
   (no feet: it floats), staff with a teal crystal in a bone claw on the image left. Poses: 'float' (f = 0..3,
   hem waves), 'cast' (staff raised, free hand forward), 'tired' (hunched, staff low: after a cast). */
const LICH_W = 42, LICH_H = 60;
const LICH_GEM = {float:[7, 9], cast:[7, 3], tired:[9, 14]};
function lichBody(pose, f){
  const c = cnv(LICH_W, LICH_H), p = painter(c);
  const RB = ['#1c1030', '#2e1a4c', '#45286e', '#5e3a90'], TL = ['#1a5a5a', '#2fa0a0', '#7ff0e0'];
  const BN = ['#8a8270', '#c8c0a8', '#efe8d4'], GD = ['#7a5414', '#c8962c', '#f2d070'], HOL = '#0a0612';
  const cast = pose === 'cast', tired = pose === 'tired', Y = tired ? 3 : 0, wv = pose === 'float' ? f : cast ? 1 : 2;
  /* robe: wide bell, ragged waving hem */
  const top = 20 + Y, hemY = 50;
  p.poly([[16, top], [28, top], [33, 34], [36, hemY - 2], [8, hemY - 2], [11, 34]], RB[1]);
  p.poly([[16, top], [21, top], [19, hemY - 2], [10, hemY - 2], [12, 34]], RB[2]);
  p.poly([[25, top + 4], [28, top], [33, 34], [36, hemY - 2], [29, hemY - 2]], RB[0]);
  for (let x = 8; x <= 36; x++){
    const ph = Math.sin(x*.9 + wv*1.57)*1.6 + Math.sin(x*2.3 - wv)*.8, len = 2 + Math.round(1.5 + ph + h2(x, 5)*2);
    p.rect(x, hemY - 2, 1, len, x < 20 ? RB[2] : x < 28 ? RB[1] : RB[0]);
    if ((x + wv) % 5 === 0) p.px(x, hemY - 2 + len, RB[1]);
  }
  /* teal rune trim down the front and along the hem */
  p.rect(21, top + 6, 2, hemY - top - 7, RB[3]);
  for (let y = top + 8; y < hemY - 2; y += 4){ p.px(21, y, TL[1]); p.px(22, y + 1, TL[0]); p.px(21, y + 2, TL[1]); }
  for (let x = 10; x <= 34; x += 3) p.px(x, hemY - 3, (x/3) % 2 ? TL[1] : TL[0]);
  p.rect(14, 33, 16, 2, RB[0]); p.rect(20, 33, 4, 2, GD[1]); p.px(21, 33, GD[2]);
  /* sleeves + bony hands */
  const sleeve = (x0, y0, x1, y1, col) => { const n = Math.max(Math.abs(x1 - x0), Math.abs(y1 - y0));
    for (let i = 0; i <= n; i++){ const t = n ? i/n : 0, w = 2 + Math.round(t*2); p.rect(Math.round(x0 + (x1 - x0)*t) - w, Math.round(y0 + (y1 - y0)*t) - 1, w*2, 3, col); } };
  // staff hand (image left)
  const gx = (LICH_GEM[pose] || LICH_GEM.float)[0], gy = (LICH_GEM[pose] || LICH_GEM.float)[1] + Y;
  const shx = cast ? 9 : 10, shy = cast ? 16 : 31 + Y;
  sleeve(15, 23 + Y, shx + 1, shy, RB[2]);
  // free hand (image right): forward and glowing while casting, else folded
  const fx = cast ? 37 : 30, fy = cast ? 24 : 33 + Y;
  sleeve(28, 23 + Y, fx - 2, fy, RB[1]);
  for (const [hx, hy] of [[shx, shy], [fx, fy]]){
    p.rect(hx - 1, hy - 1, 3, 3, BN[1]); p.px(hx - 1, hy - 1, BN[2]); p.px(hx + 1, hy + 1, BN[0]); p.px(hx + 2, hy - 1, BN[1]); p.px(hx + 2, hy + 1, BN[0]);
  }
  /* staff: dark wood wrapped in bone, claw holding the crystal */
  const sb = Math.min(58, 52 + Y);
  p.rect(gx, gy + 6, 2, sb - gy - 6, '#3a2418'); p.rect(gx, gy + 6, 1, sb - gy - 6, '#5a3a24');
  for (let y = gy + 10; y < sb; y += 7){ p.rect(gx - 1, y, 4, 1, BN[1]); p.px(gx + 2, y, BN[0]); }
  p.px(gx - 2, gy + 5, BN[1]); p.px(gx + 3, gy + 5, BN[1]); p.px(gx - 2, gy + 4, BN[2]); p.px(gx + 3, gy + 4, BN[0]); p.rect(gx - 1, gy + 6, 4, 1, BN[1]);
  p.poly([[gx + 1, gy - 4], [gx + 4, gy + 1], [gx + 1, gy + 6], [gx - 2, gy + 1]], TL[1]);
  p.poly([[gx + 1, gy - 4], [gx + 1, gy + 6], [gx - 2, gy + 1]], TL[2]);
  p.px(gx, gy - 1, '#ffffff'); p.px(gx + 3, gy + 2, TL[0]); p.px(gx + 2, gy + 4, TL[0]);
  /* high spiked collar */
  p.poly([[13, 17 + Y], [17, 21 + Y], [27, 21 + Y], [31, 17 + Y], [29, 24 + Y], [15, 24 + Y]], RB[3]);
  p.px(13, 16 + Y, RB[3]); p.px(31, 16 + Y, RB[2]); p.rect(15, 23 + Y, 14, 1, TL[0]);
  /* hood + skull */
  const hx = 22, hy = 11 + Y;
  p.sell(hx, hy, 7.5, 8, [RB[0], RB[1], RB[2], RB[3]]);
  p.rect(hx - 7, hy, 3, 9, RB[1]); p.rect(hx + 5, hy, 3, 9, RB[0]);
  p.sell(hx, hy + 2, 4.6, 5, [HOL, HOL, '#1a1024', '#1a1024']);
  p.sell(hx, hy + 1, 3.6, 3.6, [BN[0], BN[1], BN[1], BN[2]]);
  p.rect(hx - 2, hy + 4, 5, 2, BN[1]); p.rect(hx - 2, hy + 5, 5, 1, BN[0]);
  p.rect(hx - 3, hy, 2, 2, HOL); p.rect(hx + 1, hy, 2, 2, HOL);       // sockets (eyes glow at run time)
  p.px(hx, hy + 2, HOL); p.px(hx - 1, hy + 6, HOL); p.px(hx + 1, hy + 6, HOL); p.px(hx, hy + 6, BN[1]);
  /* crown: bone spikes on a gold band with a teal gem */
  p.rect(hx - 5, hy - 5, 11, 2, GD[1]); p.rect(hx - 5, hy - 5, 11, 1, GD[2]);
  for (const [dx, h] of [[-5, 3], [-3, 4], [0, 6], [3, 4], [5, 3]]){ p.rect(hx + dx, hy - 5 - h, 1, h, BN[1]); p.px(hx + dx, hy - 5 - h, BN[2]); }
  p.px(hx, hy - 4, TL[2]); p.px(hx - 1, hy - 4, TL[1]); p.px(hx + 1, hy - 4, TL[1]);
  return outlineC(c, '#0c0614');
}
