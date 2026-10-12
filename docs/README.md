# Software factory design

Status: agreed contracts; runtime not implemented. The factory is public,
local-friendly, and independent of any LLM, provider, model, or agent host.
Plugins and other host integrations are entry points, not security boundaries.

## Developing this project

Follow [Development rules](development-rules.md). [AGENTS.md](../AGENTS.md) is the
shared agent entry point. Planned work lives in
[GitHub Issues](https://github.com/thelim3y/agentic-engineering-workflow/issues).

## Contract index

| Document | Owns |
|---|---|
| [Architecture](architecture.md) | Components, trust boundaries, and scope. |
| [Workflow](workflow.md) | Stage order, handoffs, issue state, and completion. |
| [Planner](planner.md) | Clarity, planning, size, risk, and escalation. |
| [Interfaces](interfaces.md) | Product-owned adapter contracts and capabilities. |
| [Communication](communication-protocol.md) | Invocation, report, evidence, and approval records. |
| [Execution](execution.md) | Permissions, workspaces, credentials, and enforcement. |
| [Checkpoints](checkpoints.md) | Ownership, effects, retries, and recovery. |
| [Audit](audit.md) | Immutable history, artifacts, retention, and limits. |
| [Verification](verification.md) | Test quality, gates, and native profiles. |
| [Evaluation](evaluation.md) | Trials, metrics, regressions, and release evidence. |
| [Retrieval](retrieval.md) | Scoped and versioned supporting context. |
| [Learning](learning.md) | Human-approved lessons and task feedback. |
| [Configuration](configuration.md) | Precedence, policy, validation, and invariants. |
| [Setup](setup-guide.md) | Host onboarding and C++ tool selection. |
| [Build plan](build-plan.md) | Delivery order and feasibility gates. |
| [ADR-0001](decisions/0001-trusted-workflow-boundaries.md) | Why trusted control is separate from agents. |
| [ADR-0002](decisions/0002-runner-independent-core.md) | Why the core is independent of runners, providers, and models. |

## Authority and scope

Each topic has one owner above. Other documents summarize; they do not redefine.
Records use one versioned product contract. Schemas and runtime language remain
implementation work.

C++ is first; .NET/C# follows. Python remains a candidate. GitHub is initial;
Jira and local models are later. Engram is the only selected real memory backend.

Single-purpose roles do not require separate services or LLM calls for mechanical
steps. Do not add a second memory backend, mandatory vector database, generic
plugin marketplace, or microservices without evidence.

User-facing output must be as concise as possible without hiding facts, evidence,
limitations, or required action. A green run means configured checks passed; it
does not prove the application has no defects.
