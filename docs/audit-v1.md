# File audit v1

Status: implemented baseline on the [initial runtime boundary](decisions/0003-initial-runtime-boundary.md),
CPython 3.12 and a local Linux filesystem. This is a library and an observation
command, not a controller or commissioned agent runner.
The broader [audit contract](audit.md) remains the direction for later integration.

## Use

Run from the repository root; there are no third-party Python dependencies. The
trusted caller imports `EventV1` from `aew.audit.v1` and `FileAuditV1` from
`aew.audit.file_v1`. Create storage once with `FileAuditV1.create_v1(path,
workspace_roots=[...])`; reopen with `FileAuditV1(path, workspace_roots=[...])`.
Opening missing or damaged storage never creates a replacement.

The smallest real producer is the local observation command:

```sh
mkdir -p /tmp/aew-example-work
python3 -m aew.audit v1 --store /tmp/aew-example-audit --workspace /tmp/aew-example-work init
python3 -m aew.audit v1 --store /tmp/aew-example-audit --workspace /tmp/aew-example-work observe \
  --record-id 00000000-0000-4000-8000-000000000001 \
  --run-id 00000000-0000-4000-8000-000000000010 \
  --recorded-at 2026-10-12T09:00:00Z --project example --task task-1 \
  --name example.started --message 'Started the example'
python3 -m aew.audit v1 --store /tmp/aew-example-audit --workspace /tmp/aew-example-work read
python3 -m aew.audit v1 --store /tmp/aew-example-audit --workspace /tmp/aew-example-work verify
```

Choose a new directory for another example. Preserve the IDs, timestamp and content
when retrying. The command constructs an `observation.recorded` envelope, appends it,
and prints its receipt. It does not launch work, authenticate an agent's claimed
provenance, or implement degraded workflow continuation.

## Product API

`EventV1(record)` validates and takes an immutable canonical snapshot of exactly:

| Field | v1 meaning |
| --- | --- |
| `schema_version` | Integer `1`; unknown versions fail explicitly. |
| `record_id`, `run_id` | Canonical UUID strings, assigned and retained by the caller. Event IDs are globally unique within the store. |
| `record_type` | Open namespaced name such as `action.failed` or `observation.recorded`; unknown names remain readable. |
| `task_ref` | Nonempty `provider`, `project`, `id` strings; no provider SDK types. |
| `recorded_at` | Caller-supplied UTC RFC 3339 timestamp, up to six fractional digits. It is not the ordering authority. |
| `provenance` | `kind` (`controller`, `adapter`, `agent`, `operator`) and nonempty `source`. The trusted caller owns attribution. |
| `details` | JSON object containing sanitized action data; observations carry a stable `name` and concise `message`. |

Use `to_dict()` for a copy. JSON object keys must be strings, numbers finite,
integers within the interoperable ±(2^53−1) range. Events are limited to 64 KiB of
canonical UTF-8 and nesting depth 16. No automatic timestamp or identity changes.
Breaking changes require a new major API and an explicit migration; v1 is not
silently reinterpreted. Full invocation, gate, approval and evidence validators are
outside this slice; arbitrary details never grant authority or validate a gate.

| Operation | Result |
| --- | --- |
| `append_v1(event)` | Durable `ReceiptV1(sequence, record_id, run_id, digest)`. An identical retry returns its original receipt; conflicting content fails. |
| `read_v1()` | Tuple of accepted `EventV1` values in global sequence order, after full verification. |
| `verify_v1()` | `VerificationV1(count, head, run_ids)` after full verification. |

Concurrent local callers serialize through a stable `flock` file. Lock acquisition
defines order, independent of timestamps; racing callers have no promised relative
arrival order. Readers also lock, so they never observe an in-process partial
commit. Locks time out after five seconds with `busy`. All operations scan the
history in memory: suitable for a baseline, not an unbounded production workload.

## Durability, detection and recovery

`events.jsonl` holds canonical records linked by SHA-256, sequence and unique event
ID. Each digest covers sequence, previous digest and the complete event. A separate
`head.json` retains accepted byte length, count, chain head and expected run inventory.
Verification checks both, including all identity and envelope constraints.

The append protocol, under the exclusive lock, is:

1. Verify the accepted prefix and head. Publish the next line's hash and length as
   a pending intent using a private temporary head, file `fsync`, atomic rename,
   then directory `fsync`.
2. Append the line with short-write handling and `fsync` the journal.
3. Atomically publish and flush the new accepted head, clearing pending intent.
4. Return the receipt only after the final directory flush.

A restart with pending intent reports `interrupted_append` on read/verify. Only an
exact retry whose canonical line matches that intent may finish it: the existing
tail must be an exact prefix, the intent is flushed again, and only missing bytes
are appended. A complete line written before a crash can also be accepted this
way. No truncation, fabricated history or automatic selection of an older head.
Retain the sanitized pending event outside the failed store to make retry possible;
the intent retains its hash, not a recoverable copy of the event. Temporary
`.head-*` files left by failed writes are unaccepted and ignored; an operator can
remove these with all callers stopped. An interrupted initial creation is likewise
not a valid store and requires inspection, not reinitialization over existing files.

