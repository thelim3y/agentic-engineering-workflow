# Audit ownership

## Mode

Drafting review.

## Input

Use only this complete, isolated sample-product snapshot for this case. Do not
compare it with the working repository:

- the event producer creates event content;
- the controller accepts or rejects that content;
- the file audit provider owns only storage format, serialization, append,
  integrity, durability, and recovery; and
- the producer or controller owns secret classification and safe event content.

Task: Ensure audit records contain no secrets.

Plan:

1. Add secret classification and redaction to the file audit provider.
2. Scan each event immediately before serialization.
3. Test the provider with API keys and access tokens.

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
