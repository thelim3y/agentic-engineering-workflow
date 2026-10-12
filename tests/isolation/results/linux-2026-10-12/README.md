# Linux isolation evidence

Run: 2026-10-12 UTC (2026-10-11 Louisville local time).
Status: shell/build conformance only; **Checkpoint A is not approved**.

| Adapter | Result | Evidence |
|---|---|---|
| bubblewrap 0.9.0 | 22/22 pass, exit 0 | [summary](bwrap.json), [log](bwrap.log) |
| Codex CLI 0.156.1 sandbox | 22/22 pass, exit 0 | [summary](codex.json), [log](codex.log) |

Each run contains 20 attack fixtures with disabled, enabled and positive controls,
plus two contract fixtures. No fixture was skipped. These are mechanism tests,
not model-generated attacks or complete host-session tests.

## Environment and commands

Ubuntu 24.04.5 LTS, kernel 7.0.0-31-generic, x86-64. CMake 3.28.3,
GNU C++ 13.3.0 and GNU Make 4.3. The Codex executable was copied to a fresh
credential-free runtime directory; no model invocation, account access, package
installation or GitHub write occurred.

From the repository root:

```sh
python3 -B tests/isolation/runner.py --host bwrap
python3 -B tests/isolation/runner.py --host codex --runtime-root /tmp/factory-runtime-vjR3Sy
python3 -B -m unittest discover -s tests/isolation -p 'test_*.py' -v
```

The runtime path above records this run, not a portable installation path. Its
only file was `bin/codex`, SHA-256
`0b2e9301d6100dddda3b9d5c80ebaeaa3a2f1962388f2f36f6b96a9f08b1f33f`.
Regression result: 36 tests passed.

Suite commands ran with approved execution outside the surrounding Codex sandbox.
The runner's own outer safety sandbox and adapter controls remained enabled.
Inside the surrounding Codex sandbox, fake Unix-socket creation failed with
`EPERM`; the runner correctly returned `untested`, exit 1. Running the same narrow
fixture outside it passed. No host security setting was changed.

The final raw output directories were `/tmp/isolation-results-8katmi6o` (bubblewrap)
and `/tmp/isolation-results-oac6e5zw` (Codex). These copies preserve their contents.
[SHA256SUMS](SHA256SUMS) identifies the executed source and saved evidence, with
paths relative to the repository root. Base Git revision was
`9f0863746c51336890b5360d7a8b8671de23b6f6` with local changes; the hashes, not that
revision alone, identify the tested files. Hashes do not make this storage immutable.

## New C++ proof

Fixture 22 runs real CMake configure code that attempts to overwrite protected
test registration. With adapter controls disabled the overwrite succeeds; with
controls enabled CMake receives a read-only-filesystem error. Its positive control
configures, compiles, links and runs a small C++ executable in the writable workspace.

Initial attempts exposed a broken compiler alias and missing compiler support in
the outer wrapper. The fixture now uses `/usr/bin/g++` explicitly; public headers
and compiler helpers are mounted read-only. The new regression failed before that
mount change and passed afterward. No protected directory became writable.

## Still unproven

- Claude Code runtime and its native editing/MCP tools; `srt` is not installed here.
- Codex agent turns, native editing/MCP tools, structured output and effective model identity.
- Production adapters, mediated mixed-file edits, cache poisoning and the remaining
  execution-contract cases not represented by these fixtures.
- Trusted workflow state, late-result rejection, immutable audit storage and PR/merge gates.

This evidence does not select a production runtime language or approve onboarding.
