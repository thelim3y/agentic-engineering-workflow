# Plan: Human-authored planning and plan challenge

Status: approved planning decision. Skill implementation has not started. Approval
of this document does not authorize issue creation or implementation work.

## Decision

The human writes and approves the task and plan.

There will be no planner agent and no separate plan-verification agent. One
plan-challenge skill reviews the human's draft. It asks one focused question at a
time and never replaces the plan.

Research is optional and is used only when a question depends on an unknown fact.

## Scope

Deliver:

- shared agent work rules at `docs/agent-work-rules.md`;
- human-owned planning rules at `docs/planning.md`;
- one skill at `skills/plan-challenge/SKILL.md`;
- ten tests at `tests/skills/plan-challenge/`.

Out of scope: planning agents, automatic task or plan editing, controller checks,
issue creation, pull request creation, and merge.

## Basis

The human has the product context and authority. An agent-written plan can silently
change that intent. The useful agent behaviour is to find a problem, explain it, and
ask for a decision.

The design uses:

- [Superpowers writing-plans](https://github.com/obra/superpowers/blob/main/skills/writing-plans/SKILL.md)
  for small, ordered, verifiable work items, but not agent plan ownership;
- [GitHub Spec Kit analyze](https://github.com/github/spec-kit/blob/main/templates/commands/analyze.md)
  for coverage and consistency checks;
- [gstack plan-eng-review](https://github.com/garrytan/gstack/blob/main/plan-eng-review/SKILL.md)
  for interactive challenge and an optional fresh second look.

Human plan ownership and one-question-at-a-time review are project decisions.

## Skill behaviour

Input:

- the human-authored task and plan;
- shared agent work rules;
- applicable product documents;
- relevant, current repository facts.

While the human is drafting, the skill raises one concern at a time. Each concern
states:

1. what is unclear, missing, or conflicting;
2. why it matters;
3. what decision or change is needed.

The human changes the plan or explicitly keeps it unchanged.

For a final check, the skill returns:

- `ready` when it finds no unresolved concern; or
- `not_ready` with every unresolved concern and the needed decision or change.

`ready` is a review result. The human approves the plan.

The skill checks:

1. requirements have not been lost or changed;
2. assumptions and unknowns are visible;
3. each responsibility has the correct owner;
4. scope and non-goals are clear;
5. work is small, ordered, and tied to requirements;
6. acceptance criteria and important failures have verification;
7. risks, blockers, and omissions are visible;
8. claims do not exceed their evidence.

The skill does not write or edit the plan, invent requirements, make product
decisions, write code or tests, create issues or pull requests, or approve the plan.

Research answers one bounded factual question and reports its sources, date,
finding, and uncertainty. The human decides whether it changes the plan. Clear work
must not trigger research.

A high-risk plan gets its final check from a fresh context.

## Proposed tests

No tests exist yet. These ten cases must be written before the skill:

| Case | Required result |
| --- | --- |
| Clear small plan | Return `ready` without adding work, research, or questions. |
| Mechanical rename | Keep the work narrow and reject unrelated architecture or configuration. |
| Missing requirement | Ask one specific question without inventing the answer. |
| Conflicting requirements | Identify the conflict and ask the human to decide. |
| Audit ownership | Keep secret removal with the producer or controller and file persistence with the audit provider. |
| Optional guidance | Do not turn advice or an example into required work. |
| Oversized work | Explain the size problem and ask for a human decision. Create nothing. |
| Weak verification | Identify the result or failure case that lacks evidence. |
| Factual unknown | Request bounded research only when repository evidence cannot answer it. |
| Several problems | Ask one question at a time while drafting; report every unresolved concern in the final check. |

Each case defines its input, required result, forbidden result, and expected status.
Tests judge the decision, not exact wording.

## Work

1. Move the approved [shared agent work rules](agent-work-rules.md) to
   `docs/agent-work-rules.md` and add them to the design index.
2. Replace `docs/planner.md` with `docs/planning.md`. Record human plan ownership,
   challenge behaviour, optional research, and size handling. Update all links.
3. Have a separate test author write and protect the ten tests before skill
   implementation. The skill implementer cannot change them.
4. Add the smallest `skills/plan-challenge/SKILL.md` that follows
   `docs/planning.md`.
5. Run every test from a fresh context. Fix problems in their owning document,
   test, or skill, then rerun all tests.

## Completion

- The shared rules and planning document are approved.
- All ten tests pass and the skill implementer did not change them.
- No planner or plan-verification agent exists.
- Nothing required remains omitted or unresolved.
- Documentation matches tested behaviour.
- Controller integration remains absent.

Do not create an implementation pull request while anything is unresolved. Any
merge requires a new explicit user instruction.
