extends Node2D
## O campo infinito, montado com as ferramentas do Godot:
##   - "Chao" (TileMapLayer) com o TileSet assets/tiles/chao.tres. O TileSet tem um terrain set no modo
##     Match Corners (Grama, Capim alto, Terra): cada tile diz qual terreno fica em cada canto, então as bordas
##     das trilhas e do capim se encaixam sozinhas. O shader do chão (material da camada) pinta as manchas.
##   - "Detalhes" (TileMapLayer, mesmo TileSet, fonte 1): tufos, trevos, flores, canteiros e pedrinhas. Cada
##     tile de detalhe tem o dado "tipo" (grama, flores_fW..., terra), que diz onde ele pode aparecer.
##   - Props (árvores, arbustos, pedras, tocos) são cenas .tscn instanciadas no nó com Y-sort (Atores).
## Os cantos de terreno vêm de FastNoiseLite (ruido_terra, ruido_capim): um canto é Terra se o ruído da terra
## passar do limite, senão Capim alto se o ruído do capim passar, senão Grama. O campo é gerado em blocos de
## 16x16 células em volta da câmera (poucos por quadro) e os blocos longe são apagados.
##
## A peça de cada célula é escolhida lendo os bits de terreno do próprio TileSet (o mesmo que o pincel de
## terreno do editor usa) — tiles novos ou variações feitas no editor entram sozinhos no sorteio.
## Pintar à mão no editor funciona, mas o gerador escreve por cima nos blocos que ele gera.

const GRASS := 0
const TALL := 1
const DIRT := 2
const BLOCO := 16                 # células por lado de um bloco
const SRC_TERRENO := 0
const SRC_DETALHES := 1

@export_group("Terreno")
@export var ruido_terra: FastNoiseLite      ## trilhas de terra
@export var limite_terra := 0.337           ## acima disto = Terra (maior = menos terra)
@export var ruido_capim: FastNoiseLite      ## manchas de capim alto
@export var limite_capim := 0.32            ## acima disto = Capim alto
@export_group("Detalhes")
@export var ruido_flores: FastNoiseLite     ## onde aparecem canteiros de flores
@export var limite_flores := 0.55
@export_range(0.0, 1.0) var chance_detalhe_grama := 0.55   ## chance de um tufo/trevo/flor numa célula de grama
@export_range(0.0, 1.0) var chance_canteiro := 0.45        ## chance de flor numa célula de canteiro
@export_range(0.0, 1.0) var chance_detalhe_terra := 0.3    ## chance de pedrinha/rachadura numa célula de terra
@export_group("Props")
@export var cena_arvore: PackedScene
@export var cena_arbusto: PackedScene
@export var cena_arbusto_frutas: PackedScene
@export var cena_pedra: PackedScene
@export var cena_toco: PackedScene
@export var grade_props := 44               ## uma chance de prop a cada grade x grade px (HTML: propsIn)
@export var raio_livre := 40.0              ## sem props perto do início (|x| e |y| menores que isto)
@export_group("Blocos")
@export var blocos_por_quadro := 2          ## quantos blocos novos no máximo por quadro
@export var atores_path: NodePath = ^"../Atores"

@onready var chao: TileMapLayer = $Chao
@onready var detalhes: TileMapLayer = $Detalhes
var atores: Node2D

var _pecas: Dictionary = {}       # chave dos 4 cantos -> [[atlas_coords, probabilidade], ...]
var _detalhes: Dictionary = {}    # tipo -> [atlas_coords, ...]
var _blocos: Dictionary = {}      # Vector2i do bloco -> Array de props (nós)
var arvores: Array = []           # árvores carregadas (ficam transparentes com Aren atrás)
var visible_props: Array = []     # props carregados (testes)


func _ready() -> void:
	atores = get_node_or_null(atores_path)
	_ler_tileset()


static func chave(tl: int, tr: int, bl: int, br: int) -> int:
	return ((tl * 3 + tr) * 3 + bl) * 3 + br


## Lê do TileSet as peças de terreno (pelos bits de canto) e os detalhes (pelo dado "tipo").
func _ler_tileset() -> void:
	var ts := chao.tile_set
	var src := ts.get_source(SRC_TERRENO) as TileSetAtlasSource
	for i in src.get_tiles_count():
		var c := src.get_tile_id(i)
		var td := src.get_tile_data(c, 0)
		if td.terrain_set != 0:
			continue
		var k := chave(td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_TOP_LEFT_CORNER),
			td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_TOP_RIGHT_CORNER),
			td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_BOTTOM_LEFT_CORNER),
			td.get_terrain_peering_bit(TileSet.CELL_NEIGHBOR_BOTTOM_RIGHT_CORNER))
		if not _pecas.has(k):
			_pecas[k] = []
		_pecas[k].append([c, td.probability])
	var dec := ts.get_source(SRC_DETALHES) as TileSetAtlasSource
	for i in dec.get_tiles_count():
		var c := dec.get_tile_id(i)
		var tipo: String = dec.get_tile_data(c, 0).get_custom_data("tipo")
		if not _detalhes.has(tipo):
			_detalhes[tipo] = []
		_detalhes[tipo].append(c)


