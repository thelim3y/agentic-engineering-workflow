#!/bin/sh
# Shell redirection onto a protected test file.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) echo "assert True" > "$ISO_PROT/test_protected.py"; echo "fixture: redirect rc=$?" ;;
  positive) echo "hello" > "$ISO_WS/out.txt"; echo "fixture: redirect rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) [ "$(cat "$ISO_WS/out.txt" 2>/dev/null)" = hello ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
