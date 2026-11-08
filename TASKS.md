# Tarefas

## Etapa 1 — concluída

- [x] Teclas presas: `clearInput()` em blur, aba oculta, pausa e painéis; pausa automática ao perder o foco
- [x] Áudio suspenso com a aba oculta em qualquer estado (`audioSync`)
- [x] Timeouts do painel de fim/vitória cancelados em `reset`/`goTitle`
- [x] Wake lock liberado se chegar depois da pausa/fim
- [x] Botões do HUD sem foco após clique de mouse/toque
- [x] WASD por `e.code` (AZERTY)
- [x] Painel de pausa: `role="dialog"`, `aria-modal`, Tab preso, HUD `inert`
- [x] `build_web.py`: cria `dist/`, `--src/--out/--zip`, copia `OFL.txt`
- [x] Service worker: pré-cache `cache:'reload'`, navegação network-first
- [x] Limpeza de código morto (humanoides 16 bits, `flipH`, `rot90`, `seeded`, primeiro poder, goblins do menu, `tint`/`hexA` duplicados)
- [x] Objeto `BAL` com as constantes de balanceamento (valores iguais, determinismo verificado)
- [x] `tests/smoke.py` (24 verificações + determinismo); `tests/check.js` removido
- [x] Documentação: `CLAUDE.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `CHANGELOG.md`, `TASKS.md`, `README.md`

## Pendências conhecidas

- [ ] Publicar no `main` — **aguarda aprovação do Narley** (o site no ar ainda é o build de 26/10)
- [ ] Rodar `tools/gen_assets.py` + `build_web.py` e conferir o `dist/` antes de publicar
- [ ] Testar em aparelho real: wake lock, áudio ao trocar de app, foco do painel de pausa com leitor de tela (só testado em Chromium headless)
- [ ] `tests/test.html`, `tests/shot*.py` e `tests/legacy/` são cópias/scripts antigos; `test.html` está desatualizado em relação ao fonte — decidir se gera a partir do `src` ou remove
- [ ] `G.since` é inicializado e nunca usado (inofensivo; remover junto com a Etapa 2)

## Próxima: Etapa 2 — Desempenho

Ver `ROADMAP.md`.
