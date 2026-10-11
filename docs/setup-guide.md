# Software Factory Plugin — Setup and C++ Verification Guide

**Status:** Setup blueprint for a plugin under design; not documentation for an already released product.

**Updated:** 11 October 2026.

**Initial hosts:** Claude Code and Codex.

**Initial target:** C++ first; .NET/C# follows. Python remains a candidate.

Contract authority: [design index](README.md). The linked topic contracts own policy;
this guide covers onboarding and tool selection, not alternate schemas or defaults.

This guide explains how to prepare the agent hosts, GitHub integration, shared memory, and repository verification tooling. It distinguishes agreed requirements from recommendations and unresolved settings. No factory installation command, configuration parser, or cross-provider runner integration has yet been verified. Example factory configuration below is illustrative, not executable product configuration.

## 1. Start with what already exists

The project owner reports an existing, working GitHub machine user, SSH keys, a test repository with issues, and presets for ASan, UBSan, and testing. These should be reused. Their exact names and contents have not been inspected for this guide. The examples use CMake/CTest as the assumed preset tooling; confirm that mapping during repository discovery.

Clang tooling is the chosen lint and code-style family: this guide maps that to **clang-tidy for lint/static analysis** and **clang-format for formatting**. Discover and preserve existing project configuration before proposing additions.

The agreed operating model is:

- Start the plugin manually inside Claude Code or Codex.
- Supply a GitHub issue number/URL, or select from labelled issues. The configured eligibility label is mandatory in either case.
- Default selection is oldest by creation date, skipping issues blocked by unfinished GitHub dependencies. Ordering and shortlist behavior are configurable.
- Treat an issue as one task intended to produce one PR. Do not automatically split it into subtasks.
- Apply the [planner policy](planner.md): XL+ pauses for approval; Large and below notify and continue unless another concern requires a pause. Reassess material scope growth.
- Configure runner, provider, and model per agent, inheriting shared defaults where appropriate.
- Stop and notify in the terminal when the configured retry limit is reached. Preserve work and evidence; do not silently switch models.
- Use Engram initially, behind a replaceable memory integration.
- Produce structured agent outputs and an auditable record of actions and handoffs.
- Make unattended operation and approval gates configurable.

The desktop application is deferred. This does not impose a local-only deployment restriction on the factory or its services.

## 2. Workflow and responsibility boundaries

The [workflow contract](workflow.md) owns stage order, role handoffs and issue state.
Tests proceed in small batches: TDD → independent testing for meaningful red →
implementation → independent testing for green. Production and test repairs return
to their respective owners. Pre-PR checks, PR creation, review and merge remain
separate responsibilities. Required evidence comes from controlled execution, not
agent prose. See [test quality and native profiles](verification.md).

## 3. Prepare the hosts and existing GitHub identity

### Agent hosts

