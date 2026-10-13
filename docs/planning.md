# Human-owned planning

Status: required behaviour. The plan-challenge skill implements the agent side;
controller integration is not implemented.

## Ownership

The human writes and approves the task and plan. The human owns scope and material
decisions. There is no planner agent or separate plan-verification agent.

The [plan-challenge skill](../skills/plan-challenge/SKILL.md) reviews the human's
draft without replacing it. `ready` is a review result, not approval.

## Challenge

The skill reads the task and plan, [shared agent work rules](agent-work-rules.md),
applicable product documents, and relevant current repository facts.

While the human is drafting, raise one concern at a time. State:

1. what is unclear, missing, or conflicting;
2. why it matters;
3. what decision or change is needed.

The human changes the plan or explicitly keeps it unchanged. For the final check,
return `ready` when nothing remains unresolved or `not_ready` with every unresolved
concern and its needed decision or change.

Check that:

- requirements have not been lost or changed;
- assumptions and unknowns are visible;
- each responsibility has the correct owner;
- scope and non-goals are clear;
- work is small, ordered, and tied to requirements;
- acceptance criteria and important failures have verification;
- risks, blockers, and omissions are visible;
- every new copy, path, abstraction, or dependency is named and intended;
- claims do not exceed their evidence.

Keep facts, assumptions, proposals, guidance, decisions, and unknowns distinct.
Do not rewrite a clear plan merely to make it longer or more detailed.

## Research

Research only when a concern depends on a bounded factual unknown that current
repository evidence cannot answer. Report the sources, date, finding, and
uncertainty. The human decides whether the finding changes the plan. Clear work
must not trigger research.

Use [retrieval](retrieval.md) for supporting context. Load the task, plan, and
applicable rules directly rather than through search ranking. A high-risk plan gets
its final check from a fresh context.

## Size

Assess scope before implementation, not guessed line counts. Consider affected
parts, shared-interface or behaviour changes, and unresolved work.

| Band | Definition | Action |
|---|---|---|
| Below Large | One focused change, understood approach, limited knock-on effects. | Report the band. No size approval is needed. |
| Large | Several connected changes, understood approach, wider knock-on effects. | Report the band and any useful smaller steps. No size approval is needed. |
| XL and above | Broad changes, major shared-interface changes, or substantial unresolved work. | Ask the human whether to continue, reduce, or split the work. |

Size is an estimate, not a guarantee. Flag risk separately: a small change can
still be risky. Size assessment remains configurable; exact configuration fields
are not yet defined.

## Human decision

At any size, ask for a decision when something is out of place: conflicting
requirements, unclear scope, a rule conflict, a significant risk, or another
unexpected concern affecting safe progress.

Explain the concern with evidence or clear reasoning and ask a specific question.
Do not proceed until it is resolved. Approval does not silently waive a rule.

## Constraints

### Must

- Keep one task aimed at one PR.
- Keep smaller steps inside that task and PR.
- Preserve the original requirements and acceptance criteria.
- Propose corrections when needed; do not silently change requirements.
- Respect shared, agent, and task rules.

### Must not

- Write or edit the human's task or plan.
- Automatically create issues or PRs.
- Write production code or tests.
- Prescribe every class, function, or test case.
- Treat optional guidance as a new requirement.
- Invent missing requirements, make product decisions, or claim approval.

## Output

During drafting, output the one current concern or `ready`; include the size band
when size is that concern. For the final check, output `ready` or `not_ready` with
all unresolved concerns, the size band, and a concise reason for that band.

Use the shared [record contract](communication-protocol.md) when this result is
later integrated into the workflow. Its detailed payload schema remains future
controller work.

## Decision history

The size decision recorded on 10 October 2026 replaced the earlier rule that
oversized tasks always stop for reduction or splitting. XL and above require
approval; Large and smaller tasks continue unless another concern requires a pause.

The human-ownership decision recorded on 12 October 2026 replaced the planner role
with one challenge skill. Planning and approval remain with the human.

Smaller steps help implementation; they do not reduce the combined PR size.
