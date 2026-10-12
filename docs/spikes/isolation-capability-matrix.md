# Isolation capability status

Status: shell and build conformance evidence only. The production boundary is not
approved.

## Current evidence

The corrected Linux run is preserved in
[tests/isolation/results/linux-2026-10-12](../../tests/isolation/results/linux-2026-10-12/README.md).

| Boundary | Result | Proven scope |
|---|---|---|
| bubblewrap 0.9.0 | 22/22 pass | Shared shell/build fixtures |
| Codex CLI 0.156.1 sandbox | 22/22 pass | The same shell/build fixtures |
| Claude Code sandbox | Not run | None on the current host |
| Codex agent session | Not run | Native editing, MCP, model identity, and structured output unproven |
| Claude Code agent session | Not run | Native editing, MCP, model identity, and structured output unproven |

The suite checks disabled, enabled, and positive controls. It covers direct and
indirect writes, subprocesses, credentials, network policy, cancellation, result
spoofing, hidden-test reads, unsupported policy, exit propagation, and real CMake
configure-time code.

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

- [harness integrity repairs](https://github.com/thelim3y/agentic-engineering-workflow/issues/9);
- [Claude Code session proof](https://github.com/thelim3y/agentic-engineering-workflow/issues/10);
- [Codex session proof](https://github.com/thelim3y/agentic-engineering-workflow/issues/11).

Prompt restrictions, hooks, patch filtering, and hashes are supporting controls,
not substitutes for enforcement.