Install and authenticate the supported Claude Code and Codex versions using their official documentation. Pin a tested version range for each factory adapter and record the actual version on every run. A plugin bundle can package instructions and integrations, but identical behavior across hosts must be tested. See [Claude plugins](https://code.claude.com/docs/en/plugins) and [Codex plugins](https://learn.chatgpt.com/docs/plugins).

Once factory packaging exists, its installation guide should provide separate verified host instructions. Until then, do not treat an invented slash command or a manifest sketch as an installation procedure.

For each configured agent, resolve its runner, provider, model, tool permissions, and limits before execution. Reject unsupported combinations clearly. Cross-provider execution from either terminal is an adapter requirement to demonstrate, not a capability assumed from a model setting.

### GitHub

Reuse the configured machine user and SSH setup. Check the effective identity in the trusted GitHub integration environment, not inside an agent's unrestricted shell:

```sh
git --version
gh --version
gh auth status --hostname github.com
gh api user --jq .login
```

These are existing Git/GitHub CLI commands, not factory commands. SSH authentication for Git transport and the GitHub CLI's API identity are separate checks. Verify the repository remote and permissions without printing private keys or token values. [GitHub CLI authentication](https://cli.github.com/manual/gh_auth_status), [GitHub CLI API access](https://cli.github.com/manual/gh_api).

Configure the repository, permitted base branch, eligibility label, selection policy, and GitHub dependency lookup. GitHub provides explicit “blocked by” and “blocking” issue relationships; use these rather than interpreting every issue mention as a dependency. Failure to read dependencies is an unknown state, not proof that an issue is unblocked. [Issue dependencies](https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-issue-dependencies).

Keep the existing account arrangement. If the PR author and reviewer use the same account, record the factory's review verdict separately: GitHub does not allow that account to approve its own PR. Where a repository requires another identity's approval, honor it. Draft PRs cannot merge until marked ready. [Required reviews](https://docs.github.com/en/pull-requests/how-tos/review-pull-requests/approving-a-pull-request-with-required-reviews), [draft stages](https://docs.github.com/en/pull-requests/how-tos/create-pull-requests/changing-the-stage-of-a-pull-request).

## 4. Connect and verify Engram

The selected project is **thebtf/engram**. Its documented architecture uses PostgreSQL persistence, a server, and a local MCP process communicating with agent hosts over stdio. Follow the deployment instructions for a pinned release and the intended authentication mode; do not copy another similarly named project's configuration. [Engram repository and setup](https://github.com/thebtf/engram).

Before using it for task work:

1. Confirm the host discovers the intended Engram tools.
2. Write a non-secret test memory and retrieve it from a fresh session.
3. Verify both hosts can access the intended shared project context.
4. Exercise unavailable-server behavior and record the selected recovery policy.
5. Test role access restrictions before storing hidden test information.
6. Verify approval filtering, retired lessons, cache fallback and automatic host injection.
7. Record tested client/server versions and capabilities; repeat conformance checks before upgrades.

The [learning contract](learning.md) owns these rules. Backend governance does not substitute for our approval boundary.

**Factory policy:** use Engram for permitted context and human-approved lessons. Keep authoritative workflow state, evidence, and handoff records separately controlled by the factory. Search results are contextual information, not permission to skip a gate.

A namespace or tag is not proof of access isolation. If the chosen deployment cannot enforce the required boundary, hidden tests and revealing diagnostics must stay in a separate verifier-controlled store. Never place secrets or unrestricted hidden-test artifacts in shared recall.

## 5. Recommended top-tier C++ tools

“Top-tier” here means a recommended engineering shortlist, not a universal ranking. Prefer existing working tools and add a tool where it supplies missing evidence. Pin compatible versions and configurations; installing every tool does not establish correctness.

### Core verification profile

| Tool | Role and recommendation | Evidence to retain |
|---|---|---|
| **Project compiler/toolchain** | Preserve existing supported compilers and warning policy. Validate each required target/toolchain combination; the lint tool need not be the production compiler. | Compiler identity, flags, configure/build result, diagnostics |
| **CMake presets + CTest** | Reuse the existing ASan, UBSan, and testing presets. Resolve configure/build/test relationships explicitly. [Presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html), [CTest](https://cmake.org/cmake/help/latest/manual/ctest.1.html) | Preset names, effective configuration, test inventory, test results |
| **clang-format** | Chosen code-style checker; use the repository's applicable `.clang-format` files and check-only execution. [Documentation](https://clang.llvm.org/docs/ClangFormat.html) | Version, configuration identity, selected files, formatting diagnostics |
| **clang-tidy** | Chosen lint/static analyzer; use existing `.clang-tidy` settings and a matching compilation database. [Documentation](https://clang.llvm.org/extra/clang-tidy/) | Analyzed translation units, diagnostics, tool/configuration identity |
| **AddressSanitizer (ASan)** | Existing project preset: execute instrumented tests to detect memory-access defects. [Documentation](https://clang.llvm.org/docs/AddressSanitizer.html) | Instrumentation evidence, execution logs, symbolized diagnostics |
| **UndefinedBehaviorSanitizer (UBSan)** | Existing project preset: execute checks for configured undefined behavior. Verify how findings cause a gate failure. [Documentation](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html) | Enabled checks, recovery settings, execution logs and findings |
| **Existing C++ test framework** | Keep the current framework. If one is missing, **GoogleTest/GoogleMock** or **Catch2** are strong choices; choose one primary framework rather than migrating for this plugin. [GoogleTest](https://google.github.io/googletest/), [Catch2](https://github.com/catchorg/Catch2) | Test cases, assertions, framework results, requirement mapping |

For a CMake repository already using Ninja, keep it. **Ninja** is a strong build executor, but changing a working generator is not a factory prerequisite. [Ninja documentation](https://ninja-build.org/manual.html).

### Strong additions when applicable

These are recommendations to evaluate during onboarding, not previously agreed mandatory gates.

| Tool | Use when | Important limit |
|---|---|---|
| **CodeQL** | Add security-oriented code scanning for the public C++ repository; consume findings in PR review. [Documentation](https://docs.github.com/en/code-security/concepts/code-scanning/codeql/codeql-code-scanning) | No findings does not establish that extraction or coverage was complete; retain scan scope and extraction status. |
| **Gitleaks** | Scan commits/content for accidental secret disclosure before publication. [Documentation](https://github.com/gitleaks/gitleaks) | Redact reports. Do not publish the discovered secret as evidence. |
| **ThreadSanitizer (TSan)** | Exercise concurrent code in a separate supported sanitizer configuration. [Documentation](https://clang.llvm.org/docs/ThreadSanitizer.html) | Platform support and runtime overhead differ; no automatic claim of Windows parity. |
| **llvm-cov + llvm-profdata** | Identify unexecuted behavior and collect source-based coverage. [Coverage guide](https://clang.llvm.org/docs/SourceBasedCodeCoverage.html) | Coverage measures execution, not assertion quality. Any thresholds are project policy. |
| **Google Benchmark** | Measure specific performance-sensitive changes with repeatable benchmarks. [Project](https://github.com/google/benchmark) | Control build mode and environment; noisy one-off timings should not become regression verdicts. |
| **AFL++** | Fuzz parsers, importers, protocol handlers, and other input-heavy components. [Project](https://github.com/AFLplusplus/AFLplusplus) | Needs a suitable harness, corpus, execution budget, and reproducible failing inputs. |
| **Cppcheck** | Add a complementary static-analysis pass when it finds useful defects beyond the existing checks. [Project](https://github.com/cppcheck-opensource/cppcheck) | Measure noise and overlap before making it mandatory. |
| **Qt Test** | Exercise application behavior where the target actually uses Qt. [Overview](https://doc.qt.io/qt-6/qtest-overview.html) | Not a universal desktop automation solution; broader UI scenarios need a framework-appropriate harness. |
| **Vulkan validation / RenderDoc** | Validate Vulkan usage or investigate rendering when the target includes those graphics workloads. [Validation guide](https://docs.vulkan.org/guide/latest/validation_overview.html), [RenderDoc](https://renderdoc.org/docs/introduction.html) | CPU tests cannot substitute for relevant GPU/runtime evidence; a capture alone is not a pass criterion. |

Preserve the existing dependency manager. If onboarding reveals unpinned dependency resolution, evaluate **vcpkg manifest/versioning configuration** or **Conan lockfiles**, according to the existing ecosystem. Neither should be introduced solely to run the factory. [vcpkg manifests](https://learn.microsoft.com/en-us/vcpkg/concepts/manifest-mode), [Conan lockfiles](https://docs.conan.io/2/tutorial/versioning/lockfiles.html).

## 6. Discover and bind the existing verification profile

### Inventory before execution

Read project instructions, CI workflows, preset files and their includes, test registration, dependency configuration, formatting/lint settings, and verification scripts. This is discovery of executable configuration: executing a configure step can itself run repository code and must use the intended execution permissions.

Useful existing discovery commands, from the target repository root:

```sh
cmake --list-presets=all
ctest --list-presets
clang-format --version
clang-tidy --version
```

Respect preset inheritance, environment, conditions, generators, toolchain files, and multi-configuration settings. Configure, build, and test presets can have different names. Local user presets must not silently introduce unrecorded differences from CI; capture sanitized effective settings. [CMake presets](https://cmake.org/cmake/help/latest/manual/cmake-presets.7.html).

Complete this mapping using actual repository values:

| Verification lane | Configure preset | Build preset/targets | Test preset | Required host/environment |
|---|---|---|---|---|
| Normal project verification | Discover | Discover | Discover | Discover |
| Existing ASan verification | Discover | Discover | Discover | Discover |
| Existing UBSan verification | Discover | Discover | Discover | Discover |
| Other existing required lanes | Discover | Discover | Discover | Discover |

Confirm whether sanitizer test presets already exist or whether the current setup only provides sanitizer builds. An instrumented build without executing the relevant code does not verify runtime behavior. Do not silently invent missing test presets; surface the gap.

### Run each required lane

The following are command templates. Replace uppercase names with discovered values. The artifact directory must already exist and be unique to the run, revision, lane, and attempt. Use the repository's equivalent verified wrapper if one exists.

```sh
cmake --preset CONFIGURE_PRESET
cmake --build --preset BUILD_PRESET
ctest --preset TEST_PRESET --show-only=json-v1
ctest --preset TEST_PRESET --output-on-failure --no-tests=error --output-junit RUN_ARTIFACT_DIRECTORY/results.xml
```

Execute sequentially and stop on a failed configure/build step. Build the required application and test targets; an explicit test target may be necessary if tests are excluded from the default build. Apply the recorded resource limits.

CTest can emit JSON test discovery and JUnit execution results. `--no-tests=error` rejects an empty selection, but does not prove every expected test ran. Check the actual inventory, skips, filters, and executed results against the approved profile. A single CTest entry may wrap many framework cases, so retain framework-level evidence where needed. [CTest command reference](https://cmake.org/cmake/help/latest/manual/ctest.1.html).

### Preserve sanitizer intent

Keep existing ASan and UBSan configurations rather than recreating them. Inspect instrumentation, linked runtime, suppression files, relevant environment, and actual test execution. A preset's name alone is not evidence of instrumentation.

UBSan commonly continues after reporting a defect. Verify that the existing profile makes relevant reports fail the gate, through an appropriate recovery policy or validated diagnostic handling. Any setting change belongs to the verification owner. [UBSan error handling](https://clang.llvm.org/docs/UndefinedBehaviorSanitizer.html).

ASan and TSan require separate configurations; do not assume all sanitizers can be combined. Support varies by compiler and platform: Microsoft's documented ASan implementation does not imply matching UBSan/TSan availability. Preserve unsupported-required checks as blocked rather than passing them. [Clang sanitizer combinations](https://clang.llvm.org/docs/UsersManual.html), [Microsoft ASan](https://learn.microsoft.com/en-us/cpp/sanitizers/asan?view=msvc-170).

### Bind Clang checks to the project

Use existing wrapper targets/scripts where available. The underlying check-only forms are:

```sh
clang-format --dry-run --Werror --style=file SOURCE_FILE
clang-tidy -p BUILD_DIRECTORY SOURCE_FILE
```

Resolve the applicable formatting configuration before execution; a missing file must be surfaced rather than silently adopting a fallback style. The verification role must not use `clang-format -i` or apply lint fixes. Production fixes return to implementation; test fixes return to TDD. [clang-format](https://clang.llvm.org/docs/ClangFormat.html).

For clang-tidy, use the intended checks, warning policy, include paths, defines, and generated headers. Do not enable every check indiscriminately. Record diagnostics and evaluate the configured blocking rules; suggested fixes are artifacts, not permission to apply them. Analyze affected translation units when headers change. [clang-tidy](https://clang.llvm.org/extra/clang-tidy/).

CMake's compilation database export is supported by Makefile and Ninja generators; it is not universally available from every generator. Resolve an existing lint build or a deliberate compatible configuration rather than guessing. [Compilation database export](https://cmake.org/cmake/help/latest/variable/CMAKE_EXPORT_COMPILE_COMMANDS.html).

## 7. Enforce test and verification ownership

Follow the [execution contract](execution.md). Test protection includes indirect
shell/build changes, shared configuration, subprocesses and result capture.
Test visibility never changes write ownership. The implementer requests test fixes;
TDD owns them. Policy changes require separate authorization.

Before onboarding a host/version/OS, demonstrate allowed work and rejected bypasses
in disposable environments without production credentials. Prompts, hooks and hashes
alone do not prove prevention. Unsupported isolation modes must stop onboarding.

## 8. Configure the factory

Follow the [configuration contract](configuration.md): defaults → repository →
explicit run overrides, with per-role overrides within each layer. Validate before
claiming work, report value origins, and retain a sanitized effective snapshot.
No concrete configuration file format or installation command is implemented yet.

## 9. Gate results, handoffs and audit records

Use the [single record contract](communication-protocol.md); no alternate header
format is defined here. Bind evidence to exact source, test, policy and environment
identities, including dirty work. The controller computes gates from controlled
execution records. Reuse evidence only while its relevant inputs remain valid.

Apply [audit protection](audit.md) and [checkpoint recovery](checkpoints.md).
At merge, recheck current repository protections and evidence for the accepted
revision/integration state. Ready is not merged, and neither implies unexecuted
platform checks passed.

## 10. Commission the plugin in the existing test repository

These are acceptance checks for the future integration, not claims that they have already passed.

1. **Resolve setup:** both host integrations identify their versions, machine-user identity, Engram connection, agent configuration, and required repository tools.
2. **Verify eligibility:** explicit unlabelled issues are rejected; automatic selection skips unfinished dependencies and selects the oldest eligible issue.
3. **Exercise the scope gate:** XL+ waits for approval; Large and below notify and continue unless another concern requires a pause. No automatic issue/PR splitting.
4. **Establish a baseline:** existing configured builds, tests, ASan/UBSan runs, and Clang checks produce attributable results. Existing defects are reported, not silently waived.
5. **Prove TDD:** use one small issue with a clear behavioral requirement; record meaningful failing tests before the implementation succeeds.
6. **Test enforcement:** attempt direct and command-mediated changes to tests and verification controls; confirm rejection. Check hidden-test access according to the chosen policy.
7. **Test gate honesty:** an empty test selection, removed test, sanitizer diagnostic, lint violation, and unavailable required environment cannot produce a false pass.
8. **Test failure handling:** exhaust the configured attempt limit; confirm a terminal notification and preserved work/evidence, with no silent model fallback.
9. **Exercise PR flow:** create a draft after readiness checks, review the actual revision, repair findings through the owning agents, and revalidate before marking ready.
10. **Exercise merge modes and interruption:** prove the chosen approval behavior, a policy-compliant merge where enabled, and recovery without duplicate PRs or false completion claims.
11. **Exercise durable ownership:** simultaneous starts, explicit takeover, late reports and crashes between effect/receipt/checkpoint cannot bypass ownership or audit.
12. **Evaluate the factory:** use the [evaluation plan](evaluation.md) on designated test projects, including a simpler baseline and failure cases.

Repeat the host-specific checks for Claude Code and Codex. Equivalent prompts are not evidence of equivalent permissions or lifecycle behavior.

The final terminal report should link the issue, PR, and retained evidence; identify the tested/merged revision; show which required checks passed; and state any blocked or unexecuted work. “All configured checks passed” is a bounded claim. “The application has no bugs” is not supported by a green test run.

## 11. Remaining setup decisions

- Actual repository, base branch, label spelling, and permitted execution environments.
- Names and relationships of the existing ASan, UBSan, normal build, and testing presets.
- Existing test framework and exact clang-format/clang-tidy configurations.
- Scope thresholds and behavior when scope grows during implementation.
- Retry count and what constitutes a counted implementation attempt.
- Hidden-test visibility/publication policy and enforcement mechanism.
- Per-role runners/models and validated cross-provider execution support.
- Engram release, connection/authentication profile, and failure policy.
- Required additional tools, supported platform matrix, runtime scenarios, and merge/approval settings.

Repository inspection should resolve discoverable facts. Ask the operator only for genuine policy choices or ambiguities. Preserve the distinction between configured intent and verification that the installed system enforces it.
