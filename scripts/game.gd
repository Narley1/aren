extends Node2D
## O mundo e a simulação da partida — porte da parte da Etapa 1 do update() do HTML: movimento, spawn de
## goblins (com hordas e elites), espada, inimigos, joias/experiência e dano. Os comentários "HTML:" apontam
## para o trecho equivalente em src/bosque-do-enxame.html.
##
## A simulação roda em step(dt) e não depende de desenho: os testes chamam step() direto. Sorteios da
## simulação usam `rng` (semeável); efeitos só visuais usam `vis_rng`, então desenhar não muda a partida.

signal toast(title: String, sub: String)
signal died
signal leveled(lvl: int, pick: bool)

const PlayerScene := preload("res://scenes/player.tscn")
const EnemyScene := preload("res://scenes/enemy.tscn")
const GemScene := preload("res://scenes/gem.tscn")
const CELL := 32

# estado da partida (G no HTML)
var t := 0.0                 # relógio da partida (s)
var rt := 0.0                # tempo real (animações)
var kills := 0
var gems_total := 0          # joias recolhidas (= experiência total)
var ups := 0                 # poderes escolhidos (Etapa 2)
var spawn_t := 0.0
var wave_t: float = Bal.HORDE.first
var sw_cd: float = Bal.SWORD_FIRST_CD
var sw_rev := false
var swing = null             # {t, dur, ang, arc, range, dirs, rev} ou null
var xp := 0
var lvl := 1
var need := 8
var pending := 0             # escolhas de poder pendentes (as cartas chegam na Etapa 2)
var shake := 0.0
var sword_lvl := 1           # W.sword

var enemies: Array = []
var gems: Array = []
var fx: Array = []           # partículas {x, y, vx, vy, t, life, col, s}
var nums: Array = []         # números de dano {x, y, v, t, col}

var rng := RandomNumberGenerator.new()
var vis_rng := RandomNumberGenerator.new()
var vw := 200                # tamanho da vista em pixels lógicos (VW, VH do HTML)
var vh := 300
var cam := Vector2i.ZERO     # canto da câmera (cx, cy)
var joy = null               # joystick de toque: {ox, oy, x, y} em px de interface (CSS px do HTML)
var input_enabled := true
var force_input := Vector2.ZERO   # usado pelos testes/capturas (soma ao teclado)

var _grid: Dictionary = {}

@onready var ground: Node2D = $Ground
@onready var gem_layer: Node2D = $Gems
@onready var shadows: Node2D = $Shadows
@onready var actors: Node2D = $Actors
@onready var fx_layer: Node2D = $Fx
@onready var camera: Camera2D = $Camera
var player: Node2D


func _ready() -> void:
	player = PlayerScene.instantiate()
	actors.add_child(player)
	ground.actors = actors
	shadows.game = self
	fx_layer.game = self
	vis_rng.randomize()
	rng.randomize()
	reset()


## reset() do HTML (parte da Etapa 1)
func reset() -> void:
	t = 0.0; rt = 0.0; kills = 0; gems_total = 0; ups = 0
	spawn_t = 0.0; wave_t = Bal.HORDE.first; sw_cd = Bal.SWORD_FIRST_CD; sw_rev = false; swing = null
	xp = 0; lvl = 1; need = Bal.xp_need(1); pending = 0; shake = 0.0; sword_lvl = 1
	for e in enemies:
		e.queue_free()
	for g in gems:
		g.queue_free()
	enemies.clear(); gems.clear(); fx.clear(); nums.clear()
	joy = null
	player.reset()
	sync_visuals()


func rnd() -> float:
	return rng.randf()


# ---------------------------------------------------------------- spawn (HTML: "spawning")

func spawn(type: String, ang = null, dist = null, elite := false) -> Node2D:
	var a: float = ang if ang != null else rnd() * TAU
	var R: float = dist if dist != null else Vector2(vw, vh).length() / 2.0 + 18.0
	var m: float = Bal.hp_scale(t) * (Bal.ELITE.hp if elite else 1.0)
	var e := EnemyScene.instantiate()
	actors.add_child(e)
	e.setup(type, player.px + cos(a) * R, player.py + sin(a) * R, m, elite, rnd() * 2.0)
	enemies.append(e)
	if elite:
		Sfx.play("elite")
	return e


## pickType() do HTML. Na Etapa 1 só existe o goblin no SCHED.
func pick_type() -> String:
	return "goblin"


# ---------------------------------------------------------------- grade espacial (HTML: gridBuild/query)

func _grid_build() -> void:
	_grid.clear()
	for e in enemies:
		if e.dead:
			continue
		var k := floori(e.ex / CELL) * 65536 + floori(e.ey / CELL)
		if not _grid.has(k):
			_grid[k] = []
		_grid[k].append(e)


