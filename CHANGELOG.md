# Changelog

## Áudio — rodada 4 (09/11/2026, branch `dev`, não publicado)

Notas do Narley no laboratório da rodada 3 e o lote 3 de sons dos monstros. Medido com `tools/sfx_levels.py` (cada som sozinho pelo mixer do jogo; volume = RMS da janela de 150 ms mais alta, comparado com a explosão do fogo, ~−29,7 dBFS). Eu não ouço: a aprovação é do Narley, no laboratório.

- **Risada da súcubo:** sem o ronronar "mrrr" do começo; o resto é o mesmo e começa 0,3 s antes (onde estava o ronronar). O volume medido caiu de +4,2 para −0,9 dB porque o ronronar era o trecho mais alto; o resto não mudou de nível.
- **Hobgoblin:** o grunhido curto saiu (nota 1); a voz é sempre o rosnado aprovado (nota 5), com pequenas variações de altura, duração, pico e rolado. Linha `v_hobgoblin` removida do catálogo.
- **Vida baixa:** mais +4 dB (−6,8 → −2,8), a mesma batida suave.
- **Morte da serpe-dragão (terceira tentativa):** grito curto de dragão pequeno, com o timbre do rugido novo encolhido para ~0,2 s e mais agudo, e o corpo pesado caindo no chão (−4,3 dB, 12 nós). Opção B só no laboratório (`kill_wyvern_b`): chiado de réptil, o fogo de dentro apagando em estalos e um baque leve (−3,3 dB, 11 nós). A versão A é a que está no jogo.
- **Monstros, lote 3 (vozes de presença):** demônio (respiração quente e rosnado grave; −8,4 dB, 11 nós), serpe-dragão (asas grandes de couro, mais lentas e graves que as da gárgula, −9,5 dB, 5 nós; ~1 em 3 com um grasnido "kraa-ak", −10,8 dB, 12 nós) e súcubo (asas leves e rápidas, −10,8 dB, 4 nós; ~1 em 3 com um suspiro soprado, −8,3 dB, 12 nós). Intervalos por tipo: demônio 5–10 s, serpe 3,5–7,5 s, súcubo 4–9 s; depois dessas vozes os outros tipos esperam 0,9/0,9/0,7 s (antes 0,5 para todos).
- **Demônio:** o rosnado e a risada (que continua com o temporizador antigo) nunca tocam juntos: dentro do `SFX`, o rosnado não toca enquanto a risada dura, e uma risada que chegue durante um rosnado começa logo depois dele (verificado no espectrograma: rosnado até ~0,9 s, risada a partir de ~1,15 s).
- **Desempenho:** 20 demônios + 15 serpes + 15 súcubos perto de Aren por ~10 s: 11 vozes, 105 nós de voz, no máximo 24 em meio segundo (as risadas antigas criam 85 e 108 nós cada); com os 6 tipos juntos (30 goblins, 15 gárgulas, 15 hobgoblins, 15 demônios, 10 serpes, 10 súcubos): 20 vozes, 146 nós, no máximo 22 em meio segundo.
- **Determinismo:** `smoke.py --compare` IDENTICAL; `smoke.py` 0 falhas.
- **Laboratório:** "Antes" = commit fde193b (rodada 3), notas em `avaliacoes_r4`, nota anterior de `avaliacoes_r3`, depois `avaliacoes_r2`, depois a rodada 1 (`avaliacoes`); as coleções antigas só são lidas.

## Áudio — rodada 3 (08/11/2026, branch `dev`, não publicado)

Notas do Narley no laboratório da rodada 2 e o primeiro lote de sons dos monstros. Medido com `tools/sfx_levels.py` (cada som sozinho pelo mixer do jogo; volume = RMS da janela de 150 ms mais alta, comparado com a explosão do fogo, ~−29,7 dBFS). Eu não ouço: a aprovação é do Narley, no laboratório.

- **Removido:** som da Shuriken voltando (`boomCatch`); o arremesso continua.
- **Mais curto:** risada do demônio com 4 "ha" em vez de 6 (~30% mais curta).
- **Refeitos:** morte da gárgula (pedra rachando e esfarelando) e da serpe-dragão (guincho curto, baque, asas caindo), com receita própria em `KILL_FX`; Cajado da Tempestade com zumbido elétrico "bzzzt" (−6,1 → −4,4 dB); risada da súcubo mais felina e feminina (ronronar, "nyaa", risinhos soprados, "hmm") e mais baixa (+10,2 → +4,4 dB).
- **Volume:** vida baixa +4,5 dB (−10,8 → −6,6); salto do Paladino +5 dB (−13,1 → −8,6 medido). Preparar o giro ficou igual, como ele escolheu.
- **Monstros, lote 1 (vozes de presença):** goblin (risadinha "he-he-he"), gárgula (asas de pedra; ~1 em 3 com guincho rouco) e hobgoblin (grunhido; quase metade das vezes um rosnado), com um deles a menos de 150 px de Aren. Um temporizador por tipo (`VOX`/`voxTick`), intervalo de 2,5 a 7,5 s sorteado por um gerador próprio (o jogo não usa `Math.random` para isso); variação de altura e de sílabas dentro de `SFX.voice`. −10 a −8 dB em relação à explosão, até 12 nós.
- **Desempenho:** 40 goblins perto de Aren por ~10 s: 5 chamadas de voz (uma barrada pela recarga do `SFX`), 24 nós de voz; com 40 goblins + 20 gárgulas + 20 hobgoblins: 12 vozes, 100 nós (no máximo 22 em meio segundo).
- **Determinismo:** `smoke.py --compare` IDENTICAL; `smoke.py` 0 falhas.
- **Laboratório:** "Antes" = commit 10da437 (rodada 2 aprovada), notas em `avaliacoes_r3`, nota anterior vinda de `avaliacoes_r2` (ou de `avaliacoes`); commit e coleções configuráveis (`--before`, `--store`, `--prev-store`); o catálogo só marca `estado` nos sons desta rodada.

