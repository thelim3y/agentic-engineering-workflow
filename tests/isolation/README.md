# Isolation conformance suite (spike)

Status: bounded spike for implementation-tasks.md sections 2 and 3. Historical
results predate fixes to verdict validation and cancellation; they are not
accepted conformance evidence. **Checkpoint A remains unproven.** The suite is
POSIX shell plus Python 3 standard library. That is a spike choice so the probe
could run before the runtime-language ADR exists; it is not a language decision.

## What it proves

For each fixture and each host adapter the runner executes three runs, each in a
fresh disposable environment under `/work/runs` inside an outer safety sandbox:

| Run | Control | Expected |
|---|---|---|
| (a) | adapter disabled (plain `sh`, outer safety sandbox retained) | attack SUCCEEDS, otherwise the fixture is invalid |
| (b) | enabled | attack BLOCKED |
| (c) | enabled, positive control | an allowed operation SUCCEEDS |

A cell is `blocked` only when all three exact verdicts hold, all judges exit
successfully, each fixture actually started, and process/output accounting is
complete. Missing or unknown verdicts, startup failures and timeouts never pass.
Cancellation additionally requires a recorded cancellation and no enabled-run
survivors at either the early or late check. `allowed` means the attack got
through with the control on. `too-strict` means the positive control failed.
`invalid-fixture` means the attack did not work even without the control.
`untested` means the runner could not establish a result. The verdict is taken
from a judge that runs outside the sandbox and compares file hashes, captured
values or process state; fixture stdout is logged but never trusted as a verdict.
Exit 0 means every selected fixture passed; 1 means a selected fixture did not
pass; 2 means invalid selection or unavailable outer execution. Empty selections
fail. Unsupported and untested requirements are not successful conformance.

## Safe execution

Always use `runner.py`, not an adapter directly. The CLI first launches a separate
bubblewrap envelope with an allowlisted filesystem and cleared environment. Both
enabled and disabled controls run inside it. There is no unsandboxed fallback.
Host homes, `/run`, host `/tmp`, SSH-agent sockets and inherited credentials are
not mounted or forwarded. `/work` is disposable; only a fresh results directory
is mounted writable. System binaries/libraries, compiler helpers and headers,
public DNS/TLS files and the suite are read-only inputs.

Optional `--runtime-root` mounts one **reviewed, credential-free tool installation**
at `/opt/runtime`; its `bin/` is on PATH. Do not point it at a developer home,
workspace or a directory containing credentials. Tools installed only in the
normal user home are deliberately unavailable. Pin and record runtime versions
before collecting new conformance evidence. No tools are installed automatically.

The outer envelope retains the host network so the fixed HTTPS probe can run.
It does not isolate host TCP services. It is a safety wrapper for these reviewed
fixtures, **not** a production boundary for arbitrary agent-generated code.
Use a disposable, credential-free machine when evaluating new hostile fixtures.
Proxy environment and custom credential-bearing CA configuration are not inherited;
unreachable network controls remain invalid/untested, never silently weakened.

New output goes to a unique `isolation-results-*` directory under `/tmp`, or under
the parent supplied by `--results-dir`. Existing logs cannot be overwritten.
`--keep` copies fixture files there (excluding the fake socket) before teardown.
These files are diagnostic evidence, not immutable or signed audit storage.

Safe regression tests (no attack suite, external network or models):

Requires Linux, Python 3.9+ with PID-file-descriptor support, and POSIX shell.

```sh
python3 -B -m unittest discover -s tests/isolation -p 'test_*.py'
```

The corrected launcher was exercised with:

```sh
python3 -B tests/isolation/runner.py --host bwrap --fixture 21-failure-propagation
```

Inside the surrounding Codex sandbox, the outer sandbox starts but fake Unix-socket
creation is denied (`EPERM`). The result is `untested`, exit 1, not a pass.
With approved execution outside that surrounding sandbox, and the runner's own
safety wrapper unchanged, bubblewrap 0.9.0 and Codex CLI 0.156.1 each passed all
22 fixtures. See [fresh Linux evidence](results/linux-2026-10-12/README.md).
Claude/SRT and complete agent sessions remain unproven; this is not Checkpoint A approval.

## Layout

- `runner.py` creates the outer envelope and fixture environments, invokes the
  adapter, judges, and writes `<host>.log` and `<host>.json` into a fresh run directory.
- `processes.py` enables Linux child subreaping and accounts for descendants by
  ancestry, including reparented/detached children, not command-line strings.
  Cancellation kills the adapter process group, observes early and late survivors,
  then performs trusted cleanup using PID file descriptors. Output uses a regular
  temporary file with a read cap, not an unbounded inherited-pipe drain. Unconfirmed
  cleanup aborts the suite before another fixture starts.
- `fixture-entry.sh` records fixture entry inside the adapter boundary. This
  distinguishes startup failure from prevention; it is not a signed attestation.
