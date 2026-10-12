# Runner adapter contract

Status: required authoring contract. Machine-readable schemas, reference adapter,
and conformance kit are planned in
[issue #33](https://github.com/thelim3y/agentic-engineering-workflow/issues/33).

## Principle

Any runner may be integrated if it satisfies the required contract. This is not a
claim that every runner has the required capabilities.

An adapter translates between one runner and the factory's product-owned records.
Adding a conformant adapter must not require controller, workflow, policy, or record
changes. Named runner, provider, model, CLI, SDK, and payload details stay inside
the adapter.

## Responsibility

An adapter:

- declares its identity, contract version, tested environment, and capabilities;
- translates a validated invocation into runner-specific input;
- starts and observes the runner in the supplied execution boundary;
- attributes events and results to the issued invocation;
- validates runner output before exposing product records;
- requests cancellation and reports whether termination is confirmed;
- normalizes output, usage, limitations, and errors without inventing support;
- reconciles an operation whose outcome is unknown.

An adapter does not:

- choose workflow transitions, retries, approvals, or gate results;
- widen permissions or substitute a runner, provider, or model;
- decide whether tests or evidence pass;
- mutate issues, repositories, audit history, or checkpoints outside authorized
  controller operations.

## Required contract surface

The versioned contract must cover these logical operations. Exact language types
and transport remain implementation work.

| Operation | Required behavior |
|---|---|
| Describe | Return adapter, runner, provider, model-selection, platform, contract-version, permission, tool, output, cancellation, resume, and telemetry capabilities. |
| Start | Accept one validated invocation idempotently and return a stable run handle or an explicit failure before execution. |
| Observe | Return attributable, ordered events and bounded output without treating runner prose as authority. |
| Cancel | Request cancellation, terminate permitted descendants where supported, and distinguish requested from confirmed termination. |
| Complete | Return at most one terminal result bound to the invocation, input bundle, role, owner generation, and actual runner/provider/model identities. |
| Reconcile | Resolve or preserve an unknown outcome without blindly repeating external effects. |

An invocation includes:

- contract version, invocation ID, role, attempt, and owner generation;
- immutable input and configuration identities;
- workspace and permitted tools;
- runner, provider, and model selection;
- permissions, visibility, time, resource, context, and cost budgets;
- required output schema and cancellation authority.

A terminal result includes:

- the matching invocation and identity fields;
- actual runner, provider, model, adapter, and environment identities where available;
- timestamps, lifecycle state, termination confidence, and exit classification;
- structured output or a precise malformed-output error;
- bounded logs, artifacts, tool evidence, and usage references;
- unsupported, unavailable, denied, cancelled, timed-out, failed, and
  unknown-outcome states without collapsing them into success.

The invocation ID represents one intent across retries. Reusing it with different
inputs is an error. A duplicate with matching inputs returns the existing handle or
known state; it does not start another run. Timeouts preserve an unknown outcome for
reconciliation rather than creating a new invocation automatically.

## Capabilities

Capabilities have defined semantics and are either required by policy or optional.
The controller compares requirements with the adapter declaration before claiming
work. A missing required capability stops the run. Optional capability absence may
select an approved path, but never a fabricated equivalent.

Successful startup does not prove model identity, isolation, structured output,
cancellation, or tool restrictions. Each claimed capability needs conformance
evidence for the adapter, runner version, and operating environment.

## Author deliverables

An adapter contribution must include:

- the adapter implementation and capability manifest;
- setup, authentication, version, and supported-environment documentation;
- mappings for invocation, output, lifecycle, cancellation, and every error state;
- deterministic fake-runner tests;
- shared conformance results;
- known limitations and unsupported combinations;
- compatibility and migration notes when the contract or runner changes.

## Acceptance test

The extensibility bar is:

> A developer unfamiliar with the controller can implement an adapter from the
> public contract, pass conformance, and use it without runner-specific core changes.

The conformance kit must test successful work, capability mismatch, malformed and
late output, identity mismatch, timeout, cancellation, descendants, unavailable
runner, duplicate completion, and unknown outcome. A reference adapter demonstrates
structure; it is not the only permitted implementation.

## Trust

Adapters are executable integration code. Conformance proves contract behavior; it
does not prove an adapter is non-malicious.

Initially, adapters are reviewed and trusted components. Arbitrary third-party
adapters must not receive control-plane credentials or privileges merely because
they pass conformance. Supporting untrusted adapters requires a separately designed
process, permission, signing, installation, and isolation boundary.

## Versioning

Every invocation names the adapter contract version. Adapters reject unsupported
versions before execution. Compatible additions use capability discovery; breaking
semantic changes require a new contract version and migration evidence.
