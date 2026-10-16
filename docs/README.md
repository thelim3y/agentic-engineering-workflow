# Software factory design

Status: design contracts and an implemented [file audit baseline](audit-v1.md);
the controller is not implemented. The factory is public,
local-friendly, and independent of any LLM, provider, model, or agent host.
Plugins and other host integrations are entry points, not security boundaries.

## Developing this project

Follow [Development rules](development-rules.md). [AGENTS.md](../AGENTS.md) is the
shared agent entry point. Planned work lives in
[GitHub Issues](https://github.com/thelim3y/agentic-engineering-workflow/issues).

## Contract index

| Document | Owns |
|---|---|
| [First goal](first-goal.md) | Initial product outcome, operating shape, and limits. |
| [Architecture](architecture.md) | Components, trust boundaries, and scope. |
| [Component maps](component-map.md) | Human-owned diagrams and source-linked explanations of a target codebase. |
| [Workflow](workflow.md) | Stage order, handoffs, issue state, and completion. |
| [Planning](planning.md) | Human plan ownership, challenge, size, risk, and decisions. |
| [Agent work rules](agent-work-rules.md) | Shared terms, ownership, scope, evidence, and handoffs. |
| [Interfaces](interfaces.md) | Product-owned adapter contracts and capabilities. |
| [Runner adapters](runner-adapters.md) | Public adapter responsibilities, lifecycle, conformance, and trust. |
| [Communication](communication-protocol.md) | Invocation, report, evidence, and approval records. |
| [Execution](execution.md) | Permissions, workspaces, credentials, and enforcement. |
| [Checkpoints](checkpoints.md) | Ownership, effects, retries, and recovery. |
| [Audit](audit.md) | Immutable history, artifacts, retention, and limits. |
| [File audit v1](audit-v1.md) | Implemented envelope/API, local persistence, recovery, usage and measured limits. |
| [Verification](verification.md) | Test quality, gates, and native profiles. |
| [Evaluation](evaluation.md) | Trials, metrics, regressions, and release evidence. |
| [Retrieval](retrieval.md) | Scoped and versioned supporting context. |
| [Learning](learning.md) | Human-approved lessons and task feedback. |
| [Configuration](configuration.md) | Precedence, policy, validation, and invariants. |
| [Standards](standards.md) | Relevant standards, claim boundaries, and alignment direction. |
| [Setup](setup-guide.md) | Host onboarding and C++ tool selection. |
| [Build plan](build-plan.md) | Delivery order and feasibility gates. |
| [ADR-0001](decisions/0001-trusted-workflow-boundaries.md) | Why trusted control is separate from agents. |
| [ADR-0002](decisions/0002-runner-independent-core.md) | Why the core is independent of runners, providers, and models. |
| [ADR-0003](decisions/0003-initial-runtime-boundary.md) | Initial controller runtime, platform, threat boundary, and safe policy. |

## Authority and scope

Each topic has one owner above. Other documents summarize; they do not redefine.
Records use one versioned product contract. The minimal audit envelope has a Python
implementation; full record schemas and controller integration remain separate work.
The initial runtime and support boundary are fixed by [ADR-0003](decisions/0003-initial-runtime-boundary.md).

These documents contain the current design. Unsettled proposals belong in issues
or explicitly proposed ADRs, not mixed into authoritative contract text.

C++ is the first application target; .NET/C# follows. Python application support
remains a candidate. The initial controller uses Python under ADR-0003. GitHub is
initial; Jira and local models are later. Engram is the only selected real memory
backend.

Single-purpose roles do not require separate services or LLM calls for mechanical
steps. Do not add a second memory backend, mandatory vector database, generic
plugin marketplace, or microservices without evidence.

User-facing output must be as concise as possible without hiding facts, evidence,
limitations, or required action. A green run means configured checks passed; it
does not prove the application has no defects.

## Review records

Historical reviews record findings and recommendations, not changes to the design
contracts. GitHub Issues remains the backlog.

- 12 October 2026: [adversarial review](reviews/2026-10-12-adversarial-review.md)
  and [detailed findings](reviews/2026-10-12-adversarial-findings.md).
