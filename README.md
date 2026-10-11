# Agentic Engineering Workflow

A configurable, model-agnostic software factory for native application development:
planning, TDD, implementation, independent testing, review, PR creation and gated merge.

**Status: design stage.** The repository contains contracts, diagrams, setup guidance
and an incremental build plan. There is no runnable factory, installation command
or proven isolation implementation yet.

## Start here

- [Design index](docs/README.md) — authoritative documents by topic.
- [Architecture](docs/architecture.md) — components and required trust boundaries.
- [Workflow](docs/workflow.md) — stage order and repair paths.
- [Review outcome](docs/reviews/2026-10-11-design-review.md) — findings, changes and remaining decisions.
- [Build plan](docs/build-plan.md) and [implementation tasks](docs/implementation-tasks.md).
- [Setup guide](docs/setup-guide.md) — onboarding and C++ verification tools.

## Direction

Start manually from Claude Code or Codex using an eligible GitHub issue. Keep one
task aimed at one reviewable PR, with human approval for oversized or concerning
work. TDD owns tests; implementation cannot modify them. Deterministic controls
validate evidence and govern progression, approvals and recovery.

C++ is the first validation target; .NET/C# follows. Engram is the selected memory
backend, while reusable lessons require human approval. The design is local-friendly,
not local-only. Jira, local-model runners and convention analysis are future work.

## Working on the design

Read the owning topic contract before changing a requirement. Keep diagrams and
cross-links aligned, record important decisions, and distinguish required behaviour
from tested implementation. Preserve the legacy project as reference material.
Runtime support and safety claims require evidence from the planned test projects.