## Áudio — rodada 2 (08/11/2026, branch `dev`, não publicado)

Pedidos do Narley no Laboratório de Som. Medido com `tools/sfx_levels.py` (cada som sozinho pelo mixer do jogo; volume = RMS da janela de 150 ms mais alta). Eu não ouço os sons: a aprovação é do Narley, no laboratório.

- **Mix:** barramento de música −6 dB (constante `MUS` = 0,17; antes 0,34), também nas vinhetas. Cristal e relíquia −3 dB; escudo raspando +4,5 dB.
- **Refeitos:** explosão de fogo (volume mantido, é a referência; varia ±5% de altura), Martelo Sísmico e tremor, Arco Élfico (de −11 para −6 dB), risada do demônio (voz mais aguda, de +17 para +6 dB), maldição da súcubo (com risinho felino no máximo a cada 1,4 s), aterrissagem, grito, pancada, giro (de −14 para −6 dB), lâminas, lâmina disparada, espírito e morte do Paladino, teletransporte, gelo (preparar e acertar), aviso dos relâmpagos (de −12 para −8 dB), raio do Lich, rugidos do dragão (de +14..+17 para +2..+7 dB; a morte do dragão mantém o rugido antigo) e impacto do mergulho (de +10,5 para +5,5 dB).
- **Novos:** dano em Aren, vida baixa (batida de coração a cada 2,4 s com 1 coração ou menos), joia (sobe de tom em coletas seguidas), meio coração e coração, nível sem escolha, golpe da Espada (mais agudo por nível), Shuriken, disparo do fogo, Fogo-fátuo, Cajado da Tempestade, Espada Sagrada, flecha dos elfos, fogo da serpe, elite, morte de inimigo com timbre por tipo, botões, cartas, pausa; vitória e derrota tocam pelos Efeitos quando a Música está desligada.
- **Pausa:** com a pausa visível o áudio é suspenso 0,3 s depois, para a dica de pausa tocar; com a aba oculta continua imediato.
- **Desempenho:** sons frequentes com recarga e até 7 nós; 30 mortes + 30 joias em 1 s criam 105 nós.
- **Determinismo:** `smoke.py --compare` IDENTICAL; o jogo não sorteia nada para o som.
- **Ferramentas:** catálogo com `estado`; laboratório com Antes/Agora (módulo do commit 01c5ba5), notas em `avaliacoes_r2`; `sfx_levels.py --rev` mede versões antigas.

## Decisões do Narley (08/11/2026)

- Limite de armas passa de 4 para **5** (`BAL.pick.maxWeapons`).
- Confirmados: pesos novos das escolhas, nome "Fogo-fátuo" (haverá opção em inglês no futuro), menos corações e cristais depois dos 4:00, serpe-dragão mais rara ao aparecer.
- Grimório Arcano mais fraco: +8% de dano e recarga 5% menor por nível (era +10% e 7%); no nível 5, +40% de dano e −25% de recarga. O Fogo-fátuo (híbrido) continua recebendo metade.

## Etapa 5 — chefes: Paladino Possuído e Lich Ancião (novembro de 2026, branch `dev`, não publicado)

Pedido do Narley: trocar os guardiões provisórios das 5:00 e 10:00 por chefes de verdade. Medido com `tests/balance/` (bot, Chromium headless, `dt` = 1/30 s), já com o limite de 5 armas e o Grimório reduzido. O bot não é um humano: os números comparam versões e estilos. Amostras de 24 sementes variam bastante (o mesmo código deu 33% e 58% de mortes do corpo a corpo em duas rodadas), por isso os números das lutas abaixo juntam 48 sementes.

### Paladino Possuído (5:00)
- Armadura vazia de prata manchada com detalhes dourados, capa e penacho carmesim rasgados, escudo em pipa, olhos verdes no visor e fiapos roxos saindo das juntas; ~2,5× a altura de Aren, desenhada em código (passo de 4 quadros, poses de investida, golpe, agachado e giro; espadão pré-rotacionado à parte).
- Chega caindo do céu sobre um círculo de pouso; cartão "Chefe · 5:00".
- **Investida com escudo:** faixa no chão (0,85 s, bordas que andam e setas que marcham) e corrida de 175 px; acerto = 1 coração + empurrão; depois fica atordoado 1,15 s (estrelas).
- **Giro da espada:** anel no chão que se enche (0,65 s) e giro de 0,7 s (raio 44).
- **Salto esmagador:** pula para onde Aren estava; círculo de pouso com anel que fecha e mira (0,95 s); 1½ coração no centro, onda de choque; fica 1,25 s com a espada no chão.
- **Lâminas fantasmas:** 3 lâminas (5 na fase 2) aparecem sobre ele apontando para Aren e saem uma a uma a 95 px/s.
- **Fase 2 (50%):** 1,8 s invulnerável, o espírito sai da armadura e fica pairando sobre ela, olhos violeta; ataques 15% mais rápidos de telegrafar e intervalos menores.
- Depois de cada ataque ele não causa dano de contato: é a janela do corpo a corpo.
- **Morte:** a armadura desaba em pedaços (elmo quica, ombreiras e escudo voam), o espírito sobe com um grito e some; a Espada Sagrada cai quando a animação termina.
- Vida 2300 (o guardião tinha ~2570).

