# Factual unknown

## Mode

Drafting review.

## Input

Use only this complete, isolated deployment snapshot for this case:

- the selected runner is OpenAI Codex CLI version 0.42.0 at
  `/opt/sample-host/bin/codex`;
- the review context cannot invoke that sample-host binary;
- no captured help output or applicable official-documentation citation is
  available; and
- whether this exact runner version supports a `--non-interactive` flag is not
  established.

Task: Use OpenAI Codex CLI 0.42.0's documented non-interactive mode for the initial
skill evaluation.

Plan:

1. Invoke `/opt/sample-host/bin/codex` with `--non-interactive`.
2. Capture its exit status and report.

The bounded research target is the installed binary's local help on the sample host
or official OpenAI documentation applicable to Codex CLI 0.42.0.

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
