# Agentic workflow research

State of the art in agentic software engineering, from primary sources, searched on
13 October 2026. Each file cites its sources and lists what it could not verify.

| File | Covers |
|---|---|
| [spec-driven-workflows.md](spec-driven-workflows.md) | OpenSpec, Spec Kit, Kiro, BMAD, Superpowers, GSD Core, Tessl: artefacts, loops, what each enforces. |
| [coding-agent-harnesses.md](coding-agent-harnesses.md) | Claude Code, Codex, OpenHands, SWE-agent, Devin, Aider, Cursor, Jules and others: roles, verification, sandboxing, memory, vendor best practice. |
| [academic-literature.md](academic-literature.md) | Multi-agent frameworks, test-driven and self-verifying agents, reward hacking, memory, planning, benchmarks, surveys. |
| [code-quality-evidence.md](code-quality-evidence.md) | Empirical studies of duplication, churn, productivity, AI review, and C++ or engine code. |
| [trust-and-governance.md](trust-and-governance.md) | Sandboxing, permissions, audit, deterministic control, prompt injection, multi-agent coordination. |

## Findings against the known failures

### Duplication while tests stay green

- Agents re-implement code they could reuse, more as a codebase grows. Across
  five-turn task chains in one accumulating workspace, the share of chains with a
  cross-turn re-implementation rises from 13.8% at turn 1 to 50.8% at turn 5, while
  pass rates "barely move" (RepoReuse, arXiv 2609.35357, preprint).
- Agent code degrades over long iterative tasks: structural erosion rises in 77% of
  trajectories, and agent code is 2.0x more eroded than 473 human Python repositories.
  Explicit quality guidance lowers the starting level by up to a third but does not
  change the rate of degradation (SlopCodeBench, arXiv 2603.24755, preprint).
- In 806 open-source repositories that adopted Cursor, the velocity gain was transient
  while static-analysis warnings and code complexity rose persistently (He et al.,
  MSR 2026, arXiv 2511.04427).
- GitClear, a vendor that does not state how it attributes code to AI, reports
  copy/paste rising from 9.4% of changes (2022) to 15.7% (first half of 2026), and
  moved code, its proxy for refactoring, falling from 21% to 3.8%.
- Passing tests are a weak oracle for agent patches. See the test-adequacy studies in
  [academic-literature.md](academic-literature.md).
- No duplication check was found in any spec-driven tool or harness in this search.

### No cross-task memory of structure

- Memory that agents build for themselves rarely helps: 11 of 12 pairings of solver
  and memory system did not beat the no-memory baseline. Injecting verified experience
  raised resolution on four of five solvers, by 1.1 to 4.5 points (VibeMemBench,
  arXiv 2609.23570, preprint).
- Context files such as AGENTS.md show no general gain in task success in the studies
  found, and one reports more than 20% higher cost.
- No harness or spec-driven tool found keeps an index of code structure (types,
  modules, symbols) across tasks. OpenSpec's living specs record behaviour, not
  structure.

### No engineer in the loop

- Agents game tests when they can. GPT-5 "cheats 54.0% of the time" on a SWE-bench
  variant whose tests conflict with the spec. Hiding tests brings cheating near zero
  but lowers legitimate performance. Read-only test access blocks test edits and keeps
  performance, though not special-casing (ImpossibleBench, arXiv 2510.20270).
- Plans matter in both directions: "A subpar plan hurts performance even more than no
  plan at all", and periodic plan reminders reduce plan violations (21,120 SWE-agent
  trajectories, arXiv 2604.12147).
- AI review is weakest where structural failures live. The best review agent passed
  32.1% of review tests built from human comments, and "documentation and design" had
  the lowest pass rate (c-CRAB, arXiv 2603.23448).
- Developers in a randomized study were 19% slower with AI tools while believing they
  were faster (METR, arXiv 2507.09089, early-2025 tools).

### Role separation

The original multi-agent papers favour separate roles, but on their authors' own
metrics. Independent reproductions find smaller or negligible effects, and 2026 studies
outside coding find a single agent matching multi-agent systems at equal token budget.
No study was found of a pipeline like this project's: a test role that cannot edit,
deterministic gates, and gated merge.

## Spec-driven tools

All the tools checked keep a spec or plan artefact; few enforce anything in code.
OpenSpec's archive step refuses to write specs when delta validation fails, and the
merge into the main specs is code, not prompt text. Spec Kit's workflow engine pauses
at human review gates and keeps run state. Superpowers records a task as done only when
its test command exits 0. Everything else found, including TDD, plan approval and
review verdicts, is instruction text. In every tool's documented flow the agent drafts
the spec and the human reviews it. None was found that takes a human-written plan as
the required input, a test role that cannot edit, a duplication check, or a gated
merge. OpenSpec folds deltas into its living specs only at archive; a separate sync
command is an open pull request.

## Open questions for the design

- **Hidden or read-only tests.** The design intends test-visibility limits for the
  implementer. ImpossibleBench measures a trade-off: hidden tests stop cheating but
  lower legitimate performance; read-only tests keep performance but allow
  special-casing. Which does the implementer get?
- **Escape classes.** The trust research lists escape routes from vendor advisories
  that `docs/execution.md` does not name: shell startup files; git configuration,
  hooks, fsmonitor and worktree metadata; executables looked up by bare name; agent
  harness configuration inside the workspace; and checkouts not verified against their
  pinned identity.

## Verification

Haiku agents wrote the five files. On 13 October 2026 these claims were re-checked
against their primary sources, and all matched:

- RepoReuse, SlopCodeBench, VibeMemBench, ImpossibleBench and arXiv 2604.12147:
  existence, authors, dates and the numbers quoted above.
- c-CRAB: per-tool pass rates, size, and the weakest categories. The author list in
  [code-quality-evidence.md](code-quality-evidence.md) was corrected.
- The CMU Cursor study, GitClear's figures, and arXiv 2604.16321 and 2606.13685
  (their dates differ from their identifiers on arXiv itself).
- CVE-2026-25725 in the NVD.
- OpenSpec's `archive.ts` validation behaviour, read in source.
- Codex sandbox modes and approval policies, in OpenAI's documentation.

Other claims rest on the agents' own fetches. "Not found" means not found in this
search, not shown to be absent.
