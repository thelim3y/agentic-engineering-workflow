# Reviewed learning and guidance

Status: required governance for reusable lessons; automatic convention analysis is future.

## Task-writing feedback

After a run, including failed or stopped runs, an optional reviewer examines the
original task and permitted audit evidence. It suggests concise improvements to
human task writing. This is informational, not a delivery gate or an automatic edit.

Include the disclaimer: observed difficulty may come from the model, tools,
environment or supplied context, not the task wording. Similar past failures do not
establish causation. Distinguish observations from suggestions and uncertainty.

## Reusable lessons

1. Propose a lesson with evidence, scope and expected benefit.
2. A human approves the exact wording and scope, rejects it or defers it.
3. Only approved, applicable versions may enter reusable agent guidance.
4. Record where the lesson was supplied and the observed outcome.
5. Review usefulness; retire stale, misleading or harmful guidance.

Store lesson/version identity, project and role scope, source run/evidence references,
applicability conditions, author, approval receipt, status and any superseded version.
Agents cannot approve their own proposals or silently edit approved wording.
Edits create a new candidate; previous approval does not transfer. Retirement removes
active use, including cached/indexed copies, without rewriting audit history.

Human approval establishes permission to use guidance, not its truth or usefulness.
Use [evaluations](evaluation.md) and human review to assess effects. Preserve negative
outcomes and conflicting evidence. Guidance cannot override task constraints,
permissions, verification policy or current source facts. Record and escalate conflicts.

## Future convention analysis

Use repository examples to suggest architecture and idiom guidance, not merely
formatting. Distinguish explicit rules from frequently observed practice and isolated
examples. Record source revision, sample scope, exceptions and uncertainty.
Absence of a pattern does not establish a ban. A habit may be accidental or outdated.

Convention analysis is another proposal source feeding the same human approval
boundary, not a new authority or an initial-release prerequisite. No self-modifying
workflow, autonomous policy changes or model weight training is implied by learning.

## Engram boundary

Engram stores permitted context and approved lessons through our adapter. Pin and
record tested server/client versions and enabled capabilities. Validate authentication,
project/role scope, approval filtering, retirement, freshness, cache fallback and
upgrade/migration behaviour before accepting a release. Backend rule arbitration
does not substitute for our human approval or workflow authorization.

Automatic host injection must obey the same approval and visibility rules as explicit
retrieval. Disable or isolate injection that cannot do so. Keep credentials and
authoritative state outside this shared context path. Use a fake adapter for tests;
no second real memory backend is required.

The [Engram README](https://github.com/thebtf/engram) describes evolving retrieval and
governance surfaces. Verify a pinned deployment rather than relying on its name or
assuming its semantics match ours.
