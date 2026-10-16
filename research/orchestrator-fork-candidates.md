# Orchestrator fork candidates: Archon and Symphony

Could either project be forked as the base for this factory? Both were judged on their
source code, read on 15 October 2026. Nothing from either repository was installed,
built, run or tested. READMEs, specs and workflow files are cited only as claims or as
shipped configuration, and are marked as such.

Each of the three main requirements gets one of four labels:

- **enforced in orchestrator code**: the orchestrator does it, and the agent cannot
  change the outcome from its workspace;
- **configurable but the agent can tamper with it**: the mechanism exists, but the
  agent can reach what it depends on;
- **prompt or instruction text only**;
- **absent**: not found in this search. That means not found, not proven absent.

## Sources and pinned commits

| | Archon | Symphony |
|---|---|---|
| Repository | https://github.com/coleam00/Archon (default branch `dev`) | https://github.com/openai/symphony (default branch `main`) |
| How canonical was checked | GitHub API: owner `coleam00`, not a fork. The README links CI and docs to this repo. | GitHub API: owned by the `openai` organisation, not a fork. The README tells users to clone `github.com/openai/symphony`. OpenAI's announcement page (openai.com/index/open-source-codex-orchestration-symphony/) returned HTTP 403, so it was not read. |
| Commit read | `ca45f0d43d0b33d912b1c57fda561b383e78ae88`, committed 2026-10-15T23:39:59Z | `be10a1b79df723d6d7612b5651c8522704dafb2e`, committed 2026-09-15T22:12:07Z |
| Licence | MIT ([LICENSE](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/LICENSE)) | Apache-2.0 ([LICENSE](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/LICENSE)) |
| Language and runtime | TypeScript on Bun 1.4.2 ([package.json:68-69](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/package.json#L68-L69)). SQLite at `~/.archon/archon.db`, or Postgres when `DATABASE_URL` is set ([connection.ts:5-6](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/core/src/db/connection.ts#L5-L6)). | Elixir/OTP with Mix; also ships Burrito single-file binaries. Needs the `codex` CLI. |
| Size (line count) | `packages/`: about 226,000 lines of production `.ts`/`.tsx`, plus 304,000 lines of tests, across 16 packages. The largest single file, `dag-executor.ts`, is 12,479 lines. | `elixir/`: about 13,200 lines of production Elixir, plus 15,300 lines of tests. `SPEC.md` is 2,312 lines. |

Lines were counted with `wc`-style line counts. Tests are files named `*.test.*` or
under `test/` or `tests/`. Generated files are included, so treat the figures as rough.

All Archon links below go to commit `ca45f0d`; all Symphony links go to `be10a1b`.

## Archon

Archon is a DAG workflow engine. A YAML workflow declares nodes of kind `agent`, `exec`
(bash, bun or uv script), `loop`, `loop_group`, `gate` (human approval), `wait`,
`halt`, `include` and `workflow` (a child run). Agent nodes run through a provider
registry. Repository projects get one git worktree per run. "Folder" projects can
instead use a Docker container with an overlay filesystem.

### 1. Hard gates outside the agent

**Verified in source.**

- The engine runs `exec` (bash) nodes itself, in the run's working directory
  ([dag-executor.ts:3582-3590](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/dag-executor.ts#L3582-L3590)).
  A non-zero exit rejects the call, through promisified `execFile` or the owned-group
  path ([subprocess.ts:445](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/subprocess.ts#L445)).
  The node is then recorded as `failed`
  ([dag-executor.ts:3655-3664](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/dag-executor.ts#L3655-L3664)).
- The default trigger rule is `all_success`, so a failed upstream skips its dependants
  ([dag-executor.ts:2172](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/dag-executor.ts#L2172),
  [2192-2193](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/dag-executor.ts#L2192-L2193)).
  The author can opt a node out with `all_done`
  ([2208-2211](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/dag-executor.ts#L2208-L2211)).
- The workflow definition cannot be edited mid-run. Before the workflow is selected,
  `.archon` sources from the project, global and bundled scopes are copied to a capture
  under `ARCHON_HOME`
  ([workflow-source.ts:1-27](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/workflow-source.ts#L1-L27),
  [executor.ts:1139-1145](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/executor.ts#L1139-L1145)).
  The capture's digest is recorded on the run and checked again before reads; a
  mismatch fails the run
  ([workflow-source.ts:1109](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/workflow-source.ts#L1109),
  [1137](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/workflow-source.ts#L1137),
  [1169-1172](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/workflow-source.ts#L1169-L1172)).
  The gate command written in the YAML is frozen with it.
- The files the gate reads are not protected. Agent nodes and bash nodes share the run's
  `cwd`, so tests, package scripts and build config can be edited by an earlier agent
  node before the gate runs. On the host, bash nodes inherit the full `process.env`
  ([subprocess.ts:223-224](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/subprocess.ts#L223-L224)).
- By default, agents run without a harness sandbox. Claude always runs with
  `permissionMode: 'bypassPermissions'`
  ([claude/provider.ts:943-944](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/claude/provider.ts#L943-L944)).
  It is set unconditionally; no other production file under `packages/` sets it.
  Codex runs with `sandbox: 'danger-full-access'` and `approvalPolicy: 'never'`
  ([codex/provider.ts:1221-1222](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/codex/provider.ts#L1221-L1222)).
- `mutates_checkout: false` makes the engine fail a node that changed the working tree
  ([dag-node.ts:273-282](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/schemas/dag-node.ts#L273-L282)).
  This could back a read-only testing role. The check compares `git status --porcelain`
  output before and after, and is skipped when git fails
  ([dag-executor.ts:1324-1352](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/dag-executor.ts#L1324-L1352)).
  Judgement from reading that code: it would miss edits that the node also commits,
  and further edits to a file that was already dirty.

**Shipped configuration (the bundled `sdlc` pack, not the engine).**

- In `archon-validate`, an agent decides which checks to run. A script then runs them,
  and "green" comes from exit codes alone
  ([validate/README.md:6-9](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/.archon/workflows/sdlc/validate/README.md#L6-L9),
  [23](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/.archon/workflows/sdlc/validate/README.md#L23)).
- Whether CI is green "is judgment, so one agent prompt owns it"
  ([sdlc/README.md:49-50](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/.archon/workflows/sdlc/README.md#L49-L50)).

**Judgement.** On the host, the agent runs as the same OS user as the engine, so nothing
at OS level keeps it out of `ARCHON_HOME`, the capture or the SQLite database. The
digest check catches drift but is not a security boundary. Across runs, `.archon/` lives
in the repository the agent opens PRs against.

**Label: configurable but the agent can tamper with it.** The engine runs the command
and refuses to advance on failure. But the gate's inputs sit in the agent-writable
worktree, and the shipped pack lets agents choose the checks and judge CI.

### 2. Tests hidden from the implementer

**Verified in source.**

- Repository projects use one git worktree per run
  ([worktree.ts:217-230](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/isolation/src/providers/worktree.ts#L217-L230)).
  Every node in the run shares it.
- A `workflow:` child node can run in its own worktree
  ([dag-node.ts:1120](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/schemas/dag-node.ts#L1120)).
  It is a checkout of the same repository, tests included.
- The container backend cannot be used for repositories. It is folder-only
  ([backend-router.ts:62-68](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/isolation/src/backend-router.ts#L62-L68))
  and Claude-only
  ([container.ts:18](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/isolation/src/backends/container.ts#L18);
  `containerExec: false` for Codex at
  [codex/capabilities.ts:34](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/codex/capabilities.ts#L34)).
  It mounts the whole project root read-only, so tests stay readable
  ([container.ts:749-752](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/isolation/src/backends/container.ts#L749-L752)).
  No per-node mount exclusion was found.
- The only per-node read controls are Claude-specific and passed through to the Claude
  harness: `denied_tools` becomes `disallowedTools`
  ([claude/provider.ts:698-700](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/claude/provider.ts#L698-L700)),
  and `sandbox` (with `filesystem.denyRead`) goes to the Claude SDK unchanged
  ([dag-node.ts:91-125](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/schemas/dag-node.ts#L91-L125),
  [claude/provider.ts:792-795](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/claude/provider.ts#L792-L795)).
  Per [coding-agent-harnesses.md](coding-agent-harnesses.md), Claude Code's sandbox
  covers Bash commands but not its file tools, and it has an unsandboxed-retry escape
  hatch unless that is turned off. Codex and the other providers have no equivalent.
  No denyRead or path-hiding code was found in Archon itself.

**Label: configurable but the agent can tamper with it (Claude only, partial,
unverified).** For every other provider the label is **absent**. There is no OS-level
way to keep test files from the implementer's process.

### 3. Merge gate outside the agent

**Verified in source.**

- Agent processes get GitHub credentials. The Claude subprocess receives `process.env`
  ([claude/provider.ts:10-16](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/claude/provider.ts#L10-L16)).
  GitHub tokens are scrubbed only in per-user multi-user mode, for runs a specific user
  started. Server, webhook, cron and CLI runs, and solo installs, keep them
  ([github-token-policy.ts:19-21](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/utils/github-token-policy.ts#L19-L21),
  [107-108](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/utils/github-token-policy.ts#L107-L108)).
- There is a careful merge operation, `pr.merge`. It refuses unless the PR is open, not
  a draft, and at the approved head SHA, then reads the result back
  ([lifecycle.ts:1075-1115](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/adapters/src/forge/github/lifecycle.ts#L1075-L1115)).
  But it is a CLI subcommand, `archon forge pr.merge`
  ([help.ts:87](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/cli/src/help.ts#L87)),
  that authenticates from `GH_TOKEN`/`GITHUB_TOKEN`
  ([operations.ts:62-63](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/adapters/src/forge/github/operations.ts#L62-L63)).
  Any process holding that token can call it, or run `gh pr merge` directly.
- `gate` nodes pause the run until a human resolves them
  ([dag-node.ts:706-712](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/schemas/dag-node.ts#L706-L712)).
  That is engine-enforced ordering within a workflow, but an agent node before the gate
  still holds the token.
- The shipped `sdlc` pack stops at a ready PR. It "does not install a queue or authorize
  a merge" ([sdlc/README.md:414-418](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/.archon/workflows/sdlc/README.md#L414-L418)).
  Its validate docs warn, in prose only, not to give merge credentials to a gate
  ([validate/README.md:68](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/.archon/workflows/sdlc/validate/README.md#L68)).
- Neither the engine nor the pack configures or checks branch protection. Only GitHub's
  own rules stop a push to the default branch.

**Label: configurable but the agent can tamper with it.**

### Secondary items

- **GitHub Issues intake.** Webhooks are signature-checked
  ([adapter.ts:543-544](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/adapters/src/forge/github/adapter.ts#L543-L544)).
  An `issue_comment` with an @mention starts a conversation, and `issues.opened` is
  deliberately ignored
  ([adapter.ts:551-557](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/adapters/src/forge/github/adapter.ts#L551-L557)).
  `labeled` and `unlabeled` events are normalised
  ([source-conformance.ts:78-86](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/adapters/src/forge/github/source-conformance.ts#L78-L86)).
  How a label binds to a workflow start was not traced.
- **Runner and model independence.** There is a separate `provider-contract` package
  with a conformance suite. Claude, Codex and Pi are maintained providers
  ([registration.ts:6](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/provider-contract/src/registration.ts#L6)).
  Copilot and OpenCode are bundled but carry an "unowned, deprecated" notice
  ([copilot/registration.ts:26](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/community/copilot/registration.ts#L26),
  [opencode/registration.ts:21](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/community/opencode/registration.ts#L21),
  [deprecation.ts:9-14](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/providers/src/community/deprecation.ts#L9-L14)).
  Many node options are Claude-only: `sandbox`, `hooks`, `settingSources`.
- **Per-task isolation.** One git worktree per run for repositories, or a Docker overlay
  for folder projects (see requirement 2).
- **Persisted state and crash recovery.** State lives in the SQLite or Postgres database
  above. Runs resume from durable node events
  ([executor.ts:1161](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/executor.ts#L1161),
  [1219](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/workflows/src/executor.ts#L1219)),
  against the frozen source capture.
- **Event log.** A `remote_agent_workflow_events` table with a global order sequence.
  Deletes are allowed but copied to an archive table by a trigger
  ([000_combined.sql:507-518](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/migrations/000_combined.sql#L507-L518),
  [sqlite.ts:710-715](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/core/src/db/adapters/sqlite.ts#L710-L715)).
  Run deletion deletes events
  ([workflows.ts:2609-2625](https://github.com/coleam00/Archon/blob/ca45f0d43d0b33d912b1c57fda561b383e78ae88/packages/core/src/db/workflows.ts#L2609-L2625)).
  No UPDATE guard was found. Not append-only, and writable by the agent's OS user.
- **Maintenance.** Very active: 488 commits on `dev` since 2026-09-15, according to
  GitHub API pagination. Recent releases include v0.9.0 (2026-08-17) through v0.11.1
  (2026-09-25); only the latest five were listed. The API
  showed pushes after the pinned commit. The previous Python version is archived on a
  branch (README).

## Symphony

Symphony is a single-agent scheduler. It polls one tracker, creates one directory per
issue, runs workspace hooks, starts `codex app-server` in that directory, and keeps
sending turns while the issue stays in an active tracker state. It has no roles, stages
or steps. The workflow lives in the prompt body of `WORKFLOW.md`.

### 1. Hard gates outside the agent

**Verified in source.**

- After a turn, the only decision is whether the tracker issue is still in an active
  state and carries the required labels
  ([agent_runner.ex:113-138](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/agent_runner.ex#L113-L138),
  [156-171](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/agent_runner.ex#L156-L171)).
  The agent changes that state itself, through tracker tools.
- A normal exit is recorded as completed, and a continuation check is scheduled
  ([orchestrator.ex:208-224](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/orchestrator.ex#L208-L224)).
- Hooks are shell commands run with `sh -lc` in the workspace
  ([workspace.ex:404](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/workspace.ex#L404)).
  A failing `before_run` blocks the run, but it runs before the agent. `after_run`
  failures are ignored
  ([workspace.ex:245](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/workspace.ex#L245),
  [394-395](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/workspace.ex#L394-L395)).
  No post-agent check gates progress.
- The `specs.check` and `pr_body.check` Mix tasks are for Symphony's own development.
  No call site for them was found under `lib/` outside the tasks themselves.
- `WORKFLOW.md` is read from a host path given at startup, defaulting to the current
  directory, and hot-reloaded
  ([workflow.ex:11-14](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/workflow.ex#L11-L14)).
  Under the default sandbox the per-issue clone cannot write it. But keeping it in the
  repository is a stated goal ([SPEC.md:27-28](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md#L27-L28)), and the agent opens PRs against that
  repository.
- The shipped `WORKFLOW.md` tells the agent to run validation and confirm CI before
  moving to Human Review
  ([WORKFLOW.md:212-237](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/WORKFLOW.md#L212-L237)).
  This is prompt text.

**Label: prompt or instruction text only.** The orchestrator runs no gate command
after the agent.

### 2. Tests hidden from the implementer

**Verified in source.**

- There is one agent and one workspace per issue, with no role or step separation.
- The default turn sandbox allows writes in the workspace and reads everywhere
  (`readOnlyAccess: fullAccess`)
  ([config/schema.ex:570-578](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/config/schema.ex#L570-L578)).
- An explicit `turn_sandbox_policy` is passed to Codex unchanged
  ([config/schema.ex:320-344](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/config/schema.ex#L320-L344)).
  Any read restriction would come from Codex, not Symphony, and would apply to the whole
  run.
- An `after_create` hook could delete tests from the clone. That would leave the single
  agent with no tests at all, not hide them from one role.

**Label: absent.**

### 3. Merge gate outside the agent

**Verified in source and shipped configuration.**

- In the shipped workflow, the agent merges. A human moves the ticket to `Merging`, and
  the agent then runs the `land` skill until the PR is merged
  ([WORKFLOW.md:244-251](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/WORKFLOW.md#L244-L251)).
  The skill's stated precondition is "`gh` CLI is authenticated" and its goal is to
  squash-merge
  ([land/SKILL.md:15](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/.codex/skills/land/SKILL.md#L15),
  [23](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/.codex/skills/land/SKILL.md#L23)).
- The shipped workflow sets `shell_environment_policy.inherit=all`, `approval_policy:
  never` and `networkAccess: true`
  ([WORKFLOW.md:34-39](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/WORKFLOW.md#L34-L39)).
  With `never`, Symphony auto-approves Codex approval requests
  ([app_server.ex:55](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/codex/app_server.ex#L55),
  [761-781](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/codex/app_server.ex#L761-L781)).
- The Codex child inherits the orchestrator's environment, minus the tracker secret
  names only
  ([app_server.ex:199-208](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/codex/app_server.ex#L199-L208)).
  In Linear mode only `LINEAR_API_KEY` is stripped, so `GH_TOKEN` passes through
  ([config/schema.ex:421](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/config/schema.ex#L421)).
- In GitHub mode the GitHub token variables are stripped
  ([github/client.ex:21-31](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/github/client.ex#L21-L31)).
  But the host-side `github_api` tool accepts GET, POST, PATCH, PUT and DELETE on any
  path starting with `/`
  ([github/agent_tool.ex:9](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/github/agent_tool.ex#L9),
  [89-97](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/github/agent_tool.ex#L89-L97)).
  So `PUT /repos/{owner}/{repo}/pulls/{n}/merge` is reachable with the host token.
  Judgement: under the default read-everywhere sandbox, `gh`'s stored login on disk is
  also readable.
- The human step is a tracker state. The orchestrator does not dispatch issues in
  "Human Review", because it is not an active state
  ([orchestrator.ex:853-875](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/orchestrator.ex#L853-L875)).
  That part is real code. But the agent holds tracker write tools and can set
  `Merging` itself. With GitHub Issues, the only states are open and closed.
- Neither the code nor the shipped workflow configures or checks branch protection.

**Label: prompt or instruction text only.** The approval is a tracker state that the
agent can write, and the agent performs the merge.

### Secondary items

- **GitHub Issues intake.** A GitHub adapter polls one repository's issues, with
  `open`/`closed` as states. `tracker.required_labels` gates dispatch in code
  ([issue.ex:54-60](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/tracker/issue.ex#L54-L60)).
  Adapters also exist for Linear (the primary one), Jira, Asana and GitLab, behind a
  tracker behaviour
  ([tracker.ex:22-27](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/tracker.ex#L22-L27)).
- **Runner and model independence.** None. The runner protocol is the Codex app-server
  protocol by specification
  ([SPEC.md:950-970](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md#L950-L970)).
  The model is chosen through the `codex.command` string. No non-Codex runner code was
  found.
- **Per-task isolation.** A per-issue directory under `workspace.root`, with
  symlink-escape checks
  ([workspace.ex:483-510](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/workspace.ex#L483-L510)). It is populated by a hook, typically `git clone`. There is no
  container, apart from optional SSH worker hosts.
- **Persisted state and crash recovery.** Orchestrator state is in memory
  ([orchestrator.ex:29-44](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/orchestrator.ex#L29-L44)).
  Recovery comes from tracker state and preserved workspaces, with no database
  ([SPEC.md:57-58](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md#L57-L58)).
- **Event log.** Only rotating OTP disk logs, which wrap and overwrite
  ([log_file.ex:68-76](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/lib/symphony_elixir/log_file.ex#L68-L76)).
  No audit log.
- **Maintenance.** 47 commits in total, the first on 2026-03-04 and the last on
  2026-09-15. Releases v0.0.1 to v0.0.3 (July to September 2026), plus a nightly
  build. GitHub Issues are disabled on the repository (API `has_issues: false`); 8 PRs
  are open.
- **Stated intent, primary.** "Symphony is a low-key engineering preview for testing in
  trusted environments"
  ([README.md:10-11](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/README.md#L10-L11)).
  "Prototype software intended for evaluation only... We recommend implementing your
  own hardened version based on SPEC.md"
  ([elixir/README.md:7-8](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/elixir/README.md#L7-L8)).
  The spec does not require sandboxing
  ([SPEC.md:31-35](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md#L31-L35),
  [67](https://github.com/openai/symphony/blob/be10a1b79df723d6d7612b5651c8522704dafb2e/SPEC.md#L67)).
- **Stated intent, secondary only.** Help Net Security (28 April 2026,
  https://www.helpnetsecurity.com/2026/04/28/openai-symphony-codex-orchestration-linear/,
  fetched 15 October 2026 through a summarising fetch, not a raw read) reports that OpenAI "does not plan to maintain Symphony as a
  standalone product". It quotes no OpenAI wording. OpenAI's own page was not read
  (HTTP 403).

## Comparison

| Item | Archon | Symphony |
|---|---|---|
| 1. Hard gates outside the agent | Configurable but the agent can tamper with it. The engine runs the bash gate and blocks on a non-zero exit, and the workflow source is frozen. But the tests and config the gate reads are in the agent's worktree, and the shipped pack lets agents choose checks and judge CI. | Prompt or instruction text only. No post-agent check; progress follows tracker state that the agent writes. |
| 2. Tests hidden from the implementer | Configurable but the agent can tamper with it, for Claude only (partial, unverified): harness tool deny rules and a Bash sandbox with `denyRead`. Absent for other providers and at OS level. | Absent. One agent, and the default sandbox reads everywhere. |
| 3. Merge gate outside the agent | Configurable but the agent can tamper with it. There is a head-pinned merge op and a gate node, but agents inherit `GH_TOKEN` by default and can call the merge op or `gh`. | Prompt or instruction text only. The agent merges through `land`; human approval is a tracker state the agent can set. |
| GitHub Issues intake | Webhooks (signed): comment mentions and label events | Polling adapter with a required-labels filter |
| Runner seam | Yes. Provider contract and conformance suite; Claude, Codex, Pi maintained. Several options are Claude-only. | No. Codex app-server only. |
| Per-task isolation | Git worktree per run; Docker overlay for folder projects with Claude only | Directory per issue; optional SSH hosts |
| Persisted state and recovery | SQLite or Postgres; resume from durable events | In memory; rebuilt from the tracker |
| Audit log | Event table plus delete archive. Not append-only. | Rotating logs only |
| Licence, language, size | MIT; TypeScript on Bun; about 226k lines | Apache-2.0; Elixir; about 13k lines |
| Maintenance | Very active (488 commits in the last month; v0.11.1) | Preview; last commit 2026-09-15; Issues disabled; "implement your own" |

## Fit for this project

Measured against [execution.md](../docs/execution.md) and
[architecture.md](../docs/architecture.md) as current intent.

**What a fork of Archon would give.** A working DAG engine with agent, deterministic,
loop, approval and child-run nodes. Persisted runs with resume. A provider seam with
conformance tests. Worktree management. Signed GitHub webhooks. A forge layer whose
writes are read back. Three ideas worth reusing even without a fork:

- the digest-pinned capture of workflow source, so a run cannot drift under itself;
- the merge pinned to an approved head SHA, with read-back of the result;
- the provider conformance suite, which checks a provider against fixtures.

**What a fork of Archon would still need.**

- An execution boundary for repository runs. Today agents run on the host as the
  engine's user, with permission checks bypassed.
- Per-role filesystem views: tests unreadable by the implementer at OS level, and
  test inputs read-only for the testing role.
- Gates that run on a controller-owned snapshot with protected verification inputs,
  instead of the agent's worktree.
- Credentials removed from every agent environment, and merge moved behind the
  controller.
- An append-only audit log outside the agent's reach.
- Removal of the shipped pack's agent-judged CI and agent-chosen checks.

That work cuts across `dag-executor.ts` (12,479 lines), the providers and the isolation
package, in a codebase of about 226k lines that changes by hundreds of commits a month.
Archon is also TypeScript on Bun. ADR-0003 currently intends CPython 3.12, so a fork
would mean revisiting that decision. That is a cost to weigh, not the deciding reason.

**What a fork of Symphony would give.** A small, readable scheduler: polling,
reconciliation, retry with backoff, per-issue workspaces, required-label eligibility,
and a pattern for host-side tracker tools that keep tokens out of the child. All three
main requirements would have to be built from nothing, along with roles, stages, a
runner seam, durable state and an audit log. The maintainers call it a prototype and
recommend writing your own from the spec. Its tracker tool has the scope gap noted
above: it can reach any API path the token allows.

**Recommendation (judgement).** Do not fork either project. None of the six requirement
cells is "enforced in orchestrator code" without a way for the agent to tamper with it.
So a fork would buy plumbing, not the trust boundary that is this project's reason to
exist. The boundary would have to be built in either case, and retrofitting it into
Archon's engine means owning a large, fast-moving codebase whose design assumes trusted
agents. Instead, build the controller around the execution boundary first, and borrow
specific designs:

- from Archon: source capture with a digest, the head-pinned merge, the provider
  conformance suite, and the node and trigger-rule model;
- from Symphony: the reconciliation and retry loop, and host-side tracker tools,
  narrowed to an allow-list of operations.

If the team instead wants a running pipeline quickly for evaluation, Archon is the only
one of the two with roles, deterministic nodes and more than one runner. It should then
be treated as an untrusted prototype, not as the factory's control plane.

## Unverified items

- Whether Claude Code's file tools (Read, Grep, Glob) honour `sandbox.filesystem.denyRead`
  under `bypassPermissions`, and whether `disallowedTools` path patterns hold for
  subprocesses. Not tested; the harness research says file tools run outside the
  sandbox.
- What credentials Archon forwards into the Docker container for Claude. The `-e`
  forwarding was seen, but the key list was not traced.
- How Archon binds GitHub label events to workflow starts. Trigger configuration was
  not traced.
- Whether an agent in one Archon run can approve another run's `gate` node through the
  local CLI or API. The identity checks on approval were not traced.
- Codex's own default `shell_environment_policy` filtering, which matters for Symphony
  when the shipped `inherit=all` override is removed. Not checked in Codex source.
- OpenAI's own statement on maintaining Symphony. The announcement page returned 403;
  only a secondary report was read.
- Line counts are rough. Tests were identified by filename and folder, and generated
  files are included.
- Archon commits pushed after `ca45f0d` were not read.
