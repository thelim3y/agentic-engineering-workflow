# Isolation capability matrix (spike, P2 and P3)

Status: shell/build evidence exists; complete host conformance remains unproven.
Review found false-pass paths in the original runner: missing/failed judges,
unverified cancellation, and successful CLI exits for failed or empty suites.
The runner has been corrected and regression-tested; the full three-host suite
has not been revalidated. **Checkpoint A remains unproven.**

## Fresh Linux run

On Ubuntu 24.04.5 / kernel 7.0.0-31, bubblewrap 0.9.0 and Codex CLI 0.156.1 each
passed all 22 corrected fixtures, including a new real CMake configure attack and
successful C++ build/run. All 36 regression tests passed. These runs used the
credential-free outer wrapper, outside the surrounding Codex session sandbox.

See [dated evidence, commands and limits](../../tests/isolation/results/linux-2026-10-12/README.md).
This proves the tested shell/build mechanisms, not complete agent sessions,
native editing/MCP tools, model identity or the production workflow.

## Original VM observations

The remaining tables describe the original, provisional run, not the fresh run.
Suite: `tests/isolation/` (README has the exact commands). Logs:
`tests/isolation/results/bwrap.log`, `tests/isolation/results/claude-code-srt.log`,
`tests/isolation/results/codex.log`, `tests/isolation/results/claude-code-live.log`,
`tests/isolation/results/codex-exec-probe.log`.

Environment: Cowork Ubuntu 22.04.5 VM, kernel 6.8.0-138-generic, non-root,
unprivileged user namespaces enabled, already inside an srt bubblewrap sandbox.
This is a VM, not the user's workstation, so every cell below applies to
"Ubuntu 22.04 VM, kernel 6.8" only. Nested-namespace behaviour on a physical
workstation (especially Ubuntu 24.04 with AppArmor userns restriction) is untested.

Hosts evaluated:

- bwrap: bubblewrap 0.6.1 driven directly (`adapters/bwrap.sh`).
- claude-code-srt: `@anthropic-ai/sandbox-runtime` 0.0.76 (`srt --version` says
  1.0.0) driven directly (`adapters/claude-code-srt.sh`). This is the package
  Claude Code's `sandbox.enabled` setting wraps Bash commands with on Linux.
- Claude Code itself: not runnable on this VM (`claude` is a shim that says
  "claude is not enabled in this environment"). Everything that needs a session
  is untested.
- codex: Codex CLI 0.162.1 (`npm install --prefix ~/codex-prefix @openai/codex`),
  driven through `codex sandbox --permission-profile` (`adapters/codex.sh`),
  which is the documented way to run a command under its Linux sandbox
  (bubblewrap plus seccomp). No credentials, so no agent turn ran.

Vocabulary: enforced = attack blocked by the OS mechanism with the disabled-control
run succeeding and the positive control passing. discouraged = the host relies on
prompts, permission rules or tool behaviour rather than an OS boundary.
unsupported = the host cannot express the requirement. untested = not established.

## Fixture by host

The table below preserves the original run's classifications. Every `enforced`
or `held` entry is provisional pending a fresh run with the corrected runner;
it is not a current capability guarantee. Historical raw logs are unchanged.

