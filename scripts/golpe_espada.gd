extends Node2D
## Golpe da espada (visual). A simulação (game.gd) decide quando golpeia e quem acerta; esta cena só mostra:
##   - Arco: rastro de pixels que cresce com o golpe (ColorRect com o shader assets/shaders/arco.gdshader)
##   - Lamina: AnimatedSprite2D com as 48 rotações exportadas do HTML (assets/sprites/espada.tres, "girar").
##     As rotações ficam como quadros, e não como rotação livre do Sprite2D, porque são os pixels exatos do HTML
##     (girar um sprite pequeno em tempo real faz os pixels "dançarem" e muda o desenho a cada ângulo).
##   - Faiscas: CPUParticles2D na ponta da lâmina, ligado só no meio do golpe (trilha da animação).
##   - AnimationPlayer "golpe" (1 s = o golpe inteiro): trilha `progresso` 0 -> 1 e trilha das faíscas.
##     O jogo não "toca" a animação: a cada quadro ele posiciona a animação no ponto do golpe da simulação
##     (seek), então pausa, capturas e testes ficam sempre em sincronia com a partida.

const N_ROT := 48

## 0..1 dentro do golpe (escrito pela animação "golpe")
@export var progresso := 0.0:
	set(v):
		progresso = v
		_pose()

@onready var arco: ColorRect = $Arco
@onready var lamina: AnimatedSprite2D = $Lamina
@onready var faiscas: CPUParticles2D = $Faiscas
@onready var anim: AnimationPlayer = $AnimationPlayer

var _s = null                 # golpe atual da simulação {t, dur, ang, arc, range, dirs, rev}
var _pivo := Vector2.ZERO     # ponto de giro no mundo (Aren: x, y - 9), com fração
var _raio_lamina := 22        # R das rotações (metade do quadro)


func _ready() -> void:
	visible = false
	var m: Dictionary = Art.meta.get("sword", {})
	_raio_lamina = int(m.get("R", 22))


## Mostra o golpe `s` (ou esconde, se null) com o ponto de giro `pivo`.
func mostrar(s, pivo: Vector2) -> void:
	_s = s
	_pivo = pivo
	if s == null:
		if visible:
			visible = false
			faiscas.emitting = false
		return
	visible = true
	if anim.assigned_animation != "golpe":
		anim.assigned_animation = "golpe"
	anim.seek(clampf(s.t / s.dur, 0.0, 1.0), true)
	_pose()   # (a trilha já chama, mas garante a pose mesmo se o valor não mudou)


## Ângulo atual da lâmina no golpe (render() do HTML, "// sword swing")
static func swing_pose(s: Dictionary, dir: float) -> Dictionary:
	var T: float = s.t / s.dur
	var wind := 0.16
	var q := (T - wind) / (0.7 - wind)
	var pr := 0.0 if T < wind else minf(1.0, 1.0 - pow(1.0 - q, 3))
	var fade := 1.0 if T < 0.7 else maxf(0.0, 1.0 - (T - 0.7) / 0.3)
	var sg := -1.0 if s.rev else 1.0
	var a0: float = dir - sg * s.arc / 2.0
	var span: float = s.arc * sg
	var cur := (a0 - sg * 0.35 * (T / wind)) if T < wind else (a0 + span * pr)
	return {"T": T, "pr": pr, "fade": fade, "sg": sg, "a0": a0, "span": span, "cur": cur}


func _pose() -> void:
	if _s == null or not is_node_ready():
		return
	# (Etapa 1: só a primeira direção; o golpe duplo da espada nível alto chega na Etapa 2)
	var q := swing_pose(_s, _s.dirs[0])
	position = Vector2(JsMath.jround(_pivo.x), JsMath.jround(_pivo.y))
	# arco
	var R: float = _s.range
	var half := ceili(R) + 3
	arco.size = Vector2(half * 2, half * 2)
	arco.position = Vector2(-half, -half)
	var mat := arco.material as ShaderMaterial
	mat.set_shader_parameter("raio", R)
	mat.set_shader_parameter("inicio", q.a0)
	mat.set_shader_parameter("abertura", q.span)
	mat.set_shader_parameter("progresso", q.pr if q.T >= 0.16 else 0.0)
	mat.set_shader_parameter("desbotar", q.fade)
	mat.set_shader_parameter("tamanho", arco.size)
	mat.set_shader_parameter("origem", position + arco.position - _pivo)
	# lâmina: quadro k = ângulo k/48 de volta, desenhada em round(hx - R), round(hy - R) (drawSword)
	var cur: float = q.cur
	var hx := _pivo.x + cos(cur) * 4
	var hy := _pivo.y + sin(cur) * 4
	lamina.frame = posmod(JsMath.jround(cur / TAU * N_ROT), N_ROT)
	lamina.position = Vector2(JsMath.jround(hx - _raio_lamina), JsMath.jround(hy - _raio_lamina)) - position
	lamina.modulate.a = minf(1.0, q.fade * 1.5)
	# faíscas na ponta, saindo de lado (HTML: swing sparks, 30 px/s na tangente)
	var tr := minf(R, 22.0)
	faiscas.position = Vector2(cos(cur), sin(cur)) * tr + (_pivo - position)
	faiscas.direction = Vector2(cos(cur + q.sg * PI / 2), sin(cur + q.sg * PI / 2))
