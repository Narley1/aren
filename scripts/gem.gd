extends Sprite2D
## Joia de experiência (GEMS no HTML): v = experiência (1 verde, 5 azul, 10 vermelha); pull = atraída pelo ímã.

var gx := 0.0
var gy := 0.0
var v := 1
var pull := false
var dead := false


func setup(x: float, y: float, value: int) -> void:
	gx = x
	gy = y
	v = value
	centered = false
	texture = Art.tex("gem_r" if v >= 10 else ("gem_b" if v >= 5 else "gem_g"))
	update_visual()


func update_visual() -> void:
	# HTML: drawImage(img, round(g.x - cx - 2), round(g.y - cy - 3))
	position = Vector2(JsMath.jround(gx - 2), JsMath.jround(gy - 3))
