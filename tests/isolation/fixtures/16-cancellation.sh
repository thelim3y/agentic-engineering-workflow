#!/bin/sh
# The runner kills this process group about 1.5 s after start. A detached
# child tries to write after that. Attack succeeds if anything survives the
# cancellation and writes late. Positive: a normal short run completes.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    setsid sh -c "sleep 4; echo late > '$ISO_WS/late.txt'; echo late > '$ISO_EVIDENCE/late.txt'" >/dev/null 2>&1 </dev/null &
    echo "fixture: detached writer started, now blocking"; sleep 30 ;;
  positive) echo done > "$ISO_WS/done.txt"; echo "fixture: completed normally" ;;
  judge_attack) { [ -e "$ISO_WS/late.txt" ] || [ -e "$ISO_EVIDENCE/late.txt" ]; } && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) [ -s "$ISO_WS/done.txt" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
