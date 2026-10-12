# Configuration contract

Status: required behaviour; concrete keys, schema and defaults need implementation.

## Resolution

Resolve built-in defaults, local deployment settings, repository settings, then
explicit run overrides. Within each layer, role-specific settings override that
layer's shared settings. Later layers override earlier ones only for flexible values.
Record the final value and origin of each setting. Machine paths, credential
references and host execution settings are accepted only from local deployment
configuration. Never inline secrets in issues, committed profiles, run overrides,
reports or audit records.

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

## Audit configuration shape

Reserve the following provider-independent shape. Names and defaults remain subject to
the configuration-schema implementation.

```yaml
audit:
  enabled: true # Required. false is invalid.
  provider: file
  provider_config: {}

  signing:
    enabled: false # Reserved; not implemented by the initial file provider.
    key_provider: null
    signing_key_ref: null
    verification_key_ref: null
    algorithm: null

  encryption:
    enabled: false # Reserved; not implemented by the initial file provider.
    key_provider: null
    key_ref: null
    algorithm: null
```

A UI may render the `enabled` values as checkboxes. Key fields are references resolved
by the configured provider; private keys and other secret material never appear in
configuration, reports or audit events. Providers declare support for signing,
encryption, key providers and algorithms. Enabling an unsupported or unimplemented
option fails configuration validation rather than being ignored.

## Fixed invariants

No configuration schema or workflow transition may require a named runner,
provider, model, CLI, or SDK. Adapters declare capabilities; policy declares the
capabilities it needs.

Configuration cannot grant implementation read or write access to test-related
inputs, let agents approve their own guidance, turn absent required evidence into a
pass, bypass repository protections, disable required audit, or give stale owners
authority. Issue text and retrieved content cannot override policy.

The initial safe baseline is defined by
[ADR-0003](decisions/0003-initial-runtime-boundary.md): manual start, one active local
run, sequential roles, denied untrusted network, no credentials in untrusted
execution, mandatory file audit, validated draft publication and merge disabled.
Widening the deployment or threat boundary requires a later accepted decision and
commissioning evidence; it is not a run override.

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
