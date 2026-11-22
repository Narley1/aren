// Shader do chão (TileMapLayer "Chao"). Os tiles são pintados com três cores "marcadoras" (a grama base,
// a terra base e o capim alto base); aqui elas viram as manchas e listras do chão do HTML usando a posição
// do pixel no mundo — por isso as manchas atravessam os tiles sem emenda. Os outros pixels (bordas,
// pontinhos, tufos) passam como estão.
shader_type canvas_item;

// cores marcadoras pintadas nos tiles (tools/make_tileset.py): não mudar sem refazer o atlas
const vec3 MARCA_GRAMA = vec3(0.447, 0.8, 0.322);    // #72cc52
const vec3 MARCA_TERRA = vec3(0.902, 0.784, 0.565);  // #e6c890
const vec3 MARCA_CAPIM = vec3(0.31, 0.659, 0.251);   // #4fa840

uniform vec4 grama_clara : source_color = vec4(0.447, 0.8, 0.322, 1.0);    // g1
uniform vec4 grama_escura : source_color = vec4(0.392, 0.737, 0.282, 1.0); // g2
uniform float grama_limite = 0.52;      // manchas: acima do limite = grama clara (HTML: m > .52)
uniform sampler2D grama_manchas : repeat_enable, filter_nearest;

uniform vec4 terra_clara : source_color = vec4(0.902, 0.784, 0.565, 1.0);  // d1
uniform vec4 terra_escura : source_color = vec4(0.847, 0.706, 0.478, 1.0); // d2
uniform float terra_limite = 0.6;
uniform sampler2D terra_manchas : repeat_enable, filter_nearest;

uniform vec4 capim_1 : source_color = vec4(0.31, 0.659, 0.251, 1.0);   // t1
uniform vec4 capim_2 : source_color = vec4(0.361, 0.714, 0.275, 1.0);  // t2
uniform vec4 capim_escuro : source_color = vec4(0.227, 0.541, 0.212, 1.0); // tD

varying vec2 mundo;
varying vec4 modulacao;   // COLOR do vértice (modulate); no fragment COLOR já vem multiplicado pela textura

void vertex() {
	mundo = (MODEL_MATRIX * vec4(VERTEX, 0.0, 1.0)).xy;
	modulacao = COLOR;
}

float h2(ivec2 p) {
	uint n = uint(p.x) * 374761393u + uint(p.y) * 668265263u;
	n = (n ^ (n >> 13u)) * 1274126177u;
	return float(n ^ (n >> 16u)) / 4294967296.0;
}

bool igual(vec3 a, vec3 b) {
	return all(lessThan(abs(a - b), vec3(0.004)));
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	ivec2 p = ivec2(floor(mundo));
	if (igual(c.rgb, MARCA_GRAMA)) {
		vec2 tam = vec2(textureSize(grama_manchas, 0));
		float m = texture(grama_manchas, (vec2(p) + 0.5) / tam).r + (h2(p * 3 + 11) - 0.5) * 0.08;
		c.rgb = m > grama_limite ? grama_clara.rgb : grama_escura.rgb;
	} else if (igual(c.rgb, MARCA_TERRA)) {
		vec2 tam = vec2(textureSize(terra_manchas, 0));
		float m = texture(terra_manchas, (vec2(p) + 0.5) / tam).r + (h2(p * 5 + 3) - 0.5) * 0.12;
		c.rgb = m > terra_limite ? terra_escura.rgb : terra_clara.rgb;
	} else if (igual(c.rgb, MARCA_CAPIM)) {
		// listras do capim alto (HTML: (wx + (wy >> 1) * 2) % 5)
		int s = ((p.x + (p.y >> 1) * 2) % 5 + 5) % 5;
		c.rgb = s == 0 ? capim_escuro.rgb : (s == 2 ? capim_2.rgb : capim_1.rgb);
	}
	COLOR = c * modulacao;
}
