# Plan-challenge tests

These ten cases are protected inputs for the plan-challenge skill. The skill
implementer must not edit them. A changed product decision must return to the test
author instead of weakening a case.

Each case supplies the human's task and plan, the relevant facts, the review mode,
the required decision, forbidden decisions, and the expected status. Review the
skill against each case in a fresh context. Judge whether it made the required
decision; do not require exact wording.

Run the corpus check with:

```sh
python3 -B -m unittest discover -s tests/skills/plan-challenge -p 'test_*.py' -v
```

The corpus check verifies that all ten cases are present and complete. It also
requires `skills/plan-challenge/SKILL.md`, so it must fail before the skill exists.
It does not pretend that static text matching can prove an agent's behaviour.
