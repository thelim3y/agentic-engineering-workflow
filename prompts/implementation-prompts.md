# Implementation prompts

Derived from docs/implementation-tasks.md and the topic contracts. One prompt per
task, one PR per prompt. Run each in a fresh Claude Code or Codex session, from the
repo root, on its own branch.

Resolve `{RUNTIME}` and `{HOST_OS}` after P1 decisions, `{ISOLATION}` after CP-A,
and `{STORAGE}` before X2. Ask for `{C++_FIXTURE_REPO}` before P5. Never guess an
unresolved placeholder. Topic doc names below are relative to `docs/` unless stated.

## Order

| Step | Prompt | Human decision |
|---|---|---|
| 1 | P1 Contract and decisions | Review ADR proposals, pick runtime and host/OS matrix |
| 2 | P2 Claude Code isolation spike | none |
| 3 | P3 Codex conformance | none |
| 4 | CP-A Checkpoint A review | Go/no-go on execution boundary |
| 5 | X1 Records and validators | none |
| 6 | X2 Audit and artifact store | Pick storage and threat boundary |
| 7 | X3 Ownership, checkpoints, crash harness | none |
| 8 | P4a Configuration | Policy defaults |
| 9 | X4 Production runner, X5 Host plugins | Approved host versions and isolated test environment |
| 10 | P4b Intake and planning | Scratch status writes |
| 11 | P5 TDD and implementation | C++ target repo |
| 12 | P6 Testing and bounded repair, then CP-B | none |
| 13 | P7 C++ profile, P8 Clang, P9 Engram | Engram pin, outage policy |
| 14 | L1 Task-writing feedback, L2 Reviewed lessons, then CP-C | Exact lesson approval during tests |
| 15 | P10 Draft PR, P11 Review and ready, P12 Merge | Scratch repo, merge mode |
| 16 | E1 Evaluation harness and trials | Test projects and thresholds, set before trials |
| 17 | CP-D Release review | Commissioning and evaluation evidence |

Run R1 (fresh-context review) on every PR before merging it.
X1 and every later build step require a recorded human go decision at CP-A.
Untested required isolation is a stop, not permission to continue with restrictions.

---

## Shared preamble (paste at the top of every prompt, or put in AGENTS.md / CLAUDE.md)

```
Repository: agentic-engineering-workflow. Status: design stage, no runtime exists
unless a previous task added it.

Start by reading README.md, docs/README.md (the authority table) and every topic doc
named in this task. Each contract has exactly one owning doc. Do not restate or
redefine a contract elsewhere. If docs conflict, or are silent on a policy default,
stop and report it. Do not choose a default silently.

Rules:
- One task, one reviewable PR, on a new branch. Never push to main. No force push.
- Verify the listed dependencies and required human decisions before starting.
  Read the order above as well as the selected prompt; a spike is not a production adapter.
- Build prompts deliver reusable product code and automated tests, not one-off
  execution of the feature. Wire each workflow stage into the existing controller.
  Documentation, spike and review prompts are explicitly marked exceptions.
- Tests first for any behaviour. Show the meaningful red before writing production code.
- Never claim isolation, immutability, or safety without an adversarial test that
  FAILS when the control is removed, plus a positive control showing allowed work succeeds.
- Failing, unavailable, skipped, stale and not-run are distinct states. Never report
  one as another.
- Unsupported configuration fails closed with a typed error. No stub may simulate success.
- No real credentials in code, fixtures, logs or tests. Remote writes only to the
  scratch repository, and only if this task says so.
- The legacy repo (agentic-engineering-workflow-legacy) is read-only reference.
  Reuse an idea or code only after reviewing and testing it.
- Do not invent runnable commands in docs. Document only what you ran.
- Tick a box in docs/implementation-tasks.md only when its verification passed.
  If behaviour differs from a contract, fix the implementation. If the contract
  itself needs changing, propose the change and wait for human approval before
  editing its owning doc. Never change a contract to make failing work pass.
- Keep output concise. Finish with: what changed, evidence (command and result),
  limitations, open decisions.
```

---

## P1. Establish the product contract (task 1)

