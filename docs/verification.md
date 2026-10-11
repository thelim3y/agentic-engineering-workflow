# Verification and project profiles

Status: required behaviour; profiles and gates are not implemented.

## Test ownership and quality

TDD derives behavioural tests from requirements and acceptance criteria, including
edge cases and failure paths. Tests should constrain observable behaviour without
unnecessarily prescribing private implementation. Unit tests are added in small
meaningful batches as interfaces and implementation needs become clear.

The implementer proposes the smallest needed interface using project conventions;
TDD checks that the required behaviour is testable. Neither silently resolves unclear
requirements: those return to the planner and user.

Map each acceptance criterion to tests or another justified verification method.
Identify uncovered requirements and limits; coverage percentages alone do not prove
assertion quality. The PR reviewer examines both the tests and their requirement
mapping. The testing role runs checks and reports gaps; it does not edit tests.

Where useful, use property tests, mutation testing, fuzzing, negative cases and
integration scenarios. Selection, budgets and thresholds belong to the project
profile. These techniques are not mandatory for every task. Separate authorship
does not by itself establish independent interpretation or correct expectations.

## Small-batch red/green loop

1. TDD writes a meaningful test batch against the plan.
2. Testing independently runs it and identifies the intended failure.
3. Implementation changes production code only.
4. Testing reruns the batch and required regression checks on the new snapshot.
5. Route production defects to implementation, test defects to TDD, and unclear
   requirements to planning. Continue until the required behaviour is covered.

A meaningful red is a recorded failure attributable to the missing/incorrect intended
behaviour, not an empty selection, unrelated compile error or broken environment.
A new API may initially cause a compile failure: label it as interface-bootstrap
evidence, not behavioural red. Re-run once the minimal interface exists and establish
behavioural evidence before proceeding beyond that bootstrap. If it cannot be
established, stop for an explicit decision and preserve the exception in the report.

For behaviour already satisfied, do not manufacture a failing test or claim a red
transition. Record baseline evidence and use the configured, explicitly authorized
verification path for that task type. The path and its limits must be visible.

Green requires the expected test inventory to execute successfully, acceptable skips,
no blocking diagnostics, and required regression checks. A zero exit code alone is
insufficient. Changes to tests, code, dependencies, tools or policy invalidate affected
evidence; unclear impact requires rerunning the relevant checks, not guessing validity.

## Native application profile

Record a versioned profile for each project:

| Area | Required information |
|---|---|
| Targets | Languages, supported OS/architecture, compiler/runtime and build modes. |
| Inputs | Source snapshot, dependency locks, toolchain and generated-input identities. |
| Checks | Ordered configure/build/test/lint/security/sanitizer commands and pass rules. |
| Runtime | Required GUI/session, GPU/device/driver, services, assets and access limits. |
| Packaging | Install, launch, upgrade/uninstall, signing or package checks where required. |
| Evidence | Expected inventory, coverage mapping, logs, artifacts, skips and warnings. |
| Resources | Time, CPU/memory, parallelism, retry, storage and network budgets. |

Reuse existing C++ presets, ASan/UBSan settings and Clang configuration; see the
[setup guide](setup-guide.md). Other languages supply equivalent project-specific
profiles. C++ is first; support for a language does not imply every OS is supported.

Required unavailable lanes block progression. Optional unexecuted lanes are disclosed.
`not_applicable` requires profile justification; an agent cannot use it to dismiss
an inconvenient check. Known baseline failures remain explicit, not silently waived.
Do not infer GUI, packaging or hardware correctness from unit tests alone.

## Evidence and publication

Use the [record contract](communication-protocol.md) and [protected execution](execution.md).
Pre-PR may reuse evidence only while its complete input identity remains valid.
At merge, recheck repository rules and evidence for the accepted revision and
integration state. Changed source or base integration may require renewed checks.
Ready, merged and verified-after-merge are different outcomes; report what occurred.

Test this gate with empty selections, removed tests, skipped cases, stale binaries,
masked sanitizer errors, malformed/spoofed reports and unavailable runtime environments.
