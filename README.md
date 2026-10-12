# Agentic Engineering Workflow

A configurable, model-agnostic software factory for native applications. It covers
planning, TDD, implementation, independent testing, review, PR creation, and gated
merge.

**Status:** design and feasibility stage. The contracts and isolation spike exist;
the factory does not.

## Start here

- [Design index](docs/README.md)
- [Architecture](docs/architecture.md)
- [Workflow](docs/workflow.md)
- [Build plan](docs/build-plan.md)
- [Setup guide](docs/setup-guide.md)
- [GitHub backlog](https://github.com/thelim3y/agentic-engineering-workflow/issues)

## Direction

Start manually from Claude Code or Codex with a labelled GitHub issue. One issue
targets one reviewable PR. Oversized or concerning work requires human approval.

TDD owns every test-related input. Implementation cannot change it. Deterministic
controls validate evidence, transitions, approvals, recovery, and completion.

C++ is the first validation target; .NET/C# follows. Engram is the selected memory
backend. Jira, local-model runners, and convention analysis remain later work.

## Contributing

Read [AGENTS.md](AGENTS.md) and the relevant owning contracts before changing the
project. Claims about runtime support or safety require reproducible evidence.
