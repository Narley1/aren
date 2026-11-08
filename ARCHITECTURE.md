# Arquitetura — Aren, o Guardião do Bosque

Tudo está em `src/bosque-do-enxame.html` (3678 linhas). O script é uma IIFE única (`'use strict'`) sem módulos; as "seções" abaixo são blocos marcados por comentários `/* ---------------- nome ---------------- */`. As linhas valem para o fim da Etapa 2 — confira com `grep -n` antes de editar.

## Mapa do arquivo

| Linhas | Seção | Conteúdo |
|---|---|---|
| 1–135 | CSS | fonte embutida (base64, linha 4 — muito longa, evite imprimir), tokens `:root`, HUD, painéis, cartas de nível |
| 137–223 | HTML | `#app` > `canvas#c`, `#hud`, `#toast`, `#titleScreen`, overlays `#startScreen` (Como jogar), `#levelScreen`, `#pauseScreen`, `#overScreen` |
| 225–256 | início do script | `$`, `CTX` (contexto real) e `ctx` (contexto em uso: `CTX` ou a camada `LX`), `resize()` (escala inteira: `SCALE`, `VW`, `VH`), `sceneDirty`, `mk()` |
| 257–322 | kit de sprites | `cnv`, `painter` (px/rect/ell/sell/poly/line), `outlineC`, `flipC`, `tintC`, `EFrame` (quadro de inimigo com cópias branca/dourada/azul feitas no primeiro uso) |
| 323–402 | voadores | `gargoyleSprite`, `succubusSprite`, `wyvernSprite` (4 quadros de asa) |
| 403–856 | sprites 32 bits | `gridSprite`, `buildGrid`, `SPR32` (herói e inimigos desenhados em grade de caracteres) |
| 857–887 | **`BAL`** | todas as constantes de balanceamento soltas (ver abaixo) |
| 888–906 | dados de inimigos | `ET`, `SCHED`, geração de quadros (`EFrame`) |
| 907–966 | chefe | `dragonSprite`, `BOSS_T`, `ET.dragon`, `BONE_SPR` |
| 967–1055 | herói, espada, ícones | `HERO`, `swordBase`/`rotSet`/`drawSword` (48 rotações feitas sob demanda: `set.get(k)`), `ICONS`, shuriken (`SHUR`), joias |
| 1056–1086 | poderes | `UPG`, `UPG_ORDER`, `rl()`, `xpNeed()`, `isPickLevel()`, `nextPickLevel()`, `f1()` |
| 1087–1308 | chão e cenário | ruído, `GP`, `STAMPS`, blocos de chão de 128 px (`gCache`, geração fatiada: `pregenGround`, `chunkStart/chunkRows/chunkFinish`, `idleGround`), árvores/arbustos/pedras, `propsIn` (com cache `PROPS`) |
| 1309–1557 | utilitários e camada | `pixCircle` (cache `CIRC` fora da camada), **camada de software `LX`** (ver "Desempenho"), `pixLine`, sombras, `drawNum` (sprites por dígito), `fmt`, `store` |
| 1558–1895 | **som** | `SFX`: mixer, efeitos sintetizados, música procedural |
| 1896–1936 | estado | `G, P, W, E, B, EB, …`, `state`, `reset()`, `dropDead/dropExpired/dropOld` (remoção no lugar), grade espacial (`gridBuild` reaproveita arrays, `query`, `nearest`) |
| 1937–1959 | spawn | `spawn()`, `pickType()` |
| 1960–2111 | combate | `hit`, `kill`, `pickOptions`, `grant`, `applyItem`, `openLevelUp`, `chooseLevel`, `fireExplosion`, `blob`, `strike`, `hurt` |
| 2112–2385 | chefe | `startBoss`, `bossDirector`, `sealTick`, `holyStrike`, `bossDie`, `bossTick`, `drawBoss`, `pixRing`, `drawBossLayer`, `victory` |
| 2386–2421 | entrada | `keys`, `CODE_KEYS`, `clearInput`, teclado, `trapFocus`, blur, joystick de toque `J` |
| 2422–2768 | `update(dt)` | tempo, chefe, movimento, avisos, spawn/hordas, espada (`SWS`), shuriken, fogo, tempestade, meteoros, wisps, projéteis, inimigos, projéteis inimigos, maldições, ossos, joias, itens, efeitos |
| 2769–3077 | `render(dt)` → `drawScene` | chão (canvas real) → camada `LX`: joias/itens → chamas/marcas/maldições → sombras + entidades ordenadas por y (`YS`) → vida ambiente → noite/chefe (gradiente em cache, vai direto ao canvas) → espada → wisps → projéteis → efeitos (`FX_DRAW_MAX`) → números → joystick; `render` descarrega a camada no fim |
| 3078–3146 | vida ambiente | borboletas/folhas (`AMB`, `ambUpdate`, `ambDraw`), nuvens (`CLOUD`, feita em tempo ocioso) |
| 3147–3188 | HUD | `hud()`, `renderGear`, `toast` |
| 3189–3247 | fluxo | `start`, `togglePause`, `audioSync`, `gameOver`, `goTitle`, botões, humor da música, `visibilitychange` |
| 3248–3307 | extras do navegador | tela cheia, instalar app, wake lock (`keepAwake`), bestiário |
| 3308–3649 | tela de título | `buildTitleBg`, `TS2`, `drawNapScene`, `renderTitle`, `buildLogo` |
| 3650–3678 | loop | `idleGround` e `warmIdle` (tarefas em tempo ocioso), `frame(now)` com `requestAnimationFrame`, `dt` limitado a 0,05 s; fora de `play` a cena só é redesenhada ao mudar de estado ou após `resize` |

