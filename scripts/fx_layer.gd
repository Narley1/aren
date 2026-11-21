extends Node2D
## Efeitos por cima das criaturas: golpe da espada (arco de pixels + sprite girado), partículas e números
## de dano. Porte do desenho do render() do HTML ("// sword swing", FX 'p', drawNum).

var game: Node2D

const DIG := ["111101101101111", "010110010010111", "111001111100111", "111001111001111", "101101111001001",
	"111100111001111", "111100111101111", "111001001001001", "111101111101111", "111101111001111"]
const NUM_SHADOW := Color("#1b1020")
const CORE := Color("#ffffff")
const MID := Color("#bfe6ff")
const EDGE := Color("#5fa8f0")


func _px(x: int, y: int, c: Color) -> void:
	draw_rect(Rect2(x, y, 1, 1), c)


func _draw() -> void:
	if game == null:
		return
	_draw_swing()
	for f in game.fx:
		draw_rect(Rect2(JsMath.jround(f.x), JsMath.jround(f.y), f.s, f.s), f.col)
	for n in game.nums:
		_draw_num(n.v, n.x, n.y, n.col)


func _draw_swing() -> void:
	var s = game.swing
	if s == null:
		return
	var p: Node2D = game.player
	var px: float = p.px
	var py: float = p.py - 9
	for dir in s.dirs:
		var q: Dictionary = game.swing_pose(s, dir)
		var pr: float = q.pr
		var fade: float = q.fade
		if q.T >= 0.16 and pr > 0:
			var R: float = s.range
			var span: float = q.span
			var steps := maxi(8, ceili(absf(span * pr) * R * 1.4))
			for i in steps + 1:
				var qq := float(i) / steps
				var a: float = q.a0 + span * pr * qq
				var age := 1.0 - qq
				var th := 1 + JsMath.jround((1.0 - age) * (5 + R * 0.12))
				var c := cos(a)
				var sn := sin(a)
				for k in th:
					var r := R - k
					var alpha := fade * (1.0 - age * 0.85) * (1.0 if k == 0 else (0.9 if k < 2 else 0.55))
					var col := EDGE if k == 0 else (CORE if k < maxf(2.0, th * 0.5) else MID)
					col.a = alpha
					_px(JsMath.jround(px + c * r), JsMath.jround(py + sn * r), col)
		# a lâmina: um dos 48 sprites girados (drawSword)
		var cur: float = q.cur
		var hx := px + cos(cur) * 4
		var hy := py + sin(cur) * 4
		var n := 48
		var k := ((JsMath.jround(cur / TAU * n) % n) + n) % n
		var R2: int = Art.meta.sword.R
		draw_texture(Art.frames("sword")[k], Vector2(JsMath.jround(hx - R2), JsMath.jround(hy - R2)), Color(1, 1, 1, minf(1.0, fade * 1.5)))


## drawNum do HTML: dígitos 3x5 com sombra escura deslocada 1 px
func _draw_num(v: int, x: float, y: float, col: Color) -> void:
	var s := str(v)
	var x0 := JsMath.jround(x - s.length() * 2)
	var y0 := JsMath.jround(y)
	for i in s.length():
		var pat: String = DIG[s.unicode_at(i) - 48]
		for pass_i in 2:
			var c := col if pass_i == 1 else NUM_SHADOW
			var o := 0 if pass_i == 1 else 1
			for j in 15:
				if pat[j] == "1":
					_px(x0 + i * 4 + (j % 3) + o, y0 + (j / 3) + o, c)
