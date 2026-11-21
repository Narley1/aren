extends Node
## Autoload "Sfx": ponto único para os sons. Na Etapa 1 o jogo ainda não tem som; o código do jogo já chama
## Sfx.play("nome") nos mesmos momentos em que o HTML chama SFX.nome() (ver tools/sound_catalog.json no
## repositório HTML). Na Etapa 5 os efeitos serão exportados para WAV e tocados aqui.

var enabled := true
var music := true
## Registro das chamadas (usado pelos testes para conferir que os ganchos de som disparam).
var log: Array[String] = []


func play(name: String, _arg: Variant = null) -> void:
	if log.size() < 256:
		log.append(name)
