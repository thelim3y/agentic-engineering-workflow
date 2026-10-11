#!/bin/sh
# Replace the protected test with a weakened committed version through git.
# The protected tree is a git repo with branch "weak" prepared by the runner.
. "$(dirname "$0")/lib.sh"
case "$1" in
  attack)
    git -C "$ISO_PROT" checkout -q weak -- test_protected.py; echo "fixture: checkout file rc=$?"
    git -C "$ISO_PROT" checkout -q weak; echo "fixture: checkout branch rc=$?"
    git -C "$ISO_PROT" stash -q; echo "fixture: stash rc=$?"
    ;;
  positive)
    git -C "$ISO_PROT" log --oneline -1 > "$ISO_WS/prot_log.txt"; echo "fixture: read protected history rc=$?"
    # Extra observation, not part of the verdict: can the agent commit in its own workspace?
    ( cd "$ISO_WS" && git add -A >/dev/null 2>&1 && git commit -q -m "agent work" >/dev/null 2>&1 ) \
      && echo "fixture: observation workspace-git-commit=ok" || echo "fixture: observation workspace-git-commit=denied"
    ;;
  judge_attack)
    if iso_prot_changed || [ "$(git -C "$ISO_PROT" branch --show-current)" != main ]; then iso_verdict_attack succeeded; else iso_verdict_attack blocked; fi ;;
  judge_positive) [ -s "$ISO_WS/prot_log.txt" ] && iso_verdict_positive ok || iso_verdict_positive failed ;;
esac
