# ADR-0002: Keep the core independent of agent runners and models

Status: accepted design; adapter conformance pending.
Date: 2026-10-11.

## Context

Initial feasibility work uses two available agent hosts. If their commands, data
types, or limitations enter the controller, the factory becomes tied to those hosts
despite being described as model-agnostic.

The product needs per-role runner, provider, and model selection. Future adapters
may use CLIs, desktop hosts, local runtimes, hosted services, or APIs.

## Decision

The core depends only on product-owned runner contracts and declared capabilities.
It contains no named-runner branches, provider SDK types, or CLI assumptions.

Each adapter translates invocation, identity, permissions, lifecycle, cancellation,
structured output, and errors into that contract. Configuration selects the adapter,
provider, and model per role. Unsupported combinations fail before work starts;
silent model or runner substitution is forbidden.

Every adapter/version/OS combination must pass shared conformance tests. The first
two adapters are validation implementations, not part of the product definition.

## Alternatives

- Build around one agent CLI and abstract it later: rejected because host behavior
  would leak into records, policy, and recovery.
- Use only common-denominator features: rejected because it hides useful capabilities
  and still does not prove equivalent behavior.
- Expose provider payloads to the workflow: rejected because providers would control
  the internal model and make migration unsafe.

## Consequences

Runner independence does not mean universal compatibility. Support is claimed only
for adapters with current evidence. Provider-specific behavior stays in adapters,
capability records, and conformance reports.

Early validation uses at least two independent adapters to expose accidental
coupling. Adding another runner should require an adapter and evidence, not changes
to workflow policy.
