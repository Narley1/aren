extends Node
## Autoload "Bal": todos os números de jogo, copiados do jogo HTML (src/bosque-do-enxame.html, objetos
## BAL, ET e SCHED e funções xpNeed/isPickLevel). Os nomes seguem os do HTML para facilitar a conferência;
## o teste (tests/run_tests.gd) compara estes valores com tests/ref/html_numbers.json, exportado do HTML.
## Mudar um número aqui muda o jogo: balanceamento é decisão do Narley.

# BAL.hero — vida em MEIOS corações; velocidade em px/s; invulnerabilidade em s
const HERO := {
	"hp": 10, "speed": 71.3, "bootsSpeed": 9, "slowMult": 0.55,
	"invStart": 1.2, "invHit": 1.0, "invAfterPick": 0.6,
}

# BAL.sword — el = 1 + (lvl - 1)*lvlStep; dmg = dmgBase + el*dmgPerLvl; range = rangeBase + el*rangePerLvl;
# cd = max(cdMin, cdBase - el*cdPerLvl); cdIdle = espera quando não há alvo
const SWORD := {
	"lvlStep": 1.75, "dmgBase": 5, "dmgPerLvl": 1.7, "rangeBase": 17, "rangePerLvl": 2.3,
	"cdBase": 0.85, "cdPerLvl": 0.07, "cdMin": 0.3, "cdIdle": 0.05,
}
const SWORD_SWING_DUR := 0.26      # G.swing.dur no update() do HTML
const SWORD_ARC_LOW := PI * 0.8    # sw.arc abaixo do nível 5 (no 5 é o círculo inteiro)
const SWORD_KB := 90               # empurrão do golpe: hit(e, sw.dmg, nx, ny, 90)
const SWORD_FIRST_CD := 0.3        # G.swCd inicial em reset()

# BAL.xp — xpNeed(L) = round(base + lin*(L - 1) + quad*(L - 1)^2); escolha de poder nos níveis de picks,
# depois a cada pickEvery níveis
const XP := {"base": 8, "lin": 4.5, "quad": 0.3, "picks": [2, 3, 5, 7, 10], "pickEvery": 3}

# BAL.spawn — intervalo = max(intervalMin, interval/(1 + t/intervalT)); sem spawn com cap inimigos vivos
const SPAWN := {"interval": 0.95, "intervalT": 75, "intervalMin": 0.07, "cap": 230, "guardMul": 0.25, "guardCalmT": 75}

# BAL.horde — primeira horda em first s; depois a cada max(everyMin, every - t/everyPerT) s;
# quantidade = min(countMax, count + floor(t/countPerT)); antes de hobAt s a horda é de goblins
const HORDE := {"first": 50, "every": 55, "everyPerT": 12, "everyMin": 18, "count": 16, "countPerT": 18, "countMax": 60, "hobAt": 150, "demonAt": 330}

# BAL.elite — elites só depois de 'after' s (chance; multiplicadores de vida, velocidade, empurrão, joias)
const ELITE := {"after": 30, "chance": 0.022, "rampStart": 240, "rampDur": 660, "rampAdd": 0.11, "hp": 7, "spd": 0.9, "kbDiv": 3, "gems": 6}

# BAL.hpScaleT / BAL.hpScaleQ — vida dos inimigos x (1 + t/hpScaleT + (t/hpScaleQ)^2)
const HP_SCALE_T := 220
const HP_SCALE_Q := 430

# BAL.drops (só a parte usada na Etapa 1: gemCap)
const DROPS := {"up": 0.0025, "upElite": 0.12, "life": 0.05, "lifeElite": 0.4, "decayAt": 240, "decayT": 160, "gemCap": 400}

# Ímã das joias (update() do HTML, "// gems"): raio = 26 + W.magnet*16; velocidade 120 + (raio - d)*3; coleta a < 6 px
const MAGNET_BASE := 26
const MAGNET_PER_LVL := 16
const GEM_PULL_SPD := 120
const GEM_PICK_R := 6

# hurt(): ao levar dano, inimigos a até 34 px são empurrados com força 120
const HURT_PUSH_R := 34
const HURT_PUSH := 120

# ET.goblin — hp, velocidade px/s, dano (meios corações), raio, escala (sc), joias; w/h = tamanho do sprite
const ET := {
	"goblin": {"name": "Goblin", "hp": 4, "spd": 28, "dmg": 1, "r": 6, "sc": 1, "gem": 1, "ai": "walk"},
}

# SCHED — horário (s) em que cada inimigo passa a aparecer. Etapa 1: só o goblin (a gárgula chega aos 45 s
# no HTML; fica para a Etapa 3)
const SCHED := [["goblin", 0]]

# hit(): empurrão padrão e duração do clarão branco
const HIT_FLASH := 0.09


func xp_need(L: int) -> int:
	return JsMath.jround(XP.base + XP.lin * (L - 1) + XP.quad * (L - 1) * (L - 1))


func is_pick_level(L: int) -> bool:
	var picks: Array = XP.picks
	var last: int = picks[picks.size() - 1]
	return picks.has(L) or (L > last and (L - last) % int(XP.pickEvery) == 0)


func next_pick_level(L: int) -> int:
	var n := L + 1
	while not is_pick_level(n):
		n += 1
	return n


## Números da espada no nível l (SWS no update() do HTML), sem Espada Sagrada nem passivos (Etapa 2).
func sword_stats(l: int) -> Dictionary:
	var el := 1.0 + (l - 1) * SWORD.lvlStep
	return {
		"dmg": SWORD.dmgBase + el * SWORD.dmgPerLvl,
		"range": SWORD.rangeBase + el * SWORD.rangePerLvl,
		"cd": maxf(SWORD.cdMin, SWORD.cdBase - el * SWORD.cdPerLvl),
		"arc": TAU if l >= 5 else SWORD_ARC_LOW,
		"double": l >= 3 and l < 5,
	}


## hpScale() do HTML
func hp_scale(t: float) -> float:
	return 1.0 + t / HP_SCALE_T + pow(t / HP_SCALE_Q, 2)


## Intervalo de spawn no tempo t (sem chefes na Etapa 1)
func spawn_interval(t: float) -> float:
	return maxf(SPAWN.intervalMin, SPAWN.interval / (1.0 + t / SPAWN.intervalT))