func query(x: float, y: float, r: float) -> Array:
	var out := []
	for cx in range(floori((x - r) / CELL), floori((x + r) / CELL) + 1):
		for cy in range(floori((y - r) / CELL), floori((y + r) / CELL) + 1):
			var a = _grid.get(cx * 65536 + cy)
			if a == null:
				continue
			for e in a:
				if not e.dead:
					out.append(e)
	return out


func nearest(x: float, y: float, max_d: float) -> Node2D:
	var best: Node2D = null
	var bd := max_d * max_d
	for e in enemies:
		if e.dead:
			continue
		var d2: float = (e.ex - x) ** 2 + (e.ey - y) ** 2
		if d2 < bd:
			bd = d2
			best = e
	return best


# ---------------------------------------------------------------- combate (HTML: hit, kill, gainXp, hurt)

func hit(e: Node2D, dmg: float, nx = null, ny = null, kb := 70.0) -> void:
	if e.dead:
		return
	if nx == null:
		var dx: float = e.ex - player.px
		var dy: float = e.ey - player.py
		var l := Vector2(dx, dy).length()
		if l == 0: l = 1.0
		nx = dx / l
		ny = dy / l
	e.hp -= dmg
	e.flash = Bal.HIT_FLASH
	var k: float = kb / (e.d.sc * e.d.sc) / (Bal.ELITE.kbDiv if e.elite else 1.0)
	e.kx += nx * k
	e.ky += ny * k
	nums.append({"x": e.ex + (vis_rng.randf() * 6 - 3), "y": e.ey - e.d.h, "v": maxi(1, JsMath.jround(dmg)), "t": 0.0,
		"col": Color("#ffd94a") if dmg >= 15 else Color.WHITE})
	if e.hp <= 0:
		kill(e)


func kill(e: Node2D) -> void:
	e.dead = true
	kills += 1
	Sfx.play("kill", e.type)
	var n := 10 if e.d.sc > 1 else 6
	for i in n:
		var a := vis_rng.randf() * TAU
		var s := 20 + vis_rng.randf() * 40
		fx.append({"x": e.ex, "y": e.ey - e.d.h / 2.0, "vx": cos(a) * s, "vy": sin(a) * s, "t": 0.0,
			"life": 0.35 + vis_rng.randf() * 0.25, "col": Color.WHITE if i % 2 else Color("#d6d0e6"), "s": 1 if vis_rng.randf() < 0.5 else 2})
	# experiência em joias de 10/5/1 (elites x BAL.elite.gems); só conta quando Aren recolhe
	var v: int = e.d.gem * (Bal.ELITE.gems if e.elite else 1)
	var spread := 10.0
	while v > 0:
		var val := 10 if v >= 10 else (5 if v >= 5 else 1)
		v -= val
		add_gem(e.ex + (rnd() - 0.5) * spread, e.ey + (rnd() - 0.5) * spread * 0.8, val)
	# (Etapa 3: cristal e meio coração no chão — BAL.drops)
	while gems.size() > Bal.DROPS.gemCap:
		_merge_gem()


func add_gem(x: float, y: float, v: int) -> Node2D:
	var g := GemScene.instantiate()
	gem_layer.add_child(g)
	g.setup(x, y, v)
	gems.append(g)
	return g


func _merge_gem() -> void:
	var g = gems.pop_front()
	var best = gems[0]
	var bd := INF
	for o in gems:
		var d2: float = (o.gx - g.gx) ** 2 + (o.gy - g.gy) ** 2
		if d2 < bd:
			bd = d2
			best = o
	best.v += g.v
	g.queue_free()


func gain_xp(n: int) -> void:
	xp += n
	while xp >= need:
		xp -= need
		lvl += 1
		need = Bal.xp_need(lvl)
		if Bal.is_pick_level(lvl):
			pending += 1
			Sfx.play("levelUp")
			toast.emit("Nível %d!" % lvl, "A escolha de poderes chega na próxima etapa")
			leveled.emit(lvl, true)
		else:
			player.hp = mini(player.max_hp, player.hp + 1)
			Sfx.play("lvlSmall")
			toast.emit("Nível %d" % lvl, "+½ coração · próximo poder no nível %d" % Bal.next_pick_level(lvl))
			leveled.emit(lvl, false)


func hurt(n: int) -> void:
	if player.inv > 0:
		return
	player.hp -= n
	player.inv = Bal.HERO.invHit
	shake = 0.25
	Sfx.play("hurt")
	for e in query(player.px, player.py, Bal.HURT_PUSH_R):
		var dx: float = e.ex - player.px
		var dy: float = e.ey - player.py
		var l := Vector2(dx, dy).length()
		if l == 0: l = 1.0
		e.kx += dx / l * Bal.HURT_PUSH
		e.ky += dy / l * Bal.HURT_PUSH
	if player.hp <= 0:
		player.hp = 0
		died.emit()


