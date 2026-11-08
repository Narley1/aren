# Aren, o Guardião do Bosque — código-fonte (branch `dev`)

Este branch guarda o código-fonte do jogo. **Não é publicado**: o GitHub Pages serve só o branch `main`, que contém apenas o build (`dist/`). Publicar depende da aprovação do dono.

- `src/bosque-do-enxame.html` — o jogo inteiro (HTML5 Canvas + JS puro, arquivo único). Fonte da verdade.
- `src/font/` — Pixelify Sans (OFL).
- `tools/build_web.py` — gera `dist/` (PWA: index.html, manifest, service worker, README, OFL.txt) e `aren-github-pages.zip`. Ex.: `python3 tools/build_web.py --src src/bosque-do-enxame.html`.
- `tools/gen_assets.py` — ícones e og-image (gravados em `dist/`).
- `tools/parts/` — trechos de desenvolvimento (tela de título, áudio, sprites) já incorporados ao HTML; mantidos como histórico.
- `tests/smoke.py` — teste principal: simulação headless completa no Chromium, testes das correções e verificação de determinismo. `python3 tests/smoke.py`.
- `tests/perf.py` — desempenho por cenário; `tests/balance/` — simulador de balanceamento com bot (políticas por estilo).
- `tests/legacy/`, `tests/shot*.py`, `tests/test.html` — scripts e cópias antigas, mantidos como histórico.

Documentação:

- [`CLAUDE.md`](CLAUDE.md) — como trabalhar no projeto (branches, comandos, regras).
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — mapa do código, estados, entidades, `BAL`, chefe, áudio.
- [`ROADMAP.md`](ROADMAP.md) — etapas planejadas.
- [`TASKS.md`](TASKS.md) — checklist atual.
- [`CHANGELOG.md`](CHANGELOG.md) — histórico.

Versão do fonte: v21 + Etapas 1–4 (correções, desempenho, partida de 15 minutos, poderes por estilo), 08/11/2026. O site no ar ainda é o build de 26/10.
