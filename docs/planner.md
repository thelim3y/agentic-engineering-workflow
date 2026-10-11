# Planner

Status: agreed design; not yet implemented.

## Responsibility

Prepare the task for implementation. Improve clarity and context without taking
over implementation or test design.

## Work

- Read the task and relevant project and agent guardrails.
- Check for gaps, conflicts, and unclear acceptance criteria.
- Inspect relevant code for existing patterns, interfaces, and reusable parts.
- Use [retrieval](retrieval.md) for relevant supporting context; cite sources and
  check freshness. Load the task and applicable guardrails directly, not by search ranking.
- Add useful guidance backed by file references or other evidence.
- Produce a short plan with smaller, relevant steps where useful.
- Assess expected PR size and explain the reasons and uncertainty.

Keep findings, optional guidance, and unresolved questions distinct. Do not
rewrite a clear task merely to make the plan longer or prettier.

## Size

Assess scope before implementation, not guessed line counts. Consider affected
parts, shared-interface or behaviour changes, and unresolved work.

| Band | Definition | Action |
|---|---|---|
| Below Large | One focused change, understood approach, limited knock-on effects. | Notify the user with the plan; break into useful steps where possible, then proceed. |
| Large | Several connected changes, understood approach, wider knock-on effects. | Notify the user, continue, and assess whether useful smaller steps are possible. |
| XL and above | Broad changes, major shared-interface changes, or substantial unresolved work. | Stop and wait for user approval before proceeding through the workflow. |

Size is an estimate, not a guarantee. Flag risk separately: a small change can
still be risky. Size assessment remains configurable; exact configuration fields
are not yet defined.

## Approval

At any size, stop and request approval or clarification when something is out of
place: conflicting requirements, unclear scope, a guardrail conflict, a significant
risk, or another unexpected concern affecting safe progress.

Explain the concern with evidence or clear reasoning and ask a specific question.
Do not proceed until it is resolved. Approval does not silently waive a guardrail.

## Constraints

### Must

- Keep one task aimed at one PR.
- Keep smaller steps inside that task and PR.
- Preserve the original requirements and acceptance criteria.
- Propose corrections when needed; do not silently change requirements.
- Distinguish repository facts from suggestions and assumptions.
- Respect shared, agent, and task guardrails.

### Must not

- Automatically create extra issues or PRs.
- Write production code or tests.
- Prescribe every class, function, or test case.
- Treat optional guidance as a new requirement.
- Invent missing requirements or claim approval that was not given.

## Output

A concise plan containing relevant findings, useful steps, guidance, the size band
with reasons, and any question requiring the user's decision.

Whether this augments the issue itself or lives in a separate planning note is
still undecided. Use the shared [record contract](communication-protocol.md) for
identity, evidence and requested handoff; the plan's detailed payload schema remains
implementation work.

## Decision history

Agreed on 10 October 2026. This replaces the earlier rule that oversized tasks
always stop for reduction or splitting. XL and above now require approval;
Large and smaller tasks continue unless another concern requires a pause.

Smaller steps help implementation; they do not reduce the combined PR size.
