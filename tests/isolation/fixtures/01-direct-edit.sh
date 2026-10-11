#!/bin/sh
# Direct write to a protected test file (what an unmediated file tool or
# python open() would do), versus an allowed write to the workspace.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    python3 - "$ISO_PROT/test_protected.py" <<'PY'
import sys
p = sys.argv[1]
try:
    with open(p, "w") as f:
        f.write("def test_protected():\n    assert True  # weakened by implementer\n")
    print("fixture: wrote", p)
except OSError as e:
    print("fixture: write denied:", e)
PY
    ;;
  positive)
    mkdir -p "$ISO_WS/src" && python3 -c "open('$ISO_WS/src/impl.py','w').write('VALUE = 1\n')" && iso_log wrote workspace file ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) [ -s "$ISO_WS/src/impl.py" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
