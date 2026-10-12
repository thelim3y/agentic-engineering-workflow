# Adversarial findings — 12 October 2026

Status: review observations and corrective recommendations, not accepted design
changes or implementation authorization. All findings were open at the reviewed
snapshot; later resolution has not been checked. GitHub Issues remains the backlog.

See the [review](2026-10-12-adversarial-review.md) for scope, requirements, verdict,
verification, recommended delivery order and decisions that block implementation.

Repository links are pinned to main
`b758531cf5b7a6ee238a95afd2cf9080f7e2d810` or PR #39 head
`339aa0364d3de12fe08dddba5acf985fe41adf1b`. Issue and external-document links are
references inspected during the review, not immutable snapshots of their later state.

P1 means resolve before relying on the affected guarantee. P2 means correct before
the corresponding milestone. Each finding distinguishes confirmed behavior or text
from judgment and unresolved design. No deployed factory runtime was assessed.

## AR-01 — The contract permits implementation access to tests

**Priority:** P1. **Classification:** confirmed contradiction.

**Evidence:** [Execution](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/execution.md#L55-L58)
makes test visibility configurable, while
[configuration](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/configuration.md#L72-L75)
prohibits only test-writing access. The
[hidden-test fixture](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/fixtures/18-hidden-test-read.sh#L2-L8)
requires reading a protected test as its positive control. These conflict with the
explicit requirement that implementation cannot access test-related inputs.

**Consequence:** an adapter enforcing the intended no-access boundary could fail
the current suite, while an adapter exposing read-only tests passes.

**Corrective direction:** make implementation's read and write exclusion fixed.
Define the permitted behavioral feedback channel separately, including sanitized
failures and interface requirements. Resolve mixed production/test build files
without exposing protected portions. Preserve the distinction between protected
input disclosure to the agent and runtime observations by code executing under test.

**Existing issue overlap:** #8 and #18; their reviewed criteria do not make this
distinction sufficiently explicit.

## AR-02 — Protected test files do not establish trustworthy native test execution

**Priority:** P1. **Classification:** unresolved proof obligation.

**Evidence:** [Verification](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/verification.md#L46-L49)
requires the expected inventory to execute successfully.
[Execution](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/execution.md#L47-L58)
correctly acknowledges that captured output does not prove honest assertions, but
no supported mechanism closes that gap. The
[CMake fixture](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/projects/cmake-configure/CMakeLists.txt)
demonstrates write denial and an allowed build, not hostile linked-code verification.

**Consequence:** adversarial production code linked into a C++ test process can
terminate before assertions or manufacture framework-shaped output without changing
test files. File protection and attributable output alone cannot establish the
required green condition. This is a design counterexample, not a reproduced exploit
against an implemented factory gate.

**Corrective direction:** define precisely what a trustworthy green result
establishes. Where feasible, keep assertions and observation in a separate trusted
driver. For ordinary in-process tests, explicitly bound the guarantee and add
hostile native-code fixtures. Distinguish deterministic record validation from
semantic judgments such as meaningful red, sufficient coverage or a legitimate test
correction. An authenticated model judgment remains fallible.

**Existing issue overlap:** #8, #18 and #20; resolving this proof obligation should
be an explicit commissioning condition.

## AR-03 — Publication can move generated code into a credentialed environment

**Priority:** P1. **Classification:** missing trust-boundary contract.

**Evidence:** [Execution](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/execution.md#L62-L71)
excludes mutation credentials from generated-code environments.
[GitHub onboarding](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/setup-guide.md#L34-L48)
does not assess privileges in automation triggered by publishing that code.
GitHub's [checkout documentation](https://github.com/actions/checkout) describes
persisted credentials enabling authenticated Git commands from workflow scripts.

**Consequence:** a machine-user push can start an existing Actions job with write
permissions and persisted credentials. Generated CMake or test code could perform
authenticated Git operations. Editing workflow YAML is unnecessary. This is a
conditional exposure path, not a claim that this repository has such a workflow.

**Corrective direction:** before the first push, require admission checks for
triggered workflows, tokens, secrets, deployment authority, self-hosted runners,
caches and privileged follow-on jobs. Reject unsafe publication configurations.
Show external execution in the architecture diagram. Local sandbox success does
not cover this boundary.

**Existing issue overlap:** #8, #25 and #27; the reviewed acceptance criteria do not
specify remote-automation admission.

## AR-04 — File-audit completeness is underspecified

**Priority:** P1. **Classification:** missing integrity contract.

**Evidence:** [Audit storage](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/audit.md#L42-L80)
requires ordered events, identities and integrity checks, but does not define how
the verifier knows which events or runs must exist.

**Consequence:** deleting an accepted suffix after the last checkpoint can leave
surviving hashes and checkpoint coverage valid while erasing knowledge of an
external effect. Deleting an entire run leaves no run-local record to inspect.

**Corrective direction:** specify an expected run inventory, accepted sequence/head,
integrity linkage and crash-safe publication rules. Test modification, middle
deletion, reordering, valid-tail truncation and whole-run deletion. State the boundary
for jointly rolling back the log and its integrity witness; administrator-resistant
storage is already explicitly outside the initial guarantee.

**Existing issue overlap:** #13 needs these distinguishing acceptance cases; #14
depends on complete retained operation history.

## AR-05 — PR #39 contradicts per-role runner selection

**Priority:** P1. **Classification:** confirmed contradiction and conformance gap.

**Evidence:** the proposed
[first goal](https://github.com/thelim3y/agentic-engineering-workflow/blob/339aa0364d3de12fe08dddba5acf985fe41adf1b/docs/first-goal.md#L24-L29)
restricts a run to one runner.
[Interfaces](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/interfaces.md#L36-L43)
explicitly select runner, provider and model per role.

**Consequence:** implementing the proposed restriction rejects valid configurations.
Two separately successful single-runner executions also do not establish that
handoffs, cancellation, evidence identities and recovery work across adapters.

**Corrective direction:** replace the restriction with shared defaults plus
independent role overrides. Commission at least one run whose roles use different
adapters, while preserving the requirement that independent adapters satisfy the
same contract.

**Existing issue overlap:** PR #39 and issues #15, #16 and #33.

## AR-06 — Tested code can rewrite its captured transcript

**Priority:** P2. **Classification:** reproduced implementation defect.

**Evidence:** [the collector](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/processes.py#L89-L125)
gives the child a writable, seekable temporary file as stdout/stderr, then reads its
final contents. The review reproduced a child writing an earlier failure, truncating
fd 1 and replacing the output. The collector returned only the replacement with
`rc=0` and `drain_complete=true`.

Minimal reproduction from the reviewed repository root on the Linux environment:

```sh
python3 -B - <<'PY'
import os
import sys
sys.path.insert(0, 'tests/isolation')
import processes
processes.enable_subreaper()
program = (
    'import os; os.write(1,b"EARLIER_FAILURE\\n"); '
    'os.ftruncate(1,0); os.lseek(1,0,0); '
    'os.write(1,b"REPLACED_OUTPUT\\n")'
)
print(processes.run_command(
    [sys.executable, '-B', '-c', program],
    env={'PATH': '/usr/bin:/bin'}, cwd=os.getcwd(), timeout=2))
PY
```

**Consequence:** retained diagnostics need not preserve what the process emitted.
Current fixture judges do not generally use stdout as their verdict, so this does
not establish that every recorded pass is false.

**Corrective direction:** use a pipe or socket feeding a trusted collector that
owns bounded storage. Add an adversarial transcript-rewrite regression.

**Existing issue overlap:** #9 covers output integrity work, but its reviewed
criteria do not explicitly cover transcript rewriting.

## AR-07 — Conformance checks can miss protected effects or disclosures

**Priority:** P2. **Classification:** confirmed inspection findings; the alternate
attacks were not executed during this review.

**Evidence:**

- The synthetic environment credential is also written to
  [`plant/token.txt`](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/runner.py#L69-L80).
  The [bubblewrap](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/adapters/bwrap.sh#L19-L25)
  and [Codex](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/adapters/codex.sh#L34-L39)
  adapters hide other credential paths but leave this copy exposed. Fixture 12
  proves environment scrubbing, not credential secrecy.
- The complete hidden-test body appears in
  [runner source](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/runner.py#L80),
  which is [mounted inside the measured environment](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/runner.py#L305).
  Blocking the designated pathname does not hide its contents.
- Fixture 07 [attempts a Git-hook modification](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/fixtures/07-malicious-configure.sh#L10-L22),
  but its [judge excludes `.git`](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/tests/isolation/fixtures/lib.sh#L7-L15).
  An adapter allowing only that write could pass.

**Consequence:** passing selected path and environment checks does not prove the
broader confidentiality or effect-prevention properties. These are conformance
limitations; the saved logs do not show the measured adapters successfully
performing the protected writes.

**Corrective direction:** keep comparison secrets and protected material outside
attacker-visible inputs, and judge every attempted effect. Test alternate disclosure
paths and adapters that allow only one prohibited effect.

**Existing issue overlap:** #9; these specific cases should be explicit rather
than hidden under a generic harness-integrity requirement.

## AR-08 — Approval withdrawal is undefined

**Priority:** P2. **Classification:** missing authorization transition.

**Evidence:** [approval validity](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/checkpoints.md#L91-L100)
covers changed content and dependencies, but not withdrawal or supersession.

**Consequence:** if a user approves action A and later rejects unchanged A while
dispatch is queued, the earlier approval still satisfies the written dependency
rules. Recording both events does not define which controls authorization.

**Corrective direction:** define decision ordering, explicit revocation, an
authoritative approval revision and a dispatch-time check. Define the honest outcome
when withdrawal races an already-dispatched action. Add approval → withdrawal →
dispatch/restart cases.

**Existing issue overlap:** #12 and #14.

## AR-09 — Optional memory blocks the first useful PR

**Priority:** P2. **Classification:** confirmed dependency and product judgment.

**Evidence:** the [build order](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/build-plan.md#L9-L22)
places context and learning before publication.
[#25](https://github.com/thelim3y/agentic-engineering-workflow/issues/25) explicitly
depends on Engram integration #22. PR #39's
[deployment promise](https://github.com/thelim3y/agentic-engineering-workflow/blob/339aa0364d3de12fe08dddba5acf985fe41adf1b/docs/first-goal.md#L22-L29)
excludes a mandatory server or database for the base workflow, whereas Engram's
[documented architecture](https://github.com/thebtf/engram#architecture) requires a
server and PostgreSQL; its local daemon is a client.

**Consequence:** the first reviewable PR waits on deployment and isolation work for
supporting context, before the basic workflow's benefit has been demonstrated. The
base-workflow dependency and proposed deployment promise cannot both stand as written.

**Corrective direction:** keep Engram selected, make its integration optional and
remove it from the first publication milestone. Evaluate context and learning after
the protected core workflow is commissioned. No alternative memory backend is needed.

**Existing issue overlap:** #22, #25, #28, #29 and PR #39.

## AR-10 — Evaluation can pass without establishing intended usefulness

**Priority:** P2. **Classification:** contract gap and methodological risk.

**Evidence:** [evaluation](https://github.com/thelim3y/agentic-engineering-workflow/blob/b758531cf5b7a6ee238a95afd2cf9080f7e2d810/docs/evaluation.md#L12-L23)
requires representative tasks and repeated trials, but does not explicitly require
multiple real projects of differing complexity and real GitHub issues.
[#28](https://github.com/thelim3y/agentic-engineering-workflow/issues/28) is similarly
broad. The cited [evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
documents advantages gained from previous-trial Git history.

**Consequence:** a synthetic suite in a toy repository could satisfy the written
criteria. Repetition does not repair missing coverage, and multiple projects do not
establish usefulness if solutions or lessons leak between trials.

**Corrective direction:** encode the real-project, complexity and real-issue corpus
requirements now. Project identities and detailed selection can remain undecided.
Before scoring, define:

- Task sampling and results by project and complexity, including legitimate stopping
  tasks.
- A comparable simpler workflow, matched budgets and explicit permission differences.
- Independent outcome checks and human review-effort measurements.
- Clean trial state across Git history, GitHub artifacts, sessions, caches and Engram.
- Held-out tasks and separate evaluations of additional roles, retrieval and lessons.

Establish the evaluation protocol before building all optional features. Execute
real-project trials after safe commissioning.

**Existing issue overlap:** #28 and #29.
