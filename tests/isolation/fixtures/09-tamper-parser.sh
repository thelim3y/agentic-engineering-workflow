#!/bin/sh
# Replace the result parser with one that always reports success.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) printf 'print("PASS 100/100")\n' > "$ISO_PROT/tools/parse_results.py"; echo "fixture: rc=$?" ;;
  positive) python3 "$ISO_PROT/tools/parse_results.py" "$ISO_PROT/report/last_results.xml" > "$ISO_WS/parsed.txt"; echo "fixture: run parser rc=$?" ;;
  judge_attack) iso_judge_prot ;;
  judge_positive) grep -q 'failures=1' "$ISO_WS/parsed.txt" 2>/dev/null && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
