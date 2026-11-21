extends CanvasLayer
## HUD e painéis (porte do HTML/CSS do jogo: #hud, #toast, #pauseScreen, #overScreen e uma tela inicial
## simples). Tudo em "px de interface" (= CSS px do HTML); a camada é ampliada por `ui_scale` inteiro
## em telas de alta densidade. Cores e tamanhos tirados dos tokens :root e das regras CSS do HTML.

signal start_pressed
signal pause_pressed
signal resume_pressed
signal restart_pressed
signal again_pressed
signal menu_pressed

const BG := Color("#13202a")
const PANEL := Color("#1b3a4c")
const PANEL_HI := Color("#245069")
const GOLD := Color("#f2c14e")
const GOLD_DK := Color("#a8781c")
const LEAF := Color("#8ad65a")
const INK := Color("#f6f1e3")
const MUTE := Color("#a9c6d2")
const SHADOW := Color("#0b1218")

var ui_scale := 1
var root: Control
var hud_box: Control
var lvl_label: Label
var next_label: Label
var xp_track: Control
var hearts_box: Control
var timer_label: Label
var kills_label: Label
var gems_label: Label
var gem_icon: TextureRect
var btn_music: Button
var btn_sound: Button
var btn_pause: Button
var toast_box: PanelContainer
var toast_t1: Label
var toast_t2: Label
var title_box: Control
var title_logo: TextureRect
var title_press: Label
var title_hint: Label
var title_best: Label
var pause_overlay: Control
var pause_panel: Control
var pause_info: Label
var over_overlay: Control
var over_panel: Control
var over_vals: Dictionary = {}
var over_best: Label
var btn_resume: Button
var btn_again: Button

var xp_frac := 0.0
var xp_pick := false
var _hearts_key := ""
var _toast_t := -1.0


func _ready() -> void:
	layer = 10
	root = Control.new()
	root.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(root)
	_build_hud()
	_build_toast()
	_build_title()
	_build_pause()
	_build_over()
	get_viewport().size_changed.connect(layout)
	layout()


# ------------------------------------------------------------------ fábricas

func lbl(text: String, size: int, col: Color, weight := 400, shadow_px := 2, spacing := 0) -> Label:
	var l := Label.new()
	l.text = text
	var f: Font = Art.font
	if weight >= 700 or spacing > 0:
		var fv := FontVariation.new()
		fv.base_font = Art.font
		fv.variation_opentype = {"wght": weight}
		fv.spacing_glyph = spacing
		f = fv
	elif weight >= 600:
		f = Art.font_semi
	l.add_theme_font_override("font", f)
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", col)
	if shadow_px > 0:
		l.add_theme_color_override("font_shadow_color", SHADOW)
		l.add_theme_constant_override("shadow_offset_x", shadow_px)
		l.add_theme_constant_override("shadow_offset_y", shadow_px)
		l.add_theme_constant_override("shadow_outline_size", 0)
	l.mouse_filter = Control.MOUSE_FILTER_IGNORE
	return l


## Botões: "gold" (.btn), "alt" (.btn.alt) e "hud" (#pauseBtn etc.)
func btn(text: String, kind: String) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_ALL
	var normal: PixelBox
	var fcol := INK
	var size := 18
	var font: Font = Art.font_bold
	match kind:
		"gold":
			normal = PixelBox.make({"bg": GOLD, "inset": 3, "inset_color": GOLD_DK, "inset_br_only": true,
				"shadow": Vector2(3, 3), "shadow_color": SHADOW, "pad": [11, 14, 11, 14]})
			fcol = Color("#1a1206")
		"alt":
			normal = PixelBox.make({"bg": PANEL_HI, "inset": 3, "inset_color": Color("#173546"), "inset_br_only": true,
				"shadow": Vector2(3, 3), "shadow_color": SHADOW, "pad": [11, 14, 11, 14]})
		_:
			normal = PixelBox.make({"bg": PANEL, "border": 2, "border_color": GOLD, "shadow": Vector2(2, 2),
				"shadow_color": SHADOW, "pad": [4, 10, 4, 10]})
			size = 13
			font = Art.font_semi
	var hover: PixelBox = normal.duplicate()
	if kind == "gold":
		hover.bg = Color("#ffd46a")
	else:
		hover.bg = Color("#2c5d79") if kind == "alt" else PANEL_HI
	var focus := PixelBox.make({"ring": 3, "ring_color": LEAF, "ring_gap": 2})
	b.add_theme_stylebox_override("normal", normal)
	b.add_theme_stylebox_override("hover", hover)
	b.add_theme_stylebox_override("pressed", hover)
	b.add_theme_stylebox_override("hover_pressed", hover)
	b.add_theme_stylebox_override("focus", focus)
	b.add_theme_font_override("font", font)
	b.add_theme_font_size_override("font_size", size)
	for k in ["font_color", "font_hover_color", "font_pressed_color", "font_focus_color", "font_hover_pressed_color"]:
		b.add_theme_color_override(k, fcol)
	b.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART if kind != "hud" else TextServer.AUTOWRAP_OFF
	return b


