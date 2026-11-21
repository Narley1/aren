extends Node2D
## Chão infinito em blocos de 128 px (gerados por GroundGen, idênticos ao HTML) e props do cenário.
## Os blocos são gerados em threads (WorkerThreadPool) perto da câmera; a textura é criada na thread
## principal. Os props viram Sprite2D dentro do nó com y-sort (`actors`), como a lista YS do HTML.

const GCH := GroundGen.GCH
const MAX_CHUNKS := 96

var actors: Node2D                     # nó com y_sort_enabled onde ficam os props
var shadows: Node2D                    # camada de sombras (desenha as sombras dos props também)
var view := Rect2(0, 0, 200, 300)      # área visível em coordenadas do mundo (cx, cy, VW, VH)

var _stamps: Dictionary
var _tex: Dictionary = {}              # chave -> ImageTexture
var _order: Array = []                 # chaves em ordem de uso (para descartar os antigos)
var _jobs: Dictionary = {}             # chave -> task id
var _results: Dictionary = {}          # chave -> Image (preenchido pelas threads)
var _mutex := Mutex.new()
var _prop_cache: Dictionary = {}
var _prop_nodes: Dictionary = {}       # entrada do prop -> Sprite2D
var visible_props: Array = []          # props na área (para as sombras)


func _ready() -> void:
	_stamps = Art.stamp_images()


static func key_of(i: int, j: int) -> int:
	return i * 100003 + j


## Gera já (bloqueando) os blocos que cobrem a área r — usado antes da partida e nos testes.
func pregen(r: Rect2) -> void:
	for j in range(floori(r.position.y / GCH), floori(r.end.y / GCH) + 1):
		for i in range(floori(r.position.x / GCH), floori(r.end.x / GCH) + 1):
			var k := key_of(i, j)
			if _tex.has(k):
				continue
			if _jobs.has(k):
				WorkerThreadPool.wait_for_task_completion(_jobs[k])
				_jobs.erase(k)
				_collect()
				if _tex.has(k):
					continue
			_put(k, GroundGen.make_chunk(i, j, _stamps))


func _gen_task(i: int, j: int) -> void:
	var img := GroundGen.make_chunk(i, j, _stamps)
	_mutex.lock()
	_results[key_of(i, j)] = img
	_mutex.unlock()


func _put(k: int, img: Image) -> void:
	_tex[k] = ImageTexture.create_from_image(img)
	_order.append(k)
	if _order.size() > MAX_CHUNKS:
		_tex.erase(_order.pop_front())


func _collect() -> void:
	_mutex.lock()
	var done := _results.duplicate()
	_results.clear()
	_mutex.unlock()
	for k in done:
		if not _tex.has(k):
			_put(k, done[k])
	for k in _jobs.keys():
		if WorkerThreadPool.is_task_completed(_jobs[k]):
			WorkerThreadPool.wait_for_task_completion(_jobs[k])
			_jobs.erase(k)


func _exit_tree() -> void:
	for k in _jobs:
		WorkerThreadPool.wait_for_task_completion(_jobs[k])
	_jobs.clear()


## Chamado pelo jogo a cada quadro com a área visível. Pede os blocos que faltam (um anel a mais em volta).
func update_view(r: Rect2) -> void:
	view = r
	_collect()
	var i0 := floori(r.position.x / GCH) - 1
	var i1 := floori(r.end.x / GCH) + 1
	var j0 := floori(r.position.y / GCH) - 1
	var j1 := floori(r.end.y / GCH) + 1
	# os que faltam, do mais perto do centro da vista para o mais longe (como o pregenGround do HTML)
	var c := r.get_center()
	var want := []
	for j in range(j0, j1 + 1):
		for i in range(i0, i1 + 1):
			var k := key_of(i, j)
			if not _tex.has(k) and not _jobs.has(k):
				want.append([((i + 0.5) * GCH - c.x) ** 2 + ((j + 0.5) * GCH - c.y) ** 2, i, j])
	want.sort_custom(func(a, b): return a[0] < b[0])
	for w in want:
		if _jobs.size() >= 6:
			break
		_jobs[key_of(w[1], w[2])] = WorkerThreadPool.add_task(_gen_task.bind(w[1], w[2]), false, "chão")
	_update_props(r)
	queue_redraw()


func _draw() -> void:
	var r := view
	for j in range(floori(r.position.y / GCH), floori(r.end.y / GCH) + 1):
		for i in range(floori(r.position.x / GCH), floori(r.end.x / GCH) + 1):
			var t: Texture2D = _tex.get(key_of(i, j))
			if t:
				draw_texture(t, Vector2(i * GCH, j * GCH))


## Props na área (mesma margem do HTML: x -24..+24, y -8..+46) como Sprite2D no nó com y-sort.
func _update_props(r: Rect2) -> void:
	if actors == null:
		return
	visible_props = GroundGen.props_in(r.position.x - 24, r.position.y - 8, r.end.x + 24, r.end.y + 46, _prop_cache)
	var keep := {}
	var tt := Time.get_ticks_msec() / 1000.0
	for o in visible_props:
		keep[o] = true
		var s: Sprite2D = _prop_nodes.get(o)
		var m: Dictionary = Art.meta["prop_" + o.k]
		if s == null:
			s = Sprite2D.new()
			s.centered = false
			s.offset = Vector2(-int(m.ox), -int(m.oy))
			s.position = Vector2(JsMath.jround(o.x), JsMath.jround(o.y))
			actors.add_child(s)
			_prop_nodes[o] = s
		var fr: Array = Art.frames("prop_" + o.k)
		s.texture = fr[int(floor(tt * 2.2 + o.ph)) % fr.size()]
	for o in _prop_nodes.keys():
		if not keep.has(o):
			_prop_nodes[o].queue_free()
			_prop_nodes.erase(o)
	if _prop_cache.size() > 4000:   # como PROPS no HTML: limpa o cache (os nós são recriados no próximo quadro)
		_prop_cache.clear()
		for o in _prop_nodes:
			_prop_nodes[o].queue_free()
		_prop_nodes.clear()


## Árvore na frente de Aren fica semitransparente (como no HTML: alpha .55)
func update_tree_alpha(px: float, py: float) -> void:
	for o in _prop_nodes:
		if o.k != "tree":
			continue
		var behind: bool = py < o.y and absf(px - o.x) < 16 and py > o.y - 40
		_prop_nodes[o].modulate.a = 0.55 if behind else 1.0


func ready_count() -> int:
	return _tex.size()
