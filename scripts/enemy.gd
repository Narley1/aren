extends Node2D
## Inimigo comum (Etapa 1: goblin). Campos com os nomes do objeto de inimigo do HTML (E[]):
## type, x, y, hp, kx/ky (empurrão), flash, anim, elite, face, dead.
## Visual: AnimatedSprite2D com o SpriteFrames do tipo (assets/sprites/goblin.tres); o clarão ao levar dano e
## o contorno dourado do elite são parâmetros do shader assets/shaders/inimigo.gdshader (por instância).

## Nome da direção no SpriteFrames: "left" usa "lado" espelhado (flip_h)
const DIR_ANIM := {"down": "baixo", "up": "cima", "side": "lado", "left": "lado"}

var type := "goblin"
var d: Dictionary            # Bal.ET[type] + w, h do sprite (sem a borda do contorno)
var ex := 0.0
var ey := 0.0
var hp := 0.0
var kx := 0.0
var ky := 0.0
var flash := 0.0
var anim := 0.0
var elite := false
var face := "down"
var dead := false

@onready var sprite: AnimatedSprite2D = $Sprite


func setup(t: String, x: float, y: float, hp_mul: float, is_elite: bool, anim0: float) -> void:
	type = t
	d = Bal.ET[t].duplicate()
	var m: Dictionary = Art.meta[t + "_down"]
	var pad := int(m.get("pad", 0))
	d.w = int(m.w) - 2 * pad
	d.h = int(m.h) - 2 * pad
	ex = x
	ey = y
	elite = is_elite
	hp = d.hp * hp_mul
	anim = anim0
	sprite.set_instance_shader_parameter("contorno", 1.0 if elite else 0.0)
	sprite.play("andar_baixo")
	sprite.set_frame_and_progress(absi(floori(anim0)) % 4, fmod(anim0, 1.0))


func update_visual() -> void:
	var want: String = "andar_" + DIR_ANIM[face]
	if sprite.animation != want:
		var f := sprite.frame
		var pr := sprite.frame_progress
		sprite.play(want)
		sprite.set_frame_and_progress(f, pr)
	sprite.flip_h = face == "left"
	# quadros por segundo = velocidade/6 (HTML: e.anim += dt*spd/6); o SpriteFrames tem os do goblin comum
	var sp: float = d.spd * (Bal.ELITE.spd if elite else 1.0)
	sprite.speed_scale = (sp / 6.0) / sprite.sprite_frames.get_animation_speed(want)
	# HTML: x = round(e.x - w/2 - cx), y = round(e.y - h - cy + 1); nó no pé (chave do y-sort)
	position = Vector2(JsMath.jround(ex), JsMath.jround(ey))
	sprite.set_instance_shader_parameter("clarao", 1.0 if flash > 0 else 0.0)
