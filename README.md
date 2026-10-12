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

Start manually through a configured agent runner with a labelled GitHub issue.
One issue targets one reviewable PR. Oversized or concerning work requires human
approval.

TDD owns every test-related input. Implementation cannot change it. Deterministic
controls validate evidence, transitions, approvals, recovery, and completion.

C++ is the first application target; .NET/C# follows. Engram is the selected memory
backend. Jira, local-model runners, and convention analysis remain later work.

The first controller implementation targets CPython 3.12 on a single Ubuntu 24.04
x86-64 host. This is an initial commissioning boundary, not a core dependency or a
claim of support for other Linux environments; see
[ADR-0003](docs/decisions/0003-initial-runtime-boundary.md).

The core contract is independent of any LLM, provider, model, or agent host. Named
runners in feasibility work are initial adapters, not architectural dependencies.

## Contributing

Read [AGENTS.md](AGENTS.md) and the relevant owning contracts before changing the
project. Claims about runtime support or safety require reproducible evidence.
