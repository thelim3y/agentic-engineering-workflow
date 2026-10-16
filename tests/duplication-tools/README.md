# Duplication tool spike

Status: tool-selection evidence for the
[duplicated-code check proposal](../../tasks/duplication-check.md). These are not
the check's tests; TDD writes those.

## Fixtures

Synthetic C++. `fixtures/base` is a project with one render path,
`forward_pass.cpp` (92 lines). Each case adds one file to the base:

| Case | Added file | Expected |
|---|---|---|
| F1 | `f1/terrain_pass.cpp`: the forward pass with every name changed (92 lines). | Detected |
| F2 | `f2/terrain_pass.cpp`: the terrain pass from plan-challenge case 11. A height attribute replaces the normal, and a height-texture sample precedes the material samples (113 lines; longest unchanged run 19 lines). | Detected |
| F3 | `f3/tonemap_pass.cpp`: a tonemap pass with the same conventions and different logic. It repeats the forward pass's viewport block (96 lines). | Not detected |
| F4 | `f4/outline_pass.cpp`: an outline pass with the forward pass's pipeline, preamble and mesh-binding conventions; a selection filter, no textures (98 lines). | Not detected; arguable |
| F5 | `f5/water_pass.cpp`: the forward pass adapted line by line, with an edit every few statements (110 lines). | Detected |
| F6 | `f6/sky_pass.cpp`: a fullscreen sky pass with a depth test and the same pipeline and preamble conventions (78 lines). | Not detected |

F4–F6 were added in a [second run](results/linux-2026-10-14-f4-f6/README.md).

Only pairs that involve the added file count. This stands in for the proposal's
changed-lines rule.

## Running

Install the tools outside the repository; the
[results](results/linux-2026-10-14/README.md) list exact versions and sources.
From the repository root:

```sh
python3 -B tests/duplication-tools/spike.py cpd --pmd PMD/bin/pmd --java-home JDK
python3 -B tests/duplication-tools/spike.py jscpd --jscpd JSCPD/node_modules/.bin/jscpd
python3 -B tests/duplication-tools/spike.py dolos --dolos DOLOS/node_modules/.bin/dolos
python3 -B tests/duplication-tools/spike.py lizard --lizard LIZARD/bin/lizard
python3 -B tests/duplication-tools/spike.py probes --pmd PMD/bin/pmd --java-home JDK \
  --jscpd JSCPD/node_modules/.bin/jscpd
```

`probes` checks in-source markers, in-tree configuration, `.gitignore` and jscpd's
base comparison. Every run uses temporary copies; the fixtures are never changed.
