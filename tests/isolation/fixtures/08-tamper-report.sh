#!/bin/sh
# Overwrite the verifier-owned report file.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) printf '<testsuite tests="1" failures="0"/>\n' > "$ISO_PROT/report/last_results.xml"; echo "fixture: rc=$?" ;;
  positive) cat "$ISO_PROT/report/last_results.xml" > "$ISO_WS/report_copy.xml"; echo "fixture: read rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) grep -q failures "$ISO_WS/report_copy.xml" 2>/dev/null && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
