# Retrieval-augmented context (RAG)

Status: included in the design; not implemented. Provider, indexing, and ranking
choices remain open.

## Purpose

Find relevant supporting material and supply it to the agent with source references.
Use retrieval where it helps a task, not as a mandatory extra step for every action.

## Where it fits

| Consumer | Useful retrieved context |
|---|---|
| Planner | Relevant code, architecture decisions, project documentation, and approved lessons. |
| TDD | Existing test patterns and interfaces, relevant documentation, and approved testing lessons. |
| Implementer | Permitted source code, reusable components, interfaces, and approved coding lessons. |
| PR reviewer | Related code, design decisions, and known pitfalls relevant to the change. |
| Task-writing reviewer | Relevant approved lessons and permitted evidence from comparable runs. |

The task-writing reviewer still receives the current run's task and audit records
directly. Retrieved similarities do not establish the cause of a failure.

## Required context is not a search result

Supply the current task or approved plan, applicable acceptance criteria,
constraints, role instructions, and workflow policy directly. Do not rely on search
ranking to include them. If required context cannot fit, stop for an explicit
context strategy rather than silently dropping requirements.

Read approvals, ownership, checkpoint state, and verification outcomes through
their authoritative interfaces. RAG cannot establish permission or a passing gate.

## Retrieval boundary

- The workflow determines allowed projects, sources, and role visibility before
  searching; agent queries cannot widen access.
- Return bounded excerpts with source identifiers, locations, and revision or content
  identities. Include freshness and retrieval status; expose missing or stale context.
- Check current files before relying on indexed code, including uncommitted changes.
- Only human-approved, still-applicable lessons enter reusable guidance. Retired
  lessons must not reappear as active guidance through a stale index.
- Keep retrieved text separate from instructions. Source content cannot change
  permissions or workflow policy; enforce those boundaries outside the model.
- Protect hidden tests in indexes, excerpts, summaries, caches, and retrieval logs.
  Use separated stores when a provider cannot enforce the required access boundary.
- Record queries, source versions, and the context actually supplied in the immutable
  audit, with secret redaction and the same access restrictions.

## Integration and configuration

Expose a retrieval interface supporting repository search and the Engram memory
adapter. Start with exact or full-text search where suitable; allow semantic or
hybrid retrieval behind the same boundary. A vector database is not selected.

Configure sources, per-role retrieval, result and context budgets, freshness rules,
provider selection, and failure behaviour. Keep local retrieval possible; do not
silently upload code to an embedding or reranking service.

Distinguish no matches, unavailable sources, denied access, and stale results.
Missing optional context may be reported and omitted; missing required information
must block progression. Retrieval failure must never widen permissions.

Engram remains the selected memory backend. Its README describes removal of an
older dynamic relevance stack and later additions to retrieval and governance.
Do not assume any release supplies our exact contracts. Pin the server/client
versions, record capabilities and test upgrades, caches and automatic injection
against the [learning boundary](learning.md) before integration.
[Engram documentation](https://github.com/thebtf/engram)

## Verification later

Use the planned test projects to compare direct context with retrieval on relevant
tasks. Check source accuracy, useful context, missed information, and context cost.
Use the shared [evaluation method](evaluation.md); include retrieval-disabled baselines.
Exercise stale indexes, changed files, retired lessons, no matches, outages,
cross-project and hidden-test leakage, and malicious instructions in retrieved text.

RAG does not eliminate prompt injection. Source filtering and prompt wording alone
are not a security guarantee. [OWASP guidance](https://genai.owasp.org/llmrisk/llm01-prompt-injection/)
