# Duplication tool status

Status: tool-selection evidence for
[#64](https://github.com/thelim3y/agentic-engineering-workflow/issues/64). The
check is not implemented.

## Result

The fixtures, script and run records are in
[tests/duplication-tools](../../tests/duplication-tools/README.md). F1, F2 and F5
are copies: renamed, with clustered edits, and with edits spread throughout. F3,
F4 and F6 are convention-similar, though F4 is arguable. The window is the range of
settings that reports every copy and no convention fixture, with identifiers and
literals ignored.

| Tool | Version, licence | Copies F1, F2, F5 | Convention F3, F4, F6 | Window, F4 convention | Window, F4 copy | Scan inventory |
|---|---|---|---|---|---|---|
| PMD CPD | 7.28.0, BSD-style | 581, 245, 86 tokens | 68, 85, 78 tokens | 86 tokens only | 79–85 tokens | Every scanned file, with token counts |
| jscpd | 5.3.3, MIT | 494, 282, 89 tokens | 72, 93, 81 tokens | None | 82–89 tokens | Counts only; files below the minimum are left out |
| Dolos | 2.9.3, MIT | Similarity 1.00, 0.90, 0.78 | 0.53, 0.61, 0.62 | Above 0.62, up to 0.78 | None | Not checked; no line ranges in its output |
| lizard | 1.24.0, MIT | F1 only | Silent | None: minimum fixed at 70 tokens | None | Not checked |

With F1–F3 alone, the CPD window was 70–245 tokens
([first run](../../tests/duplication-tools/results/linux-2026-10-14/README.md)).
F4–F6 shrink it to a few tokens
([second run](../../tests/duplication-tools/results/linux-2026-10-14-f4-f6/README.md)).
Dolos was not a pre-run question for F4–F6.

Without ignoring identifiers and literals, neither CPD nor jscpd detects F1 at any
setting where F3 is silent.

## Suppression and configuration

- CPD and jscpd honour in-source markers (`CPD-OFF`/`CPD-ON`,
  `jscpd:ignore-start`/`jscpd:ignore-end`) and cannot turn them off. One marker
  pair hid the whole F1 copy.
- jscpd reads `.jscpd.json`, or a `jscpd` key in `package.json`, from its working
  directory, and honours `.gitignore` by default. Each hid F1. Running outside the
  tree with `--no-gitignore` avoided both.
- CPD opened only the scanned sources and ignored `.gitignore`.
- jscpd `--baseline-from-ref` marked a copy already in the base as old and the F2
  copy as new.

## Limits

- Synthetic code, C++ only, one to three fixtures of each kind. The agent that
  wrote the proposal wrote them; it wrote F4–F6 to stress the margin.
- Both tools need one unchanged stretch at least as long as the minimum; jscpd's
  gap merge joins only pieces that each meet it. F5, edited every few statements,
  kept an 86-token stretch under CPD. Denser edits leave shorter stretches.
- Convention code here shares stretches as long as a spread-edit copy's. A minimum
  size alone separates them only within a project's measured margin, if one
  exists; see the proposal's
  [calibration](../../tasks/duplication-check.md#calibration).
