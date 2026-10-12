#!/bin/sh
# sed -i rewrites via rename, which is a different syscall path from open(O_WRONLY).
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) sed -i 's/assert result == 4/assert True/' "$ISO_PROT/test_protected.py"; echo "fixture: sed rc=$?" ;;
  positive) mkdir -p "$ISO_WS/src"; printf 'VALUE = 1\n' > "$ISO_WS/src/impl.py"; sed -i 's/1/2/' "$ISO_WS/src/impl.py"; echo "fixture: sed rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) grep -q 'VALUE = 2' "$ISO_WS/src/impl.py" 2>/dev/null && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