## hash inteiro -> [0, 1), igual em toda execução (o campo é sempre o mesmo)
static func h(x: int, y: int, s: int) -> float:
	var n := (x * 374761393 + y * 668265263 + s * 1442695041) & 0xFFFFFFFF
	n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
	return float((n ^ (n >> 16)) & 0xFFFFFFFF) / 4294967296.0


## Terreno de um canto (vértice da grade de células), sem a regra de vizinhança.
func _canto_bruto(vx: int, vy: int) -> int:
	var x := float(vx * chao.tile_set.tile_size.x)
	var y := float(vy * chao.tile_set.tile_size.y)
	if ruido_terra.get_noise_2d(x, y) > limite_terra:
		return DIRT
	if ruido_capim.get_noise_2d(x, y) > limite_capim:
		return TALL
	return GRASS


## Terreno da posição no mundo (px): o do canto mais perto (antes das regras de vizinhança; só para props).
func terreno_em(p: Vector2) -> int:
	var t := Vector2(chao.tile_set.tile_size)
	return _canto_bruto(roundi(p.x / t.x), roundi(p.y / t.y))


func _gerar_bloco(b: Vector2i) -> void:
	# cantos do bloco + 2 de margem (as regras olham os vizinhos; o resultado não depende do bloco)
	var n := BLOCO + 5
	var x0 := b.x * BLOCO - 2
	var y0 := b.y * BLOCO - 2
	var raw := PackedByteArray()
	raw.resize(n * n)
	for j in n:
		for i in n:
			raw[j * n + i] = _canto_bruto(x0 + i, y0 + j)
	# 1) canto isolado (os 8 vizinhos iguais entre si e diferentes dele) vira o terreno dos vizinhos:
	#    sem ilhas de um canto só, que viram losangos
	var f1 := raw.duplicate()
	for j in range(1, n - 1):
		for i in range(1, n - 1):
			var o := raw[(j - 1) * n + i - 1]
			if o == raw[j * n + i]:
				continue
			var same := true
			for dj in range(-1, 2):
				for di in range(-1, 2):
					if (di != 0 or dj != 0) and raw[(j + dj) * n + i + di] != o:
						same = false
			if same:
				f1[j * n + i] = o
	# 2) capim alto não encosta na terra (o tile teria 3 terrenos): vira grama perto dela
	var v := f1.duplicate()
	for j in range(2, n - 2):
		for i in range(2, n - 2):
			if f1[j * n + i] != TALL:
				continue
			for dj in range(-1, 2):
				for di in range(-1, 2):
					if f1[(j + dj) * n + i + di] == DIRT:
						v[j * n + i] = GRASS
	var cx0 := b.x * BLOCO
	var cy0 := b.y * BLOCO
	for j in BLOCO:
		for i in BLOCO:
			var a := (j + 2) * n + i + 2
			var tl := v[a]
			var tr := v[a + 1]
			var bl := v[a + n]
			var br := v[a + n + 1]
			var cell := Vector2i(cx0 + i, cy0 + j)
			chao.set_cell(cell, SRC_TERRENO, _peca(chave(tl, tr, bl, br), cell))
			var tipo := ""
			if tl == GRASS and tr == GRASS and bl == GRASS and br == GRASS:
				var wx := float(cell.x * 16 + 8)
				var wy := float(cell.y * 16 + 8)
				if ruido_flores.get_noise_2d(wx, wy) > limite_flores:
					if h(cell.x, cell.y, 3) < chance_canteiro:
						var kinds := ["flores_fW", "flores_fY", "flores_fP", "flores_fB"]
						tipo = kinds[int(h(floori(cell.x / 4.0), floori(cell.y / 4.0), 4) * 4.0)]
				elif h(cell.x, cell.y, 5) < chance_detalhe_grama:
					tipo = "grama"
			elif tl == DIRT and tr == DIRT and bl == DIRT and br == DIRT and h(cell.x, cell.y, 6) < chance_detalhe_terra:
				tipo = "terra"
			var lista: Array = _detalhes.get(tipo, [])
			if lista.is_empty():
				detalhes.erase_cell(cell)
			else:
				detalhes.set_cell(cell, SRC_DETALHES, lista[int(h(cell.x, cell.y, 7) * lista.size())])
	_blocos[b] = _gerar_props(b)


func _peca(k: int, cell: Vector2i) -> Vector2i:
	var opts: Array = _pecas.get(k, _pecas.get(0, []))
	if opts.size() == 1:
		return opts[0][0]
	var tot := 0.0
	for o in opts:
		tot += o[1]
	var r := h(cell.x, cell.y, 1) * tot
	for o in opts:
		r -= o[1]
		if r <= 0.0:
			return o[0]
	return opts[-1][0]