## Estados e transições

`state` ∈ `'menu' | 'play' | 'levelup' | 'pause' | 'over'`.

```
menu ──start()──▶ play ──G.pending>0 (frame)──▶ levelup ──chooseLevel()──▶ play
                  play ◀──togglePause()──▶ pause      (P/Esc, botão Pausa, perda de foco, aba oculta)
                  play ──hurt()→hp 0──▶ over (gameOver: painel após 500 ms)
                  play ──bossDie→2,8 s──▶ over (victory: painel após 900 ms)
over ──start()──▶ play        over ──goTitle()──▶ menu        pause ──Recomeçar──▶ play
```

- `frame()`: em `play` chama `update`, `ambUpdate`, `hud` e abre o nível se houver escolha pendente; em `menu` só anima. Desenha `renderTitle` no menu e `render` em `play`; em `levelup`/`pause`/`over` a cena é desenhada uma vez ao entrar no estado (ou depois de um `resize`, via `sceneDirty`) e o último quadro fica congelado atrás do painel.
- Toda abertura de painel e toda pausa chama `clearInput()` (zera teclas e joystick). `overTimer` guarda o timeout do painel de fim; `reset()` e `goTitle()` o cancelam.
- `audioSync()` decide se o `AudioContext` roda: só com a aba visível, fora da pausa e com Música ou Efeitos ligados.
- `keepAwake()` pede wake lock ao jogar e solta ao pausar/terminar; se a permissão chegar depois que a partida parou, é liberada na hora.

## Formas das entidades

- `G` (partida): `t, kills, gems, ups, xp, lvl, need, pending` (escolhas de poder pendentes), recargas `swCd, bmCd, frCd, stCd, mtCd`, `spawnT, waveT`, `swing`, `orbA`, `shake, flash, dark`, `unlocked, lateSeen` (Sets dos avisos), `boss`. (`since` é inicializado mas não é usado.)
- `P` (herói): `x, y, hp, maxHp` (em meios corações), `slow`, `inv` (invulnerável enquanto > 0), `dir, moving, anim, faceA`.
- `W`: nível de cada poder (`sword, boom, orb, fire, boots, magnet, heart, holy, storm, meteor`).
- Inimigo (`E[]`): `{type, d: ET[type], x, y, hp, kx, ky (empurrão), flash, anim, elite, cd, state, st, orbCd, boomCd, side, dead, stun?, face?, cast?, gig?}`.
- Chefe: inimigo com `d.boss`, mais `fade, lift, rise, untouch` e `bs = {st, t, last, a, ang, e, k, enraged, stun, sealT, seals, sealWin, sx, sy, orbitA}`.
- Projéteis do herói (`B[]`, campo `k`): `boom` (shuriken; `alive` = segundos de vida, some após `BAL.boom.maxLife`), `wave` (onda da Espada Sagrada; `hit` é um Set reaproveitado de `WAVE_SETS`), `fire`, `meteor`.
- Projéteis inimigos (`EB[]`): `arrow` (elfo), `wfire` (wyvern), `bb` (chefe). `MARKS` = ossos do chefe, `CURSES` = maldição da succubus.
- `GEMS {x, y, v, pull}`, `ITEMS {x, y, kind: 'life'|'apple'|'up', t}`, `FX` (`p, fl, sm, ring, bolt, xpl, beam`), `NUMS` (números de dano), `DECALS`, `BURNS` (chão em chamas).

