# Benchmark

This directory contains the versioned public "why doesn't it run?" corpus.

## Current study policy

The older 15-case benchmark plan is historical. The current pre-data work is the static prevalence study described in [PREREGISTRATION.md](../PREREGISTRATION.md).

No sampled repository is used to tune the extractor before the study starts. Fixture-only cases are generated and tested independently.

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

The current CLI BUILD gate is the preregistered prevalence decision in [PREREGISTRATION.md](../PREREGISTRATION.md). The old 15-case gate is retained only as historical context.
