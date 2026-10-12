# Adversarial project review — 12 October 2026

Status: historical review and recommendations, not an accepted design decision or
authorization to implement changes. Findings describe the reviewed snapshot and
have not been revalidated against later changes. GitHub Issues remains the backlog.

The detailed evidence, consequences and corrective directions are in the separate
[findings document](2026-10-12-adversarial-findings.md).

## Review scope and evidence

- Repository: [Agentic Engineering Workflow](https://github.com/thelim3y/agentic-engineering-workflow).
- Main: [`b758531cf5b7a6ee238a95afd2cf9080f7e2d810`](https://github.com/thelim3y/agentic-engineering-workflow/tree/b758531cf5b7a6ee238a95afd2cf9080f7e2d810).
- Sole open PR at review time: [#39](https://github.com/thelim3y/agentic-engineering-workflow/pull/39),
  head [`339aa0364d3de12fe08dddba5acf985fe41adf1b`](https://github.com/thelim3y/agentic-engineering-workflow/tree/339aa0364d3de12fe08dddba5acf985fe41adf1b).
- Read AGENTS.md, development rules, README, the design index, all design documents,
  the backlog, available issue/PR discussions and the isolation implementation.
- Used a fresh writable clone because the attached checkout was an older
  documentation branch. Repository evidence below is pinned to reviewed commits.
- Three independent same-model review passes covered control/recovery, isolation,
  and product/build/evaluation. No cross-model review was run.
- All 36 isolation regression tests passed, and every entry in the retained evidence
  hash manifest matched. These checks establish only their stated scope.
- Reproduced the transcript-rewriting defect recorded as
  [AR-06](2026-10-12-adversarial-findings.md#ar-06--tested-code-can-rewrite-its-captured-transcript).
- Did not rerun complete sandbox conformance or model sessions. No implementation,
  issue creation or GitHub mutation formed part of the review.

Verification performed on the reviewed clone:

```sh
python3 -B -m unittest discover -s tests/isolation -p 'test_*.py'
sha256sum -c tests/isolation/results/linux-2026-10-12/SHA256SUMS
```

## Review requirements

The review used these explicit product requirements, including requirements that
conflict with the reviewed documents:

- Design and feasibility stage; the runtime is not implemented.
- Solo developers first, with foundations that can support later governed deployment.
- Runner, LLM/provider and model are independently configurable per agent role.
  One run may use multiple runners; independent adapters satisfy the same contract.
- TDD exclusively owns test-related inputs. Implementation cannot access or modify
  them. Trusted deterministic control governs gates, permissions, approvals,
  evidence, audit, recovery and external actions.
- The initial audit provider is file-based and must detect deletion, modification
  and reordering within its declared boundary.
- GitHub and C++ first. Engram is the selected memory backend.
- Future evaluation uses multiple real projects of differing complexity and real
  GitHub issues. Project identities and detailed evaluation choices remain undecided.
- Design documents describe the current design, not proof. Implementation evidence
  can justify revision; required invariants remain binding until deliberately changed.

## 1. Executive verdict

The project has defensible core invariants, but it is **not yet a coherent, proven
implementation contract**. The principal risks are test confidentiality,
trustworthy native verification, credential exposure after publication and audit
completeness. The build order also delays the first useful result behind optional
infrastructure.

**PR #39 should not merge as reviewed.** Its one-runner-per-run restriction
contradicts the established per-role configuration requirement.

Proceed with a narrow execution-and-evidence slice that leads to a useful C++ PR.
Do not treat the existing design or shell/build spike as proof of the full factory.

## 2. Prioritized findings

The [findings document](2026-10-12-adversarial-findings.md) is the authoritative
record of this review's individual findings, not an authoritative product contract.

P1 means resolve before relying on the affected guarantee. P2 means correct before
the corresponding milestone. Design gaps are not presented as deployed vulnerabilities.

| ID | Priority | Finding |
|---|---|---|
| AR-01 | P1 | The contract permits implementation access to tests. |
| AR-02 | P1 | Protected test files do not establish trustworthy native test execution. |
| AR-03 | P1 | Publication can move generated code into a credentialed environment. |
| AR-04 | P1 | File-audit completeness is underspecified. |
| AR-05 | P1 | PR #39 contradicts per-role runner selection and under-tests independence. |
| AR-06 | P2 | Tested code can rewrite its captured transcript. |
| AR-07 | P2 | Conformance checks can pass while missing protected effects or disclosures. |
| AR-08 | P2 | Approval withdrawal is undefined. |
| AR-09 | P2 | Optional memory blocks the first useful PR and conflicts with the deployment promise. |
| AR-10 | P2 | Evaluation can satisfy the written contract without establishing intended usefulness. |

## 3. What should remain unchanged

- Trusted deterministic control owns authorization, state transitions, evidence
  acceptance and external actions. Agents propose.
- TDD exclusively owns test-related inputs; implementation cannot access or modify
  them. Correct the conflicting documents and fixtures.
- Per-role runner/provider/model configuration, capability validation and
  independent adapter implementations.
- Revision-bound evidence, protected artifacts, stable operation identities,
  ownership fencing and reconciliation before retry.
- Explicit unsupported, unavailable, stale, unknown and failed states.
- Manual start, GitHub and C++ first, one issue aimed at one reviewable PR.
- Engram as the selected memory backend, with memory providing context rather than
  authority.
- Honest design-status language and the rejection of separate services or LLM calls
  merely because logical roles exist.

These foundations support later growth better than introducing distributed
infrastructure now.

## 4. What should be removed or deferred

- Engram, lesson approval and task-writing feedback as prerequisites for the first
  useful PR.
- Separate reasoning-agent calls for mechanical pre-PR checks, PR creation and merge
  dispatch.
- Stabilizing a broad public adapter API before real implementations expose its
  necessary semantics. Keep the independence invariant and an experimental
  conformance surface.
- Reserved signing/encryption configuration and generic key-provider choices until
  an implementation or concrete deployment requires them. Unsupported placeholders
  add user-facing surface without capability.
- Distributed ownership, organization-wide administration, compliance profiles and
  additional integrations until demonstrated demand.

Do not defer credential separation, trustworthy capture, file-integrity detection
or recovery correctness to simplify onboarding.

## 5. Missing decisions that genuinely block implementation

Resolve these at the relevant boundary, not through another large design phase:

1. **Initial execution scope:** controller language, supported OS, isolation
   mechanism, trusted components and whether only one local deployment is supported.
   The [ownership contract](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/checkpoints.md#L32-L46)
   refers to supported workstations; the support domain must be explicit.
2. **Verification ownership and visibility:** classification of mixed build inputs,
   who approves classification changes, implementation-facing diagnostics and the
   supported native-verification guarantee.
3. **Policy bootstrap:** who authorizes repository profiles and policy changes; how
   human decisions are authenticated; safe initial approval/completion defaults.
   [Configuration](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/configuration.md#L5-L16)
   mentions local configuration without placing it in the precedence hierarchy.
4. **File-state implementation:** durability protocol, ownership fencing, integrity
   expectations, retention and recovery after incomplete writes or suspected deletion.
5. **Before publication/merge:** remote-CI admission and a concrete mechanism binding
   accepted evidence to the actual integration state. GitHub's ordinary merge API
   can constrain the PR head; that alone does not freeze the base. See the
   [GitHub merge API](https://docs.github.com/en/rest/pulls/pulls#merge-a-pull-request).

Evaluation project names, additional memory providers, enterprise identity systems
and exact future compliance mappings do not block the initial slice.

## 6. Recommended next implementation step

Resolve the narrow execution decisions in
[#8](https://github.com/thelim3y/agentic-engineering-workflow/issues/8), then make
[#9's](https://github.com/thelim3y/agentic-engineering-workflow/issues/9) repaired
execution-and-evidence harness the next code change. Include the reproduced capture
defect, private comparison data, complete effect checks and hostile native verification.

Use that work immediately to build a small vertical slice:

- One disposable C++ issue with one behavioral requirement.
- TDD authors protected tests; implementation receives only permitted production
  inputs and feedback.
- Two independent adapters participate in the same run.
- Trusted execution records red, green and one bounded repair.
- File audit and checkpoints survive interruption, reject altered history and
  reject late results.
- The workflow reaches one reviewable draft PR after remote-automation admission,
  or stops with accurate evidence.

Implement only the records, configuration and recovery needed to make that slice
safe. Keep Engram and learning off its critical path. This produces an early useful
result while testing assumptions that would be expensive to reverse. It is
commissioning evidence, not a substitute for the later multi-project evaluation.
