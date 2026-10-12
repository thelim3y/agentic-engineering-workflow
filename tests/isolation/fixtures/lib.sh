# Shared helpers for isolation fixtures. POSIX sh. Sourced both inside the
# sandbox (attack/positive phases) and outside it (judge phases).
# Every fixture reads its targets from ISO_* variables supplied by the runner.

iso_log() { printf '%s\n' "fixture: $*"; }

# Hash of every regular file under a directory, excluding .git internals.
iso_tree_hash() {
  ( cd "$1" 2>/dev/null && find . -type f -not -path './.git/*' -print0 \
      | sort -z | xargs -0 sha256sum 2>/dev/null ) | sha256sum | cut -c1-64
}

# Baseline hashes are written by the runner before each phase.
iso_prot_changed() {
  [ "$(iso_tree_hash "$ISO_PROT")" != "$(cat "$ISO_T/baseline/prot.sha256")" ]
}
iso_evidence_changed() {
  [ "$(iso_tree_hash "$ISO_EVIDENCE")" != "$(cat "$ISO_T/baseline/evidence.sha256")" ]
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
