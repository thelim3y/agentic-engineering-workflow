# Duplication tool status

Status: tool-selection evidence for
[#64](https://github.com/thelim3y/agentic-engineering-workflow/issues/64). The
check is not implemented.

## Result

The fixtures, script and run record are in
[tests/duplication-tools](../../tests/duplication-tools/README.md). The window is
the range of minimum match lengths that detects F1 and F2 but not F3, with
identifiers and literals ignored.

| Tool | Version, licence | F1 renamed | F2 small edits | F3 convention | Window | Scan inventory |
|---|---|---|---|---|---|---|
| PMD CPD | 7.28.0, BSD-style | Detected | Detected in 2–3 pieces | Silent from 70 tokens | 70–245 tokens | Every scanned file, with token counts |
| jscpd | 5.3.3, MIT | Detected | Detected; one pair with `--max-gap-lines` | Silent from 75 tokens | 75–282 tokens | Counts only; files below the minimum are left out |
| Dolos | 2.9.3, MIT | Similarity 1.00 | 0.90 | 0.53 | None: whole-file score; no line ranges in its output | Not checked |
| lizard | 1.24.0, MIT | Detected | Missed | Silent | None: minimum fixed at 70 tokens | Not checked |

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

- Synthetic code, C++ only, one fixture of each kind.
- F2's edits are clustered. Both tools need one unchanged stretch at least as long
  as the minimum; jscpd's gap merge joins only pieces that each meet it. A copy
  with edits throughout is missed.
- F3 matched at 68 tokens (CPD) and 72 (jscpd), just below the window floors. The
  floor depends on the longest boilerplate a project's conventions share, so each
  project calibrates it. Choose a value mid-window, not at the floor.