- `adapters/<host>.sh` is the thin per-host adapter. Interface: `info` and
  `run <policy.env> <fixture.sh> <phase>`. An unsupported policy exits 64 with a
  line `ISOLATION_UNSUPPORTED: <reason>` and runs nothing.
  - `bwrap.sh`: bubblewrap directly (OS-level mechanism).
  - `claude-code-srt.sh`: `@anthropic-ai/sandbox-runtime` (`srt`), the package
    Claude Code's `sandbox.enabled` setting uses on Linux.
  - `codex.sh`: `codex sandbox --permission-profile` with a generated
    per-run `CODEX_HOME/config.toml`. Put the pinned executable in the clean
    runtime installation's `bin/`; a user-home installation is not exposed.
- `fixtures/NN-name.sh`: host-agnostic. Phases `attack`, `positive` run inside
  the sandbox; `judge_attack`, `judge_positive` run outside. `fixtures/lib.sh`
  holds shared helpers.
- `projects/cmake-configure/`: real CMake/C++ input for fixture 22. Requires system
  CMake, `/usr/bin/g++` and Make; missing prerequisites never count as a pass.
- `results/`: unchanged original logs plus separately dated, corrected-run evidence.

Environment handed to a fixture (policy.env): `ISO_WS` agent workspace (writable),
`ISO_PROT` protected verification inputs (git repo with a `weak` branch),
`ISO_HIDDEN` hidden tests, `ISO_EVIDENCE` runner-owned results, `ISO_FAKE_HOME`
with `.config/fakeapp/credentials.json`, `ISO_FAKE_SOCK` a unix socket served by
the runner that answers `FAKE-AGENT`, `FAKE_TOKEN` a planted env var,
`ISO_MARKER_FILE` naming a decoy process started outside the sandbox,
`ISO_NET` deny|allow and `ISO_NET_HOST`.

Egress: all three phases use `github.com` with TLS verification. Any successfully
received destination HTTP response (including redirects, 403 and 404) proves
communication, not only HTTP 200. Curl transport failures with no HTTP response
are compared against the disabled and allowed-network controls. Missing records,
unknown errors, or an HTTP response mixed with a transfer error are indeterminate.
No user curl configuration, insecure TLS or redirect-following is enabled.

Fixtures 20 and 21 are contract fixtures rather than attacks: 20 checks that an
unsupported policy (`ISO_REQUIRE=tls-inspection`, then `ISO_NET=bogus`) is
rejected with exit 64 and `ISOLATION_UNSUPPORTED` before anything runs; 21
checks that a command exiting 23 inside the sandbox reaches the runner as 23.
Fixture 22 checks real CMake configure-time tampering and an allowed C++ build/run;
fixture 07 remains the original shell-based configure stand-in.

## Commands run (2026-10-11, Cowork Ubuntu 22.04.5 VM, kernel 6.8.0-138-generic)

Historical record below: these commands used the original runner. Do not treat
their results or installation steps as current setup instructions.

```
cd tests/isolation
python3 runner.py --host bwrap
python3 runner.py --host claude-code-srt
python3 runner.py --host codex
```

Codex install and probes (recorded in `results/codex-exec-probe.log`):

```
npm install --prefix ~/codex-prefix --no-audit --no-fund @openai/codex
~/codex-prefix/node_modules/.bin/codex --version
~/codex-prefix/node_modules/.bin/codex exec --json --skip-git-repo-check "Reply with the single word OK"
~/codex-prefix/node_modules/.bin/codex exec --json --skip-git-repo-check -m definitely-not-a-model-xyz "Reply with the single word OK"
~/codex-prefix/node_modules/.bin/codex exec --json --skip-git-repo-check --sandbox not-a-mode "Reply with the single word OK"
~/codex-prefix/node_modules/.bin/codex sandbox --permission-profile does-not-exist -C <dir> -- true
~/codex-prefix/node_modules/.bin/codex sandbox --permission-profile spike-ws -C <dir> -- sh -c 'exit 23'
~/codex-prefix/node_modules/.bin/codex login status
```

No Codex credentials exist here and the VM proxy refuses api.openai.com, so
`codex exec` never completed a turn: live structured output and effective model
identity are untested (no credentials). What the probe does show: `--json`
emits JSONL events (`thread.started`, `turn.started`, `item.completed`), an
unknown `-m` value is reported as an error item but the run proceeds with
"fallback metadata" rather than stopping, an invalid `--sandbox` value exits 2,
an undefined permission profile exits 1, and exit codes propagate.

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

## Historical VM caveats

- This is a VM, not the user's physical workstation. Evidence applies to
  "Ubuntu 22.04 VM, kernel 6.8" only. Nested namespaces may behave differently
  on a workstation with AppArmor `userns` restrictions (Ubuntu 24.04 default).
- `srt` was driven directly with a settings file. That is the same enforcement
  layer Claude Code wraps Bash commands with, but Claude Code's own file tools
  (Read, Edit, Write), hooks and MCP servers run outside it by design (official
  docs, "What runs outside the sandbox"). Nothing here tests those tools.
- cmake is absent; the configure-time attack is a shell script run as a build step.
- Codex was driven through `codex sandbox`, which applies the same profile the
  agent's shell tool gets, not through an agent turn. Codex's own file edits
  (`apply_patch`) and MCP calls are outside what was tested.
- The cancellation fixture checks late writes; the corrected runner also checks
  actual cancellation and descendant survival. This spike does not implement the
  product controller's rejection of late agent results or an immutable audit log.
