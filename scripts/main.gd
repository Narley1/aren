extends Control
## Cena principal: estados (menu, play, pause, over — como `state` no HTML), escala inteira da vista,
## entrada (teclado, toque/joystick) e o modo de capturas de tela (`-- --shots=PASTA`).
##
## Escala (igual ao resize() do HTML): SCALE = max(2, round(sqrt(largura*altura/60000))); a vista lógica tem
## VW = ceil(largura/SCALE) x VH = ceil(altura/SCALE) pixels e é desenhada numa SubViewport desse tamanho,
## ampliada SCALE vezes com filtro "nearest" — pixel perfeito. O HUD fica por cima em px de tela, como o DOM.

@onready var screen: TextureRect = $Screen
@onready var view: SubViewport = $View
@onready var game: Node2D = $View/World
@onready var joy_draw: Node2D = $View/JoyLayer/Joy
@onready var hud: CanvasLayer = $HUD

var state := "menu"
var scale_px := 2           # SCALE
var ui_scale := 1           # px de tela por px de interface (devicePixelRatio)
var best := 0.0
var _over_timer := -1.0
var _joy_id := -1
var _shots_dir := ""
var _no_autopause := false

const RECORD_FILE := "user://recorde.cfg"


static func ensure_actions() -> void:
	var map := {
		"move_left": [KEY_A, KEY_LEFT], "move_right": [KEY_D, KEY_RIGHT],
		"move_up": [KEY_W, KEY_UP], "move_down": [KEY_S, KEY_DOWN],
	}
	for a in map:
		if InputMap.has_action(a):
			continue
		InputMap.add_action(a)
		for i in map[a].size():
			var ev := InputEventKey.new()
			if i == 0:
				ev.physical_keycode = map[a][i]   # WASD pela posição (AZERTY: ZQSD), como CODE_KEYS no HTML
			else:
				ev.keycode = map[a][i]
			InputMap.action_add_event(a, ev)


func _ready() -> void:
	ensure_actions()
	for a in OS.get_cmdline_user_args():
		if a.begins_with("--shots="):
			_shots_dir = a.substr(8)
			_no_autopause = true
	if OS.get_name() in ["Android", "iOS"]:
		ui_scale = maxi(1, roundi(DisplayServer.screen_get_dpi() / 160.0))
	hud.ui_scale = ui_scale
	screen.texture = view.get_texture()
	get_viewport().size_changed.connect(_resize)
	_load_best()
	hud.start_pressed.connect(start)
	hud.pause_pressed.connect(toggle_pause)
	hud.resume_pressed.connect(toggle_pause)
	hud.restart_pressed.connect(start)
	hud.again_pressed.connect(start)
	hud.menu_pressed.connect(go_title)
	game.toast.connect(hud.toast)
	game.died.connect(game_over)
	_resize()
	go_title()
	if _shots_dir != "":
		_run_shots.call_deferred()


func _resize() -> void:
	var win := get_viewport().get_visible_rect().size
	scale_px = maxi(2, roundi(sqrt((win.x * win.y) / 60000.0)))
	var vw := ceili(win.x / scale_px)
	var vh := ceili(win.y / scale_px)
	view.size = Vector2i(vw, vh)
	game.vw = vw
	game.vh = vh
	screen.size = Vector2(vw * scale_px, vh * scale_px)
	# a sobra (menos de SCALE px) é cortada igualmente dos dois lados
	screen.position = -((screen.size - win) / 2).floor()
	game.sync_visuals()
	hud.layout()


func _process(delta: float) -> void:
	var dt := minf(delta, 0.05)   # como o frame() do HTML
	if state == "play":
		game.step(dt)
	if state == "play" or state == "menu":
		game.sync_visuals()
		hud.update_from(game)
	if _over_timer >= 0:
		_over_timer -= delta
		if _over_timer < 0:
			_show_over()
	joy_draw.queue_redraw()


# ------------------------------------------------------------------ fluxo (HTML: "flow")

func start() -> void:
	_over_timer = -1.0
	game.reset()
	state = "play"
	hud.show_state(state)
	hud.toast("Sobreviva, Aren!", "A espada ataca sozinha quando há inimigos perto")
	Sfx.play("start")


func toggle_pause() -> void:
	if state == "play":
		state = "pause"
		game.joy = null
		_joy_id = -1
		hud.pause_info.text = "%s sobrevividos · %d abates" % [hud.fmt(game.t), game.kills]
		hud.show_state(state)
		Sfx.play("pauseCue", true)
	elif state == "pause":
		state = "play"
		hud.show_state(state)
		Sfx.play("pauseCue", false)


func game_over() -> void:
	state = "over"
	game.joy = null
	_joy_id = -1
	Sfx.play("lose")
	hud.show_state(state)
	_over_timer = 0.5   # o painel aparece depois de 500 ms


