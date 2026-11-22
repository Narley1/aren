# CLAUDE.md — como trabalhar na versão Godot

Jogo: **Aren, o Guardião do Bosque** — porte para Godot do jogo HTML (sobrevivência 2D em pixel art).
Dono: Narley (GitHub `Narley1`). Interface em português do Brasil.

## Onde fica cada coisa

- **`godot`** (este branch, órfão) — a versão Godot. Só se trabalha aqui.
- **`dev`** e **`main`** — o jogo HTML (código e site publicado). **Nunca** modificar, commitar ou dar push neles
  a partir deste trabalho. O HTML pode ser lido (de preferência num clone/worktree separado, ex. `../aren`).
- O jogo HTML (`src/bosque-do-enxame.html` do `dev`) é a **especificação**: números, comportamentos e sprites vêm
  dele. Em dúvida, leia o HTML (`ARCHITECTURE.md` do `dev` tem o mapa do código).

## Versão do motor

- **Godot 4.7.2-stable** (padrão, GDScript, sem .NET), renderizador **Compatibility** (OpenGL; bom para web e
  celular). A versão está em `project.godot` (`config/features`) e no README. Trocar de versão só com o Narley.
- Executável fora do repositório. Sem janela: `--headless`; capturas: `xvfb-run` com `--rendering-driver opengl3`
  e `--audio-driver Dummy` (o contêiner não tem placa de som).

## Comandos

```bash
GODOT=/caminho/Godot_v4.7.2-stable_linux.x86_64
GODOT=$GODOT tests/run_tests.sh                      # testes; código 1 se algo falhar ou o log tiver ERROR
python3 tools/export_sprites.py                      # reexporta sprites e tests/ref a partir de ../aren
python3 tools/make_tileset.py                        # atlas do chão/detalhes a partir da paleta e carimbos do HTML
$GODOT --headless --path . -s res://tools/build_resources.gd   # SpriteFrames e TileSet (.tres) a partir dos PNGs
GODOT=$GODOT tools/shots.sh /tmp/aren-shots          # capturas 390x844 e 1366x768
python3 tools/html_shots.py --aren ../aren --out /tmp/aren-shots   # as mesmas capturas do HTML
xvfb-run -a $GODOT --path . --rendering-driver opengl3 --audio-driver Dummy res://tools/bench.tscn  # desempenho
```

## Regras

1. **Números só no `Bal`** (`scripts/bal.gd`), com o nome do HTML no comentário (`BAL.sword`, `ET.goblin`...).
   Nada de constante de jogo solta no código. Mudar balanceamento, remover poderes, inimigos ou mecânicas só com
   aprovação do Narley. O teste compara o `Bal` com `tests/ref/html_numbers.json` (exportado do HTML): número
   novo portado entra também no exportador e no teste.
2. **Sprites vêm do HTML.** Nunca desenhar nem editar PNG à mão: acrescentar o sprite em
   `tools/export_sprites.py` e rodar o exportador. Conferir o PNG com uma ampliação antes de usar. Os tiles do
   chão saem de `tools/make_tileset.py` (paleta e carimbos do HTML); SpriteFrames e TileSet de
   `tools/build_resources.gd` (rodar de novo sobrescreve esses .tres).
3. **Visual do jeito do Godot**, editável no editor: personagens em AnimatedSprite2D + SpriteFrames, cenário em
   TileMapLayer/TileSet (terrain set) e cenas de props, tintas e balanço em shaders (`assets/shaders`, parâmetros
   nos materiais de `assets/materiais`), efeitos como cenas em `scenes/efeitos` (CPUParticles2D, Tween,
   AnimationPlayer) que se apagam sozinhas. Nada de `_draw()` para o que pode ser cena ou recurso. Parâmetros que
   o Narley pode querer ajustar viram `@export` ou parâmetro de shader; a seção "Onde mexer no visual" do README
   acompanha. Sem `@tool`: as cenas abrem no editor sem rodar código.
4. **Pixel perfeito.** Filtro Nearest, vista em pixels lógicos ampliada por inteiro (SubViewport em `main.gd`),
   posições de desenho arredondadas com `JsMath.jround` (o `Math.round` do JS; o `round()` do Godot é diferente
   nos .5 negativos). Nada de rotação/escala livre em sprite: rotações são quadros exportados (como a espada, nos
   48 quadros de `espada.tres`). Partículas sem textura (1–2 px) e shaders que calculam por pixel inteiro do mundo.
5. **Comportamento igual ao HTML**: ao portar um trecho, siga a ordem das contas do `update()`/`render()` e deixe
   um comentário "HTML: ..." apontando o trecho. Simplificações ficam escritas no README.
6. **Simulação separada do desenho**: `game.step(dt)` não desenha; `sync_visuals()` não muda a partida. Sorteios
   da partida em `game.rng`, sorteios só visuais em `game.vis_rng`. Efeitos saem da simulação como eventos em
   `game.fx_events`, que `sync_visuals()` entrega à camada `Efeitos`.
7. **Interface em PT-BR**, com a Pixelify Sans. Identificadores e comentários de código podem ser em inglês ou
   português.
8. **Sem plugins/addons ou bibliotecas** sem aprovação do Narley (GDScript puro).
9. **Som** sempre por `Sfx.play("nome")` (autoload `scripts/sfx.gd`), com o nome do efeito do HTML.
10. **Não afirmar o que não foi testado.** Ao relatar, diga o que foi verificado e como (teste, número, captura
   olhada) e o que ficou sem verificar.
11. Commits no `godot`, em português, pequenos e por assunto. Autor `Narley1 <lemosnarley@gmail.com>`.
    Push só do branch `godot`.
12. Arquivos `.import` são versionados (guardam as opções de importação: PNG sem perda, sem mipmaps);
    a pasta `.godot/` não.
