# Interfaces and adapters

Status: required contract semantics; typed APIs and implementations remain to be defined.

## Product-owned contracts

Our interfaces are designed exclusively for our product's needs. They define our
data structures, meanings, operations, and guarantees. External providers do not
dictate the internal data model.

We care about receiving the data our workflow needs in our defined form, with its
meaning preserved. We are not designing a universal API for every external system.

## Adapters

Adapters translate between provider-specific systems and our contracts, including
data, identifiers, operations, capabilities, and errors. Retain provider identifiers
and source references where needed for traceability and reconciliation.

The workflow consumes our contract, not provider payloads or SDK types. Workflow
policy remains in the workflow; translation belongs in the adapter.

Any provider may be integrated if its adapter fulfils the required contract.
Matching a response shape alone is insufficient: behaviour, permissions, and
guarantees must match too. Missing capabilities must be reported, not fabricated.

Named providers in the architecture are initial or planned implementations, not
an exhaustive list or a limit on what can be connected.

## Runner independence

The core must not contain named-runner branches, provider SDK types, or assumptions
about a CLI. It consumes product-owned invocation, capability, lifecycle, output,
and error records.

An adapter may use a CLI, desktop host, local runtime, hosted agent service, or API
if it fulfils the same contract. Configuration selects runner, provider, and model
per role. The core receives declared capabilities and stable product identifiers;
provider-specific details stay inside the adapter and its evidence.

Runner independence is an architecture rule, not a claim that every runner already
works. Each adapter/version/OS combination must pass conformance before support is
claimed. The public [runner adapter contract](runner-adapters.md) defines the
authoring and acceptance requirements.

## Contract responsibilities

| Interface | Owns | Does not own |
|---|---|---|
| Issue | Discover/read tasks, dependencies, eligibility and visible issue status. | Git branches, PRs, merges or exclusive run locks. |
| Repository and PR | Snapshots, branches, publication, PR state, checks and merge operations. | Task meaning, approval policy or gate decisions. |
| Agent runner | Scoped invocation, model selection, lifecycle, cancellation and attributable outputs. | Permission escalation or accepting its own gate verdict. |
| Execution/evidence | Controlled tool execution, environment identity, protected result capture. | Assuming generated code or logs are trusted. |
| State/checkpoint | Exclusive ownership and recoverable run progress. | Rewriting historical audit events. |
| Audit/artifact | Durable append receipts and protected evidence retention. | Declaring recorded claims true. |
| Memory | Permitted context and approved lesson versions. | Workflow authorization or authoritative execution results. |
| Retrieval | Scoped source selection with identities and freshness. | Choosing which mandatory policy to obey. |

These are logical contracts, not a requirement for separate processes or databases.
GitHub can implement both issue and PR adapters; Jira only implements the task side
unless a separate repository provider is configured. Preserve origin identifiers.

## Runner capabilities

Resolve runner, provider and model per role with shared defaults. Report the actual
host/version and effective model identity, including identity limitations reported
by the provider. Never silently substitute a different model. Reject unsupported
model selections or unverifiable required identity before execution.

Declare supported permissions, test visibility, structured output, cancellation,
resume, telemetry and environment capabilities. Validate them against
[execution requirements](execution.md), not just a successful CLI invocation.
Local inference compatibility does not establish agent-runner compatibility.

Cancellation revokes invocation authority and requests termination of its process
tree. Record whether termination is confirmed; a request alone is not completion.
Reject late results and prevent overlapping write authority while termination or
an external effect remains uncertain. Preserve work and audit evidence for recovery.

## Operations and conformance

Use the [common record/error contract](communication-protocol.md). Every mutating
operation declares its authorization, input preconditions, stable intent identity,
unknown-outcome handling and retry semantics. The controller owns policy; adapters
must still reject dispatch without valid scoped authorization. Raw credentials and
unrestricted provider clients must not escape into agent tools.

Pin tested adapter/provider versions and record capabilities. Contract fixtures must
exercise success, denial, unsupported features, malformed output, timeouts, duplicates,
stale ownership and cancellation. Engram additionally verifies approved-guidance
filtering, retirement and injection paths; see [learning](learning.md).

Missing implementations return explicit unsupported results. Empty stubs must never
simulate success. A fake test adapter cannot satisfy live commissioning evidence.

## Evolution

Change contracts when our product needs change, with explicit versioning and
migration where compatibility breaks. Keep provider-specific details inside adapters
and use contract tests to verify each implementation.
