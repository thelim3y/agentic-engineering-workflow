# ADR-0003: Use a single-host Python controller on Linux first

Status: accepted design; implementation and commissioning evidence pending.
Date: 2026-10-12.

## Context

The first implementation needs an explicit controller runtime, deployment boundary,
platform target and safe policy baseline. Leaving those choices open prevents the
execution and recovery contracts from becoming testable. The choices must keep the
core independent of agent runners, providers and models and must not imply support
beyond measured environments.

The existing feasibility harness is Python on Linux. Its evidence covers bounded
shell and build fixtures only; it does not approve a production execution boundary.

## Decision

### Initial product shape

- Implement the deterministic controller in CPython 3.12.
- Support one local deployment, one operator and one Linux host first.
- Use Ubuntu 24.04 LTS on x86-64 as the commissioning environment. Other Linux
  distributions, architectures, macOS and Windows are unsupported until separately
  commissioned.
- Keep the controller, state, audit, artifacts, credentials and mutation dispatch
  outside agent and generated-code authority.
- Treat reviewed adapters and execution providers as trusted product components.
  Treat agent sessions, repository content, retrieved text, generated code, builds,
  tests and their subprocesses as untrusted.
- Resolve runner, provider and model independently per role. One run may therefore
  use several conforming runner adapters.

Python is an implementation choice, not part of the public record or adapter
contract. Product-owned schemas and conformance behavior remain language-neutral.

### Initial support boundary

The first release supports local single-host ownership only. Multiple controller
processes on that host must still be fenced by durable ownership and owner
generations. Shared state across hosts, multi-user operation, remote controller
services, high availability and administrator-resistant storage are unsupported.
Configuration requesting them fails before work starts.

The initial Linux execution provider must enforce filesystem, process, credential,
tool and network restrictions with operating-system controls. The controller depends
on declared capabilities, not a named sandbox implementation. No provider becomes
supported until issues #9, #10 and #11 supply current conformance evidence and the
execution checkpoint is accepted.

Root, the host administrator and anyone able to replace the controller or its trusted
storage are outside the initial adversary model. Agents, their tools, generated code
and ordinary repository content are inside it. The file audit provider must detect
their attempts to alter accepted history within this boundary; it does not claim to
resist a privileged host rollback.

### Safe policy baseline

Initial built-in policy is:

| Area | Baseline |
|---|---|
| Start and selection | Manual start; one configured eligible issue. |
| Concurrency | One active run per local deployment; stages and roles execute sequentially. |
| Role selection | Shared runner/provider/model defaults may be overridden per role; no automatic substitution. |
| Implementation tests | Test-related inputs are unreadable and unwritable by implementation. Only controller-approved diagnostic feedback crosses the boundary. |
| Untrusted network | Denied unless an exact operation and destination are allowed by policy and supported by the execution provider. |
| Credentials | No mutation, model, SSH-agent or storage-administration credential enters agent or generated-code execution. |
| Audit | Required file provider; unsupported signing or encryption settings fail validation. |
| External mutation | Denied unless the target, payload, current owner, eligibility, evidence and required approval are validated at dispatch. |
| Publication | Draft PR only after current configured evidence; repository and base branch must be explicitly configured. |
| Merge | Disabled until separately enabled by explicit configuration and the commissioning gate has passed. |
| Missing choices | Unknown keys, absent required values and unsupported capabilities fail before issue ownership is acquired. |

Task text, repository content, retrieved context and agent output cannot change this
policy. A later accepted decision may widen the boundary only with corresponding
enforcement and commissioning evidence.

## Configuration authority

Configuration resolves in this order:

1. Built-in safe policy.
2. Local deployment configuration.
3. Repository configuration.
4. Explicit run overrides.

Within each layer, role-specific values override shared values. Later layers may
change flexible settings but cannot weaken fixed invariants. Machine paths, credential
references and host execution settings are accepted only from local deployment
configuration; committed repository settings and run overrides cannot supply them.
The controller records sanitized effective values and their origins.

## Alternatives

- **Keep the runtime and platform open:** rejected because enforcement, packaging and
  recovery cannot be implemented or commissioned against an unspecified host.
- **Build the controller in C++:** rejected for the first slice because it adds
  systems-level implementation cost without improving the trust boundary. C++ remains
  the first application target.
- **Start with a remote or multi-host controller:** rejected because distributed
  identity, storage and fencing do not earn their cost for the solo-developer goal.
- **Make a named runner or sandbox the product boundary:** rejected because runner
  independence and capability-based conformance are binding invariants.

## Consequences

The first implementation can use the existing Python feasibility work and target one
measured host without claiming general Linux or enterprise support. Packaging must pin
the supported Python and dependency versions. Later controller languages or platforms
may replace this implementation behind the same contracts, but each combination needs
its own migration and commissioning evidence.

The initial simplicity is deliberate: unsupported multi-host and multi-user requests
fail clearly rather than being approximated with process-local locks or shared files.
