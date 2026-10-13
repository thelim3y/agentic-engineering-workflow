# Weak verification

## Mode

Drafting review.

## Input

Task: Append audit records without damaging records that are already durable. A
failed append must leave earlier records readable.

Plan:

1. Implement append.
2. Test that two successful appends can be read back in order.

The plan contains no failure injection or other evidence for the required failed
append behaviour.

## Required result

- Identify that the existing test proves only successful append and ordering.
- Ask for verification that a failed append preserves earlier durable records and
  leaves them readable.

## Forbidden result

- Report that the happy-path test proves the failure invariant.
- Add unrelated performance, concurrency, or storage requirements.
- Prescribe an implementation mechanism instead of the missing evidence.

## Expected status

`not_ready`
