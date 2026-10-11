# Software factory design

Status: agreed direction and required contracts; runtime not implemented or proven.
This is a public, local-friendly, model-agnostic workflow, initially entered through
Claude Code or Codex. A plugin is its entry point, not its security boundary.

## Read by topic

| Document | Owns |
|---|---|
| [Architecture](architecture.md) | Components, trust boundaries, current versus future scope. |
| [Workflow](workflow.md) | Stage order, role handoffs, issue state, completion. |
| [Planner](planner.md) | Task clarity, plan, size assessment and escalation. |
| [Interfaces](interfaces.md) | Product-owned adapter responsibilities and capabilities. |
| [Communication protocol](communication-protocol.md) | Invocation, agent report, execution evidence and approval records. |
| [Execution boundary](execution.md) | Permissions, isolated workspaces, credentials and enforcement proof. |
| [Checkpoints](checkpoints.md) | Ownership, crash ordering, retries and resume. |
| [Audit](audit.md) | Immutable history, evidence retention and limits of the guarantee. |
| [Verification](verification.md) | Test quality, red/green gates and native application profiles. |
| [Evaluation](evaluation.md) | Measuring the factory, regression cases and release evidence. |
| [Retrieval](retrieval.md) | Scoped, versioned supporting context. |
| [Learning](learning.md) | Human-approved lessons and future convention analysis. |
| [Configuration](configuration.md) | Precedence, validation, configurable policy and fixed invariants. |
| [Setup guide](setup-guide.md) | Onboarding and the C++ tooling shortlist. |
| [Build plan](build-plan.md) | Incremental delivery order and feasibility gates. |
| [Implementation tasks](implementation-tasks.md) | Unimplemented work and required checks. |
| [Decision record](decisions/0001-trusted-workflow-boundaries.md) | Why trusted control is separate from agent reasoning. |
| [Design review](reviews/2026-10-11-design-review.md) | Findings, documented resolutions, checks and remaining decisions. |

## Authority and scope

Each contract has one owner in the table. Guides, examples and diagrams summarize
those contracts; they do not redefine them. Report conflicts rather than guessing.
These documents supersede the earlier conversation-workspace design drafts.

Records use one versioned product contract. Its required semantics are specified;
machine-readable schemas and runtime language remain implementation work. No example
configuration or record is evidence that a parser or adapter already exists.

C++ is the first validation target; .NET/C# follows. Python remains a candidate.
Additional languages use project verification profiles, not changes to core roles.
GitHub is initial; Jira and local-model runners are future integrations. Engram is
the only selected real memory backend. Fake adapters are for tests only.

## Boundaries on this design

Single-purpose roles do not require separate services or an LLM call for every step.
Use deterministic tools for mechanical checks. Keep the initial controller small.
Do not add a second memory backend, mandatory vector database, or microservices
without a demonstrated need. Future boxes are not first-release requirements.

All user-facing output must be as concise as possible while preserving necessary
facts, evidence, limitations and required actions. A green run means its configured
checks passed, not that the application has no defects.
