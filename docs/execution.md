# Execution boundary

Status: required contract; enforcement technology is undecided. The initial platform
is CPython 3.12 on Ubuntu 24.04 LTS x86-64 under the support boundary in
[ADR-0003](decisions/0003-initial-runtime-boundary.md). No adapter or execution
provider is supported until its actual boundary passes conformance tests.

## Trusted control, untrusted work

The controller owns policy, gate decisions, operation authorization, authoritative
state and evidence collection. Agents propose changes and explanations. Repository
content, retrieved text, generated code, build scripts and subprocesses are untrusted.

Use isolated execution or a controlled change-application boundary backed by runtime
isolation. Prompt instructions, edit hooks, Git branches and after-the-fact hashes
alone do not establish prevention. A patch filter does not contain executed code.

Untrusted execution must not modify controller code, policy, approved inputs,
other roles' work, checkpoints, audit history or authoritative result records.
Enforce filesystem, process, credential, tool and network permissions outside the
model. Children inherit the same restrictions. Reject unsupported configurations.

## Ownership

| Role | May change | Cannot authorize |
|---|---|---|
| TDD | Tests, fixtures and test assets within the approved task | Weakened acceptance criteria, policy or verifier control. |
| Implementer | Production code and permitted production build inputs | Any tests or protected verification inputs. |
| Testing / pre-PR / PR review | Reports and permitted temporary build outputs | Source fixes, test fixes or their own passing gate. |
| Merge | A scoped merge request through the controller | Code changes, stale approvals or repository-rule bypasses. |

Protected verification inputs include test discovery/registration, selectors,
fixtures, mocks, golden data, thresholds, suppressions, result parsers, runner
commands and relevant shared build settings. TDD owns test changes; workflow policy
and trusted verifier settings require separate authorized configuration changes.
For mixed production/test files, use mediated, owner-checked edits. File extensions
alone cannot determine ownership.

The implementer may request a test correction with evidence, but cannot apply it.
TDD handles clear corrections; disputed behaviour or reduced coverage requires
human approval bound to the exact proposal. Requirement gaps return to human planning.

## Workspaces and verification

- Give each invocation an identified workspace and permitted input snapshot.
- Preserve user changes; do not use the operator's unrestricted checkout as a sandbox.
- Accept only owner-permitted changes into the next source snapshot.
- Build and test that exact snapshot in a controlled environment, with protected
  verification inputs. Treat configure steps and dependency hooks as code execution.
- Keep authoritative capture and gate evaluation outside the write/process authority
  of the tested program. Report files inside a sandbox are untrusted outputs.
- Check actual test inventory, process completion and diagnostics. Captured stdout
  is attributable output, not proof that every assertion is honest or sufficient.
- Do not reuse builds or caches without matching identities and isolation controls.

Implementation cannot read or write test-related inputs. Controller-approved
diagnostic feedback is a separate bounded output, not test visibility. The boundary
must cover tool output, process access, caches, memory and artifacts. Code executing
in a test process may observe runtime inputs; do not promise complete behavioural
secrecy. Reject an isolation guarantee the execution provider cannot prove.

## External actions and secrets

Keep GitHub mutation credentials, SSH-agent sockets and storage-admin credentials
outside agent and generated-code environments. Keep model credentials outside
generated-code execution too; limit any host access needed for inference.

Agents request external actions through scoped tools. The controller checks current
ownership, label eligibility, policy, approval and evidence before dispatch. A
credential-hiding proxy must also restrict operations; hiding a token alone does
not prevent unauthorized use. Direct unrestricted `gh`, Git push, merge or storage
access must not bypass this path. Existing machine-user credentials are reused
through the trusted integration, not copied into every role environment.

## Proof required before onboarding

For each host/version/OS, test direct edits, shell redirection, symlinks/path traversal,
child processes, mixed build files, malicious configure/test code, cache poisoning,
result spoofing, credential access, network escape, hidden-test disclosure, cancellation
and late outputs. Include allowed operations so a sandbox that blocks all work
cannot pass. Loss of isolation stops the run; it never enables wider permissions.

See [verification](verification.md), [adapter contracts](interfaces.md) and the
[trust decision](decisions/0001-trusted-workflow-boundaries.md). The initial runtime,
topology and adversary boundary are fixed in
[ADR-0003](decisions/0003-initial-runtime-boundary.md).
