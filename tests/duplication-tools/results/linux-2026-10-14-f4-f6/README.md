# Linux duplication tool evidence: F4–F6

Run: 2026-10-14. Status: tool-selection spike; the check is not implemented.

Same host and tool versions as [the first run](../linux-2026-10-14/README.md):
PMD 7.28.0 on Temurin 21.0.12.1, jscpd 5.3.3, Dolos 2.9.3, lizard 1.24.0, each
confirmed from the tool. The installs were reused from the first run's working
directory. F4–F6 pass `clang++ -std=c++20 -fsyntax-only -Wall -Wextra` (Ubuntu
clang 19.1.1).

## Question

Does a minimum match size still separate copies from convention-similar code when
convention code shares more boilerplate, and when a copy's edits are spread out?

| Case | Added file | Class recorded before the run |
|---|---|---|
| F4 | `outline_pass.cpp` | Convention, close: the forward pass's pipeline, preamble and mesh-binding conventions; a selection filter, no textures, no clear. |
| F5 | `water_pass.cpp` | Copy: the forward pass adapted line by line, with an edit every few statements. |
| F6 | `sky_pass.cpp` | Convention, medium: a fullscreen pass with a depth test and the same pipeline and preamble conventions. |

The classes and expected results were recorded in [EXPECTED.md](EXPECTED.md) and
hashed with the fixtures in [SHA256SUMS](SHA256SUMS) before the first tool run.
The agent that wrote the proposal wrote F4–F6, to stress its margin, knowing how
CPD tokenizes.

F4 is arguable. It repeats the forward pass's mesh-binding loop without textures,
and a reviewer could call that a copy. Its class decides which mechanism the
results favour.

## Results

Longest match involving the added file, identifiers and literals ignored:

| Tool | F1 copy | F2 copy | F5 copy | F3 conv. | F4 | F6 conv. |
|---|---|---|---|---|---|---|
| PMD CPD | 581 | 245 | 86 | 68 | 85 | 78 |
| jscpd | 494 | 282 | 89 | 72 | 93 | 81 |

Whole-file similarity, Dolos default settings:

| F1 | F2 | F5 | F3 | F4 | F6 |
|---|---|---|---|---|---|
| 1.00 | 0.90 | 0.78 | 0.53 | 0.61 | 0.62 |

lizard reports only F1. F1–F3 results are identical to the first run.

## Finding

Range of settings that reports every copy and no convention fixture:

| F4 class | CPD minimum | jscpd minimum | Dolos score |
|---|---|---|---|
| Convention | 86 only | None: F4 exceeds F5 | Separates: copies ≥ 0.78, conventions ≤ 0.62 |
| Copy | 79–85 | 82–89 | None: F6 0.62 exceeds F4 0.61 |

Either way, the margin between copy and convention is a few tokens, not the 70–245
of the first run. A floor set above the convention code can miss a copy whose edits
are spread out. Dolos was not a pre-run question, gives no line ranges, and
separates only if F4 is convention.

## Files

| File | Command |
|---|---|
| [cpd.txt](cpd.txt) | `spike.py cpd` |
| [jscpd.txt](jscpd.txt) | `spike.py jscpd` |
| [dolos.txt](dolos.txt) | `spike.py dolos` |
| [lizard.txt](lizard.txt) | `spike.py lizard` |
| [probes.txt](probes.txt) | `spike.py probes`; identical to the first run |
