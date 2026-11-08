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
- [ ] `G.since` é inicializado e nunca usado (inofensivo; não removido na Etapa 2 para não misturar limpeza com desempenho)

## Etapa 2 — Desempenho — concluída

- [x] `tests/perf.py` (cenários early/mid/late/boss, CPU 1x/4x, rAF real, contagem de chamadas, boot, pausa)
- [x] Camada de software `LX` (efeitos, sprites pequenos, arco da espada, ondas, anéis, maldições, números)
- [x] `pixCircle`/`drawNum` com sprites em cache fora da camada; culling de joias, itens e inimigos
- [x] Chão em fatias + tempo ocioso, à frente do movimento
- [x] Listas compactadas no lugar, grade espacial/lista por y/props/rastros/Sets reaproveitados, gradiente em cache
- [x] Cena congelada em pausa/escolha/fim
- [x] Inicialização: tingidos, rotações da espada e nuvem sob demanda / tempo ocioso
- [x] Shurikens voltam mais rápido (aprovado pelo Narley)
- [x] Determinismo idêntico em todos os commits antes do shuriken; comparação de imagem (máx. 13/255)

## Pendências da Etapa 2

- [ ] Medir num celular real (Android intermediário): FPS no fim de partida e no chefe, aquecimento após alguns minutos
- [ ] `early` ficou com render médio maior (custo fixo da camada + geração do chão), ainda a 60 fps; se incomodar no celular, desligar a camada quando houver pouca coisa na tela
- [ ] O rastro do shuriken e as partículas ainda são objetos novos por disparo (pool não foi necessário pelas medições)

## Etapa 3 — Balanceamento e 15 minutos — concluída no `dev`

- [x] Simulador `tests/balance/` (antes/depois em 96 partidas cada)
- [x] Marcos `BOSSES` (5:00 Paladino, 10:00 Lich, 15:00 Dragão); guardiões provisórios soltam a relíquia
- [x] Relíquias só dos chefes, sem desbloqueio por tempo; Chuva de Meteoros removida
- [x] Joias = experiência (por tipo de inimigo), fusão de joias acima do limite, nova curva
- [x] 3 opções; escolhas nos níveis 2, 3, 5, 7, 10 e a cada 3
- [x] Agenda/vida/elites/hordas até 15:00, spawn reduzido com guardião; quedas de cristal/coração caem com o tempo
- [x] Nerf do 1º nível 0,75/0,85
- [x] Dragão 20000 de vida, selos 7%, espada alcança quando atordoado
- [x] Como jogar, bestiário (chefes com horário), barra de chefe com nome

## Pendências da Etapa 3 (para o Narley testar)

- [ ] Jogar 2–3 partidas: o ritmo das escolhas (~40 s) e o pico de 7:00–9:00 (Wyvern + hordas de demônios + elites) parecem bons?
- [ ] Guardiões provisórios: vida (Paladino ~2600, Lich ~6000 na hora em que surgem) — fáceis/difíceis demais? Se não matar, a relíquia se perde às 15:00
- [ ] Quedas de cristal/meio coração agora caem depois dos 4:00 (decisão nossa para a partida longa — confirmar)
- [ ] Dragão: com build cheia a luta dura ~2 min; com build média ~4 min. A espada no dragão atordoado é perceptível?
- [ ] Flechas dos elfos são a maior fonte de dano para o bot; ver se para humanos também
- [ ] Bot: a política "balanced" (espalha níveis) morre cedo (~4:00); builds só de espada morrem ~7:00
- [ ] Etapa 5 vai trocar os guardiões por Paladino e Lich de verdade (`GUARD_EV`, ver `ARCHITECTURE.md`)
