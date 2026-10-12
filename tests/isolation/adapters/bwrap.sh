#!/bin/sh
# OS-level adapter: bubblewrap user namespaces, no host product involved.
# enabled : read-only root, workspace bind-mounted rw, hidden/credential
#           directories replaced by empty tmpfs, credential env var unset,
#           fresh pid/ipc/uts namespaces, network namespace removed unless
#           ISO_NET=allow. --die-with-parent ties the tree to the runner.
# disabled: plain `sh fixture phase` with no sandbox at all.
here=$(cd "$(dirname "$0")" && pwd); . "$here/common.sh"
case "$1" in
  info)
    echo "host=bwrap"; echo "version=$(bwrap --version 2>/dev/null)"
    echo "mechanism=bubblewrap user namespaces (ro-bind root, bind rw workspace, tmpfs hides, unshare-net)"
    echo "supports_require="; echo "kernel=$(uname -r)"; echo "os=$(. /etc/os-release; echo "$PRETTY_NAME")" ;;
  run)
    iso_load_policy "$2" ""; iso_check_run_args "$3" "$4"
    if [ "$ISO_CONTROL" = disabled ]; then cd "$ISO_WS" && exec sh "$3" "$4"; fi
    command -v bwrap >/dev/null || iso_unsupported "bwrap not installed"
    net=--unshare-net; [ "$ISO_NET" = allow ] && net=--share-net
    exec bwrap --ro-bind / / --dev /dev --proc /proc \
      --bind "$ISO_WS" "$ISO_WS" \
      --tmpfs "$ISO_HIDDEN" --tmpfs "$ISO_FAKE_HOME" --tmpfs "$ISO_FAKE_SOCK_DIR" \
      --unsetenv "$ISO_SCRUB_ENV" \
      --unshare-user --unshare-pid --unshare-ipc --unshare-uts $net \
      --die-with-parent --new-session --chdir "$ISO_WS" \
      -- sh "$3" "$4" ;;
  *) echo "usage: $0 info | run <policy.env> <fixture.sh> <phase>" >&2; exit 2 ;;
esac
