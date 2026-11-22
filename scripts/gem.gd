extends Sprite2D
## Joia de experiência (GEMS no HTML): v = experiência (1 verde, 5 azul, 10 vermelha); pull = atraída pelo ímã.

const TEX := {1: preload("res://assets/sprites/gem_g.png"), 5: preload("res://assets/sprites/gem_b.png"),
	10: preload("res://assets/sprites/gem_r.png")}
## cor do brilho ao recolher (cena efeitos/brilho_joia.tscn)
const COR := {1: Color("#4fe07a"), 5: Color("#4fa3ff"), 10: Color("#ff4f7a")}

var gx := 0.0
var gy := 0.0
var v := 1
var pull := false
var dead := false


func setup(x: float, y: float, value: int) -> void:
	gx = x
	gy = y
	v = value
	texture = TEX[tier()]
	update_visual()


func tier() -> int:
	return 10 if v >= 10 else (5 if v >= 5 else 1)


func update_visual() -> void:
	# HTML: drawImage(img, round(g.x - cx - 2), round(g.y - cy - 3))
	position = Vector2(JsMath.jround(gx - 2), JsMath.jround(gy - 3))