### Lich Ancião (10:00)
- Esqueleto de mago com capuz e coroa de osso e ouro, manto roxo com runas verde-água, cajado com cristal; flutua; sobe do chão numa névoa; cartão "Chefe · 10:00".
- **Teleporte:** some numa nuvem e reaparece a 90–125 px de Aren (quando Aren fica a menos de 75 px por 0,6 s ou a cada 7 s); mantém ~130 px de distância.
- **Orbes de gelo:** 3 (5) orbes em leque; acerto = ½ coração + Aren 40% mais lento por 1,6 s, azulado.
- **Chuva de relâmpagos:** 5 (8) círculos, um sobre Aren, com símbolo de raio e anel que fecha (1,05 s).
- **Relâmpago em cadeia:** feixe tracejado que segue Aren e trava (fica grosso e pisca) 0,3 s antes do raio; 3 feixes na fase 2.
- **Invocar esqueletos:** túmulos no chão, 3 (5) esqueletos sobem (inimigo novo, fraco, solta joias normais; não entra na agenda).
- **Fase 2 (50%):** feitiços 20% mais rápidos, e a chuva às vezes emenda nas orbes.
- **Morte:** desfaz-se em pó de cima para baixo e o cristal estoura; solta o Cajado da Tempestade. Vida 7600 (o guardião tinha ~6200).

### Regras comuns
- Barra de chefe com a cor do chefe (dourado / verde-água; o dragão continua roxo), marca de 50% e "Fase 1 / Fase 2 / Invulnerável / Recuando"; o cartão de apresentação vai para a metade da tela onde o chefe não está.
- Tremor e clarão das introduções e da troca de fase só sem `prefers-reduced-motion`.
- Música: a de combate com os tambores de chefe (116 bpm; 128 na fase 2), sem o drone, que fica para o dragão; silêncio durante a entrada.
- Sons novos (armadura, grito, gelo, trovão, zumbido do relâmpago, ossos); picos medidos no mixer entre −18 e −30 dBFS (explosão do fogo −19,4); os que passavam de −18 foram baixados.
- Todos os textos visíveis dos chefes em `BOSS_TXT` (para a futura opção em inglês); números em `BAL.paladin`/`BAL.lich`.
- **Fuga (decisão nossa, a confirmar):** chefe não derrotado em 240 s vai embora e a relíquia se perde. Antes o guardião ficava até as 15:00; com a fuga o Paladino nunca encontra o Lich.
- **Spawn durante a luta (a confirmar):** `BAL.spawn.guardMul` 0,4 → 0,25 (nos primeiros 75 s de um chefe vivo, sem hordas, como antes).
- **Mira automática que prefere o chefe (a confirmar):** com um chefe vivo no alcance, o Shuriken e o Arco miram nele (`BAL.aimBoss` = 0,6: ele conta como se estivesse a 60% da distância) e a primeira bola de fogo vai nele. Sem isso as armas a distância gastavam a luta nos inimigos pequenos e levavam ~75% mais tempo que o corpo a corpo para derrubar o Paladino.
- Removidos: `spawnGuardian`, `guardType`, `BAL.guard` e o leque de flechas do elfo-guardião.

### Lutas (bot chega ao chefe sem poder morrer antes, `run.py --god-until`, 48 sementes; mortes = morreu até 120 s depois de o chefe surgir)

| política | Paladino: tempo p/ matar (mediana) | mortes na luta | guardião antigo (24 sementes) | Lich: tempo p/ matar | mortes na luta | guardião antigo (24 sementes) |
|---|---|---|---|---|---|---|
| prioridade (`prio`) | 44 s | 23% | 12,5% | 50 s | 65% | 75% |
| a distância (`ranged`) | 33 s | 19% | 17% | 39 s | 62,5% | 62,5% |
| híbrido (`hybrid`) | 31 s | 27% | 21% | 30 s | 62,5% | 75% |
| corpo a corpo (`melee`, cauteloso) | 34 s | 46% | 17% (54% sem limite de tempo) | 31 s | 50% | 37,5% |
| corpo a corpo de perto (`agg`) | 45 s | 62,5% | 25% (54% sem limite) | 27 s | 73% | 62,5% |
| aleatório (`random`) | 64 s | 62,5% | 54% | 43 s | 75% | 79% |