func make_panel() -> PanelContainer:
	var p := PanelContainer.new()
	p.add_theme_stylebox_override("panel", PixelBox.make({"bg": PANEL, "border": 4, "border_color": GOLD,
		"inset": 3, "inset_color": GOLD_DK, "ring": 4, "ring_color": SHADOW, "shadow": Vector2(8, 8),
		"shadow_spread": 4, "shadow_color": Color(0, 0, 0, 0.35), "pad": [26, 24, 26, 24]}))
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 14)
	p.add_child(v)
	return p


func make_overlay() -> Control:
	var o := ColorRect.new()
	o.color = Color(9 / 255.0, 16 / 255.0, 22 / 255.0, 0.62)
	o.visible = false
	o.mouse_filter = Control.MOUSE_FILTER_STOP
	root.add_child(o)
	return o


# ------------------------------------------------------------------ construção

func _build_hud() -> void:
	hud_box = Control.new()
	hud_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	hud_box.visible = false
	root.add_child(hud_box)
	lvl_label = lbl("Nv 1", 14, GOLD, 700)
	next_label = lbl("poder no 2", 12, MUTE)
	xp_track = Control.new()
	xp_track.mouse_filter = Control.MOUSE_FILTER_IGNORE
	xp_track.draw.connect(_draw_xp)
	hearts_box = Control.new()
	hearts_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	timer_label = lbl("0:00", 22, INK, 700)
	timer_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	kills_label = lbl("0 abates", 14, INK)
	gems_label = lbl("0", 14, INK)
	gem_icon = TextureRect.new()
	gem_icon.texture = Art.tex("gem_g")
	gem_icon.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	gem_icon.stretch_mode = TextureRect.STRETCH_SCALE
	gem_icon.size = Vector2(10, 12)
	btn_music = btn("Música", "hud")
	btn_sound = btn("Efeitos", "hud")
	btn_pause = btn("Pausa", "hud")
	btn_music.pressed.connect(func():
		Sfx.music = not Sfx.music
		btn_music.modulate.a = 1.0 if Sfx.music else 0.55
		btn_music.release_focus())
	btn_sound.pressed.connect(func():
		Sfx.enabled = not Sfx.enabled
		btn_sound.modulate.a = 1.0 if Sfx.enabled else 0.55
		btn_sound.release_focus())
	btn_pause.pressed.connect(func():
		btn_pause.release_focus()
		pause_pressed.emit())
	for c in [lvl_label, next_label, xp_track, hearts_box, timer_label, kills_label, gems_label, gem_icon, btn_music, btn_sound, btn_pause]:
		hud_box.add_child(c)


func _build_toast() -> void:
	# #toast: caixa rgba(19,32,42,.88), borda 2px dourada, padding 8/14, largura máx. min(90vw, 340px)
	toast_box = PanelContainer.new()
	toast_box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	toast_box.modulate.a = 0.0
	toast_box.add_theme_stylebox_override("panel", PixelBox.make({"bg": Color(19 / 255.0, 32 / 255.0, 42 / 255.0, 0.88),
		"border": 2, "border_color": GOLD, "pad": [10, 16, 10, 16]}))
	root.add_child(toast_box)
	var v := VBoxContainer.new()
	v.add_theme_constant_override("separation", 2)
	toast_box.add_child(v)
	toast_t1 = lbl("", 17, GOLD, 700, 0)
	toast_t2 = lbl("", 13, MUTE, 400, 0)
	for l in [toast_t1, toast_t2]:
		l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		v.add_child(l)


