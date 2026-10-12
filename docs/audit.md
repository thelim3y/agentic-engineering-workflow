# Audit and evidence storage

Status: required contract with an implemented [file audit v1 baseline](audit-v1.md).
Full controller integration, artifact storage and retention remain planned.

## Purpose

The audit exists primarily to make runs diagnosable, reproducible and traceable. It
may later supply evidence for ISO-aligned controls, but this design does not claim
certification. Audit availability is not an execution-safety or authorization
boundary: an outage reduces debugging and compliance evidence, and an informed user
may accept that loss for a run.

## Meaning of immutable

Every run has a durable, append-only audit, including failed, cancelled and paused
runs. Agents and their code cannot edit, replace, delete or truncate accepted history
or referenced evidence. Corrections append a new event linked to the original.

This is the required agent-facing boundary, not a claim of resistance to a host
administrator or database owner. Before release, document privileged operators,
backup access, enforcement mechanism, retention and deletion powers. If operator-
resistant retention is required, select and validate suitable independent storage;
ordinary database permissions alone do not establish that guarantee.

Checksums detect changes; they do not prevent them. Immutable storage preserves
what was recorded; it does not make an agent's claim true. The
[communication protocol](communication-protocol.md) distinguishes claims from
controller-owned observations and decisions.

## What is recorded

Submit every action visible to the workflow to the audit, regardless of outcome. This
covers controller decisions and state transitions, agent dispatch and results,
adapter operations, tool requests and executions, gates, approvals, retries,
cancellations, recovery and external operations. Rejected, denied, unsupported,
failed, timed-out and unknown-outcome attempts belong in the history too.

Append authorized intent before an action starts and append its observed outcome
afterward. If an append fails, pause the run, preserve the event and failure details
as pending recovery data, notify the user through the configured channel, and wait
for an explicit decision. The user may retry, abort, or approve continuation while
the audit remains unavailable.

Approved continuation marks the run `audit-degraded`; it does not pretend the append
succeeded. Continue collecting pending events where possible and backfill them in
order after recovery. Record the notification and user decision when storage becomes
available. If any event cannot be recovered, retain an explicit gap marker describing
the affected interval and cause. Reports and exports disclose degraded coverage and
must not claim a complete trace or use that run as compliance evidence.

- Run/task/role/invocation identities and effective configuration.
- Original task, accepted plan, input snapshots and the context actually supplied.
- Agent outputs, tool requests, execution records, artifacts and gate decisions.
- Ownership acquisition/takeover, approvals, invalidations and policy changes.
- Intent and outcome of external operations, retries, failures and unknown outcomes.
- Checkpoints, recovery, cancellation, final reports and approved follow-up issues.

Record observable actions and concise decision reasons. Do not claim access to
hidden model reasoning or record credentials. Identify unavailable telemetry rather
than silently calling an incomplete trace complete.

Audit event names are open, namespaced strings. Use `observation.recorded` for a
useful message or structured event that has no defined type yet. It carries a stable
observation name, source, concise message, optional structured details and references.
It is informational: it cannot advance workflow state, satisfy a gate or override a
defined record. Promote repeated observations to a defined type without rewriting
their original events.

## Storage contract

The controller appends ordered run events with unique event and operation identities.
Duplicate identical appends return the existing receipt; identity reuse with different
content fails. Accepted artifacts have immutable content identities and access labels.
Mutable paths alone are not evidence references. A hash is not a substitute for
retaining the bytes needed to inspect or recover the work.

Audit providers own their storage protection. The common configuration reserves
optional signing and encryption controls with provider-owned key references. The
initial file provider does not implement either option; requesting one must fail
configuration validation. Integrity checks and agent isolation remain required.

Publish referenced artifacts before accepting the event that relies on them. Retain
the durable event position in every checkpoint. Use atomic publication or a
write-ahead/reconciliation protocol where complete audit coverage is required; see
[crash ordering](checkpoints.md). A failed append enters the pause and user-decision
path above. Approved degraded continuation preserves product progress while making
the reduced diagnostic and compliance evidence explicit.

Redact secrets before persistence. Apply hidden-test and project restrictions to
artifacts, indexes, logs, backups and exports. If required evidence cannot be safely
retained, block the affected gate and report the limitation. Do not publish private
runtime logs into this public documentation repository.

## Retention and recovery

Define retention per record/artifact class and disclose its limits. During the
promised retention period, ordinary workflow actions cannot delete retained history.
Active or resumable work and pending external-operation receipts must not expire.
Expiry must not leave a checkpoint appearing usable or evidence appearing available.
Retain operation identities for every permitted retry/recovery path; reject replay
outside that window instead of silently treating it as a new action.

Backups must preserve identities and access controls. Restore tests must demonstrate
complete history and usable artifacts. Restoring old state must reconcile ownership
and remote effects before execution resumes. Missing records or detected tampering
enter the same pause and user-decision path. They are never repaired by inventing
historical events, and approved continuation retains an explicit gap marker.

Verification includes concurrent appends, denied mutation, evidence replacement,
disk-full errors, crashes between writes, redaction, expiry and backup restoration.

## Rationale

[PostgreSQL privileges](https://www.postgresql.org/docs/current/ddl-priv.html) distinguish
application permissions from owner powers. Storage selection must match the declared
threat boundary, rather than treating an append-only application API as sufficient.
