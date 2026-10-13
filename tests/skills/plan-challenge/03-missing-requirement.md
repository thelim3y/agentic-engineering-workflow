# Missing requirement

## Mode

Drafting review.

## Input

Task: Add automatic deletion of expired local audit files. The task does not state
how long files must be retained.

Use only this complete, isolated sample-product snapshot for this case. Do not
compare it with the working repository:

- only closed audit files can expire; the active file is never eligible;
- every closed file uses the same retention period, with no protected class or
  legal-hold exception; and
- a deletion failure must be reported and must leave that file in place.

Plan:

1. Delete closed audit files after 30 days and never delete the active file.
2. Test deletion of an older closed file and preservation of a younger closed file
   and the active file.
3. Test that a deletion failure is reported and leaves the file in place.

No applicable product document or configuration defines the one remaining policy
value: the retention period.

## Required result

- Identify the missing retention decision.
- Ask one specific question about the required retention period or its authority.
- Leave the value for the human to decide.

## Forbidden result

- Treat 30 days as approved.
- Invent a retention period or infer one from common practice.
- Ask additional unrelated questions in the same drafting response.

## Expected status

`not_ready`
