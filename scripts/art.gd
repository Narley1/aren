extends Node
## Autoload "Art": carrega os sprites exportados do jogo HTML (assets/sprites, gerados por
## tools/export_sprites.py) e entrega os quadros como texturas. Os PNGs não são editados à mão.

const DIR := "res://assets/sprites/"

var meta: Dictionary = {}          # nome -> {file, w, h, n, ...} (sprites.json)
var _frames: Dictionary = {}       # nome -> Array[Texture2D]
var _images: Dictionary = {}       # nome -> Image (para compor o chão)
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


func image(name: String) -> Image:
	if not _images.has(name):
		var t: Texture2D = load(DIR + meta[name].file)
		var img := t.get_image()
		img.convert(Image.FORMAT_RGBA8)
		_images[name] = img
	return _images[name]


## Carimbos do chão como {nome: Image}, para GroundGen.make_chunk (thread-safe depois de carregados).
func stamp_images() -> Dictionary:
	var out := {}
	for k in ["tuft", "tuft2", "clover", "fW", "fP", "fY", "fB", "peb", "dpeb", "crack", "tall"]:
		out[k] = image("stamp_" + k)
	return out
