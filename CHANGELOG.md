# Changelog

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
