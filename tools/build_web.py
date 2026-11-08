import re, json, hashlib, os, zipfile, datetime
SRC='bosque-do-enxame.html'; D='dist'
SITE='https://narley1.github.io/aren/'
s=open(SRC).read()
title=re.search(r'<title>(.*?)</title>',s).group(1)
body=s.replace(re.search(r'<title>.*?</title>\n',s).group(0),'',1)
DESC='Aren, aprendiz de guardião, enfrenta hordas de goblins, demônios e um Dragão Esqueleto. Sobrevivência em pixel art 32 bits, direto no navegador.'
head=f'''<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover, user-scalable=no">
<title>{title}</title>
<meta name="description" content="{DESC}">
<meta name="theme-color" content="#13202a">
<meta name="color-scheme" content="dark">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="Aren">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{DESC}">
<link rel="canonical" href="{SITE}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:locale" content="pt_BR">
<meta name="twitter:card" content="summary_large_image">
<style>
:root{{padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px);box-sizing:border-box}}
body{{margin:0;font:14px system-ui,sans-serif}}
img{{max-width:100%}}
[hidden]{{display:none!important}}
</style>
</head>
<body>
<noscript><p style="color:#f6f1e3;background:#13202a;padding:24px;font:16px system-ui">Ative o JavaScript para jogar.</p></noscript>
'''
tail='''
<script>
if ('serviceWorker' in navigator && location.protocol.startsWith('http')) {
  addEventListener('load', () => { navigator.serviceWorker.register('sw.js').catch(() => {}); });
}
</script>
</body>
</html>
'''
index=head+body+tail
open(os.path.join(D,'index.html'),'w').write(index)
ver=hashlib.sha1(index.encode()).hexdigest()[:10]
manifest={
  "id":"./","name":title,"short_name":"Aren","description":DESC,"lang":"pt-BR",
  "start_url":"./","scope":"./","display":"fullscreen","display_override":["fullscreen","standalone"],
  "orientation":"any","background_color":"#13202a","theme_color":"#13202a","categories":["games"],
  "icons":[
    {"src":"icons/icon-192.png","sizes":"192x192","type":"image/png","purpose":"any"},
    {"src":"icons/icon-512.png","sizes":"512x512","type":"image/png","purpose":"any"},
    {"src":"icons/maskable-512.png","sizes":"512x512","type":"image/png","purpose":"maskable"}
  ]
}
open(os.path.join(D,'manifest.webmanifest'),'w').write(json.dumps(manifest,ensure_ascii=False,indent=2))
sw=f'''/* Aren, o Guardião do Bosque — cache para jogar offline. Versão {ver} */
const CACHE = 'aren-{ver}';
const ASSETS = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png', './icons/maskable-512.png', './icons/apple-touch-icon.png', './icons/favicon-32.png'];
self.addEventListener('install', e => {{
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS)).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('aren-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  e.respondWith(caches.open(CACHE).then(async cache => {{
    const hit = await cache.match(req, {{ignoreSearch: true}});
    const net = fetch(req).then(res => {{ if (res && res.ok) cache.put(req, res.clone()); return res; }}).catch(() => null);
    if (hit) {{ e.waitUntil(net); return hit; }}
    const res = await net;
    return res || (req.mode === 'navigate' ? cache.match('./index.html') : Response.error());
  }}));
}});
'''
open(os.path.join(D,'sw.js'),'w').write(sw)
readme_gh=f"""# Aren, o Guardião do Bosque

![Aren cercado pela horda no bosque](og-image.png)

### ▶ [Jogar agora no navegador]({SITE})

Aren, aprendiz de guardião, só tem a velha espada da família quando o enxame invade o bosque. Sobreviva às hordas, recolha os poderes que as criaturas deixam cair e enfrente o Dragão Esqueleto aos 10 minutos.

## Como jogar

- **Computador:** WASD ou setas para andar · **P** pausa · **F** tela cheia
- **Celular:** toque e arraste em qualquer lugar da tela
- A espada ataca sozinha quando há inimigos por perto.

## O que tem no jogo

- 9 tipos de inimigo: goblins, gárgulas, hobgoblins, elfos negros, orcs, demônios, succubus, wyverns e o Dragão Esqueleto
- Sistema de experiência: nos níveis 3, 5 e depois a cada 5 níveis, escolha entre dois poderes (espada, shuriken gigante, Will-o'-Wisp, magia de fogo, botas, amuleto ímã e recipiente de coração), cada um com 5 níveis
- No chão caem meios corações para curar e, raramente, cristais que aprimoram um poder que você já tem
- Relíquias lendárias com 3 níveis depois dos 5 minutos: Espada Sagrada, Cajado da Tempestade e Chuva de Meteoros
- Chefe final com padrões de ataque próprios e a mecânica dos Selos de Luz
- Pixel art no estilo 32 bits, música que muda com o momento do jogo (ocarina, flauta e alaúde) e efeitos sonoros sintetizados

## Instalar como app

Abra o link no celular. No Android (Chrome), toque em **Instalar app**; no iPhone (Safari), use **Compartilhar → Adicionar à Tela de Início**. Instalado, o jogo abre em tela cheia e funciona sem internet.

## Detalhes técnicos

Tudo roda num único `index.html` em HTML5 Canvas e JavaScript puro, sem bibliotecas: os sprites são desenhados em código, o áudio é gerado com a Web Audio API e a fonte vai embutida. O `manifest.webmanifest` e o `sw.js` deixam o jogo instalável e jogável offline.

Fonte: [Pixelify Sans](https://github.com/eifetx/Pixelify-Sans), licença SIL Open Font License 1.1 (veja `OFL.txt`).
"""
open(os.path.join(D,'README.md'),'w').write(readme_gh)
open(os.path.join(D,'.nojekyll'),'w').write('')
if os.path.exists(os.path.join(D,'LEIA-ME.md')): os.remove(os.path.join(D,'LEIA-ME.md'))
zp='aren-github-pages.zip'
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for root,_,files in os.walk(D):
        for f in sorted(files):
            full=os.path.join(root,f); z.write(full, os.path.relpath(full,D))
print('version',ver)
for root,_,files in os.walk(D):
    for f in sorted(files): print(os.path.relpath(os.path.join(root,f),D), os.path.getsize(os.path.join(root,f)))
print('zip', os.path.getsize(zp))
