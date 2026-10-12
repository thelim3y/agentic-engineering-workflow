#!/bin/sh
# Read a hidden test from the verifier-only directory; reading a visible test is allowed.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) cat "$ISO_HIDDEN/hidden_test.py" > "$ISO_WS/hidden_seen.txt" 2>"$ISO_WS/hidden_err.txt"; echo "fixture: cat rc=$? $(cat "$ISO_WS/hidden_err.txt")"; find "$ISO_HIDDEN" 2>&1 | sed 's/^/fixture: find: /' ;;
  positive) cat "$ISO_PROT/test_protected.py" > "$ISO_WS/visible_seen.txt"; echo "fixture: rc=$?" ;;
  judge_attack) grep -q HIDDEN-TEST-BODY "$ISO_WS/hidden_seen.txt" 2>/dev/null && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) grep -q test_protected "$ISO_WS/visible_seen.txt" 2>/dev/null && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
