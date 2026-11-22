// Clarão ao levar dano e contorno dourado do elite, num shader só (antes eram PNGs separados).
// Parâmetros por instância (cada inimigo tem os seus, o material é um só e o Godot continua agrupando o desenho):
//   clarao   0 = normal, 1 = silhueta na cor_clarao (o "_flash" do HTML, EFrame.w)
//   contorno 0 = sem, 1 = contorno de 1 px na cor_contorno em volta da silhueta (o elite, EFrame.g nos 4 lados)
// Os quadros do goblin têm 1 px de borda transparente (exportador, pad: 1) para caber o contorno.
shader_type canvas_item;

instance uniform float clarao = 0.0;
instance uniform float contorno = 0.0;
uniform vec4 cor_clarao : source_color = vec4(1.0, 1.0, 1.0, 1.0);
uniform vec4 cor_contorno : source_color = vec4(1.0, 0.851, 0.29, 1.0);

varying vec4 modulacao;   // COLOR do vértice (modulate)

void vertex() {
	modulacao = COLOR;
}

void fragment() {
	vec4 c = texture(TEXTURE, UV);
	if (c.a > 0.0) {
		COLOR = mix(c, vec4(cor_clarao.rgb, c.a), step(0.5, clarao)) * modulacao;
	} else if (contorno > 0.5) {
		vec2 px = TEXTURE_PIXEL_SIZE;
		float n = texture(TEXTURE, UV + vec2(px.x, 0.0)).a + texture(TEXTURE, UV - vec2(px.x, 0.0)).a
			+ texture(TEXTURE, UV + vec2(0.0, px.y)).a + texture(TEXTURE, UV - vec2(0.0, px.y)).a;
		COLOR = n > 0.0 ? vec4(cor_contorno.rgb, cor_contorno.a * modulacao.a) : vec4(0.0);
	} else {
		COLOR = vec4(0.0);
	}
}
