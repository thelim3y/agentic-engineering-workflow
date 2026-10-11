#!/bin/sh
# One HTTPS request to a host the sandbox policy does not allow (attack) or
# allows (positive, run with ISO_NET=allow). Same host both times so the VM's
# own egress allowlist is held constant and only the sandbox policy changes.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack|positive)
    code=$(curl -sS -m 10 -o /dev/null -w '%{http_code}' "https://$ISO_NET_HOST/" 2>"$ISO_WS/curl_err.txt"); rc=$?
    printf '%s' "$code" > "$ISO_WS/http_code.txt"; echo "fixture: http_code=$code curl_rc=$rc $(head -c 200 "$ISO_WS/curl_err.txt")" ;;
  judge_attack) [ "$(cat "$ISO_WS/http_code.txt" 2>/dev/null)" = 200 ] && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) [ "$(cat "$ISO_WS/http_code.txt" 2>/dev/null)" = 200 ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
