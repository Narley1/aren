# Arquitetura — Aren, o Guardião do Bosque

Tudo está em `src/bosque-do-enxame.html` (3352 linhas). O script é uma IIFE única (`'use strict'`) sem módulos; as "seções" abaixo são blocos marcados por comentários `/* ---------------- nome ---------------- */`. As linhas valem para o commit da Etapa 1 — confira com `grep -n` antes de editar.

## Mapa do arquivo

| Linhas | Seção | Conteúdo |
|---|---|---|
| 1–135 | CSS | fonte embutida (base64, linha 4 — muito longa, evite imprimir), tokens `:root`, HUD, painéis, cartas de nível |
| 137–223 | HTML | `#app` > `canvas#c`, `#hud`, `#toast`, `#titleScreen`, overlays `#startScreen` (Como jogar), `#levelScreen`, `#pauseScreen`, `#overScreen` |
| 225–252 | início do script | `$`, `ctx`, `resize()` (escala inteira: `SCALE`, `VW`, `VH` em pixels do jogo), `mk()` |
| 253–310 | kit de sprites | `cnv`, `painter` (px/rect/ell/sell/poly/line), `outlineC`, `flipC`, `tintC` |
| 311–390 | voadores | `gargoyleSprite`, `succubusSprite`, `wyvernSprite` (4 quadros de asa) |
| 391–844 | sprites 32 bits | `gridSprite`, `buildGrid`, `SPR32` (herói e inimigos desenhados em grade de caracteres) |
| 845–872 | **`BAL`** | todas as constantes de balanceamento soltas (ver abaixo) |
| 873–891 | dados de inimigos | `ET` (vida, velocidade, dano, raio, escala, joias, IA), `SCHED` (quando cada tipo aparece), geração de quadros com variações branca/dourada/azul |
| 892–951 | chefe | `dragonSprite`, `BOSS_T`, `ET.dragon`, `BONE_SPR` |
| 952–1036 | herói, espada, ícones | `HERO`, `swordBase`/`rotSet`/`drawSword` (48 rotações pré-calculadas), `ICONS`, shuriken (`SHUR`), joias |
| 1037–1067 | poderes | `UPG` (nome, nível máx., peso, `late` = relíquia liberada em t s, descrição), `UPG_ORDER`, `rl()`, `xpNeed()`, `isPickLevel()`, `nextPickLevel()`, `f1()` |
| 1068–1246 | chão e cenário | ruído, `GP` (paleta), `STAMPS`, `groundChunk` (blocos 128 px em cache), árvores/arbustos/pedras, `propsIn` |
| 1247–1283 | utilitários | `pixCircle`, `pixLine`, sombras, `drawNum`, `fmt`, `store` (recorde em `localStorage['bosque-enxame-best']`) |
| 1284–1621 | **som** | `SFX`: mixer, efeitos sintetizados, música procedural |
| 1622–1657 | estado | `G, P, W, E, B, EB, …`, `state`, `overTimer`, `reset()`, grade espacial (`gridBuild`, `query`, `nearest`) |
| 1658–1680 | spawn | `spawn()`, `pickType()` |
| 1681–1832 | combate | `hit`, `kill` (joias, xp, níveis, drops), `pickOptions`, `grant`, `applyItem`, `openLevelUp`, `chooseLevel`, `fireExplosion`, `strike`, `hurt` |
| 1833–2103 | chefe | `startBoss`, `bossDirector`, `sealTick`, `holyStrike`, `bossDie`, `bossTick`, `drawBoss`, `drawBossLayer`, `victory` |
| 2104–2139 | entrada | `keys`, `CODE_KEYS`, `clearInput`, teclado, `trapFocus`, blur, joystick de toque `J` |
| 2140–2483 | `update(dt)` | tempo, chefe, movimento, avisos, spawn/hordas, espada, shuriken, fogo, tempestade, meteoros, wisps, projéteis, inimigos, projéteis inimigos, maldições, ossos, joias, itens, efeitos |
| 2484–2766 | `render(dt)` | chão → joias/itens → chamas/marcas/maldições → sombras + entidades ordenadas por y → escurecimento do chefe → espada → wisps → projéteis → efeitos → joystick |
| 2767–2834 | vida ambiente | borboletas/folhas (`AMB`, `ambUpdate`, `ambDraw`), nuvens |
| 2835–2876 | HUD | `hud()` (só mexe no DOM quando o valor muda), `renderGear`, `toast` |
| 2877–2935 | fluxo | `start`, `togglePause`, `audioSync`, `gameOver`, `goTitle`, botões, humor da música (`SFX.moodFn`), `visibilitychange` |
| 2936–2995 | extras do navegador | tela cheia, instalar app, wake lock (`keepAwake`), bestiário |
| 2996–3337 | tela de título | fundo em camadas (`buildTitleBg`), cena do Aren cochilando (`TS2`, `drawNapScene`), `renderTitle`, logo (`buildLogo`) |
| 3338–3352 | loop | `frame(now)` com `requestAnimationFrame`, `dt` limitado a 0,05 s |

