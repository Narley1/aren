extends Node
## Medição de desempenho numa cena cheia: muitos goblins em volta de Aren (invulnerável), a espada
## golpeando, e alguns goblins mortos por quadro (números de dano, partículas, joias). Mede o tempo de cada
## quadro de verdade (processo + desenho), com o V-Sync desligado. Uso (precisa de janela; no Linux, xvfb):
##   xvfb-run -a godot --path . --rendering-driver opengl3 --audio-driver Dummy --resolution 1366x768 \
##     res://tools/bench.tscn -- --goblins=150 --frames=600

var goblins := 150
var frames := 600
var kills_per_frame := 2


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--goblins="): goblins = int(a.substr(10))
		elif a.begins_with("--frames="): frames = int(a.substr(9))
		elif a.begins_with("--kills="): kills_per_frame = int(a.substr(8))
	_run.call_deferred()


func _run() -> void:
	DisplayServer.window_set_vsync_mode(DisplayServer.VSYNC_DISABLED)
	Engine.max_fps = 0
	var main: Control = load("res://scenes/main.tscn").instantiate()
	add_child(main)
	await get_tree().process_frame
	var game: Node2D = main.game
	main.start()
	game.rng.seed = 1
	game.spawn_t = 1e9
	game.wave_t = 1e9
	# aquece: chão em volta pronto
	for i in 60:
		game.player.inv = 1e9
		await get_tree().process_frame
	var times := PackedFloat64Array()
	var last := Time.get_ticks_usec()
	for f in frames + 60:
		game.player.inv = 1e9
		game.force_input = Vector2(cos(f / 90.0), sin(f / 70.0))   # anda em curvas (chão novo)
		var live := 0
		for e in game.enemies:
			if not e.dead: live += 1
		while live < goblins:
			game.spawn("goblin", game.rng.randf() * TAU, 30.0 + game.rng.randf() * 120.0)
			live += 1
		for k in kills_per_frame:
			if game.enemies.size() > 0:
				var e = game.enemies[game.rng.randi() % game.enemies.size()]
				if not e.dead:
					game.hit(e, 999.0)
		await get_tree().process_frame
		var now := Time.get_ticks_usec()
		if f >= 60:   # descarta os primeiros quadros
			times.append((now - last) / 1000.0)
		last = now
	var s := times.duplicate()
	s.sort()
	var sum := 0.0
	for v in times: sum += v
	var win := get_viewport().get_visible_rect().size
	print("BENCH %dx%d goblins=%d kills/quadro=%d quadros=%d: média %.2f ms (%.0f fps), mediana %.2f ms, p95 %.2f ms, nós %d, draw calls %d" % [
		int(win.x), int(win.y), goblins, kills_per_frame, frames, sum / times.size(), 1000.0 / (sum / times.size()),
		s[s.size() / 2], s[int(s.size() * 0.95)], Performance.get_monitor(Performance.OBJECT_NODE_COUNT),
		Performance.get_monitor(Performance.RENDER_TOTAL_DRAW_CALLS_IN_FRAME)])
	get_tree().quit()
