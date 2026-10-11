# Evaluating the factory

Status: evaluation design; no trials or performance claims yet. Use the planned
test projects later, not production applications as an unapproved experiment.

## Questions

Does the factory deliver correct changes more reliably than a simpler workflow?
Do separate roles, retrieval and approved lessons justify their time and cost?
Does it stop safely when requirements, tools or authority are missing?

## Evaluation contract

Keep a versioned set of representative tasks with starting revisions, environments,
expected outcomes and evaluator-owned checks. Include ordinary delivery, ambiguous
tasks, existing defects and tasks that should stop. Factory agents cannot alter the
evaluation rubric or its protected checks. Keep evaluation-only material out of
production retrieval and learning inputs to avoid contaminating the measurement.

Compare against a simpler host-native workflow using equivalent task inputs, models,
resource budgets and environments. Record differing permissions or capabilities.
Use repeated trials because one successful run is not a reliability estimate.
Report sample size, variability, exclusions and unresolved results, not just averages.

## Measures

- Verified completion rate and false-success rate, with explicit denominators.
- Requirement coverage, regressions and defects found by independent evaluation.
- Human interventions, review effort and repair rounds per task.
- End-to-end time, model/token usage where available, compute and attributable cost.
- Correct escalation, unauthorized actions and hidden-data disclosure.
- Recovery success, lost work, duplicate remote actions and stale-result acceptance.
- Retrieval relevance, omissions, source accuracy, context cost and lesson usefulness.

Unknown cost or telemetry remains unknown, not zero. Failed/stopped trials remain
in the results. Publish sanitized summaries without exposing protected test material.

## Required failure scenarios

Exercise shell/subprocess boundary attacks, malicious retrieved instructions, forged
reports, missing tests, stale approvals, denied tools, changed issues, dependency
outages, exhausted budgets, lost ownership and concurrent starts. Inject crashes
before/after intent, external effect, result, audit append and checkpoint publication.
Verify safe stopping and reconciliation, not merely eventual success.

## Improvement and release

Maintain regression cases separately from harder capability tasks. Compare retrieval
on/off and approved lessons on/off where relevant; do not infer causality merely
because a successful run retrieved a lesson. Calibrate model-based review with human
judgment and deterministic checks. No evaluator agent may authorize release alone.

Record controller, host, model, prompt, tool, profile and memory snapshot versions.
Re-run affected evaluations when any changes. Publish a compatibility matrix and
limitations only for configurations actually tested. Agree release thresholds before
scoring trials; do not adjust them afterwards to turn a failure into a pass.

No state-of-the-art or superiority claim without a relevant, reproducible comparison.
Additional agents or infrastructure must earn their place through these results.

Basis: [Anthropic's agent-evaluation guidance](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents).
