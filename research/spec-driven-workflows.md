# Spec-driven workflows for AI coding agents

Scope: spec-driven and plan-driven workflow tools for AI coding agents. Access date for all sources: 2026-10-13.

Markers: **Claimed** = the tool's README or docs say it. **Confirmed** = seen in the repo's code, hooks, templates, CLI source or release data. **Unverified** = could not fetch or confirm.

[S#] references point to the Sources section at the end, which gives the full URL and page date.

## OpenSpec (Fission-AI)

Method note: code facts were read through WebFetch summaries of raw source files. Identifiers are as the summary returned them; re-check before relying on exact strings.

| Item | Finding | Source |
|---|---|---|
| Repository | github.com/Fission-AI/OpenSpec, described as "Spec-driven development (SDD) for AI coding assistants." | [S1] |
| Licence | MIT | [S1] |
| Latest release | v1.14.1, published 2026-10-06 | [S2] |
| Last push | 2026-10-12 | [S1] |
| Maintainer | Fission-AI organisation. Individual maintainers: Unverified (MAINTAINERS.md not read) | |
| Node requirement | Node.js 20.19.0 or higher (Claimed) | [S3] |

**Artefacts (Claimed).** `openspec/specs/` holds live main specs. Each change is `openspec/changes/<name>/` with `proposal.md`, `specs/` (delta specs), `design.md` and `tasks.md`. Archived changes move to `openspec/changes/archive/YYYY-MM-DD-<name>/`. No constitution-equivalent file was found in the README or docs. Project context is a prompt-level input (docs/agent-contract.md §4.6) [S3][S4][S5].

**Delta sections (Claimed).** `## ADDED Requirements` (appended), `## MODIFIED Requirements` (replaces), `## REMOVED Requirements` (deletes; removing the last one retires the capability only with `retire_capabilities: true`), `## Purpose` (seeds a new spec only) [S4].

**Loop (Claimed).** Default profile: `/opsx:explore` (optional), `/opsx:propose`, `/opsx:apply`, `/opsx:archive`. Expanded profile adds `/opsx:new`, `/opsx:continue`, `/opsx:ff`, `/opsx:verify`, `/opsx:bulk-archive`, `/opsx:onboard` [S3]. The docs state "no phase gates, work on what makes sense" [S4].

**Agent hosts (Claimed).** The table lists 39 tools plus a shared `.agents` target. Claude Code is listed; its outputs are `.claude/skills/openspec-*/SKILL.md` and `.claude/commands/opsx/<id>.md`. Others include Codex, Cursor, GitHub Copilot, Gemini CLI, Kiro and Amazon Q [S6].

**Mechanical enforcement (Confirmed in source).**
- `src/core/archive.ts` calls `buildUpdatedSpec` and `writeUpdatedSpec` from `src/core/specs-apply.ts`. The merge is code; the files read import no model or agent call [S7][S8].
- Apply order is RENAMED, then REMOVED, then MODIFIED, then ADDED. The code throws on duplicate names across sections, on MODIFIED of a missing requirement, on ADDED of an existing requirement with different content, and on MODIFIED or RENAMED against a missing spec [S8].
- Archive refuses when delta validation fails (`archive_validation_failed` in JSON mode; exit 1 in human mode). It aborts before any write when a rebuilt spec fails validation (`archive_spec_validation_failed`; "Aborted. No files were changed.") [S7].
- Validation can be skipped with `--no-validate`, and spec updates with `--skip-specs` or a `skip_specs` marker in change metadata [S7].
- Retirement of a capability requires `retire_capabilities: true`; otherwise a spec whose last requirement was removed fails validation [S7][S8].

**Enforced by CLI per docs (Claimed).** `apply` blocks on missing required artefacts (`apply.requires`). `validate` exits 1 when any item fails. Archive in JSON mode is non-interactive [S5].

**Prompt-level.**
- Generated skill and command files come from `src/core/templates/skill-templates.ts`, which re-exports getters for propose, apply, archive and verify (Confirmed) [S9]. The text of those templates was not read: Unverified.
- docs/concepts.md asks that each task state how it is verified ("a test, command, or observable result"). That is prompt guidance, not checked by code [S4].
- `/opsx:verify` is "optional" in the docs [S4].
- No test-first mechanism (red-green, tester role or edit restriction) was found in the README, docs or `src/core` listing [S3][S10]. This is a negative from a partial search.

**Spec currency across tasks.**
- A change's deltas are merged into `openspec/specs/` by code during archive (Confirmed) [S7][S8]. The docs describe the same process (Claimed) [S4].
- Docs state two changes can touch the same spec file without conflict if they modify different requirements (Claimed) [S4].
- Only archive folds deltas today. Open PR #1813, "feat(sync): fold delta specs without archiving the change" (opened 2026-09-07, open at fetch), adds `openspec sync`. Its body says folding "currently happens only through archive" (Claimed, PR body) [S12].
- No cross-artifact consistency check was found. Open issue #783, "[Feature Request] Cross-artifact quality review between propose/ff and apply" (opened 2026-03-01, open, 16 comments), states that `openspec validate --strict` cannot detect semantic drift between proposal, specs, design and tasks (paraphrased by fetch) [S11].

**Limitations stated by maintainers or in issues.**
- README: "OpenSpec works best with high-reasoning models" and "benefits from a clean context window" (Claimed) [S3].
- README: the Stores feature is "beta" (Claimed) [S3].
- Release v1.14.1: requirements over 500 characters now warn, and this makes `openspec validate --strict` fail (Claimed, release notes via fetch summary) [S2].
- Issue #783 as above (open) [S11].
- Thoughtworks Technology Radar, April 2026 edition (published 2026-04-15), ring "Assess": the Radar calls OpenSpec "well-suited for existing systems" and advises teams to "continue to monitor and revisit native capabilities and re-evaluate the need for SDD tooling." It states no limitation of OpenSpec itself [S15].
- Maintainer concentration (contributors API, live): top contributor TabishB with 521 contributions; next human contributor clay-good with 177 [S14].
- Blog write-ups returned by search (Unverified; not fetched, not cited) report overhead on small changes, a learning curve, and that a Markdown spec does not guarantee code quality.
- The fetched critiques (Böckeler, Eberhardt) cover Spec Kit, Kiro and Tessl, not OpenSpec.

## GitHub Spec Kit

Method note: as for OpenSpec, code facts come from WebFetch summaries of raw files.

| Item | Finding | Source |
|---|---|---|
| Repository | github.com/github/spec-kit, described as "Toolkit to help you get started with SDD or any other process!" | [S16] |
| Licence | MIT | [S16] |
| Latest release | v1.1.3, published 2026-10-09 | [S17] |
| Last push | 2026-10-13 | [S16] |
| Launch | Blog post by Den Delimarsky, 2 September 2025 | [S18] |
| Language | Python package (`src/specify_cli`, `pyproject.toml`) | [S27] |

**Artefacts.**
- Per feature (Confirmed in `templates/`): `spec-template.md`, `plan-template.md`, `tasks-template.md`, `checklist-template.md`. Outputs go to a feature directory as `spec.md`, `plan.md`, `tasks.md` (Claimed) [S19][S20][S27].
- Constitution: `memory/constitution.md`, generated from `templates/constitution-template.md` (path Claimed in `spec-driven.md`) [S20][S27].
- Bugs and assessments: `.specify/bugs/<name>/` and `.specify/assessments/<name>/` (Claimed) [S19]. The `workflows/bugfix` and `workflows/assess` directories exist (Confirmed in listing); their content was not read: Unverified [S27].
- Workflow runs: `.specify/workflows/runs/<run_id>/` with `state.json`, `inputs.json`, `log.jsonl`, `workflow.yml` (Confirmed) [S24][S26].

**Loop.** README (Claimed): constitution, specify, plan, tasks, implement, then converge, plus bug and assess commands. The README command names are `/speckit-*` [S19]. `spec-driven.md` still uses `/speckit.plan` and similar names, so the two docs disagree [S20].

Bundled default workflow `workflows/speckit/workflow.yml` (name "Full SDD Cycle", version 1.0.1, Confirmed): `specify`, then gate `review-spec` (approve or reject, on_reject abort), then `plan`, then gate `review-plan`, then `tasks`, then `implement` [S25].

**Agent hosts.** `src/specify_cli/integrations/` has 43 subdirectories, including `claude`, `codex`, `copilot`, `cursor_agent`, `gemini`, `kiro_cli`, `opencode` and `generic` (Confirmed in listing). The list includes non-agent entries such as `catalog` [S27]. README says only "a supported AI coding agent" and links to an integrations reference that was not fetched [S19]. Agent count: Unverified.

**Mechanical enforcement (Confirmed in source unless noted).**
- The workflow engine executes steps through `STEP_REGISTRY`. Shell steps run with the user's privileges, and the engine writes state files itself [S24].
- A gate pauses the run for human review. Per `workflows/README.md` (Claimed), "Gates rely on human review, not an LLM verdict or code check." `on_reject` is `abort`, `retry` or `skip`; `abort` raises `WorkflowAbortError` [S24][S26].
- `engine.py` also validates gate `verdict_input` bindings. Its role was not determined [S24].
- Resume re-runs the current step so that gates can prompt again [S24].
- `workflows/README.md` (Claimed): `{{ ... }}` expressions in shell steps are substituted as raw text, with no quoting or escaping [S26].
- Community catalog workflows are not reviewed or endorsed by the project (Claimed) [S26].

**Prompt-level (Confirmed as text in templates; not enforced by code).**
- `templates/commands/implement.md`: "Follow TDD approach: Execute test tasks before their corresponding implementation tasks." Also "Halt execution if any non-parallel task fails." Also a yes/no prompt when checklists are incomplete [S21].
- `templates/plan-template.md`: a "Constitution Check" section with "*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*" No script or code referenced in that template enforces it [S23].
- `spec-driven.md` (Claimed) describes gates as "compile-time checks" and says "The LLM cannot proceed without either passing the gates or documenting justified exceptions." No code path enforcing this was found. This is a documentation claim, not a mechanism [S20].
- `templates/commands/converge.md`: reads spec, plan, tasks and constitution; its only write is appending a `## Phase N: Convergence` section to `tasks.md`; it must not modify `spec.md` or `plan.md` (Claimed, file text). Enforcement is prompt-level [S22].
- Extension hooks: the converge template contains hook sections that "direct the agent to invoke registered hooks" (Confirmed text) [S22]. A PR titled "Resolve extension hooks with native pre/post scripts" (#4883, created 2026-10-08) was open at fetch time [S28].

**Spec currency across tasks.**
- No code was found that re-syncs specs or plans after implementation. The `converge` command appends to `tasks.md` only (Claimed) [S22].
- Claims in `spec-driven.md` (Claimed): "Change a core requirement in the PRD, and affected implementation plans update automatically." and "Specifications stay in sync with code because they generate it." No mechanism for these was found in the files read [S20].
- Maintainer open question (Claimed, launch post): "Managing lots of Markdown files can get overwhelming." [S18]
- Third-party extension `openlore` adds a drift check after implementation: Unverified (search summary only, not fetched).

**Limitations stated by maintainers.**
- Launch post (Claimed): "Spec Kit is our experiment in making that transition real." [S18]
- `spec-driven.md` (Claimed): "Today, practicing SDD requires assembling existing tools"; "raw AI generation without structure produces chaos." [S20]
- README does not use the words "experimental", "beta" or "limitation" (checked by fetch) [S19].
- Open PRs at fetch time harden extension removal (#4745) and workflow and bundle step integrity (#4470). The Kiro CLI dispatch fix (#4798, 37 comments) is open [S28].

**Criticism from credible practitioners (fetched).**
- Birgitta Böckeler (Thoughtworks), martinfowler.com, published 15 October 2025: a single spec produced 8 files; "Overall they were just very verbose and tedious to review." "I frequently saw the agent ultimately not follow all the instructions." The tool was "overkill for the size of the problem" for a mid-sized feature [S30]. Last-updated date not shown.
- Colin Eberhardt, Scott Logic, published 26 November 2025: "I don't consider it a viable process, at least not in its purest form, as exemplified by Spec Kit." Feature 1: 2,577 lines of markdown and 689 lines of code, 3.5 hours of review. Iterative run: 8 minutes of agent time, "1,000 loc (and no markdown!)". After a bug surfaced, he did not update the spec, and he says specs are "Very rarely" revisited [S31].
- Both critiques were published in October and November 2025. Whether they still hold for v1.1.3 was not tested.

## AWS Kiro specs

Method note: Kiro is a closed product. Its mechanics below are Claimed from kiro.dev documentation. No Kiro source code was available to confirm them, so nothing here is Confirmed in code. The kiro.dev concepts page (`/docs/specs/concepts/`) returned 404 when fetched.

| Item | Finding | Source |
|---|---|---|
| Product | Kiro IDE and Kiro CLI | [S32] |
| Maintainer | Amazon Web Services; the IDE and CLI are "AWS Content" (©2026) | [S32] |
| Licence | Proprietary: "The Kiro IDE and Kiro CLI are each licensed to you as 'AWS Content' under the AWS Customer Agreement." Open-source components (Chromium, Bun, WebKit and others) keep their own licences | [S32] |
| Public GitHub repo | github.com/kirodotdev/Kiro is "the public issue and feedback tracker for Kiro." "The Kiro product source code is not hosted here." GitHub reports no licence. Repo pushed 2026-09-15 | [S38][S39] |
| Specs docs | "Page updated: October 2, 2026" | [S33] |
| Hooks docs | "Page updated: October 10, 2026" | [S34] |
| Steering docs | "Page updated: October 6, 2026" | [S35] |
| Changelog | Latest entry October 12, 2026. IDE 1.2.56 entry dated October 8, 2026 mentions "spec-only commands, and Hook matching" | [S36][S37] |

**Artefacts (Claimed).** Each spec has `requirements.md` (or `bugfix.md` for bug fixes), `design.md` and `tasks.md`. Requirements hold user stories and acceptance criteria "in structured notation". Design covers "technical architecture, sequence diagrams, and implementation considerations". Storage path for specs: not stated on the page [S33]. Steering files are markdown in `.kiro/steering/` (workspace) or `~/.kiro/steering/` (global). "AGENTS.md files do not support inclusion modes and are always included." The docs describe steering as "persistent knowledge about your project" [S35].

**Loop (Claimed).** Three phases: requirements (or bug analysis), design, tasks. Two variants, "Requirements-First and Design-First" [S33]. Quick Spec "can auto-generate all three artifacts without approval gates", which implies the other workflows have approval gates. The standard workflow's gates are not explicitly stated: Unverified [S33]. Tasks run individually or all at once. Kiro "builds a dependency graph of the tasks in your tasks.md and groups independent tasks into waves", and tasks in a wave run concurrently [S33].

Kiro's repo README (Claimed) says "Requirements Analysis can find contradictions, ambiguities, and gaps before coding begins," and that correctness testing "turns requirements into executable properties." Correctness appears as IDE-only in the docs' capability table [S38][S33].

**Agent hosts.** Kiro IDE and Kiro CLI only (Claimed) [S32]. The docs do not describe other hosts.

**Mechanical enforcement (Claimed, no code available).**
- Hooks "run shell commands or agent prompts automatically when specific events happen in your session." Command actions run a shell command in the project root. Agent actions inject a prompt. The docs list "block tool execution unless preconditions are met (PreToolUse)" as a use case, but do not describe a general blocking mechanism. Limitations and determinism: not stated [S34].
- Task wave execution is built by the tool from `tasks.md` dependencies (Claimed) [S33].
- Approval gates between phases for the standard workflow: Unverified.
- Test-first instructions, status markers for optional tasks, and test-run requirements: not stated in the pages read [S33].

**Spec currency across tasks.**
- Specs docs: no statement on updating a spec after code changes. The only update language refers to task status: "Real-time status updates as you implement." (Claimed) [S33].
- Steering: "Link to live workspace files to keep Steering current." And "Treat steering changes like code changes - require reviews." The page does not say whether the agent may edit steering files (Claimed) [S35].
- Böckeler (below) describes Kiro as "mostly spec-first" [S30].

**Limitations and criticism.**
- Birgitta Böckeler (Thoughtworks), martinfowler.com, published 15 October 2025: Kiro is "lightweight and mostly spec-first", but "for a small bug 'the workflow was like using a sledgehammer to crack a nut.'" The article predates the 2026 changelog entries above [S30].
- No official limitation statement was found on the specs, hooks or steering pages [S33][S34][S35].

## BMAD Method

Method note: code facts come from WebFetch summaries of raw files and the docs site's raw Markdown. Identifiers are as the summary returned them.

| Item | Finding | Source |
|---|---|---|
| Repository | github.com/bmad-code-org/BMAD-METHOD, described as "Breakthrough Method for Agile Ai Driven Development" | [S40] |
| Maintainer | "Copyright (c) 2025 BMad Code, LLC" | [S43] |
| Licence | MIT, with an added trademark notice that "does not grant any rights to use the trademarks for any other purpose" (see TRADEMARK.md). GitHub reports SPDX "NOASSERTION" (cause not checked) | [S40][S43] |
| Latest release | v6.12.2, published 2026-10-11 | [S41] |
| Main-branch README | Last commit 2026-10-11 ("docs: put the stable v6.12 install first and mark the skills route as a preview (#3076)") | [S42] |
| Last push | 2026-10-12 | [S40] |

**Release channels (Claimed, README on main).** "Stable: v6.12" installed with `npx bmad-method install`. "V7 Preview Alpha" installed with `npx skills add bmad-code-org/BMAD-METHOD`, described as "recommended for solo or small teams that can pivot as things will change before beta" and "Expect breaking changes between updates." The README now lists the stable route first [S42].

**Artefacts (Claimed, docs/plan/choose-a-planning-path.md).**
- Per change: `spec-<slug>.md` (from `bmad-spec`), plus companions [S44].
- Per epic: `tickets.toml`, epic envelopes, optional story files, and Build plans beside `tickets.toml` (from `bmad-ticket` and `bmad-build`) [S44][S45].
- Planning documents, optional: `prd-<slug>.md`, `architecture-<slug>.md`, `brief-<slug>.md`, `prfaq-<slug>.md`, `research-<topic>.md`, `ux-<slug>.md`, `DESIGN.md` [S44].
- Output folder: `_bmad-output` by default, configurable via `output_folder` in `_bmad/custom/config.toml` [S44][S45].
- Build plan frontmatter (Confirmed, `skills/bmad-build/plan-template.md`) [S50]: `status` one of draft, ready-for-dev, in-progress, in-review, built, done, blocked, dropped; `baseline_revision`; `route`; `risk`; `review`; `review_loop_iteration`.
- Build plan sections (Confirmed, same file) [S50]: a `frozen-after-approval` block (Intent, Boundaries & Constraints, I/O & Edge-Case Matrix), Code Map, Tasks & Acceptance, Implementation Notes, Plan Change Log, Review Triage Log, Design Notes, Verification.
- Project context: `bmad-project-context` writes a managed block inside the repo's `AGENTS.md`. "the user approves every write." "The agent never commits." (Claimed) [S53].

**Loop (Claimed, docs/plan/choose-a-planning-path.md) [S44].**
- Single session: `bmad-spec`, then `bmad-build`.
- Epic-sized: `bmad-spec`, then `bmad-ticket`, then `bmad-build` once per story, then `bmad-retrospective`.
- Autonomous: `bmad-build-auto`, one run per story. Docs say "Build Auto never moves a ticket to `done`" [S46].
- Optional planning skills can be used "in any order." The docs say "You don't need BMad for an obvious, low-risk edit." [S44]

**Build workflow (Confirmed, `skills/bmad-build/`).** Files `step-01-clarify-and-route.md`, `step-02-plan.md`, `step-03-implement.md`, `step-04-review.md`, `step-05-present.md`, `step-oneshot.md` [S51].
- Step 2: "Approve and continue": the user must approve the plan at Checkpoint 1 before implementation. The step halts for the choice [S47].
- Step 3: "Change `{plan_file}` status to `in-progress` in the frontmatter before starting implementation." Also "If no subagents are available, implement directly from the plan." Also "Content inside `<frozen-after-approval>` ... is read-only. Do not modify." [S48]
- Step 3 matrix audit: "A covering test that exists but did not run — unregistered, filtered out, skipped, or disabled — counts as missing." Also "never edit the expectation to match the code" when a test disagrees with the matrix [S48].
- Step 3 has no TDD or red-green instruction (checked) [S48].
- Step 4: review "lenses" run as subagents, and the step says to "launch them together, then wait for all results before continuing." Triage is by the current agent, which is told to "Disregard any severity a reviewing subagent assigned." The step does not run the test suite itself. Loopback: "bad_plan" to step 3, "intent_gap" to step 2. "If it exceeds 5, HALT and escalate to the human." [S49]

**Mechanical enforcement.**
- Confirmed: the runtime rules above are prompt text. Fetched text of steps 2 to 4 names no script that checks status transitions, the frozen block, the matrix or completion [S47][S48][S49].
- The repo has `tools/validate_skills.py`, `tools/validate_file_refs.py`, `tools/quality.py` and a `tools/tests` directory (names only, from listing) [S58]. Their contents were not read: Unverified. Whether they run at install or at workflow time was not determined.
- The `bmad-build` plan's `status` values and `review_loop_iteration` are written by the agent (Confirmed, step files and template) [S47][S50].
- `bmad-build-auto` halts with `blocked` when "the workflow ran into a situation where unattended execution would be unsafe", and when "review repair loop exceeded 5 iterations (non-convergence)" (Claimed) [S46].

**Spec currency across tasks.**
- `bmad-correct-course` (Confirmed in SKILL.md) [S52]: drafts edit proposals for stories, PRD, architecture and UI/UX documents. Epics are not edited directly; epic and story changes are listed "for the user to apply with `bmad-ticket`." The only file it writes is a Sprint Change Proposal. Each proposal needs Approve, Edit or Skip, and a final "Do you approve this Sprint Change Proposal for implementation? (yes/no/revise)."
- The plan template has a Plan Change Log and a Review Triage Log section (Confirmed, template headings) [S50]. Whether steps 3 and 4 write to them was not checked.
- No automatic propagation found. Open issue #2649, "Feature: human-gated intent reconciliation after implementation discoveries" (created 2026-07-29, open, 3 comments), proposes a human-approved checkpoint for discoveries the approved spec did not cover. Its author excludes automatic drift detection and automatic spec edits (paraphrased by fetch). The issue is a proposal, not a feature [S55].

**Limitations and criticism.**
- Maintainers (Claimed, README): v7 is "Preview Alpha" with "breaking changes between updates" [S42].
- Open bug #2987, "[BUG] Recursive Agent Delegation and Token Waste" (created 2026-09-29, open, reports BMAD 6.11.0): the dev agent calls itself and passes the same task on without work, wasting tokens (paraphrased by fetch; the reporter did not know how to reproduce it) [S56].
- Open issue #3008 (created 2026-10-01): title "[BUG] Installed bmad skill ships test_render_skill.py without the helpers module it imports" [S54].
- Ry Walker, "Research by Ry Walker," rywalker.com (page shows a release date of September 4, 2026 and a check date of September 15): "Process can outweigh the change." Poor fit includes "Trivial changes where the team can inspect the edit directly." "Unattended Build needs real subagents." "It does not establish a support SLA or demonstrate superior code quality." This is an independent write-up, not a controlled test [S57].
- The same write-up quotes a reviewer who found "the full workflow costly to read and slow to complete" (on v6.0.3, tested February, per the author). This is secondhand [S57].
- Credible practitioner tests from academic or vendor sources: not found in this run.

## Superpowers (obra)

Method note: skill text was read through WebFetch summaries of raw Markdown and scripts. Quotes are as the summary returned them.

| Item | Finding | Source |
|---|---|---|
| Repository | github.com/obra/superpowers, "An agentic skills framework & software development methodology that works." | [S59] |
| Maintainer | Jesse Vincent (GitHub `obra`, company "Prime Radiant") | [S71] |
| Licence | MIT | [S59] |
| Latest release | v7.0.0, published 2026-10-10T00:28:58Z per API. The release-notes header says 2026-10-09 | [S60][S62] |
| Last push | 2026-10-10 | [S59] |
| Repo created | 2025-10-09 | [S59] |

**Artefacts (Confirmed in skill text).**
- Design: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`, "committed" in a software repo. The user's preference overrides the path [S65].
- Plan: `docs/superpowers/plans/YYYY-MM-DD-<feature-name>.md`. The user's preference overrides the path [S66].
- Per-plan workspace: `.superpowers/sdd/<slug>/`, git-ignored, with a `progress.md` ledger and `task-N-tests.log` files [S69][S70].
- No constitution-equivalent file was found. The README lists principles, and the `using-superpowers` skill is injected as a bootstrap [S61][S63].

**Loop (Claimed, README; order confirmed in skill names).** README lists: brainstorming, using-git-worktrees, writing-plans, then subagent-driven-development or executing-plans, then test-driven-development, requesting-code-review, finishing-a-development-branch [S61]. Other skills: systematic-debugging, verification-before-completion, receiving-code-review, dispatching-parallel-agents, writing-skills, diagnosing-superpowers [S73].

**Agent hosts (Claimed, README).** 16 harnesses listed: Claude Code, Antigravity, Codex App, Codex CLI, Cursor, Devin CLI, Factory Droid, Gemini CLI, GitHub Copilot CLI, Grok Build CLI, Kimi Code, OpenCode, Pi, Qwen Code, Hermes Agent, Muse. Installation differs per harness. The repo has plugin directories for these (for example `.claude-plugin`, `.codex-plugin`, `.cursor-plugin`, `.opencode`) [S61][S73].

**Brainstorming (Confirmed, skills/brainstorming/SKILL.md) [S65].**
- Block: "Nothing gets built until your human partner approves the full description." Reading and exploring are allowed; building includes product code, scaffolding and installing dependencies.
- Steps include asking one question per message, sizing the work, writing the design doc, dispatching a fresh reviewer subagent with `builder-check-prompt.md`, sorting the reviewer's questions, then after approval invoking `superpowers:writing-plans`.
- No post-implementation step in this skill.

**Writing plans (Confirmed, skills/writing-plans/SKILL.md) [S66].**
- Each step is "one action with a checkable result." No minutes-per-step rule was found.
- Test steps include "the test's name and its assertions, as code". Code steps include "the exact signature ... the file it lives in". Verification steps include "the command to run and the output that means it passed."
- Task template starts "Write the failing test," then "Run it to make sure it fails."
- Self-review by the author (not a subagent): spec coverage, step scan, type consistency, review focus, proportion.
- Execution choice put to the user: subagent-driven or "Native" (inline). The user chooses before implementation.

**TDD (Confirmed, skills/test-driven-development/SKILL.md) [S68].**
- Rule: "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST." RED step: "MANDATORY. Never skip." The failure must be "because feature missing (not typos)."
- "Write code before the test? Delete it. Start over." "Delete means delete."
- Exceptions require the human's permission: throwaway prototypes, generated code, configuration files.
- Enforcement described: a "Before marking work complete" self-check. "You skipped TDD. Start over." No hook, reviewer or tool is named for enforcement.

**Subagent-driven development (Confirmed, skills/subagent-driven-development/SKILL.md) [S67].**
- "Execute plan by dispatching a fresh implementer subagent per task." Subagents "should never inherit your session's context or history." Implementers must not dispatch subagents of their own, and parallel implementation dispatches are prohibited.
- After each task: "a task review (spec compliance + code quality)". "spec compliance AND task quality are both required." A final whole-branch review runs once at the end.
- Fix loop: "Five rounds maximum per task." Rounds 1-3 resume the original implementer; rounds 4-5 use a fresh implementer on a stronger model. After the cap, "Adjudicate only at the cap."
- Controller rules: "Never fix findings yourself in the controller session." "Never skip the task review."

**Mechanical enforcement (Confirmed in scripts and hooks).**
- `skills/executing-plans/scripts/task-done PLAN_FILE TASK_NUMBER BASE -- TEST_COMMAND [ARGS...]`: runs the task's test command, writes full output to `task-N-tests.log`, and appends a ledger line to `progress.md` only if the command exits 0. `BASE` must pass `git rev-parse --verify` or the script exits 2. Pass or fail is decided by exit status, not by parsing output [S69].
- `skills/executing-plans/scripts/task-start` exists; its content was not read: Unverified [S73].
- `skills/subagent-driven-development/scripts/sdd-workspace PLAN_FILE`: creates `.superpowers/sdd/<slug>/` with a `.gitignore` containing `*` and a `plan-path` marker. Exits 2 on bad arguments or a missing plan file. It does not check for a prior step file [S70].
- `scripts/` at the repo root: `bump-version.sh`, `lint-shell.sh`, `package-codex-plugin.sh`, `render-antigravity-logo.sh`, `sync-to-codex-plugin.sh` (release and packaging tools, not runtime gates) [S73].
- `hooks/hooks.json`: registers SessionStart with matcher "startup|clear|compact" and runs `run-hook.cmd session-start` [S64].
- `hooks/session-start`: reads `skills/using-superpowers/SKILL.md` and prints it as context. It "only adds context. It ends with `exit 0` and never denies or blocks a tool call." [S63]
- Everything else (brainstorm gate, plan approval, TDD, reviewer verdicts, when `task-done` is called and with which test command) is prompt text. The agent must choose to call the scripts; no mechanism was found that forces that.
- `tests/` contains skill and harness tests, including `writing-skills`, `diagnosing-superpowers`, `explicit-skill-requests`, `systematic-debugging`, and `hooks`. Their content was not read: Unverified [S73].

**Spec currency across tasks.**
- The design doc is "committed" to the repo (brainstorming skill text) [S65]. No skill for updating a design or plan after implementation was found. Brainstorming's flow has no post-implementation step [S65].
- The subagent controller keeps `progress.md` as a ledger of completed tasks with commit ranges and test output [S69]. The skill text does not say the controller edits the plan or spec file (fetch summary of [S67]).
- Open issue #2342, "executing-plans: task-done ledgers the last log line as the test result" (created 2026-09-19, open, 11 comments): with `node --test`, the last line can be a duration, so the ledger does not show pass or fail. The script still gates on exit status (paraphrased by fetch) [S74].

**Limitations and criticism.**
- Maintainer statements (Claimed, README): "Superpowers updates are somewhat coding-agent dependent." "Hermes has no post-compaction hook." "We don't generally accept contributions of new skills." No experimental label found [S61].
- Open issue #743, "Im seeing slowness in responses since using the skill" (created 2026-03-15, 26 comments) [S72]. Open issue #512, "brainstorming/writing-plans SKILL efficiency" (created 2026-02-20, 17 comments) [S72].
- Open issue #1152 (created 2026-04-13, 14 comments): on a Codex Plus plan, a 20-step plan consumed a 5-hour token budget. The reporter attributes the cost to subagents and to separate spec and code-quality reviewers (paraphrased by fetch) [S75].
- Open issue #2017, "Retuning subagent driven development for Opus 6 and Sol 5.6" (created 2026-07-22, 14 comments). Title only; body not read [S72].
- Hands-on critiques are blog write-ups, several by users of the tool. Themes: overhead on one-line or small changes; clarifying questions before trivial edits. They are Unverified: search summaries only, not fetched, not cited. No independent benchmark was found.

## Other tools

Two additional tools were checked against primary sources: GSD (Get Shit Done) and Tessl. Other spec-driven tools were not surveyed in this run.

### GSD (Get Shit Done), now GSD Core

| Item | Finding | Source |
|---|---|---|
| Original repo | github.com/gsd-build/get-shit-done, MIT, `archived: true`, last push 2026-05-31. Description: "A light-weight and powerful meta-prompting, context engineering and spec-driven development system for Claude Code by TÂCHES." | [S77] |
| Active repo | github.com/open-gsd/gsd-core, MIT, not archived, created 2026-05-22, last push 2026-10-13. Description: "Git. Ship. Done - Core" | [S78] |
| Loop | Discuss, Plan, Execute, Verify, Ship. "capture implementation decisions before anything is planned." Commands named: `/gsd-new-project`, `/gsd-onboard` (Claimed) | [S76] |
| Artefacts | `STATE.md` and `CONTEXT.md` "survive session boundaries". Folder not stated (Claimed) | [S76] |
| Hosts | Nine runtimes named, "and more": Claude Code, OpenCode, Antigravity CLI, Kimi CLI, Kilo, Codex, Copilot, Cursor, Windsurf (Claimed) | [S76] |
| Verification | "the verify step walks through what was built and generates fix plans before a phase is declared done." No TDD statement (Claimed) | [S76] |

Mechanical enforcement, spec currency and criticism were not checked in source for GSD Core: Unverified. Its README does not mention the archived repo [S76]. Search results (secondary) say the original repo's owner archived it in June 2026. The API confirms `archived: true` but not the date: that date is Unverified.

### Tessl

| Item | Finding | Source |
|---|---|---|
| Launch post | "Tessl launches spec-driven framework and registry," by Simon Maple, 23 Sept 2025 | [S79] |
| Status at launch | Spec Registry "available now in open beta". Tessl Framework "which is in closed beta" (Claimed) | [S79] |
| Current status | Unverified. The docs page returned "Page Not Found" when fetched | [S80] |
| Sync and tests | Two spec modes: generate code from the spec, or document existing code (`@describe`). The Framework pairs specs "with tests to enforce guardrails" (Claimed) | [S79] |
| Open source | Not stated in the launch post. Search results describe a methodology tile on GitHub; the Framework's open-source status: Unverified | [S79] |

Böckeler (martinfowler.com, published 15 October 2025) calls Tessl "the only one of the three that explicitly aspires to a spec-anchored approach" and says it "is still in private beta" (fetch summary) [S30].

## Comparison

Rows restate facts from the sections above. "Unverified" marks something not confirmed in this run.

| Tool | Maintainer | Licence | Latest release or last push (fetched 2026-10-13) | Artefacts | Loop | Hosts (Claimed unless noted) | Mechanical enforcement (Confirmed in source unless noted) | Spec kept current by | Main criticism found |
|---|---|---|---|---|---|---|---|---|---|
| OpenSpec | Fission-AI (org) | MIT | v1.14.1, 2026-10-06; push 2026-10-12 | `openspec/specs/`, change `proposal.md`, delta `specs/`, `design.md`, `tasks.md` | explore, propose, apply, archive; expanded profile adds verify | 39 tools plus shared `.agents`, incl. Claude Code | Archive merges deltas in code; refuses on validation failure; `apply` blocks on missing artefacts (docs) | Archive folds deltas into main specs (code). `sync` in open PR #1813 | No cross-artifact check (issue #783, open). Delta folding only at archive (PR #1813). Top contributor 521 contributions, next human 177 |
| Spec Kit | GitHub (github/spec-kit) | MIT | v1.1.3, 2026-10-09; push 2026-10-13 | `spec.md`, `plan.md`, `tasks.md`, `memory/constitution.md`, checklists, `.specify/workflows/runs/` | constitution, specify, plan, tasks, implement, converge; bundled workflow has human gates | 43 integration directories (Confirmed, listing), incl. `claude`, `codex`, `copilot`, `gemini`, `kiro_cli` | Workflow engine runs steps; gates pause for humans; state persisted for resume. TDD, constitution check, halt rules are prompt text | `converge` appends to `tasks.md` only (Claimed). No re-sync code found | Böckeler: "just very verbose and tedious to review"; Eberhardt: "I don't consider it a viable process, at least not in its purest form" |
| Kiro | AWS (proprietary) | Proprietary, AWS Customer Agreement | Specs docs updated 2026-10-02; latest changelog 2026-10-12 | `requirements.md` or `bugfix.md`, `design.md`, `tasks.md`; steering in `.kiro/steering/` | requirements, design, tasks; Quick Spec skips gates; task waves | Kiro IDE and CLI only | Hooks run commands or prompts on events (Claimed); no source available | Not stated in docs; steering: "Link to live workspace files to keep Steering current" (Claimed) | Böckeler: "sledgehammer to crack a nut" for a small bug |
| BMAD Method | BMad Code, LLC | MIT with trademark notice | v6.12.2, 2026-10-11; push 2026-10-12. v7 is "Preview Alpha" | `spec-<slug>.md`, `tickets.toml`, build plan with frozen block, PRD, architecture; output `_bmad-output` | spec, build (plan, implement, review); auto build per story; epic path with tickets and retrospective | "an AI coding tool that supports skills"; Claude Code and Codex plugins named | Plan status and frozen block are prompt-enforced; review loop cap 5 is prompt text; `tools/validate_*.py` (names only, not read) | `bmad-correct-course` proposes changes; human approves; no auto-propagation. Issue #2649 (open) proposes a human-gated reconciliation | Open bugs #2987 (token waste) and #3008; Ry Walker: "Process can outweigh the change" |
| Superpowers | Jesse Vincent (`obra`) | MIT | v7.0.0, 2026-10-10 (API); push 2026-10-10 | `docs/superpowers/specs/`, `docs/superpowers/plans/`, `.superpowers/sdd/<slug>/progress.md` | brainstorm, plan, execute (subagent or inline), TDD, review, finish | 16 harnesses incl. Claude Code, Codex, Cursor, Gemini CLI, OpenCode | `task-done` records a task only if the test command exits 0; SessionStart hook only adds context; TDD, plan approval and review verdicts are prompt text | Design doc committed; no post-implementation sync skill found | Open issues #1152 (token budget), #743 (slowness), #2342 (ledger records last log line); blog critiques on overhead (Unverified) |
| GSD Core | open-gsd (org) | MIT | open-gsd/gsd-core push 2026-10-13. Original `gsd-build/get-shit-done` archived | `STATE.md`, `CONTEXT.md` | discuss, plan, execute, verify, ship | Nine runtimes | Unverified | Unverified | Unverified |
| Tessl | Tessl | Framework: Unverified | Launch post 2025-09-23; current status Unverified | Spec files; tests paired with specs | Unverified | Unverified | Unverified | Two spec modes (generate or document) | Fowler: "still in private beta" (published 2025-10-15) |

Stars and download counts were not used. Search results gave conflicting star counts for every tool.

## Relevance to this project

Facts and gaps only. Items are marked Confirmed (source read this run) or Claimed (tool docs). Bullets without a marker restate a finding from the sections above.

**Overlaps.**
- Controller and gates. OpenSpec's `archive.ts` refuses to write specs when delta validation fails, and validates the rebuilt spec before any write (Confirmed) [S7]. Spec Kit's workflow engine runs YAML steps, pauses at human gates (`review-spec` and `review-plan`, each `on_reject: abort`), and resumes from persisted run state (Confirmed) [S24][S25]. Superpowers' `task-done` records a task only when its test command exits 0 (Confirmed) [S69]. Other gates in the tools checked are prompt text.
- Role separation. Superpowers dispatches a fresh implementer subagent per task. A separate task reviewer checks spec compliance and code quality after each task. The controller is told never to fix findings itself and never to skip the task review. Implementers may not dispatch subagents (Confirmed) [S67]. BMAD runs review lenses as subagents, with a loop cap of 5 before HALT (Confirmed) [S49].
- Audit record. Spec Kit writes `state.json`, `inputs.json`, a copy of the workflow definition, and `log.jsonl`, which `engine.py` describes as an append-only event log (Confirmed) [S24]. Superpowers' `progress.md` gets one line per completed task with the commit range and the last line of test output (Confirmed) [S69]. OpenSpec keeps each change folder, including its artefacts, after archive (Claimed) [S4].
- TDD rule. Superpowers' TDD skill reads "NO PRODUCTION CODE WITHOUT A FAILING TEST FIRST", with delete-and-restart for code written first (prompt text, Confirmed) [S68]. Spec Kit's `implement.md` says "Follow TDD approach" (prompt text, Confirmed) [S21]. BMAD's matrix audit requires each row to be covered by a test that ran (prompt text, Confirmed) [S48].
- Human plan approval. BMAD's Step 2 requires the user to approve the plan at Checkpoint 1 before implementation (Confirmed) [S47]. Superpowers' brainstorming blocks building until the human approves the design (Confirmed) [S65].

**Plan authorship.**
- In the documented flows of all tools checked, the agent drafts the spec or plan from the human's prompt, and the human reviews it. Confirmed for Superpowers brainstorming and BMAD's plan approval; Claimed for OpenSpec, Spec Kit and Kiro.
- No tool checked documents a human-authored plan as the required input (Claimed, docs read).
- The project's plan is human-written (project context).

**Plan challenge.**
- Superpowers sends the design doc to a fresh reviewer subagent with `builder-check-prompt.md` (Confirmed, skill text) [S65].
- Spec Kit ships `analyze.md` and `clarify.md` command templates (Confirmed in listing; contents not read: Unverified) [S27]. Its `converge.md` reads spec, plan, tasks and constitution after implementation (Claimed) [S22].
- Spec Kit's plan template has a Constitution Check gate, which is prompt text (Confirmed) [S23].
- BMAD's review lenses examine the same code diff in parallel, and a triage step verifies each finding (Claimed, docs/build/review-a-change.md) [S81]. Step 4 runs the lenses as subagents (Confirmed) [S49].
- OpenSpec has no plan-challenge step in the docs read. Issue #783, open, requests a cross-artifact review between propose and apply [S11].

**Observed red.**
- `task-done` gates only on exit 0 of a test command that the agent chooses (Confirmed) [S69].
- The Superpowers TDD skill asks the agent to watch the test fail "because feature missing" (prompt text, Confirmed) [S68]. No tool checked records that a test failed before implementation, or stores that result as evidence.
- Spec Kit's `implement.md` says "Follow TDD approach" (prompt text, Confirmed) [S21]. BMAD's Step 3 has no TDD instruction (Confirmed) [S48].

**Host model.**
- Kiro is one proprietary product, offered as an IDE and a CLI (Claimed) [S32][S33].
- The other tools install into several hosts: Spec Kit 43 integration directories; OpenSpec 39 tools plus `.agents`; Superpowers 16 harnesses; GSD Core nine runtimes; BMAD requires "an AI coding tool that supports skills" (Claimed) [S6][S27][S61][S76][S42].

**Gaps relative to the stated failures.**
- Duplicated render path across tasks (copying kept tests green): no code-duplication check was found in any tool's files read.
- No cross-task memory of structure: OpenSpec's archive keeps deltas and the `openspec/specs/` tree; Spec Kit and Superpowers keep per-feature docs; BMAD keeps tickets and plan change logs. None was found to record code structure (types, modules, symbols) across tasks. Kiro's steering is described as "persistent knowledge about your project" (Claimed); no code-structure index was described in the pages read.
- Tester role that cannot edit: no tool found enforces a tester role that cannot edit production code. Superpowers' TDD is one agent following a rule. In BMAD, the implementing agent performs the matrix audit (step 3) and the current agent triages review findings (step 4).
- Test-run evidence: Superpowers' `task-done` records only the last line of output. Issue #2342 reports that with `node --test` the line is a duration, not pass or fail (Confirmed in issue; paraphrased) [S74].
- Gated merge: no merge step gated by a check was found in any tool. OpenSpec's archive writes spec files in the working tree. Superpowers' `task-done` gates its ledger entry on the test exit code, and the scripts read do not perform a merge. BMAD's `bmad-build-auto` "commits but does not push" (Claimed) [S46].
- Append-only audit log: Spec Kit writes `log.jsonl` per run (Confirmed; described as an "append-only event log" in engine.py's `RunState.append_log()` summary) [S24]. Superpowers' `task-done` appends a line to `progress.md` on success (Confirmed); whether anything rewrites the file was not checked [S69]. OpenSpec and BMAD write change logs inside the plan or change folder; append-only behaviour was not checked.
- Sandboxing: Spec Kit's shell steps "always run with the user's privileges" (Confirmed, engine.py summary) [S24]. No tool found sandboxes agent execution. Superpowers' hook and scripts are shell files; no sandboxing was found [S63][S69].
- Human approval: where an approval step was found, it is a prompt or a CLI pause. Spec Kit's bundled workflow has review gates (Confirmed) [S25]. BMAD has a plan checkpoint (Confirmed) [S47] and a course-correction approval (Confirmed) [S52]. Superpowers requires design approval (Confirmed, skill text) [S65]. The approval does not check that the approver read the tests or the code. Böckeler writes that checklists are interpreted by AI, "so there is no 100% guarantee that they will be respected" (Claimed) [S30].
- Criticism evidence: the fetched critiques (Böckeler; Eberhardt; Ry Walker) target process weight and review burden. None of them measured defects that the process prevented.

**Not covered.** Only the tools named above were fetched. No defect benchmark was found for any tool. Versions and docs change quickly: Spec Kit's README and `spec-driven.md` disagree on command names, and BMAD's stable and v7 channels differ.

**Unverified items, collected.** Tessl's current status; Spec Kit's agent count; Kiro's standard-workflow approval gates; GSD Core's internals (mechanics, spec currency, criticism); OpenSpec's skill and command template text; Spec Kit's `analyze.md`, `clarify.md`, `workflows/bugfix` and `workflows/assess` content; BMAD's `tools/` validators; Superpowers' `task-start` and `tests/` content; the GSD archive date; the openlore extension; blog critiques.

## Sources

Page date convention: the last commit date that touched the file (commits API, `commit.committer.date`); or the API field named; or the date printed on the page. "Not shown" where none exists. Access date for all: 2026-10-13. Listing URLs are directory or list responses, so they carry no page date.

**OpenSpec**
- [S1] https://api.github.com/repos/Fission-AI/OpenSpec: `pushed_at` 2026-10-12T12:42:49Z; `created_at` 2025-08-05.
- [S2] https://api.github.com/repos/Fission-AI/OpenSpec/releases/latest: `published_at` 2026-10-06T00:38:28Z (v1.14.1).
- [S3] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/README.md: last commit 2026-09-22T17:28:58Z.
- [S4] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/concepts.md: last commit 2026-09-23T15:04:37Z.
- [S5] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/agent-contract.md: last commit 2026-10-01T20:42:16Z.
- [S6] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/docs/supported-tools.md: last commit 2026-09-22T17:29:09Z.
- [S7] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/src/core/archive.ts: last commit 2026-10-01T20:42:16Z.
- [S8] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/src/core/specs-apply.ts: last commit 2026-09-23T16:11:13Z.
- [S9] https://raw.githubusercontent.com/Fission-AI/OpenSpec/main/src/core/templates/skill-templates.ts: last commit 2026-08-05T15:50:11Z.
- [S10] https://api.github.com/repos/Fission-AI/OpenSpec/contents/ and `/contents/src`, `/contents/docs`, `/contents/src/core`, `/contents/src/core/templates`: directory listings.
- [S11] https://api.github.com/repos/Fission-AI/OpenSpec/issues/783: `created_at` 2026-03-01T01:26:48Z; state open; 16 comments.
- [S12] https://api.github.com/repos/Fission-AI/OpenSpec/issues/1813 (PR): `created_at` 2026-09-07T13:57:48Z; state open.
- [S14] https://api.github.com/repos/Fission-AI/OpenSpec/contributors?per_page=5: live counts; no page date.
- [S15] https://www.thoughtworks.com/de/radar/tools/openspec: Radar edition April 2026, published 2026-04-15.

**GitHub Spec Kit**
- [S16] https://api.github.com/repos/github/spec-kit: `pushed_at` 2026-10-13T11:57:26Z; `created_at` 2025-08-21.
- [S17] https://api.github.com/repos/github/spec-kit/releases/latest: `published_at` 2026-10-09T19:30:56Z (v1.1.3).
- [S18] https://github.blog/2025-09-02-spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/: published 2 September 2025 (byline Den Delimarsky).
- [S19] https://raw.githubusercontent.com/github/spec-kit/main/README.md: last commit 2026-09-23T18:14:40Z.
- [S20] https://raw.githubusercontent.com/github/spec-kit/main/spec-driven.md: last commit 2026-06-23T13:27:26Z.
- [S21] https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/implement.md: last commit 2026-09-09T15:42:37Z.
- [S22] https://raw.githubusercontent.com/github/spec-kit/main/templates/commands/converge.md: last commit 2026-09-18T20:30:17Z.
- [S23] https://raw.githubusercontent.com/github/spec-kit/main/templates/plan-template.md: last commit 2026-07-10T14:45:31Z.
- [S24] https://raw.githubusercontent.com/github/spec-kit/main/src/specify_cli/workflows/engine.py: last commit 2026-10-09T17:44:26Z.
- [S25] https://raw.githubusercontent.com/github/spec-kit/main/workflows/speckit/workflow.yml: last commit 2026-09-03T11:51:15Z.
- [S26] https://raw.githubusercontent.com/github/spec-kit/main/workflows/README.md: last commit 2026-10-12T15:40:17Z.
- [S27] https://api.github.com/repos/github/spec-kit/contents/ and `/contents/templates`, `/contents/templates/commands`, `/contents/src/specify_cli`, `/contents/src/specify_cli/integrations`, `/contents/src/specify_cli/workflows`, `/contents/workflows`: directory listings.
- [S28] https://api.github.com/repos/github/spec-kit/issues?state=open&sort=comments&direction=desc&per_page=15: list; `created_at` per item (#4883 2026-10-08; #4798 2026-09-30; #4745 2026-09-25; #4470 2026-09-08).
- [S30] https://www.martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html: by Birgitta Böckeler, published 15 October 2025; last-updated not shown.
- [S31] https://blog.scottlogic.com/2025/11/26/putting-spec-kit-through-its-paces-radical-idea-or-reinvented-waterfall.html: by Colin Eberhardt, published 26 November 2025.

**Kiro**
- [S32] https://kiro.dev/license/: ©2026; no page date beyond that.
- [S33] https://kiro.dev/docs/specs/: "Page updated: October 2, 2026."
- [S34] https://kiro.dev/docs/hooks/: "Page updated: October 10, 2026."
- [S35] https://kiro.dev/docs/steering/: "Page updated: October 6, 2026."
- [S36] https://kiro.dev/changelog/index: latest entry 2026-10-12; entries listed 2026-10-08, 2026-10-05, 2026-10-01.
- [S37] https://kiro.dev/changelog/ide/1-2-56/: entry date October 8, 2026.
- [S38] https://raw.githubusercontent.com/kirodotdev/Kiro/main/README.md: README commit date not shown.
- [S39] https://api.github.com/orgs/kirodotdev/repos?per_page=30&sort=pushed: list; `pushed_at` 2026-09-15T14:31:12Z for kirodotdev/Kiro.

**BMAD Method**
- [S40] https://api.github.com/repos/bmad-code-org/BMAD-METHOD: `pushed_at` 2026-10-12T21:39:24Z; `created_at` 2025-04-13.
- [S41] https://api.github.com/repos/bmad-code-org/BMAD-METHOD/releases/latest: `published_at` 2026-10-11T05:57:04Z (v6.12.2).
- [S42] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/README.md: last commit 2026-10-11T21:12:30Z.
- [S43] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/LICENSE: last commit 2026-01-18T23:03:47Z.
- [S44] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/plan/choose-a-planning-path.md: last commit 2026-09-28T05:29:49Z.
- [S45] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/plan/set-up-the-ticket-tree.md: last commit 2026-10-02T14:08:35Z.
- [S46] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/build/autonomous-development-loops.md: last commit 2026-10-03T05:29:51Z.
- [S47] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-build/step-02-plan.md: last commit 2026-10-06T16:15:28Z.
- [S48] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-build/step-03-implement.md: last commit 2026-09-29T07:09:44Z.
- [S49] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-build/step-04-review.md: last commit 2026-10-06T16:15:28Z.
- [S50] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-build/plan-template.md: last commit 2026-10-03T03:22:00Z.
- [S51] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-build/workflow.md: last commit 2026-10-06T16:24:30Z.
- [S52] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-correct-course/SKILL.md: last commit 2026-09-28T15:33:29Z.
- [S53] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/skills/bmad-project-context/SKILL.md: last commit 2026-09-29T12:29:25Z.
- [S54] https://api.github.com/repos/bmad-code-org/BMAD-METHOD/issues?state=open&sort=comments&direction=desc&per_page=12: list; #3008 `created_at` 2026-10-01T19:38:54Z.
- [S55] https://api.github.com/repos/bmad-code-org/BMAD-METHOD/issues/2649: `created_at` 2026-07-29T18:17:33Z; state open.
- [S56] https://api.github.com/repos/bmad-code-org/BMAD-METHOD/issues/2987: `created_at` 2026-09-29T07:48:22Z; state open.
- [S57] https://rywalker.com/research/bmad-method: release date shown as September 4, 2026; check date September 15 (page-stated).
- [S58] https://api.github.com/repos/bmad-code-org/BMAD-METHOD/contents/, `/contents/skills`, `/contents/skills/bmad-build`, `/contents/skills/bmad-spec`, `/contents/tools`, `/contents/docs`, `/contents/docs/build`, `/contents/docs/plan`: directory listings.

**Superpowers**
- [S59] https://api.github.com/repos/obra/superpowers: `pushed_at` 2026-10-10T03:03:30Z; `created_at` 2025-10-09T19:45:18Z.
- [S60] https://api.github.com/repos/obra/superpowers/releases/latest: `published_at` 2026-10-10T00:28:58Z (v7.0.0).
- [S61] https://raw.githubusercontent.com/obra/superpowers/main/README.md: last commit 2026-10-10T00:28:04Z.
- [S62] https://raw.githubusercontent.com/obra/superpowers/main/RELEASE-NOTES.md: last commit 2026-10-10T00:28:04Z; v7.0.0 header dated 2026-10-09.
- [S63] https://raw.githubusercontent.com/obra/superpowers/main/hooks/session-start: last commit 2026-10-10T00:28:04Z.
- [S64] https://raw.githubusercontent.com/obra/superpowers/main/hooks/hooks.json: last commit 2026-07-24T00:27:16Z.
- [S65] https://raw.githubusercontent.com/obra/superpowers/main/skills/brainstorming/SKILL.md: last commit 2026-10-10T00:28:04Z.
- [S66] https://raw.githubusercontent.com/obra/superpowers/main/skills/writing-plans/SKILL.md: last commit 2026-09-25T18:06:27Z.
- [S67] https://raw.githubusercontent.com/obra/superpowers/main/skills/subagent-driven-development/SKILL.md: last commit 2026-09-19T00:31:35Z.
- [S68] https://raw.githubusercontent.com/obra/superpowers/main/skills/test-driven-development/SKILL.md: last commit 2026-09-19T00:31:35Z.
- [S69] https://raw.githubusercontent.com/obra/superpowers/main/skills/executing-plans/scripts/task-done: last commit 2026-10-10T00:28:04Z.
- [S70] https://raw.githubusercontent.com/obra/superpowers/main/skills/subagent-driven-development/scripts/sdd-workspace: last commit 2026-10-10T00:28:04Z.
- [S71] https://api.github.com/users/obra: profile; no page date.
- [S72] https://api.github.com/repos/obra/superpowers/issues?state=open&sort=comments&direction=desc&per_page=12: list; `created_at` per item (#743 2026-03-15; #512 2026-02-20; #2017 2026-07-22).
- [S73] https://api.github.com/repos/obra/superpowers/contents/, `/contents/skills`, `/contents/skills/executing-plans`, `/contents/skills/executing-plans/scripts`, `/contents/skills/subagent-driven-development`, `/contents/skills/subagent-driven-development/scripts`, `/contents/hooks`, `/contents/scripts`, `/contents/tests`: directory listings.
- [S74] https://api.github.com/repos/obra/superpowers/issues/2342: `created_at` 2026-09-19T13:23:37Z; state open.
- [S75] https://api.github.com/repos/obra/superpowers/issues/1152: `created_at` 2026-04-13T17:42:24Z; state open.

**GSD Core and GSD**
- [S76] https://raw.githubusercontent.com/open-gsd/gsd-core/main/README.md: last commit 2026-07-15T02:49:44Z.
- [S77] https://api.github.com/repos/gsd-build/get-shit-done: `pushed_at` 2026-05-31T17:46:54Z; `archived` true.
- [S78] https://api.github.com/repos/open-gsd/gsd-core: `pushed_at` 2026-10-13T12:30:58Z; `created_at` 2026-05-22T11:36:21Z.

**Tessl**
- [S79] https://tessl.io/blog/tessl-launches-spec-driven-framework-and-registry: published 23 Sept 2025, by Simon Maple.
- [S80] https://docs.tessl.io/use/spec-driven-development-with-tessl: returned "Page Not Found"; no page date.

**BMAD Method, additional**
- [S81] https://raw.githubusercontent.com/bmad-code-org/BMAD-METHOD/main/docs/build/review-a-change.md: last commit 2026-09-28T16:48:41Z.
</content>
