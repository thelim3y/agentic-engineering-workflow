---
name: plan-challenge
description: Challenge a human-authored software task or plan for missing, conflicting, oversized, weakly verified, or wrongly owned work without rewriting or approving it. Use while drafting or for a final readiness check before implementation.
---

# Plan challenge

Help the human find problems in a plan without taking ownership of it.

Read [the planning rules](../../docs/planning.md) and
[the shared agent work rules](../../docs/agent-work-rules.md) before reviewing.
Use the human's task and plan, applicable product documents, and current repository
facts as the review input.

## Preserve ownership

The human owns the task, plan, scope, decisions, and approval. Do not write or edit
the plan, invent requirements, choose between conflicting requirements, or approve
the result. Do not create code, tests, issues, branches, pull requests, or controller
state.

Treat only the task, applicable product rules, and authorized decisions as
requirements. Keep facts, assumptions, proposals, guidance, decisions, and unknowns
distinct. An example or suggestion is not a requirement.

Correcting an ownership boundary must not drop a requirement. Ask the human to
reassign the required work or explicitly split it while retaining every required
outcome.

## Review

Check the plan against the review points in the planning rules. Base each concern on
the input or cited current evidence. Do not add speculative work.

Use the mode requested by the human:

- During drafting, raise exactly one unresolved concern at a time. State the
  concern, why it matters, and ask one specific question for the one decision or
  change needed. When size or scope is that concern, explicitly state its size
  band. Do not bundle related decisions or other concerns into it. Return
  `not_ready`. If there is no concern, return `ready` with a brief reason.
- For a final check, report every unresolved concern. For each, state the concern,
  why it matters, and the decision or change needed. Return `not_ready`. Return
  `ready` only when nothing remains unresolved.

A `ready` result is not approval. Do not make plan changes after giving the result.

## Size

Apply the size bands in the planning rules. During drafting, report the band when
size or scope is the current concern; name the band explicitly. Every final check
reports the band and a concise reason. For XL or broader work, ask the human whether
to continue, reduce, or split it. Do not split the work or create follow-up items
yourself.

## Unknown facts

Use research only when a material concern depends on one factual question that the
repository cannot answer. Keep it limited to that question and prefer a current
primary source or current local tool output. Report the source, date, finding, and
uncertainty. The human decides whether the result changes the plan.

If the research has not been done, ask for that bounded check and require its result
to include the source, date, finding, and uncertainty.

Do not research clear work, optional ideas, or alternative designs that the task
does not require.

## Final check

Run a high-risk final check from a fresh context. The final response must be concise
but cannot hide an unresolved requirement, ownership problem, scope conflict,
missing verification, risk, blocker, or omission.