## Estados e transições

`state` ∈ `'menu' | 'play' | 'levelup' | 'pause' | 'over'`.

```
menu ──start()──▶ play ──G.pending>0 (frame)──▶ levelup ──chooseLevel()──▶ play
                  play ◀──togglePause()──▶ pause      (P/Esc, botão Pausa, perda de foco, aba oculta)
                  play ──hurt()→hp 0──▶ over (gameOver: painel após 500 ms)
                  play ──bossDie→2,8 s──▶ over (victory: painel após 900 ms)
over ──start()──▶ play        over ──goTitle()──▶ menu        pause ──Recomeçar──▶ play
```

- `frame()`: em `play` chama `update`, `ambUpdate`, `hud` e abre o nível se houver escolha pendente; em `menu` só anima. Desenha `renderTitle` no menu e `render` nos demais estados (o jogo fica congelado atrás dos painéis).
- Toda abertura de painel e toda pausa chama `clearInput()` (zera teclas e joystick). `overTimer` guarda o timeout do painel de fim; `reset()` e `goTitle()` o cancelam.
- `audioSync()` decide se o `AudioContext` roda: só com a aba visível, fora da pausa e com Música ou Efeitos ligados.
- `keepAwake()` pede wake lock ao jogar e solta ao pausar/terminar; se a permissão chegar depois que a partida parou, é liberada na hora.

## Formas das entidades

- `G` (partida): `t, kills, gems, ups, xp, lvl, need, pending` (escolhas de poder pendentes), recargas `swCd, bmCd, frCd, stCd, mtCd`, `spawnT, waveT`, `swing`, `orbA`, `shake, flash, dark`, `unlocked, lateSeen` (Sets dos avisos), `boss`. (`since` é inicializado mas não é usado.)
- `P` (herói): `x, y, hp, maxHp` (em meios corações), `slow`, `inv` (invulnerável enquanto > 0), `dir, moving, anim, faceA`.
- `W`: nível de cada poder (`sword, boom, orb, fire, boots, magnet, heart, holy, storm, meteor`).
- Inimigo (`E[]`): `{type, d: ET[type], x, y, hp, kx, ky (empurrão), flash, anim, elite, cd, state, st, orbCd, boomCd, side, dead, stun?, face?, cast?, gig?}`.
- Chefe: inimigo com `d.boss`, mais `fade, lift, rise, untouch` e `bs = {st, t, last, a, ang, e, k, enraged, stun, sealT, seals, sealWin, sx, sy, orbitA}`.
- Projéteis do herói (`B[]`, campo `k`): `boom` (shuriken), `wave` (onda da Espada Sagrada), `fire`, `meteor`.
- Projéteis inimigos (`EB[]`): `arrow` (elfo), `wfire` (wyvern), `bb` (chefe). `MARKS` = ossos do chefe, `CURSES` = maldição da succubus.
- `GEMS {x, y, v, pull}`, `ITEMS {x, y, kind: 'life'|'apple'|'up', t}`, `FX` (`p, fl, sm, ring, bolt, xpl, beam`), `NUMS` (números de dano), `DECALS`, `BURNS` (chão em chamas).

## Objeto `BAL`

