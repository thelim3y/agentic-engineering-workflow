# Isolation capability status

Status: shell and build conformance evidence only. The production boundary is not
approved.

Named tools below identify measured adapters. They are not product dependencies or
an exhaustive support list.

## Current evidence

The prior Linux run is preserved in
[tests/isolation/results/linux-2026-10-12](../../tests/isolation/results/linux-2026-10-12/README.md).
It predates the issue 9 harness-integrity repairs and is historical evidence, not
current commissioning evidence. The adapters require a fresh run.

| Boundary | Result | Proven scope |
|---|---|---|
| bubblewrap 0.9.0 | Historical 22/22; revalidation required | Earlier shell/build harness |
| Codex CLI 0.156.1 sandbox | Historical 22/22; revalidation required | Earlier shell/build harness |
| Claude Code sandbox | Not run | None on the current host |
| Codex agent session | Not run | Native editing, MCP, model identity, and structured output unproven |
| Claude Code agent session | Not run | Native editing, MCP, model identity, and structured output unproven |

The suite checks disabled, enabled, and positive controls. It covers direct and
indirect writes, subprocesses, credentials, fixed-destination HTTPS reachability,
cancellation, result spoofing, hidden-test reads, unsupported policy, exit
propagation, and real CMake configure-time code. These are fixture-specific claims,
not proof of general filesystem or network containment.

## Limits

- The outer wrapper is a safety envelope for reviewed fixtures, not a production
  sandbox for arbitrary generated code.
- Retained network permits the fixed HTTPS control and does not isolate host TCP
  services.
- Shell boundaries do not prove protection from native host file tools or MCP.
- The files are reproducible evidence, not immutable audit storage.
- Full controller state, late-result rejection, mediated mixed-file edits, caches,
  PR actions, and merge gates remain unproven.

## Decision

Do not select a production execution boundary yet. Complete:

- fresh evidence from the repaired harness in
  [issue 9](https://github.com/thelim3y/agentic-engineering-workflow/issues/9);
- [Claude Code session proof](https://github.com/thelim3y/agentic-engineering-workflow/issues/10);
- [Codex session proof](https://github.com/thelim3y/agentic-engineering-workflow/issues/11).

Prompt restrictions, hooks, patch filtering, and hashes are supporting controls,
not substitutes for enforcement.
