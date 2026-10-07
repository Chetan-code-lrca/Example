# RunMismatch

RunMismatch is a dataset-first research project investigating whether public GitHub repositories contain actionable conflicts between their own Node.js/Python runtime declarations, whether those conflicts are already detected by existing tools, and whether the problem is broad enough to justify a deterministic diagnostic CLI. The project deliberately freezes its preregistered study protocol before data collection and does not add extraction or analysis code until the validation decision has been made.

## Research question

> How prevalent are actionable conflicts among repository-declared Node.js/Python runtime configurations in active public GitHub repositories, and how often are those conflicts already detected by existing tools?

## Protocol

The frozen protocol is copied byte-for-byte to [`protocol/PREREGISTRATION.md`](protocol/PREREGISTRATION.md).

**Timestamp anchor:** [Example commit 20ec39e40ed8b8a73a34c965c65468e685b0d9bf](https://github.com/Chetan-code-lrca/Example/commit/20ec39e40ed8b8a73a34c965c65468e685b0d9bf)

## STOP / PIVOT / BUILD

The following decision rules are copied from the operative v1.3 protocol without rewording:

### STOP

```text
N_multi_final < 150
OR
P_multi < 2%
```

### BUILD

```text
N_multi_final >= 150
AND
P_multi >= 5%
AND
D_owner >= 5
AND
M >= 2
AND
ToolCoverage < 50%
```

### PIVOT

PIVOT to the measurement study plus small static linter in every remaining case.

STOP, BUILD, and PIVOT are exhaustive and non-overlapping because STOP is evaluated first, BUILD second, and PIVOT is the complement.

## Protocol freeze

No protocol changes are allowed after Day 1. The frozen v1.3 protocol permits only clerical fixes before Day 1 that do not change eligibility, sampling, declaration parsing, scope assignment, conflict classification, harm criteria, tool detection, thresholds, sensitivity analyses, or decision rules. Any substantive later change must be recorded as a protocol deviation and excluded from the primary analysis.

## Current status

- Pre-data collection.
- No extraction implementation.
- No analysis implementation.
- No sampled-repository cases have been added.
- The v1.3 protocol is frozen.

## Repository structure

```text
data/
analysis/
protocol/
  PREREGISTRATION.md
  deviations.md
tests/
  fixtures/
src/
```

## Tools used

AI assistants helped draft the preregistration protocol. The protocol's substantive rules are frozen before data collection; AI assistance does not substitute for the preregistered evidence and verification process.

## License

MIT.
