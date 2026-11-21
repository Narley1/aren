extends Node
## Testes da Etapa 1, sem janela:
##   godot --headless --path . res://tests/run_tests.tscn      (ou tests/run_tests.sh, que também falha com
##                                                              qualquer ERROR/SCRIPT ERROR no log)
## Imprime PASS/FAIL por verificação e sai com código 1 se alguma falhar.

var fails := 0
var passes := 0
var main: Control
var game: Node2D


func check(name: String, ok: bool, info := "") -> void:
	if ok:
		passes += 1
		print("PASS  ", name, ("  (" + info + ")") if info != "" else "")
	else:
		fails += 1
		print("FAIL  ", name, ("  (" + info + ")") if info != "" else "")


func near(a: float, b: float, eps := 1e-6) -> bool:
	return absf(a - b) <= eps


func _ready() -> void:
	_run.call_deferred()


func _run() -> void:
	print("== Aren (Godot) — testes da Etapa 1 — Godot ", Engine.get_version_info().string)
	_test_load()
	if main == null:
		_finish()
		return
	await get_tree().process_frame
	await get_tree().process_frame
	main.set_process(false)   # os testes avançam a simulação na mão, com passos fixos
	_test_numbers()
	_test_ground()
	_test_movement()
	_test_spawn()
	_test_sword()
	_test_xp()
	_test_horde()
	await _test_streaming()
	await _test_pause()
	await _test_game_over()
	_finish()


func _finish() -> void:
	print("== %d PASS, %d FAIL" % [passes, fails])
	get_tree().quit(1 if fails > 0 else 0)


# ------------------------------------------------------------------

func _test_load() -> void:
	for p in ["res://scenes/main.tscn", "res://scenes/world.tscn", "res://scenes/player.tscn", "res://scenes/enemy.tscn",
			"res://scenes/gem.tscn", "res://scenes/hud.tscn"]:
		check("carrega " + p, load(p) != null)
	for a in ["Bal", "Art", "Sfx"]:
		check("autoload " + a, get_node_or_null("/root/" + a) != null)
	var ps: PackedScene = load("res://scenes/main.tscn")
	main = ps.instantiate() if ps else null
	if main:
		add_child(main)
		game = main.game
	check("cena principal instanciada", main != null and game != null and game.player != null)
	check("estado inicial = menu", main != null and main.state == "menu")
	check("todos os sprites do manifesto existem", _all_sprites_ok())


func _all_sprites_ok() -> bool:
	for k in Art.meta:
		var fr: Array = Art.frames(k)
		if fr.size() != int(Art.meta[k].n) or fr[0].get_width() != int(Art.meta[k].w):
			return false
	return true


func _test_numbers() -> void:
	var f := FileAccess.open("res://tests/ref/html_numbers.json", FileAccess.READ)
	var H: Dictionary = JSON.parse_string(f.get_as_text())
	var ok := true
	var bad := []
	for pair in [["hero", Bal.HERO], ["sword", Bal.SWORD], ["spawn", Bal.SPAWN], ["horde", Bal.HORDE], ["elite", Bal.ELITE]]:
		var h: Dictionary = H[pair[0]]
		for k in h:
			if not pair[1].has(k) or not near(float(pair[1][k]), float(h[k])):
				ok = false
				bad.append(pair[0] + "." + k)
	for k in ["base", "lin", "quad", "pickEvery"]:
		if not near(float(Bal.XP[k]), float(H.xp[k])): ok = false; bad.append("xp." + k)
	for k in ["hp", "spd", "dmg", "r", "sc", "gem"]:
		if not near(float(Bal.ET.goblin[k]), float(H.goblin[k])): ok = false; bad.append("goblin." + k)
	if not near(Bal.HP_SCALE_T, H.hpScaleT) or not near(Bal.HP_SCALE_Q, H.hpScaleQ): ok = false; bad.append("hpScale")
	check("Bal = números do HTML (BAL.hero/sword/spawn/horde/elite/xp, ET.goblin)", ok, ", ".join(bad))
	var xn := true
	for L in range(1, 31):
		if Bal.xp_need(L) != int(H.xpNeed[L - 1]): xn = false
	check("xpNeed(1..30) igual ao HTML", xn, "xpNeed(1..5) = %s" % [[Bal.xp_need(1), Bal.xp_need(2), Bal.xp_need(3), Bal.xp_need(4), Bal.xp_need(5)]])
	var pl := []
	for L in range(2, 31):
		if Bal.is_pick_level(L): pl.append(L)
	check("níveis de escolha iguais ao HTML", pl == H.pickLevels.map(func(x): return int(x)), str(pl))
	var gob: Dictionary = H.goblin
	check("tamanho do sprite do goblin igual ao HTML", Art.size("goblin_down") == Vector2i(int(gob.w), int(gob.h)))


