extends Node2D
## Número de dano: sobe 18 px/s por 0,6 s e some (HTML: nums, drawNum). Os dígitos 3x5 são uma fonte de imagem
## (assets/font/digitos.png) com a sombra escura de 1 px do próprio Label.

@export var subida := 18.0       ## px por segundo
@export var duracao := 0.6       ## segundos
@export var cor_forte := Color("#ffd94a")   ## golpes de 15 ou mais

@onready var texto: Label = $Texto


## v = dano já arredondado; forte = dano >= 15 (amarelo)
func mostrar(v: int, forte: bool) -> void:
	texto.text = str(v)
	texto.position = Vector2(-texto.text.length() * 2, 0)   # HTML: x - s.length*2
	if forte:
		texto.add_theme_color_override("font_color", cor_forte)
	var tw := create_tween()
	tw.tween_property(self, "position:y", position.y - subida * duracao, duracao)
	tw.tween_callback(queue_free)