```
Task: implementation-tasks.md section 1. Documentation only. No runtime code.
Read: docs/README.md, build-plan.md, setup-guide.md section 11, all of docs/ for gaps,
decisions/0001, reviews/2026-10-11-design-review.md.

Produce:
1. docs/decisions/0002-runtime-language.md (status: proposed). Compare a small Python
   controller against at least two alternatives (suggest Go, TypeScript, Rust) on:
   host integration with Claude Code and Codex, packaging, schema validation,
   process isolation support, testability of crash injection, and maintainability by
   one owner fluent in C++, Python and TypeScript. Give a recommendation and what
   evidence would change it. Do not mark it accepted.
2. docs/decisions/0003-host-os-matrix.md (status: proposed). Candidate initial host
   versions and OS targets, with the isolation mechanisms plausible on each.
3. A table of every unresolved policy default found in the docs (scope thresholds,
   retry counting, mid-run scope growth, Engram outage handling, merge approvals,
   shortlist size, hidden-test visibility, retention). For each: owning doc, options,
   recommended default, consequence of each. Put it in docs/decisions/0004-policy-defaults.md.
4. A threat model section for ownership: who are the adversaries (generated code,
   prompt-injected agent, concurrent operator, stale process), what is out of scope.

Done when: every link resolves, every unresolved item in build-plan.md "Risks and
open decisions" is covered or explicitly deferred, and nothing is marked accepted.
Stop and ask me before editing any existing contract doc.
```

## P2. Prove Claude Code execution isolation (task 2)

```
Task: implementation-tasks.md section 2. Bounded spike, disposable directories only,
no production credentials. Read: execution.md (especially "Proof required before
onboarding"), interfaces.md "Runner capabilities", ADR-0001.

Build a capability probe and adversarial fixtures. Do not pre-decide the mechanism:
evaluate at least Claude Code's own sandbox settings and one OS-level mechanism
(e.g. bubblewrap/namespaces, Landlock, rootless container) on {HOST_OS}.

Fixtures, each with an expected-block result AND a positive control that must succeed:
- direct edit of a protected test file; shell redirection; sed -i; git checkout over it
- symlink and ../ traversal into protected inputs
- child process and nested subprocess writes
- a malicious build/configure script (CMake configure-time code) writing to protected paths
- tampering with report files, result parser, selectors, test registration
- reading a credential-shaped env var, ssh-agent socket, ~/.config
- network egress to a non-allowlisted host
- cancellation: kill the process tree, then a late write must be rejected
Also demonstrate one role invocation returning structured output with the effective
model identity reported, per interfaces.md.

Output: tests/ fixtures, a capability matrix (what is enforced, what is only
discouraged, what is unsupported) in docs/ or a spike report, and a recommendation.
Each fixture must be shown to FAIL (attack succeeds) with the control disabled.
Record unsupported modes. Do not widen access to make a test pass.
Done when the matrix is evidence-backed and the attacks that succeeded are listed.
```

## P3. Prove the same contract with Codex (task 3)

```
Task: implementation-tasks.md section 3. Depends on P2 merged.
First refactor the P2 fixtures into a host-agnostic conformance suite with a thin
per-host adapter. Then run the same suite through Codex on the actual installed
version (record it). Add: cancellation, failure, configured-model handling, and
rejection of an unsupported execution configuration with a typed error.
Read current official Codex docs for sandbox and approval modes; do not assume they
mirror Claude Code. Record host differences in the capability matrix.
Done when both hosts run one suite and every difference is documented.
```

## CP-A. Checkpoint A review

```
Fresh-context reviewer. You did not write P1 to P3. Read execution.md "Proof required
before onboarding" and the P2/P3 evidence. For each listed attack category, state:
proven blocked, proven allowed, or untested, citing the fixture and a run result.
Check each block has a disabled-control run and a positive control. Recommend go,
no-go, or go with restrictions for the production execution boundary. Per build-plan:
if either host cannot provide the isolation, say stop; do not suggest prompt-based
substitutes. You advise; the human decides.
```

---

## X1. Record contract and validators (cross-cutting)

```
Depends on CP-A human go and accepted {RUNTIME} ADR. Read communication-protocol.md fully.
Implement the v1 record types (invocation, agent report, execution, gate decision,
approval, external operation) as machine-readable schemas plus validators, in {RUNTIME}.
Tests first. Cover: required common identity, task_ref uniqueness (provider instance,
project, native id), controller-owned fields not trusted from agent echo, invocation
binding, stale/unsolicited/mismatched/malformed rejection, identical duplicate returns
existing receipt, same id with different content is a conflict, unknown schema version
fails explicitly, gate outcomes limited to the five states, typed error set, external
operation states including unknown. Add conformance fixtures usable by later adapters.
Do not implement storage. Done when the invalid-record corpus is rejected for the
stated reason, not merely rejected.
```

## X2. Audit log and artifact store (cross-cutting)

