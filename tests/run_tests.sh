#!/usr/bin/env bash
# Roda os testes da Etapa 1 sem janela e falha também se o log tiver qualquer erro do Godot.
#   GODOT=/caminho/Godot_v4.7.2-stable_linux.x86_64 tests/run_tests.sh
set -u
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
LOG="$(mktemp)"
"$GODOT" --headless --path . --import >/dev/null 2>&1
"$GODOT" --headless --path . res://tests/run_tests.tscn 2>&1 | tee "$LOG"
code=${PIPESTATUS[0]}
if grep -E "SCRIPT ERROR|^ERROR:|Parse Error" "$LOG" >/dev/null; then
  echo "FAIL  o log do Godot tem erros (veja acima)"
  code=1
fi
rm -f "$LOG"
exit $code
