# ADR-0001: Keep workflow authority outside agent execution

Status: accepted design; implementation and enforcement proof pending.
Date: 2026-10-11.

## Context

The factory must preserve test ownership, meaningful verification, human approvals
and immutable history while executing agent-written code. Model instructions and
well-formed reports cannot enforce those guarantees. Memory may contain incorrect
or malicious text. Crashes can occur after external effects but before receipt storage.

## Decision

Use a deterministic controller with product-owned contracts. Separate its authority
and durable records from untrusted agent/generated-code execution. Agents propose;
controlled tools collect evidence; the controller validates and advances gates.
Human decisions bind exact proposals. Memory and retrieval provide context, not authority.

Initial immutability enforcement must resist agents and their execution tools.
Administrator resistance is not claimed; privileged access and retention must be
declared before release. Storage engines, isolation technology, runtime language
and OS support remain open and require separate decisions and proof.

## Alternatives

- Prompt-only restrictions: insufficient against shell/subprocess actions.
- Agent-written reports as gate authority: allows stale or fabricated success.
- Shared memory as workflow state: confuses contextual recall with authorization.
- One service per role: adds deployment costs without establishing stronger isolation.

## Consequences

The plugin remains the user-facing entry point. A small controller can own multiple
logical contracts; no distributed-service architecture is required. Each host must
pass the same enforcement and recovery tests. Unsupported configurations fail closed.
More capable models do not remove these authority boundaries.

The contract is specified in [execution](../execution.md),
[records](../communication-protocol.md), [recovery](../checkpoints.md) and
[audit](../audit.md). Related current practice separates execution, orchestration and
durable sessions: [Anthropic architecture](https://www.anthropic.com/engineering/managed-agents).
