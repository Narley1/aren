extends CPUParticles2D
## Partículas que disparam uma vez quando a cena entra no jogo e se apagam sozinhas ao terminar.
## Usado pelas cenas de efeito (poeira da morte, faísca, brilho da joia). Quantidade, cores, velocidade e
## duração ficam no próprio CPUParticles2D (inspetor).


func _ready() -> void:
	one_shot = true
	finished.connect(queue_free)
	restart()
