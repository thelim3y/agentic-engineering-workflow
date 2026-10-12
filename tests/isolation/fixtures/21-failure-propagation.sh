#!/bin/sh
# Contract fixture, not an attack. A failing command inside the sandbox must
# surface as the same non-zero exit status to the runner, with the control on
# and off. A sandbox that swallows exit codes would let a failed verification
# look like success.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack) echo "fixture: failing on purpose with exit 23"; exit 23 ;;
  positive) echo "fixture: succeeding"; exit 0 ;;
  judge_attack|judge_positive) echo "EXIT_CODE_IS_JUDGED_BY_RUNNER" ;;
esac