```
Depends on X1 and a human decision on {STORAGE} and threat boundary. Read audit.md and
the audit section of implementation-tasks.md.
Implement append-only events with unique event/operation ids, idempotent duplicate
appends, linked corrections, content-addressed artifacts that retain bytes, artifacts
published before the event that references them, secret redaction before persistence,
access labels. A failed required append must block progression.
Enforce immutability in storage, not by convention. Attack it through the agent tool
path AND direct storage access: edit, overwrite, delete, truncate, replace referenced
artifact. Test concurrent appends, interrupted writes, disk full, redaction, backup
restore. Write the doc stating privileged operators, retention and what is NOT
guaranteed (no administrator resistance unless you demonstrate it). Checksums alone do
not count as enforcement; say so wherever relevant.
```

## X3. Ownership, checkpoints and crash harness (cross-cutting)

```
Depends on X1, X2. Read checkpoints.md fully, including the recovery sequence.
Implement atomic ownership acquisition with monotonic generations, explicit audited
takeover, stale-generation rejection at the controller and the mutation dispatcher,
write-ahead intents with stable intent ids, checkpoint publication only at a durable
audit position, reconciliation of unknown outcomes, and resume that invalidates
changed inputs and approvals without resetting retry counts.
Build a deterministic crash-injection harness with a hook at each boundary: before
intent, after intent, after external effect, after result, after audit append, after
checkpoint publish. For every boundary assert safe stop or correct reconciliation,
no duplicate effect, no false completion. Include: concurrent starts, an old process
continuing after takeover, corrupt or missing checkpoint (no silent restart), restore
from backup. Done when the harness is part of the normal test run.
```

---

## P4a. Configuration (task 4, part 1)

```
Depends on X1. Read configuration.md and the config bullets in planner.md/workflow.md.
Implement layered resolution (defaults, repo, run override; role over shared within a
layer), origin tracking per value, unknown-key and conflict rejection, secret
references kept out of committed config, sanitized effective-config output, and a
config-check entry point. Enforce the fixed invariants as non-configurable: test
writing for implementer, self-approval, absent evidence as pass, audit disable,
stale-owner authority, XL+ approval, silent model substitution.
Tests: conflicting layers, unknown keys, missing models, unsupported visibility mode,
redaction, budget exhaustion, resumed counters, attempts to configure an invariant away.
Do not invent permissive defaults; missing required choices are errors.
```

## X4. Production runner and controller foundation (cross-cutting)

```
Depends on CP-A human go, X1, X2, X3 and P4a. Read build-plan.md architecture,
interfaces.md, execution.md and communication-protocol.md.
Implement the shared deterministic controller foundation in {RUNTIME} and production
Claude Code/Codex runner adapters using the accepted {ISOLATION}. Reuse spike code
only after review; rerun conformance against the actual production adapter path.
Connect validated configuration, scoped invocation, record acceptance, audit and
recovery. Supply required task/role/policy context directly; retrieval is supplementary.
Resolve per-role runner/provider/model against proven capabilities, without fallback.
Keep host calls behind adapters; use CLI execution, not new model REST clients.
Tests: valid invocation, unsupported configuration, malformed/stale output, protected
write attempts, cancellation with confirmed termination, and rejected late results.
Done when a benign role invocation through each real adapter retains attributable
evidence and the shared negative/positive controls pass. No GitHub mutations or
target-app coding yet; future workflow stages remain explicitly unavailable.
```

## X5. Installable host plugins (cross-cutting)

```
Depends on X4. Read setup-guide.md section 3 and build-plan.md architecture.
Implement thin, installable Claude Code and Codex entry points for the same controller.
Verify packaging against official documentation for the approved host versions.
Keep policy in the controller, not duplicated in host prompts. Expose configuration
validation and the implemented diagnostic invocation; later stages attach here.
Test fresh installation, discovery and invocation in clean host profiles. Verify both
reach the same controller and preserve typed failures and concise terminal output.
Document only tested installation commands and compatibility. Done when a clean
installation works without developer-only paths or manually pasted glue code.
Do not modify the operator's normal host configuration for these tests.
```

## P4b. Intake, ownership and planning (task 4, part 2)

```
Depends on P4a, X3, X4, X5. Read workflow.md intake section, planner.md,
interfaces.md Issue row. Implement, behind the Issue adapter contract with a fake
GitHub adapter first: label required for explicit and automatic selection, oldest-first
default, unknown dependency status blocks selection, atomic claim, preserved issue
snapshot, safe status projection (labels plus status comment), planner invocation,
size bands with Large notify/proceed and XL+ stop for approval, any concern pauses.
Order of work: read-only discovery against the scratch repo (authorized), then
scratch status writes only after I confirm. Tests: concurrent start rejected, explicit
takeover, stale owner rejected, unlabelled explicit issue rejected, dependency lookup
failure treated as blocked, issue edited mid-run pauses for impact review.
Invoke from both hosts. No production coding, no PRs.
```