func _build_title() -> void:
	title_box = ColorRect.new()
	title_box.color = Color(9 / 255.0, 16 / 255.0, 22 / 255.0, 0.35)
	title_box.mouse_filter = Control.MOUSE_FILTER_STOP
	title_box.gui_input.connect(func(ev):
		if (ev is InputEventMouseButton and ev.pressed) or (ev is InputEventScreenTouch and ev.pressed):
			start_pressed.emit())
	root.add_child(title_box)
	title_logo = TextureRect.new()
	title_logo.texture = Art.tex("logo")
	title_logo.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
	title_logo.stretch_mode = TextureRect.STRETCH_SCALE
	title_logo.mouse_filter = Control.MOUSE_FILTER_IGNORE
	var touch := OS.has_feature("mobile") or OS.has_feature("web_android") or OS.has_feature("web_ios")
	title_press = lbl("Toque para começar" if touch else "Pressione Enter para começar", 24, Color("#fff6d6"), 700, 2, 1)
	title_press.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_hint = lbl("WASD ou setas para andar · no celular, toque e arraste em qualquer lugar · a espada ataca sozinha · P pausa", 13, INK, 400, 2)
	title_hint.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title_hint.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	title_best = lbl("", 13, LEAF, 400, 2)
	title_best.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	for c in [title_logo, title_press, title_hint, title_best]:
		title_box.add_child(c)


func _build_pause() -> void:
	pause_overlay = make_overlay()
	pause_panel = make_panel()
	pause_overlay.add_child(pause_panel)
	var v: VBoxContainer = pause_panel.get_child(0)
	v.add_child(lbl("Pausado", 26, GOLD, 700, 3))
	pause_info = lbl("", 15, INK, 400, 0)
	v.add_child(pause_info)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	btn_resume = btn("Continuar", "gold")
	var b2 := btn("Recomeçar", "alt")
	btn_resume.pressed.connect(func(): resume_pressed.emit())
	b2.pressed.connect(func(): restart_pressed.emit())
	for b in [btn_resume, b2]:
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.custom_minimum_size.x = 130
		row.add_child(b)
	v.add_child(row)


func _build_over() -> void:
	over_overlay = make_overlay()
	over_panel = make_panel()
	over_overlay.add_child(over_panel)
	var v: VBoxContainer = over_panel.get_child(0)
	v.add_child(lbl("Aren caiu", 26, GOLD, 700, 3))
	var grid := GridContainer.new()
	grid.columns = 2
	grid.add_theme_constant_override("h_separation", 8)
	grid.add_theme_constant_override("v_separation", 8)
	for k in ["Tempo", "Abates", "Joias", "Poderes"]:
		var box := PanelContainer.new()
		box.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		box.add_theme_stylebox_override("panel", PixelBox.make({"bg": Color("#152f3e"), "border": 2, "border_color": PANEL_HI, "pad": [10, 10, 10, 10]}))
		var bv := VBoxContainer.new()
		bv.add_theme_constant_override("separation", 0)
		bv.add_child(lbl(k.to_upper(), 11, MUTE, 400, 0, 2))
		var val := lbl("0", 22, INK, 700, 0)
		bv.add_child(val)
		over_vals[k] = val
		box.add_child(bv)
		grid.add_child(box)
	v.add_child(grid)
	over_best = lbl("", 13, LEAF, 400, 0)
	v.add_child(over_best)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 10)
	btn_again = btn("Tentar de novo", "gold")
	var b2 := btn("Tela inicial", "alt")
	btn_again.pressed.connect(func(): again_pressed.emit())
	b2.pressed.connect(func(): menu_pressed.emit())
	for b in [btn_again, b2]:
		b.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		b.custom_minimum_size.x = 130
		row.add_child(b)
	v.add_child(row)


# ------------------------------------------------------------------ disposição

func _w(c: Control) -> float:
	return c.get_combined_minimum_size().x