Tests detect changed events, insertion, duplication, reordering, middle deletion,
valid suffix deletion, whole-run removal, journal deletion and isolated head
rollback. Missing head, lock or store is an error. A joint rollback/rewrite of the
journal **and** matching head cannot be detected; complete replacement with a valid
older store cannot be detected either. No independent witness or administrator
resistance is claimed. Flush ordering relies on the local filesystem and device
honoring `fsync` and atomic rename; injected failures and process death do not prove
physical power-loss behavior. Network filesystems are outside this boundary.

## Protection and secrets

The provider enforces a private owned directory (0700), owned regular files (0600),
no hard links or symlink paths, trusted parent directories, and separation from the
declared agent workspace roots. Parent owners must be the caller or the filesystem
root owner (including its user-namespace mapping); writable ancestors require the
sticky bit. All handles are close-on-exec. The provider exposes no mutation API for
accepted records.

**The trusted caller must run outside agent filesystem and process authority.**
File modes and workspace paths alone do not protect against unrestricted code
running as the same OS user. Mount/process isolation or a separate OS identity must
deny agents the store, the trusted process, its descriptors and any mutation tools.
The boundary test proves denied direct, replacement, deletion, symlink, subprocess
and `/proc` writes in a restricted workspace while allowed workspace writes work.
It uses bubblewrap only as a test fixture; the product API has no runner dependency.
This is bounded evidence, not certification of any real agent integration. The host
administrator and trusted storage/controller owners retain replacement/deletion
powers; retention automation and backups do not exist yet.

Before persistence, the envelope rejects common credential keys, bearer tokens,
private-key markers and recognizable token formats throughout its contents. The
provider additionally rejects caller-supplied `secret_values` wherever they occur
in string keys/values; register credentials from the trusted secret source, never
from agent input. Errors do not echo rejected values or raw OS paths. This is
defense in depth: no pattern matcher can identify arbitrary unknown, encoded or
split secrets. Callers must construct allowlisted sanitized details, never forward
raw configuration, environment variables, prompts or tool output. This slice
rejects instead of storing a silently altered event.

## Failures and caller policy

Every expected failure raises `AuditErrorV1` with a stable `code`, safe message,
`acceptance`, optional `phase`, OS `errno`, and (for append IO failure) sanitized
`pending_event`. `not_attempted` means this call did not enter the write protocol;
it says nothing about earlier attempts. `unknown` means acceptance or durability
cannot be confirmed. Retrying the same event resolves a lost receipt safely.

| Code | Meaning / next action |
| --- | --- |
| `invalid_event`, `unsupported_version`, `invalid_configuration`, `secret_rejected` | Correct or sanitize input; no append attempted. |
| `identity_conflict` | Reused identity with different accepted content; preserve the original and use a new event for a correction. |
| `busy` | Another caller holds the lock; retry the same event. |
| `interrupted_append`, `pending_conflict` | Preserve pending data; retry the exact outstanding event first. |
| `integrity_error`, `storage_missing`, `unsafe_storage` | Preserve state and inspect the store or deployment boundary. Do not overwrite or invent history. |
| `permission_denied`, `io_error`, `already_exists` | Inspect the phase/errno and configuration; retry when corrected. Creation never overwrites. |

The caller can notify the user and choose retry, abort or explicit audit-degraded
continuation. This library does not impose a global execution stop or grant
execution authority. A failure never becomes a successful receipt. The command
prints safe failure JSON and those choices with exit status 1. Preserve its exact
sanitized arguments for retry. A future controller owns pending-event retention,
notifications, user decisions, ordered backfill and permanent gap markers.

## Verification and deferred work

```sh
python3 -B -m unittest discover -s tests/audit -p 'test_*.py' -v
python3 -B -m unittest discover -s tests/isolation -p 'test_*.py'
git diff --check
```

The audit suite requires Linux, Python 3.12 and bubblewrap with user namespaces.
A surrounding sandbox may prevent its isolation fixture from starting; that is a
failed environment check, not proof that mutation was denied. Run it on the declared
host boundary. Tests cover concurrent processes, exact retries, corruption, partial
writes, process death, every append flush failure, secret rejection and the real
observation command. The joint-rollback test explicitly demonstrates the limit.

Verified on 12 October 2026 against main `ca949b2`: 28 audit tests and 52 existing
isolation regression tests passed on Ubuntu 24.04, Python 3.12.3 and bubblewrap
0.9.0. The audit fixture required running outside the surrounding agent sandbox;
that sandbox denied namespace setup before any attack ran. Nine new Python files
passed Black 24.10.0 checks at line length 100 (direct API; CLI worker shutdown
stalled in the surrounding environment). `git diff --check` passed.

TDD regression evidence: the pending-retry test first failed because journal bytes
were written before re-flushing a previously ambiguous intent. The symlink-loop
test first failed because the command emitted a raw path-bearing traceback instead
of safe error JSON. Both pass with the corresponding fixes.

Deferred: encryption, signing/key management, external witnesses, databases, remote
and multi-host storage, enterprise RBAC, retention/backup automation, full artifact
storage, generic provider/plugin frameworks, controller orchestration and ISO
certification. Artifact/checkpoint publication, full record schemas, automatic
backfill/gap records and real runner commissioning remain broader #12/#13/#43 work.
No placeholders or unsupported configuration switches are exposed for them.