- Os ataques do próprio chefe tiram pouco: ~3 meios corações por luta do Paladino (investida 1,3, lâminas 0,4, contato 0,3) e ~1–1,5 do Lich. Quem mata é o enxame em volta (flechas dos elfos às 5:00, fogo das wyverns às 10:00). Às 10:00 o bot já morria muito com o guardião antigo, que quase não atacava.
- O Lich só é derrubado ~26% mais rápido pelo corpo a corpo cauteloso que pelas armas a distância (31 s contra 39 s); o corpo a corpo de perto, 27 s.

### Partidas inteiras (48 sementes por política, cauteloso + corpo a corpo de perto)

| bot | Etapa 4 (limite 4): média · vitória | limite 5, Grimório antigo | limite 5 + Grimório reduzido, guardiões | **Etapa 5 (chefes novos)** |
|---|---|---|---|---|
| corpo a corpo (`melee`) | 601 s · 33% | 538 s · 23% | 565 s · 27% | **554 s · 27%** |
| corpo a corpo de perto (`agg`) | 529 s · 21% | 555 s · 25% | 499 s · 15% | **488 s · 21%** |
| a distância (`ranged`) | 595 s · 31% | 541 s · 21% | 509 s · 19% | **511 s · 17%** |
| híbrido (`hybrid`) | 578 s · 29% | 471 s · 8% | 528 s · 15% | **483 s · 10%** |
| prioridade (`prio`) | 714 s · 56% | 553 s · 21% | 522 s · 17% | **530 s · 15%** |
| aleatório (`random`) | 468 s · 17% | 425 s · 6% | 482 s · 17% | **412 s · 8%** |

- O limite de 5 armas explica a maior parte da queda em relação à Etapa 4 (o bot espalha níveis em mais armas); a redução do Grimório pesa menos (diferenças dentro do ruído de ±5 pontos de vitória).
- **A distância fica atrás do corpo a corpo cauteloso:** 17% contra 27% de vitórias (média de sobrevivência −8%). Não foi compensado: são números de poderes, decisão do Narley.
- Nas partidas inteiras, morrer até 120 s depois do Paladino surgir: prio 11% (3% com o guardião), a distância 13% (17%), híbrido 21% (22%), corpo a corpo 51% (32%), de perto 67% (30%). Poucos bots chegam vivos às 10:00 (8–31%); os que chegam quase sempre matam o Lich.

### Desempenho (`tests/perf.py`, 390×844, CPU 4x)
- Cenários novos: `paladin` (5:12) 59,7 fps, render 6,6 ms (p95 10,1); `lich` (10:15, build cheia) 59,4 fps, render 11,5 ms (p95 18,3). 1x: 60 fps.
- `late` ficou em ~50 fps nesta máquina, igual ao `dev` sem chefes medido na mesma hora (49–51,5 fps; na Etapa 4 eram 56–57 numa medição mais folgada). Sem chefe vivo o código novo só percorre listas vazias.
- A arte dos chefes é feita em tempo ocioso depois do título (e o bestiário só a desenha ao abrir "Como jogar"), não na inicialização.

### Testes e ferramentas
- `tests/smoke.py`: 36/36 (novas: os dois chefes no horário com barra e cartão, fase 2 com transição invulnerável, relíquia só depois da animação, esqueletos, círculos de relâmpago, fuga sem relíquia). Duas execuções seguidas: determinismo IDENTICAL entre elas (o `det` muda em relação à Etapa 4, como esperado).
- `tests/balance/`: acompanha cada luta (início, fim, dano por causa), `--god-until`, bot que desvia das telegrafias e entra nas janelas do chefe.
- `tests/perf.py`: cenários `paladin` e `lich`.

### Não verificado
- Ninguém jogou: só bot, capturas de tela (390×844 e 1366×768, telegrafias, fases, morte, esqueletos) e medição de volume. A sensação das lutas, o tempo de reação humano às telegrafias e o som num alto-falante real não foram avaliados.
- Desempenho só em Chromium headless com CPU limitada; não num celular.

## Etapa 4 — novos poderes por estilo (novembro de 2026, branch `dev`, não publicado)

Pedido do Narley: poderes para montar um arsenal corpo a corpo, a distância ou híbrido, à escolha do jogador. Medido com `tests/balance/` (bot, Chromium headless, `dt` = 1/30 s, **48 sementes** por política; movimento cauteloso `kite` para todos e, para corpo a corpo, também o de perto `agg`). O bot não é um humano: os números servem para comparar versões e estilos. Como a sobrevivência é bimodal (o bot morre perto das 7:00–9:00 ou vence), a média e as vitórias dizem mais que a mediana.

| bot, 48 partidas por linha | antes: média · p25/mediana/p75 · vitória | depois: média · p25/mediana/p75 · vitória |
|---|---|---|
| corpo a corpo (`melee`, cauteloso) | 447 s · 426/446/467 · 0% | 601 s · 411/429/973 · 33% |
| corpo a corpo (`melee`, de perto `agg`) | 446 s · 429/448/466 · 0% | 529 s · 403/438/528 · 21% |
| a distância (`ranged`) | 535 s · 289/515/563 · 17% | 595 s · 482/516/940 · 31% |
| híbrido (`hybrid`) | 507 s · 267/403/577 · 21% | 578 s · 401/512/937 · 29% |
| prioridade (`prio`) | 667 s · 498/523/1024 · 38% | 714 s · 417/937/941 · 56% |
| aleatório (`random`) | 474 s · 236/403/527 · 19% | 468 s · 325/408/449 · 17% |
| maior fatia de dano de um poder (prio + aleatório, mediana / máx.) | 47% / 77% | 46% / 72% |

