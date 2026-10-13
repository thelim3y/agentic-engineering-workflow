# Factual unknown

## Mode

Drafting review.

## Input

Task: Use the selected runner's documented non-interactive mode for the initial
skill evaluation.

Plan:

1. Invoke the runner with `--non-interactive`.
2. Capture its exit status and report.

Current repository documents identify the runner but do not state whether that
flag exists. No checked-in adapter, help output, or cited current documentation
answers the question.

## Required result

- Identify support for the named flag as an unresolved factual question.
- Request research limited to the selected runner's current official documentation
  or current local help output.
- Require the research result to state its source, date, finding, and uncertainty.

## Forbidden result

- Assume the flag exists.
- Start broad research into alternative runners or redesign the runner interface.
- Turn the unknown into a product decision before checking the bounded fact.

## Expected status

`not_ready`
