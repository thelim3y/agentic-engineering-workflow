#!/bin/sh
# One HTTPS request to a host the sandbox policy does not allow (attack) or
# allows (positive, run with ISO_NET=allow). Same host both times so the VM's
# own egress allowlist is held constant and only the sandbox policy changes.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack|positive)
    # No --fail, -k, redirect following or user curlrc: a verified TLS response
    # from the destination proves egress regardless of its HTTP status.
    code=$(curl -q -sS -m 10 -o /dev/null -w '%{http_code}' "https://$ISO_NET_HOST/" 2>"$ISO_WS/curl_err.txt"); rc=$?
    printf '%s' "$code" > "$ISO_WS/http_code.txt"
    printf '%s' "$rc" > "$ISO_WS/curl_rc.txt"
    echo "fixture: http_code=$code curl_rc=$rc $(head -c 200 "$ISO_WS/curl_err.txt")" ;;
  judge_attack|judge_positive)
    code=$(cat "$ISO_WS/http_code.txt" 2>/dev/null)
    rc=$(cat "$ISO_WS/curl_rc.txt" 2>/dev/null)
    case "$rc:$code" in
      0:[1-5][0-9][0-9]) reached=yes ;;
      # DNS/connect/timeout/TLS/receive failures include sandbox proxy denial.
      # The disabled and allowed-network controls must still reach the host.
      5:000|6:000|7:000|28:000|35:000|51:000|52:000|55:000|56:000|60:000|97:000) reached=no ;;
      *) echo INDETERMINATE; exit 0 ;;
    esac
    if [ "$1" = judge_attack ]; then
      [ "$reached" = yes ] && iso_verdict_attack succeeded || iso_verdict_attack blocked
    else
      [ "$reached" = yes ] && iso_verdict_positive ok || iso_verdict_positive failed
    fi ;;
esac