"Antes" = Etapa 3 com as mesmas políticas (lá o corpo a corpo só tinha a Espada, a Espada Sagrada e o Fogo-fátuo de reserva). Os três estilos ficaram a menos de 5% um do outro na média (cauteloso); o corpo a corpo de perto sobrevive ~12% menos, como esperado de um estilo arriscado.

Dano por segundo no nível 5 aos 10:00 (bot cauteloso invulnerável, 3 sementes, `--t 600`): Martelo 681, Shuriken 566, Fogo 497, Arco 381, Aura 369 (297 de perto), Espada 217, Fogo-fátuo 67. Aos 7:30, 5 níveis de Manoplas levam Espada+Martelo+Aura nível 4 de 233 para 404/s; 5 de Grimório levam Shuriken+Fogo+Arco nível 4 de 432 para 523/s (a build a distância já mata quase tudo que aparece, então o ganho aparece menos nesse teste).

### Estilos
- Todo poder tem estilo: **Corpo a corpo** (Espada, Martelo Sísmico, Aura de Espinhos, Espada Sagrada), **A distância** (Shuriken Gigante, Arco Élfico, Magia de Fogo, Cajado da Tempestade), **Híbrido** (Fogo-fátuo). Botas, Ímã e Coração são "Passivo"; Manoplas e Grimório são passivos que reforçam um estilo.
- Mostrado por insígnia em pixel + cor + texto (nunca só cor): punho laranja, alvo azul, losango meio a meio. Nas cartas de nível (pílula ao lado dos níveis), nos chips do HUD (insígnia + borda; no celular o chip fica só com ícone, insígnia e nível) e na nova lista "Poderes · monte seu estilo" de "Como jogar", que também ganhou um parágrafo sobre estilos e o limite de armas.
- "Will-o'-Wisp" passou a se chamar **Fogo-fátuo** (a interface é em PT-BR).

### Armas novas (5 níveis; o 1º nível bate × 0,75 como as outras)
- **Martelo Sísmico** (corpo a corpo): com inimigo perto, Aren ergue o martelo e golpeia o chão; um anel de choque cresce em 0,3 s e acerta cada inimigo uma vez, empurrando forte. Dano 20 + 10·nível (30–70), raio 36 + 5·nível (41–61 px), recarga 3 − 0,3·nível (2,7–1,5 s). Nível 5: tremor secundário 0,35 s depois, raio × 1,5 e dano × 0,6. Tremor de tela leve (desligado com movimento reduzido), poeira, lascas, rachaduras no chão.
- **Aura de Espinhos** (corpo a corpo): elipse de espinhos em volta de Aren, raio 26 + 4·nível (30–46 px); a cada max(0,3; 0,6 − 0,06·nível) s acerta todos dentro com 7 + 5·nível (12–32) e empurra de leve; do nível 3 em diante quem está dentro anda 12/18/24% mais devagar. Números de dano verdes; os espinhos brilham a cada tique.
- **Arco Élfico** (a distância): rajada em leque no inimigo mais próximo (ou para onde Aren olha). Flechas por rajada 1/2/2/3/3, atravessam 1/1/2/3/4 inimigos, dano 11 + 4·nível (15–31), recarga 1,3 − 0,14·nível (1,16–0,6 s).

### Passivos novos (5 níveis)
- **Manoplas do Guerreiro**: poderes corpo a corpo +10% de dano e +6% de alcance por nível (alcance da espada, raio do martelo e da aura, largura das ondas sagradas).
- **Grimório Arcano**: poderes a distância +10% de dano e recarga 7% menor por nível (inclui o Cajado da Tempestade).
- O Fogo-fátuo (híbrido) recebe metade de cada um (dano, raio da órbita, intervalo entre acertos).

### Escolhas
- Arma ainda não tida ganha +1,4 de peso só enquanto Aren tem menos de 3 armas (antes valia sempre, para Shuriken/Fogo/Fogo-fátuo); poder já tido vale × 2. Sem isso, com 14 poderes, as ofertas espalhavam a build em várias armas de nível 1 e o bot morria perto dos 4:00.
- **Limite de 4 armas** (a espada conta; relíquias e passivos não): com 4, armas novas deixam de aparecer. **Decisão a confirmar pelo Narley.** Com 5 o bot (24 sementes) ficou bem pior nas builds que espalham: aleatório 346 → 418 s de mediana, a distância 367 → 540, híbrido 341 → 456 com o limite de 4.
- Nas partidas do bot, 94–95% das ofertas têm ao menos uma opção do estilo da build e ~70% uma arma ou passivo do estilo.

### Som
- Martelo: baque grave + terra + pedrinhas; o tremor secundário é mais baixo. Arco: "fiu" curto + corda. Aura: sem som (é contínua). Volumes medidos no mixer (OfflineAudioContext): golpe do martelo pico −18,5 dBFS (explosão do fogo −19,1), tremor −23,0, arco −23,7 (dispara com frequência, por isso abaixo).

