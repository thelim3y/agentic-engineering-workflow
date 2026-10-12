# Communication and evidence contract

Status: authoritative v1 design semantics. The minimal [audit envelope](audit-v1.md)
is implemented; full record schemas and validators remain planned. This replaces
the legacy agent/ticket/verdict header. Guides link
here rather than maintaining alternate field lists.

## Common identity

Every record has `schema_version`, `record_id`, `record_type`, `run_id`, `task_ref`,
`recorded_at` and provenance. `task_ref` includes provider instance, project/repository
identity and native task identifier; an issue number alone is not unique.

Controller-owned fields are assigned or verified by the controller, not trusted
because the agent echoed them. The transport binds a response to its authorized
invocation and role. A role name in YAML is not authentication.

## Record types

| Type | Required contents | Authority |
|---|---|---|
| Invocation | Stage, batch if applicable, invocation ID, attempt, role, owner generation, input bundle identity, effective runner/provider/model, permissions and budgets. | Controller issues it after validation. |
| Agent report | Invocation ID, concise summary, proposed outcome, evidence references, produced artifact references, findings, limitations and requested handoff. | Agent claim; cannot advance a gate. |
| Execution | Invocation/operation IDs, exact input identities, command and arguments, working directory, tool/environment versions, start/end, termination reason, exit status where available, diagnostics and artifact references. | Controlled runner records observed execution. |
| Gate decision | Gate ID, outcome, rule/configuration identity, evidence references, reasons, coverage and unresolved work. | Controller evaluates current records. |
| Approval | Proposal/action identity and content, scope, dependency identities, authenticated human identity, decision, timestamp and optional reason. | Human decision recorded by controller. |
| External operation | Stable intent ID, payload identity, target, owner generation, authorization/evidence references, dispatch attempt, state and provider receipt. | Trusted integration; recovery rules apply. |
| Observation | Stable namespaced observation name, source, concise message, optional structured details and references. | Informational only; cannot advance a gate or override a defined record. |

An input bundle identifies task, plan, applicable policy, effective configuration,
source/base snapshot, test/verification manifest, dependencies and relevant environment.
Capture dirty work by content identity, not commit SHA alone. Retain recoverable
content behind those identities. Not-applicable fields require an explicit reason.

Execution records for test runs additionally include expected/discovered/executed
inventory, framework-level cases where available, failures, skips, filters and
requirement mapping. Build failures, unavailable environments and empty selections
are not meaningful behavioural red. See [verification](verification.md).

Artifact references include immutable content identity, media type, retained location
and access classification. File/line references are useful context, not execution
proof. The collector records output provenance; it does not treat agent-produced
logs or stdout as intrinsically trustworthy.

## Outcomes and errors

Agent reports propose `complete`, `needs_user`, `blocked` or `failed`. `needs_user`
requires a specific question/proposal; blocked/failed require a typed reason and
supporting evidence. `complete` means the role proposes its work is complete, not
that checks passed, a PR merged or the task finished.

Gate outcomes are `passed`, `failed`, `blocked`, `not_run` or `not_applicable`.
Missing, stale or untrustworthy required evidence blocks the gate. Skips and warnings
are recorded separately; applicability and acceptable skips come from policy.

Use typed errors for invalid input, unsupported capability, permission denied,
ownership conflict, stale input, unavailable environment/provider, exhausted budget,
invalid output and unknown external outcome. Include a concise explanation and
safe next action. Transport errors cannot silently become task success.

External-operation states distinguish `pending`, `succeeded`, `failed` and `unknown`.
Timeout is not proof of failure. See [recovery](checkpoints.md).

## Acceptance and compatibility

Validate schema/version, identity, current ownership, input bindings, role permissions
and evidence access before accepting a result. Reject stale, unsolicited, mismatched
or malformed reports without advancing. An identical duplicate receives its existing
receipt; duplicate IDs with different content are conflicts. Preserve rejection
events with appropriate redaction.

Late output from a cancelled invocation or old owner cannot advance the run. Input
changes require a new invocation or explicit revalidation, never relabelling old
evidence as fresh. Free-form notes cannot override structured fields or policy.

Unknown schema versions fail explicitly. Define migrations and conformance fixtures
before evolving the wire format; optional extensions cannot redefine existing meaning.
Readers preserve and display unknown event names in a known envelope, but do not use
them for control decisions unless a configured extension defines their semantics.
Adapters must preserve provenance and unsupported/unknown outcomes.

All explanations remain concise. Full evidence lives in protected artifacts rather
than being duplicated into every handoff or terminal report.