Linhas 845–872. Reúne os números que antes estavam soltos no código: `hero` (vida, velocidade 71,3 + 9 por nível de botas, invulnerabilidades), `sword` (fórmula do nível efetivo, dano, alcance, recarga), `cd` (recargas de shuriken/fogo/tempestade/meteoro), `firstLvl` (nerf do 1º nível: 0,55 poderes, 0,7 relíquias), `spawn` (intervalo e limite de 230 inimigos), `weights` (pesos de `pickType`), `elite` (chance e multiplicadores), `xpPerKill`, `hpScaleT` (vida × (1 + t/150)), `horde`, `drops` (meio coração, cristal, limite de 400 joias), `boss` (10:00, 60000 de vida, tempos dos selos). Tabelas `ET`, `SCHED` e `UPG` continuam como estão (já são dados). Mudar `BAL` muda o jogo: precisa de aprovação do dono.

## Chefe: Dragão Esqueleto

`G.boss = {phase, t, e}`.

1. **intro** (`startBoss` em `BOSS_T` = 600 s): apaga os inimigos, o spawn para; tremor, raios em 1,4/2,3/3,1 s; o dragão surge em 3 s (rugido); vira `fight` em 5,4 s.
2. **fight** (`bossTick`): orbita acima do herói; em `rest` escolhe um ataque diferente do anterior entre `spiral`, `rings`, `breath`, `bones`, `dive`. Abaixo de 50% de vida fica **enfurecido** (recargas × 0,72, mais braços/anéis/ondas, música `boss2`). Contato causa 2 de dano. **Selos de Luz** (`sealTick`): 3 selos aparecem (primeiro aos 14 s, ficam 22 s); ficar 1,6 s sobre cada um acende; os três acesos → `holyStrike` (−20% da vida máxima, atordoa 3,5 s, dano × 1,5 enquanto atordoado, 2 maçãs); depois voltam em 30 s (acertou) ou 24 s (falhou).
3. **won** (`bossDie`): animação de 2,8 s com explosões, 40 joias, `victory()`.

## Áudio

`SFX` (1284–1621) cria o `AudioContext` no primeiro toque/tecla (`SFX.init`). Mixer: `master` → compressor; barramentos `sfxDry/sfxWet` e `musDry/musWet` (reverb por convolução). Efeitos usam `ready(chave, recarga)` para não empilhar o mesmo som. Música procedural: `musicTick` a cada 40 ms com 300 ms de antecedência; instrumentos ocarina, flauta, alaúde (Karplus-Strong), tambores e drone.

Humores (`SFX.moodFn`, em "fluxo"): `title` (menu; calm a 60 bpm), `calm` (84 bpm, Ré maior), `combat` (104 bpm, ré menor, ≥ 16 inimigos a 130 px ou t > 210 s), `boss` (112 bpm + drone), `boss2` (enfurecido, 132 bpm), `silent` (intro do chefe e fim de jogo). A troca acontece no início do compasso (a cada 4 compassos, exceto trocas urgentes). Estados de Música/Efeitos ficam em `localStorage` (`bosque-enxame-musica`, `bosque-enxame-som`).

## Onde adicionar

- **Inimigo:** sprite em `SPR32` (grade) ou função de voador; entrada em `ET`; horário em `SCHED` (o bestiário se monta sozinho); se tiver IA nova, um ramo `d.ai === '...'` no laço de inimigos de `update`; peso em `pickType`/`BAL.weights`.
- **Arma/poder:** entrada em `UPG` + `UPG_ORDER`; campo em `W` dentro de `reset()`; ícone em `ICONS`; bloco de disparo em `update` (com recarga em `G` e números em `BAL`); desenho do projétil em `render`; incluir na lista de `renderGear`. Relíquias usam `late` e `rl()`.
- **Som:** função dentro de `SFX` usando `ready()`, `route(no, mixWet)` e os barramentos `sfx*`; exportar no `return` do `SFX`; chamar do jogo.
- **Constante de balanceamento:** em `BAL`, nunca solta no código.

## Testes

`tests/smoke.py` copia o fonte para uma pasta temporária, injeta um hook antes do `})();` final que expõe `window.__t` (estado e funções internas) e `window.__seed` (troca `Math.random` por um PRNG semeado). Uma partida inteira roda dentro de um único `evaluate` síncrono, então `requestAnimationFrame` não interfere. A passada de determinismo desliga o áudio porque os efeitos consultam `AudioContext.currentTime` antes de sortear.
