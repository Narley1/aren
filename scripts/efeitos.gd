extends Node2D
## Camada de efeitos por cima das criaturas. Recebe os eventos que a simulação deixou em game.fx_events
## (golpe, morte, joia, nível) e instancia a cena de cada efeito. As cenas se apagam sozinhas.

@export var cena_numero: PackedScene = preload("res://scenes/efeitos/numero_dano.tscn")
@export var cena_faisca: PackedScene = preload("res://scenes/efeitos/faisca.tscn")
@export var cena_morte: PackedScene = preload("res://scenes/efeitos/poeira_morte.tscn")
@export var cena_joia: PackedScene = preload("res://scenes/efeitos/brilho_joia.tscn")
@export var cena_nivel: PackedScene = preload("res://scenes/efeitos/subiu_nivel.tscn")
@export var max_efeitos := 300    ## limite de efeitos vivos ao mesmo tempo (os novos são ignorados acima disso)
@export var morte_grande := 10    ## partículas na morte de inimigo grande (sc > 1); o comum usa o da cena

@onready var golpe: Node2D = $GolpeEspada


func play(ev: Dictionary) -> void:
	if get_child_count() > max_efeitos:
		return
	match ev.k:
		"hit":
			var n: Node2D = cena_numero.instantiate()
			n.position = Vector2(JsMath.jround(ev.x), JsMath.jround(ev.y))
			add_child(n)
			n.mostrar(ev.v, ev.forte)
			_add(cena_faisca, ev.fx, ev.fy)
		"kill":
			var p: CPUParticles2D = _make(cena_morte, ev.x, ev.y)
			if ev.grande:
				p.amount = morte_grande
			add_child(p)
		"gem":
			var p: CPUParticles2D = _make(cena_joia, ev.x, ev.y)
			p.color = ev.cor
			add_child(p)
		"level":
			_add(cena_nivel, ev.x, ev.y)


func _make(cena: PackedScene, x: float, y: float) -> Node2D:
	var n: Node2D = cena.instantiate()
	n.position = Vector2(JsMath.jround(x), JsMath.jround(y))
	return n


func _add(cena: PackedScene, x: float, y: float) -> void:
	add_child(_make(cena, x, y))


## Efeitos vivos (sem contar o golpe da espada)
func vivos() -> int:
	return get_child_count() - 1