## P5. Protected TDD and implementation (task 5)

```
Depends on P4b. Read verification.md, execution.md ownership table, workflow.md delivery.
Target: one small C++ requirement in {C++_FIXTURE_REPO} (ask me for it if unset).
Implement: TDD invocation producing a small test batch; independent testing establishing
meaningful red (not empty selection, not unrelated compile error; label interface
bootstrap separately); acceptance-criteria-to-evidence mapping; implementer changes
accepted only inside the production ownership boundary; mixed files handled by
mediated owner-checked edits; source/test/policy identities preserved.
Malicious tests: implementer edits a test, edits CTest registration, edits a suppression,
tampers with a report, edits policy. All must be rejected by enforcement, not prompts.
If the diff is large, stop and propose a split into record-validation and execution PRs.
```

## P6. Independent testing and bounded repair (task 6)

```
Depends on P5. Implement routing: production failure to implementer, suspected test
defect to TDD, requirement gap to planner, environment failure to blocked recovery,
malformed agent output as its own class. Dispute gets one review round by default,
then stops for the user. Limits stop with preserved evidence and a terminal
explanation; limits never authorize weakened tests.
Cases: passing, failing, disputed test, unavailable environment, exhausted retries,
resume with counters preserved. Then run Checkpoint B through both hosts.
```

## CP-B. Checkpoint B review

```
Fresh-context reviewer. Run the full red, green, repair path on both hosts yourself.
Confirm no PR publication occurred, failure routing was real, recovery survived an
injected crash, and the terminal report only claims what evidence supports.
Report pass or fail per item with run output.
```

## P7. C++ build and test profile (task 7)

```
Depends on P6 and CP-B evidence with no unresolved blocking findings.
Read verification.md profile section and setup-guide.md sections 5 to 6.
Implement the reusable C++ profile executor and connect it to the testing stage.
Discover, do not replace, existing normal/ASan/UBSan/test presets. Execute approved
configure, build and test lanes with captured inventory and diagnostics. Record
OS/toolchain/runtime, GUI/hardware and packaging lanes. Required unavailable lane
blocks; optional unexecuted lane is disclosed.
Controlled defects to prove the gate: empty selection, removed test, skipped case,
stale binary, masked sanitizer error, spoofed report, unexpectedly reduced inventory.
Each must not produce a pass. Assertion-quality and mutation/property/fuzz checks only
where the profile justifies them.
```

## P8. Clang readiness (task 8)

```
Depends on P7. Read workflow.md, verification.md and setup-guide.md section 6.
Implement the Clang check adapters and wire their evidence into the separate pre-PR
gate. Run existing clang-format and clang-tidy configs in check-only mode.
Route fixes to the correct owner, never weaken config automatically. Reuse evidence
only when source, tests, tool environment and policy identities all match.
Tests: deliberate format failure, lint failure, stale evidence after tool upgrade.
Done when controller integration tests block the pre-PR gate on each failure and
allow the verified path; manually running the tools is not completion.
```

## P9. Connect Engram (task 9)

```
Depends on P3, P6. Read learning.md, retrieval.md, setup-guide.md section 4.
Pin thebtf/engram client and server versions and read its current README first; do not
assume semantics. Implement the Memory adapter and Retrieval interface with a fake
adapter for tests and fixture records for approved/unapproved lessons.
Verify through both hosts: tool discovery, write and fresh-session
recall of a non-secret record, project and role scoping, approval filtering, retirement
including caches and indexes, automatic injection obeying the same rules, outage policy,
upgrade. If Engram cannot enforce role isolation, hidden tests stay in a verifier store.
Memory cannot authorize progression or supply an authoritative gate result. The
controller blocks when required information is unavailable; missing optional context
is disclosed and handled under the configured policy. Test both outage paths and
prompt injection inside a retrieved lesson. L1/L2 implement feedback and lesson lifecycle.
Live tests only with non-secret records, after I authorize.
```

## L1. Optional task-writing feedback

```
Depends on P6 and P9. Read learning.md task-writing feedback and workflow.md reporting.
Implement a separate, configurable post-run reviewer using the original task and
permitted audit evidence. Cover finished, failed, paused and cancelled runs.
Return concise wording guidance with the required uncertainty disclaimer; no issue
edits, delivery-state changes or gate authority. Feedback failure is reported separately.
Tests: disabled feedback, each run outcome, evidence access restrictions, and failure
without changing the delivery result. Done when feedback is available through both
host entry points without extending the delivery or repair loop.
```

## L2. Human-reviewed reusable lessons

