# Aren, o Guardião do Bosque — versão Godot

Porte para **Godot 4.7.2-stable** do jogo HTML *Aren, o Guardião do Bosque* (sobrevivência 2D em pixel art).
O jogo HTML continua sendo a referência: ele fica intacto nos branches `dev` (código) e `main` (site em
https://narley1.github.io/aren/). Esta versão vive só no branch **`godot`** (branch órfão, sem histórico em comum).

## Como abrir o projeto

1. Baixe exatamente o **Godot 4.7.2-stable** (versão padrão, não a .NET), da página oficial de versões:
   https://github.com/godotengine/godot/releases/tag/4.7.2-stable
   - Windows: `Godot_v4.7.2-stable_win64.exe.zip` · Linux: `Godot_v4.7.2-stable_linux.x86_64.zip` ·
     macOS: `Godot_v4.7.2-stable_macos.universal.zip`
   - Não precisa instalar: é só descompactar e abrir.
2. Pegue o branch: `git clone -b godot https://github.com/Narley1/aren.git aren-godot`
3. No Godot: **Importar** → escolha o arquivo `project.godot` da pasta → **Importar e editar**.
4. Aperte **F5** (ou o botão ▶) para jogar.

Outra versão do Godot 4.x provavelmente abre, mas o projeto foi feito e testado na 4.7.2.

## Controles

| Ação | Teclado | Celular / mouse |
|---|---|---|
| Andar (8 direções) | WASD (pela posição da tecla: no AZERTY é ZQSD) ou setas | toque e arraste em qualquer lugar (joystick virtual) |
| Atacar | a espada ataca sozinha o inimigo mais perto | — |
| Pausar | P ou Esc | botão **Pausa** |
| Começar | Enter (ou Espaço) | toque na tela |

Perder o foco da janela também pausa, como no HTML.

## O que tem na Etapa 1 (base jogável)

- **Sprites idênticos ao HTML**, pixel por pixel: Aren (andando para baixo, cima e lados), goblin, espada (as
  48 rotações), joias, corações, logo, árvores, arbustos, pedras, tocos, sombras e a nuvem. Eles são
  **exportados do próprio jogo HTML** por `tools/export_sprites.py`. No Godot viram recursos editáveis:
  **AnimatedSprite2D + SpriteFrames** (`aren.tres`, `goblin.tres`, `espada.tres`); o lado esquerdo é o lado
  direito espelhado (`flip_h`), como no HTML.
- **Clarão e elite por shader**: o clarão branco ao levar dano e o contorno dourado do elite são parâmetros do
  shader `inimigo.gdshader` (por instância), não mais cópias do PNG.
- **Campo infinito com TileMapLayer**: o chão é um `TileMapLayer` com o TileSet `assets/tiles/chao.tres`, que
  tem um *terrain set* (Grama, Capim alto, Terra) no modo *Match Corners* — as bordas das trilhas e do capim
  se encaixam sozinhas. O campo é gerado em volta da câmera, em blocos de 16x16 células, com **FastNoiseLite**.
  Uma segunda camada (`Detalhes`) põe tufos, trevos, flores, canteiros e pedrinhas. As peças de tile são
  montadas a partir da paleta e dos carimbos do chão do HTML (`tools/make_tileset.py`), e um shader pinta as
  manchas da grama e da terra e as listras do capim usando a posição no mundo (sem emenda entre tiles).
- **Props como cenas** (`scenes/props/`): árvore, arbusto, arbusto com frutas, pedra e toco, cada um com a sombra
  (Sprite2D) e, nas plantas, o **balanço ao vento por shader** (`balanco.gdshader`, os mesmos passos de 1 px dos
  quadros do HTML). Ficam no nó com **Y-sort**, junto com Aren e os goblins.
- **Efeitos como cenas** (`scenes/efeitos/`): número de dano (Label com fonte de imagem + Tween), faísca do
  golpe, poeira da morte, brilho da joia (CPUParticles2D), subida de nível (anéis por shader + AnimationPlayer)
  e o golpe da espada (AnimationPlayer + shader do arco + rotações em SpriteFrames + faíscas). Cada um se apaga
  sozinho. **Sombras de nuvem** num `Parallax2D` e **folhas caindo** (CPUParticles2D).
- **Pixel perfeito**: a vista tem o mesmo tamanho lógico do HTML (`SCALE = max(2, round(√(largura×altura/60000)))`,
  vista = tela ÷ SCALE) e é ampliada por um inteiro, sem suavização. Funciona em retrato (celular) e paisagem.
- **Aren**: velocidade 71,3 px/s, diagonal normalizada, animação por direção, piscando quando invulnerável.
- **Câmera** seguindo Aren em pixel inteiro (com o tremor ao levar dano).
- **Espada** nível 1 como no HTML: golpe automático no inimigo mais perto, dano 6,7, alcance 19,3 px, recarga
  0,78 s, arco de 144°, empurrão, arco de pixels e lâmina girando, números de dano.
- **Goblins** nascendo fora da tela com o intervalo do HTML (0,95 s caindo com o tempo), vida que cresce com o
  tempo, perseguição, separação, clarão ao levar dano, empurrão, morte com partículas; **elites** depois de 30 s
  e a **primeira horda** aos 50 s (18 goblins em círculo).
- **Joias e experiência**: joias de 1/5/10, ímã de 26 px, barra de experiência, níveis pela fórmula `xpNeed`
  do HTML. Nos níveis de escolha (2, 3, 5, 7, 10…) aparece o aviso "Nível N!" (as cartas vêm na Etapa 2); nos
  outros níveis Aren recupera meio coração, como no HTML.
- **HUD** como o do HTML: corações (meios corações), relógio m:ss, nível e barra, "poder no N", abates, joias,
  botões Música/Efeitos/Pausa; avisos; painel de pausa; painel "Aren caiu" com **Tentar de novo** e recorde.
- Texto em português do Brasil com a fonte **Pixelify Sans** (licença OFL, `assets/font/OFL.txt`).

## O que está simplificado nesta etapa

- Só existe o **goblin**. No HTML a gárgula chega aos 0:45; aqui ela e os outros inimigos ficam para a Etapa 3.
- Sem cartas de poder (só o aviso), sem outras armas e sem passivos (Etapa 2). O chip "Espada 1" do rodapé
  também fica para a Etapa 2.
- Inimigos não soltam **meio coração** nem **cristal** (`BAL.drops`).
- **Sem som**. O código já chama `Sfx.play("nome")` nos mesmos pontos do HTML (`scripts/sfx.gd` é o ponto
  único para o som); os botões Música/Efeitos só guardam a escolha.
- Da vida ambiente do HTML, há as folhas caindo e as sombras de nuvem; as borboletas e a poeira dos passos
  ficam para depois.
- Tela inicial simples: logo, "Pressione Enter / Toque para começar", dicas e recorde, sobre o próprio bosque
  (o cenário pintado do título, "Como jogar", tela cheia e instalar ficam para a Etapa 6).

## Diferenças conhecidas em relação ao HTML

- **Chão**: não é mais pixel por pixel igual ao do HTML. As cores, a borda escura das trilhas, as listras do
  capim, os tufos e as flores são os do HTML, mas as formas vêm de FastNoiseLite e da grade de tiles de 16 px
  (bordas com cantos arredondados/diagonais em vez do contorno livre do ruído), e os canteiros e tufos ficam
  dentro de cada célula. As posições dos props seguem a regra do HTML (uma chance a cada 44 px, mesmas
  proporções), com outro sorteio, então o mapa é outro.
- **Efeitos novos**: a faísca no inimigo atingido, o brilho ao pegar joia e os anéis de subida de nível não
  existem na Etapa 1 do HTML (os anéis imitam os da relíquia do HTML). O arco do golpe é calculado por pixel
  num shader e sai um pouco mais fino que o do HTML.
- **Pausa e fim de jogo congelam o mundo** (árvore pausada): partículas, números e animações param onde estão.
- **Sorteios**: o Godot usa o próprio gerador de números aleatórios, então a mesma semente não repete uma
  partida do HTML. Os sorteios só visuais (partículas, tremor) usam outro gerador e não mudam a partida.
- **Escala**: o HTML estica o canvas (VW = teto(largura/SCALE)) para a largura exata da tela, o que dá uma escala
  levemente fracionária; aqui a escala é exatamente inteira e a sobra (menos de SCALE px) é cortada igual dos
  dois lados.
- **Texto**: o Godot desenha a Pixelify um pouco mais estreita que o Chromium; o HUD tem a mesma disposição.
- Ícone da joia no HUD em 10×12 px (2×); no HTML é 12×14 (ampliação não inteira).
- Recorde guardado em `user://recorde.cfg` (separado do recorde do navegador).

## Onde mexer no visual

Tudo abre e aparece no editor do Godot. O que cada coisa controla:

| Quero mudar… | Onde |
|---|---|
| Animações de Aren (quadros, velocidade) | `assets/sprites/aren.tres` (SpriteFrames; abre no painel SpriteFrames) — animações `andar_baixo/cima/lado` e `parado_*` |
| Animações do goblin | `assets/sprites/goblin.tres` (a velocidade real acompanha a velocidade do goblin) |
| Cor do clarão ao levar dano / do contorno do elite | `assets/materiais/inimigo.tres` → `cor_clarao`, `cor_contorno` |
| Sombra de Aren, do goblin, dos props | nó `Sombra` em `scenes/player.tscn`, `scenes/enemy.tscn`, `scenes/props/*.tscn` |
| Árvores, arbustos, pedras, tocos | `scenes/props/*.tscn` (sprite, sombra, ponto do pé = origem da cena) |
| Força/velocidade do balanço das plantas | `assets/materiais/balanco_arvore.tres` e `balanco_arbusto.tres` → `amplitude`, `velocidade`, `linhas`, `passos` |
| Peças do chão (tiles, bordas, variações) | `assets/tiles/chao.tres` (TileSet; aba TileSet do editor). O pincel de **Terreno** (Grama, Capim alto, Terra) pinta com as bordas certas |
| Cores e manchas do chão | `assets/materiais/chao.tres` → cores da grama/terra/capim, limites e os ruídos das manchas (NoiseTexture2D) |
| Quanto há de terra, capim alto, flores, tufos e props | nó `Campo` em `scenes/world.tscn` → `ruido_terra`/`limite_terra`, `ruido_capim`/`limite_capim`, `ruido_flores`/`limite_flores`, chances de detalhe, cenas dos props |
| Sombras de nuvem | nó `SombrasNuvens` (Parallax2D) em `scenes/world.tscn` → `modulate` (transparência), `autoscroll` (vento), as nuvens filhas |
| Folhas caindo | nó `Folhas` (CPUParticles2D) em `scenes/world.tscn` → `amount`, cores, velocidade |
| Golpe da espada | `scenes/efeitos/golpe_espada.tscn` → cores do arco (material do `Arco`), `Faiscas`, animação `golpe` do AnimationPlayer |
| Números de dano | `scenes/efeitos/numero_dano.tscn` → `subida`, `duracao`, `cor_forte`, sombra do Label |
| Poeira da morte, faísca, brilho da joia | `scenes/efeitos/poeira_morte.tscn`, `faisca.tscn`, `brilho_joia.tscn` (CPUParticles2D: quantidade, cores, velocidade, duração) |
| Subida de nível | `scenes/efeitos/subiu_nivel.tscn` → animação `explodir`, anéis, `Brilho` |
| Limite de efeitos ao mesmo tempo | nó `Efeitos` em `scenes/world.tscn` → `max_efeitos` |

Cuidados:
- Os PNGs vêm do HTML: para mudar um desenho, mude no jogo HTML e rode `tools/export_sprites.py`.
- `aren.tres`, `goblin.tres`, `espada.tres` e `chao.tres` são gerados por `tools/build_resources.gd`: rodar a
  ferramenta de novo apaga mudanças feitas à mão neles (mudanças nos materiais e cenas ficam).
- O campo é gerado quando o jogo roda; no editor o `TileMapLayer` aparece vazio (dá para pintar, mas o gerador
  escreve por cima nos blocos que gera). Tiles novos ou variações feitas no TileSet entram sozinhos no sorteio
  (pelos bits de terreno; os detalhes pelo dado personalizado `tipo`).
- Os números do jogo continuam só no `Bal` (`scripts/bal.gd`); nada do visual muda a partida.

## Ferramentas e testes

```bash
# testes sem janela (89 verificações: carga das cenas e recursos, números iguais ao HTML, movimento, espada,
# goblins, joias/níveis, horda, campo em blocos, TileMapLayer e terrenos, props, shaders, animações, efeitos que
# se apagam, pausa, fim de jogo). Sai com código 1 se algo falhar ou se o log tiver erro.
GODOT=/caminho/Godot_v4.7.2-stable_linux.x86_64 tests/run_tests.sh

# reexportar os sprites e as referências a partir do jogo HTML (Python + Playwright/Chromium)
python3 tools/export_sprites.py --src ../aren/src/bosque-do-enxame.html
# remontar os atlas de tiles (Python + Pillow) e os recursos do Godot (SpriteFrames, TileSet)
python3 tools/make_tileset.py
$GODOT --headless --path . -s res://tools/build_resources.gd

# desempenho numa cena cheia (150 goblins, 2 mortes por quadro), com janela (xvfb no Linux)
xvfb-run -a $GODOT --path . --rendering-driver opengl3 --audio-driver Dummy --resolution 1366x768 res://tools/bench.tscn

# capturas de tela (início, partida, efeitos, pausa, fim) em 390x844 e 1366x768, via xvfb
GODOT=/caminho/Godot... tools/shots.sh /tmp/aren-shots
# as mesmas capturas do jogo HTML, para comparar
python3 tools/html_shots.py --aren ../aren --out /tmp/aren-shots
```

## Etapas

1. **Base jogável** (esta): Aren, câmera, chão, espada, goblins, joias/níveis, HUD, pausa, fim de jogo.
2. Todas as armas e poderes + cartas de nível (escolha de 3, estilos, passivos, limite de armas).
3. Todos os inimigos + o horário (`SCHED`), hordas completas, elites, itens no chão.
4. Chefes: Paladino Possuído (5:00), Lich Ancião (10:00) e Dragão Esqueleto (15:00).
5. Som: exportar os efeitos para WAV com as ferramentas do HTML (`tools/sfx_levels.py`, catálogo de sons) + música.
6. Menus: tela de título completa, "Como jogar", bestiário, recordes.
7. Exportação para Android e para a web.

## Estrutura

```
project.godot            configurações (Compatibility, filtro Nearest, snap de pixel)
scenes/                  main, world, player, enemy, gem, hud (.tscn)
scenes/props/            arvore, arbusto, arbusto_frutas, pedra, toco
scenes/efeitos/          golpe_espada, numero_dano, faisca, poeira_morte, brilho_joia, subiu_nivel
scripts/bal.gd           autoload Bal: números do BAL/ET/SCHED do HTML, com os mesmos nomes
scripts/art.gd           autoload Art: manifesto dos sprites, quadros do HUD e a fonte
scripts/sfx.gd           autoload Sfx: ponto único para o som (vazio na Etapa 1)
scripts/game.gd          simulação da partida (porte do update() do HTML)
scripts/campo.gd         campo infinito: TileMapLayer + FastNoiseLite em blocos, detalhes e props
scripts/efeitos.gd       camada de efeitos (instancia as cenas de scenes/efeitos)
scripts/js_math.gd       Math.round do JavaScript
assets/sprites/          PNGs exportados do HTML + sprites.json (não editar à mão) + SpriteFrames (.tres)
assets/tiles/            atlas do chão e dos detalhes + tiles.json + TileSet chao.tres
assets/shaders/          inimigo, balanco, chao, arco, anel (.gdshader)
assets/materiais/        materiais com os parâmetros dos shaders (.tres)
assets/font/             Pixelify Sans + OFL.txt + digitos.png (fonte de imagem dos números de dano)
tests/                   run_tests.gd/.tscn/.sh + ref/ (números do HTML)
tools/                   export_sprites.py, make_tileset.py, build_resources.gd, bench.gd/.tscn, shots.sh, html_shots.py
```
