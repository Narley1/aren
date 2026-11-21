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

- **Sprites idênticos ao HTML**, pixel por pixel: Aren (andando para baixo, cima e lados), goblin (com o
  clarão branco e o contorno dourado do elite), espada (as 48 rotações), joias, corações, logo, árvores,
  arbustos, pedras, tocos e sombras. Eles são **exportados do próprio jogo HTML** por `tools/export_sprites.py`.
- **Chão infinito igual ao do HTML**: o gerador de chão (ruído, trilhas de terra, capim alto, flores, carimbos)
  e a posição dos props foram portados com a mesma aritmética; o teste compara blocos de chão com os do HTML e
  eles saem idênticos (0 pixel diferente).
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
- Sem a vida ambiente do HTML (borboletas, folhas, sombras de nuvem).
- Tela inicial simples: logo, "Pressione Enter / Toque para começar", dicas e recorde, sobre o próprio bosque
  (o cenário pintado do título, "Como jogar", tela cheia e instalar ficam para a Etapa 6).

## Diferenças conhecidas em relação ao HTML

- **Sorteios**: o Godot usa o próprio gerador de números aleatórios, então a mesma semente não repete uma
  partida do HTML. Os sorteios só visuais (partículas, tremor) usam outro gerador e não mudam a partida.
- **Escala**: o HTML estica o canvas (VW = teto(largura/SCALE)) para a largura exata da tela, o que dá uma escala
  levemente fracionária; aqui a escala é exatamente inteira e a sobra (menos de SCALE px) é cortada igual dos
  dois lados.
- **Texto**: o Godot desenha a Pixelify um pouco mais estreita que o Chromium; o HUD tem a mesma disposição.
- Ícone da joia no HUD em 10×12 px (2×); no HTML é 12×14 (ampliação não inteira).
- Recorde guardado em `user://recorde.cfg` (separado do recorde do navegador).

## Ferramentas e testes

```bash
# testes sem janela (56 verificações: carga, números iguais ao HTML, chão idêntico, movimento, espada,
# goblins, joias/níveis, horda, chão em threads, pausa, fim de jogo). Sai com código 1 se algo falhar.
GODOT=/caminho/Godot_v4.7.2-stable_linux.x86_64 tests/run_tests.sh

# reexportar os sprites e as referências a partir do jogo HTML (Python + Playwright/Chromium)
python3 tools/export_sprites.py --src ../aren/src/bosque-do-enxame.html

# capturas de tela (início, partida, pausa, fim) em 390x844 e 1366x768, via xvfb
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
scripts/bal.gd           autoload Bal: números do BAL/ET/SCHED do HTML, com os mesmos nomes
scripts/art.gd           autoload Art: carrega os sprites exportados e a fonte
scripts/sfx.gd           autoload Sfx: ponto único para o som (vazio na Etapa 1)
scripts/game.gd          simulação da partida (porte do update() do HTML)
scripts/ground_gen.gd    gerador do chão e dos props (porte exato)
scripts/js_math.gd       aritmética do JavaScript (Math.imul, Math.round, hash, ruído)
assets/sprites/          PNGs exportados do HTML + sprites.json (não editar à mão)
assets/font/             Pixelify Sans + OFL.txt
tests/                   run_tests.gd/.tscn/.sh + ref/ (blocos de chão e números do HTML)
tools/                   export_sprites.py, shots.sh, html_shots.py
```
