#!/bin/sh
# Claude Code sandbox layer: @anthropic-ai/sandbox-runtime (`srt`), the package
# Claude Code's `sandbox.enabled` setting wraps Bash commands with on Linux
# (bubblewrap plus a host-side domain-filtering proxy). Driven directly here
# because the `claude` binary on this host cannot start a session.
# enabled : allowWrite=[workspace], denyRead=[hidden, fake home, fake socket dir],
#           allowedDomains=[] (or [ISO_NET_HOST] when ISO_NET=allow),
#           credentials.envVars deny for ISO_SCRUB_ENV.
# disabled: plain `sh fixture phase`, no srt at all. srt has no total off
#           switch: with filesystem.disabled=true it still applied the seccomp
#           unix-socket filter, a private pid namespace and tree termination
#           (results/claude-code-srt.filesystem-disabled-variant.log).
here=$(cd "$(dirname "$0")" && pwd); . "$here/common.sh"
case "$1" in
  info)
    echo "host=claude-code-srt"; pkg=$(dirname "$(dirname "$(readlink -f "$(command -v srt)")")")/package.json
    echo "version=srt --version reports $(srt --version 2>/dev/null); package.json version $(python3 -c "import json;print(json.load(open('$pkg'))['version'])" 2>/dev/null)"
    echo "mechanism=sandbox-runtime: bubblewrap + unix-socket proxy allowlist + seccomp unix-socket filter"
    echo "supports_require=domain-allowlist"; echo "kernel=$(uname -r)"; echo "os=$(. /etc/os-release; echo "$PRETTY_NAME")" ;;
  run)
    iso_load_policy "$2" "domain-allowlist"; iso_check_run_args "$3" "$4"
    command -v srt >/dev/null || iso_unsupported "srt not installed"
    cfg="$ISO_T/srt-settings.json"
    if [ "$ISO_CONTROL" = disabled ]; then cd "$ISO_WS" && exec sh "$3" "$4"; fi
    domains='[]'; [ "$ISO_NET" = allow ] && domains="[\"$ISO_NET_HOST\"]"
    cat > "$cfg" <<JSON
{"network":{"allowedDomains":$domains,"deniedDomains":[]},
 "filesystem":{"denyRead":["$ISO_HIDDEN","$ISO_FAKE_HOME","$ISO_FAKE_SOCK_DIR"],"allowWrite":["$ISO_WS"],"denyWrite":[]},
 "credentials":{"envVars":[{"name":"$ISO_SCRUB_ENV","mode":"deny"}]}}
JSON
    cd "$ISO_WS" && exec srt --settings "$cfg" -c "sh '$3' '$4'" ;;
  *) echo "usage: $0 info | run <policy.env> <fixture.sh> <phase>" >&2; exit 2 ;;
esac
