"""Paleta da arte nova (rodada 1): rampas com nome, sempre do mais escuro para o mais claro.

Base: as cores do Aren e do goblin do jogo HTML (SPR32.hero / SPR32.goblin), com tons a mais em cada ponta
para dar volume (estilo Minish Cap: cores vivas, sombra puxada para o roxo/vinho, brilho puxado para o amarelo).
"""

RAMPAS = {
    # --- Aren
    'cabelo':  ['#4a2412', '#6e3818', '#a35c2e', '#d08a44', '#f4c070'],   # HTML: h, H, i (+2)
    'pele':    ['#9a4e3a', '#d8946a', '#f8cca0', '#fff0dc'],              # HTML: s, S (+2)
    'bochecha': ['#f29a86'],
    'tunica':  ['#1c3270', '#2a5aa6', '#3f86dc', '#78b4f0', '#c8e6ff'],   # HTML: t, T, u (+2)
    'cachecol': ['#5e1420', '#a82e22', '#e8503a', '#ff9466'],             # HTML: r, R (+2)
    'couro':   ['#2e180c', '#4a2810', '#7a4422', '#a8683a', '#d4975e'],   # HTML: n, B, L (+2)
    'calca':   ['#7a6a52', '#c8b896', '#e9dcc0', '#fffaee'],              # HTML: p, P (+2)
    'ouro':    ['#7a4a0c', '#c98a1e', '#f2c14e', '#fff2a8'],              # HTML: y (+3)
    'olho':    ['#1a1030', '#2a1a3a', '#4a6ab8', '#ffffff'],              # HTML: e (+ reflexo)
    'metal':   ['#2a3048', '#5a6a88', '#9aaac4', '#dfe6ee', '#ffffff'],   # lâmina da espada
    'madeira': ['#3a2010', '#5e3b1a', '#8a5a2b', '#b8844a'],
    # --- goblin
    'goblin':  ['#173a14', '#2e6a1e', '#58922a', '#86c83e', '#b8ec78', '#e6ffb4'],  # HTML: g, G, l (+3)
    'tanga':   ['#2e1e0e', '#4a3018', '#6e4a26', '#9a6a38', '#c08c50'],              # HTML: n, c, C (+2)
    'olho_gob': ['#8a5a08', '#e0a820', '#ffe14a', '#fffbe8'],                        # HTML: Y, w
    'boca':    ['#2a0e0a', '#3a1a10', '#8a2a2a'],
    'dente':   ['#c8c0a0', '#fffbe8'],
    # --- efeitos
    'faisca':  ['#ff7a1a', '#ffc23a', '#fff07a', '#ffffff'],
    'corte':   ['#3a78d8', '#78b8ff', '#c8ecff', '#ffffff'],
    'poeira':  ['#8a6e4c', '#b89a70', '#dcc8a0', '#fff4dc'],
    'fumaca':  ['#4a4a6a', '#7a7a9a', '#b4b4cc', '#eeeef8'],
    'brilho':  ['#3ad6a0', '#9affd8', '#fff6b0', '#ffffff'],
    'sombra':  ['#14281466'],
}

# Contornos coloridos: (lado da luz, lado da sombra). Nunca preto puro. O herói do HTML usa #2a1820.
CONTORNO = {
    'cabelo':  ('#4a2014', '#2a1418'),
    'pele':    ('#6a2c24', '#3a1a1c'),
    'tunica':  ('#1a2050', '#141434'),
    'cachecol': ('#4a1018', '#2a0c14'),
    'couro':   ('#2a1410', '#1e100c'),
    'calca':   ('#4a3a30', '#2a1e20'),
    'ouro':    ('#5a3010', '#3a2010'),
    'metal':   ('#2a3048', '#1a1c30'),
    'madeira': ('#2a1810', '#1e100c'),
    'goblin':  ('#1c3a10', '#102008'),
    'tanga':   ('#24160a', '#180e06'),
    'olho_gob': ('#3a2a08', '#2a1a06'),
    'boca':    ('#1c0a08', '#1c0a08'),
    'dente':   ('#3a2a20', '#2a1a14'),
}

CONTORNO_HEROI = '#2a1820'
CONTORNO_GOBLIN = '#1c2a10'
