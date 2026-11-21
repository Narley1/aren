class_name JsMath
## Funções que reproduzem exatamente a aritmética do jogo HTML (JavaScript), para que o chão, as posições
## dos props e o arredondamento dos sprites saiam iguais pixel por pixel.

const M32 := 0xFFFFFFFF


## Math.imul(a, b) como padrão de 32 bits sem sinal (o mesmo padrão de bits do resultado do JS).
static func imul(a: int, b: int) -> int:
	a &= M32
	b &= M32
	var lo := (a * (b & 0xFFFF)) & M32
	var hi := ((a * (b >> 16)) & 0xFFFF) << 16
	return (lo + hi) & M32


## h2(x, y) do HTML (seção "ground"): hash inteiro -> [0, 1).
static func h2(x: int, y: int) -> float:
	var n := (imul(x, 374761393) + imul(y, 668265263)) & M32
	n = imul(n ^ (n >> 13), 1274126177)
	return float((n ^ (n >> 16)) & M32) / 4294967296.0


## Math.round do JS: metade arredonda para +infinito (o round() do Godot arredonda para longe do zero).
static func jround(v: float) -> int:
	return floori(v + 0.5)


## vnoise(x, y) do HTML: ruído de valor com interpolação suave.
static func vnoise(x: float, y: float) -> float:
	var xi := floorf(x)
	var yi := floorf(y)
	var xf := x - xi
	var yf := y - yi
	var u := xf * xf * (3.0 - 2.0 * xf)
	var v := yf * yf * (3.0 - 2.0 * yf)
	var ix := int(xi)
	var iy := int(yi)
	var a := h2(ix, iy)
	var b := h2(ix + 1, iy)
	var c := h2(ix, iy + 1)
	var d := h2(ix + 1, iy + 1)
	return a + (b - a) * u + (c - a) * v + (a - b - c + d) * u * v
