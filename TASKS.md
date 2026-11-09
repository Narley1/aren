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
- [x] Guardiões provisórios substituídos pelo Paladino e pelo Lich de verdade (Etapa 5)
- [x] Quedas de cristal/meio coração caem depois dos 4:00 — confirmado pelo Narley (08/11/2026); serpe-dragão mais rara ao aparecer também confirmada
- [ ] Dragão: com build cheia a luta dura ~2 min; com build média ~4 min. A espada no dragão atordoado é perceptível?
- [ ] Flechas dos elfos são a maior fonte de dano para o bot; ver se para humanos também
- [ ] Bot: a política "balanced" (espalha níveis) morre cedo (~4:00); builds só de espada morrem ~7:00
- [x] Etapa 5 trocou os guardiões por Paladino e Lich de verdade

## Etapa 4 — Novos poderes por estilo — concluída no `dev`

- [x] Estilo de cada poder (`UPG.kind/style/boost`), pílula com insígnia + cor + texto nas cartas, chips do HUD com insígnia e borda, lista de poderes em "Como jogar", texto de "Como jogar"
- [x] Martelo Sísmico, Aura de Espinhos, Arco Élfico (5 níveis, nerf do 1º nível), Manoplas do Guerreiro, Grimório Arcano (5 níveis); números em `BAL`
- [x] Ícones 8×8, flecha e martelo pré-rotacionados, anel de choque com rachaduras, aura de espinhos; capturas em 390×844 e 1366×768
- [x] Sons do martelo (golpe e tremor) e do arco, volume medido contra a explosão do fogo; aura sem som
- [x] Pesos das escolhas (arma nova só até ter 3, poder já tido ×2) e limite de armas (5, escolha do Narley)
- [x] Bot: políticas `melee`/`ranged`/`hybrid`, 48 sementes; `smoke.py` 34/34; `perf.py` late com as armas novas no máximo
- [x] "Will-o'-Wisp" passou a se chamar "Fogo-fátuo" (texto da interface em PT-BR)

## Pendências da Etapa 4 (decisões e testes do Narley)

- [x] Limite de armas: o Narley escolheu **5** (08/11/2026). Com 5 o bot espalhava mais as builds na medição da Etapa 4 (ver `CHANGELOG.md`); remedir na Etapa 5
- [x] Pesos novos das escolhas confirmados pelo Narley (08/11/2026)
- [x] Nome "Fogo-fátuo" confirmado pelo Narley (08/11/2026); no futuro haverá opção de jogar em inglês
- [x] Grimório Arcano reduzido pelo Narley (08/11/2026): +8% de dano e −5% de recarga por nível (era +10% e −7%); nível 5: +40% de dano, −25% de recarga; híbrido continua com metade
- [ ] Jogar uma build de cada estilo: o corpo a corpo parece arriscado mas recompensador? A aura dá para ler sem poluir?
- [ ] O Fogo-fátuo (único híbrido) continua a arma mais fraca (67 de dano/s aos 10:00 no nível 5 contra 217 da Espada e 370–680 das outras); não foi mexido porque é número de poder existente
- [ ] O bot com movimento de perto (`agg`) sobrevive menos que o cauteloso mesmo com corpo a corpo; um humano pode render bem diferente

## Etapa 5 — Chefes: Paladino Possuído e Lich Ancião — concluída no `dev`

- [x] Paladino Possuído (5:00): sprite em código (passo, poses, espada pré-rotacionada, espírito), investida com escudo, giro da espada, salto esmagador, lâminas fantasmas; fase 2 aos 50%; morte com a armadura caindo em pedaços; solta a Espada Sagrada
- [x] Lich Ancião (10:00): sprite em código, teleporte, orbes de gelo (Aren lento e azulado), chuva de relâmpagos, relâmpago em cadeia, esqueletos (inimigo novo, só invocado); fase 2; vira pó; solta o Cajado da Tempestade
- [x] Telegrafias no chão com forma + animação (faixa, anéis que fecham, mira, símbolo de raio, feixe travado), legíveis em 390×844 e 1366×768 (capturas)
- [x] Cartão de apresentação, barra com cor do chefe e marca de 50%, "Fase 1/2", sons novos (picos medidos), música de chefe sem drone; tremor/clarão só sem movimento reduzido
- [x] Números em `BAL.paladin`/`BAL.lich`, textos em `BOSS_TXT` (para a futura opção em inglês)
- [x] Guardiões provisórios removidos (`spawnGuardian`, `guardType`, `BAL.guard`, leque de flechas do elfo-guardião)
- [x] Bot: lutas medidas por chefe e política (`run.py --god-until`, `analyze.py`); `smoke.py` 36/36; `perf.py` cenários `paladin` e `lich`

