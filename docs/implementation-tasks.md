# Implementation tasks

Unchecked means not implemented. File areas are provisional, not an agreed layout.
The [design index](README.md) owns contract routing; these tasks implement those contracts.
Each task is intended as a focused PR; split during planning if its actual diff is
too large. No issues have been published and no implementation is authorized by this list.

## Cross-cutting requirement: audit-log immutability

Agreed requirement; not implemented. Every run requires a complete, durable,
immutable, append-only audit log. This applies across all workflow stages.

- [ ] Record inputs, effective configuration, agent outputs, tool actions, evidence,
      approvals, failures, retries, checkpoints, and GitHub changes.
- [ ] Enforce immutability through storage controls, not agent instructions.
      Prevent edits, overwrites, deletion, and truncation of recorded history.
- [ ] Record corrections as new entries referencing the original; preserve both.
- [ ] Protect referenced evidence from replacement, so immutable records cannot
      point to silently changed artifacts.
- [ ] Redact secrets before persistence and preserve hidden-test access restrictions.
- [ ] Preserve recorded history across crashes, retries, and checkpoint recovery.
- [ ] Stop progression and notify the user if required audit records cannot be saved.
- [ ] Document the storage choice, enforcement boundary, privileged access, and
      retention policy before claiming an immutability guarantee. These remain open.

Verification: attempt edits, deletion, truncation, and artifact replacement through
agent tools and direct storage access; confirm rejection within the defined boundary.
Test linked corrections, concurrent appends, interrupted writes, recovery, and secret
redaction. Checksums alone demonstrate tamper detection, not enforced immutability.

## Cross-cutting capability: retrieval-augmented context (RAG)

Included in the design; not implemented. Use selective retrieval for planning,
test design, implementation, review, and task-writing feedback where helpful.

- [ ] Define a retrieval contract with source references, revision identities,
      bounded results, freshness, and explicit failure states.
- [ ] Connect repository search and the Engram adapter; verify actual backend
      capabilities before selecting semantic search or additional storage.
- [ ] Supply required task context and policy directly, independently of retrieval.
- [ ] Enforce project and role visibility across indexes, results, caches, and logs;
      prevent hidden tests or unapproved lessons reaching unauthorized agents.
- [ ] Audit the context supplied and its sources; keep local retrieval possible
      without silently sending code to external providers.
- [ ] Expose source, provider, budget, freshness, and failure settings.
- [ ] Evaluate relevance and source accuracy in the planned test projects; test
      stale data, no matches, outages, retired lessons, leakage, and prompt injection.

## 1. Establish the product contract

- [ ] Review the consolidated contracts and legacy disposition before runtime implementation.
- [ ] Agree runtime language, initial host/platform matrix, and ownership threat model.
- [ ] Identify unresolved policy defaults without silently choosing them.

Verification: owner review against the conversation and guide. Dependencies: none.
Likely files: product specification and architecture decision. Scope: small documentation change.

## 2. Prove Claude Code execution isolation

- [ ] Demonstrate one role invocation with model identity and structured output.
- [ ] Reject direct, shell-mediated, traversal/symlink, and subprocess changes to protected inputs.
- [ ] Demonstrate verifier inputs remain protected during execution of agent-authored code.

Verification: adversarial fixtures in disposable directories; no production credentials.
Dependencies: 1. Likely areas: capability probe and isolation tests. Scope: bounded spike;
record unsupported modes instead of silently widening access.

## 3. Prove the same contract with Codex

- [ ] Run the same isolation and output contract tests through the Codex adapter.
- [ ] Verify cancellation, failure, and configured model handling.
- [ ] Record host differences and reject unsupported execution configurations.

Verification: shared conformance fixtures on actual supported host versions.
Dependencies: 1, 2. Likely areas: second host probe and conformance tests. Scope: medium.

## Checkpoint A

- [ ] Review feasibility and choose the production execution boundary before proceeding.

## 4. Deliver manual intake, ownership and planning

- [ ] Validate configuration and resolve per-role runner/provider/model settings.
- [ ] Require the label for explicit and automatic selection; default to oldest eligible issue.
- [ ] Apply planner size/risk rules: XL+ approval, Large/below notify and proceed; unknown dependencies block selection.
- [ ] Atomically claim the task, preserve source issue snapshots and publish issue status safely.
- [ ] Demonstrate concurrent-start rejection, explicit takeover and stale-owner rejection.

Verification: fake GitHub cases, authorized read-only discovery, then authorized scratch
status writes; invoke from both hosts. Read-only discovery alone is not the completed slice.
Dependencies: 1–3. Likely areas: intake, config schema, host entry points, tests. Scope: medium;
separate configuration and intake PRs if needed.

## 5. Deliver protected TDD and implementation

- [ ] Create small test batches for one C++ task; independent testing establishes meaningful red before implementation.
- [ ] Map acceptance criteria to evidence and handle interface bootstrap explicitly.
- [ ] Accept implementation changes only inside the production ownership boundary.
- [ ] Preserve source/test/policy identities and separately controlled role records.

Verification: a C++ fixture and malicious write attempts, including report and policy tampering.
Dependencies: 4. Likely areas: local controller, role definitions, evidence schema, tests.
Scope: split into record-validation and execution PRs before coding if needed.

## 6. Deliver independent testing and bounded repair