func _test_ground() -> void:
	var st := Art.stamp_images()
	for p in [[0, 0], [-1, 0], [0, -1], [3, -2], [-5, 7]]:
		var img := GroundGen.make_chunk(p[0], p[1], st)
		var ref := Image.load_from_file(ProjectSettings.globalize_path("res://tests/ref/ground_%d_%d.png" % p))
		ref.convert(Image.FORMAT_RGBA8)
		var a := img.get_data()
		var b := ref.get_data()
		var diff := 0
		for k in range(0, a.size(), 4):
			if a[k] != b[k] or a[k + 1] != b[k + 1] or a[k + 2] != b[k + 2]:
				diff += 1
		check("bloco de chão %s idêntico ao HTML" % str(p), diff == 0, "%d px diferentes" % diff)


func _start() -> void:
	main.start()
	game.rng.seed = 12345
	main.set_process(false)
	# sem janela a vista teria o tamanho mínimo; usa a de um celular de 390x844 (SCALE 2 -> 195x422)
	game.vw = 195
	game.vh = 422


func _test_movement() -> void:
	_start()
	game.spawn_t = 1e9   # sem inimigos
	game.wave_t = 1e9
	var dt := 1.0 / 60
	Input.action_press("move_right")
	for i in 30:
		game.step(dt)
	Input.action_release("move_right")
	check("Aren anda para a direita com a tecla (D/seta)", near(game.player.px, Bal.HERO.speed * 0.5, 1e-6) and near(game.player.py, 0.0),
		"x = %.3f, esperado %.3f" % [game.player.px, Bal.HERO.speed * 0.5])
	check("animação lateral ao andar", game.player.dir == "side" and game.player.moving)
	var x0: float = game.player.px
	var y0: float = game.player.py
	Input.action_press("move_up")
	Input.action_press("move_left")
	for i in 60:
		game.step(dt)
	Input.action_release("move_up")
	Input.action_release("move_left")
	var dist := Vector2(game.player.px - x0, game.player.py - y0).length()
	check("diagonal normalizada (mesma velocidade)", near(dist, Bal.HERO.speed, 1e-4), "%.3f px em 1 s" % dist)
	game.step(dt)
	check("parado depois de soltar", not game.player.moving)
	# joystick de toque: arrastar 40 px para baixo = velocidade total
	game.joy = {"ox": 100.0, "oy": 100.0, "x": 100.0, "y": 140.0}
	var py0: float = game.player.py
	for i in 60:
		game.step(dt)
	game.joy = null
	check("joystick de toque move Aren", near(game.player.py - py0, Bal.HERO.speed, 1e-6) and game.player.dir == "down")
	# movimento por evento de toque de verdade (passa pelo _input da cena principal)
	var t := InputEventScreenTouch.new()
	t.index = 0
	t.pressed = true
	t.position = Vector2(200, 200)
	Input.parse_input_event(t)
	var d := InputEventScreenDrag.new()
	d.index = 0
	d.position = Vector2(160, 200)
	Input.parse_input_event(d)
	Input.flush_buffered_events()
	var ok_joy: bool = game.joy != null and near(game.joy.x - game.joy.ox, -40.0 / main.ui_scale)
	var px0: float = game.player.px
	game.step(0.5)
	var up := InputEventScreenTouch.new()
	up.index = 0
	up.pressed = false
	up.position = Vector2(160, 200)
	Input.parse_input_event(up)
	Input.flush_buffered_events()
	check("toque + arrasto viram joystick", ok_joy and game.player.px < px0 and game.joy == null)


func _test_spawn() -> void:
	_start()
	for i in 60 * 3:
		game.step(1.0 / 60)
	var n: int = game.enemies.size()
	check("goblins aparecem com o tempo", n >= 2, "%d goblins em 3 s (intervalo inicial %.2f s)" % [n, Bal.spawn_interval(0)])
	_start()
	var e: Node2D = game.spawn("goblin")
	var R := Vector2(game.vw, game.vh).length() / 2.0 + 18
	check("goblin nasce fora da tela, no anel de raio hypot(VW,VH)/2 + 18", near(Vector2(e.ex, e.ey).length(), R, 1e-6), "R = %.1f" % R)
	check("vida do goblin = ET.goblin.hp x hpScale", near(e.hp, 4.0))
	var d0 := Vector2(e.ex, e.ey).length()
	game.spawn_t = 1e9
	game.step(0.1)
	check("goblin persegue Aren a 28 px/s", near(d0 - Vector2(e.ex, e.ey).length(), 28 * 0.1, 0.01))


