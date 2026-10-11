#!/bin/sh
# Contract fixture, not an attack. The runner passes a policy the adapter
# cannot honour (ISO_REQUIRE=tls-inspection, then ISO_NET=bogus). The adapter
# must exit 64 with an ISOLATION_UNSUPPORTED line and must not run this script.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack|positive) echo ran > "$ISO_WS/ran.txt"; echo "fixture: RAN DESPITE UNSUPPORTED CONFIG" ;;
  judge_attack|judge_positive) [ -e "$ISO_WS/ran.txt" ] && echo CONTRACT_VIOLATED || echo CONTRACT_HELD ;;
esac
