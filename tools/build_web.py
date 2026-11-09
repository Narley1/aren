"""Gera dist/ (PWA para o GitHub Pages) e aren-github-pages.zip a partir do fonte.

Uso:  python3 tools/build_web.py [--src caminho/bosque-do-enxame.html] [--out pasta/dist] [--zip arquivo.zip]
Sem --src: usa ./bosque-do-enxame.html se existir na pasta atual, senão src/bosque-do-enxame.html do repositório.
--out e --zip são relativos à pasta atual (padrão: dist/ e aren-github-pages.zip).
Ícones e og-image vêm de tools/gen_assets.py (gravados em dist/icons e dist/og-image.png); sem eles o build falha.
"""
import re, json, hashlib, os, zipfile, shutil, argparse
HERE = os.path.dirname(os.path.abspath(__file__))
_ap = argparse.ArgumentParser()
_ap.add_argument('--src'); _ap.add_argument('--out', default='dist'); _ap.add_argument('--zip', default='aren-github-pages.zip')
_args = _ap.parse_args()
SRC = _args.src or ('bosque-do-enxame.html' if os.path.exists('bosque-do-enxame.html') else os.path.join(HERE, '..', 'src', 'bosque-do-enxame.html'))
D = _args.out
os.makedirs(os.path.join(D, 'icons'), exist_ok=True)
SITE='https://narley1.github.io/aren/'
ICONS = ['icons/icon-192.png', 'icons/icon-512.png', 'icons/maskable-512.png', 'icons/apple-touch-icon.png', 'icons/favicon-32.png']
REQUIRED = ICONS + ['og-image.png']
PRECACHE = ['./', './index.html', './manifest.webmanifest'] + ['./' + f for f in ICONS]   # lista do sw.js
s=open(SRC, encoding='utf-8').read()
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
open(os.path.join(D,'index.html'),'w',encoding='utf-8').write(index)
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
open(os.path.join(D,'manifest.webmanifest'),'w',encoding='utf-8').write(json.dumps(manifest,ensure_ascii=False,indent=2))
sw=f'''/* Aren, o Guardião do Bosque — cache para jogar offline. Versão {ver} */
const CACHE = 'aren-{ver}';
const ASSETS = {json.dumps(PRECACHE)};
self.addEventListener('install', e => {{
  /* cache:'reload' skips the HTTP cache so a new version never precaches stale files */
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(ASSETS.map(u => new Request(u, {{cache: 'reload'}})))).then(() => self.skipWaiting()));
}});
self.addEventListener('activate', e => {{
  e.waitUntil(caches.keys().then(keys => Promise.all(keys.filter(k => k.startsWith('aren-') && k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
}});
self.addEventListener('fetch', e => {{
  const req = e.request;
  if (req.method !== 'GET' || new URL(req.url).origin !== location.origin) return;
  if (req.mode === 'navigate') {{
    /* the page: network first (new versions show on the next load), cache when offline */
    e.respondWith(caches.open(CACHE).then(cache => fetch(req).then(res => {{
      if (res && res.ok) {{ const u = new URL(req.url); e.waitUntil(cache.put(u.origin + u.pathname, res.clone())); }}
      return res;
    }}).catch(async () => (await cache.match(req, {{ignoreSearch: true}})) || (await cache.match('./index.html')) || Response.error())));
    return;
  }}
  /* other files: stale-while-revalidate */
  e.respondWith(caches.open(CACHE).then(async cache => {{
    const hit = await cache.match(req, {{ignoreSearch: true}});
    const net = fetch(req).then(res => {{ if (res && res.ok) cache.put(req, res.clone()); return res; }}).catch(() => null);
    if (hit) {{ e.waitUntil(net); return hit; }}
    return (await net) || Response.error();
  }}));
}});
'''
open(os.path.join(D,'sw.js'),'w',encoding='utf-8').write(sw)
readme_gh=f"""# Aren, o Guardião do Bosque

![Aren cercado pela horda no bosque](og-image.png)

### ▶ [Jogar agora no navegador]({SITE})

Aren, aprendiz de guardião, só tem a velha espada da família quando o enxame invade o bosque. Sobreviva às hordas por 15 minutos, recolha os poderes que as criaturas deixam cair e derrote os três chefes: o Paladino Possuído aos 5 minutos, o Lich Ancião aos 10 e o Dragão Esqueleto aos 15.

## Como jogar

- **Computador:** WASD ou setas para andar · **P** pausa · **F** tela cheia
- **Celular:** toque e arraste em qualquer lugar da tela
- As armas atacam sozinhas; você só se movimenta.

## O que tem no jogo

- Inimigos: goblins, gárgulas, hobgoblins, elfos negros, orcs, demônios, súcubos e wyverns; o Lich ainda invoca esqueletos
- Três chefes com ataques avisados no chão, duas fases e música própria; enquanto o Paladino ou o Lich vive, o relógio da partida para
- Joias viram experiência; nos níveis de escolha você pega um entre três poderes, cada um com estilo Corpo a corpo, A distância ou Híbrido: Espada, Martelo Sísmico, Aura de Espinhos, Shuriken Gigante, Arco Élfico, Fogo-fátuo, Magia de Fogo e os passivos Botas Ligeiras, Amuleto Ímã, Recipiente de Coração, Manoplas do Guerreiro e Grimório Arcano
- Relíquias que só os chefes soltam: Espada Sagrada (Paladino) e Cajado da Tempestade (Lich)
- No chão caem meios corações para curar e, raramente, cristais que aprimoram um poder que você já tem
- Pixel art no estilo 32 bits, música que muda com o momento do jogo (ocarina, flauta e alaúde) e efeitos sonoros sintetizados

## Instalar como app

Abra o link no celular. No Android (Chrome), toque em **Instalar app**; no iPhone (Safari), use **Compartilhar → Adicionar à Tela de Início**. Instalado, o jogo abre em tela cheia e funciona sem internet.

## Detalhes técnicos

Tudo roda num único `index.html` em HTML5 Canvas e JavaScript puro, sem bibliotecas: os sprites são desenhados em código, o áudio é gerado com a Web Audio API e a fonte vai embutida. O `manifest.webmanifest` e o `sw.js` deixam o jogo instalável e jogável offline.

Fonte: [Pixelify Sans](https://github.com/eifetx/Pixelify-Sans), licença SIL Open Font License 1.1 (veja `OFL.txt`).
"""
open(os.path.join(D,'README.md'),'w',encoding='utf-8').write(readme_gh)
ofl = os.path.join(os.path.dirname(os.path.abspath(SRC)), 'font', 'OFL.txt')
if os.path.exists(ofl): shutil.copyfile(ofl, os.path.join(D, 'OFL.txt'))
# Ícones são obrigatórios: o sw.js pré-cacheia todos com addAll, e um arquivo faltando quebra a instalação
# do service worker (sem offline e sem "Instalar app"). Melhor falhar aqui do que publicar assim.
falta = [f for f in REQUIRED if not os.path.exists(os.path.join(D, f))]
if falta:
    raise SystemExit('ERRO: faltam no build: ' + ', '.join(falta) + '\n'
                     f'Rode antes: python3 {os.path.join(HERE, "gen_assets.py")} --out {D}  (ou --from-main para copiar os do main)\n'
                     'Sem esses arquivos o service worker não instala (o jogo não funciona offline nem se instala como app).')
open(os.path.join(D,'.nojekyll'),'w').write('')
if os.path.exists(os.path.join(D,'LEIA-ME.md')): os.remove(os.path.join(D,'LEIA-ME.md'))
zp=_args.zip
if os.path.exists(zp): os.remove(zp)
with zipfile.ZipFile(zp,'w',zipfile.ZIP_DEFLATED,compresslevel=9) as z:
    for root,_,files in os.walk(D):
        for f in sorted(files):
            full=os.path.join(root,f); z.write(full, os.path.relpath(full,D))
print('version',ver)
for root,_,files in os.walk(D):
    for f in sorted(files): print(os.path.relpath(os.path.join(root,f),D), os.path.getsize(os.path.join(root,f)))
print('zip', os.path.getsize(zp))
