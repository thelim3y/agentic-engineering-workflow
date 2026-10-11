# Audit and evidence storage

Status: required contract; storage, deployment and retention defaults undecided.

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

- Run/task/role/invocation identities and effective configuration.
- Original task, accepted plan, input snapshots and the context actually supplied.
- Agent outputs, tool requests, execution records, artifacts and gate decisions.
- Ownership acquisition/takeover, approvals, invalidations and policy changes.
- Intent and outcome of external operations, retries, failures and unknown outcomes.
- Checkpoints, recovery, cancellation, final reports and approved follow-up issues.

Record observable actions and concise decision reasons. Do not claim access to
hidden model reasoning or record credentials. Identify unavailable telemetry rather
than silently calling an incomplete trace complete.

## Storage contract

The controller appends ordered run events with unique event and operation identities.
Duplicate identical appends return the existing receipt; identity reuse with different
content fails. Accepted artifacts have immutable content identities and access labels.
Mutable paths alone are not evidence references. A hash is not a substitute for
retaining the bytes needed to inspect or recover the work.

Publish referenced artifacts before accepting the event that relies on them. Retain
the durable event position in every checkpoint. Never publish completed state ahead
of its audit coverage; use atomic publication or a write-ahead/reconciliation protocol.
See [crash ordering](checkpoints.md). A failed required append blocks further work.

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
block progression; they are not repaired by inventing historical events.

Verification includes concurrent appends, denied mutation, evidence replacement,
disk-full errors, crashes between writes, redaction, expiry and backup restoration.

## Rationale

[PostgreSQL privileges](https://www.postgresql.org/docs/current/ddl-priv.html) distinguish
application permissions from owner powers. Storage selection must match the declared
threat boundary, rather than treating an append-only application API as sufficient.
