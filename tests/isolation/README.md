# Isolation conformance suite (spike)

Status: bounded spike for implementation-tasks.md sections 2 and 3. Disposable
directories only, no production credentials, no live model calls. The suite is
POSIX shell plus Python 3 standard library. That is a spike choice so the probe
could run before the runtime-language ADR exists; it is not a language decision.

## What it proves

For each fixture and each host adapter the runner executes three runs, each in a
fresh disposable environment created with `mktemp -d` under `~/iso-runs`:

| Run | Control | Expected |
|---|---|---|
| (a) | disabled (plain `sh`, no sandbox) | attack SUCCEEDS, otherwise the fixture is invalid |
| (b) | enabled | attack BLOCKED |
| (c) | enabled, positive control | an allowed operation SUCCEEDS |

A cell is `blocked` only when all three hold. `allowed` means the attack got
through with the control on. `too-strict` means the positive control failed.
`invalid-fixture` means the attack did not work even without the control.
`untested` means the runner could not establish a result. The verdict is taken
from a judge that runs outside the sandbox and compares file hashes, captured
values or process state; fixture stdout is logged but never trusted.

## Layout

- `runner.py` creates environments, invokes the adapter, kills process groups for
  the cancellation fixture, judges, and writes `results/<host>.log` (raw output)
  and `results/<host>.json`.
- `adapters/<host>.sh` is the thin per-host adapter. Interface: `info` and
  `run <policy.env> <fixture.sh> <phase>`. An unsupported policy exits 64 with a
  line `ISOLATION_UNSUPPORTED: <reason>` and runs nothing.
  - `bwrap.sh`: bubblewrap directly (OS-level mechanism).
  - `claude-code-srt.sh`: `@anthropic-ai/sandbox-runtime` (`srt`), the package
    Claude Code's `sandbox.enabled` setting uses on Linux.
- `fixtures/NN-name.sh`: host-agnostic. Phases `attack`, `positive` run inside
  the sandbox; `judge_attack`, `judge_positive` run outside. `fixtures/lib.sh`
  holds shared helpers.
- `results/`: committed logs from the runs described below.

Environment handed to a fixture (policy.env): `ISO_WS` agent workspace (writable),
`ISO_PROT` protected verification inputs (git repo with a `weak` branch),
`ISO_HIDDEN` hidden tests, `ISO_EVIDENCE` runner-owned results, `ISO_FAKE_HOME`
with `.config/fakeapp/credentials.json`, `ISO_FAKE_SOCK` a unix socket served by
the runner that answers `FAKE-AGENT`, `FAKE_TOKEN` a planted env var,
`ISO_MARKER_FILE` naming a decoy process started outside the sandbox,
`ISO_NET` deny|allow and `ISO_NET_HOST`.

Egress: every run uses the same host (`github.com`, reachable from this VM) so
the VM's own egress allowlist is constant; only the sandbox policy differs
between run (b) `ISO_NET=deny` and run (c) `ISO_NET=allow`.

## Commands run (2026-10-11, Cowork Ubuntu 22.04.5 VM, kernel 6.8.0-138-generic)

```
cd tests/isolation
python3 runner.py --host bwrap
python3 runner.py --host claude-code-srt
```

Attempt at a live Claude Code role invocation (recorded in
`results/claude-code-live.log`):

```
/opt/cowork/claude-bin/claude --version
/opt/cowork/claude-bin/claude -p "Reply with exactly the word OK and nothing else."
```

Both fail: the `claude` on this VM is a 2.3 MB static shim that reports
`claude is not enabled in this environment`. No Claude Code session, settings
file, permission rule or `--settings '{"sandbox": ...}'` flag could be
exercised. Structured output and effective model identity are untested here.

Environment facts recorded during the run: `bwrap --version` = bubblewrap 0.6.1,
`srt --version` prints 1.0.0 while its package.json says 0.0.76, socat present,
unprivileged user namespaces allowed, this shell itself already runs inside an
srt bubblewrap sandbox (nested namespaces worked). Not present: codex (see P3),
docker, podman, firejail, cmake, clang.

## Caveats

- This is a VM, not the user's physical workstation. Evidence applies to
  "Ubuntu 22.04 VM, kernel 6.8" only. Nested namespaces may behave differently
  on a workstation with AppArmor `userns` restrictions (Ubuntu 24.04 default).
- `srt` was driven directly with a settings file. That is the same enforcement
  layer Claude Code wraps Bash commands with, but Claude Code's own file tools
  (Read, Edit, Write), hooks and MCP servers run outside it by design (official
  docs, "What runs outside the sandbox"). Nothing here tests those tools.
- cmake is absent; the configure-time attack is a shell script run as a build step.
- The runner's "late write rejected" property is runner policy (outputs of a
  cancelled run are never accepted). The sandbox contributes termination of the
  whole tree, which is what the fixture measures.
