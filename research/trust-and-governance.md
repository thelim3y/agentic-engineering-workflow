# Trust, control and governance of coding agents, 2026

Only URLs fetched in this run are cited, each with its page date (or "undated") and fetch date 2026-10-13. Claims not confirmed from a primary source are marked "unverified". Sources are listed at the end.

## 1. Sandboxing and execution isolation

### Claude Code

| Mechanism | Publisher, date | Isolates | Enforced or advised | Stated limits |
|---|---|---|---|---|
| Bash sandbox: Seatbelt (macOS); bubblewrap, network namespace and proxy relay (Linux, WSL2) | Anthropic, [sandboxing docs](https://code.claude.com/docs/en/sandboxing) (undated; fetched 2026-10-13) | Shell commands and their child processes. Writes limited to working directory, per-user temp and added directories. Reads allowed except denied paths. No direct network route; hosts pass a proxy allowlist that starts empty. | Enforced by the OS. Off by default. | Covers Bash, PowerShell and Monitor only. Read, Edit, Write, WebFetch, WebSearch, hooks, local MCP servers, LSP and status-line commands run outside it. If the sandbox cannot start, commands run unsandboxed unless `failIfUnavailable` is set. Native Windows runs commands unsandboxed. |
| Protected paths inside writable directories | Same page | Writes to `.claude` settings, hooks, skills and agents, `.mcp.json`, `.bashrc`, `.gitconfig`, `.git/hooks` and `.git/config`. | Enforced by the OS. | Cannot be exempted by an allow rule. Only `filesystem.disabled` lifts it. |
| Unsandboxed retry (`dangerouslyDisableSandbox`) | Same page | Lets Claude re-run a failed command outside the sandbox. | Approval by permission mode: bypass runs without prompt; manual and acceptEdits prompt; auto mode uses a classifier; dontAsk denies. | Disabled by `allowUnsandboxedCommands: false`. |
| `excludedCommands` | Same page | Removes matching commands from the sandbox. | Configuration. | Page warns a broad pattern such as `docker *` gives full access, and a script in the working directory can be written then run outside the sandbox. |
| Credential protection (`credentials.files`, `credentials.envVars`, mask via TLS-terminating proxy) | Same page | Denies reads of listed files and unsets listed variables in sandboxed commands. | Enforced for sandboxed commands. | No built-in credential deny list; default read policy still allows `~/.ssh` and `~/.aws/credentials` unless listed. |
| Managed enforcement: `sandbox.enabled`, `failIfUnavailable`, `allowUnsandboxedCommands`, `allowManagedDomainsOnly`, `strictAllowlist` | Same page | Administrator lock. Under an admin-required sandbox Claude Code ignores repository settings that loosen it. | Enforced when delivered as managed settings. | Typed commands at the `!` prompt run unsandboxed in most sessions. Subagents share the parent sandbox configuration. |
| Whole-process boundary: run Claude Code inside the sandbox runtime (`@anthropic-ai/sandbox-runtime`) or a dev container | [Sandboxing](https://code.claude.com/docs/en/sandboxing) and [Security](https://code.claude.com/docs/en/security) pages (fetched 2026-10-13) | Tools, hooks and MCP servers, not only Bash. | Advised by vendor as "additional isolation". | Not a default. |

Vendor statements, quoted from the sandboxing page: "Sandboxing reduces risk but is not a complete isolation boundary." "Effective sandboxing requires both filesystem and network isolation." The built-in proxy "does not terminate or inspect TLS", so "code running inside the sandbox can potentially use domain fronting or similar techniques to reach hosts outside the allowlist." Unix-socket allowance can expose host services (the page's example is `/var/run/docker.sock`). Writable `$PATH` directories or shell startup files can lead to code execution in another context. `enableWeakerNestedSandbox` "considerably weakens security". `allowAppleEvents` "removes code-execution isolation" on macOS. Filesystem isolation can be disabled with `filesystem.disabled`; the page warns sandboxed commands can then write startup files and widen their own access on the next run. Project settings cannot set it.

Vendor security page ([code.claude.com/docs/en/security](https://code.claude.com/docs/en/security), undated; fetched 2026-10-13): the working-directory boundary in manual mode "is a permission prompt, so a Bash command you approve can still write anywhere your user account can". It recommends running untrusted content in virtual machines. It states "no system is completely immune to all attacks". Cloud sessions run in "an isolated, Anthropic-managed VM". Remote Control sessions: "No cloud VMs or sandboxing are involved."

### Claude Code advisories (GitHub Security Advisories and NVD, fetched 2026-10-13)

GitHub's advisory list for `anthropics/claude-code` ([page](https://github.com/anthropics/claude-code/security/advisories)) showed 10 entries on its first of 4 pages, dated May 6 to Oct 13, 2026. Entries marked "listing only" were seen in the list summary and not opened.

| Advisory | Published (NVD / GHSA) | Class | Affected, fixed | Enforcement note |
|---|---|---|---|---|
| [CVE-2026-25725](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-25725) | NVD 2026-02-06 | Bubblewrap did not protect `.claude/settings.json` when absent at startup; sandboxed code could inject hooks that run with host privileges on restart. | < 2.1.2 | Sandbox escape, fixed. NVD 3.1 score 10.0. |
| [CVE-2026-39861](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-39861) | NVD 2026-04-21 | Sandboxed processes created symlinks pointing outside the workspace; the unsandboxed process later followed them. Needed injected content. | < 2.1.64 | Sandbox escape, fixed. NVD 3.1 score 10.0; GitHub 4.0 score 7.7. |
| [CVE-2026-33068](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-33068) | NVD 2026-03-20 | Permission mode read from the repository's own `.claude/settings.json` before the trust dialog, allowing bypass on first open. | < 2.1.53 | Not a sandbox bug. NVD 3.1 score 8.8. |
| [GHSA-7835-87q9-rgvv](https://github.com/anthropics/claude-code/security/advisories/GHSA-7835-87q9-rgvv) / [CVE-2026-55607](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-55607) | GHSA Jun 25, 2026; NVD 2026-06-29 | Worktrees named `.git` and symlink manipulation plus git fsmonitor execution overwrote `.zshenv`, giving code execution outside the Seatbelt sandbox. | >= 2.1.38, < 2.1.163 | Sandbox escape, fixed. |
| [GHSA-5j29-h97v-84ch](https://github.com/anthropics/claude-code/security/advisories/GHSA-5j29-h97v-84ch) / [CVE-2026-103435](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-103435) | GHSA Oct 5, 2026; NVD 2026-10-07 | Path validated at permission check, re-resolved at write; symlink race let writes land outside the project. | < 2.1.129 | Permission-check gap, fixed. |
| [GHSA-pq7j-f95f-qfcv](https://github.com/anthropics/claude-code/security/advisories/GHSA-pq7j-f95f-qfcv) / CVE-2026-86063 | GHSA Oct 9, 2026 | Plugin install ran `git checkout` on the pinned SHA without checking HEAD; a branch named as the SHA was installed. | < 2.1.179 | Supply chain, fixed. CVE ID taken from the GHSA page; not checked in NVD. |
| [GHSA-4p2j-qj3c-6x84](https://github.com/anthropics/claude-code/security/advisories/GHSA-4p2j-qj3c-6x84) / CVE-2026-88066 | GHSA Oct 13, 2026 | Claude Desktop on Windows ran `git.exe` by bare name, so a malicious `git.exe` in the project directory ran when the folder opened. | Claude Desktop < 1.8089.0 | Claude Desktop, not the CLI. Not checked in NVD. |
| GHSA-v234-4jrq-mgg6 | Sep 25, 2026 | Claude Desktop (macOS): opening a malicious file in a Cowork folder ran commands. | Not shown | Listing only. |
| GHSA-5p5x-5294-qhp3, GHSA-3rwf-2g6p-c2f9 | May 6, 2026 | Local privilege escalation via directory junction in CoworkVMService; SSH host-key verification bypass on remote sessions. | Not shown | Listing only. |
| GHSA-fg94-h982-f3mm, GHSA-4vp2-6q8c-pvq2 | Jun 13 and Jun 25, 2026 | Exfiltration via a pre-approved WebFetch domain; insecure temp file in `/copy`. | Not shown | Listing only. |

Network-sandbox bypasses with no CVE: [The Register](https://www.theregister.com/a/5243662) (secondary, unverified; published 20 May 2026 per the page) reports two patched bypasses in the network sandbox, found by Aonan Guan. The later one is a SOCKS5 hostname null-byte injection that can defeat the allowlist filter. The article says the fix shipped in 2.1.88 on March 31, and that the reporter counts the network boundary as absent from sandbox GA until v2.1.90. The article quotes Anthropic declining a Claude Code CVE with "The root cause is in the library." Affected range is disputed in the article. None of them appears in the GitHub advisory list pages fetched for this section.

Further advisory-list rows (pages 2 to 4 of the same list, fetched 2026-10-13). Titles and dates are as returned by the listing fetch; none was opened. The IDE websocket advisory GHSA-9f65-56v6-gxw7 (Jun 23, 2025) is omitted as outside sandbox, permission and trust scope.

| GHSA | Published | Title as listed | Severity |
|---|---|---|---|
| GHSA-5cwg-9f6j-9jvx | Apr 17, 2026 | Insecure System-Wide Configuration Loading Enables Local Privilege Escalation on Windows | Moderate |
| GHSA-q5hj-mxqh-vv77 | Apr 24, 2026 | Trust Dialog Bypass via Git Worktree Spoofing Allows Arbitrary Code Execution | High |
| GHSA-mmgp-wc2j-qcv7 | Mar 18, 2026 | Workspace Trust Dialog Bypass via Repo-Controlled Settings File | High |
| GHSA-vp62-r36r-9xqp | Apr 20, 2026 | Sandbox Escape via Symlink Following Allows Arbitrary File Write Outside Workspace | High |
| GHSA-66q4-vfjg-2qhh | Feb 6, 2026 | Command Injection via Directory Change Bypasses Write Protection | High |
| GHSA-mhg7-666j-cqg4 | Feb 6, 2026 | Command Injection via Piped sed Command Bypasses File Write Restrictions | High |
| GHSA-ff64-7w26-62rf | Feb 6, 2026 | Sandbox Escape via Persistent Configuration Injection in settings.json | High |
| GHSA-4q92-rfm6-2cqx | Feb 6, 2026 | Permission Deny Bypass Through Symbolic Links | Low |
| GHSA-qgqw-h4xq-7w8w | Feb 3, 2026 | Command Injection in find Command Bypasses User Approval Prompt | High |
| GHSA-q728-gf8j-w49r | Feb 3, 2026 | Path Restriction Bypass via ZSH Clobber Allows Arbitrary File Writes | High |
| GHSA-vhw5-3g5m-8ggf | Feb 3, 2026 | Domain Validation Bypass Allows Automatic Requests to Attacker-Controlled Domains | High |
| GHSA-jh7p-qr78-84p7 | Jan 20, 2026 | Malicious repo configuration can trigger data leakage via environment configuration used before trust confirmation | Moderate |
| GHSA-xq4m-mc3c-vvg3 | Dec 3, 2025 | Command Validation Bypass Allows Arbitrary Code Execution | High |
| GHSA-7mv8-j34q-vp7q | Nov 20, 2025 | Sed Command Validation Bypass Allows Arbitrary File Writes | High |
| GHSA-5hhx-v7f6-x7gv | Nov 19, 2025 | Command execution prior to Claude Code startup trust dialog | High |
| GHSA-4fgq-fpq9-mr3g | Oct 3, 2025 | Command execution prior to Claude Code startup trust dialog | High |
| GHSA-66m2-gx93-v996 | Oct 3, 2025 | Permission deny bypass through symlink | Low |
| GHSA-2jjv-qf24-vfm4 | Sep 24, 2025 | Claude Code Vulnerable to Arbitrary Code Execution via Plugin Autoloading with Specific Yarn Versions | High |
| GHSA-j4h9-wv2m-wrf7 | Sep 9, 2025 | Claude Code vulnerable to arbitrary code execution caused by maliciously configured git email | High |
| GHSA-qxfv-fcpc-w36x | Sep 9, 2025 | Command Injection in Claude Code rg command allowed bypass of user approval prompt for command execution | High |
| GHSA-ph6w-f82w-28w6 | Sep 2, 2025 | Claude Code Vulnerable to Arbitrary Code Execution Due to Insufficient Startup Warning | High |
| GHSA-x5gv-jw7f-j6xj | Aug 15, 2025 | Permissive Default Allowlist Enables Unauthorized File Read and Network Exfiltration in Claude Code | High |
| GHSA-x56v-x2h6-7j34 | Aug 1, 2025 | Command Injection in Claude Code echo command allowed bypass of user approval prompt for command execution | High |
| GHSA-pmw4-pwvc-3hx2 | Aug 1, 2025 | Path Restriction Bypass in Claude Code Research Preview could allow unauthorized file access when path prefixes collide | High |

### OpenAI Codex

Undated OpenAI pages, redirected from `developers.openai.com/codex/...` to `learn.chatgpt.com/docs/...`, fetched 2026-10-13: [approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) and [sandboxing](https://learn.chatgpt.com/docs/sandboxing).

| Mechanism | Isolates | Enforced or advised | Stated limits |
|---|---|---|---|
| Sandbox modes: `read-only`, `workspace-write` (the "Auto" preset), `danger-full-access` | Writes and commands by mode. Full access "removes the filesystem and network boundaries". | Enforced. | Page marks `danger-full-access` "(not recommended)". Edits outside the workspace and network commands need approval. |
| Linux: `bwrap` plus `seccomp` by default; falls back to a bundled helper needing unprivileged user namespaces | Commands run under bubblewrap. | Enforced. | Page names no Landlock; startup warning if `bwrap` is missing. Uses the first `bwrap` on PATH. |
| macOS: Seatbelt via `sandbox-exec` | Commands. | Enforced. | Not stated. |
| Windows: native sandbox in PowerShell, Linux sandbox in WSL2 | Commands. | Enforced. | Names `elevated` and `unelevated` as legacy fallbacks. |
| Network off by default in `workspace-write`; `network_access = true` enables it | Commands' egress. | Enforced by configuration. | Web search is a separate switch. Network proxy scope "does not filter web search, app or connector tool calls, MCP server connections". DNS rebinding check "reduces DNS rebinding risk, but it does not eliminate it." |
| Approval policies: `on-request`, `never`, `granular`; `untrusted` retired | When the agent pauses. | Advised UX gate; the sandbox sets the technical boundary. | "Actions already allowed inside the sandbox run without extra review." |
| Devcontainer pattern | Host, per OpenAI's guidance. | Advised. | "Devcontainers provide substantial protection, but they do not prevent every attack." A malicious project "can exfiltrate anything available inside the devcontainer, including Codex credentials." |

Codex advisories and disclosures:

| Item | Date | Class | Affected, fixed | Status |
|---|---|---|---|---|
| [GHSA-w5fx-fh39-j5rw](https://github.com/openai/codex/security/advisories/GHSA-w5fx-fh39-j5rw) / CVE-2025-59532 | Published Sep 19, 2025 | Model-supplied `cwd` treated as writable root, allowing writes and execution outside the start folder. Network-disabled restriction not affected. | npm 0.2.0 to 0.38.0; fixed in CLI 0.39.0 and IDE extension 0.4.12. CVSS 4.0 8.6. | The only GHSA on the `openai/codex` advisory page as fetched. |
| [ZDI-26-305](https://www.zerodayinitiative.com/advisories/ZDI-26-305/) | Published Apr 28, 2026 | "allows remote attackers to bypass the sandbox"; "User interaction is required", as the target must use Codex to process a repository. | Affected version not shown. | Vendor rejected on Apr 13, 2026 as out of scope; vendor statement: "the vulnerability was not in the default Codex product surface". |
| Heapjack and Overpatch | Reported to OpenAI Aug 12, 2026 | Heapjack: shared V8 heap in Codex Desktop `node_repl` let untrusted code forge a validation token; worked in read-only mode with no approval. Overpatch: `apply_patch` granted write to parent directories of patch paths; a symlink widened it so a shell startup file was written. | Desktop build 26.818.21641; CLI 0.149.0. | No CVE and no OpenAI advisory, per [CSA research note](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/09/CSA_research_note_openai_codex_sandbox_escapes_20260922-csa-styled.pdf) (AI-assisted, not CSA-reviewed, dated 2026-09-22). That note cites the researcher's blog (Accomplish AI, Sep 15, 2026) and BleepingComputer; neither fetched, so unverified. |

### OpenHands

Sources: [sandboxes overview](https://docs.openhands.dev/openhands/usage/sandboxes/overview) and [SDK security guide](https://docs.openhands.dev/sdk/guides/security), both undated, fetched 2026-10-13.

- Providers: Docker ("Good isolation from your host machine", recommended); process ("No container isolation", labelled "unsafe, but fast"); remote for managed deployments. The overview page makes no statement on mounted files, port binding or host access.
- SDK confirmation policies: `AlwaysConfirm`, `NeverConfirm`, `ConfirmRisky` (needs an analyzer). No default confirmation policy is stated.
- Security analyzer rates actions LOW to HIGH, or UNKNOWN. Analyzers "classify actions at the boundary — before the tool runs, not after". The page says "The analyzer does not prevent execution". Its "What this does not do" list includes "A complete prompt-injection solution". Other listed limits: content past 30k characters is invisible; `thinking_blocks` are not scanned; `conversation.execute_tool()` bypasses the analyzer and confirmation policy. The page says the approach is "not: A sandbox replacement" and advises "Pair with Docker isolation for stronger safety guarantees."
- Enterprise-only Docker-in-sandbox: the enterprise docs describe unprivileged nested containers, no host Docker socket, and user-namespace remapping. Not fetched; per search snippet only, so unverified.

### Devin

Source: [Devin Enterprise VPC overview](https://docs.devin.ai/enterprise/vpc/overview) (undated, fetched 2026-10-13).

- Enterprise Cloud: "both Devin's brain and Devbox run in Cognition's secure, multi-tenant cloud."
- Customer-dedicated deployment: the brain stays in Cognition's cloud; the Devbox runs in a customer-isolated, single-tenant VPC.
- Session isolation: "Each Devin session runs on its own isolated machine."
- Egress: HTTPS/443 required. "Granting internet access to Devin's workspace is strongly recommended to ensure full functionality."
- Secrets handling and audit logs: not addressed on this page.
- Limits stated: "MFA VPNs are not compatible with Enterprise Cloud deployments."
- Enterprise security page and Trust Center not fetched; no claims made from them.

### Isolation primitives

| Primitive | Source (fetched 2026-10-13, undated) | What it isolates | Stated limits |
|---|---|---|---|
| bubblewrap | [README](https://github.com/containers/bubblewrap/blob/main/README.md) and [SECURITY.md](https://github.com/containers/bubblewrap/blob/main/SECURITY.md) | Namespaces and mounts built from arguments. | "bubblewrap is not a complete, ready-made sandbox with a specific security policy." Protection is "entirely determined by the arguments passed to bubblewrap." "bubblewrap is not a security boundary between the user and the OS" when not setuid. Limitations section: `--new-session` is needed against out-of-sandbox command execution; "Everything mounted into the sandbox can potentially be used to escalate privileges"; a bound D-Bus socket can run commands via systemd. Newer builds refuse to run setuid. |
| gVisor | [Security model](https://gvisor.dev/docs/architecture_guide/security/) | Application syscalls handled by a user-space kernel (Sentry); file access through Gofer processes. | Does not protect against hardware side channels; relies on the host for hardware attacks and resource exhaustion (cgroups); "the host kernel or hypervisor is ultimately responsible for defending against attacks from within malicious guests." The Sentry's host system API is "minimized to a safer, restricted set". "A sandbox is not a substitute for a secure architecture." No escape policy or CVE handling on that page. |
| Firecracker | [design.md](https://raw.githubusercontent.com/firecracker-microvm/firecracker/main/docs/design.md) | microVM: guest vCPU threads treated as "running malicious code", contained by nested trust zones. | "Firecracker does not perform any network traffic filtering"; egress "should be filtered at the host-level". Production use "should be started only via the `jailer` binary". Seccomp filters limit host syscalls. Side channels not addressed on the page. |
| Containers (Docker) | [Docker Engine security](https://docs.docker.com/engine/security/) (undated, fetched 2026-10-13) | Not stated on the fetched page. | Not stated. | The fetched page does not state that containers share the host kernel. Its only related sentence is "Docker containers are very similar to LXC containers, and they have similar security features." The shared-kernel point appears only in third-party search results, not cited. The gVisor page's statement that "the host kernel or hypervisor is ultimately responsible for defending against attacks from within malicious guests" is the primary-source comparison used here. |

## 2. Permission and approval models

### Claude Code

Sources: [permission modes](https://code.claude.com/docs/en/permission-modes), [hooks](https://code.claude.com/docs/en/hooks), [security](https://code.claude.com/docs/en/security), [sandboxing](https://code.claude.com/docs/en/sandboxing), [worktrees](https://code.claude.com/docs/en/worktrees). All undated, fetched 2026-10-13.

| Mechanism | Controls | Enforced or advised | Stated limits |
|---|---|---|---|
| Permission modes: `default` (manual), `acceptEdits`, `plan`, `auto`, `dontAsk`, `bypassPermissions` | What runs without a prompt. Manual runs reads only. `dontAsk` denies anything that would prompt. | Enforced by the client before a tool runs. | "Auto mode reduces permission prompts but does not guarantee safety." `bypassPermissions` "offers no protection against prompt injection or unintended actions." |
| Allow, ask and deny rules | Per-tool and content-scoped rules, evaluated before the tool runs. | Enforced by the client. Deny rules "block in every mode, including `bypassPermissions`". Allow rules "have no effect in `bypassPermissions`". | Ask rules on command content, such as `Bash(git push *)`, still prompt in sandboxed auto-allow. |
| Protected paths | Writes to Claude's configuration and repository state. Never auto-approved except in `bypassPermissions`. Settings allow rules do not pre-approve them. | Enforced by the client. | Scope is listed paths only. |
| Auto mode classifier | A separate model reviews actions outside the fixed decision order. It blocks by default: `curl \| bash`, sensitive data sent externally, production deploys, force push, `git reset --hard`, among others. | Model judgement. Vendor calls it a background safety check, not a guarantee. | Repeated blocks (3 in a row or 20 in total) pause auto mode. Thresholds are not configurable. Without a server verdict, "Claude Code denies the action rather than run it unreviewed." `rm` on critical paths is not reviewed by default. |
| Hooks (`PreToolUse` and others) | Can deny a tool call or return `allow`, `deny`, `ask` or `defer`. | Client-executed code. Exit 0 with no output leaves the call to the normal permission flow. | "On most events, when a hook fails or times out, Claude Code still carries out the action, so a policy hook with a wrong path or a crashing script lets everything through." A timed-out `command`, `http` or `mcp_tool` hook "doesn't block the tool call". Opt-in `"onFailure": "block"` on `command` and `http` hooks (v2.1.295 or later). The page says "use the permission system rather than a hook to enforce a hard allow or deny." Hooks run outside the sandbox. |
| Command-injection check | Asks before running a Bash command it cannot fully analyze, even with an allow rule for part of it. | Enforced in Manual mode. | Sandboxed commands can run without it. |
| Workspace boundary | Manual mode asks before file tools act outside the start folder. | Prompt, not OS enforcement. | "a Bash command you approve can still write anywhere your user account can." |
| Worktree isolation checks | Blocks edits to the main checkout from a worktree session, and git commands that redirect into it. | Enforced by the client. "You can't turn this check off" for command-shape checks. | "None of them tracks which files a shell command writes, so a command that writes into the main checkout without running git there, such as `cp` or a shell redirect, isn't refused by them." |
| Managed controls | `permissions.disableBypassPermissionsMode`, managed settings, managed MCP. | Enforced when delivered as managed settings. | Under an admin-required sandbox, repository settings that loosen it are ignored (section 1). |

Agent teams (experimental, disabled by default, [docs](https://code.claude.com/docs/en/agent-teams), fetched 2026-10-13): teammates "start with the lead's permission mode". Teammate permission prompts "appear in the lead session". A teammate "can't approve a permission prompt or supply consent on your behalf". In auto mode the classifier reviews inter-agent messages before delivery. A teammate's plan is approved "in the lead's session as soon as the request arrives, without the lead reviewing it".

### OpenAI Codex

Source: [approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) (undated, fetched 2026-10-13).

- Approval policies: `on-request`, `never`, `granular`. `untrusted` is retired. Approvals decide "when Codex pauses"; the sandbox decides "which files and network resources commands can access".
- Escalations cover "sandbox escalations, blocked network access, or side-effecting tool calls". Rules "allow, prompt, or forbid command prefixes outside the sandbox".
- "Approve for me" routes eligible requests to automatic review, which "doesn't change the sandbox boundary".
- CSA's research note (secondary, unverified) states that in the Overpatch case the approval gate "was itself a target the exploit could manipulate". Heapjack "required no approval click". See section 1 for both.

### OpenHands SDK

Source: [SDK security guide](https://docs.openhands.dev/sdk/guides/security) (undated, fetched 2026-10-13).

- Confirmation policies: `AlwaysConfirm`, `NeverConfirm`, `ConfirmRisky` (requires an analyzer). The default is not stated.
- Analyzer: "classify actions at the boundary — before the tool runs, not after", returning a level from LOW to HIGH, or UNKNOWN. Limits: "The analyzer does not prevent execution". `conversation.execute_tool()` "bypasses the analyzer and confirmation policy".

### Devin

Not researched in this run. The Devin VPC page fetched in section 1 does not describe an approval model.

### Policy as code

Claude Code's managed settings, hooks and permission rules are the only policy-as-code surface fetched in this run. OPA, Cedar or similar engines applied to agent actions were not searched.

## 3. Audit and provenance

### Harness logging and attribution

| Item | Publisher, date | What it records | Enforced or advised | Stated limits |
|---|---|---|---|---|
| OpenTelemetry export (Claude Code) | Anthropic, [monitoring usage](https://code.claude.com/docs/en/monitoring-usage) (undated; fetched 2026-10-13) | Metrics, events (`claude_code.tool_decision`, `claude_code.tool_result`, `claude_code.api_request`, `claude_code.user_prompt`) and optional traces. | Emitted by the client. Opt-in content fields. | Prompt text, tool input and tool content are redacted by default and enabled by `OTEL_LOG_USER_PROMPTS`, `OTEL_LOG_TOOL_DETAILS` and `OTEL_LOG_TOOL_CONTENT`. Assistant responses exclude thinking and tool-use blocks. The page makes no tamper-evidence claim. |
| Session transcripts (Claude Code) | Same page; settings index | Transcript entries in `~/.claude/projects/*/*.jsonl`. | Local files written by the client. | "The transcript entry format is internal to Claude Code ... and changes between versions." Retention set by `cleanupPeriodDays` ("how many days Claude Code keeps transcripts before deleting them"). No tamper protection is stated. |
| Commit and PR attribution (Claude Code) | Anthropic, [settings reference](https://code.claude.com/docs/en/settings-reference) (undated; fetched 2026-10-13) | The trailer added to commits and the line added to PR descriptions. | Configurable. Index text: `attribution.commit` "Change or hide the trailer Claude Code adds to commits"; `attribution.pr` "Change or hide the attribution line in pull request descriptions". `includeCoAuthoredBy` is deprecated. | Attribution is a text trailer. The fetched index does not say it is verified. Detailed defaults were not retrieved (page truncated). |
| Hook-based logging (Claude Code) | Anthropic, [hooks](https://code.claude.com/docs/en/hooks) and [security](https://code.claude.com/docs/en/security) pages (fetched 2026-10-13) | `PostToolUse`, `ConfigChange` and similar events, which a user may script. | Advised. Hooks fail open by default. | See section 2. |
| Cloud-session audit (Claude Code) | Anthropic, [security](https://code.claude.com/docs/en/security) (fetched 2026-10-13) | "All operations in cloud sessions are logged for compliance and audit purposes." | Vendor-operated. | Applies to Anthropic-hosted cloud sessions only. Not applied to local sessions. |
| Codex, OpenHands, Devin logs | Not found in fetched pages | Not established. | Not established. | Devin's VPC overview says nothing on audit logs. Codex and OpenHands logging was not searched. |

### Standards and frameworks

| Item | Publisher, date | Scope | Enforced or advised | Relevant text |
|---|---|---|---|---|
| SLSA Build Provenance | SLSA / Linux Foundation; v1.2 status "Approved" ([v1.2](https://slsa.dev/spec/v1.2/provenance), fetched 2026-10-13). v1.1 page shows "Retired" and "Version 1.2 is the current version" ([v1.1](https://slsa.dev/spec/v1.1/provenance), fetched 2026-10-13). | Build provenance of software artifacts. | Specification. No enforcement mechanism stated on the fetched pages. | Build provenance "tracks the output of a build process back to the source code used to produce that output" (v1.2). Provenance "is an attestation that a particular build platform produced a set of software artifacts" (v1.1 page). The fetched pages do not address who authored source code, including agent-written code. |
| OpenSSF Security-Focused Guide for AI Code Assistant Instructions | OpenSSF Best Practices and AI/ML Working Groups, dated 2025-08-01 ([guide](https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions), fetched 2026-10-13) | Instruction files for assistants (Claude markdown, Copilot, Cline, Cursor rules, Kiro steering). | Advised. Based on "expert opinion". | "Critically evaluate and edit AI-generated code just as you would code written by a human colleague." "Do not add dependencies that may be malicious or hallucinated." Guarantee of secure output: not stated. Agent permissions and sandboxing: not stated. |
| NIST SP 800-218A (SSDF community profile for generative AI) | NIST, [announcement](https://csrc.nist.gov/news/2024/nist-publishes-sp-800218a) dated July 26, 2024 (fetched 2026-10-13) | Practices for AI model and system producers and acquirers. | Advised. | "should be used in conjunction with SP 800-218". SSDF 1.2 draft SP 800-218r1 was announced Dec 17, 2025 ([CSRC SSDF news](https://csrc.nist.gov/projects/ssdf/news), fetched 2026-10-13, status "draft"). Final status not confirmed. |
| NIST AI 600-1 (Generative AI Profile) | NIST, [publication page](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence), July 26, 2024 (fetched 2026-10-13) | Cross-sectoral profile of AI RMF 1.0 for generative AI. | Voluntary. | "a cross-sectoral profile of and companion resource for the AI Risk Management Framework". The page says the profile responds to EO 14110. A search snippet, not fetched, says EO 14110 was revoked on January 20, 2025 (unverified). |
| OWASP Top 10 for Agentic Applications for 2026 | OWASP GenAI Security Project, Dec 9, 2025 ([resource](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026), fetched 2026-10-13; [press release](https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security/), dated Dec 9 and Dec 10, 2025) | Risks of autonomous and agentic AI systems. Items ASI01 to ASI10. | Advised. | The fetched pages do not show the ten titles. The press release names three risks in a group sentence: "Agent Behavior Hijacking", "Tool Misuse and Exploitation", "Identity and Privilege Abuse". Titles of ASI01 to ASI10 unverified. |
| ISO/IEC 42001:2023 | ISO (unverified) | Unverified in this run. | Unverified. | The ISO page returned HTTP 403 when fetched. The repository's `docs/standards.md` lists it. |

Not found in this run: an OpenSSF or NIST text on agent-written commit attribution. The fetched pages of these standards do not address an append-only audit of agent actions. OWASP's text was not retrieved beyond its publication date.

## 4. Deterministic control over agents

| Item | Publisher, date | Pattern | Enforced or advised | Stated limits |
|---|---|---|---|---|
| [Managed agents architecture](https://www.anthropic.com/engineering/managed-agents) | Anthropic, Apr 8, 2026 | Separates a session (the "append-only log of everything that happened"), a harness (the loop that routes tool calls) and a sandbox. | Architecture described by the vendor. Not an enforcement claim by itself. | "Because the session log sits outside the harness, nothing in the harness needs to survive a crash." Credentials: "make sure the tokens are never reachable from the sandbox where Claude's generated code runs" and "The harness is never made aware of any credentials." How the harness decides permissions: not stated. |
| Agents Rule of Two | Meta AI, [Oct 31, 2025](https://ai.meta.com/blog/practical-ai-agent-security/) | Within one session, an agent may hold at most two of: [A] process untrustworthy input, [B] access sensitive systems or private data, [C] change state or communicate externally. | Design rule. No enforcement mechanism described. | "until robustness research allows us to reliably detect and refuse prompt injection, agents must satisfy no more than two of the following three properties within a session." Where all three are needed, "the agent should not be permitted to operate autonomously" and it "at a minimum requires supervision". Limits: "should not be viewed as sufficient"; "a supplement — and not a substitute — for common security principles such as least-privilege." |
| CaMeL, "Defeating Prompt Injections by Design" ([arXiv:2503.18813](https://arxiv.org/abs/2503.18813), submitted 24 Mar 2025, first author Edoardo Debenedetti) | Academic paper | Design for LLM agents on untrusted data. Mechanism not retrieved in this run. | "provable security" per the abstract. | Abstract: "solving 77% of tasks with provable security". The undefended baseline on AgentDojo is 84%. |
| "Design Patterns for Securing LLM Agents against Prompt Injections" ([arXiv:2506.08837](https://arxiv.org/abs/2506.08837), submitted 10 Jun 2025) | Academic paper | "principled design patterns for building AI agents with provable resistance to prompt injection". | Design guidance. | Pattern count and names not retrieved. |
| "The Attacker Moves Second" ([arXiv:2510.09023](https://arxiv.org/abs/2510.09023), submitted 10 Oct 2025) | Academic paper | Adaptive attacks against 12 recent defenses. | Evaluation result. | "we bypass 12 recent defenses ... with attack success rate above 90% for most"; "the majority of defenses originally reported near-zero attack success rates"; "We argue that this evaluation process is flawed." Author affiliations: secondary source only, unverified. |
| Hooks as gates | Anthropic, [hooks](https://code.claude.com/docs/en/hooks) and [agent teams](https://code.claude.com/docs/en/agent-teams) (fetched 2026-10-13) | `PreToolUse` can deny a call. Exit code 2 on `TaskCompleted` prevents completion; on `TeammateIdle` it keeps the teammate working. | Client-executed. | Fail open by default (see section 2). `"onFailure": "block"` is opt-in for `command` and `http` hooks, v2.1.295 or later. |
| Auto mode classifier | Anthropic, [permission modes](https://code.claude.com/docs/en/permission-modes) (fetched 2026-10-13) | A separate model reviews actions outside a fixed decision order. Denies when no verdict is returned. | Model judgement, with a deterministic fallback to deny. | "Auto mode reduces permission prompts but does not guarantee safety." Pauses after 3 consecutive blocks or 20 in total. Thresholds are not configurable. |
| Cloud push restrictions | Anthropic, [security](https://code.claude.com/docs/en/security) (fetched 2026-10-13) | The GitHub proxy "rejects branch deletions and pushes of anything other than a branch". | Enforced for Anthropic-hosted cloud sessions. | "A rule that access can bypass doesn't block a session's push." Branch protection and rulesets apply only to the GitHub access the session uses. |
| Teammate messages | Anthropic, [agent teams](https://code.claude.com/docs/en/agent-teams) (experimental; fetched 2026-10-13) | Inter-agent messages are treated as coming "from another Claude session, not from you". | Enforced by the client. Auto mode also reviews messages before delivery. | A teammate "can't approve a permission prompt or supply consent on your behalf". |
| Sandbox-mediated controls, Codex | OpenAI, [approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) (fetched 2026-10-13) | Approval gate sits on top of the sandbox. "Approve for me" routes eligible requests to automatic review. | Enforced for sandbox boundary. Approval is a UX gate. | "Automatic review ... doesn't change the sandbox boundary." |
| Analyzer plus container, OpenHands | OpenHands, [SDK security](https://docs.openhands.dev/sdk/guides/security) (fetched 2026-10-13) | Risk analyzer classifies actions before the tool runs. | Advised. | "The analyzer does not prevent execution". "Pair with Docker isolation for stronger safety guarantees." |

Vendor-stated structure for whole-process isolation: Claude Code's [security page](https://code.claude.com/docs/en/security) recommends running the "whole Claude Code (local mode) process inside the sandbox runtime or a dev container", and its [sandboxing page](https://code.claude.com/docs/en/sandboxing) states that subagents "run in the same process as the parent session and use the same sandbox configuration".

Published architectures that separate trusted control from agents, found in this run: Anthropic's managed-agents post (session, harness and sandbox separated; the harness holds no credentials) and Meta's Rule of Two (a design constraint). Neither describes a controller that owns gate decisions over recorded evidence. Gated-merge controls found are the cloud push proxy and GitHub branch protection, both vendor-side. No evaluator-agent or verifier-agent architecture with stated enforcement was found in the fetched sources.

## 5. Prompt injection and supply-chain risk

### Documented incidents, 2025 to 2026

| Incident | Date | Vector | Impact stated | Response stated | Source |
|---|---|---|---|---|---|
| Amazon Q Developer extension for VS Code, version 1.84.0 | AWS bulletin published 2025/07/23, updated 2025/07/25; CVE-2025-8217 | Overly scoped GitHub token in CodeBuild. Malicious code committed and included in a release. The code's prompt instructed the agent to delete files and cloud resources. | AWS: "This issue did not affect any production services or end-users." Code "unsuccessful in executing due to a syntax error." | Credentials revoked and replaced; code removed; version 1.85.0 released. | [AWS bulletin](https://aws.amazon.com/security/security-bulletins/rss/aws-2025-015/) (fetched 2026-10-13; its text also cites AWS-2025-016, a numbering mismatch). Prompt and CLI flags from [The Register](https://www.theregister.com/2025/07/24/amazon_q_ai_prompt/) (secondary, unverified; July 24, 2025): the script passed the prompt to the Amazon Q CLI "including the arguments `--trust-all-tools` and `--no-interactive`". The bulletin gives no release dates for 1.84 or 1.85; the Register reports 1.84 released July 19 and 1.85 two days later. |
| Nx npm packages ("s1ngularity") | GitHub advisory [GHSA-cxm3-wv7p-598c](https://github.com/advisories/GHSA-cxm3-wv7p-598c) (CVE-2025-10894), published Aug 27, 2025; the page states it was withdrawn Jul 28, 2026 | Malicious versions of nx and plugins. The advisory says the code ran at install time, "scanned user's file system for text files, collected paths, and credentials", "modified the `.zshrc` and `.bashrc`", and posted "an encoded string to a github repo under the user's Github account". Supplementary: a [Snyk analysis](https://snyk.io/blog/weaponizing-ai-coding-agents-for-malware-in-the-nx-malicious-package/) (Aug 27, 2025) says a `telemetry.js` post-install script ran installed AI CLIs with `--dangerously-skip-permissions` (Claude Code), `--yolo` (Gemini CLI) and `--trust-all-tools` (Amazon Q). | Snyk: the initial foothold was "a flawed GitHub Actions CI workflow contributed via a Pull Request on August 21", "estimated to have been generated by Claude Code". Entry point disputed: one source names a stolen npm publishing token. | The advisory lists no patched versions. Shows affected versions only. | Advisory (fetched 2026-10-13); Snyk (fetched 2026-10-13, secondary). |
| GitHub MCP server, prompt injection via a public issue | May 26, 2025 | A malicious GitHub issue hijacks the agent, which pulls private repository data into context and leaks it "in an autonomously-created PR in the public repository". | Private repository data exposed. | Invariant recommends granular permission controls, least privilege, runtime security layers and monitoring. | [Invariant Labs](https://invariantlabs.ai/blog/mcp-github-vulnerability) (dated 2025-05-26; fetched 2026-10-13). The post states the flaw "affects any agent that uses the GitHub MCP server, regardless of the underlying model or implementation." |
| Claude Code plugin install (SHA pin bypass) | GHSA Oct 9, 2026 | A branch named as the pinned 40-character SHA was installed. | Attacker code installed. | Fixed in 2.1.179. | [GHSA-pq7j-f95f-qfcv](https://github.com/anthropics/claude-code/security/advisories/GHSA-pq7j-f95f-qfcv) (fetched 2026-10-13). |
| Claude Code hostile repository, permission mode | NVD 2026-03-20 | A repository's own settings set bypass mode before the trust dialog. | Trust prompt skipped on first open. | Fixed in 2.1.53. | [CVE-2026-33068](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-33068) (fetched 2026-10-13). |
| Codex, Heapjack and Overpatch (unverified) | Reported Aug 12, 2026 (per CSA note) | Shared V8 heap in Codex Desktop; `apply_patch` scope with a symlink in the CLI. | Sandbox escape. Heapjack worked in read-only mode with no approval. | Fixed (Desktop build 26.818.21641; CLI 0.149.0). No CVE or advisory. | [CSA research note](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/09/CSA_research_note_openai_codex_sandbox_escapes_20260922-csa-styled.pdf) (secondary, unverified: AI-assisted, not CSA-reviewed, dated 2026-09-22). |
| Claude Code network sandbox bypasses | Press article dated May 20, 2026; report dates not stated | SOCKS5 hostname null-byte injection defeats the allowlist filter. | The article calls it "especially dangerous when combined with prompt injection". | Fix in 2.1.88 per the article; no CVE or changelog note, per the reporter. | [The Register](https://www.theregister.com/a/5243662) (secondary, unverified). |

Sections 1 and 2 list the Claude Code and Codex sandbox and permission advisories in full.

### Vendor and standards guidance on prompt injection

- Anthropic, [security page](https://code.claude.com/docs/en/security) (fetched 2026-10-13): "Avoid piping untrusted content directly to Claude"; "Use virtual machines (VMs) to run scripts and make tool calls, especially when interacting with external web services"; "no system is completely immune to all attacks".
- OpenAI, [approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) (fetched 2026-10-13): "Prompt injection can cause the agent to fetch and follow untrusted instructions." "Treat web results as untrusted."
- OpenHands, [SDK security](https://docs.openhands.dev/sdk/guides/security) (fetched 2026-10-13): the analyzer is not "A complete prompt-injection solution".
- OWASP, Dec 9, 2025: agentic risk list, see section 3. Titles not retrieved.
- Attacker-adaptive evaluation: [arXiv:2510.09023](https://arxiv.org/abs/2510.09023) (section 4).

Enforced versus advised: the sandbox and permission controls in sections 1 and 2 are the controls vendors describe as enforced. The guidance above is advice. Where the incidents touched approval controls: CSA (secondary, unverified) states the Overpatch approval step "was itself a target the exploit could manipulate"; the Nx package script ran AI CLIs with permission prompts disabled; the Amazon Q payload was passed `--trust-all-tools`.

## 6. Multi-agent coordination risks

| Mechanism | Publisher, date | What it isolates | Enforced or advised | Stated limits |
|---|---|---|---|---|
| Claude Code `--worktree` and worktree subagents (`isolation: worktree`) | Anthropic, [worktrees](https://code.claude.com/docs/en/worktrees) (undated; fetched 2026-10-13) | Files and branch. "They isolate file edits." | Enforced checks: edits to the main checkout from a worktree session are blocked. | Shared with the main checkout: the `.git` directory, plugins, and approvals. "choosing 'Yes, and don't ask again' ... saves the rule to the main checkout's `.claude/settings.local.json`", so it applies in every worktree. Without a `.claude/skills` directory of its own, a worktree loads the main checkout's project skills. "None of them tracks which files a shell command writes"; `cp` or a shell redirect into the main checkout is not refused. |
| Worktree cleanup | Same page | Worktrees with changes or unpushed commits are kept. | Enforced by Claude Code. | Interactive exit prompts when a worktree holds work. A background sweep removes subagent worktrees older than `cleanupPeriodDays` when they hold no work. |
| Claude Code subagents | [Sandboxing](https://code.claude.com/docs/en/sandboxing) and [agent teams](https://code.claude.com/docs/en/agent-teams) comparison table (fetched 2026-10-13) | Own context window; results return to the caller. | Same process, same sandbox configuration. | "subagents run in the same process as the parent session and use the same sandbox configuration." |
| Agent teams (experimental, off by default) | Anthropic, [agent teams](https://code.claude.com/docs/en/agent-teams) (fetched 2026-10-13) | Separate context windows. Shared task list and mailboxes. | Advised for file ownership. | "Two teammates editing the same file leads to overwrites. Break the work so each teammate owns a different set of files." Teammates start with the lead's permission mode; "Teammate permission prompts appear in the lead session." Limits: "No session resumption with in-process teammates"; "Task status can lag"; "One team per session"; "No nested teams". |
| Codex app worktrees | OpenAI, [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees) (undated; fetched 2026-10-13) | Separate checkouts. The worktree "isn't checked out as a branch. It's in a detached HEAD state." | Product behaviour. | "Git prevents the same branch from being checked out in more than one worktree at a time." "By default, Codex keeps your most recent 15 Codex-managed worktrees." "Codex only copies ignored files that match `.worktreeinclude`." |
| Codex sandbox, parallel runs | [Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security) (fetched 2026-10-13) | Per-session sandbox. | Enforced by the sandbox. | No statement on conflicts between parallel agents. |

Other findings:

- Worktree isolation is file-level in the vendor text. Ports, databases and other shared resources are not mentioned by the fetched Anthropic or OpenAI pages. A third-party Codex guide says parallel dev servers "each worktree needs its own port". Unverified.
- Merge conflicts between worktree branches are a Git behaviour. The fetched pages do not describe how the harness resolves them. Claude Code's agent-teams page names overwrites as the risk and tells the user to split file ownership.
- Stale worktrees: a third-party guide reports that abandoned worktrees "can block later branch operations". Unverified in the vendor docs.
- Not researched: Cursor background agents, Devin and OpenHands parallel runs, and any harness's concurrency controls beyond Claude Code and Codex.

## Sources

Every URL below was fetched during this run on 2026-10-13. Page dates are as shown on the page; "undated" means no date was shown.

Sandboxing, permissions and harness docs (Anthropic, undated unless noted):
- [Sandboxing](https://code.claude.com/docs/en/sandboxing)
- [Security](https://code.claude.com/docs/en/security)
- [Permission modes](https://code.claude.com/docs/en/permission-modes)
- [Hooks](https://code.claude.com/docs/en/hooks)
- [Worktrees](https://code.claude.com/docs/en/worktrees)
- [Agent teams](https://code.claude.com/docs/en/agent-teams)
- [Monitoring usage](https://code.claude.com/docs/en/monitoring-usage)
- [Settings reference](https://code.claude.com/docs/en/settings-reference) (index and partial text)
- [Managed agents architecture](https://www.anthropic.com/engineering/managed-agents) (Apr 8, 2026)

OpenAI Codex (redirected from developers.openai.com to learn.chatgpt.com; undated):
- [Approvals and security](https://learn.chatgpt.com/docs/agent-approvals-security)
- [Sandboxing](https://learn.chatgpt.com/docs/sandboxing)
- [Git worktrees](https://learn.chatgpt.com/docs/environments/git-worktrees)
- [GHSA-w5fx-fh39-j5rw](https://github.com/openai/codex/security/advisories/GHSA-w5fx-fh39-j5rw) (Sep 19, 2025)
- [openai/codex advisories list](https://github.com/openai/codex/security/advisories)
- [ZDI-26-305](https://www.zerodayinitiative.com/advisories/ZDI-26-305/) (Apr 28, 2026)
- [CSA research note, Codex sandbox escapes](https://labs.cloudsecurityalliance.org/wp-content/uploads/2026/09/CSA_research_note_openai_codex_sandbox_escapes_20260922-csa-styled.pdf) (Sep 22, 2026)

Claude Code advisories (GitHub Security Advisories and NVD):
- [anthropics/claude-code advisories list, page 1](https://github.com/anthropics/claude-code/security/advisories)
- [anthropics/claude-code advisories list, page 2](https://github.com/anthropics/claude-code/security/advisories?page=2)
- [anthropics/claude-code advisories list, page 3](https://github.com/anthropics/claude-code/security/advisories?page=3)
- [anthropics/claude-code advisories list, page 4](https://github.com/anthropics/claude-code/security/advisories?page=4)
- [GHSA-cxm3-wv7p-598c, Nx malicious versions](https://github.com/advisories/GHSA-cxm3-wv7p-598c) (Aug 27, 2025; page states withdrawn Jul 28, 2026)
- [GHSA-7835-87q9-rgvv](https://github.com/anthropics/claude-code/security/advisories/GHSA-7835-87q9-rgvv) (Jun 25, 2026)
- [GHSA-5j29-h97v-84ch](https://github.com/anthropics/claude-code/security/advisories/GHSA-5j29-h97v-84ch) (Oct 5, 2026)
- [GHSA-pq7j-f95f-qfcv](https://github.com/anthropics/claude-code/security/advisories/GHSA-pq7j-f95f-qfcv) (Oct 9, 2026)
- [GHSA-4p2j-qj3c-6x84](https://github.com/anthropics/claude-code/security/advisories/GHSA-4p2j-qj3c-6x84) (Oct 13, 2026; Claude Desktop)
- [NVD CVE-2026-25725](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-25725) (published 2026-02-06; modified 2026-06-17)
- [NVD CVE-2026-33068](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-33068) (published 2026-03-20; modified 2026-06-17)
- [NVD CVE-2026-39861](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-39861) (published 2026-04-21; modified 2026-06-17)
- [NVD CVE-2026-55607](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-55607) (published 2026-06-29; modified 2026-06-30)
- [NVD CVE-2026-103435](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-103435) (published 2026-10-07; modified 2026-10-07)
- [The Register, Claude Code network sandbox bypasses](https://www.theregister.com/a/5243662) (press; May 20, 2026)

Other vendor and product docs:
- [Docker Engine security](https://docs.docker.com/engine/security/) (undated)
- [OpenHands sandboxes overview](https://docs.openhands.dev/openhands/usage/sandboxes/overview) (undated)
- [OpenHands SDK security guide](https://docs.openhands.dev/sdk/guides/security) (undated)
- [Devin Enterprise VPC overview](https://docs.devin.ai/enterprise/vpc/overview) (undated)
- [gVisor security model](https://gvisor.dev/docs/architecture_guide/security/) (undated; © 2026)
- [Firecracker design](https://raw.githubusercontent.com/firecracker-microvm/firecracker/main/docs/design.md) (undated)
- [bubblewrap README](https://github.com/containers/bubblewrap/blob/main/README.md) (undated)
- [bubblewrap SECURITY.md](https://github.com/containers/bubblewrap/blob/main/SECURITY.md) (undated)
- [Snyk, Nx "s1ngularity" analysis](https://snyk.io/blog/weaponizing-ai-coding-agents-for-malware-in-the-nx-malicious-package/) (Aug 27, 2025)
- [AWS security bulletin, Amazon Q Developer extension](https://aws.amazon.com/security/security-bulletins/rss/aws-2025-015/) (published 2025/07/23; updated 2025/07/25)
- [The Register, Amazon Q injected prompt](https://www.theregister.com/2025/07/24/amazon_q_ai_prompt/) (press; Jul 24, 2025)
- [Invariant Labs, GitHub MCP](https://invariantlabs.ai/blog/mcp-github-vulnerability) (May 26, 2025)

Standards and frameworks:
- [OpenSSF Security-Focused Guide for AI Code Assistant Instructions](https://best.openssf.org/Security-Focused-Guide-for-AI-Code-Assistant-Instructions) (Aug 1, 2025)
- [SLSA Build Provenance v1.2](https://slsa.dev/spec/v1.2/provenance) (status Approved; © 2026)
- [SLSA Build Provenance v1.1](https://slsa.dev/spec/v1.1/provenance) (status Retired)
- [NIST SP 800-218A announcement](https://csrc.nist.gov/news/2024/nist-publishes-sp-800218a) (Jul 26, 2024)
- [NIST SSDF news](https://csrc.nist.gov/projects/ssdf/news) (Dec 17, 2025 draft item)
- [NIST AI 600-1 publication page](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence) (Jul 26, 2024)
- [OWASP Top 10 for Agentic Applications for 2026](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026) (Dec 9, 2025)
- [OWASP GenAI press release](https://genai.owasp.org/2025/12/09/owasp-genai-security-project-releases-top-10-risks-and-mitigations-for-agentic-ai-security/) (Dec 9, 2025)
- [OWASP agentic applications page](https://genai.owasp.org/owasp-top-10-for-agentic-applications) (undated; no list shown)

Research papers:
- [CaMeL, arXiv:2503.18813](https://arxiv.org/abs/2503.18813) (submitted Mar 24, 2025)
- [Design Patterns for Securing LLM Agents, arXiv:2506.08837](https://arxiv.org/abs/2506.08837) (submitted Jun 10, 2025)
- [The Attacker Moves Second, arXiv:2510.09023](https://arxiv.org/abs/2510.09023) (submitted Oct 10, 2025)
- [Meta, Agents Rule of Two](https://ai.meta.com/blog/practical-ai-agent-security/) (Oct 31, 2025)

Not fetched, unverified: ISO/IEC 42001 (iso.org/standard/42001 returned HTTP 403).

## Relevance to this project

Facts only. Overlaps are listed first, then differences the fetched sources do not show.

### Overlaps with published practice

- **Controller separate from agent, credentials outside the agent.** ADR-0001 and `docs/execution.md` place policy, gates and credentials outside agent authority. Anthropic's managed-agents post (Apr 8, 2026) describes a similar split between session log, harness and sandbox, and states that the harness "is never made aware of any credentials". Claude Code's sandbox denies writes to its own settings, hooks and `.git/config` inside writable directories.
- **OS-level isolation, not prompt rules.** The vendor sandboxes (Claude Code, Codex) use Seatbelt on macOS and bubblewrap on Linux. `docs/execution.md` names prompt instructions, hooks and hashes as insufficient. Anthropic's hooks page says that on most events a failing hook lets the action proceed. Codex's sandbox is described as a "technical boundary" and the approval policy as "when the agent must stop and ask".
- **Sandbox is not the whole boundary.** Anthropic: "Sandboxing reduces risk but is not a complete isolation boundary." OpenHands: the analyzer "does not prevent execution". The project's `docs/spikes/isolation-capability-matrix.md` says the shell boundary is not a production boundary. The project's `docs/execution.md` requires proof per host before onboarding; Claude Code's sandbox docs state scope limits (Bash only, network proxy not TLS-inspecting).
- **Bubblewrap is a toolkit.** The bubblewrap README states it "is not a complete, ready-made sandbox with a specific security policy" and that protection depends on arguments. The project's spike evidence is per fixture for this reason (`isolation-capability-matrix.md`).
- **Human approval.** ADR-0001 binds human decisions to exact proposals. The fetched vendor pages describe per-action prompts and saved allow rules. None of them describes approval bound to a content identity.
- **Teammate or inter-agent messages are not authority.** Claude Code treats inter-agent messages as "from another Claude session, not from you". `docs/communication-protocol.md` says free-form notes cannot override structured fields or policy.
- **Role separation against a combined-capability rule.** Meta's Rule of Two limits untrusted input, sensitive access and external action to two per session. The project's roles split test, implementation and review across invocations, and implementation cannot access test-related inputs (`docs/execution.md`). The project does not state an equivalent per-session capability rule. Both are design rules; neither is a verified enforcement result.
- **Gated merge.** Claude Code's cloud push proxy rejects branch deletions and non-branch pushes. ADR-0003 keeps merge disabled until separately enabled and commissioned. Both place the push or merge step behind a controlled path.
- **Single run at a time.** ADR-0003 sets one active run and sequential stages. The vendor worktree and team features address concurrent editing; the project avoids that concurrency by policy.

### Differences the fetched sources do not show

- **Audit semantics.** Claude Code's OpenTelemetry events are redacted by default, and transcripts are local files whose format changes between versions. The fetched Claude Code pages state no append-only record, pre-action intent event, unknown-outcome state, or gap marker. The managed-agents post calls its session an "append-only log", without a stated tamper-evidence mechanism. `docs/audit.md` specifies all four.
- **Audit failure handling.** The fetched vendor pages describe no pause on audit-write failure and no degraded-continuation mode. `docs/audit.md` specifies both.
- **Protected verification inputs.** Claude Code's protected paths cover configuration and repository state (`.claude`, `.git/hooks`, shell startup files). They do not name test discovery, fixtures, golden data, thresholds or result parsers. `docs/execution.md` names all of these.
- **Evidence from the runner versus agent claims.** `docs/communication-protocol.md` separates agent reports (claims) from execution records observed by the controlled runner. The fetched vendor docs describe no equivalent split; hooks and logs are client-side.
- **Fail-closed on isolation loss.** Claude Code's sandbox runs commands unsandboxed when its dependencies are missing, unless `failIfUnavailable` is set. `docs/execution.md` says "Loss of isolation stops the run". The vendor default is the opposite, and the strict setting is opt-in.
- **Stale and late outputs.** `docs/communication-protocol.md` rejects late output from cancelled invocations or old owners. No fetched vendor page describes this.
- **Approval-gate independence.** Claude Code's auto mode uses a model classifier as the gate, with a fallback to deny. Claude Code hooks are deterministic client-side gates, and the hooks page describes them failing open on most events. The project's gates are specified as deterministic controller decisions over recorded evidence (`docs/architecture.md`). The fetched sources describe no controller that owns gate decisions over recorded evidence.
- **Topology.** Claude Code's local sandbox and worktrees run on the user's machine; its cloud sessions run in "an isolated, Anthropic-managed VM" (security page). The project's first topology is one operator and one controller on one commissioned Linux host (ADR-0003).

### Escape classes outside the proof list

In the fetched primary advisories the sandbox holds for the agent's own commands, and the escape happens when a later trusted step outside it reads or runs what the agent was allowed to write. Examples:

- Startup-loaded configuration: CVE-2026-25725 (`.claude/settings.json` hooks); GHSA-ff64-7w26-62rf ("Persistent Configuration Injection in settings.json", listing only).
- Symlinks followed by an unsandboxed process: CVE-2026-39861; GHSA-5j29-h97v-84ch (CVE-2026-103435); GHSA-vp62-r36r-9xqp (listing only).
- Shell startup files: GHSA-7835-87q9-rgvv (`.zshenv`); GHSA-cxm3-wv7p-598c (`.zshrc` and `.bashrc`, Nx package).
- Git metadata and the git executable: GHSA-7835-87q9-rgvv (worktree `.git` naming and git fsmonitor); GHSA-j4h9-wv2m-wrf7 (git email configuration, listing only); GHSA-4p2j-qj3c-6x84 (bare `git.exe` lookup, Claude Desktop on Windows).
- Pinned source identity: GHSA-pq7j-f95f-qfcv (checkout of a pinned SHA not verified).

Against the proof list in `docs/execution.md`:

- Named there: symlinks and path traversal; cache poisoning; result spoofing; late outputs. Also named in the contract text, outside the proof list: "configure steps and dependency hooks as code execution".
- Not named there: shell startup files; git configuration, git hooks, fsmonitor and worktree metadata; lookup of executables by bare name; agent harness configuration files in the workspace (for example `.claude/settings.json`); verification that a checked-out source matches its pinned identity. `docs/verification.md` lists "dependency locks" as input identities; it does not require checkout verification.
- The untrusted-execution list in `docs/execution.md` names controller code, policy, approved inputs, other roles' work, checkpoints, audit history and authoritative results. It does not name the classes above.
- CSA (secondary, unverified) calls the sandbox-intact, trusted-step-escapes pattern a "trust handoff", citing a July 2026 CSA note not fetched in this run.

### Gaps in this research

- ISO/IEC 42001 text not retrieved (HTTP 403). Standards claims for it rely on the repository's `docs/standards.md`, unverified here.
- SSDF 1.2 final status not confirmed.
- OWASP ASI01 to ASI10 titles not retrieved.
- Codex, OpenHands and Devin logging and audit features not found.
- Devin approval model not researched.
- Advisory-list rows from pages 2 to 4 are listing summaries; their details were not opened.
- Heapjack and Overpatch primary researcher post (Accomplish AI, Sep 15, 2026) not fetched.
- No published evaluator-agent or verifier-agent architecture with stated enforcement was found.
