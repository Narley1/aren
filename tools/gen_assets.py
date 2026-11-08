import asyncio, os, base64
from playwright.async_api import async_playwright
JS = r"""
async () => {
  const D = __d(), H = D.HERO.down[0], ET = D.ET;
  await document.fonts.load('700 120px "Pixelify Sans"'); await document.fonts.load('600 40px "Pixelify Sans"');
  const mk = (w, h) => { const c = document.createElement('canvas'); c.width = w; c.height = h; const g = c.getContext('2d'); g.imageSmoothingEnabled = false; return [c, g]; };
  // find a grassy 48x48 window
  let gx = 0, gy = 0;
  outer: for (let y = -400; y < 400; y += 16) for (let x = -400; x < 400; x += 16){
    let ok = true;
    for (let yy = 0; yy <= 48 && ok; yy += 6) for (let xx = 0; xx <= 48 && ok; xx += 6) if (dirtN(x + xx, y + yy) > DIRT_T - .06 || tallN(x + xx, y + yy) > TALL_T - .02) ok = false;
    if (ok){ gx = x; gy = y; break outer; }
  }
  const ground = (g, wx, wy, ww, wh, k) => {
    for (let j = Math.floor(wy/D.GCH); j <= Math.floor((wy + wh)/D.GCH); j++) for (let i = Math.floor(wx/D.GCH); i <= Math.floor((wx + ww)/D.GCH); i++)
      g.drawImage(D.groundChunk(i, j), (i*D.GCH - wx)*k, (j*D.GCH - wy)*k, D.GCH*k, D.GCH*k);
  };
  const shadowE = (g, cx, cy, rx, ry) => { g.fillStyle = 'rgba(16,40,22,.38)'; g.beginPath(); g.ellipse(cx, cy, rx, ry, 0, 0, Math.PI*2); g.fill(); };
  const icon = (size, heroFrac, bg) => {
    const [c, g] = mk(size, size);
    const k = Math.max(1, Math.floor(size*heroFrac/H.height));
    if (bg){ const area = size/k; ground(g, gx, gy, area, area, k); const v = g.createRadialGradient(size/2, size/2, size*.2, size/2, size/2, size*.75); v.addColorStop(0, 'rgba(0,0,0,0)'); v.addColorStop(1, 'rgba(8,20,16,.45)'); g.fillStyle = v; g.fillRect(0, 0, size, size); }
    const hw = H.width*k, hh = H.height*k, x = Math.round((size - hw)/2), y = Math.round((size - hh)/2 + k*.5);
    if (bg) shadowE(g, size/2, y + hh - k*1.2, hw*.36, k*1.6);
    g.drawImage(H, x, y, hw, hh);
    return c.toDataURL('image/png');
  };
  const fav = (() => { const [c, g] = mk(32, 32); const k = 2, cropH = 15; g.drawImage(H, 0, 0, H.width, cropH, Math.round((32 - H.width*k)/2), 1, H.width*k, cropH*k); return c.toDataURL('image/png'); })();
  // OG image
  const [o, og] = mk(1200, 630), K = 4, WW = 300, WH = 158;
  const ox = gx - 120, oy = gy - 60;
  ground(og, ox, oy, WW, WH, K);
  const S = (img, wx, wy, k = K) => og.drawImage(img, Math.round((wx - ox)*K - img.width*k/2), Math.round((wy - oy)*K - img.height*k), img.width*k, img.height*k);
  const hxw = ox + 78, hyw = oy + 92;
  const foes = [['goblin', -36, -6], ['goblin', 30, -16], ['hobgoblin', -22, 30], ['orc', 46, 34], ['demon', -58, 22], ['goblin', 14, 44], ['elf', -8, -40]];
  const fly = [['succubus', 52, -46], ['gargoyle', -56, -44]];
  const list = [];
  for (const [k, dx, dy] of foes){ const d = ET[k], face = Math.abs(dx) > Math.abs(dy) ? (dx > 0 ? 'left' : 'side') : (dy > 0 ? 'up' : 'down'); list.push({y:hyw + dy, img:d.dirs[face][(dx + dy + 64) % 4].n, x:hxw + dx}); }
  list.push({y:hyw, img:H, x:hxw});
  list.sort((a, b) => a.y - b.y);
  for (const it of list){ shadowE(og, (it.x - ox)*K, (it.y - oy)*K - 2, it.img.width*K*.3, K*1.6); S(it.img, it.x, it.y); }
  for (const [k, dx, dy] of fly){ const d = ET[k]; S(d.dirs.all[1].n, hxw + dx, hyw + dy - 6); }
  // sword slash: pixel crescent
  { const cx0 = hxw - ox, cy0 = hyw - 9 - oy;
    for (let a = -1.25; a <= .55; a += .02){ const q = (a + 1.25)/1.8;
      for (let r = 17 - q*4; r <= 19; r += .5){ const x = Math.round((cx0 + Math.cos(a)*r)*2)/2, y = Math.round((cy0 + Math.sin(a)*r)*2)/2;
        og.fillStyle = r > 18.4 ? '#5fa8f0' : q > .55 ? '#ffffff' : '#bfe6ff'; og.globalAlpha = .35 + q*.65; og.fillRect(x*K, y*K, K/2, K/2); } }
    og.globalAlpha = 1; }
  // title panel
  const px = 640, py = 150, pw = 520, ph = 330;
  og.fillStyle = 'rgba(9,16,22,.55)'; og.fillRect(px + 14, py + 14, pw, ph);
  og.fillStyle = '#1b3a4c'; og.fillRect(px, py, pw, ph);
  og.strokeStyle = '#f2c14e'; og.lineWidth = 10; og.strokeRect(px + 5, py + 5, pw - 10, ph - 10);
  og.strokeStyle = '#a8781c'; og.lineWidth = 5; og.strokeRect(px + 15, py + 15, pw - 30, ph - 30);
  og.textBaseline = 'alphabetic';
  og.fillStyle = '#a9c6d2'; og.font = '600 26px "Pixelify Sans"'; og.fillText('SOBREVIVÊNCIA · PIXEL 2D', px + 44, py + 72);
  og.font = '700 150px "Pixelify Sans"'; og.fillStyle = '#0b1218'; og.fillText('Aren', px + 50, py + 212); og.fillStyle = '#f2c14e'; og.fillText('Aren', px + 42, py + 204);
  og.font = '600 40px "Pixelify Sans"'; og.fillStyle = '#0b1218'; og.fillText('o Guardião do Bosque', px + 47, py + 266); og.fillStyle = '#f6f1e3'; og.fillText('o Guardião do Bosque', px + 44, py + 263);
  og.font = '600 26px "Pixelify Sans"'; og.fillStyle = '#8ad65a'; og.fillText('Jogue grátis no navegador', px + 44, py + 306);
  return {i512:icon(512, .7, true), i192:icon(192, .7, true), m512:icon(512, .5, true), apple:icon(180, .66, true), fav, og:o.toDataURL('image/png'), at:[gx, gy]};
}
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':420,'height':800})
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath('test.html'))
        await pg.wait_for_timeout(800)
        r = await pg.evaluate(JS)
        out = {'i512':'dist/icons/icon-512.png','i192':'dist/icons/icon-192.png','m512':'dist/icons/maskable-512.png','apple':'dist/icons/apple-touch-icon.png','fav':'dist/icons/favicon-32.png','og':'dist/og-image.png'}
        for k, path in out.items():
            open(path,'wb').write(base64.b64decode(r[k].split(',',1)[1]))
        print('grass at', r['at'], errs)
        await b.close()
asyncio.run(main())