# ---------------------------------------------------------------- entrada

## Direção pedida (teclado WASD/setas + joystick de toque), como no update() do HTML.
func read_input() -> Vector2:
	var ix := 0.0
	var iy := 0.0
	if input_enabled:
		if Input.is_action_pressed("move_left"): ix -= 1
		if Input.is_action_pressed("move_right"): ix += 1
		if Input.is_action_pressed("move_up"): iy -= 1
		if Input.is_action_pressed("move_down"): iy += 1
	ix += force_input.x
	iy += force_input.y
	if joy != null:
		var dx: float = joy.x - joy.ox
		var dy: float = joy.y - joy.oy
		var l := Vector2(dx, dy).length()
		if l > 6:
			var m := minf(1.0, l / 40.0)
			ix = dx / l * m
			iy = dy / l * m
	return Vector2(ix, iy)


# ---------------------------------------------------------------- passo da simulação (HTML: update(dt))

func step(dt: float) -> void:
	rt += dt
	t += dt
	var inp := read_input()
	player.move(inp.x, inp.y, dt)
	shake = maxf(0.0, shake - dt)

	# spawn
	spawn_t -= dt
	var interval := Bal.spawn_interval(t)
	while spawn_t <= 0:
		spawn_t += interval
		if enemies.size() < Bal.SPAWN.cap:
			var type := pick_type()
			var EL: Dictionary = Bal.ELITE
			var elite: bool = t > EL.after and rnd() < EL.chance + minf(1.0, maxf(0.0, t - EL.rampStart) / EL.rampDur) * EL.rampAdd
			spawn(type, null, null, elite)
	wave_t -= dt
	if wave_t <= 0:
		var HO: Dictionary = Bal.HORDE
		wave_t = maxf(HO.everyMin, HO.every - t / HO.everyPerT)
		var n: int = mini(HO.countMax, HO.count + floori(t / HO.countPerT))
		for i in n:   # antes de hobAt (150 s) a horda é de goblins; hobgoblins e demônios na Etapa 3
			spawn("goblin", float(i) / n * TAU, Vector2(vw, vh).length() / 2.0 + 10.0)
		toast.emit("Uma horda cerca você!", "Abra caminho")

	_grid_build()
	_sword(dt)
	_enemies(dt)
	_gems(dt)
	# partículas e números
	for f in fx:
		f.t += dt
		f.x += f.vx * dt
		f.y += f.vy * dt
		f.vx *= 0.92
		f.vy *= 0.92
	fx = fx.filter(func(f): return f.t < f.life)
	for n in nums:
		n.t += dt
		n.y -= 18 * dt
	nums = nums.filter(func(n): return n.t < 0.6)
	if nums.size() > 80:
		nums = nums.slice(nums.size() - 80)


## Espada: golpe automático no inimigo mais próximo (HTML: "// sword" no update)
func _sword(dt: float) -> void:
	sw_cd -= dt
	if swing != null:
		swing.t += dt
		if swing.t >= swing.dur:
			swing = null
		elif swing.t / swing.dur >= 0.16 and swing.t / swing.dur < 0.72 and vis_rng.randf() < 0.7:
			_swing_spark()
	if sw_cd > 0:
		return
	var sw := Bal.sword_stats(sword_lvl)
	var tg := nearest(player.px, player.py, sw.range + 16)
	if tg == null:
		sw_cd = Bal.SWORD.cdIdle
		return
	var ang := atan2(tg.ey - (player.py - 9), tg.ex - player.px)
	var dirs := [ang, ang + PI] if sw.double else [ang]
	sw_rev = not sw_rev
	swing = {"t": 0.0, "dur": Bal.SWORD_SWING_DUR, "ang": ang, "arc": sw.arc, "range": sw.range, "dirs": dirs,
		"rev": sw_rev and sw.arc < 6}
	Sfx.play("sword", sword_lvl)
	for e in query(player.px, player.py - 9, sw.range + 14):
		var dx: float = e.ex - player.px
		var dy: float = (e.ey - e.d.h / 3.0) - (player.py - 9)
		var dist := Vector2(dx, dy).length()
		if dist > sw.range + e.d.r:
			continue
		var a := atan2(dy, dx)
		var ok: bool = sw.arc >= 6
		for d in dirs:
			if absf(angle_difference(d, a)) <= sw.arc / 2.0 + 0.25:
				ok = true
		if ok:
			var dd := dist if dist != 0 else 1.0
			hit(e, sw.dmg, dx / dd, dy / dd, Bal.SWORD_KB)
	sw_cd = sw.cd
	player.face_toward(ang)