## Objeto `BAL`

Linhas 857–887. Reúne os números que antes estavam soltos no código: `hero` (vida, velocidade 71,3 + 9 por nível de botas, invulnerabilidades), `sword` (fórmula do nível efetivo, dano, alcance, recarga), `cd` (recargas de shuriken/fogo/tempestade/meteoro), `firstLvl` (nerf do 1º nível: 0,55 poderes, 0,7 relíquias), `spawn` (intervalo e limite de 230 inimigos), `weights` (pesos de `pickType`), `elite` (chance e multiplicadores), `xpPerKill`, `hpScaleT` (vida × (1 + t/150)), `horde`, `drops` (meio coração, cristal, limite de 400 joias), `boss` (10:00, 60000 de vida, tempos dos selos), `boom` (volta do shuriken: `max(returnSpd, velocidade do herói × returnHeroMul)`, `maxLife` — Etapa 2, aprovado pelo dono). Tabelas `ET`, `SCHED` e `UPG` continuam como estão (já são dados). Mudar `BAL` muda o jogo: precisa de aprovação do dono.

## Chefe: Dragão Esqueleto

`G.boss = {phase, t, e}`.

1. **intro** (`startBoss` em `BOSS_T` = 600 s): apaga os inimigos, o spawn para; tremor, raios em 1,4/2,3/3,1 s; o dragão surge em 3 s (rugido); vira `fight` em 5,4 s.
2. **fight** (`bossTick`): orbita acima do herói; em `rest` escolhe um ataque diferente do anterior entre `spiral`, `rings`, `breath`, `bones`, `dive`. Abaixo de 50% de vida fica **enfurecido** (recargas × 0,72, mais braços/anéis/ondas, música `boss2`). Contato causa 2 de dano. **Selos de Luz** (`sealTick`): 3 selos aparecem (primeiro aos 14 s, ficam 22 s); ficar 1,6 s sobre cada um acende; os três acesos → `holyStrike` (−20% da vida máxima, atordoa 3,5 s, dano × 1,5 enquanto atordoado, 2 maçãs); depois voltam em 30 s (acertou) ou 24 s (falhou).
3. **won** (`bossDie`): animação de 2,8 s com explosões, 40 joias, `victory()`.

## Áudio

`SFX` (1558–1895) cria o `AudioContext` no primeiro toque/tecla (`SFX.init`). Mixer: `master` → compressor; barramentos `sfxDry/sfxWet` e `musDry/musWet` (reverb por convolução). Efeitos usam `ready(chave, recarga)` para não empilhar o mesmo som. Música procedural: `musicTick` a cada 40 ms com 300 ms de antecedência; instrumentos ocarina, flauta, alaúde (Karplus-Strong), tambores e drone.

Humores (`SFX.moodFn`, em "fluxo"): `title` (menu; calm a 60 bpm), `calm` (84 bpm, Ré maior), `combat` (104 bpm, ré menor, ≥ 16 inimigos a 130 px ou t > 210 s), `boss` (112 bpm + drone), `boss2` (enfurecido, 132 bpm), `silent` (intro do chefe e fim de jogo). A troca acontece no início do compasso (a cada 4 compassos, exceto trocas urgentes). Estados de Música/Efeitos ficam em `localStorage` (`bosque-enxame-musica`, `bosque-enxame-som`).

## Onde adicionar

- **Inimigo:** sprite em `SPR32` (grade) ou função de voador; entrada em `ET`; horário em `SCHED` (o bestiário se monta sozinho); se tiver IA nova, um ramo `d.ai === '...'` no laço de inimigos de `update`; peso em `pickType`/`BAL.weights`.
- **Arma/poder:** entrada em `UPG` + `UPG_ORDER`; campo em `W` dentro de `reset()`; ícone em `ICONS`; bloco de disparo em `update` (com recarga em `G` e números em `BAL`); desenho do projétil em `render`; incluir na lista de `renderGear`. Relíquias usam `late` e `rl()`.
- **Som:** função dentro de `SFX` usando `ready()`, `route(no, mixWet)` e os barramentos `sfx*`; exportar no `return` do `SFX`; chamar do jogo.
- **Constante de balanceamento:** em `BAL`, nunca solta no código.

