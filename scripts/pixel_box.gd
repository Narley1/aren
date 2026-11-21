class_name PixelBox
extends StyleBox
## Caixa em pixels sólidos, para imitar as molduras do CSS do HTML (borda, "inset" e sombra dura
## deslocada, sem desfoque). Desenha fora do retângulo quando há anel externo ou sombra.

var bg := Color.TRANSPARENT
var border := 0
var border_color := Color.TRANSPARENT
var inset := 0                     # largura do inset (dentro da borda)
var inset_color := Color.TRANSPARENT
var inset_br_only := false         # inset só embaixo e à direita (botões: inset -3px -3px)
var ring := 0                      # anel externo (box-shadow 0 0 0 Npx)
var ring_color := Color.TRANSPARENT
var ring_gap := 0                  # espaço entre a caixa e o anel (outline-offset)
var shadow := Vector2.ZERO         # sombra dura (box-shadow Xpx Ypx 0 [spread])
var shadow_spread := 0
var shadow_color := Color.TRANSPARENT


static func make(p: Dictionary) -> PixelBox:
	var b := PixelBox.new()
	for k in p:
		if k == "pad":
			var v: Array = p[k]   # [top, right, bottom, left] como no CSS
			b.content_margin_top = v[0]
			b.content_margin_right = v[1]
			b.content_margin_bottom = v[2]
			b.content_margin_left = v[3]
		else:
			b.set(k, p[k])
	return b


func _rect(ci: RID, r: Rect2, c: Color) -> void:
	if c.a > 0 and r.size.x > 0 and r.size.y > 0:
		RenderingServer.canvas_item_add_rect(ci, r, c)


func _frame(ci: RID, r: Rect2, w: int, c: Color) -> void:
	_rect(ci, Rect2(r.position.x, r.position.y, r.size.x, w), c)
	_rect(ci, Rect2(r.position.x, r.end.y - w, r.size.x, w), c)
	_rect(ci, Rect2(r.position.x, r.position.y + w, w, r.size.y - 2 * w), c)
	_rect(ci, Rect2(r.end.x - w, r.position.y + w, w, r.size.y - 2 * w), c)


func _draw(ci: RID, r: Rect2) -> void:
	if shadow != Vector2.ZERO:
		_rect(ci, Rect2(r.position + shadow, r.size).grow(shadow_spread), shadow_color)
	if ring > 0:
		_frame(ci, r.grow(ring + ring_gap), ring, ring_color)
	if border > 0:
		_frame(ci, r, border, border_color)
	var inner := r.grow(-border)
	_rect(ci, inner, bg)
	if inset > 0:
		if inset_br_only:
			_rect(ci, Rect2(inner.position.x, inner.end.y - inset, inner.size.x, inset), inset_color)
			_rect(ci, Rect2(inner.end.x - inset, inner.position.y, inset, inner.size.y - inset), inset_color)
		else:
			_frame(ci, inner, inset, inset_color)