func _show_over() -> void:
	var nb: bool = game.t > best
	var prev := best
	if nb:
		best = game.t
		_save_best()
	hud.show_over(game.t, game.kills, game.gems_total, game.ups,
		"Novo recorde de tempo!" if nb else "Recorde: %s" % hud.fmt(prev))


func go_title() -> void:
	state = "menu"
	_over_timer = -1.0
	game.reset()
	hud.title_best.text = ("Recorde: %s" % hud.fmt(best)) if best > 0 else ""
	hud.show_state(state)


func _load_best() -> void:
	var c := ConfigFile.new()
	if c.load(RECORD_FILE) == OK:
		best = float(c.get_value("recorde", "tempo", 0.0))


func _save_best() -> void:
	if _shots_dir != "":
		return
	var c := ConfigFile.new()
	c.set_value("recorde", "tempo", best)
	c.save(RECORD_FILE)


# ------------------------------------------------------------------ entrada (HTML: "input")

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT and state == "play" and not _no_autopause:
		toggle_pause()   # perder o foco pausa, como o blur/visibilitychange do HTML


func _unhandled_input(ev: InputEvent) -> void:
	if ev is InputEventKey and ev.pressed and not ev.echo:
		var k: int = ev.keycode
		if (k == KEY_P or k == KEY_ESCAPE) and (state == "play" or state == "pause"):
			toggle_pause()
			get_viewport().set_input_as_handled()
		elif (k == KEY_ENTER or k == KEY_KP_ENTER or k == KEY_SPACE) and state == "menu":
			start()
			get_viewport().set_input_as_handled()


func _over_button(p: Vector2) -> bool:
	for b in [hud.btn_music, hud.btn_sound, hud.btn_pause]:
		if b.is_visible_in_tree() and b.get_global_rect().has_point(p / ui_scale):
			return true
	return false


## Joystick de toque: o primeiro dedo que encosta (fora dos botões) vira a origem; arrastar dá a direção.
## Com o mouse funciona igual (emulate_touch_from_mouse), como os pointer events do HTML.
func _input(ev: InputEvent) -> void:
	if ev is InputEventScreenTouch:
		if ev.pressed and state == "play" and _joy_id < 0 and not _over_button(ev.position):
			_joy_id = ev.index
			var p: Vector2 = ev.position / ui_scale
			game.joy = {"ox": p.x, "oy": p.y, "x": p.x, "y": p.y}
		elif not ev.pressed and ev.index == _joy_id:
			_joy_id = -1
			game.joy = null
	elif ev is InputEventScreenDrag and ev.index == _joy_id and game.joy != null:
		var p: Vector2 = ev.position / ui_scale
		game.joy.x = p.x
		game.joy.y = p.y


## Desenho do joystick em pixels lógicos (render() do HTML, "// joystick")
func joy_geometry() -> Dictionary:
	if game.joy == null:
		return {}
	var j: Dictionary = game.joy
	var s := float(scale_px)
	var b := (Vector2(j.ox, j.oy) * ui_scale - screen.position) / s
	var d := Vector2(j.x - j.ox, j.y - j.oy) * ui_scale / s
	var mx := 40.0 * ui_scale / s
	if d.length() > mx:
		d = d / d.length() * mx
	return {"base": b, "knob": b + d, "r": JsMath.jround(mx + 3), "kr": JsMath.jround(mx * 0.45)}


# ------------------------------------------------------------------ capturas (xvfb)

func _snap(name: String) -> void:
	await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	var win := get_viewport().get_visible_rect().size
	var path := "%s/godot_%s_%dx%d.png" % [_shots_dir, name, int(win.x), int(win.y)]
	img.save_png(path)
	print("captura: ", path)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().process_frame


func _run_shots() -> void:
	DirAccess.make_dir_recursive_absolute(_shots_dir)
	game.ground.pregen(Rect2(game.cam.x - 130, game.cam.y - 130, game.vw + 260, game.vh + 260))
	await _frames(4)
	await _snap("start")
	# partida semeada, Aren parado e invulnerável por 25 s (o mesmo roteiro da captura do HTML)
	start()
	game.rng.seed = 7
	game.player.inv = 1e9
	for i in 60 * 25:
		game.step(1.0 / 60)
	# (Aren continua invulnerável até a captura: senão pode sair no meio de uma piscada)
	# espera um golpe da espada no meio para a captura
	for i in 120:
		if game.swing != null and game.swing.t / game.swing.dur > 0.45:
			break
		game.step(1.0 / 60)
	game.sync_visuals()
	hud.update_from(game)
	set_process(false)
	await _frames(3)
	await _snap("play")
	set_process(true)
	toggle_pause()
	await _frames(3)
	await _snap("pause")
	toggle_pause()
	game.player.inv = 0.0
	game.hurt(999)
	await get_tree().create_timer(0.8).timeout
	await _snap("over")
	get_tree().quit()
