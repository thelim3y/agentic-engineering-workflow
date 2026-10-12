# First goal

Status: product goal; not implemented.

## Goal

Deliver a software factory that is genuinely useful to a solo native-application
developer while preserving the boundaries needed for larger governed deployments.
Solo use is the first acceptance test. Enterprise-shaped operational complexity
must not be required.

## Intended experience

1. Install the factory and configure one repository and a conforming runner.
2. Label a GitHub issue and start the run manually.
3. Follow concise terminal progress and respond only when approval is required.
4. Receive a reviewable PR, its configured merge outcome and a report, or a clear
   stopped outcome with evidence and the next required action.

## Initial operating shape

- One local deployment and one repository per run.
- GitHub issue and PR adapters first.
- One configured runner per run; independently tested adapters prove that core
  behaviour is runner-independent.
- Sequential roles coordinated by one trusted controller.
- Protected local execution, durable checkpoints and a file-based audit provider.
- Strong defaults with minimal required configuration.
- No mandatory central server, hosted service or database for the base workflow.

Logical roles and replaceable providers do not require separate services. Add
infrastructure only when a demonstrated requirement justifies it.

## Growth constraint

Local providers must sit behind product-owned contracts so a larger deployment can
replace storage, identity, issue, repository, runner and execution providers without
rewriting workflow semantics. Do not stabilize an imagined abstraction: exercise an
important contract through a real implementation and a test fake first.

This foundation does not prove enterprise readiness. Multi-user operation, policy
administration, scale and stronger storage guarantees require separate evidence.

## Evidence that the goal works

- A solo developer can set up and operate the base workflow without administering
  unrelated infrastructure.
- A representative C++ task can reach a PR through the configured gates, or stop
  safely with an accurate reason.
- A failed or interrupted run preserves its audit history and can be reconciled
  without duplicate external actions or invented success.
- Repeated trials show whether the factory improves verified outcomes enough to
  justify its additional roles, time and cost.

Implementation evidence may revise the design. Required trust and ownership
invariants remain in force until deliberately changed; code and documentation must
not diverge silently.

## Not the first goal

- Multi-tenancy, organization-wide RBAC or SSO.
- High availability, distributed controllers or runner fleets.
- Central administration dashboards.
- Formal compliance or certification claims.
- Every language, operating system, issue provider or runner.
