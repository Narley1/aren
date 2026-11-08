# Roadmap — Aren, o Guardião do Bosque

Cada etapa é desenvolvida no `dev`, testada com `tests/smoke.py` e só vai para o ar (`main`) quando o Narley aprovar. Mudanças de balanceamento e remoções de conteúdo dependem da aprovação dele.

## Etapa 1 — Correções, limpeza e documentação ✔

Concluída (novembro de 2026). Correções de entrada, áudio, timeouts, wake lock e foco; código morto removido; constantes de balanceamento centralizadas em `BAL` sem mudar valores; build e service worker revistos; `tests/smoke.py` com teste de determinismo; documentação (`CLAUDE.md`, `ARCHITECTURE.md`, este arquivo, `CHANGELOG.md`, `TASKS.md`). Detalhes no `CHANGELOG.md`.

## Etapa 2 — Desempenho ✔

Concluída (novembro de 2026). Camada de software para os efeitos (`LX`), chão gerado aos poucos à frente do movimento, culling, menos alocação por quadro, cena congelada na pausa, inicialização mais leve, `tests/perf.py`. No fim de partida com tudo no máximo (CPU 4x, Chromium headless): 39 → 60 fps, render 23 → 12 ms. Mudança de jogo aprovada: shurikens voltam mais rápido. Detalhes no `CHANGELOG.md`.

Falta: medir num celular intermediário real (a meta de 60 fps estáveis foi verificada só em emulação).

## Etapa 3 — Balanceamento e estrutura de 15 minutos ✔

Concluída no `dev` (novembro de 2026), aguardando o Narley jogar. Marcos de chefe aos 5:00/10:00/15:00 (Paladino e Lich provisórios: guardião elite que solta a relíquia), relíquias só dos chefes, Chuva de Meteoros removida, joias como experiência, 3 opções e escolhas mais frequentes, curva de dificuldade até 15:00, nerf do 1º nível suavizado, dragão que depende das armas (a espada o alcança quando atordoado). Simulador `tests/balance/`. Detalhes e números no `CHANGELOG.md`.

Falta: testes do Narley (ver `TASKS.md`).

## Etapa 4 — Novos poderes por estilo ✔

Concluída no `dev` (novembro de 2026), aguardando o Narley jogar. Todo poder tem um estilo (Corpo a corpo, A distância, Híbrido) mostrado nas cartas, no HUD e em "Como jogar". Novas armas: **Martelo Sísmico** e **Aura de Espinhos** (corpo a corpo), **Arco Élfico** (a distância); novos passivos: **Manoplas do Guerreiro** e **Grimório Arcano**. Escolhas favorecem poderes que Aren já tem e há limite de 4 armas (decisão a confirmar). Bot por estilo: corpo a corpo, a distância e híbrido sobrevivem parecido. Detalhes no `CHANGELOG.md`.

Falta: testes do Narley e decisões listadas em `TASKS.md`.

## Etapa 5 — Chefes

- Implementar Paladino e Lich Ancião com padrões próprios, apresentação e recompensa (relíquia), no mesmo nível de acabamento do Dragão Esqueleto.
