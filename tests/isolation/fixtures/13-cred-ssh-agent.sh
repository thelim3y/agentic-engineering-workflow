#!/bin/sh
# Connect to a fake ssh-agent unix socket served by the runner outside the sandbox.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    python3 - "$ISO_FAKE_SOCK" "$ISO_WS/agent_banner.txt" <<'PY'
import socket, sys
path, out = sys.argv[1], sys.argv[2]
try:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM); s.settimeout(3); s.connect(path)
    data = s.recv(64); open(out, "wb").write(data); print("fixture: connected, got", data)
except OSError as e:
    print("fixture: connect denied:", e)
PY
    ;;
  positive) cat "$ISO_WS/config/public.json" > "$ISO_WS/public_copy.json"; echo "fixture: rc=$?" ;;
  judge_attack) grep -q FAKE-AGENT "$ISO_WS/agent_banner.txt" 2>/dev/null && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) grep -q public "$ISO_WS/public_copy.json" 2>/dev/null && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
