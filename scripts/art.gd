extends Node
## Autoload "Art": manifesto dos sprites exportados do jogo HTML (assets/sprites/sprites.json, gerado por
## tools/export_sprites.py), quadros soltos para o HUD (corações, joia, logo) e a fonte. Os personagens usam
## SpriteFrames (.tres) e o cenário usa TileSet e cenas; os PNGs não são editados à mão.

const DIR := "res://assets/sprites/"

var meta: Dictionary = {}          # nome -> {file, w, h, n, ...} (sprites.json)
var _frames: Dictionary = {}       # nome -> Array[Texture2D]
var font: FontFile
var font_bold: FontVariation
var font_semi: FontVariation


func _init() -> void:
	var f := FileAccess.open(DIR + "sprites.json", FileAccess.READ)
	meta = JSON.parse_string(f.get_as_text())
	font = load("res://assets/font/PixelifySans.ttf")
	font_bold = FontVariation.new()
	font_bold.base_font = font
	font_bold.variation_opentype = {"wght": 700}
	font_semi = FontVariation.new()
	font_semi.base_font = font
	font_semi.variation_opentype = {"wght": 600}


## Quadros de uma tira (cada quadro w x h).
func frames(name: String) -> Array:
	if _frames.has(name):
		return _frames[name]
	var m: Dictionary = meta[name]
	var tex: Texture2D = load(DIR + m.file)
	var out := []
	var w := int(m.w)
	var h := int(m.h)
	for i in int(m.n):
		var at := AtlasTexture.new()
		at.atlas = tex
		at.region = Rect2(i * w, 0, w, h)
		out.append(at)
	_frames[name] = out
	return out


func tex(name: String) -> Texture2D:
	return frames(name)[0]


func size(name: String) -> Vector2i:
	return Vector2i(int(meta[name].w), int(meta[name].h))