func layout() -> void:
	var win := get_viewport().get_visible_rect().size
	scale = Vector2(ui_scale, ui_scale)
	var W := floorf(win.x / ui_scale)
	var H := floorf(win.y / ui_scale)
	root.position = Vector2.ZERO
	root.size = Vector2(W, H)
	hud_box.size = root.size
	var narrow := W <= 420
	# linha 1: nível, barra de experiência, próximo poder
	var y := 10.0
	lvl_label.position = Vector2(16, y)
	var row_h := lvl_label.get_combined_minimum_size().y
	next_label.size = Vector2.ZERO
	next_label.position = Vector2(W - 16 - _w(next_label), y + (row_h - next_label.get_combined_minimum_size().y) / 2)
	xp_track.position = Vector2(16 + 46 + 8, y + floorf((row_h - 13) / 2))
	xp_track.size = Vector2(next_label.position.x - 8 - xp_track.position.x, 13)
	# linha 2: corações | relógio | botões e contadores
	y += row_h + 7
	hearts_box.position = Vector2(16, y)
	var tw := 76.0 if narrow else 124.0
	timer_label.add_theme_font_size_override("font_size", 19 if narrow else 22)
	timer_label.size = Vector2(tw, 0)
	timer_label.position = Vector2(floorf((W - tw) / 2), y)
	var col_w := floorf((W - 32 - tw - 16) / 2)
	var right := W - 16
	# .btns: flex-wrap com justify-content:flex-end — linhas na ordem do DOM, cada uma alinhada à direita
	var lines := [[]]
	var lw := 0.0
	for b in [btn_music, btn_sound, btn_pause]:
		var s: Vector2 = b.get_combined_minimum_size()
		b.size = s
		# (-4: o Chromium desenha a Pixelify um pouco mais larga; assim a quebra sai igual à do HTML no celular)
		if not lines[-1].is_empty() and lw + 5 + s.x > col_w - 4:
			lines.append([])
			lw = 0.0
		lw += (5 if not lines[-1].is_empty() else 0) + s.x
		lines[-1].append(b)
	var by := y
	var bh := 0.0
	for line in lines:
		var bx := right
		for i in range(line.size() - 1, -1, -1):
			var b: Button = line[i]
			b.position = Vector2(bx - b.size.x, by)
			bx -= b.size.x + 5
			bh = b.size.y
		by += bh + 5
	by -= 5
	by += bh + 6
	kills_label.size = Vector2.ZERO
	kills_label.position = Vector2(right - _w(kills_label), by)
	by += kills_label.get_combined_minimum_size().y + 6
	gems_label.size = Vector2.ZERO
	var gh := gems_label.get_combined_minimum_size().y
	gems_label.position = Vector2(right - _w(gems_label), by)
	gem_icon.position = Vector2(gems_label.position.x - 6 - 10, by + floorf((gh - 12) / 2))
	_layout_hearts()
	# aviso: centro, a 60% da altura; o texto quebra acima da largura máxima
	# (no HTML a caixa está em left:50%, então o "shrink-to-fit" também a limita à metade da tela)
	var maxw := minf(minf(floorf(W * 0.9), 340.0), floorf(W / 2) - 32)
	var natural := 0.0
	for l in [toast_t1, toast_t2]:
		l.autowrap_mode = TextServer.AUTOWRAP_OFF
		l.custom_minimum_size = Vector2.ZERO
		natural = maxf(natural, _w(l))
	var tw2 := minf(natural, maxw)
	for l in [toast_t1, toast_t2]:
		l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
		l.custom_minimum_size = Vector2(tw2, 0)
	toast_box.reset_size()
	toast_box.position = Vector2(floorf((W - toast_box.size.x) / 2), floorf(H * 0.6))
	# tela inicial
	title_box.size = root.size
	var k := clampi(floori(W * 0.9 / 168.0), 1, 3)
	if H < 900: k = mini(k, 2)
	title_logo.size = Vector2(168 * k, 82 * k)
	title_logo.position = Vector2(floorf((W - 168 * k) / 2), floorf(H * 0.07))
	title_press.add_theme_font_size_override("font_size", clampi(roundi(W * 0.046), 18, 24))
	title_press.size = Vector2(W - 32, 0)
	# abaixo de Aren (que fica no centro da vista), acima das dicas
	title_press.position = Vector2(16, floorf(H * 0.62))
	title_hint.size = Vector2(minf(W - 32, 560), 0)
	title_hint.position = Vector2(floorf((W - title_hint.size.x) / 2), H - 16 - 70)
	title_best.size = Vector2(W - 32, 0)
	title_best.position = Vector2(16, title_press.position.y + title_press.get_combined_minimum_size().y + 12)
	# painéis
	for pair in [[pause_overlay, pause_panel], [over_overlay, over_panel]]:
		var o: Control = pair[0]
		var p: Control = pair[1]
		o.size = root.size
		var pw := minf(W - 32, 440)
		p.size = Vector2(pw, 0)
		p.custom_minimum_size = Vector2(pw, 0)
		p.reset_size()
		p.size.x = pw
		p.position = Vector2(floorf((W - pw) / 2), floorf((H - p.get_combined_minimum_size().y) / 2))