### Testes e ferramentas
- `tests/smoke.py`: as armas novas entram na partida de estresse; 5 verificações novas (cada arma nova sozinha mata mais que só a espada e o efeito aparece; limite de armas; pílula de estilo nas cartas e lista de poderes completa). 34/34.
- `tests/balance/`: políticas `melee`, `ranged`, `hybrid`; nomes desconhecidos ficam com prioridade mínima; marcação da fonte de dano das armas novas; `agg` usa o alcance da aura/martelo.
- `tests/perf.py`: o cenário `late` também põe as 3 armas novas e os 2 passivos no máximo (mais armas do que o limite permite: pior caso). CPU 4x, `late`: 59,7 → 56–57 fps, render 9,9 (p95 13,1) → 12,4–13,0 (p95 ~19) ms; 1x 60 fps. `boss` 4x: 60 fps, render 6,9 ms. Os espinhos da aura passaram a ir direto para a camada `LX` (~1 ms → ~0,7 ms).
- Infraestrutura (commit separado): estilos + multiplicadores dos passivos com os passivos em 0 → determinismo com números idênticos ao da Etapa 3.

### Não verificado
- Nada foi jogado por um humano: só bot, capturas de tela (390×844 e 1366×768) e medição de volume. Sensação do martelo/tremor e legibilidade da aura num celular real não foram vistas.
- Desempenho medido só em Chromium headless com CPU limitada, não em celular.

## Etapa 3 — balanceamento e estrutura de 15 minutos (novembro de 2026, branch `dev`, não publicado)

Mudanças aprovadas pelo Narley. Medido com o novo simulador `tests/balance/` (bot, Chromium headless, `dt` = 1/30 s, 8 sementes × 6 políticas de escolha × 2 movimentos = 96 partidas por versão). O bot não é um humano: os números servem para comparar versões.

| bot cauteloso (`kite`), 48 partidas | antes | depois |
|---|---|---|
| tempo de morte (p25 / mediana / p75) | 229 / 314 / 346 s | 305 / 428 / 520 s |
| chega a 6:00 / 10:00 / 15:00 | 10% / 2% / — (chefe aos 10:00) | 73% / 19% / 15% |
| vitória | 2% | 15% |
| escolhas por partida (mediana) / intervalo mediano | 5 / 33 s | 8 / 39 s (p75 51 s) |
| maior fatia de dano de um poder (builds mistas, mediana) | 53% | 47% |
| dragão, build média (`boss.py`): duração / parte dos selos | ~3,5 min / 81–87% | ~3,5–4 min / 35–42% |
| dragão, build máxima: duração / parte dos selos | ~2,6 min / 68–70% | ~1,9 min / 20–21% |

### Estrutura da partida
- Três chefes: **Paladino Possuído** aos 5:00, **Lich Ancião** aos 10:00, **Dragão Esqueleto** aos 15:00 (era 10:00). Sistema de marcos por dados (`BOSSES`).
- Paladino e Lich são **provisórios** até a Etapa 5: aviso + um guardião elite grande (orc e elfo negro em 2x, barra de chefe) que, ao morrer, solta a relíquia (item dourado com coluna de luz e marcador na borda da tela). Enquanto o guardião está vivo (primeiros 75 s), o spawn fica mais lento e não há hordas.
- Relíquias só vêm dos chefes: **Espada Sagrada** do Paladino, **Cajado da Tempestade** do Lich. Pegar a relíquia dá o nível 1; depois ela pode aparecer nas escolhas (máximo 3). O desbloqueio por tempo (5:00/6:30/8:00) saiu.
- **Chuva de Meteoros removida** (código, ícone, `UPG`, recargas, testes, documentação).

### Experiência e escolhas
- As joias são a experiência: cada inimigo solta joias pelo valor de `ET.gem` (goblin 1 … wyvern 12; elite ×6; guardiões 60 e 120) e a experiência só conta ao recolher — o Amuleto Ímã passou a importar. Com mais de 400 joias no chão, a mais antiga se funde com a vizinha (nada se perde).
- Curva nova: `xpNeed(L) = round(8 + 4,5·(L−1) + 0,3·(L−1)²)` (nível 1: 8, nível 10: 73, nível 20: 202, nível 40: 627).
- Escolha de poder nos níveis 2, 3, 5, 7 e 10, depois a cada 3 níveis (era 3, 5 e a cada 5), com **3 opções** (eram 2). Nos outros níveis continua +½ coração. Teclas 1–3 e setas na tela de escolha.
- Nerf do primeiro nível suavizado: poderes 0,55 → 0,75; relíquias 0,7 → 0,85. Peso das relíquias nas escolhas 5 → 2,5.

### Curva de dificuldade (15 minutos)
- Inimigos: mesma ordem; Succubus 4:50 → 6:00, Wyvern 5:30 → 8:00 (bônus de novidade menor para os dois). Hordas de demônios a partir de 5:30 (era 5:00), tamanho máximo aos ~13 min.
- Vida dos inimigos: `1 + t/150` → `1 + t/220 + (t/430)²` (×2,9 aos 5:00, ×5,7 aos 10:00, ×9,5 aos 15:00).
- Spawn: intervalo `0,95/(1 + t/75)` (era `/45`), limite de 230 mantido. Elites: rampa de 4:00 a 15:00 até +11% (era 5:00–10:00, +7%, sem teto).
- Cristais e meio coração: a chance por abate cai depois dos 4:00 (`1/(1 + (t − 240)/160)`), porque morrem muito mais inimigos por minuto no fim; sem isso as builds terminavam com tudo no máximo e ~200 meios corações.
- O "muro" dos 5:00–6:00 foi espalhado (Succubus, Wyvern, hordas de demônios e elites não chegam mais juntos); o pico agora fica perto dos 7:00–9:00 para o bot.

