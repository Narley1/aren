# CLAUDE.md — como trabalhar neste projeto

Jogo: **Aren, o Guardião do Bosque** — sobrevivência 2D em pixel art (HTML5 Canvas + JavaScript puro), interface em português do Brasil. Dono: Narley (GitHub `Narley1`).

## Branches

- **`dev`** — código-fonte, ferramentas, testes e documentação. É aqui que se trabalha.
- **`main`** — só o build (`dist/`), servido pelo GitHub Pages em https://narley1.github.io/aren/. **Nunca** commitar, dar push ou force-push no `main` sem aprovação explícita do dono. Publicar = substituir o conteúdo do `main` pelo `dist/` gerado; isso só acontece quando o Narley pedir.

## Arquivos

- `src/bosque-do-enxame.html` — o jogo inteiro, arquivo único. Fonte da verdade. É um *fragmento* (sem `<!doctype>`/`<head>`): o build e o shell do artifact colocam o cabeçalho, o charset e a regra `[hidden]{display:none!important}`.
- `src/font/` — Pixelify Sans (OFL). A fonte já vai embutida em base64 no HTML.
- `tools/build_web.py` — gera `dist/` (index.html, manifest, sw.js, README, OFL.txt) e `aren-github-pages.zip`.
- `tools/gen_assets.py` — ícones e og-image (precisa de navegador).
- `tools/sound_catalog.json` — catálogo de todos os sons e músicas (nome, quando toca, chamada no `SFX`) e dos momentos sem som.
- `tools/sfx_levels.py` — mede pico/volume de cada som pelo mixer real do jogo (OfflineAudioContext). `tools/build_sound_lab.py` — gera o Laboratório de Som (página para ouvir, comparar e dar nota).
- `tools/sprite_sheet.py` — folha de contato de todos os sprites (herói, inimigos, chefes, ícones) em escala inteira, sobre fundo escuro e claro, para revisão.
- `tests/smoke.py` — teste principal (ver abaixo). `tests/legacy/`, `tests/shot*.py`, `tests/test.html` são históricos.
- Documentação: `ARCHITECTURE.md` (mapa do código), `ROADMAP.md`, `TASKS.md`, `CHANGELOG.md`.

## Comandos

```bash
# testes (Chromium headless via Playwright; ~30 s)
python3 tests/smoke.py                       # sai com código 1 se algo falhar
python3 tests/smoke.py --json /tmp/a.json    # guarda os números
python3 tests/smoke.py --compare /tmp/antes.json /tmp/depois.json   # determinismo

# build (de qualquer pasta; dist/ é criado na pasta atual)
python3 tools/build_web.py --src src/bosque-do-enxame.html
python3 tools/gen_assets.py                  # se dist/icons ainda não existir

# áudio (Chromium headless; ~40 s)
python3 tools/sfx_levels.py                  # tabela de volume; --json arq.json para guardar, --only id1,id2
python3 tools/build_sound_lab.py --out lab.html [--levels arq.json]

# sprites (Chromium headless; ~10 s)
python3 tools/sprite_sheet.py --out sprites.png [--zoom 3] [--only hero,paladin,lich,icons]
```

Para refatorações que não devem mudar o jogo: rode `smoke.py --json` antes e depois e compare com `--compare`. A seção `det` (simulação com `Math.random` semeado e áudio desligado) precisa sair **IDENTICAL**.

## Regras

1. **Sem bibliotecas.** Nada de frameworks, engines ou CDNs: canvas 2D, Web Audio e DOM puros.
2. **Pixel-perfect.** Sprites desenhados em código, sem suavização (`imageSmoothingEnabled = false`), coordenadas arredondadas, escala inteira. Não introduzir imagens externas.
3. **Interface em PT-BR.** Todo texto visível em português do Brasil. Identificadores e comentários de código podem ser em inglês (é o padrão do arquivo).
4. **Saída em arquivo único.** O jogo continua sendo um único HTML; o build só acrescenta cabeçalho/PWA.
5. **Balanceamento e remoções são do dono.** Mudar números de `BAL`/`ET`/`UPG`/`SCHED`, remover poderes, inimigos ou mecânicas só com aprovação do Narley. Correções e limpezas não podem alterar o comportamento (prove com o teste de determinismo).
6. **Não afirmar o que não foi testado.** Ao relatar, diga o que foi verificado e como (teste, número, captura) e o que ficou sem verificar.
7. Commits no `dev`, em português, pequenos e por assunto. Autor `Narley1 <lemosnarley@gmail.com>`.
8. Antes de remover um nome, confirme com `grep` que ele não é usado.
