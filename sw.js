/* Aren, o Guardião do Bosque — cache para jogar offline. Versão cfb4abc45c */
const CACHE = 'aren-cfb4abc45c';
const ASSETS = ["./", "./index.html", "./manifest.webmanifest", "./icons/icon-192.png", "./icons/icon-512.png", "./icons/maskable-512.png", "./icons/apple-touch-icon.png", "./icons/favicon-32.png"];
self.addEventListener('install', e => {
  /* cache:'reload' skips the HTTP cache so a new version never precaches stale files */
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(u => new Request(u, {cache: 'reload'})))).then(() => self.skipWaiting()));
});
self.addEventListener('activate', e => {
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('aren-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {
    /* the page: network first (new versions show on the next load), cache when offline */
    e.respondWith(caches.open(CACHE).then(cache => fetch(req).then(res => {
      if (res && res.ok) { const u = new URL(req.url); e.waitUntil(cache.put(u.origin + u.pathname, res.clone())); }
      return res;
    }).catch(async () => (await cache.match(req, {ignoreSearch: true})) || (await cache.match('./index.html')) || Response.error())));
    return;
  }
  /* other files: stale-while-revalidate */
  e.respondWith(caches.open(CACHE).then(async cache => {
    const hit = await cache.match(req, {ignoreSearch: true});
    const net = fetch(req).then(res => { if (res && res.ok) cache.put(req, res.clone()); return res; }).catch(() => null);
    if (hit) { e.waitUntil(net); return hit; }
    return (await net) || Response.error();
  }));
});
