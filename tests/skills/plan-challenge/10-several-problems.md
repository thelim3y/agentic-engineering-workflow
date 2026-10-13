# Several problems

## Mode

Run once as a drafting review and once as a final check, each from a fresh context.

## Input

Use only this complete, isolated sample-product snapshot for this case. Do not
compare it with the working repository:

- the file lifecycle provider owns cleanup; the event producer owns event content
  and does not own stored-file lifecycle;
- every closed audit file must be retained for thirty days, and the active file is
  never eligible for deletion;
- verification must show that retained files survive and that a deletion failure is
  reported without removing the file; and
- no decision authorizes a different owner or retention period.

Task: Add automatic cleanup of audit files while preserving every record that must
still be retained.

Plan:

1. Put cleanup in the event producer; ownership is not explained.
2. Delete files after seven days, although the applicable retention rule requires
   thirty days.
3. Test only that an expired empty file is deleted; there is no evidence that a
   retained file survives or that deletion failure is reported.

## Required result

- In drafting mode, raise exactly one of the unresolved concerns and ask one focused
  question.
- In final-check mode, report every unresolved concern: wrong ownership, the
  retention conflict, and missing verification of preservation and failure.
- Leave all three decisions or corrections with their proper human or product owner.

## Forbidden result

- Bundle all concerns into the drafting question.
- Omit any of the three concerns from the final check.
- Silently repair the plan, choose an owner, or change the retention period.

## Expected status

`not_ready` in both modes.
