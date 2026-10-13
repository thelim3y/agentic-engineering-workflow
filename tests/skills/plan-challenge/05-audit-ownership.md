# Audit ownership

## Mode

Drafting review.

## Input

Task: Ensure audit records contain no secrets.

Plan:

1. Add secret classification and redaction to the file audit provider.
2. Scan each event immediately before serialization.
3. Test the provider with API keys and access tokens.

Applicable shared rule: the producer or controller owns safe event content. The file
audit provider owns storage format, serialization, append, integrity, durability,
and recovery. It does not own secret classification.

## Required result

- Identify that the plan assigns secret classification to the wrong component.
- Keep safe event content with the producer or controller and file persistence with
  the provider.
- Ask the human to revise or split the work along that boundary.

## Forbidden result

- Approve secret scanning or redaction in the file provider.
- Move file persistence responsibilities to the producer.
- Design a secret detector.

## Expected status

`not_ready`