func _test_sword() -> void:
	_start()
	game.spawn_t = 1e9
	var sw := Bal.sword_stats(1)
	check("espada nível 1: dano 6,7, alcance 19,3, recarga 0,78 s", near(sw.dmg, 6.7, 1e-9) and near(sw.range, 19.3, 1e-9) and near(sw.cd, 0.78, 1e-9))
	var e: Node2D = game.spawn("goblin", 0.0, 14.0)
	e.hp = 100.0   # para ver o dano sem matar
	var far: Node2D = game.spawn("goblin", PI, 60.0)
	far.hp = 100.0
	e.d.spd = 0
	far.d.spd = 0
	var hits := 0
	var t := 0.0
	var dt := 1.0 / 60
	var last_hp: float = e.hp
	var first_swing := -1.0
	var max_kx := 0.0
	while t < 2.0:
		game.step(dt)
		t += dt
		max_kx = maxf(max_kx, e.kx)
		e.ex = 14.0   # o boneco de treino fica no lugar (o empurrão o tiraria do alcance)
		e.ey = 0.0
		e.kx = 0.0
		e.ky = 0.0
		if e.hp < last_hp:
			hits += 1
			if first_swing < 0: first_swing = t
			if hits == 1:
				check("golpe tira %.1f de vida" % sw.dmg, near(last_hp - e.hp, sw.dmg, 1e-9))
			last_hp = e.hp
	check("primeiro golpe em ~0,3 s (G.swCd inicial)", first_swing > 0.28 and first_swing < 0.34, "%.3f s" % first_swing)
	check("espada golpeia sozinha a cada 0,78 s", hits == 3, "%d golpes em 2 s" % hits)
	check("goblin fora do alcance não é atingido", near(far.hp, 100.0))
	check("golpe empurra o goblin (knockback 90 / sc²)", near(max_kx, 90.0 * 14.0 / Vector2(14.0, 9.0 - 20.0 / 3.0).length() * maxf(0.0, 1.0 - dt * 9.0), 1e-6), "kx = %.2f" % max_kx)
	check("clarão branco ao ser atingido", e.flash <= Bal.HIT_FLASH)
	# goblin comum morre de um golpe (4 de vida < 6,7) e solta 1 joia
	_start()
	game.spawn_t = 1e9
	var g2: Node2D = game.spawn("goblin", 0.0, 14.0)
	for i in 30:
		game.step(dt)
		if game.kills > 0:
			break
	check("goblin morre com a espada", g2 not in game.enemies and game.kills == 1)
	check("goblin solta uma joia de 1", game.gems.size() == 1 and game.gems[0].v == 1)


func _test_xp() -> void:
	_start()
	game.spawn_t = 1e9
	game.wave_t = 1e9
	var toasts := []
	var cb := func(a, b): toasts.append(a)
	game.toast.connect(cb)
	check("começa no nível 1 precisando de 8", game.lvl == 1 and game.need == 8)
	game.add_gem(game.player.px + 40, game.player.py - 8, 5)   # longe: fora do ímã (26 px)
	game.step(0.2)
	check("joia fora do ímã fica parada", game.gems.size() == 1 and not game.gems[0].pull)
	game.add_gem(game.player.px + 20, game.player.py - 8, 5)
	game.add_gem(game.player.px + 10, game.player.py - 8, 1)
	game.add_gem(game.player.px + 12, game.player.py - 8, 1)
	for i in 60:
		game.step(1.0 / 60)
	check("ímã puxa e recolhe as joias perto (5+1+1 = 7 de experiência)", game.xp == 7 and game.gems_total == 7 and game.lvl == 1)
	game.player.px += 40   # vai até a joia de 5
	for i in 30:
		game.step(1.0 / 60)
	check("nível 2 exatamente ao passar de 8 (sobra 4)", game.lvl == 2 and game.xp == 4 and game.need == 13, "lvl %d xp %d need %d" % [game.lvl, game.xp, game.need])
	check("nível 2 é de escolha: escolha pendente e aviso 'Nível 2!'", game.pending == 1 and toasts.has("Nível 2!"))
	game.gain_xp(9)    # 4 + 9 = 13 -> nível 3 (escolha)
	game.player.hp = 5
	game.gain_xp(18)   # xpNeed(3) = 18 -> nível 4 (não é de escolha: cura meio coração)
	check("nível 4 cura meio coração e avisa", game.lvl == 4 and game.player.hp == 6 and toasts.has("Nível 4"))
	game.toast.disconnect(cb)