- [ ] Route production failures to implementation and suspected test defects to TDD.
- [ ] Separate environment failures, test failures, and malformed agent output.
- [ ] Stop at configured limits with preserved evidence and a terminal explanation.

Verification: passing, failing, disputed-test, unavailable-environment, and exhausted-retry cases.
Dependencies: 5. Likely areas: transition rules, testing role, local integration tests. Scope: medium.

## Checkpoint B

- [ ] Demonstrate the complete red/green/repair path through both hosts; no PR publication yet.

## 7. Bind the C++ build and test profile

- [ ] Discover actual normal, ASan, UBSan, and test presets without replacing them.
- [ ] Execute approved configure/build/test lanes and capture inventory and diagnostic results.
- [ ] Record OS/toolchain/runtime, GUI/hardware and packaging lanes; required unavailable checks block.
- [ ] Evaluate assertion quality and select mutation/property/fuzz checks where justified.
- [ ] Reject empty, missing, stale, or unexpectedly reduced verification evidence.

Verification: controlled C++ defects and missing/empty test cases; compare to approved profile.
Dependencies: 6. Likely areas: verification profile, build/test executor, fixtures. Scope: medium.

## 8. Bind Clang readiness checks

- [ ] Execute existing clang-format and clang-tidy settings in check-only mode.
- [ ] Route production/test fixes to the correct owner; never weaken policy automatically.
- [ ] Reuse evidence only when source, tests, tool environment, and policy still match.

Verification: deliberate formatting/lint failures and stale-evidence cases.
Dependencies: 7. Likely areas: Clang checks, evidence invalidation, tests. Scope: medium.

## 9. Connect the selected Engram

- [ ] Verify `thebtf/engram` integration through both hosts with project-scoped context.
- [ ] Keep authority and protected test disclosures outside shared recall.
- [ ] Exercise the agreed outage policy and fresh-session retrieval.
- [ ] Pin tested client/server versions; validate approval filtering, retirement, caches, automatic injection and upgrades.
- [ ] Record lesson provenance, human approval and observed outcomes without granting memory gate authority.

Verification: fake adapter tests and designated non-secret live test records after authorization.
Dependencies: 3, 6. Likely areas: memory adapter, configuration, integration tests. Scope: medium.

## Checkpoint C

- [ ] Review gate honesty, disclosure boundaries, and both host integrations before publication work.

## 10. Create draft PRs from verified work

- [ ] Verify the existing machine-user identity without altering its setup.
- [ ] Publish only the verified revision with evidence references and accurate status.
- [ ] Retry safely without creating duplicate PRs; preserve work if publication fails.

Verification: fake GitHub failure/retry tests, then an explicitly authorized scratch PR.
Dependencies: 7–9. Likely areas: GitHub delivery, publication records, tests. Scope: medium.

## 11. Review, repair, and mark ready

- [ ] Review the actual PR revision against the configured criteria.
- [ ] Send changes through the correct owner and rerun invalidated checks/review.
- [ ] Mark ready only with complete current evidence; distinguish agent verdict from GitHub approval.

Verification: findings, revision changes during review, unavailable checks, and successful repair.
Dependencies: 10. Likely areas: PR review role, ready gate, tests. Scope: medium.

## 12. Add gated merge and commission the workflow

- [ ] Respect configured approval rules and current repository protections without bypasses.
- [ ] Recover interrupted operations without duplicate delivery or false completion reports.
- [ ] Exercise both hosts and selected merge modes; publish accurate setup/limitations documentation.

Verification: fake merge failure/stale-revision cases, then authorized scratch lifecycle tests.
Dependencies: 11. Likely areas: merge gate, recovery, report, commissioning tests, docs.
Scope: split merge, recovery, and release documentation into separate PRs during detailed planning.

## Checkpoint D

- [ ] Review commissioning evidence before declaring the first usable release or enabling real-project runs.

## Cross-cutting implementation: records, safety and recovery

These are dependencies of the first executable slice, not tasks deferred until merge.

- [ ] Implement the versioned [record contract](communication-protocol.md) and validators.
- [ ] Bind reports to issued invocation/role/input identities; reject spoofed, stale and conflicting records.
- [ ] Protect execution, credentials and evidence under the [execution contract](execution.md).
- [ ] Persist intent before effects and audit/artifacts before checkpoint publication.
- [ ] Preserve stable operation identities; reconcile unknown effects without blind retries.
- [ ] Bind human approval to exact content/scope and invalidate changed dependencies.
- [ ] Prove backup restore, retention safety, cancellation and counter preservation.
- [ ] Document tested threat boundary and privileged access before claiming immutability.

Verification: deterministic fixtures and crash injection at each write/dispatch boundary,
including concurrent owners and an old process continuing after takeover.

## Factory evaluation and later capabilities

- [ ] Build the [evaluation suite](evaluation.md) when the planned test projects are available.
- [ ] Agree release thresholds before trials; report repeated-run results against a simpler baseline.
- [ ] Cover false success, review effort, cost/time, recovery, safety and human intervention.
- [ ] Compare RAG and approved lessons against disabled baselines; keep protected evaluator material separate.
- [ ] Re-run affected suites on model, host, prompt, tool, policy or memory changes.
- [ ] Add .NET/C# profiles after the first C++ slice; assess Python separately.
- [ ] Keep convention analysis, local-model runners and Jira visibly future until selected.
