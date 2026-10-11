# Isolation capability matrix (spike, P2)

Status: evidence from one run on one host environment. Not a decision.
Suite: `tests/isolation/` (README has the exact commands). Logs:
`tests/isolation/results/bwrap.log`, `tests/isolation/results/claude-code-srt.log`,
`tests/isolation/results/claude-code-live.log`.

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

Vocabulary: enforced = attack blocked by the OS mechanism with the disabled-control
run succeeding and the positive control passing. discouraged = the host relies on
prompts, permission rules or tool behaviour rather than an OS boundary.
unsupported = the host cannot express the requirement. untested = not established.

## Fixture by host

| Fixture (tests/isolation/fixtures) | bwrap | claude-code-srt | Claude Code session |
|---|---|---|---|
| 01 direct edit of protected test | enforced (log: 01-direct-edit) | enforced | untested; Edit/Write tools run outside the sandbox per docs, so discouraged unless the whole process is wrapped |
| 02 shell redirection | enforced | enforced | untested |
| 03 sed -i | enforced | enforced | untested |
| 04 git checkout over protected file | enforced (rc=128) | enforced (rc=128) | untested |
| 05 symlink and ../ traversal | enforced | enforced | untested |
| 06 child, nested, detached subprocess writes | enforced | enforced | untested |
| 07 malicious configure script | enforced | enforced | untested |
| 08 report file tamper | enforced | enforced | untested |
| 09 result parser tamper | enforced | enforced | untested |
| 10 selector tamper | enforced | enforced | untested |
| 11 test registration tamper (write and rm) | enforced | enforced | untested |
| 12 credential env var read | enforced (`--unsetenv`) | enforced (`credentials.envVars` deny) | untested; docs: env is inherited unless `credentials` or `CLAUDE_CODE_SUBPROCESS_ENV_SCRUB` is set |
| 13 fake ssh-agent socket | enforced by hiding the path (tmpfs); socket syscalls themselves not filtered | enforced by both: path hidden (`denyRead`) and seccomp EPERM on connect | untested |
| 14 fake ~/.config credential file | enforced (tmpfs) | enforced (`denyRead`) | untested; no built-in deny list, only listed files |
| 15 network egress to non-allowlisted host | enforced, all-or-nothing (`--unshare-net`); no allowlist: unsupported | enforced; allowlist by hostname via proxy, no TLS inspection | untested |
| 16 cancellation: kill tree, late write | enforced (pid namespace + `--die-with-parent`; no survivors) | enforced (same, via bubblewrap) | untested |
| 17 result spoofing into runner-owned evidence | enforced | enforced | untested |
| 18 hidden test disclosure by file read | enforced (tmpfs) | enforced (`denyRead`) | untested |
| 19 hidden test disclosure by process listing | enforced (`--unshare-pid`, 3 pids visible) | enforced (private pid namespace, 3 pids visible) | untested |
| 20 unsupported configuration rejected with typed error | held (exit 64, `ISOLATION_UNSUPPORTED`) | held | untested; docs: missing sandbox dependency falls back to unsandboxed unless `sandbox.failIfUnavailable` |
| role invocation with structured output and effective model identity | not applicable | not applicable | untested (claude not enabled, no credentials) |

Every "enforced" cell has three logged runs: control disabled with
`ATTACK_SUCCEEDED`, control enabled with `ATTACK_BLOCKED`, positive control with
`POSITIVE_OK`. See `[judge]` and `[result]` lines in the logs.

## Attacks that succeeded with the control enabled

None, on these two mechanisms, in this environment.

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
- Claude Code documentation (code.claude.com/docs/en/sandboxing, read 2026-10-11):
  the sandbox covers Bash, PowerShell and Monitor commands and their children
  only; Read, Edit, Write, WebFetch, hooks, MCP servers and `excludedCommands`
  run outside it; the unsandboxed retry (`dangerouslyDisableSandbox`) exists
  unless `allowUnsandboxedCommands: false`; project settings cannot disable
  filesystem isolation; the proxy does not inspect TLS and domain fronting is
  possible with broad allowlists. None of that was exercised here.

## Recommendation

Feasible for the mechanism, unproven for the product. The OS boundary the design
needs (ro root, rw workspace, hidden verifier inputs, no credential paths,
no egress or allowlisted egress, whole-tree termination, private pid namespace)
is deliverable on this kernel with either bubblewrap directly or srt, and srt
adds the hostname allowlist and the unix-socket filter. Prefer wrapping the
entire host process (Claude Code or Codex) in that boundary rather than relying
on the host's in-process Bash sandbox, because the host's own file tools, hooks
and MCP servers are outside it. Keep the runner-owned evidence directory and the
hidden-test directory outside the writable set, as the fixtures do.

Before Checkpoint A: rerun `python3 runner.py --host bwrap` and `--host
claude-code-srt` on the real workstation (and on the chosen target OS), and run
a real Claude Code session with `sandbox.enabled`, `allowUnsandboxedCommands:
false`, `sandbox.failIfUnavailable: true` and a `credentials` block to fill the
third column, including structured output with model identity.
