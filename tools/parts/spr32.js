/* ================= 32-bit hand-pixelled sprites ================= */
/* Each view = hand-drawn upper body grid + generated walking legs. 1px auto outline. */
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

const SPR32 = {
  hero:{
    outline:'#2a1820',
    pal:{H:'#a35c2e', h:'#6e3818', i:'#d88a4a', S:'#f8cca0', s:'#d8946a', e:'#2a1a3a', b:'#f29a86', R:'#e8503a', r:'#a82e22',
      T:'#3f86dc', t:'#2a5aa6', u:'#78b4f0', L:'#6e3f1e', y:'#f2c14e', P:'#e9dcc0', p:'#c8b896', B:'#7a4422', n:'#4a2810'},
    legs:{xL:5, xR:9, w:2, pr:1, br:2, p:'P', ps:'p', b:'B', bs:'n', xs:7, spread:2},
    down:{rows:[
      "................",
      ".......iH.......",
      ".....HHiHHH.....",
      "...HHiiHHHHHh...",
      "..HHiHHHHHHHHh..",
      "..HiHHHHHHHHHh..",
      "..HHHHHhHHHHhh..",
      "..HHhSShHSShhh..",
      "..HhSSSSSSSSsh..",
      "..hSSeSSSSeSsh..",
      "..hSSeSSSSeSsh..",
      "...SbSSSSSSbs...",
      "....sSSSSSSs....",
      "....RRRRRRRr....",
      "...uuRTTTTTtt...",
      "...uTrTTTTTTt...",
      "...SLLLyyLLLS...",
      "...uTTTTTTTTt..."]},
    up:{rows:[
      "................",
      ".......hH.......",
      ".....HHiHHH.....",
      "...HHiiHHHHHh...",
      "..HHiHHHHHHHHh..",
      "..HiHHHHHHHHHh..",
      "..HHHHHHHHHHhh..",
      "..HHHHhHHhHHhh..",
      "..HHHhHHHHhHhh..",
      "..hHHHHhHHHHhh..",
      "..hhHHHHHHHhhh..",
      "...hhHhHHhHhh...",
      "....shhhhhhs....",
      "....RRRRRRRr....",
      "...uTTRrTTTtt...",
      "...uTTrRTTTTt...",
      "...SLLLLLLLLS...",
      "...uTTTTTTTTt..."]},
    side:{rows:[
      "................",
      ".....hiH........",
      "....HHiHHH......",
      "...HHiiHHHHH....",
      "..HHiHHHHHHHH...",
      "..HHHHHHHHHHHH..",
      "..HHHHHHhHhSHh..",
      "..hHHHHhSSSSSS..",
      "..hHHHhSSSSeSS..",
      "..hHHhSsSSSeSSS.",
      "...hHhSSSSSbSs..",
      "....hsSSSSSSs...",
      ".....ssSSSSs....",
      ".....RRRRRr.....",
      "..RrrTTTTTt.....",
      ".rr..TTTTTt.....",
      ".....LLLyLL.....",
      ".....tTTTTTt...."],
      arm:{x:7, y:14, rows:["uT", "uT", "SS"]}}
  },
  goblin:{
    outline:'#1c2a10',
    pal:{G:'#86c83e', g:'#58922a', l:'#b8ec78', d:'#3e2a14', Y:'#ffe14a', e:'#2a1a08', m:'#3a1a10', w:'#fffbe8',
      V:'#8a5a2b', v:'#5e3b1a', L:'#3e2a14', y:'#c9a43a', C:'#6e4a26', c:'#4a3018', W:'#dfe6ee', K:'#7a4a26', B:'#4a3420', n:'#2e1e0e'},
    legs:{xL:6, xR:10, w:2, pr:1, br:1, p:'G', ps:'g', b:'B', bs:'n', xs:8, spread:1},
    down:{rows:[
      "..................",
      ".........d........",
      "......GGGlGG......",
      ".....GlGGGGGG.....",
      "....GlGGGGGGGg....",
      ".GGgGGGGGGGGGGggg.",
      "..GgGYeGGGGeYGgg..",
      "....GYYGGGGYYg....",
      "....GGGGggGGGg....",
      "....gGmwmwmmGg....",
      ".....gGGGGGGg.W...",
      ".....GVVGGVVg.W...",
      ".....GVvGGVvgGK...",
      ".....GLLLyLLg.....",
      "......CCcCCc......"]},
    up:{rows:[
      "..................",
      ".........d........",
      "......GGGlGG......",
      ".....GlGGGGGG.....",
      "....GlGGGGGGGg....",
      ".GGgGGGGGGGGGGggg.",
      "..GgGGGGGGGGGGgg..",
      "....GGGGGGGGGg....",
      "....gGGGGGGGgg....",
      "....ggGGGGGggg....",
      ".....gggggggg.W...",
      ".....GVVVVVVg.W...",
      ".....GVvVVvVgGK...",
      ".....GLLLLLLg.....",
      "......CCcCCc......"]},
    side:{rows:[
      "..................",
      "......d...........",
      ".....GGGlG........",
      "....GGlGGGGG......",
      "...GGlGGGGGGG.....",
      ".GGgGGGGGGGGGGG...",
      "..GgGGGGGGGYeG....",
      "....GGGGGGGYYGG...",
      "....gGGGGGGGGGGG..",
      "....gGGGGGGmwmg...",
      ".....gGGGGGGg.....",
      "......VVGGVv......",
      "......VvGGVv......",
      "......LLLyLL......",
      "......CCcCCc......"],
      arm:{x:8, y:11, rows:["GG..", "gG..", "GGWW"]}}
  },
  hobgoblin:{
    outline:'#2a1610',
    pal:{O:'#e08040', o:'#a6522a', q:'#f6b07a', M:'#8d98a6', m:'#555f6c', x:'#d2dae2', Z:'#c83a2a', e:'#2a0a08', w:'#ffffff',
      A:'#7c8a9a', a:'#5a6878', L:'#4a2e18', y:'#d8b24a', P:'#5a3a22', p:'#46301c', B:'#3a2618', n:'#2a1a10', W:'#aeb8c4', H:'#7a4a26', f:'#3a0a08', t:'#fff6e0'},
    legs:{xL:6, xR:10, w:2, pr:2, br:2, p:'P', ps:'p', b:'B', bs:'n', xs:8, spread:2},
    down:{rows:[
      "..................",
      "........ZZ........",
      "......xMMMMM......",
      ".....xMMMMMMm.....",
      "....MMMMxMMMMm....",
      ".OOommmmmmmmmmooO.",
      "..OoOOOOmmOOOOoo..",
      "....OweOmmOewo....",
      "....OOOOOOOOOo..WW",
      "....oOftfftfOo..WW",
      ".....oOOOOOOo...H.",
      "....OAAaAAaAAo..H.",
      "....OAaAAaAAao..H.",
      "....OLLLyyLLLoOOH.",
      "....aAAAAAAAAa..H."]},
    up:{rows:[
      "..................",
      "........ZZ........",
      "......xMMMMM......",
      ".....xMMMMMMm.....",
      "....MMMMMMMMMm....",
      ".OOommmmmmmmmmooO.",
      "..OoMMMMMMMMMMoo..",
      "....mMMMMMMMMm....",
      "....oOOOOOOOOo..WW",
      "....ooOOOOOOoo..WW",
      ".....oooooooo...H.",
      "....OAAaAAaAAo..H.",
      "....OAaAAaAAao..H.",
      "....OLLLLLLLLoOOH.",
      "....aAAAAAAAAa..H."]},
    side:{rows:[
      "..................",
      ".....ZZ...........",
      "....ZxMMMM........",
      "....xMMMMMMm......",
      "...MMMMxMMMMm.....",
      ".OOmmmmmmmmmmm....",
      "..oOMMMMOOOOOm....",
      "....MMMOOOOewm....",
      "....oMOOOOOOOOO...",
      "....ooOOOOOftf....",
      ".....ooOOOOOo.....",
      "......AAaAAo......",
      "......AaAAao......",
      "......LLLyLL......",
      "......aAAAAa......"],
      arm:{x:7, y:7, rows:["....WW", "....WH", ".....H", "AA...H", "aA...H", "OOOOOH"]}}
  },
  elf:{
    outline:'#140a22',
    pal:{S:'#6a5e8c', s:'#463c66', l:'#8e82b2', H:'#efeaff', h:'#b4a8dc', i:'#ffffff', E:'#ff5ad1', m:'#a8144a',
      R:'#3e2860', r:'#2a1a40', u:'#5a3c86', L:'#1a0e2a', y:'#ff5ad1', B:'#1e1230', n:'#120a1e', W:'#8a5328', w:'#d9d2ff', P:'#2a1a40', p:'#1e1230'},
    legs:{xL:6, xR:10, w:2, pr:2, br:2, p:'P', ps:'p', b:'B', bs:'n', xs:8, spread:2},
    down:{rows:[
      "..................",
      "......HHHHHH......",
      ".....HiiHHHHh.....",
      "....HiHHHHHHHh....",
      "..S.HHHHHHHHHh.s..",
      "..SSHhSSSSSShHss..",
      "....HSESSSSESh....",
      "....HSESSSSESh....",
      "....HsSSSSSSshW...",
      "....HHsSmmSshh.W..",
      "....HHHsssshhh.W..",
      "....HRRuRRRrrh.Ww.",
      "...SHuRuRRRRrhSW..",
      "....LLLLyLLLLL.W..",
      "....RRuRRRRRrr.W..",
      "....RuRRRRRRrrW...",
      "....rRRRRRRRrr...."]},
    up:{rows:[
      "..................",
      "......HHHHHH......",
      ".....HiiHHHHh.....",
      "....HiHHHHHHHh....",
      "..S.HHHHHHHHHh.s..",
      "..SSHHHHHHHHHhss..",
      "....HHHHHHHHHh....",
      "....HHHHhHHHHh....",
      "....HHHhHHhHHhW...",
      "....HHHhHHhHhh.W..",
      "....hHHhHHhHhh.W..",
      "....hRRhHHhRrh.W..",
      "...SuRRhHhRRrhSW..",
      "....LLLLLLLLLL.W..",
      "....RRuRRRRRrr.W..",
      "....RuRRRRRRrrW...",
      "....rRRRRRRRrr...."]},
    side:{rows:[
      "..................",
      "......HHHHH.......",
      ".....HiiHHHH......",
      "....HiHHHHHHH.....",
      "...HHHHHHHHHHH....",
      "..sHHHHHHhSSS.....",
      "...HHHHHhSSSES....",
      "...HHHHhSSSSES....",
      "...HHHHhSSSSSSS...",
      "...HHHHhsSSSms....",
      "...HHHHhhsss......",
      "...HHHhRRRRr......",
      "...HHhRRuRRr......",
      "....hLLLLyLL......",
      "......RRuRRr......",
      ".....RRuRRRr......",
      ".....rRRRRRr......"],
      arm:{x:8, y:9, rows:["...W.", "....W", "uu..W", "ru..W", "SSSSW", "....W", "...W."]}}
  },
  orc:{
    outline:'#1a1410',
    pal:{G:'#6a8a3c', g:'#455e26', l:'#94b45e', d:'#1e1a14', e:'#2a0806', E:'#ff4a2a', t:'#f6eedc', m:'#2a1a10',
      M:'#8d98a6', n:'#5f6a78', x:'#d2dae2', A:'#5e4838', a:'#3e2e22', q:'#7a5e4a', L:'#2a1c12', y:'#c9a43a',
      P:'#3e2e22', p:'#2e2018', B:'#2a1c12', b:'#1c120a', W:'#9aa6b4', w:'#e8eef4', H:'#5a3418'},
    legs:{xL:8, xR:13, w:3, pr:4, br:3, p:'P', ps:'p', b:'B', bs:'b', xs:10, spread:3},
    down:{rows:[
      "...........................",
      "...........dd..............",
      "..........dddd.............",
      "........GGGGGGGG...........",
      ".......GlGGGGGGGg..........",
      "......GlGGGGGGGGGg.........",
      "......GgggGGGGgggg.........",
      "....GGGEeGGGGGGeEGgg.......",
      "......GGGGGgGGGGGg.........",
      "......GtmmmmmmmmtG.........",
      ".......gGtGGGGtGg.......xW.",
      "...xMMMgGGGGGGGGgMMMn...xWn",
      "..xMMMMAAAqAAAAAAMMMMn..xWn",
      "..GMMMnAqAAAAAaAAnMMMg..xWn",
      "..GGg.AAqAAAAaAAAA.gGg..xWn",
      "..GGg.AAAqAAaAAAAA.gGg..xWn",
      "..GGg.AAAAqaAAAAAA.gGg..WWn",
      "..lGg.AAAAAqAAAAAA.gGg...H.",
      "..GGg.AAAAAAqAAAAA.gGg...H.",
      "..GGg.AAAAAAAqAAAA.gGGGGGH.",
      "..GGG.LLLLLyyLLLLL.GGG.....",
      "..gGg.aAAAAAAAAAAa.gGg.....",
      "......aAaAaAaAaAaa.........",
      "......AaAaAaAaAaAa........."]},
    up:{rows:[
      "...........................",
      "...........dd..............",
      "..........dddd.............",
      "........GGGGGGGG...........",
      ".......GlGGGGGGGg..........",
      "......GlGGGGGGGGGg.........",
      "......GGGGGGGGGGGg.........",
      "....GGGGGGGGGGGGGGgg.......",
      "......GGGGGGGGGGGg.........",
      "......gGGGGGGGGGgg.........",
      ".......ggGGGGGGgg.......xW.",
      "...xMMMgGGGGGGGGgMMMn...xWn",
      "..xMMMMAAAqAAAAAAMMMMn..xWn",
      "..GMMMnAAAAAAAAAAnMMMg..xWn",
      "..GGg.AAAAAAAAAAAA.gGg..xWn",
      "..GGg.AAAAAaAAAAAA.gGg..xWn",
      "..GGg.AAAAAaAAAAAA.gGg..WWn",
      "..lGg.AAAAAaAAAAAA.gGg...H.",
      "..GGg.AAAAAaAAAAAA.gGg...H.",
      "..GGg.AAAAAaAAAAAA.gGGGGGH.",
      "..GGG.LLLLLLLLLLLL.GGG.....",
      "..gGg.aAAAAAAAAAAa.gGg.....",
      "......aAaAaAaAaAaa.........",
      "......AaAaAaAaAaAa........."]},
    side:{rows:[
      "...........................",
      "........dd.................",
      ".......dddd................",
      ".......GGGGGGGG............",
      "......GlGGGGGGGG...........",
      ".....GlGGGGGGGGGG..........",
      ".....GGGGGGGgggggg.........",
      "...GGGGGGGGGGGGeEG.........",
      ".....GGGGGGGGGGGGGG........",
      ".....gGGGGGGGGmmmt.........",
      "......gGGGGGGGGGt..........",
      "......xMMMMgGGGGg..........",
      ".....xMMMMMMnAAAA..........",
      ".....GMMMMMnAAAAA..........",
      "......AAAqAAAAAAA..........",
      "......AAAAqAAAAAA..........",
      "......AAAAAqAAAAA..........",
      "......AAAAAAqAAAA..........",
      "......AAAAAAAqAAA..........",
      "......AAAAAAAAqAA..........",
      "......LLLLLLLyyLL..........",
      "......aAAAAAAAAAa..........",
      "......aAaAaAaAaAa..........",
      "......AaAaAaAaAaA.........."],
      arm:{x:9, y:12, rows:["MMn.......", "GGg.......", "GGg.......", "GGg.......", "GGg....xW.", "GGg....xWn", "GGg....xWn", "GGGGGGGHWn", "........H."]}}
  },
  demon:{
    outline:'#1c0810',
    pal:{R:'#d0343e', r:'#8e1e2a', l:'#ff7a6a', K:'#eadfc4', k:'#a8987a', Y:'#ffd23a', e:'#2a0806', f:'#3a0810', t:'#ffffff',
      C:'#2b1627', c:'#170b15', L:'#170b15', y:'#ffd23a', B:'#3a1018', b:'#2a0a10', T:'#a8283a', w:'#f6eedc', P:'#c02e3a', p:'#8e1e2a'},
    legs:{xL:6, xR:10, w:2, pr:2, br:2, p:'P', ps:'p', b:'B', bs:'b', xs:8, spread:2},
    down:{rows:[
      "...K..........K...",
      "...KK........kk...",
      "....KK......kk....",
      ".....KRRRRRRk.....",
      "....RlRRRRRRRr....",
      "..r.RlRRRRRRRr.r..",
      "..rrRRRRRRRRRRrr..",
      "...rRrrRRRRrrRr...",
      "....RYeRRRReYr....",
      "....RRRRrrRRRr....",
      "....rRtffffftr....",
      ".....rRRRRRRr.....",
      "...RRlRRRRRRRrr...",
      "..RR.lRRRrRRr.rR.T",
      "..RR.RRRrRRRr.rR.T",
      "..ww.RRrRRRRr.ww.T",
      ".....LLLyyLLL...T.",
      ".....CCcCCcCCTTT..",
      "......cCCCCc......"]},
    up:{rows:[
      "...K..........K...",
      "...KK........kk...",
      "....KK......kk....",
      ".....kRRRRRRk.....",
      "....RlRRRRRRRr....",
      "..r.RRRRRRRRRr.r..",
      "..rrRRRRRRRRRRrr..",
      "...rRRRRRRRRRRr...",
      "....RRRRRRRRRr....",
      "....rRRRRRRRrr....",
      "....rrRRRRRrrr....",
      ".....rrrrrrrr.....",
      "...RRlRRRRRRRrr...",
      "..RR.RRRrRRRr.rR..",
      "..RR.RRRrRRRr.rR..",
      "..ww.RRRrRRRr.ww..",
      ".....LLLLLLLL.....",
      ".....CCcTTcCC.....",
      "......cCTCCc......"]},
    side:{rows:[
      "....K.............",
      "....KK............",
      ".....KK...........",
      ".....KRRRRR.......",
      "....RlRRRRRRR.....",
      "...rRRRRRRRRRR....",
      "..rrRRRRRRRrRR....",
      "...rRRRRRRrRYe....",
      "....RRRRRRRRRRR...",
      "....rRRRRRRftf....",
      ".....rRRRRRRr.....",
      "......RlRRRr......",
      ".TT...RRRrRr......",
      "..T...RRrRRr......",
      "...T..RRRRRr......",
      "....TTLLLyLL......",
      "......CCcCCc......",
      ".......cCCc......."],
      arm:{x:8, y:11, rows:["RR", "Rr", "Rr", "ww"]}}
  }
};
