# Missing requirement

## Mode

Drafting review.

## Input

Task: Add automatic deletion of expired local audit files. The task does not state
how long files must be retained.

Plan:

1. Delete audit files after 30 days.
2. Test deletion of files older than 30 days.

No applicable product document or configuration defines a retention period.

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
