# Design review and documentation outcome

Date: 2026-10-11.
Scope: architecture accuracy, viability, usefulness, safety and modern agent practice.
Status: findings addressed in the design; runtime proof remains outstanding.

## Assessment

The direction is viable. Its value depends on reliable, verifiable delivery, not
agent count. Plugin entry points can remain small while enforced execution controls,
trusted records and durable recovery provide the required safeguards.

The review used two independent fresh-context agent reviews and primary-source
research. No additional cross-model review was performed. Findings were reconciled
against the existing setup guide so already-agreed safeguards were not mistaken for
missing requirements.

## Findings and changes

| Finding | Documented resolution |
|---|---|
| Role prompts do not enforce test ownership or contain generated code. | [Execution](../execution.md) defines process, filesystem, tool, credential and network boundaries plus required adversarial proof. |
| Legacy report headers conflict with richer evidence requirements. | [One record contract](../communication-protocol.md) replaces the old header and binds reports to controller-issued invocations and input identities. |
| Concurrent resume and late owners can duplicate work. | [Recovery](../checkpoints.md) requires atomic ownership, generations, explicit takeover and rejection of stale actions/results. |
| Checkpoint/audit ordering and uncertain external effects are underspecified. | Recovery now requires durable intent, protected artifacts, outcome events, audit-bound checkpoints and reconciliation before retry. |
| Approvals can outlive the proposal they authorized. | Approvals bind exact content, scope and dependencies; changed inputs expire authority without erasing history. |
| Immutability can be mistaken for truth or administrator resistance. | [Audit](../audit.md) separates provenance, integrity, retention and privileged access; no administrator-resistant guarantee is claimed. |
| Separate test authorship does not establish test quality. | [Verification](../verification.md) adds acceptance mapping, meaningful red, inventory checks and selective property/mutation/fuzz techniques. |
| Desktop support needs more than unit-test success. | Verification profiles identify OS/toolchain/runtime, GUI/hardware and packaging requirements and block unavailable required lanes. |
| Factory usefulness and learned guidance are not measured. | [Evaluation](../evaluation.md) defines repeated trials, simpler baselines, failure injection and outcomes; [learning](../learning.md) tracks evidence, approval, use and retirement. |
| Engram capabilities cannot be assumed stable or equivalent to ours. | Learning and retrieval require pinned versions, conformance checks, approval filtering and controlled automatic injection. |
| The diagram makes human guidance approval appear future-only. | [Architecture](../architecture.md) makes approval initial, adds protected execution/evidence and separates issue from repository/PR operations. |
| Multiple document locations encourage policy drift. | The repository owns the design, setup guide and build tasks; old conversation-workspace drafts now point here. |

The overview, delivery workflow and recovery sequence are separate diagrams. Future
convention analysis, Jira and local runners remain visibly distinct. No second real
memory backend, mandatory vector database or microservice architecture was added.

## Remaining decisions and proof

- Runtime language and concrete schemas/validators.
- Supported host/OS matrix, isolation mechanism and adapter conformance evidence.
- Storage engine, locking implementation, privileged-access model and retention defaults.
- Actual project profiles, policy defaults, resource budgets and merge configuration.
- Pinned host/Engram versions and verified deployment instructions.
- Factory evaluation thresholds and trials on the planned test projects.

These are explicit implementation choices and validation work, not completed
capabilities. The next feasibility priority is the execution boundary. Do not claim
state-of-the-art results without relevant reproducible comparisons.

## Documentation validation

- Local Markdown links and fenced blocks checked.
- Git whitespace checks applied to publication content.
- Architecture, workflow and recovery diagrams rendered during the design update.
- Publication content checked for obvious credential patterns and machine-local paths.
- No runtime tests run: the repository has no factory implementation or test runner.

These checks validate the documentation package, not sandbox strength, crash safety,
model quality or application correctness. External documentation links may change.

## Primary references used in the review

- [Anthropic: separating orchestration, execution and durable sessions](https://www.anthropic.com/engineering/managed-agents).
- [Anthropic: agent evaluation methods](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
- [AWS: idempotency and retries](https://docs.aws.amazon.com/durable-execution/patterns/best-practices/idempotency/).
- [PostgreSQL: privileges and owner powers](https://www.postgresql.org/docs/current/ddl-priv.html).
- [OWASP: prompt injection and limits of RAG](https://genai.owasp.org/llmrisk/llm01-prompt-injection/).
- [Engram: current backend capabilities](https://github.com/thebtf/engram).
