# Changelog

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