func _test_horde() -> void:
	_start()
	game.spawn_t = 1e9
	game.player.inv = 1e9
	var toasts := []
	var cb := func(a, b): toasts.append(a)
	game.toast.connect(cb)
	while game.t < 49.9:
		game.step(0.1)
		game.spawn_t = 1e9
	var n0: int = game.enemies.size()
	game.step(0.2)
	game.toast.disconnect(cb)
	var expect: int = mini(Bal.HORDE.countMax, Bal.HORDE.count + floori(50.0 / Bal.HORDE.countPerT))   # 16 + 2 = 18
	check("horda aos 50 s: min(60, 16 + floor(t/18)) = %d goblins" % expect, game.enemies.size() - n0 == expect and toasts.has("Uma horda cerca você!"), "+%d" % (game.enemies.size() - n0))


func _test_streaming() -> void:
	_start()
	game.spawn_t = 1e9
	game.wave_t = 1e9
	game.force_input = Vector2(1, 0)
	var t0 := Time.get_ticks_msec()
	for i in 60 * 8:   # 8 s andando para a direita (~570 px, mais de 4 blocos novos)
		game.step(1.0 / 60)
		if i % 6 == 0:
			game.sync_visuals()
			await get_tree().process_frame
	game.force_input = Vector2.ZERO
	var ok := false
	var t1 := Time.get_ticks_msec()
	while Time.get_ticks_msec() - t1 < 5000:      # até 5 s para as threads terminarem
		game.sync_visuals()
		await get_tree().process_frame
		var k: int = game.ground.key_of(floori((game.cam.x + game.vw / 2.0) / 128.0), floori((game.cam.y + game.vh / 2.0) / 128.0))
		if game.ground._tex.has(k):
			ok = true
			break
	check("chão novo é gerado (em threads) enquanto Aren anda", ok, "x = %.0f, %d blocos prontos, %d ms" % [game.player.px, game.ground.ready_count(), Time.get_ticks_msec() - t0])
	check("props aparecem na área nova", game.ground.visible_props.size() > 0, "%d props visíveis" % game.ground.visible_props.size())


func _test_pause() -> void:
	_start()
	main.set_process(true)
	await get_tree().process_frame
	await get_tree().process_frame
	var ev := InputEventKey.new()
	ev.keycode = KEY_P
	ev.pressed = true
	Input.parse_input_event(ev)
	Input.flush_buffered_events()
	await get_tree().process_frame
	var t0: float = game.t
	for i in 5:
		await get_tree().process_frame
	check("P pausa o jogo (relógio parado, painel visível)", main.state == "pause" and near(game.t, t0) and main.hud.pause_overlay.visible)
	var ev2 := InputEventKey.new()
	ev2.keycode = KEY_ESCAPE
	ev2.pressed = true
	Input.parse_input_event(ev2)
	Input.flush_buffered_events()
	for i in 3:
		await get_tree().process_frame
	check("Esc volta ao jogo", main.state == "play" and game.t > t0 and not main.hud.pause_overlay.visible)
	main.set_process(false)


func _test_game_over() -> void:
	_start()
	main.set_process(true)
	game.spawn_t = 1e9
	var died := [false]
	game.died.connect(func(): died[0] = true, CONNECT_ONE_SHOT)
	for i in 9:
		game.player.inv = 0
		game.hurt(1)
	check("com meio coração ainda está vivo", game.player.hp == 1 and main.state == "play")
	game.player.inv = 0.5
	game.hurt(1)
	check("invulnerável depois de um golpe não leva dano", game.player.hp == 1)
	game.player.inv = 0
	game.hurt(1)
	check("0 corações = fim de jogo", died[0] and game.player.hp == 0 and main.state == "over")
	await get_tree().create_timer(0.7).timeout
	check("painel 'Aren caiu' com 'Tentar de novo' depois de 500 ms", main.hud.over_overlay.visible and main.hud.btn_again.text == "Tentar de novo")
	main.hud.btn_again.pressed.emit()
	await get_tree().process_frame
	check("Tentar de novo começa outra partida", main.state == "play" and game.player.hp == 10 and game.t < 0.5 and not main.hud.over_overlay.visible)
	main.set_process(false)
