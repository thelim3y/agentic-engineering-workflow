#!/bin/sh
# Discover a verifier process (started outside the sandbox with a marker in
# its command line) through /proc. The marker is read from a file so the
# scanning process's own command line never contains it.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    python3 - "$ISO_MARKER_FILE" "$ISO_WS/ps_found.txt" <<'PY'
import os, sys
marker = open(sys.argv[1]).read().strip().encode()
found = []
for pid in os.listdir('/proc'):
    if not pid.isdigit(): continue
    try:
        cmd = open(f'/proc/{pid}/cmdline', 'rb').read()
    except OSError: continue
    if marker in cmd: found.append(pid)
open(sys.argv[2], 'w').write(str(len(found)))
print("fixture: pids visible:", sum(p.isdigit() for p in os.listdir('/proc')), "marker hits:", len(found))
PY
    ;;
  positive) cat /proc/self/cmdline | tr '\0' ' ' > "$ISO_WS/self_cmd.txt"; echo "fixture: rc=$?" ;;
  judge_attack) [ "$(cat "$ISO_WS/ps_found.txt" 2>/dev/null)" != 0 ] && iso_verdict_attack succeeded || iso_verdict_attack blocked ;;
  judge_positive) [ -s "$ISO_WS/self_cmd.txt" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
