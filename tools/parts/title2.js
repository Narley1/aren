/* --- napping scene sprites --- */
const TS2 = (() => {
  const LEAF = ['#2a6e34', '#3f9a45', '#5fbb4c', '#92dc62'], BUSHC = ['#2a6e34', '#3f9a45', '#5cb84a', '#8ed860'];
  /* big shade tree */
  const tree = cnv(50, 64), p = painter(tree);
  p.rect(20, 34, 11, 26, '#7a4a26'); p.rect(20, 34, 3, 26, '#9a6236'); p.rect(28, 34, 3, 26, '#5a3418');
  p.poly([[14, 62], [20, 54], [21, 62]], '#7a4a26'); p.poly([[37, 62], [30, 53], [30, 62]], '#5a3418'); p.poly([[24, 62], [26, 57], [28, 62]], '#6a3e20');
  for (const [x0, y0, x1, y1] of [[23, 58, 22, 44], [27, 56, 28, 42], [25, 50, 26, 38]]) for (let i = 0; i <= 12; i++){ const t = i/12; p.px(x0 + (x1 - x0)*t, y0 + (y1 - y0)*t, '#5a3418'); }
  p.ell(26, 47, 1.6, 2.2, '#3e2412'); p.px(25, 46, '#2a160a');
  p.rect(19, 34, 13, 3, '#3e2412');
  for (const [x, y, rx, ry] of [[14, 16, 11, 10], [36, 16, 11, 10], [25, 11, 14, 11], [7, 27, 8, 8], [43, 27, 8, 8], [25, 25, 21, 13], [15, 33, 10, 6], [35, 33, 10, 6]]) p.sell(x, y, rx, ry, LEAF);
  for (const [x, y] of [[14, 9], [22, 5], [8, 20], [17, 15], [30, 7], [24, 19], [11, 26], [38, 13]]){ p.rect(x, y, 2, 1, '#c0f08a'); p.px(x, y + 1, '#92dc62'); }
  for (const [x, y] of [[33, 30], [17, 35], [44, 24], [5, 30], [28, 22]]) p.px(x, y, '#1f5a2a');
  /* red apples */
  for (const [x, y] of [[11, 22], [37, 21], [29, 31]]){ p.rect(x, y, 2, 2, '#e8383a'); p.px(x, y, '#ffc0b0'); }
  outlineC(tree, '#163a20');
  const treeFr = swayFrames(tree, 36, 1, 6);
  /* Aren asleep, sitting against the trunk */
  const HP = SPR32.hero.pal, PAL = Object.assign({}, HP, {m:'#a04a4a', z:'#3a2a3a'});
  const HEAD = [
    "........iH........",
    "......HHiHHH......",
    "....HHiiHHHHHh....",
    "...HHiHHHHHHHHh...",
    "...HiHHHHHHHHHh...",
    "...HHHHHhHHHHhh...",
    "...HHhSShHSShhh...",
    "...HhSSSSSSSSsh...",
    "...hSzzSSSSzzSh...",
    "...hSSSSSSSSSsh...",
    "....SbSSmSSSbs....",
    ".....sSSSSSSs....."];
  const BODY = [
    "....RRRRRRRRr.....",
    "...uRrTTTTTTtt....",
    "..uTTrTTTTTTTtt...",
    "..SSTTTTTTTTTSS...",
    "..LLLLLyyLLLLLL...",
    "..PPPPPPPPPPPPpp..",
    "..PPPPpPPPPPPPpp..",
    "..BBBnn....BBBnn..",
    "..BBBBn....BBBBn.."];
  const sleep = [0, 1].map(inhale => {
    const c = cnv(20, HEAD.length + BODY.length + 2), g = c.getContext('2d');
    const draw = (rows, oy, ox) => rows.forEach((r, y) => { for (let x = 0; x < r.length; x++){ const col = PAL[r[x]]; if (col && r[x] !== '.'){ g.fillStyle = col; g.fillRect(x + 1 + ox, y + oy, 1, 1); } } });
    draw(HEAD, inhale ? 1 : 2, 1);
    draw(BODY, HEAD.length + 1, 0);
    return outlineC(c, SPR32.hero.outline);
  });
  /* hiding bush */
  const bush = cnv(30, 17), b = painter(bush);
  for (const [x, y, rx, ry] of [[8, 10, 7, 6], [21, 10, 7, 6], [15, 7, 9, 7], [15, 12, 12, 4.5]]) b.sell(x, y, rx, ry, BUSHC);
  for (const [x, y] of [[9, 5], [16, 2], [22, 6]]) b.rect(x, y, 2, 1, '#b4ec80');
  outlineC(bush, '#163a20');
  /* goblin in a bush disguise: two frames of little feet, eyes peeking out */
  const disguise = [0, 1, 2].map(f => {
    const c = cnv(22, 20), q = painter(c);
    for (const [x, y, rx, ry] of [[7, 8, 6, 5.5], [15, 8, 6, 5.5], [11, 6, 8, 6], [11, 11, 9.5, 4]]) q.sell(x, y, rx, ry, BUSHC);
    q.rect(10, 0, 1, 2, '#3a843a'); q.rect(11, 0, 2, 1, '#5cb84a');
    if (f < 2){ q.rect(5, 15, 3, 2, '#86c83e'); q.rect(14, 15, 3, 2, '#86c83e'); q.rect(f ? 4 : 5, 17, 4, 2, '#4a3420'); q.rect(f ? 14 : 13, 17, 4, 2, '#4a3420'); }
    else { q.rect(4, 15, 3, 3, '#86c83e'); q.rect(15, 15, 3, 3, '#86c83e'); q.rect(3, 18, 4, 1, '#4a3420'); q.rect(15, 18, 4, 1, '#4a3420'); }
    q.rect(7, 8, 3, 2, '#ffe14a'); q.rect(12, 8, 3, 2, '#ffe14a'); q.px(f === 1 ? 7 : 8, 9, '#2a1a08'); q.px(f === 1 ? 12 : 13, 9, '#2a1a08');
    return outlineC(c, '#163a20');
  });
  /* tiny pixel glyphs */
  const glyph = (rows, col, out) => { const c = cnv(rows[0].length + 2, rows.length + 2), g = c.getContext('2d'); g.fillStyle = col;
    rows.forEach((r, y) => { for (let x = 0; x < r.length; x++) if (r[x] === '#') g.fillRect(x + 1, y + 1, 1, 1); }); return outlineC(c, out); };
  const zS = glyph(["###", "..#", ".#.", "#..", "###"], '#ffffff', '#3a4a6a');
  const zL = glyph(["#####", "...#.", "..#..", ".#...", "#####"], '#ffffff', '#3a4a6a');
  const shh = (() => { const c = cnv(22, 13), g = c.getContext('2d');
    g.fillStyle = '#ffffff'; g.fillRect(1, 1, 20, 8); g.fillRect(3, 9, 3, 2); g.fillRect(4, 11, 1, 1);
    const S = ["###", "#..", "###", "..#", "###"], H = ["#..", "#..", "###", "#.#", "#.#"], X = ["#", "#", "#", ".", "#"];
    g.fillStyle = '#2a1a3a';
    [[S, 3], [H, 7], [H, 11], [X, 16]].forEach(([gl, ox]) => gl.forEach((r, y) => { for (let x = 0; x < r.length; x++) if (r[x] === '#') g.fillRect(ox + x, 3 + y, 1, 1); }));
    return outlineC(c, '#2a1a3a'); })();
  const drop = glyph([".#.", "###", "###", ".#."], '#9fe0ff', '#2a4a7a');
  return {treeFr, sleep, bush, disguise, zS, zL, shh, drop};
})();
function napLayout(){
  const L = titleLayout(), land = VW > VH*1.1, k = L.k;
  const base = Math.round(VH*.87), Tx = Math.round(VW*(land ? .22 : .34));
  return {L, k, base, Tx, heroX:Tx - 2*k, bushX:Math.round(VW*(land ? .7 : .8)), bushY:Math.round(VH*.9), pathY:Math.round(VH*.95), land};
}
function drawNapScene(t){
  const N = napLayout(), k = N.k, S = TS2;
  const sc = (img, x, y) => ctx.drawImage(img, Math.round(x), Math.round(y), img.width*k, img.height*k);
  /* tree shade */
  ctx.globalAlpha = .22; ctx.fillStyle = '#123a1a';
  for (let i = 0; i < 6; i++){ const w = (44 - i*4)*k, y = N.base - 3*k + i*k*.5; ctx.fillRect(Math.round(N.Tx + 2*k - w/2), Math.round(y), Math.round(w), Math.ceil(k*.6)); }
  ctx.globalAlpha = 1;
  const treeX = N.Tx - 25*k, treeY = N.base - 62*k, trunkL = treeX + 20*k;
  /* goblin peeking from behind the trunk (drawn first, the trunk hides his body) */
  const cP = ((t + 2.5) % 9)/9, out = cP < .15 ? cP/.15 : cP < .45 ? 1 : cP < .55 ? 1 - (cP - .45)/.1 : 0;
  if (out > 0){
    const fr = ET.goblin.dirs.side[0].n, look = Math.floor(t*1.5) % 3 === 0;
    sc(look ? ET.goblin.dirs.down[0].n : fr, trunkL - (fr.width - 6 + 9*out - 9)*k + (look ? 0 : 0), N.base - 34*k);
  }
  sc(S.treeFr[Math.floor(t*2) % S.treeFr.length], treeX, treeY);
  /* sword leaning on the trunk, tip in the grass */
  ctx.save(); ctx.translate(N.heroX - 1*k, N.base - 19*k); ctx.scale(k, k); drawSword(0, 0, Math.PI/2 + .22, false); ctx.restore();
  /* Aren napping */
  const breath = (t % 3.2) < 1.6 ? 1 : 0, hero = S.sleep[breath];
  sc(hero, N.heroX, N.base - hero.height*k + k);
  /* ambush timing: the bush-goblin creeps in, panics when Aren snores, runs off */
  const cyc = (t % 17)/17, x0 = VW + 10, x1 = N.heroX + 24*k;
  let bx = x0, hop = 0, frame = 0, panic = false;
  if (cyc < .55){ const q = cyc/.55, step = (t*1.6) % 1; bx = x0 + (x1 - x0)*q; hop = step < .5 ? Math.sin(step*Math.PI*2)*1.5*k : 0; frame = step < .5 ? 1 : 0; }
  else if (cyc < .7){ bx = x1 + Math.sin(t*45)*.6*k; frame = 2; panic = true; }
  else if (cyc < .82){ const q = (cyc - .7)/.12; bx = x1 + (x0 + 30 - x1)*q*q; frame = Math.floor(t*14) % 2; hop = frame*k; }
  else bx = x0 + 40;
  /* Zzz: bigger snore when the bush is right next to him */
  const headX = N.heroX + 13*k, headY = N.base - 25*k;
  for (let i = 0; i < 3; i++){
    const ph = ((t*.45 + i/3) % 1), big = panic && i === 0;
    ctx.globalAlpha = Math.min(1, (1 - ph)*1.6);
    sc(big || ph > .55 ? S.zL : S.zS, headX + ph*8*k + Math.sin(ph*6 + i)*2*k, headY - ph*22*k - (big ? 6*k : 0));
  }
  ctx.globalAlpha = 1;
  /* goblin behind the hiding bush, shushing the bush-goblin */
  const aP = (t % 6.5)/6.5, rise = aP < .15 ? aP/.15 : aP < .7 ? 1 : aP < .8 ? 1 - (aP - .7)/.1 : 0;
  const gA = ET.goblin.dirs[Math.floor(t*.9) % 2 ? 'left' : 'down'][0].n;
  const gAx = N.bushX - gA.width*k/2 + 2*k, gAy = N.bushY - 13*k - rise*7*k;
  sc(gA, gAx, gAy);
  sc(S.bush, N.bushX - S.bush.width*k/2, N.bushY - S.bush.height*k + 2*k);
  if (rise > .9 && cyc < .55 && cyc > .1) sc(S.shh, gAx - 14*k, gAy - 10*k);
  /* the walking bush */
  if (bx < VW + 30){
    const d = S.disguise[frame];
    sc(d, bx - d.width*k/2, N.pathY - d.height*k - hop);
    if (panic){ sc(S.drop, bx + 8*k, N.pathY - d.height*k - 4*k + ((t*3) % 1)*3*k); }
  }
}