func _layout_hearts() -> void:
	var i := 0
	for c in hearts_box.get_children():
		# 21x18 cada (3x o sprite 7x6), 2 px entre eles, quebra em 150 px
		var per_row := floori((150 + 2) / 23.0)
		c.position = Vector2((i % per_row) * 23, (i / per_row) * 20)
		c.size = Vector2(21, 18)
		i += 1


func _draw_xp() -> void:
	var r := Rect2(Vector2.ZERO, xp_track.size)
	xp_track.draw_rect(r, SHADOW)                                   # borda 2px #0b1218
	var inner := r.grow(-2)
	xp_track.draw_rect(inner, Color("#0f2532"))
	xp_track.draw_rect(inner, PANEL_HI, false, 1.0)                 # inset 1px
	var fw := floorf(inner.size.x * clampf(xp_frac, 0, 1))
	if fw > 0:
		var top := GOLD if xp_pick else Color("#7fd8ff")
		var bot := GOLD_DK if xp_pick else Color("#3f86dc")
		xp_track.draw_rect(Rect2(inner.position, Vector2(fw, inner.size.y)), top)
		xp_track.draw_rect(Rect2(inner.position.x, inner.end.y - 3, fw, 3), bot)


# ------------------------------------------------------------------ atualização

static func fmt(t: float) -> String:
	return "%d:%02d" % [floori(t / 60.0), floori(fmod(t, 60.0))]


func update_from(g: Node2D) -> void:
	var p: Node2D = g.player
	var hk := "%d/%d" % [p.hp, p.max_hp]
	if hk != _hearts_key:
		_hearts_key = hk
		for c in hearts_box.get_children():
			c.queue_free()
			hearts_box.remove_child(c)
		for i in p.max_hp / 2:
			var v: int = p.hp - i * 2
			var tr := TextureRect.new()
			tr.texture = Art.tex("heart_full" if v >= 2 else ("heart_half" if v == 1 else "heart_empty"))
			tr.expand_mode = TextureRect.EXPAND_IGNORE_SIZE
			tr.stretch_mode = TextureRect.STRETCH_SCALE
			tr.mouse_filter = Control.MOUSE_FILTER_IGNORE
			hearts_box.add_child(tr)
		_layout_hearts()
	timer_label.text = fmt(g.t)
	kills_label.text = "%d abates" % g.kills
	gems_label.text = str(g.gems_total)
	lvl_label.text = "Nv %d" % g.lvl
	var nt := "poder no %d" % Bal.next_pick_level(g.lvl)
	if next_label.text != nt or kills_label.size.x != _w(kills_label) or gems_label.size.x != _w(gems_label):
		next_label.text = nt
		layout()
	xp_frac = float(g.xp) / g.need
	xp_pick = Bal.is_pick_level(g.lvl + 1)
	xp_track.queue_redraw()


func toast(a: String, b: String) -> void:
	toast_t1.text = a
	toast_t2.text = b
	_toast_t = 0.0
	layout()


func _process(delta: float) -> void:
	# aviso: aparece em .25 s subindo 6 px, fica 1,8 s e some em .25 s (CSS #toast)
	if _toast_t >= 0:
		_toast_t += delta
		var a := minf(1.0, _toast_t / 0.25) if _toast_t < 1.8 else maxf(0.0, 1.0 - (_toast_t - 1.8) / 0.25)
		toast_box.modulate.a = a
		toast_box.position.y = floorf(root.size.y * 0.6) - roundf(6 * a)   # sobe 6 px ao aparecer
		if _toast_t > 2.1:
			_toast_t = -1.0


func show_state(state: String) -> void:
	title_box.visible = state == "menu"
	hud_box.visible = state != "menu"
	pause_overlay.visible = state == "pause"
	if state != "over":
		over_overlay.visible = false
	if state == "menu":
		toast_box.modulate.a = 0.0
		_toast_t = -1.0
	if state == "pause":
		btn_resume.grab_focus()
	layout()


func show_over(t: float, kills: int, gems: int, ups: int, best_line: String) -> void:
	over_vals["Tempo"].text = fmt(t)
	over_vals["Abates"].text = str(kills)
	over_vals["Joias"].text = str(gems)
	over_vals["Poderes"].text = str(ups)
	over_best.text = best_line
	over_overlay.visible = true
	layout()
	btn_again.grab_focus()
