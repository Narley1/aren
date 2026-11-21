extends Node2D
## Aren. Estado igual ao objeto P do HTML (x, y, hp em meios corações, inv, dir, moving, anim, faceA).
## A posição lógica (px, py) é float; o nó fica sempre em pixel inteiro (arredondamento do JS).

var px := 0.0
var py := 0.0
var hp := 10
var max_hp := 10
var inv := 0.0
var dir := "down"            # down | up | side (direita) | left
var moving := false
var anim := 0.0
var face_a := PI / 2

@onready var sprite: Sprite2D = $Sprite


func reset() -> void:
	px = 0.0
	py = 0.0
	hp = Bal.HERO.hp
	max_hp = Bal.HERO.hp
	inv = Bal.HERO.invStart
	dir = "down"
	moving = false
	anim = 0.0
	face_a = PI / 2
	update_visual()


## Movimento do update() do HTML ("// movement"): ix, iy já normalizados para comprimento <= 1.
func move(ix: float, iy: float, dt: float) -> void:
	var il := Vector2(ix, iy).length()
	if il > 1.0:
		ix /= il
		iy /= il
	moving = il > 0.1
	var spd: float = Bal.HERO.speed   # + W.boots*bootsSpeed (Etapa 2); lentidão e gelo (Etapas 3-4)
	px += ix * spd * dt
	py += iy * spd * dt
	if moving:
		anim += dt * 9.0
		face_a = atan2(iy, ix)
		if absf(ix) > absf(iy):
			dir = "left" if ix < 0 else "side"
		else:
			dir = "up" if iy < 0 else "down"
	inv -= dt


## Quando a espada golpeia com Aren parado, ele vira para o golpe (update() do HTML)
func face_toward(ang: float) -> void:
	if moving:
		return
	if absf(cos(ang)) > absf(sin(ang)):
		dir = "left" if cos(ang) < 0 else "side"
	else:
		dir = "up" if sin(ang) < 0 else "down"


func update_visual() -> void:
	var fr: Array = Art.frames("hero_" + dir)
	var f := (absi(floori(anim)) % 4) if moving else 0
	sprite.texture = fr[f]
	var sz := Art.size("hero_down")
	# HTML: drawImage(set[f], round(P.x - w/2 - cx), round(P.y - h + 1 - cy)); w é par, então dá no mesmo
	# pôr o nó no pé (round(P.x), round(P.y)) — que é a chave da ordenação por y — e deslocar o sprite
	position = Vector2(JsMath.jround(px), JsMath.jround(py))
	sprite.offset = Vector2(-sz.x / 2, -sz.y + 1)
	# piscando enquanto invulnerável
	sprite.visible = not (inv > 0 and floori(inv * 14) % 2 == 1)
