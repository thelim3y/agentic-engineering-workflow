# Shared agent work rules

Status: required behaviour for every factory agent. Controller enforcement is not
implemented.

## Purpose

Give every factory role the same terms and rules for requirements, ownership,
scope, evidence, and handoffs. They apply to every agent change, report, review,
and handoff, including agent feedback on a human-authored plan.

Role authority remains in the workflow, execution, verification, and
communication contracts.

## Terms

| Term | Meaning |
| --- | --- |
| Outcome | Observable result sought or reached. State whether it is requested or actual. |
| Requirement | Behaviour or constraint set by the authorized task, an applicable contract, or an authorized decision. |
| Acceptance criterion | Observable condition required to satisfy a requirement. |
| Invariant | Condition that must remain true, including during failure and recovery. |
| Responsibility | Behaviour expected from a role or component. |
| Accountable owner | The one role or component answerable for an indivisible requirement. Others may contribute. |
| Boundary | Where one responsibility ends and another begins. |
| Scope | Approved work needed to complete the task. |
| Non-goal | Explicitly excluded behaviour. It does not waive a contract or invariant. |
| Fact | Claim supported by direct observation or a current cited source. |
| Assumption | Unverified premise. |
| Proposal | Suggested but unapproved choice. |
| Decision | Choice made by the authority entitled to make it, for a defined scope or version. |
| Guidance | Non-binding advice. It becomes required only through an authorized task, contract, or decision. |
| Work item | Bounded work that maps to at least one approved requirement. |
| Evidence | Attributable information that directly supports a claim for identified inputs and state. |
| Verification | Assessment of evidence against a requirement, acceptance criterion, or invariant. |
| Risk | Uncertainty that could harm the outcome or an invariant. It is not automatically a blocker. |
| Unknown | Relevant information not yet established. A material unknown blocks progress until resolved. |
| Omission | Required work, ownership, verification, evidence, limitation, or decision that is missing. |
| Blocker | Unresolved condition that prevents safe, correct, or authorized progress. |

An acceptance criterion defines a required result. An invariant must also hold
while reaching that result and when the work fails.

## Rules

### Preserve authority

Why: supporting context must not silently become a requirement. This extends the
[planning rule](planning.md) to every role.

- Use the authorized task and applicable contracts as requirements. Other context
  may support a fact or proposal; it does not create authority.
- The human owns the task, plan, scope, and material decisions. An agent may
  challenge or suggest changes; it cannot silently rewrite or approve the plan.
- Preserve the requested outcome, requirements, and acceptance criteria. Keep
  facts, assumptions, proposals, guidance, decisions, and unknowns distinct.
- Stop when material ambiguity, conflict, unknowns, missing authority, or uncertain
  task impact cannot be resolved from authoritative sources.

### Assign responsibility before work

Why: behaviour belongs with the component responsible for it, not whichever
component can conveniently enforce it. This builds on the role ownership in the
[execution contract](execution.md).

- Give each indivisible requirement one accountable owner.
- Split a requirement when separate parts belong to different owners. Record the
  relationship and any contributors.
- State the affected responsibilities and boundaries before assigning work. Report
  an ownership gap instead of silently choosing an owner.
- Do not change another owner's behaviour or protected inputs without an authorized
  handoff.

Example: "write audit records without secrets" contains two responsibilities. The
producer or controller owns safe event content. The file audit provider owns storage
format, serialization, append, integrity, durability, and recovery. It does not own
secret classification.

### Control scope

Why: plans and unrelated findings must not expand the approved change. This makes
the [workflow's scope rule](workflow.md) explicit for all roles.

- Map every work item to an approved requirement.
- Do not implement a non-goal. Document it when needed to preserve the boundary.
- Report out-of-scope findings without implementing them. Make the smallest change
  that satisfies the requirements and preserves affected invariants.

### Require evidence

Why: a plausible change or passing command proves only what it exercised. This
extends the [verification contract](verification.md) from acceptance
criteria to affected invariants.

- Identify relevant invariants and their owners.
- Map every acceptance criterion and affected invariant to required evidence. The
  role contracts decide who creates and evaluates it.
- State what the evidence proves and its limits. Missing, stale, mismatched, or
  untrustworthy required evidence is not a pass.

### Make handoffs honest

Why: missing work must not hide behind an agent's completion claim. This makes the
reporting rules in the [communication contract](communication-protocol.md)
explicit across handoffs.

- Distinguish the requested outcome from the actual outcome. State completed and
  remaining work, risks, blockers, known omissions, evidence, and limitations.
- Any required work, review, verification, or evidence still omitted blocks a
  complete or ready handoff.
- An agent may propose completion. It cannot approve its own gate, expand its
  authority, or waive another owner's requirement.
- Reassess affected work and decisions after a material change to the task,
  contracts, source, configuration, or evidence.
- Be concise without hiding requirements, risks, limitations, or unresolved
  decisions.

## Boundary

These rules define shared reasoning and reporting. They do not define role
permissions, workflow transitions, schemas, controller checks, or skill output
formats. Those remain with their owning contracts.
