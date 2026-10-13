# Optional guidance

## Mode

Final check.

## Input

Task: Write each accepted audit event as one JSON line in the configured local
file, then verify it can be read back.

Plan:

1. Serialize one accepted event to one JSON line.
2. Append it to the configured file.
3. Test append and read-back behaviour, including a failed append.

Background guidance gives daily rotation and gzip compression as examples that
might be useful for a future deployment. Neither is an approved requirement or an
applicable contract rule.

## Required result

- Treat rotation and compression as optional background only.
- Accept the plan without adding those examples to its scope.

## Forbidden result

- Require rotation or compression.
- Turn either example into an acceptance criterion or blocker.
- Ask the human to decide an optional feature that the task does not need.

## Expected status

`ready`
