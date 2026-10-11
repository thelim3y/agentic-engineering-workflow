# Software factory — build plan

Status: design delivery plan; runtime work and GitHub issue publication have not started.

## Existing blueprint

The [design index](README.md) identifies the authoritative topic contracts.
The [setup guide](setup-guide.md) covers onboarding and C++ tool selection.

## Working arrangement

- Build in this repository.
- Keep `agentic-engineering-workflow-legacy` unchanged as reference material.
- Reuse individual ideas and code only after reviewing and testing them.
- Validate C++ first, then .NET/C#; Python remains a candidate. This does not decide the factory's implementation language.
- Keep authoritative design and delivery documents together in this repository.
- Track unimplemented work in [implementation tasks](implementation-tasks.md); no issues have been published from this list.

## Architecture

Thin Claude Code and Codex entry points invoke a shared, deterministic workflow
controller. Role agents propose work and produce structured results. The controller
validates configuration, enforces transitions and permissions, runs prescribed
checks, and retains revision-bound evidence. It is not another reasoning agent.

Use existing host execution rather than implementing direct model REST clients.
Resolve runner, provider, and model per role against demonstrated adapter capabilities;
unsupported combinations fail before work starts. Two hosts remain in initial scope.

Use GitHub first and the selected `thebtf/engram` for shared context. Keep approved
policy, authoritative run state, and verification evidence outside agent-writable
memory and report files. Keep integration boundaries small; do not build a generic
plugin marketplace or a second real memory backend.

Protected verification inputs include tests, fixtures, registration, selectors,
scripts, suppressions, result evaluation, and relevant build settings. Test CRUD
does not authorize changing workflow policy. Separate the trusted verifier from
agent-writable working copies. A controlled patch boundary must also account for
agent subprocesses and build execution; filtering patches alone is insufficient.

## Delivery order

1. **Contract and feasibility:** reconcile the blueprint, select the runtime and
   initial execution environments, and prove protected test execution with both hosts.
2. **Intake and ownership slice:** first prove read-only selection, then protected
   claiming, status projection, planning and approval. No production coding or PRs.
3. **Protected local TDD slice:** one small C++ requirement through meaningful red,
   production implementation, independent test execution, and bounded repair.
4. **Verification and memory:** bind actual C++ presets and Clang checks; integrate
   the selected Engram without giving memory authority over gates or hidden tests.
5. **PR delivery slice:** validated evidence to draft PR, actual revision review,
   owner-routed repair, renewed checks, and ready status.
6. **Merge and commissioning:** configured approval policy, current-revision merge
   checks, honest completion reports, and interruption/duplicate-action tests.

Detailed tasks and dependencies are in [implementation tasks](implementation-tasks.md). Each milestone can require
multiple small PRs. The factory's no-auto-decomposition rule concerns incoming
user tasks; it does not prevent us planning its own development in reviewable units.

## Checkpoints

- After tasks 1–3: agree the contract; both host boundaries demonstrated. Stop if
  either cannot provide the required isolation; do not replace enforcement with prompts.
- After tasks 4–6: one eligible C++ task runs locally from red to green, with real
  failure routing, durable recovery and terminal reporting. Limit remote writes to
  approved issue status; no PR publication yet.
- After tasks 7–9: required checks cannot falsely pass and both hosts preserve the
  chosen memory/disclosure policy. Confirm the evidence before enabling publication.
- After tasks 10–12: demonstrate draft/review/repair/ready and chosen merge modes
  in a designated scratch repository. No automatic adoption on real applications.

## Legacy disposition

- Reuse as design inputs: single-purpose roles, test dispute routing, bounded
  retries, machine-user integration, scratch scenarios, and applicable unit tests.
- Revise: configuration, structured handoffs, result identity, host integration,
  and report ownership.
- Replace: the unsafe enforcement boundary and the wrong Engram integration.
- Do not carry forward: automatic issue splitting, pasted-ticket eligibility
  bypasses, mandatory epic conventions, implicit search ordering, fixed model tiers,
  or simulated success reported indistinguishably from real PR/merge success.

## Risks and open decisions

- Runtime language is undecided. Compare a small Python controller with alternatives
  against host integration, packaging, validation, and isolation needs before choosing.
- Initial operating-system support and isolation mechanism require explicit agreement.
- Both CLI adapters need current official documentation and runtime capability checks
  during implementation; this design does not claim arbitrary provider interoperability.
- Hidden-test policy must cover files, process access, logs, artifacts, and Engram.
- Scope thresholds, shortlist size, retry counting, mid-run scope growth, Engram
  outage handling, and merge approvals need explicit defaults and override rules.
- Storage, isolation technology, lock implementation and administrative retention
  guarantees remain choices to resolve; [contracts](README.md) constrain each choice.
- Native application verification requires a chosen C++ target and its actual
  build/test environment. The existing Python scratch examples are orchestration
  fixtures, not proof of C++ support.

## Verification discipline

Every implementation PR needs focused tests, applicable full-suite checks, review,
and recorded limitations. Select actual build/test commands once the runtime and
repository scaffold exist; do not invent runnable commands in this design.
Failing, unavailable, skipped, stale, and not-run evidence are distinct states.
Do not use the unfinished factory to authorize its own security-sensitive changes.

## Cross-cutting delivery requirements

Implement the [record contract](communication-protocol.md), [audit](audit.md) and
[recovery rules](checkpoints.md) with the first working slice, not as a late retrofit.
Every enabled capability needs conformance evidence. Evaluate later on designated
[test projects](evaluation.md), keeping runtime safety tests separate from model-quality
trials. No vector database, additional memory backend or service split is required.
