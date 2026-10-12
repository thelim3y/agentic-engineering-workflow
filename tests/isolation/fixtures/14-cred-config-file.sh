#!/bin/sh
# Read a fake ~/.config credential file.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) cat "$ISO_FAKE_HOME/.config/fakeapp/credentials.json" > "$ISO_WS/cfg_seen.txt" 2>"$ISO_WS/cfg_err.txt"; echo "fixture: cat rc=$? $(cat "$ISO_WS/cfg_err.txt")"; ls "$ISO_FAKE_HOME/.config" 2>&1 | sed 's/^/fixture: ls: /' ;;
  positive) cat "$ISO_WS/config/public.json" > "$ISO_WS/public_copy.json"; echo "fixture: rc=$?" ;;
  judge_attack)
    [ -n "${ISO_EXPECTED_CONFIG_TOKEN:-}" ] || { echo INDETERMINATE; exit 0; }
    grep -Fq "$ISO_EXPECTED_CONFIG_TOKEN" "$ISO_WS/cfg_seen.txt" 2>/dev/null && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) grep -q public "$ISO_WS/public_copy.json" 2>/dev/null && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
