# Build plan

Status: planned work is tracked in
[GitHub Issues](https://github.com/thelim3y/agentic-engineering-workflow/issues).
The contracts in the [design index](README.md) own requirements.

## Delivery order

1. [Prove trustworthy agent execution](https://github.com/thelim3y/agentic-engineering-workflow/issues/2):
   settle the product boundary, repair the conformance harness, and prove Claude
   Code and Codex sessions.
2. [Build the trusted controller](https://github.com/thelim3y/agentic-engineering-workflow/issues/3):
   records, audit, recovery, configuration, host plugins, GitHub intake, and planning.
3. [Deliver the protected C++ workflow](https://github.com/thelim3y/agentic-engineering-workflow/issues/4):
   TDD, implementation, independent testing, bounded repair, presets, and Clang.
4. [Add bounded context and learning](https://github.com/thelim3y/agentic-engineering-workflow/issues/5):
   Engram, approved lessons, and post-run task feedback.
5. [Deliver the GitHub PR lifecycle](https://github.com/thelim3y/agentic-engineering-workflow/issues/6):
   draft, review, repair, ready, gated merge, recovery, and completion.
6. [Evaluate and extend](https://github.com/thelim3y/agentic-engineering-workflow/issues/7):
   compare with a simpler baseline before adding later targets.

## Checkpoints

- **Execution:** both hosts satisfy the same declared contract. A human selects
  the production boundary.
- **Local workflow:** one C++ task completes red, green, repair, and native checks
  without PR publication.
- **Context:** Engram cannot disclose protected inputs or override gates.
- **Commissioning:** a designated scratch repository completes the PR lifecycle
  without duplicate or false-success actions.
- **Release:** repeated trials meet thresholds agreed before evaluation.

Stop at a failed checkpoint. Do not replace missing enforcement with prompts.

## Working arrangement

- Build here; keep the legacy repository read-only.
- One issue targets one focused PR. Split our development work when needed.
- Reuse legacy ideas or code only after review and testing.
- Keep authoritative state and evidence outside agent-writable memory.
- Treat failing, unavailable, skipped, stale, and not-run checks as distinct states.
- Do not use the unfinished factory to approve its own security-sensitive changes.
