#!/usr/bin/env bash
# Capturas de tela da versão Godot (início, partida com goblins, pausa, fim de jogo) em 390x844 e 1366x768,
# com o renderizador Compatibility em OpenGL por software (xvfb). Uso:
#   GODOT=/caminho/Godot_v4.7.2-stable_linux.x86_64 tools/shots.sh /pasta/de/saida
set -eu
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
OUT="${1:-/tmp/aren-shots}"
mkdir -p "$OUT"
for r in 390x844 1366x768; do
  xvfb-run -a -s "-screen 0 1400x900x24" "$GODOT" --path . --rendering-driver opengl3 --audio-driver Dummy \
    --resolution "$r" --position 0,0 -- --shots="$OUT"
done
