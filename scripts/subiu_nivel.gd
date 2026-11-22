extends Node2D
## Explosão de "subiu de nível" em volta de Aren: três anéis de pixels (shader anel.gdshader) e um brilho
## dourado. A animação "explodir" do AnimationPlayer controla os anéis; a cena se apaga quando ela termina.

@onready var anim: AnimationPlayer = $AnimationPlayer


func _ready() -> void:
	anim.animation_finished.connect(func(_n): queue_free())
	anim.play("explodir")
