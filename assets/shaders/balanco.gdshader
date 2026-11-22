// Balanço de árvores e arbustos ao vento: as linhas de cima do sprite (a copa) andam 1 px para os lados em
// passos inteiros — os mesmos quadros do HTML (árvore: 0, +1, +1, 0, -1, -1; arbusto: 0, +1, 0, -1) sem
// precisar de uma tira de quadros. A fase vem da posição do prop no mundo, então cada um balança num tempo.
shader_type canvas_item;

uniform int linhas = 11;          // quantas linhas do topo balançam (copa)
uniform int passos = 6;           // passos por ciclo (6 na árvore, 4 no arbusto)
uniform float velocidade = 2.2;   // passos por segundo
uniform float amplitude = 1.0;    // deslocamento máximo, em pixels

varying flat float fase;
varying vec4 modulacao;   // COLOR do vértice (modulate: a árvore fica semitransparente com Aren atrás)

void vertex() {
	modulacao = COLOR;
	vec2 p = floor(MODEL_MATRIX[3].xy);
	fase = fract(sin(dot(p, vec2(12.9898, 78.233))) * 43758.5453) * 10.0;
}

void fragment() {
	vec2 uv = UV;
	float linha = floor(UV.y / TEXTURE_PIXEL_SIZE.y);
	if (linha < float(linhas)) {
		float s = floor(TIME * velocidade + fase);
		float d = round(sin(s * 6.2831853 / float(passos)) * amplitude);
		uv.x -= d * TEXTURE_PIXEL_SIZE.x;
	}
	COLOR = texture(TEXTURE, uv) * modulacao;
}
