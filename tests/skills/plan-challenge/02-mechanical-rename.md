# Mechanical rename

## Mode

Final check.

## Input

Task: Rename `src/audit/v1.py` to `src/audit/events_v1.py` because the file owns
audit-event handling. Update its imports and the tests that import it. Preserve
behaviour.

Plan:

1. Rename the file.
2. Update direct imports and test paths found by repository search.
3. Run the affected tests and the full test suite.

Repository inspection shows no public package export, generated reference, or
configuration entry for the old path.

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