## Pendências da Etapa 5 (decisões e testes do Narley)

- [ ] **Confirmar a mira automática que prefere o chefe** (`BAL.aimBoss` = 0,6: Shuriken, Arco e a 1ª bola de fogo miram o chefe vivo se ele estiver no alcance). Sem isso as armas a distância gastavam a luta nos inimigos pequenos e levavam ~75% mais tempo que o corpo a corpo para matar o Paladino
- [ ] **Confirmar o spawn a 25% durante a luta** (`BAL.spawn.guardMul` 0,4 → 0,25, primeiros 75 s de um chefe vivo)
- [ ] **Confirmar a fuga**: chefe não derrotado em 240 s (`BAL.paladin.flee`/`BAL.lich.flee`) vai embora e a relíquia se perde (antes o guardião ficava até as 15:00; com a fuga o Paladino nunca encontra o Lich)
- [ ] Jogar as duas lutas: as telegrafias dão tempo de reagir? O Paladino na fase 2 fica injusto? O Lich parece ameaçador (para o bot ele quase não acerta; quem mata às 10:00 é o enxame)?
- [ ] Testar num celular real: legibilidade das telegrafias e do cartão, desempenho do Lich na fase 2
- [ ] Bot de corpo a corpo morre mais na luta do Paladino que com o guardião antigo (partidas inteiras: 51% contra 32% até 120 s; de perto 67% contra 30%), quase tudo por flechas dos elfos enquanto contorna o chefe; as vitórias do corpo a corpo não mudaram (27%). Ver se acontece com humanos antes de mexer
- [ ] Com limite 5 + Grimório reduzido, **A distância fica ~38% atrás do corpo a corpo em vitórias** (17% contra 27%; média de sobrevivência −8%) — números de poderes, não mexidos
- [ ] O cenário `late` do `perf.py` ficou ~50 fps a 4x nesta máquina, igual ao `dev` sem chefes medido na mesma hora (na Etapa 4 era 56–57 em outra medição); os cenários dos chefes ficam em ~60 fps

## Áudio — auditoria e Laboratório de Som (08/11/2026)

Só leitura: nenhum som do jogo mudou. Medição com `tools/sfx_levels.py` (cada som sozinho pelo mixer do jogo; "volume" = RMS da janela de 150 ms mais alta; referência = explosão da Magia de Fogo, −29,5 dBFS).

- [x] **Música cobre os efeitos:** músicas com RMS médio de −23 a −20 dBFS; arco −40,5, explosão −29,5. Proposta no laboratório: música −6 dB (ajustável)
- [x] **Sons antigos muito altos:** risada do demônio +17,9 dB sobre a explosão (pico −3,3 dBFS), rugidos do dragão +14 a +18, morte do dragão pico −2,4, súcubo +9,4, impacto do mergulho +11,2. Proposta: no máximo +6 (+8 para chegada, fúria e morte do dragão)
- [x] **Avisos de ataque baixos:** escudo raspando −12,4, salto −13,1, aviso da chuva de relâmpagos −11,6; arco −11. Proposta: subir para −8
- [x] **18 momentos sem som** (dano em Aren, morte de inimigo, joia, coração, Espada, Shuriken, disparo do fogo, Fogo-fátuo, Cajado, Espada Sagrada, flecha dos elfos, fogo da serpe, elite, vida baixa, botões, pausa, vitória/derrota sem música)
- [x] Sem variação de altura nos sons repetidos (arco, explosão)
- [ ] Só liga/desliga Música e Efeitos; sem volume separado
- [x] Acessibilidade: todo som que avisa um ataque tem marcação visual
- [x] Laboratório publicado para o Narley ouvir e dar nota; as notas ficam no armazenamento do artifact (coleção `avaliacoes`) e são lidas antes de mexer no som



### Áudio — rodada 2 (08/11/2026): pedidos do Narley no laboratório

