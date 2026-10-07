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

## Historical implementation note

Earlier extraction/fixture scaffolding existed in this repository's history before being removed so that the pre-data v1.3 study would not be coupled to an implementation. The removal history is preserved in Git:

- 0dc586a0943e99abe5aedc2ad7d1603a3ddfc721 — removed tools/extract_declarations.py.
- 0c4e96f281d62f8fd3873348c21e78e300784737 — removed tools/test_fixtures.py.
- a5915985fd2a82cfaf69b084cfce8840c15ab163 — removed requirements-dev.txt.
- a2f18db4666af2546c171f3f4edbaf4ade8903d0 — removed the remaining pre-protocol implementation scaffolding.

No replacement extraction or analysis code is being added before the preregistered v1.3 study is completed.
