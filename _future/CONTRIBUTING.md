# Contributing benchmark cases

RunMismatch is dataset-first. A useful contribution is a well-evidenced failure case, not a large code change.

## Before submitting

A case should have:
- a public source URL;
- a pinned repository commit when possible;
- a clear symptom;
- an evidence-backed root cause;
- an explicit detectability decision;
- enough information to reproduce the relevant environment state.

## Never include secrets

Do not commit:
- API keys
- passwords
- tokens
- private environment-variable values
- private logs containing credentials

For environment variables, record only whether a variable is present, missing, or unknown.

## Prefer difficult truth over convenient truth

If the root cause cannot be established from repository + machine evidence, mark the case as non-detectable or unknown.

Do not convert an unresolved failure into a deterministic rule merely to make the benchmark easier.

## Case ID

Use the next available ID:

WRB-0001
WRB-0002
...

The evaluator will eventually enforce uniqueness and schema validity.
