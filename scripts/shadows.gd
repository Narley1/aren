extends Node2D
## Todas as sombras, desenhadas antes das criaturas e dos props (como no HTML, "shadows first").

var game: Node2D


func _draw() -> void:
	if game == null:
		return
	for o in game.ground.visible_props:
		var sh: int = Art.meta["prop_" + o.k].sh
		draw_texture(Art.tex("shadow_%d" % sh), Vector2(JsMath.jround(o.x - sh / 2.0), JsMath.jround(o.y - 3)))
	for e in game.enemies:
		var w: int = maxi(4, JsMath.jround(e.d.w * 0.75))
		draw_texture(Art.tex("shadow_%d" % w), Vector2(JsMath.jround(e.ex - e.d.w * 0.75 / 2.0), JsMath.jround(e.ey - 2)))
	var p: Node2D = game.player
	draw_texture(Art.tex("shadow_12"), Vector2(JsMath.jround(p.px - 6), JsMath.jround(p.py - 3)))
