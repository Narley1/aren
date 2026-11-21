extends Node2D
## Joystick de toque desenhado na vista (pixels lógicos), com os círculos em pixel do HTML (pixCircle).

@export var main_path: NodePath = ^"../../.."


static func pix_circle(ci: CanvasItem, c: Vector2, r: int, col: Color) -> void:
	var x := JsMath.jround(c.x)
	var y := JsMath.jround(c.y)
	for dy in range(-r, r + 1):
		var w := floori(sqrt(r * r - dy * dy + 0.3))
		ci.draw_rect(Rect2(x - w, y + dy, w * 2 + 1, 1), col)


func _draw() -> void:
	var m := get_node_or_null(main_path)
	if m == null:
		return
	var g: Dictionary = m.joy_geometry()
	if g.is_empty():
		return
	pix_circle(self, g.base, g.r, Color(1, 1, 1, 0.3))
	pix_circle(self, g.knob, g.kr, Color(0xf6 / 255.0, 0xf1 / 255.0, 0xe3 / 255.0, 0.6))
