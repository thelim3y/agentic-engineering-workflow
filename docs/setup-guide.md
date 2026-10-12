# Setup and C++ verification

Status: onboarding blueprint, not installation instructions. No factory package or
configuration parser exists.

Initial hosts: Claude Code and Codex. Initial target: C++. The
[contract index](README.md) owns policy.

## Reuse existing infrastructure

The intended environment already has:

- a GitHub machine user, SSH keys, and a test repository;
- CMake presets for normal, ASan, UBSan, and test builds;
- Clang-based lint and formatting policy.

Discover exact names and behavior. Do not replace working project configuration.

## Host checklist

For each supported host:

1. Install and authenticate from official instructions.
2. Pin and record the tested host version.
3. Resolve runner, provider, model, permissions, and limits per role.
4. Run the shared isolation and structured-output conformance suite.
5. Reject unsupported combinations before claiming an issue.

Plugin packaging supplies entry points; it does not make host behavior identical.
Cross-provider execution is a capability to prove, not assume.

## GitHub checklist

Reuse the machine user. Verify Git and API identities without exposing secrets:

```sh
git --version
gh --version
gh auth status --hostname github.com
gh api user --jq .login
```

Configure the repository, base branch, required eligibility label, oldest-first
selection, and dependency lookup. Unknown dependency state blocks selection.
Honor branch protection and required reviews. The PR author's agent verdict is
not a GitHub approval.

## Engram checklist

Use [thebtf/engram](https://github.com/thebtf/engram) for permitted context and
human-approved lessons only.

1. Pin the client and server versions.
2. Write a non-secret record and retrieve it from a fresh session.
3. Verify project and role isolation through both hosts.
4. Test outage, stale-data, retirement, cache, and upgrade behavior.
5. Keep policy, workflow state, evidence, credentials, and hidden tests elsewhere.

A namespace or tag does not prove access isolation.

## C++ verification profile

Prefer existing project tools. Add a tool only when it supplies missing evidence.

| Tool | Required use |
|---|---|
| Compiler and warnings | Preserve supported toolchains and warning policy. |
| CMake presets and CTest | Discover and run normal, ASan, UBSan, and test lanes. |
| Existing test framework | Keep it; do not migrate merely for the factory. |
| clang-format | Run repository policy in check-only mode. |
| clang-tidy | Use repository checks and the intended compilation database. |
| ASan and UBSan | Prove instrumentation and execute relevant tests. |

Evaluate when relevant: TSan, llvm-cov, CodeQL, Gitleaks, Cppcheck, fuzzing,
Google Benchmark, framework-specific UI tests, Vulkan validation, and RenderDoc.
None is universally mandatory.

## Discover the project profile

Read project instructions, CI, presets and includes, test registration, dependency
configuration, verification scripts, and Clang settings. Useful discovery commands:

```sh
cmake --list-presets=all
ctest --list-presets
clang-format --version
clang-tidy --version
```

Map every required lane to its configure preset, build preset or targets, test
preset, host, and environment. Then run the project's verified commands. For CTest:

```sh
ctest --preset TEST_PRESET --show-only=json-v1
ctest --preset TEST_PRESET --output-on-failure --no-tests=error
```

Check inventory, filters, skips, and executed results. A preset name does not prove
sanitizer instrumentation. A sanitizer build without execution proves no runtime
behavior. Missing or unavailable required lanes block progression.

Use existing wrappers for Clang checks. Otherwise the underlying check-only forms are:

```sh
clang-format --dry-run --Werror --style=file SOURCE_FILE
clang-tidy -p BUILD_DIRECTORY SOURCE_FILE
```

Verification never applies fixes. Production findings return to implementation;
test findings return to TDD.

## Commissioning gate

Use a disposable repository and non-production credentials. Demonstrate:

- labelled intake, atomic claim, planning, and approval;
- meaningful red before production implementation;
- protected tests during implementation and build execution;
- independent green, failure routing, limits, and recovery;
- revision-bound native checks and audit evidence;
- draft, review, repair, ready, merge, and completion without duplicate actions.

Record tested hosts, tools, operating systems, limitations, and required unavailable
checks. Do not use the factory on a real project until the commissioning issue passes.
