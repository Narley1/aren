class_name GroundGen
## Gerador do chão, porte fiel das funções do HTML (seção "ground" e "props": dirtN, tallN, chunkRows,
## chunkFinish, propsIn). Mesmo hash, mesmo ruído, mesmos limiares e mesmos carimbos: um bloco gerado
## aqui é idêntico pixel por pixel ao do jogo HTML (o teste compara com tests/ref/ground_*.png).
## Tudo aqui é puro (sem estado global), então os blocos podem ser gerados em threads.

const GCH := 128            # tamanho do bloco de chão (GCH no HTML)
const DIRT_T := 0.665
const TALL_T := 0.64

# paleta GP do HTML
const G1 := [0x72, 0xcc, 0x52]
const G2 := [0x64, 0xbc, 0x48]
const GL := [0x98, 0xe0, 0x70]
const GD := [0x4c, 0x9e, 0x3c]
const GDD := [0x3a, 0x84, 0x3a]
const T1 := [0x4f, 0xa8, 0x40]
const T2 := [0x5c, 0xb6, 0x46]
const TD := [0x3a, 0x8a, 0x36]
const TL := [0x7c, 0xd2, 0x5a]
const D1 := [0xe6, 0xc8, 0x90]
const D2 := [0xd8, 0xb4, 0x7a]
const DD := [0xbe, 0x96, 0x60]
const DL := [0xf4, 0xe2, 0xb4]
const DE := [0xa8, 0x7e, 0x4a]
const DE2 := [0xc6, 0x9c, 0x64]


## Camada de ruído vnoise(x/s + ox, y/s + oy) com os 4 cantos da grade guardados: ao varrer uma linha
## de pixels os cantos quase nunca mudam, então quase não recalculamos o hash. Resultado idêntico.
class VLayer:
	var s: float
	var ox: float
	var oy: float
	var cx := 1 << 40
	var cy := 1 << 40
	var a := 0.0
	var b := 0.0
	var c := 0.0
	var d := 0.0

	func _init(scale: float, offx: float, offy: float) -> void:
		s = scale
		ox = offx
		oy = offy

	func at(wx: int, wy: int) -> float:
		var x := float(wx) / s + ox
		var y := float(wy) / s + oy
		var xi := floorf(x)
		var yi := floorf(y)
		var ix := int(xi)
		var iy := int(yi)
		if ix != cx or iy != cy:
			cx = ix
			cy = iy
			a = JsMath.h2(ix, iy)
			b = JsMath.h2(ix + 1, iy)
			c = JsMath.h2(ix, iy + 1)
			d = JsMath.h2(ix + 1, iy + 1)
		var xf := x - xi
		var yf := y - yi
		var u := xf * xf * (3.0 - 2.0 * xf)
		var v := yf * yf * (3.0 - 2.0 * yf)
		return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v


static func dirt_n(x: float, y: float) -> float:
	return JsMath.vnoise(x / 110.0 + 100.0, y / 110.0 + 100.0) * 0.78 + JsMath.vnoise(x / 26.0 + 40.0, y / 26.0 + 40.0) * 0.22


static func tall_n(x: float, y: float) -> float:
	return JsMath.vnoise(x / 64.0 + 300.0, y / 64.0 + 300.0) * 0.85 + JsMath.vnoise(x / 14.0 + 9.0, y / 14.0 + 9.0) * 0.15