## Ângulo atual da lâmina no golpe (render() do HTML, "// sword swing")
static func swing_pose(s: Dictionary, dir: float) -> Dictionary:
	var T: float = s.t / s.dur
	var wind := 0.16
	var q := (T - wind) / (0.7 - wind)
	var pr := 0.0 if T < wind else minf(1.0, 1.0 - pow(1.0 - q, 3))
	var fade := 1.0 if T < 0.7 else maxf(0.0, 1.0 - (T - 0.7) / 0.3)
	var sg := -1.0 if s.rev else 1.0
	var a0: float = dir - sg * s.arc / 2.0
	var span: float = s.arc * sg
	var cur := (a0 - sg * 0.35 * (T / wind)) if T < wind else (a0 + span * pr)
	return {"T": T, "pr": pr, "fade": fade, "sg": sg, "a0": a0, "span": span, "cur": cur}


func _swing_spark() -> void:
	for dir in swing.dirs:
		var p := swing_pose(swing, dir)
		var tr := minf(swing.range, 22.0)
		var cur: float = p.cur
		var sg: float = p.sg
		fx.append({"x": player.px + cos(cur) * tr, "y": player.py - 9 + sin(cur) * tr,
			"vx": cos(cur + sg * PI / 2) * 30, "vy": sin(cur + sg * PI / 2) * 30, "t": 0.0, "life": 0.25,
			"col": Color.WHITE if vis_rng.randf() < 0.5 else Color("#bfe6ff"), "s": 1})


## Inimigos (HTML: "// enemies" — só a IA 'walk' do goblin)
func _enemies(dt: float) -> void:
	var far_r := maxf(vw, vh) * 0.95
	for e in enemies:
		if e.dead:
			continue
		e.flash -= dt
		var dx: float = player.px - e.ex
		var dy: float = player.py - e.ey
		var dist := Vector2(dx, dy).length()
		if dist == 0: dist = 1.0
		var ux := dx / dist
		var uy := dy / dist
		e.face = ("left" if ux < 0 else "side") if absf(ux) > absf(uy) * 1.1 else ("up" if uy < 0 else "down")
		var sp: float = e.d.spd * (Bal.ELITE.spd if e.elite else 1.0)
		e.anim += dt * sp / 6.0
		e.ex += (ux * sp + e.kx) * dt
		e.ey += (uy * sp + e.ky) * dt
		var damp := maxf(0.0, 1.0 - dt * 9.0)
		e.kx *= damp
		e.ky *= damp
		# separação
		for o in query(e.ex, e.ey, e.d.r + 10):
			if o == e:
				continue
			var sx: float = e.ex - o.ex
			var sy: float = e.ey - o.ey
			var sd := Vector2(sx, sy).length()
			var mn: float = e.d.r + o.d.r
			if sd < mn and sd > 0:
				var push := (mn - sd) * 0.5
				e.ex += sx / sd * push
				e.ey += sy / sd * push
		if dist < e.d.r + 4:
			hurt(e.d.dmg)
		if dist > far_r:   # longe demais: reaparece do outro lado, mais perto
			e.ex = player.px + dx * 0.85
			e.ey = player.py + dy * 0.85
	var alive := []
	for e in enemies:
		if e.dead:
			e.queue_free()
		else:
			alive.append(e)
	enemies = alive


## Joias: ímã e coleta (HTML: "// gems")
func _gems(dt: float) -> void:
	var mag: float = Bal.MAGNET_BASE   # + W.magnet*16 (Amuleto Ímã, Etapa 2)
	var keep := []
	for g in gems:
		var dx: float = player.px - g.gx
		var dy: float = player.py - 8 - g.gy
		var d := Vector2(dx, dy).length()
		if d < mag:
			g.pull = true
		if g.pull:
			var s: float = Bal.GEM_PULL_SPD + (mag - minf(d, mag)) * 3
			var dd := d if d != 0 else 1.0
			g.gx += dx / dd * s * dt
			g.gy += dy / dd * s * dt
		if d < Bal.GEM_PICK_R:
			gems_total += g.v
			gain_xp(g.v)
			Sfx.play("gem")
			g.queue_free()
		else:
			keep.append(g)
	gems = keep


# ---------------------------------------------------------------- visual

## Atualiza nós, câmera (canto em pixel inteiro) e camadas de desenho. Não muda a simulação.
func sync_visuals() -> void:
	var sx := 0.0
	var sy := 0.0
	if shake > 0:
		sx = (vis_rng.randf() - 0.5) * 4
		sy = (vis_rng.randf() - 0.5) * 4
	cam = Vector2i(JsMath.jround(player.px - vw / 2.0 + sx), JsMath.jround(player.py - vh / 2.0 + sy))
	camera.position = Vector2(cam)
	player.update_visual()
	for e in enemies:
		e.update_visual()
	for g in gems:
		g.update_visual()
	ground.update_view(Rect2(cam.x, cam.y, vw, vh))
	ground.update_tree_alpha(player.px, player.py)
	shadows.queue_redraw()
	fx_layer.queue_redraw()
