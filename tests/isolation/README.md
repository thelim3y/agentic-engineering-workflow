# Isolation conformance suite

Status: bounded feasibility spike. It does not approve the production execution
boundary, choose the controller language, or make any measured adapter part of the
core architecture.

## Contract

For each fixture and adapter, the runner uses fresh disposable environments for:

| Run | Expected result |
|---|---|
| Control disabled | The attack succeeds, proving the fixture is valid. |
| Control enabled | The attack is blocked. |
| Positive control | The permitted operation succeeds. |

A fixture passes only when all verdicts, judges, startup records, process checks,
and output checks succeed. Missing, unknown, skipped, timed-out, unsupported, or
untested results never pass. Exit 0 means every selected fixture passed; exit 1
means at least one did not; exit 2 means selection or outer execution failed.

Judges run outside the adapter sandbox and compare controlled state. Fixture output
is diagnostic only.

## Safe use

Run `runner.py`; do not run adapters directly. The runner creates a bubblewrap
safety envelope with:

- a cleared environment and allowlisted read-only system inputs;
- no host home, SSH agent, credentials, `/run`, or host `/tmp`;
- a disposable `/work`;
- one fresh writable results directory.

There is no unsandboxed fallback. The wrapper retains host networking for the fixed
HTTPS control and does not isolate host TCP services. It is safe only for reviewed
fixtures on a disposable, credential-free machine.

`--runtime-root` mounts one reviewed, credential-free tool installation at
`/opt/runtime`. Never point it at a home, workspace, or credential store.

Results use a new `isolation-results-*` directory under `/tmp`, or the parent
given to `--results-dir`. Existing output is not overwritten. `--keep` copies
fixture files before teardown. Results are not immutable audit storage.

## Commands

Safe regression tests require Linux, Python 3.9+, PID file descriptors, and POSIX
shell. They do not run the attack suite, external network, or models.

```sh
python3 -B -m unittest discover -s tests/isolation -p 'test_*.py'
```

Example bounded conformance run:

```sh
python3 -B tests/isolation/runner.py --host bwrap --fixture 21-failure-propagation
```

Current evidence for complete bubblewrap and Codex-sandbox runs is in
[results/linux-2026-10-12](results/linux-2026-10-12/README.md). Complete agent
sessions and Claude Code remain unproven.

## Layout

- `runner.py`: creates environments, invokes adapters, judges, and writes results.
- `processes.py`: tracks descendants, bounds output, cancels, and confirms cleanup.
- `fixture-entry.sh`: records that a fixture entered the adapter boundary.
- `adapters/`: thin `info` and `run` implementations for each boundary.
- `fixtures/`: host-neutral attacks, judges, positive controls, and contract cases.
- `projects/`: real build-system inputs used by fixtures.
- `results/`: retained dated evidence.

Adapters implement:

```text
info
run <policy.env> <fixture.sh> <phase>
```

Unsupported policy exits 64 with `ISOLATION_UNSUPPORTED: <reason>` and runs
nothing.

The fixture environment names writable workspace, protected verification inputs,
hidden tests, evidence, fake credentials, a fake socket, a decoy process, and
network policy. These values are synthetic.

The network fixture uses `github.com` with TLS verification. Any received HTTP
response proves communication. Transport failure is compared with disabled and
allowed controls; ambiguity remains untested.

Fixture 20 proves unsupported policy fails closed. Fixture 21 proves exit-code
propagation. Fixture 22 runs real CMake configure-time tampering and an allowed
C++ build. Fixture 07 remains a smaller shell-based build-script case and is part
of the preserved evidence manifest.

## Current limits

- Codex and bubblewrap passed the 22 shell/build fixtures on the recorded Linux host.
- A surrounding Codex sandbox can deny fake-socket setup; that is `untested`, not pass.
- Claude/SRT and complete model sessions have not run.
- Native editing tools, MCP, trusted workflow state, immutable storage, and PR
  actions are outside this suite.
- [Issue 9](https://github.com/thelim3y/agentic-engineering-workflow/issues/9)
  tracks remaining harness-integrity work before new claims.
