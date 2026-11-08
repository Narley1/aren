# Roadmap — Aren, o Guardião do Bosque

Cada etapa é desenvolvida no `dev`, testada com `tests/smoke.py` e só vai para o ar (`main`) quando o Narley aprovar. Mudanças de balanceamento e remoções de conteúdo dependem da aprovação dele.

## Etapa 1 — Correções, limpeza e documentação ✔

Concluída (novembro de 2026). Correções de entrada, áudio, timeouts, wake lock e foco; código morto removido; constantes de balanceamento centralizadas em `BAL` sem mudar valores; build e service worker revistos; `tests/smoke.py` com teste de determinismo; documentação (`CLAUDE.md`, `ARCHITECTURE.md`, este arquivo, `CHANGELOG.md`, `TASKS.md`). Detalhes no `CHANGELOG.md`.

## Etapa 2 — Desempenho ✔

Concluída (novembro de 2026). Camada de software para os efeitos (`LX`), chão gerado aos poucos à frente do movimento, culling, menos alocação por quadro, cena congelada na pausa, inicialização mais leve, `tests/perf.py`. No fim de partida com tudo no máximo (CPU 4x, Chromium headless): 39 → 60 fps, render 23 → 12 ms. Mudança de jogo aprovada: shurikens voltam mais rápido. Detalhes no `CHANGELOG.md`.

Falta: medir num celular intermediário real (a meta de 60 fps estáveis foi verificada só em emulação).

## Etapa 3 — Balanceamento e estrutura de 15 minutos

- Partida de 15 minutos com três chefes: **Paladino** aos 5:00 → **Lich Ancião** aos 10:00 → **Dragão** aos 15:00.
- Relíquias passam a vir dos chefes: **Espada Sagrada** do Paladino, **Tempestade de Raios** do Lich. A relíquia **Chuva de Meteoros** sai do jogo.
- Experiência por tipo de inimigo, com as joias como a própria experiência.
- 3 opções por escolha de poder e escolhas mais frequentes.
- Armas passam a contar contra o chefe (dano normal relevante, não só os selos).
- Suavizar o "muro" dos 5:30 (pico de dificuldade).
- Suavizar o nerf do primeiro nível dos poderes.

## Etapa 4 — Novos poderes por estilo

- Corpo a corpo: **Martelo Sísmico**, **Aura de Espinhos**.
- À distância: **Arco Élfico**.
- Passivos: **Manoplas do Guerreiro** (reforça corpo a corpo), **Grimório Arcano** (reforça à distância).

## Etapa 5 — Chefes

- Implementar Paladino e Lich Ancião com padrões próprios, apresentação e recompensa (relíquia), no mesmo nível de acabamento do Dragão Esqueleto.