Feito (medido com `tools/sfx_levels.py`; referência = explosão nova, ~−29,5 dBFS; nenhum pico acima de −8 dBFS nas medições):
- [x] Mix: música −6 dB (`MUS` = 0,17, uma constante), Cristal e relíquia −3 dB, escudo raspando +4,5 dB
- [x] Refeitos: explosão de fogo (sopro, chama, estalos), martelo e tremor (terra e areia), arco (corda + flecha saindo, ±4,5%), risada do demônio (mais aguda, sem sub, +5,8 dB sobre a explosão, era +17), maldição (risinho felino "nya-ha-ha"), aterrissagem, grito possuído e "bonk" do escudo do Paladino, lâminas fantasmas, lâmina disparada mais afiada, giro mais alto e metálico, espírito e morte do Paladino ~1 s mais longos, teletransporte curto, gelo formando e quebrando, aviso de relâmpagos com estática, raio retrô, rugidos do dragão (+2 a +7 dB, eram +14 a +17), impacto do mergulho
- [x] 18 sons novos: dano em Aren, vida baixa, joia, coração, nível sem escolha, Espada por nível, Shuriken (arremesso e volta), disparo do fogo, Fogo-fátuo, Cajado, Espada Sagrada, flecha dos elfos, fogo da serpe, elite, morte de inimigo por tipo, botões e cartas, pausa, vitória/derrota pelos Efeitos com a Música desligada
- [x] Determinismo IDENTICAL (o som não muda o jogo); rajada de 30 mortes + 30 joias em 1 s = 105 nós de áudio
- [x] Laboratório da rodada 2: Antes/Agora, selos de estado, notas em `avaliacoes_r2` com a nota da rodada 1 visível

Esperando o ouvido do Narley (laboratório, coleção `avaliacoes_r2`):
- [ ] Todos os sons refeitos e novos (eu não ouço: só medi nível, duração, nós e olhei espectrogramas)
- [ ] Interpretações: risinho felino colocado no estouro da maldição (a risada da súcubo ficou igual); teletransporte e raio são originais, só inspirados no "jeito" pedido
- [ ] Ainda acima do limite e sem pedido de mudança: morte do dragão (+18 dB, ele gostou), risada da súcubo (+9 a +11), subir de nível (+6,5); abaixo de −8 sem pedido: preparar o giro, salto, carregar relâmpago em cadeia. O laboratório mostra a Proposta para cada um
- [ ] Lâmina disparada continua baixa (−14 dB) porque só foi pedido "mais afiado"
- [ ] Volume separado para Música e Efeitos (hoje só liga/desliga)

### Áudio — rodada 3 (08/11/2026): notas do Narley na rodada 2 + monstros, lote 1

Feito (medido com `tools/sfx_levels.py`; volume = rms150 em relação à explosão; picos dos sons novos e mudados entre −13,6 e −25 dBFS):
- [x] Shuriken: sem som na volta (`boomCatch` removido do jogo e do catálogo); o arremesso ficou
- [x] Risada do demônio: a mesma, ~30% mais curta (4 "ha"; voz de ~1,4 s para ~1,0 s)
- [x] Morte da gárgula refeita (pedra rachando e esfarelando) e da serpe-dragão (guincho curto, baque, asas caindo); receitas em `KILL_FX`, 8 nós
- [x] Vida baixa +4,5 dB (−10,8 → −6,6); salto do Paladino +5 dB (proposta escolhida; medido −13,1 → −8,6); preparar o giro ficou igual (escolha dele)
- [x] Cajado da Tempestade: zumbido elétrico "bzzzt" (quadrada grave picotada a ~37 Hz), −6,1 → −4,4 dB
- [x] Risada da súcubo refeita: ronronar "mrrr", "nyaa" de gato, risinhos soprados e "hmm"; +10,2 → +4,4 dB
- [x] Vozes de presença, lote 1: goblin (risadinha), gárgula (asas de pedra, às vezes guincho rouco), hobgoblin (grunhido ou rosnado); −10 a −8 dB, até 12 nós; um temporizador por tipo com gerador próprio (sem `Math.random`), no máximo uma voz por tipo a cada 2,5–7,5 s
- [x] Determinismo IDENTICAL; `smoke.py` 0 falhas
- [x] Laboratório da rodada 3: Antes = commit 10da437, notas em `avaliacoes_r3`, nota anterior de `avaliacoes_r2` (ou `avaliacoes`)

Esperando o ouvido do Narley (laboratório, coleção `avaliacoes_r3`):
- [ ] Todos os sons da rodada 3 (eu não ouço: medi nível, duração, nós e olhei espectrogramas)
- [ ] Vozes de presença: frequência (2,5–7,5 s por tipo) e volume
- [ ] Ainda acima do limite e sem pedido: morte do dragão (+18,5 dB, pico −2,7 dBFS; ele gostou)

### Áudio — próximos lotes de monstros (proposta, não feito)

- [ ] **Lote 2:** orc (bufada/rugido curto e pesado), elfo (voz curta ao atirar ou ao chegar perto, aguda e limpa), esqueleto (chacoalhar de ossos e mandíbula batendo)
- [ ] **Lote 3:** demônio (rosnado ou respiração além da risada), serpe-dragão (bater de asas grandes e grasnido além do fogo), súcubo (asas leves/sussurro enquanto voa)
- Mesmas regras do lote 1: temporizador por tipo em `VOX`, nada de `Math.random` no jogo, −12 a −6 dB, até ~12 nós
