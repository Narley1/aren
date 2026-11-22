// Rastro do golpe da espada: arco de pixels que cresce com o golpe (HTML: render(), "// sword swing").
// Desenhado num ColorRect em volta do ponto de giro; cada pixel decide sozinho se faz parte do arco.
shader_type canvas_item;

uniform vec4 cor_borda : source_color = vec4(0.373, 0.659, 0.941, 1.0);  // #5fa8f0
uniform vec4 cor_meio : source_color = vec4(0.749, 0.902, 1.0, 1.0);     // #bfe6ff
uniform vec4 cor_centro : source_color = vec4(1.0, 1.0, 1.0, 1.0);       // #ffffff
uniform float raio = 19.3;        // alcance da espada (px)
uniform float inicio = 0.0;       // ângulo onde o arco começa (a0)
uniform float abertura = 2.5;     // ângulo total com sinal (span: negativo = golpe ao contrário)
uniform float progresso = 0.0;    // 0..1, quanto do arco já foi varrido (pr)
uniform float desbotar = 1.0;     // 1 = opaco, 0 = sumiu (fade)
uniform vec2 tamanho = vec2(48.0);    // tamanho do ColorRect em px
uniform vec2 origem = vec2(-24.0);    // canto do ColorRect menos o ponto de giro (px, com fração)

void fragment() {
	vec2 d = floor(UV * tamanho) + origem;
	float r = length(d);
	float a = atan(d.y, d.x);
	float sg = abertura < 0.0 ? -1.0 : 1.0;
	float coberto = abs(abertura) * progresso;
	float da = mod((a - inicio) * sg, 6.2831853);
	COLOR = vec4(0.0);
	if (progresso > 0.0 && da <= coberto) {
		float qq = da / max(coberto, 1e-4);
		float th = 1.0 + floor(qq * (5.0 + raio * 0.12) + 0.5);
		float k = floor(raio - r + 0.5);
		if (k >= 0.0 && k < th) {
			float age = 1.0 - qq;
			vec4 col = k < 0.5 ? cor_borda : (k < max(2.0, th * 0.5) ? cor_centro : cor_meio);
			float al = desbotar * (1.0 - age * 0.85) * (k < 0.5 ? 1.0 : (k < 2.0 ? 0.9 : 0.55));
			COLOR = vec4(col.rgb, col.a * al);
		}
	}
}
