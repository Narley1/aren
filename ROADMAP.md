# Roadmap — Aren, o Guardião do Bosque

Cada etapa é desenvolvida no `dev`, testada com `tests/smoke.py` e só vai para o ar (`main`) quando o Narley aprovar. Mudanças de balanceamento e remoções de conteúdo dependem da aprovação dele.

## Etapa 1 — Correções, limpeza e documentação ✔

Concluída (novembro de 2026). Correções de entrada, áudio, timeouts, wake lock e foco; código morto removido; constantes de balanceamento centralizadas em `BAL` sem mudar valores; build e service worker revistos; `tests/smoke.py` com teste de determinismo; documentação (`CLAUDE.md`, `ARCHITECTURE.md`, este arquivo, `CHANGELOG.md`, `TASKS.md`). Detalhes no `CHANGELOG.md`.

## Etapa 2 — Desempenho

- Medir antes (perfil do fim de partida com muitos inimigos, efeitos e o chefe; celulares fracos).
- Reduzir alocação por quadro: `filter()` de listas a cada quadro, objetos de partículas, `Set` por projétil; usar pools e remoção in-place.
- Diminuir `fillRect` de 1 px em efeitos (anéis, selos, sopro do chefe) com sprites pré-renderizados.
- Limitar partículas por tipo; grade espacial reaproveitando arrays.
- Meta: 60 fps estáveis no fim da partida em celular intermediário. Comportamento idêntico (teste de determinismo).

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
