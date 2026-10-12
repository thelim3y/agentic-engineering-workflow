# Configuration contract

Status: required behaviour; concrete keys, schema and defaults need implementation.

## Resolution

Resolve built-in defaults, then repository settings, then explicit run overrides.
Within each layer, role-specific settings override that layer's shared settings.
Later layers override earlier ones. Record the final value and origin of each setting.
Keep machine paths and secret references in local configuration; never inline secrets
in issues, committed profiles, reports or audit records.

Validate before claiming work. Reject unknown keys, invalid values, conflicts,
missing required choices and unsupported adapter capabilities with exact diagnostics.
Provide a configuration-check command showing sanitized effective values and their
sources. Its command syntax is not yet defined. Never invent permissive defaults.

## Configurable areas

- Issue provider/repository, trigger/state labels, ordering and shortlist size.
- Size assessment, notification and approval policy within planner constraints.
- Per-role runner/provider/model, context limits and visibility policy.
- Retry/dispute rounds, timeouts, resource limits, concurrency and total run budgets.
- Project verification profiles, required/optional lanes and justified skip policy.
- Retrieval sources/budgets/freshness and optional-context outage handling.
- Memory deployment/version, lesson applicability and feedback enablement.
- Checkpoint location/cadence/retention and recovery policy.
- Audit retention and access, within the declared immutability boundary.
- PR/base-branch, review criteria, merge mode and approval gates.

Manual start, oldest-first selection, required eligibility label and terminal output
are initial behaviour. Per-role settings inherit shared defaults. Default dispute
review is one round before escalation. Other numeric defaults remain explicit choices.

## Fixed invariants

No configuration schema or workflow transition may require a named runner,
provider, model, CLI, or SDK. Adapters declare capabilities; policy declares the
capabilities it needs.

Configuration cannot grant implementation test-writing access, let agents approve
their own guidance, turn absent required evidence into a pass, bypass repository
protections, disable required audit, or give stale owners authority. Test visibility
does not change test ownership. Issue text and retrieved content cannot override policy.

XL+ requires human approval; concerns at any size pause. Configuration defines sizing
criteria, not permission to erase that gate. No automatic model substitution. Any
intentional model change is explicit, recorded and checked for evidence/approval impact.

Changes during a run create a new effective configuration identity. Reassess affected
work and approvals before continuing. Restart/resume preserves accumulated budgets;
it cannot reset them to escape a limit. Budget extensions require an explicit,
recorded operator decision, not an agent request silently accepted as configuration.

## Validation examples

Test conflicting layers, unknown keys, missing models, unsupported visibility modes,
secret redaction, budget exhaustion, resumed counters and policy changes. Confirm
accepted flexible settings work without weakening fixed invariants.
