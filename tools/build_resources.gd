extends SceneTree
## Monta os recursos do Godot a partir dos PNGs exportados do HTML (tools/export_sprites.py) e dos atlas de
## tiles (tools/make_tileset.py). Rodar de novo sobrescreve os .tres (mudanças feitas à mão neles se perdem):
##
##   godot --headless --path . -s res://tools/build_resources.gd
##
## Saídas:
##   assets/sprites/aren.tres     SpriteFrames de Aren: andar_baixo/cima/lado (4 quadros, 9 qps) e parado_*
##   assets/sprites/goblin.tres   SpriteFrames do goblin: andar_baixo/cima/lado (4 quadros, 28/6 qps)
##   assets/sprites/espada.tres   SpriteFrames da espada: "girar" = as 48 rotações exportadas do HTML
##   assets/tiles/chao.tres       TileSet 16x16: fonte 0 = terreno (terrain set "Chão", Match Corners, com
##                                Grama, Capim alto e Terra), fonte 1 = detalhes (dado "tipo" em cada tile)

const SPR := "res://assets/sprites/"
const TILES := "res://assets/tiles/"


func _init() -> void:
	var meta: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(SPR + "sprites.json"))
	_frames("aren", meta, [["andar_baixo", "hero_down"], ["andar_cima", "hero_up"], ["andar_lado", "hero_side"]], 9.0, true)
	_frames("goblin", meta, [["andar_baixo", "goblin_down"], ["andar_cima", "goblin_up"], ["andar_lado", "goblin_side"]], 28.0 / 6.0, false)
	_frames("espada", meta, [["girar", "sword"]], 0.0, false)
	_tileset()
	quit()


func _strip(meta: Dictionary, name: String) -> Array:
	var m: Dictionary = meta[name]
	var tex: Texture2D = load(SPR + m.file)
	var out := []
	for i in int(m.n):
		var at := AtlasTexture.new()
		at.atlas = tex
		at.region = Rect2(i * int(m.w), 0, int(m.w), int(m.h))
		out.append(at)
	return out


func _frames(file: String, meta: Dictionary, anims: Array, fps: float, idle: bool) -> void:
	var sf := SpriteFrames.new()
	sf.remove_animation("default")
	for a in anims:
		var fr := _strip(meta, a[1])
		sf.add_animation(a[0])
		sf.set_animation_speed(a[0], fps if fps > 0 else 1.0)
		sf.set_animation_loop(a[0], fps > 0)
		for t in fr:
			sf.add_frame(a[0], t)
		if idle:   # parado = o primeiro quadro do andar, como no HTML (quadro 0 quando não anda)
			var n: String = a[0].replace("andar_", "parado_")
			sf.add_animation(n)
			sf.set_animation_loop(n, false)
			sf.add_frame(n, fr[0])
	_save(sf, SPR + file + ".tres")


func _tileset() -> void:
	var info: Dictionary = JSON.parse_string(FileAccess.get_file_as_string(TILES + "tiles.json"))
	var T := int(info.tile)
	var ts := TileSet.new()
	ts.tile_size = Vector2i(T, T)
	ts.add_terrain_set()
	ts.set_terrain_set_mode(0, TileSet.TERRAIN_MODE_MATCH_CORNERS)
	var cols := [Color("72cc52"), Color("3a8a36"), Color("e6c890")]
	for i in info.terrains.size():
		ts.add_terrain(0)
		ts.set_terrain_name(0, i, info.terrains[i])
		ts.set_terrain_color(0, i, cols[i])
	ts.add_custom_data_layer()
	ts.set_custom_data_layer_name(0, "tipo")
	ts.set_custom_data_layer_type(0, TYPE_STRING)

	var ground := TileSetAtlasSource.new()
	ground.resource_name = "Terreno"
	ground.texture = load(TILES + "chao.png")
	ground.texture_region_size = Vector2i(T, T)
	ts.add_source(ground, 0)
	var bits := [TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER, TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER,
		TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER, TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER]
	for t in info.chao:
		var c := Vector2i(int(t.x), int(t.y))
		ground.create_tile(c)
		var td := ground.get_tile_data(c, 0)
		td.terrain_set = 0
		td.terrain = int(t.terrain)
		for k in 4:
			td.set_terrain_peering_bit(bits[k], int(t.corners[k]))
		td.probability = float(t.probability)
		td.set_custom_data("tipo", "terreno")

	var dec := TileSetAtlasSource.new()
	dec.resource_name = "Detalhes"
	dec.texture = load(TILES + "detalhes.png")
	dec.texture_region_size = Vector2i(T, T)
	ts.add_source(dec, 1)
	for t in info.detalhes:
		var c := Vector2i(int(t.x), int(t.y))
		dec.create_tile(c)
		dec.get_tile_data(c, 0).set_custom_data("tipo", t.tipo)
	_save(ts, TILES + "chao.tres")


func _save(res: Resource, path: String) -> void:
	var err := ResourceSaver.save(res, path)
	print(("salvo " if err == OK else "ERRO ao salvar ") + path)
