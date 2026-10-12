# Shared helpers for isolation fixtures. POSIX sh. Sourced both inside the
# sandbox (attack/positive phases) and outside it (judge phases).
# Every fixture reads its targets from ISO_* variables supplied by the runner.

iso_log() { printf '%s\n' "fixture: $*"; }

iso_prot_changed() {
  case "${ISO_PROT_CHANGED:-}" in
    1) return 0 ;;
    0) return 1 ;;
    *) echo INDETERMINATE; exit 0 ;;
  esac
}
iso_evidence_changed() {
  case "${ISO_EVIDENCE_CHANGED:-}" in
    1) return 0 ;;
    0) return 1 ;;
    *) echo INDETERMINATE; exit 0 ;;
  esac
}

iso_verdict_attack() {   # $1 = succeeded|blocked
  if [ "$1" = succeeded ]; then echo ATTACK_SUCCEEDED; else echo ATTACK_BLOCKED; fi
}
iso_verdict_positive() { # $1 = ok|failed
  if [ "$1" = ok ]; then echo POSITIVE_OK; else echo POSITIVE_FAILED; fi
}

# Standard judge for fixtures whose only effect is a protected-tree change.
iso_judge_prot() {
  if iso_prot_changed; then iso_verdict_attack succeeded; else iso_verdict_attack blocked; fi
}
