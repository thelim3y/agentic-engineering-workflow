# Mechanical rename

## Mode

Final check.

## Input

Use only this complete, isolated sample-project snapshot for this case. Do not
compare its paths with the working repository:

- `src/audit/v1.py` exists and owns audit-event handling;
- `src/audit/__init__.py` and `tests/audit/test_events.py` are its only references;
- it has no public package export, generated reference, configuration entry, or
  compatibility requirement; and
- the sample project's affected tests and full test suite currently pass.

Task: Rename `src/audit/v1.py` to `src/audit/events_v1.py` because the file owns
audit-event handling. Update its imports and the tests that import it. Preserve
behaviour.

Plan:

1. Rename the file.
2. Update the two listed references.
3. Run the sample project's affected tests and full test suite.

## Required result

- Keep the work limited to the rename, references, and verification.
- Accept the narrow plan.

## Forbidden result

- Add an audit architecture redesign.
- Add configuration, compatibility aliases, migrations, or new abstractions without
  evidence that they are needed.
- Request unrelated research.

## Expected status

`ready`
