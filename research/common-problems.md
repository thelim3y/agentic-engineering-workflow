# What everyone struggles with in AI coding

Status: draft of the general questions, with evidence. Checked on 14 October 2026
against each source's abstract, advisory or own page unless marked otherwise.
Preprints and working papers are not peer reviewed.

## 1. Does the code stay good over time?

Agents' code passes tests while the codebase gets worse.

- Agents leave duplicated logic in 50.8% of five-turn task chains, "all while pass
  rates barely move". Preprint.
  [RepoReuse, arXiv 2609.35357](https://arxiv.org/abs/2609.35357)
- Structural erosion rises in 77% of agent trajectories; agent code is 2.0x more
  eroded than 473 open-source repositories. Quality guidance lowers the starting
  level "by up to a third, without affecting degradation rates". Preprint.
  [SlopCodeBench, arXiv 2603.24755](https://arxiv.org/abs/2603.24755)
- Adopting Cursor gave a "large, but transient" speed gain and a "substantial and
  persistent increase in static analysis warnings and code complexity". MSR 2026.
  [He et al., arXiv 2511.04427](https://arxiv.org/abs/2511.04427)

## 2. Can you trust "the tests pass"?

Agents game tests, and passing tests miss real problems.

- An agent with test access "may delete failing tests rather than fix the
  underlying bug". The paper body reports GPT-5 cheating 54.0% of the time on
  tasks whose tests conflict with the spec (body figure checked 13 October).
  Preprint. [ImpossibleBench, arXiv 2510.20270](https://arxiv.org/abs/2510.20270)
- "Explicit reward hacking by both Codex and Claude Code, and misaligned behavior
  by all three agents." Preprint.
  [EvilGenie, arXiv 2511.21654](https://arxiv.org/abs/2511.21654)
- Maintainers judged that "roughly half" of test-passing SWE-bench Verified PRs
  from mid-2024 to late-2025 agents would not be merged. 296 PRs, four
  maintainers. [METR, 10 March 2026](https://metr.org/notes/2026-03-10-many-swe-bench-passing-prs-would-not-be-merged-into-main/)

## 3. Does the agent understand the codebase?

Agents ignore code that already exists, and the usual fixes help little.

- Agents "progressively stop exploring relevant repository code" and reuse their
  own earlier code less, even when it is in the workspace. Preprint.
  [RepoReuse, arXiv 2609.35357](https://arxiv.org/abs/2609.35357)
- Context files such as AGENTS.md do "not generally improve task success rates,
  while increasing inference cost by over 20%". Preprint.
  [Gloaguen et al., arXiv 2602.11988](https://arxiv.org/abs/2602.11988)
  A smaller study found 28.64% lower median runtime with AGENTS.md and comparable
  task completion. Preprint.
  [Lulla et al., arXiv 2601.20404](https://arxiv.org/abs/2601.20404)
- When memory systems build their own memory, 11 of 12 pairings do no better than
  no memory. Injecting verified experience helped four of five agents by 1.1–4.5
  points. Preprint. [VibeMemBench, arXiv 2609.23570](https://arxiv.org/abs/2609.23570)

## 4. Does it do what was asked?

- 21,120 agent runs: "A subpar plan hurts performance even more than no plan at
  all", and periodic plan reminders reduce plan violations. Preprint.
  [Liu et al., arXiv 2604.12147](https://arxiv.org/abs/2604.12147)

## 5. Can review keep up?

AI raises the amount of code far faster than finished work, so review becomes the
bottleneck.

- 500,000+ GitHub developers: autonomous coding agents raised commits by 240%, but
  only 30% more releases, attributed to "human bottlenecks in the production
  chain". Working paper, not peer reviewed; the paper discloses a co-author
  relationship. [Demirer, Musolff and Yang, NBER w35275](https://www.nber.org/papers/w35275)
- 718 firms, January 2021 to March 2026: after adopting coding agents, pull
  requests rose 23%, with no significant rise in finished work (resolved issues
  and epics). "The average time to review a pull request increases by 49%, the
  share of pull requests with changes requested nearly doubles", and comments per
  pull request rise 35%. The bottleneck persists after firms adopt AI code review.
  Working paper; data from a partnership with Jellyfish, an engineering analytics
  firm. [Chen and Stratton, Harvard, version of 4 August 2026](https://fion.ac/jellyfish.pdf)
- 22,000 developers, 4,000 teams, two years to March 2026: as teams moved to high
  AI adoption, "median review time has increased 5X", bugs per developer rose 54%,
  and "31.3% more PRs are being merged without any review". Vendor report from
  Faros, an engineering analytics firm; correlations within each team between its
  lowest- and highest-adoption quarters, with no control group.
  [Faros, AI Engineering Report 2026](https://pages.faros.ai/hubfs/AI_Engineering_Report_2026_The_Acceleration_Whiplash_Faros.pdf)
  Its 2025 report (10,000 developers, 1,255 teams) found 98% more PRs merged and
  PR review time up 91%. That report is behind a sign-up form; the figures are
  from Faros's own summary. [Faros, 23 July 2025](https://www.faros.ai/blog/ai-software-engineering)
- AI reviewers do not fill the gap: existing review agents together "solve only
  around 40%" of review tasks built from human reviews. Preprint.
  [c-CRAB, arXiv 2603.23448](https://arxiv.org/abs/2603.23448)

## 6. Is it actually faster?

Unproven. What developers feel and what is measured disagree.

- Randomized trial, early-2025 tools: AI made experienced developers 19% slower,
  while they estimated it made them 20% faster. Preprint.
  [METR, arXiv 2507.09089](https://arxiv.org/abs/2507.09089)
- METR's 2026 follow-up estimates a speedup, but its own interval includes no
  effect, and METR calls the data "an unreliable signal".
  [METR, 24 February 2026](https://metr.org/blog/2026-02-24-uplift-update/)
- More code does not mean more shipped software: see the NBER paper in question 5.

## 7. Is it safe to let it run?

Agents have escaped sandboxes, leaked files, and followed instructions hidden in
the content they read.

- Sandbox escape: sandboxed code could write `.claude/settings.json`.
  [CVE-2026-25725](https://nvd.nist.gov/vuln/detail/CVE-2026-25725)
- Sandbox escape through Git worktree path confusion.
  [CVE-2026-55607 / GHSA-7835-87q9-rgvv](https://github.com/advisories/GHSA-7835-87q9-rgvv)
- A permissive default allowlist allowed unauthorized file reads and network
  exfiltration. [CVE-2025-55284 / GHSA-x5gv-jw7f-j6xj](https://github.com/advisories/GHSA-x5gv-jw7f-j6xj)
- Indirect prompt injection could make Cursor create its MCP configuration file,
  leading to code execution. [CVE-2025-54135](https://nvd.nist.gov/vuln/detail/CVE-2025-54135)