| Fixture (tests/isolation/fixtures) | bwrap | claude-code-srt | codex (`codex sandbox`) | Claude Code session |
|---|---|---|---|---|
| 01 direct edit of protected test | enforced (log: 01-direct-edit) | enforced | enforced | untested; Edit/Write tools run outside the sandbox per docs, so discouraged unless the whole process is wrapped |
| 02 shell redirection | enforced | enforced | enforced | untested |
| 03 sed -i | enforced | enforced | enforced | untested |
| 04 git checkout over protected file | enforced (rc=128) | enforced (rc=128) | enforced (rc=128) | untested |
| 05 symlink and ../ traversal | enforced | enforced | enforced | untested |
| 06 child, nested, detached subprocess writes | enforced | enforced | enforced | untested |
| 07 malicious configure script | enforced | enforced | enforced | untested |
| 08 report file tamper | enforced | enforced | enforced | untested |
| 09 result parser tamper | enforced | enforced | enforced | untested |
| 10 selector tamper | enforced | enforced | enforced | untested |
| 11 test registration tamper (write and rm) | enforced | enforced | enforced | untested |
| 12 credential env var read | enforced (`--unsetenv`) | enforced (`credentials.envVars` deny) | enforced (`shell_environment_policy.exclude`) | untested; docs: env is inherited unless `credentials` or `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is set |
| 13 fake ssh-agent socket | enforced by hiding the path (tmpfs); socket syscalls themselves not filtered | enforced by both: path hidden (`denyRead`) and seccomp EPERM on connect | enforced: seccomp EPERM on connect, path denied | untested |
| 14 fake ~/.config credential file | enforced (tmpfs) | enforced (`denyRead`) | enforced (`deny` rule, EACCES; directory name still visible) | untested; no built-in deny list, only listed files |
| 15 network egress to non-allowlisted host | enforced, all-or-nothing (`--unshare-net`); no allowlist: unsupported | enforced; allowlist by hostname via proxy, no TLS inspection | enforced, all-or-nothing (`network.enabled`); domain rules need `features.network_proxy`, untested | untested |
| 16 cancellation: kill tree, late write | enforced (pid namespace + `--die-with-parent`; no survivors) | enforced (same, via bubblewrap) | enforced (no survivors 0.3 s after SIGKILL) | untested |
| 17 result spoofing into runner-owned evidence | enforced | enforced | enforced | untested |
| 18 hidden test disclosure by file read | enforced (tmpfs) | enforced (`denyRead`) | enforced (`deny`, EACCES; directory name still visible) | untested |
| 19 hidden test disclosure by process listing | enforced (`--unshare-pid`, 3 pids visible) | enforced (private pid namespace, 3 pids visible) | enforced (private pid namespace, 3 pids visible) | untested |
| 20 unsupported configuration rejected with typed error | held (exit 64, `ISOLATION_UNSUPPORTED`) | held | held; codex itself: undefined profile exits 1, invalid `--sandbox` exits 2 | untested; docs: missing sandbox dependency falls back to unsandboxed unless `sandbox.failIfUnavailable` |
| 21 failure propagation (exit 23 inside the sandbox) | held | held | held | untested |
| role invocation with structured output and effective model identity | not applicable | not applicable | untested (no credentials); `codex exec --json` emits JSONL events; unknown `-m` is reported as an error item and the run continues with fallback metadata | untested (claude not enabled, no credentials) |

Every historically reported "enforced" cell has three logged runs: control disabled with
`ATTACK_SUCCEEDED`, control enabled with `ATTACK_BLOCKED`, positive control with
`POSITIVE_OK`. See `[judge]` and `[result]` lines in the logs.

## Attacks that succeeded with the control enabled

The original runner reported none. Its verdict defects mean this is not proof
that every enabled attack was prevented. Inspect the raw observations and rerun
the corrected suite before accepting any capability.

## Host differences recorded (P3)

| Topic | claude-code-srt | codex |
|---|---|---|
| Policy surface | JSON settings: `filesystem.allowWrite/denyWrite/denyRead/allowRead`, `network.allowedDomains/deniedDomains`, `credentials` | TOML `[permissions.<name>]` profiles with `filesystem` path rules (`read`, `write`, `deny`), `workspace_roots`, `network.enabled`; the older `sandbox_mode` keys are a separate, mutually exclusive system |
| Default writable set | only `allowWrite` entries | `:workspace` root plus `:tmpdir` and `:slash_tmp` unless overridden (the adapter sets both to `read`); the fixture tree therefore lives outside `$TMPDIR` |
| Deny read behaviour | path disappears (ENOENT) | EACCES; the directory entry is still visible |
| Workspace `.git` | writable except `hooks/` and `config`; `git add -A` fails on the `/dev/null` placeholders srt mounts over protected names (`.bashrc`, `.mcp.json`, `.vscode`, `.idea`, ...); `git add <file>` and `git commit` work | `<root>/.git` read-only in `:workspace`: `git add` fails with "Read-only file system"; read-only `.agents` and `.codex` placeholders appear in the workspace |
| Unix sockets | seccomp filter, EPERM | seccomp filter, EPERM |
| Env scrubbing | `credentials.envVars` deny | `shell_environment_policy.exclude` |
| Network allowlist | hostname proxy, default deny | default off; domain rules only with `features.network_proxy` (untested) |
| Invalid policy | missing required key refuses to run; unknown key silently ignored | undefined profile refuses (exit 1); invalid `--sandbox` value refuses (exit 2) |
| Running arbitrary command in the sandbox | `srt --settings <file> -c <cmd>` | `codex sandbox --permission-profile <name> -C <dir> -- <cmd>`; `CODEX_HOME` must not be under `$TMPDIR` or the helper fails with `execvp codex-linux-sandbox` |
| Model selection | untested | unknown model is not rejected before the run starts (error item, then "fallback metadata"); the controller must verify the configured model itself |
| Unsupported environment (docs) | `enableWeakerNestedSandbox` for containers, documented as considerably weaker | docs say to use `danger-full-access` inside an already isolated container when bwrap or seccomp are blocked |

## Observations that matter for the design

- srt has no total off switch. With `filesystem.disabled=true` it still applied
  the seccomp unix-socket filter, a private pid namespace and tree termination
  (`results/claude-code-srt.filesystem-disabled-variant.log`, fixtures 13, 16, 19
  reported `invalid-fixture` because the "disabled" run was still partly
  sandboxed). The adapter now uses plain `sh` for the disabled run.
- srt ignores unknown settings keys silently (`"bogus": true` ran anyway) but
  refuses to start on a missing required key. The controller must validate its
  own policy before handing it to srt.
- srt masks protected names in the working directory (`.bashrc`, `.mcp.json`,
  `.vscode`, `.idea`, ...) as `/dev/null` character devices while a command runs.
  `git add -A` fails on them ("can only add regular files"); `git add <file>` and
  `git commit` work. Fixture 04 records this as
  `observation workspace-git-commit=denied` under srt and `ok` under bwrap.
- bwrap egress is all-or-nothing. An allowlist needs a proxy (what srt adds).
- Credential hiding on both mechanisms is per listed path. Nothing is hidden by
  default; the controller must enumerate what to deny.
- Both mechanisms rely on unprivileged user namespaces. Where those are
  restricted (Ubuntu 24.04 AppArmor default, many containers) srt documents
  `enableWeakerNestedSandbox`, which it calls considerably weaker. Reject that
  mode rather than enabling it.
- Codex documentation (learn.chatgpt.com/codex/sandboxing, /codex/permissions,
  /codex/agent-approvals-security, /codex/config-file/config-reference, read
  2026-10-11): Linux uses `bwrap` plus `seccomp`; sandbox rules apply to spawned
  commands and their children; `workspace-write` keeps network off unless
  `network_access = true`; `approval_policy` values are `on-request` and `never`
  (`untrusted` retired, `on-failure` deprecated); the proxy does not filter MCP
  connections, web search or the client's own model requests; hostname checks
  are best effort against DNS rebinding. Only the `codex sandbox` path was
  exercised here.
- Claude Code documentation (code.claude.com/docs/en/sandboxing, read 2026-10-11):
  the sandbox covers Bash, PowerShell and Monitor commands and their children
  only; Read, Edit, Write, WebFetch, hooks, MCP servers and `excludedCommands`
  run outside it; the unsandboxed retry (`dangerouslyDisableSandbox`) exists
  unless `allowUnsandboxedCommands: false`; project settings cannot disable
  filesystem isolation; the proxy does not inspect TLS and domain fronting is
  possible with broad allowlists. None of that was exercised here.

## Recommendation

Promising mechanism evidence, not yet verified product isolation. Revalidate the
shared contract with the corrected runner before selecting an adapter. An outer
boundary around the whole host process remains worth evaluating; shell-only
probes do not establish protection for every host tool.

Claude Code documents its Read/Edit/Write tools, hooks and MCP servers outside
its shell sandbox. Do not generalize that to Codex `apply_patch`: the pinned
[Codex 0.162.1 source](https://github.com/openai/codex/blob/rust-v0.162.1/codex-rs/core/src/tools/runtimes/apply_patch.rs#L156)
passes a filesystem sandbox context into patch application. That source reading
does not prove this product's policy, but contradicts the blanket claim that
patches bypass filesystem sandboxing. Non-shell tools remain **untested here**.

Before Checkpoint A: rerun all three adapters using the credential-free outer
launcher described in the [suite README](../../tests/isolation/README.md), on
each target OS. Never run disabled controls directly on a credentialed workstation.
Separately, with human approval and a scoped credential boundary, run a real
Claude Code session with `sandbox.enabled`,
`allowUnsandboxedCommands: false`, `sandbox.failIfUnavailable: true` and a
`credentials` block; run `codex exec --json` with credentials and a pinned model
to capture structured output and the reported model identity on both hosts.
