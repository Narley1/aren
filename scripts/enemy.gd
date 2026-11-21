extends Node2D
## Inimigo comum (Etapa 1: goblin). Campos com os nomes do objeto de inimigo do HTML (E[]):
## type, x, y, hp, kx/ky (empurrão), flash, anim, elite, face, dead.

var type := "goblin"
var d: Dictionary            # Bal.ET[type] + w, h do sprite
var ex := 0.0
var ey := 0.0
var hp := 0.0
var kx := 0.0
var ky := 0.0
var flash := 0.0
var anim := 0.0
var elite := false
var face := "down"
var dead := false

@onready var sprite: Sprite2D = $Sprite
@onready var outline: Node2D = $Outline


func setup(t: String, x: float, y: float, hp_mul: float, is_elite: bool, anim0: float) -> void:
	type = t
	d = Bal.ET[t].duplicate()
	var sz := Art.size(t + "_down")
	d.w = sz.x
	d.h = sz.y
	ex = x
	ey = y
	elite = is_elite
	hp = d.hp * hp_mul
	anim = anim0


func update_visual() -> void:
	var f := absi(floori(anim)) % 4
	var base: String = type + "_" + face
	var w: int = d.w
	var h: int = d.h
	# HTML: x = round(e.x - w/2 - cx), y = round(e.y - h - cy + 1); nó no pé (chave do y-sort)
	position = Vector2(JsMath.jround(ex), JsMath.jround(ey))
	var off := Vector2(-w / 2, -h + 1)
	sprite.offset = off
	sprite.texture = Art.frames(base + ("_flash" if flash > 0 else ""))[f]
	outline.visible = elite
	if elite:
		var g: Texture2D = Art.frames(base + "_gold")[f]
		var i := 0
		for o in [Vector2(-1, 0), Vector2(1, 0), Vector2(0, -1), Vector2(0, 1)]:
			var s: Sprite2D = outline.get_child(i)
			s.texture = g
			s.offset = off + o
			i += 1
