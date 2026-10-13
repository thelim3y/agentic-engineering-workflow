# Optional guidance

## Mode

Final check.

## Input

Use only this complete, isolated sample-project snapshot for this case. Do not
compare it with the working repository:

- the project has no audit-file implementation yet;
- its existing event schema and serializer produce one complete JSON object without
  a newline;
- its file interface appends one UTF-8 line to an already configured local file and
  returns either success or the append error;
- the configured directory, concurrency, durability level, and file lifecycle are
  already owned outside this task; and
- the required tests are successful append and read-back, plus propagation of an
  append failure without reporting success.

Task: Write each accepted audit event as one JSON line in the configured local
file, then verify it can be read back.

Plan:

1. Serialize one accepted event to one JSON line.
2. Append it to the configured file.
3. Test append and read-back behaviour and verify a failed append is returned
   without success.

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