## Desempenho

Medição: `python3 tests/perf.py` (ver o cabeçalho do script). Cenários `early` (30 s), `mid` (300 s), `late` (540 s, todos os poderes e relíquias no máximo) e `boss`, CPU 1x e 4x. O tempo de `update` é pequeno (< 1 ms a 4x); o custo está no `render`.

**Por que a camada de software.** No Chromium cada chamada de canvas tem custo fixo alto: `drawImage` de um canvas ~2,5 µs, `fillRect` ~0,5 µs, independente do tamanho (medido também com `--disable-gpu`). O jogo fazia ~12 000 `fillRect` de 1 px e ~850 `drawImage` por quadro no fim de partida. Agora:

- **`LX`** (camada de software, seção "utilitários e camada"): enquanto `render` roda, `ctx` aponta para `LX`, um objeto com a mesma API pequena que o jogo usa (`fillRect`, `drawImage(img, x, y)`, `fillStyle`, `globalAlpha`, `createRadialGradient`). Ele mistura (source-over, pré-multiplicado, em `Float32Array`) num buffer do tamanho da tela e, a cada descarga (`LX.flush`), converte só os trechos sujos de cada linha e faz um `putImageData` + um `drawImage`. Como source-over é associativo, o resultado é o mesmo de desenhar direto (diferença máxima medida: 13/255 por canal, arredondamento). Gradientes, `drawImage` recortado/escalado e sprites com mais de `LX_BIG` pixels descarregam a camada e vão ao canvas real (`LX.pass()`), mantendo a ordem. `fillRect` grande (> 8192 px: clarão, feixes) também vai ao canvas. Caminhos rápidos: `LX.px` (1 pixel; arco da espada, ondas, anéis), `LX.circle` (pixCircle), `LX.span`.
- **Regras para código novo de desenho:** use `ctx` (nunca `CTX`) dentro de `render`; `globalAlpha` fora de [0, 1] é ignorado como no canvas; sprites passados a `ctx.drawImage` não podem ser alterados depois do primeiro uso (o `LX` guarda os pixels em `LXS`, um `WeakMap` por canvas).
- **Caches:** `CIRC` (pixCircle fora da camada, por cor + forma), `DIGSPR` (dígitos por cor), `LXC` (cor → RGBA), `LXS` (pixels dos sprites), `SHADOWS`, `gCache` (até 72 blocos de chão), `PROPS` (props por célula, limpo acima de 4000), `NIGHT` (gradiente da noite/chefe), `YS` (lista ordenada por y e suas entradas), `SWS`/`WAVE_SETS`, arrays da grade espacial.
- **Feito sob demanda / em tempo ocioso:** cópias tingidas dos inimigos (`EFrame`), rotações da espada (`rotSet().get`), `CLOUD`; `warmIdle` os prepara depois que o título aparece. Blocos de chão: `pregenGround` com orçamento de 1,5 ms por quadro + `idleGround` (requestIdleCallback, `setTimeout` como reserva), o mais perto de onde a câmera está indo primeiro.
- **Orçamentos (CPU 4x, Chromium headless, fim de partida):** render ≤ ~12 ms em média e ≤ ~16 ms no p95; chão ≤ 1,5 ms por quadro; partículas desenhadas ≤ `FX_DRAW_MAX` = 1200 (pico medido ~610; o limite é só de segurança e não afeta a simulação). Pausado: ~0,1 ms de JS por quadro.
- Números de antes/depois no `CHANGELOG.md` (Etapa 2).

## Testes

`tests/smoke.py` copia o fonte para uma pasta temporária, injeta um hook antes do `})();` final que expõe `window.__t` (estado e funções internas) e `window.__seed` (troca `Math.random` por um PRNG semeado). Uma partida inteira roda dentro de um único `evaluate` síncrono, então `requestAnimationFrame` não interfere. A passada de determinismo desliga o áudio porque os efeitos consultam `AudioContext.currentTime` antes de sortear. O `render` também consome `Math.random` (tremor da tela, faíscas da espada) e é chamado pelo teste a cada 15 passos: otimizações de desenho precisam manter essas chamadas na mesma ordem.

`tests/perf.py` monta outra cópia instrumentada (internos em `window.__d()`, `Math.random` semeado, `requestAnimationFrame` embrulhado para medir o JS de cada quadro e poder ser parado com `?halt`).
