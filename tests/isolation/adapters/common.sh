# Shared adapter plumbing. POSIX sh. Sourced by every per-host adapter.
#
# Adapter interface (the runner calls only these):
#   adapter.sh info                                  -> key=value lines
#   adapter.sh run <policy.env> <fixture.sh> <phase> -> runs `sh fixture phase`
#                                                        under the policy
# Exit 64 with a line starting ISOLATION_UNSUPPORTED: when the policy asks for
# something this adapter cannot enforce. Nothing may run in that case.

ISO_EXIT_UNSUPPORTED=64

iso_unsupported() {
  printf 'ISOLATION_UNSUPPORTED: %s\n' "$*" >&2
  exit $ISO_EXIT_UNSUPPORTED
}

# $1 = policy file, $2 = space-separated ISO_REQUIRE values this adapter supports
iso_load_policy() {
  policy=$1; supported=" $2 "
  [ -r "$policy" ] || iso_unsupported "policy file not readable: $policy"
  # shellcheck disable=SC1090
  . "$policy"
  for v in ISO_T ISO_WS ISO_PROT ISO_HIDDEN ISO_EVIDENCE ISO_FAKE_HOME ISO_FAKE_SOCK_DIR \
           ISO_FAKE_SOCK ISO_NET ISO_NET_HOST ISO_SCRUB_ENV ISO_MARKER_FILE ISO_CONTROL; do
    eval "val=\${$v:-}"
    [ -n "$val" ] || iso_unsupported "policy missing $v"
    export "$v"
  done
  case "$ISO_NET" in deny|allow) ;; *) iso_unsupported "unknown ISO_NET value '$ISO_NET'" ;; esac
  case "$ISO_CONTROL" in enabled|disabled) ;; *) iso_unsupported "unknown ISO_CONTROL value '$ISO_CONTROL'" ;; esac
  for req in ${ISO_REQUIRE:-}; do
    case "$supported" in *" $req "*) ;; *) iso_unsupported "requirement '$req' not supported by this adapter" ;; esac
  done
  export ISO_REQUIRE
}

iso_check_run_args() {
  [ -r "$1" ] || iso_unsupported "fixture not readable: $1"
  case "$2" in attack|positive) ;; *) iso_unsupported "unknown phase '$2'" ;; esac
}