## Gera o bloco (i, j) como Image RGBA8 de 128x128. `stamps` = {nome: Image} (carimbos exportados do HTML).
static func make_chunk(i: int, j: int, stamps: Dictionary) -> Image:
	var data := PackedByteArray()
	data.resize(GCH * GCH * 4)
	var ox := i * GCH
	var oy := j * GCH
	var l_d1 := VLayer.new(110.0, 100.0, 100.0)
	var l_d2 := VLayer.new(26.0, 40.0, 40.0)
	var l_s1 := VLayer.new(18.0, 7.0, 3.0)
	var l_s2 := VLayer.new(7.0, 2.0, 9.0)
	var l_t1 := VLayer.new(64.0, 300.0, 300.0)
	var l_t2 := VLayer.new(14.0, 9.0, 9.0)
	var l_m := VLayer.new(34.0, 50.0, 80.0)
	var k := 0
	for y in GCH:
		var wy := oy + y
		for x in GCH:
			var wx := ox + x
			var n := l_d1.at(wx, wy) * 0.78 + l_d2.at(wx, wy) * 0.22
			var h := JsMath.h2(wx * 3 + 11, wy * 7 + 5)
			var col: Array
			if n > DIRT_T:
				if n < DIRT_T + 0.012:
					col = DE if h < 0.5 else DE2
				elif n < DIRT_T + 0.02:
					col = DD
				else:
					col = D2 if (l_s1.at(wx, wy) * 0.65 + l_s2.at(wx, wy) * 0.35 + (h - 0.5) * 0.12) > 0.6 else D1
					if h < 0.035:
						col = DD
					elif h < 0.07:
						col = DL
			elif n > DIRT_T - 0.016:
				col = GDD if n > DIRT_T - 0.007 else (GD if h < 0.5 else GDD)
			else:
				var t := l_t1.at(wx, wy) * 0.85 + l_t2.at(wx, wy) * 0.15
				if t > TALL_T:
					var stripe := (wx + ((wy >> 1) * 2)) % 5   # % e >> com sinal, como no JS
					col = GD if t < TALL_T + 0.015 else (TD if stripe == 0 else (T2 if stripe == 2 else T1))
					if h < 0.04:
						col = TL
				else:
					var m := l_m.at(wx, wy) + (h - 0.5) * 0.08
					col = G1 if m > 0.52 else G2
					if h < 0.018:
						col = GL
					elif h < 0.036:
						col = GD
			data[k] = col[0]
			data[k + 1] = col[1]
			data[k + 2] = col[2]
			data[k + 3] = 255
			k += 4
	var img := Image.create_from_data(GCH, GCH, false, Image.FORMAT_RGBA8, data)
	# carimbos numa grade de 8 px (chunkFinish)
	var SG := 8
	for gy in range(floori((oy - 8) / float(SG)), floori((oy + GCH) / float(SG)) + 1):
		for gx in range(floori((ox - 8) / float(SG)), floori((ox + GCH) / float(SG)) + 1):
			var r := JsMath.h2(gx * 13 + 7, gy * 17 + 3)
			var sx := gx * SG + floori(JsMath.h2(gx, gy + 51) * 6.0)
			var sy := gy * SG + floori(JsMath.h2(gx + 77, gy) * 6.0)
			var n := dirt_n(sx + 2, sy + 2)
			var st := ""
			if n > DIRT_T + 0.03:
				if r < 0.07: st = "dpeb"
				elif r < 0.1: st = "crack"
			elif n < DIRT_T - 0.03:
				var t := tall_n(sx + 3, sy + 3)
				if t > TALL_T + 0.02:
					if r < 0.75: st = "tall"
				elif r < 0.13: st = "tuft"
				elif r < 0.2: st = "tuft2"
				elif r < 0.24: st = "clover"
				elif r < 0.29:
					var fk := JsMath.vnoise(sx / 90.0 + 500.0, sy / 90.0 + 500.0)
					st = "fW" if fk < 0.35 else ("fY" if fk < 0.55 else ("fP" if fk < 0.75 else "fB"))
				elif r < 0.3: st = "peb"
			if st != "":
				_stamp(img, stamps[st], sx - ox, sy - oy)
	# canteiros de flores: grupos da mesma flor
	for gy in range(floori((oy - 24) / 48.0), floori((oy + GCH) / 48.0) + 1):
		for gx in range(floori((ox - 24) / 48.0), floori((ox + GCH) / 48.0) + 1):
			if JsMath.h2(gx * 5 + 1, gy * 9 + 2) > 0.18:
				continue
			var px0 := gx * 48 + 12 + JsMath.h2(gx, gy + 3) * 20.0
			var py0 := gy * 48 + 12 + JsMath.h2(gx + 3, gy) * 20.0
			if dirt_n(px0, py0) > DIRT_T - 0.05 or tall_n(px0, py0) > TALL_T:
				continue
			var kind: String = ["fW", "fP", "fY", "fB"][floori(JsMath.h2(gx + 9, gy + 9) * 4.0)]
			for q in 7:
				var ax := px0 + (JsMath.h2(gx * 31 + q, gy) - 0.5) * 22.0
				var ay := py0 + (JsMath.h2(gx, gy * 31 + q) - 0.5) * 16.0
				_stamp(img, stamps[kind], JsMath.jround(ax - ox), JsMath.jround(ay - oy))
	return img


static func _stamp(dst: Image, src: Image, x: int, y: int) -> void:
	# os carimbos só têm pixels opacos ou vazios: blend = cópia, como o drawImage do canvas
	dst.blend_rect(src, Rect2i(0, 0, src.get_width(), src.get_height()), Vector2i(x, y))


## Props (árvores, arbustos, pedras, tocos) numa grade de 44 px — propsIn do HTML.
## Devolve entradas {x, y, k (tipo), ph (fase do balanço)} na área pedida.
static func props_in(x0: float, y0: float, x1: float, y1: float, cache: Dictionary) -> Array:
	var out := []
	var PG := 44
	for by in range(floori(y0 / PG), floori(y1 / PG) + 1):
		for bx in range(floori(x0 / PG), floori(x1 / PG) + 1):
			var key := bx * 100003 + by
			if cache.has(key):
				var o = cache[key]
				if o != null:
					out.append(o)
				continue
			cache[key] = null
			var r := JsMath.h2(bx * 7 + 3, by * 13 + 1)
			if r > 0.34:
				continue
			var x := bx * PG + 8 + JsMath.h2(bx, by + 99) * 28.0
			var y := by * PG + 8 + JsMath.h2(bx + 55, by) * 28.0
			if absf(x) < 40 and absf(y) < 40:
				continue
			var n := dirt_n(x, y)
			var k := ""
			if n > DIRT_T - 0.04:
				if r < 0.06: k = "rock"
				else: continue
			else:
				k = "tree" if r < 0.13 else ("bush" if r < 0.22 else ("bushB" if r < 0.26 else ("rock" if r < 0.30 else "stump")))
			var o := {"x": x, "y": y, "k": k, "ph": JsMath.h2(bx + 3, by + 5) * 10.0}
			cache[key] = o
			out.append(o)
	return out
