# Proposal: Duplicated-code check

Status: proposed for
[#64](https://github.com/thelim3y/agentic-engineering-workflow/issues/64); not
approved. Contracts are unchanged until it is.

## Need

A change can repeat existing code while every test passes. The plan challenge
catches only copies the plan names. This check catches the rest before a change is
PR-ready. Evidence: #64 and the
[research findings](../research/README.md#duplication-while-tests-stay-green).

## Decision

Add one deterministic check as a pre-PR lane of the project
[verification profile](../docs/verification.md). It reports each new copy with both
locations. The human decides whether each copy stays. No agent can waive a finding.

## What is reported

A finding is a pair of code fragments the detector judges to be copies, where at
least one fragment overlaps lines the change adds or modifies relative to its base.
This covers copies of base code and copies made within the change.

- A pair wholly in the base is not reported; it is not this change's work.
- A base pair the change edits is reported; the human can keep it.
- Each finding names both files and line ranges.

Only production paths are scanned; tests repeat setup by convention, which would
raise false findings. The profile sets those paths, languages, minimum fragment
size and similarity threshold. C++ is first.

## Detector

Use an existing, maintained, permissively licensed tool that meets the fixtures.
It must:

- ignore whitespace, comments and formatting;
- match copies with renamed identifiers or changed literals;
- match copies with a few statements inserted, removed or changed;
- report both locations of each pair.

Remove in-source suppression markers from the scanned copy; an agent could add
them. Intended copies are marked only by the human's approval. The tool, its
version, thresholds, paths and exclusions are protected verification inputs under
[execution](../docs/execution.md). Changing them needs an authorized configuration
change.

Tool: PMD CPD, ignoring identifiers and literals. On synthetic C++ fixtures it
caught the renamed and small-edit copies and stayed silent on the
convention-similar code from 70 to 245 tokens. Its report lists every scanned
file, which the scan inventory needs. Evidence:
[duplication tool status](../docs/spikes/duplication-tools.md).

## Where it runs

In pre-PR, on the exact snapshot to be published, under controlled execution
outside agent write authority. Evidence binds to head and base, so a source repair
or a new base reruns it.

## Evidence

Use the existing [record contract](../docs/communication-protocol.md); add no
record type.

- **Execution record:** head and base content identities, tool version,
  configuration identity, scan inventory (files and languages scanned) and findings.
- **Gate decision:**
  - `passed`: every in-scope file was scanned and every finding is approved;
  - `failed`: a finding is unresolved;
  - `blocked`: the tool is unavailable, the inventory is empty or reduced, or an
    identity is stale.

## Resolution

The gate reports every unresolved finding, with both locations, to the human. PR
evidence carries the findings and their resolutions to the reviewer. The human
decides each finding:

- **Keep.** The controller records an approval bound to both fragments' content and
  the configuration. An edit to either fragment reopens it.
- **Remove.** The human amends the plan to reuse the named existing code. Work
  resumes through the normal TDD, implementation and testing loop; the check then
  reruns. The instruction is to reuse that code, not to make the check pass.

Neither the implementer nor the reviewer can approve, suppress or reconfigure a
finding. A copy named in the approved plan is still confirmed at its finding:
matching plan text to a finding is judgement, and the gate must not rest on it.

Agent instructions and AI review may flag more; the gate rests on the check.

## Limits

The check catches accidental copies above the profile's thresholds. It does not
catch deliberate obfuscation, copies below the thresholds, or code that repeats
behaviour without repeating its text. A pass means no reported copy, not no
duplication.

## Verification

| Fixture | Expected | Source |
| --- | --- | --- |
| Pass copied with renamed variables | Finding with both locations | #64 Verification |
| Pass copied with small edits: case 11's forward and terrain passes | Finding with both locations | #64 acceptance criterion 2 |
| Unrelated code similar by convention | No finding | #64 Verification |
| Copy made within the change | Finding | What is reported |
| Pair wholly in the base | No finding | What is reported |
| Approved finding, then one fragment edited | Finding reopens | Resolution |
| Tool unavailable | `blocked` | [Verification](../docs/verification.md): required unavailable lanes block |
| Empty or reduced scan | `blocked` | [Verification](../docs/verification.md): empty selections and removed tests |
| Head, base or configuration changed after the run | Evidence stale | #64 acceptance criterion 4 |

Case 11 is `tests/skills/plan-challenge/11-unintended-shape.md`.

## Delivery

1. Record the approved behaviour in its owning contracts:
   `docs/verification.md` for the lane, evidence and gate, and `docs/workflow.md`
   for routing findings to the human.
2. TDD writes the fixtures; the implementer cannot change them.
3. Run candidate tools against the fixtures and record the results. Select one or
   stop for a decision.
4. Build the standalone check: head and base in; findings and inventory out. This
   meets acceptance criterion 2.
5. Bind it as a pre-PR lane. This needs the record contract (#12), controller (#16)
   and C++ profile (#20), and meets acceptance criteria 3 and 4.

Out of scope: removing duplication already in a project, automatic refactoring,
AI-review prompts, a detector of our own, and languages after C++.
