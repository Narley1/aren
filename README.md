# Aren, o Guardião do Bosque — código-fonte (branch `dev`)

Este branch guarda o código-fonte do jogo. **Não é publicado**: o GitHub Pages serve só o branch `main`, que contém apenas o build (`dist/`).

- `src/bosque-do-enxame.html` — o jogo inteiro (HTML5 Canvas + JS puro, arquivo único). Fonte da verdade.
- `src/font/` — Pixelify Sans (OFL).
- `tools/build_web.py` — gera `dist/` (PWA: index.html, manifest, service worker, ícones) a partir do fonte. Rodar a partir de uma pasta que contenha `bosque-do-enxame.html` e `font/`.
- `tools/gen_assets.py` — ícones e og-image.
- `tools/parts/` — trechos de desenvolvimento (tela de título, áudio, sprites) já incorporados ao HTML; mantidos como histórico.
- `tests/` — wrapper `test.html` e scripts Playwright (simulação headless, screenshots). `tests/legacy/` são scripts de verificação usados ao longo das versões.

Versão do fonte: v21 (artifact), 08/11/2026. O site no ar ainda é o build de 26/10.
