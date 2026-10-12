# Development rules

These are required rules for humans and LLMs developing this repository. They apply
to code, interfaces, configuration, tests, documentation and communication.

They are **not factory workflow policy**. Equivalent rules for the factory's own
agents and generated work require a separate decision, including their caveats.

## Minimise cognitive load

Keep everything as small, simple and clear as practical. Work actively to remove
unnecessary complexity. Separate responsibilities and minimise coupling. Structure
work so a human can understand, change, test and debug one part without holding the
whole system in their head.

- Optimise for understanding, not line count. Dense code and clever shortcuts can
  be shorter but harder to maintain.
- Use clear names, simple wording and consistent structure. Keep messages concise
  without hiding important facts, errors, risks or required actions.
- Make abstractions earn their place. Add layers, interfaces and configuration
  when they provide a concrete benefit, not merely the appearance of flexibility.

## Engineering rules

- **One responsibility per component.** Make ownership and boundaries clear.
  This does not require one tiny file or service per operation; avoid fragmentation.
- **Prefer explicit behaviour.** Make side effects, defaults and failure paths
  visible. Avoid surprising defaults and silent fallbacks.
- **Build what is needed.** Implement agreed requirements; leave speculative
  features and abstractions out of the change.
- **Treat design as a tested hypothesis.** Design documents record the current
  direction, not proof that it works. Implementation may expose incorrect assumptions,
  missing constraints or simpler solutions. Preserve required invariants, but revise
  the design when evidence warrants it. Never let code and documentation diverge silently.
- **Keep proposals separate.** Put unsettled alternatives in issues or ADRs with an
  explicit proposed status. Do not mix them into authoritative contract text; the word
  `proposed` alone is not a sufficient boundary there.
- **Keep changes focused.** Separate unrelated fixes, refactors and features.
- **Use deterministic tools where possible.** Use tools for mechanical checks;
  reserve judgement for questions those tools cannot establish.
- **Prove behaviour.** Test requirements and edge cases. Never weaken tests merely
  to make code pass.
- **Fail clearly.** Explain what failed, its impact and the next useful action.
- **Keep one source of truth.** Link to authoritative rules rather than copying
  them into other documents or prompts.
- **Preserve runner independence.** Core contracts and workflow policy must not
  depend on a named LLM, provider, model, host, CLI or SDK. Keep specifics in adapters.
- **Challenge assumptions with evidence.** Assess proposals independently, including
  the user's. Explain conflicts and trade-offs with facts or clear reasoning;
  distinguish evidence from judgement and uncertainty. Do not agree by default.
- **Write concise documents.** Get to the point in as few words as possible without
  losing necessary meaning. Remove filler and repetition.
- **Keep documentation accurate.** Distinguish implemented, verified,
  planned and unknown. A passing check supports only what it actually tested.

## Review question

Does this change make the system easier for a human to understand and safely modify?
If it adds unavoidable complexity, explain why and keep that complexity contained.
