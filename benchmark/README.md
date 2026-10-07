# Benchmark

This directory contains the versioned public "why doesn't it run?" corpus.

## Frozen benchmark policy

The first release will contain 15 cases selected before evaluating the reference implementation.

The selection must deliberately include:

- genuine detectable failures;
- compatible configurations where the correct result is silence;
- unresolved/non-detectable failures;
- mixed or conflicting declarations.

The benchmark must not be optimized after seeing implementation results.

## Case requirements

Each case must identify:

- repository URL;
- pinned commit when possible;
- public failure source;
- root cause and confidence;
- repository evidence;
- machine evidence;
- detectability;
- expected diagnosis.

See schema/case.schema.json.

## Selection bias controls

The initial corpus should not consist only of closed, easily solved issues.

The target mix includes:

- resolved/reproduced cases;
- unresolved cases;
- maintainer-confirmed cases;
- cases where the correct answer is "unknown".

## Metrics

The evaluator will report:

- true positives;
- false positives;
- false negatives;
- precision;
- recall;
- coverage of detectable cases;
- non-detectable cases;
- ambiguous cases.

The v0.1 build gate is **at least 8 correctly diagnosed detectable cases and at most 1 false positive** on the frozen 15-case set.
