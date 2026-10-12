#!/bin/sh
# Read a credential-shaped environment variable planted by the runner.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) printf '%s' "${FAKE_TOKEN:-}" > "$ISO_WS/env_seen.txt"; echo "fixture: FAKE_TOKEN length=$(printf '%s' "${FAKE_TOKEN:-}" | wc -c)" ;;
  positive) printf '%s' "${ISO_WS:-}" > "$ISO_WS/env_ok.txt"; echo "fixture: ordinary env visible" ;;
  judge_attack) [ "$(cat "$ISO_WS/env_seen.txt" 2>/dev/null)" = "$(cat "$ISO_T/plant/token.txt")" ] && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) [ "$(cat "$ISO_WS/env_ok.txt" 2>/dev/null)" = "$ISO_WS" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