```
Depends on L1, P9 and X3. Read learning.md reusable lessons and retrieval.md.
Implement lesson proposal, exact-content/scope human approval, applicable-version
reuse, outcome recording and retirement through the existing memory/retrieval adapters.
Keep candidate lessons separate from active guidance; approval is recorded through
the trusted controller. Edits require fresh approval. Agents cannot self-approve.
Tests: reject unapproved/out-of-scope/edited lessons; accept an approved applicable
version; retire it across recall, caches and automatic injection while retaining audit.
Done when the lifecycle works through the host entry points with recorded approval
and provenance. No automatic policy changes, convention mining or model training.
```

## CP-C. Checkpoint C review

```
Depends on P7, P8, P9, L1, L2. Fresh-context reviewer.
Try to make a required check falsely pass. Try to leak a hidden
test through recall, logs, caches and artifacts on both hosts. Report findings only.
Check that unapproved, edited or retired lessons cannot become active guidance and
feedback cannot alter delivery state. Unresolved blocking findings stop publication work.
```

## P10. Draft PRs (task 10)

```
Depends on CP-C evidence with no unresolved blocking findings. Read workflow.md,
interfaces.md Repository and PR row, and checkpoints.md external-operation rules.
Implement the draft-PR adapter and publication stage, separate from pre-PR checks.
Verify the existing machine-user identity from the trusted
integration environment only; do not alter its setup. Publish only the verified
revision with evidence references and accurate status. Retries must not duplicate PRs
(stable intent id, reconcile before retry, unknown outcome blocks). Preserve work if
publication fails. Fake GitHub failure and retry tests first; scratch PR only after I confirm.
Recheck eligibility and scoped authorization immediately before dispatch. Done when
the controller creates one authorized draft and rejects stale or ineligible work.
```

## P11. Review, repair, ready (task 11)

```
Depends on P10. Read workflow.md, verification.md and communication-protocol.md.
Implement the PR-review role, owner-routed repair transitions and separate ready gate.
Wire them into the controller. Review the actual PR revision against configured
criteria, including test quality and requirement mapping. Route findings to the owner, rerun invalidated
checks and review. Ready requires complete current evidence. Record the factory
verdict separately from GitHub approval (same account cannot self-approve).
Cases: revision changes mid-review, unavailable check, successful repair loop.
Done when integration tests exercise those transitions and ready is possible only
with current evidence. Reviewing this implementation PR alone does not deliver the stage.
```

## P12. Gated merge and commissioning (task 12)

```
Depends on P11. Read workflow.md, checkpoints.md and setup-guide.md section 10.
Implement the merge stage, recovery integration and terminal outcome reporting.
Respect repository protections and configured approval; never bypass.
Recheck label eligibility, protections and evidence for the exact accepted revision
and integration state immediately before merge. Ready is not merged; report what
actually happened. Recover interrupted merge without duplicate or false completion.
Fake merge failure and stale-revision cases first, then scratch lifecycle on both hosts.
Split merge, recovery and release docs into separate PRs if the diff is large.
Setup docs must state tested configurations only. Completion here supplies evidence
to E1 and CP-D; it does not authorize release or real-project adoption.
```

## E1. Evaluation harness

```
Depends on P12 and designated test projects. Read evaluation.md.
Thresholds must be agreed by me before any trial; refuse to score
without them. Build the versioned task set (ordinary, ambiguous, existing-defect,
should-stop), evaluator-owned checks the factory cannot modify, a simpler host-native
baseline with equal inputs and budgets, repeated trials, and failure injection per the
required scenarios list. Report sample size, variance and exclusions. Unknown cost
stays unknown. Keep evaluation material out of retrieval and learning inputs.
Run the agreed trials and retain a threshold-by-threshold report for CP-D, including
retrieval/lessons on-off comparisons where relevant. A harness without results is not completion.
```

## CP-D. Checkpoint D review

```
Depends on P12 commissioning evidence and completed E1 trials against pre-agreed thresholds.
Fresh-context reviewer. Walk setup-guide.md section 10 items 1 to 12. For each, mark
proven, not proven or untested with evidence. Do not recommend real-project adoption
unless all are proven and the agreed evaluation thresholds are met. The human decides release.
```

---

## R1. Fresh-context PR review (use on every PR)

```
You did not write this change. Read the owning contract docs and the diff.
Check: does it match the contract; do tests fail when the control is removed; any
claim of isolation, immutability or safety without adversarial proof; any simulated
success; any weakened or removed test; any hidden-test or credential exposure; stale
or reused evidence; docs that now disagree with code. Report findings ranked by
severity with file and line. Do not fix anything.
```