### Dragão
- Vida 60000 → 20000; selos tiram 7% (eram 20%) e atordoam 5 s (eram 3,5). Atordoado, o dragão desce e não causa dano de contato, e **a espada alcança o peito dele**. As armas fazem a maior parte do dano.

### Testes e ferramentas
- `tests/balance/` (`patch.py`, `bot.js`, `run.py`, `analyze.py`, `boss.py`): simulador adaptado da auditoria.
- `tests/smoke.py`: partida de estresse até ~920 s, guardiões e relíquias (5 verificações novas: guardião, barra, relíquia só depois de pegar, nível 1, marcos). 29/29.
- `tests/perf.py`: `late` em 840 s e `boss` em ~912 s (sem meteoros). CPU 4x: late render 10,4 ms (p95 16,0), 59 fps; boss 5,6 ms, 60 fps.

### Não verificado
- Nada disso foi jogado por um humano: só bot e capturas de tela. O ritmo do bot (nível 20 aos ~5:00) é parecido com o do Narley antes (nível 20 aos 5:23), mas a sobrevivência humana pode ser bem diferente.

## Etapa 2 — desempenho (novembro de 2026, branch `dev`, não publicado)

Medido com o novo `tests/perf.py` (Chromium headless, viewport de celular 390×844, simulação semeada; "4x" = CPU 4× mais lenta via DevTools). FPS = laço real de `requestAnimationFrame`; render = média (p95) de 600 quadros síncronos.

| cenário | antes 1x | depois 1x | antes 4x | depois 4x |
|---|---|---|---|---|
| early (30 s) | 60 fps · render 0,5 (2,5) ms | 60 fps · 0,9 (2,4) ms | 60 fps · 2,2 (10,3) ms | 60 fps · 4,5 (6,8) ms |
| mid (300 s) | 60 fps · 3,6 (8,6) ms | 60 fps · 2,4 (4,1) ms | 39 fps · 15,3 (37,3) ms | 60 fps · 9,0 (12,9) ms |
| late (540 s, tudo no máximo) | 60 fps · 5,9 (12,0) ms | 60 fps · 2,9 (5,4) ms | 39 fps · 23,4 (46,8) ms | 60 fps · 11,8 (16,1) ms |
| boss | 60 fps · 1,7 (8,9) ms | 60 fps · 1,6 (2,9) ms | 59 fps · 8,3 (40,0) ms | 60 fps · 6,5 (8,0) ms |

Inicialização (script): 136 → 108 ms (1x), 552 → 416 ms (4x). Pausado no fim de partida: ~10 ms → ~0,14 ms de JS por quadro (4x). Em `early` a média do render subiu (custo fixo da camada + geração do chão à frente), mas o p95 caiu e continua em 60 fps.

### Desempenho
- **Camada de software (`LX`)**: durante o `render`, pixels de efeitos, sprites pequenos, joias, inimigos e números são misturados num buffer em JS e vão ao canvas com um `putImageData` por descarga, em vez de milhares de `fillRect`/`drawImage` (no Chromium cada chamada tem custo fixo alto). Arco da espada, ondas sagradas, anéis e círculos de maldição sem troca de `fillStyle`/`globalAlpha` por pixel.
- Chão gerado em fatias, à frente do movimento (orçamento de 1,5 ms por quadro + tempo ocioso): sem picos de ~2–9 ms ao entrar em área nova.
- Joias, itens e inimigos fora da tela não são desenhados; `pixCircle` e números de dano com sprites em cache fora da camada.
- Menos lixo por quadro: listas compactadas no lugar (sem `filter`), grade espacial, lista ordenada por y, props, rastro do shuriken, objeto da espada e Sets das ondas reaproveitados; gradiente da noite/chefe em cache.
- Pausa/escolha de poder/fim: a cena é desenhada uma vez e fica congelada (árvores, itens e wisps param de balançar atrás do painel).
- Inicialização: cópias tingidas dos inimigos, rotações da espada e nuvem feitas no primeiro uso ou em tempo ocioso.
- Limite de segurança de 1200 partículas desenhadas (o pico medido é ~610; não corta nada hoje).

### Jogabilidade (aprovado pelo Narley)
- Shurikens voltam a `max(125, velocidade do herói × 1,6)` px/s e somem após 6 s (`BAL.boom`). Com Botas no máximo eles não ficam mais perseguindo o herói: ~39 → ~12 vivos no fim da partida.

### Verificação
- Imagem: 24 quadros × 5 cenários renderizados com a mesma semente antes e depois (até o commit do shuriken): diferença máxima de 13/255 por canal (arredondamento de alfa), nenhuma diferença visível lado a lado.
- `smoke.py --compare`: IDENTICAL em todos os commits da etapa antes do shuriken; o commit do shuriken muda a simulação (esperado). `smoke.py`: 24/24.
- Só medido em Chromium headless num desktop (CPU limitada por emulação); não testado em celular real.