## Props do bloco: uma chance por grade de 44 px, como o propsIn do HTML (árvore 13%, arbusto 9%, arbusto
## com frutas 4%, pedra 4%, toco 4%; na terra só pedra, 6%), numa posição sorteada dentro da grade.
func _gerar_props(b: Vector2i) -> Array:
	var out := []
	if atores == null:
		return out
	var ts := chao.tile_set.tile_size.x
	var r0 := Rect2(b.x * BLOCO * ts, b.y * BLOCO * ts, BLOCO * ts, BLOCO * ts)
	var G := grade_props
	for gy in range(floori(r0.position.y / G) - 1, floori(r0.end.y / G) + 1):
		for gx in range(floori(r0.position.x / G) - 1, floori(r0.end.x / G) + 1):
			var r := h(gx, gy, 11)
			if r > 0.34:
				continue
			var p := Vector2(gx * G + 8 + h(gx, gy, 12) * (G - 16), gy * G + 8 + h(gx, gy, 13) * (G - 16)).round()
			if not r0.has_point(p) or (absf(p.x) < raio_livre and absf(p.y) < raio_livre):
				continue
			var cena: PackedScene
			if terreno_em(p) == DIRT:
				if r < 0.06: cena = cena_pedra
				else: continue
			else:
				cena = cena_arvore if r < 0.13 else (cena_arbusto if r < 0.22 else (cena_arbusto_frutas if r < 0.26 else (cena_pedra if r < 0.30 else cena_toco)))
			if cena == null:
				continue
			var o: Node2D = cena.instantiate()
			o.position = p
			atores.add_child(o)
			out.append(o)
			if o.is_in_group("arvores"):
				arvores.append(o)
	return out


func _apagar_bloco(b: Vector2i) -> void:
	for j in BLOCO:
		for i in BLOCO:
			var cell := Vector2i(b.x * BLOCO + i, b.y * BLOCO + j)
			chao.erase_cell(cell)
			detalhes.erase_cell(cell)
	for o in _blocos[b]:
		arvores.erase(o)
		o.queue_free()
	_blocos.erase(b)


func _faixa(r: Rect2) -> Rect2i:
	var px := float(BLOCO * chao.tile_set.tile_size.x)
	var a := Vector2i(floori(r.position.x / px), floori(r.position.y / px))
	var z := Vector2i(floori(r.end.x / px), floori(r.end.y / px))
	return Rect2i(a, z - a + Vector2i.ONE)


## Gera já todos os blocos que cobrem a área (usado antes da partida, nas capturas e nos testes).
func pregen(r: Rect2) -> void:
	var f := _faixa(r)
	for y in range(f.position.y, f.end.y):
		for x in range(f.position.x, f.end.x):
			if not _blocos.has(Vector2i(x, y)):
				_gerar_bloco(Vector2i(x, y))
	_atualizar_lista()


## Chamado a cada quadro com a área visível: gera os blocos que faltam (do centro para fora, no máximo
## `blocos_por_quadro`) numa margem de 64 px e apaga os que ficaram a mais de um bloco de distância.
func update_view(r: Rect2) -> void:
	var f := _faixa(r.grow(64))
	var c := r.get_center()
	var px := float(BLOCO * chao.tile_set.tile_size.x)
	var falta := []
	for y in range(f.position.y, f.end.y):
		for x in range(f.position.x, f.end.x):
			if not _blocos.has(Vector2i(x, y)):
				falta.append([((x + 0.5) * px - c.x) ** 2 + ((y + 0.5) * px - c.y) ** 2, Vector2i(x, y)])
	if not falta.is_empty():
		falta.sort_custom(func(a, b): return a[0] < b[0])
		for i in mini(blocos_por_quadro, falta.size()):
			_gerar_bloco(falta[i][1])
	var keep := f.grow(1)
	for b in _blocos.keys():
		if not keep.has_point(b):
			_apagar_bloco(b)
	_atualizar_lista()


func _atualizar_lista() -> void:
	visible_props.clear()
	for b in _blocos:
		visible_props.append_array(_blocos[b])


func blocos_prontos() -> int:
	return _blocos.size()


func tem_bloco_em(p: Vector2) -> bool:
	var px := float(BLOCO * chao.tile_set.tile_size.x)
	return _blocos.has(Vector2i(floori(p.x / px), floori(p.y / px)))


## Árvore na frente de Aren fica semitransparente (HTML: alpha .55)
func update_tree_alpha(px: float, py: float) -> void:
	for o in arvores:
		var behind: bool = py < o.position.y and absf(px - o.position.x) < 16 and py > o.position.y - 40
		(o.get_node("Sprite") as CanvasItem).modulate.a = 0.55 if behind else 1.0
