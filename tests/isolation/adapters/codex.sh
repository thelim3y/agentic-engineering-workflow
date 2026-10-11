#!/bin/sh
# Codex CLI sandbox layer, driven through `codex sandbox` (the documented way
# to run an arbitrary command under the Linux sandbox: bubblewrap plus seccomp).
# A per-run CODEX_HOME holds a config.toml with a permissions profile:
#   extends ":workspace"; workspace root = ISO_WS; ISO_HIDDEN, ISO_FAKE_HOME and
#   ISO_FAKE_SOCK_DIR = "deny"; :tmpdir and :slash_tmp = "read" (":workspace"
#   makes them writable by default); network.enabled = ISO_NET.
# The credential env var is removed with shell_environment_policy.exclude.
# disabled: plain `sh fixture phase`, no codex at all.
# CODEX_HOME must not live under $TMPDIR: codex refuses to create its helper
# aliases there and the sandbox then fails with "execvp codex-linux-sandbox".
here=$(cd "$(dirname "$0")" && pwd); . "$here/common.sh"
CODEX_BIN=${CODEX_BIN:-$(command -v codex 2>/dev/null || echo "$HOME/codex-prefix/node_modules/.bin/codex")}
case "$1" in
  info)
    echo "host=codex"; echo "version=$("$CODEX_BIN" --version 2>/dev/null || echo 'not installed')"
    echo "mechanism=codex sandbox: bubblewrap + seccomp, permissions profile (filesystem read/write/deny, network.enabled)"
    echo "supports_require="; echo "kernel=$(uname -r)"; echo "os=$(. /etc/os-release; echo "$PRETTY_NAME")" ;;
  run)
    iso_load_policy "$2" ""; iso_check_run_args "$3" "$4"
    if [ "$ISO_CONTROL" = disabled ]; then cd "$ISO_WS" && exec sh "$3" "$4"; fi
    [ -x "$CODEX_BIN" ] || iso_unsupported "codex not installed (CODEX_BIN=$CODEX_BIN)"
    export CODEX_HOME="$ISO_T/codex-home"; mkdir -p "$CODEX_HOME"
    net=false; [ "$ISO_NET" = allow ] && net=true
    cat > "$CODEX_HOME/config.toml" <<TOML
default_permissions = "spike"

[permissions.spike]
extends = ":workspace"

[permissions.spike.workspace_roots]
"$ISO_WS" = true

[permissions.spike.filesystem]
":tmpdir" = "read"
":slash_tmp" = "read"
"$ISO_HIDDEN" = "deny"
"$ISO_FAKE_HOME" = "deny"
"$ISO_FAKE_SOCK_DIR" = "deny"

[permissions.spike.network]
enabled = $net
TOML
    cd "$ISO_WS" && exec "$CODEX_BIN" sandbox --permission-profile spike -C "$ISO_WS" \
      -c "shell_environment_policy.exclude=[\"$ISO_SCRUB_ENV\"]" -- sh "$3" "$4" ;;
  *) echo "usage: $0 info | run <policy.env> <fixture.sh> <phase>" >&2; exit 2 ;;
esac