### Testes
- `tests/perf.py`: benchmark por cenário (`--calls` conta chamadas de canvas, `--boot` mede a inicialização, `--pause` mede o quadro pausado, `--json` guarda os números).

## Etapa 1 — correções, limpeza e documentação (novembro de 2026, branch `dev`, não publicado)

### Corrigido
- Teclas ficavam "presas" ao trocar de janela/aba ou abrir um painel: teclas e joystick de toque são zerados em blur, aba oculta, pausa e em todos os painéis; a partida pausa sozinha quando a janela perde o foco.
- A música continuava tocando com a aba oculta no menu, na escolha de poder, na tela de fim e na pausa: o áudio agora é suspenso sempre que a aba fica oculta e só volta se Música ou Efeitos estiverem ligados.
- Morrer (ou vencer) e recomeçar logo em seguida fazia o painel de fim da partida anterior aparecer por cima da nova: os timeouts são guardados e cancelados.
- Wake lock concedido depois da pausa ficava ativo: agora é liberado.
- Depois de clicar em Música/Efeitos/Pausa com o mouse, Enter ou Espaço voltavam a acionar o botão: o foco sai do botão após clique de mouse/toque.
- WASD não funcionava em teclado AZERTY: as teclas também são lidas pela posição física (`e.code`); setas inalteradas.
- Painel de pausa: anunciado como diálogo modal, Tab circula só dentro dele e o HUD fica inacessível enquanto pausado.

### Build
- `tools/build_web.py` cria `dist/` se faltar, aceita `--src`, `--out` e `--zip`, encontra o fonte do repositório sozinho e copia `OFL.txt`. `index.html`, manifest e README gerados são idênticos aos de antes.
- Service worker: pré-cache ignora o cache HTTP (`cache:'reload'`); a página usa rede primeiro com o cache como reserva (offline continua funcionando e uma versão nova aparece já no primeiro carregamento online); demais arquivos stale-while-revalidate; caches versionados e limpeza dos antigos mantidos.

### Código
- Constantes de balanceamento centralizadas no objeto `BAL`, sem mudar nenhum valor (simulação semeada idêntica antes e depois).
- Removido código morto: construtor de humanoides 16 bits (`humanoid`, `buildWalker`, `WPN`, `HERO_SPEC`, `ENEMY_SPECS`), `flipH`, `rot90`, `seeded`, o caminho nunca usado do "primeiro poder" (`openLevelUp(first)`, `lvlFirst`, `pickOptions(n, onlyNew)`), goblins de fundo do menu (atualizados, nunca desenhados), duplicatas `tint` (= `tintC`) e `hexA` (= `hexRGB`). O arquivo foi de 3575 para 3352 linhas.

### Testes e documentação
- `tests/smoke.py`: partida de ~620 s com herói invulnerável e todos os poderes (relíquias incluídas), chefe, vitória, volta ao título e 3 recomeços; partida de 120 s com bot; testes de cada correção; determinismo com `Math.random` semeado. v21 original: 15/24 verificações; depois da etapa: 24/24.
- `tests/check.js` (cópia manual desatualizada do script do jogo) removido; o `smoke.py` monta sua cópia instrumentada a partir do `src` a cada execução.
- Novos `CLAUDE.md`, `ARCHITECTURE.md`, `ROADMAP.md`, `TASKS.md` e este changelog; `README.md` atualizado.

## v21 — estado do jogo antes da Etapa 1 (08/11/2026)

O que já existe:

- Sobrevivência 2D estilo "survivors" em pixel art 32 bits desenhada em código, arquivo HTML único, sem bibliotecas; interface em PT-BR.
- Herói Aren com espada automática; movimento por WASD/setas ou toque e arraste; P/Esc pausa, F tela cheia.
- 8 tipos de inimigo com IAs próprias (goblin, gárgula, hobgoblin, orc, elfo negro arqueiro, demônio, succubus conjuradora, wyvern), entrando de 0:00 a 5:30, elites e hordas periódicas.
- Experiência e níveis: escolha entre dois poderes nos níveis 3, 5 e a cada 5 níveis; nos outros, meio coração.
- Poderes com 5 níveis: Espada, Shuriken Gigante, Will-o'-Wisp, Magia de Fogo, Botas Ligeiras, Amuleto Ímã, Recipiente de Coração. Relíquias com 3 níveis liberadas após 5:00/6:30/8:00: Espada Sagrada, Cajado da Tempestade, Chuva de Meteoros.
- Drops de meio coração e Cristal de Aprimoramento.
- Chefe Dragão Esqueleto aos 10:00 com cinco ataques, fúria abaixo de 50% e a mecânica dos Selos de Luz.
- Música procedural com humores (título, calmo, combate, chefe, chefe enfurecido) e efeitos sintetizados.
- Tela de título animada (Aren cochilando, goblin disfarçado de arbusto), bestiário, recorde salvo no navegador.
- PWA: instalável, offline, wake lock, tela cheia. No ar em https://narley1.github.io/aren/ (build de 26/10).
