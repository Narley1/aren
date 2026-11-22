class_name JsMath
## Aritmética do JavaScript que o jogo precisa para arredondar igual ao HTML.


## Math.round do JS: metade arredonda para +infinito (o round() do Godot arredonda para longe do zero).
static func jround(v: float) -> int:
	return floori(v + 0.5)
