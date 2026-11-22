// Anel de pixels (como o pixRing do HTML): usado na explosão de "subiu de nível".
shader_type canvas_item;

uniform vec4 cor : source_color = vec4(1.0, 0.886, 0.478, 1.0);   // #ffe27a
uniform float raio = 4.0;
uniform float espessura = 1.0;
uniform vec2 tamanho = vec2(64.0);

void fragment() {
	vec2 d = floor(UV * tamanho) - floor(tamanho * 0.5);
	float r = length(d);
	COLOR = abs(r - raio) <= espessura * 0.5 ? cor : vec4(0.0);
}
