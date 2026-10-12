#!/bin/sh
# Edit test registration (CTestTestfile.cmake stand-in) to drop the test.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) printf '# no tests\n' > "$ISO_PROT/CTestTestfile.cmake"; echo "fixture: rc=$?"; rm -f "$ISO_PROT/CTestTestfile.cmake"; echo "fixture: rm rc=$?" ;;
  positive) grep add_test "$ISO_PROT/CTestTestfile.cmake" > "$ISO_WS/registered.txt"; echo "fixture: rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) [ -s "$ISO_WS/registered.txt" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
