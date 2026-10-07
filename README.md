# RunMismatch Benchmark

**A public benchmark for one question: why doesn't this repository run on my machine?**

RunMismatch is being built as a dataset-first project.

It records real repository failures, their confirmed root causes, the evidence available from the repository and machine, and whether a deterministic diagnostic can identify the problem without guessing.

> **Status: pre-v0.1 validation.**
>
> The benchmark is intentionally small and evidence-driven before any reference CLI is built.

## Why this exists

Environment-management tools help prevent drift. RunMismatch is for the cases where you already have a repository and need to understand why it does not run on the current machine.

The benchmark is designed to measure both **detection** and **silence**:

- Can the tool detect a real, reproducible mismatch?
- Does it avoid reporting compatible configurations as failures?
- Can it honestly say **unknown** when the repository does not contain enough evidence?

## Current validation gate

No reference CLI is being implemented yet.

The current pre-data study is a static prevalence study of repository-declared Node.js/Python runtime conflicts. The operative protocol is recorded in [PREREGISTRATION.md](PREREGISTRATION.md).

The study will only move to CLI implementation if the preregistered BUILD gate is satisfied after the frozen sample is collected. The earlier 15-case benchmark gate is retained only as historical planning.

## Dataset principles

1. **Real cases over synthetic failures.**
2. **Source provenance for every case.**
3. **Pinned repository commit whenever possible.**
4. **Root cause must be evidence-backed.**
5. **Non-detectable cases stay in the benchmark.**
6. **False positives are treated as a first-class failure.**
7. **Environment secrets are never collected.**
8. **The benchmark evaluator is deterministic and reproducible.**

## Planned structure

```
benchmark/          # historical/future failure corpus
fixtures/           # generated local parser fixtures
tools/              # deterministic declaration extractor + tests
rules/              # declarative diagnostic rules
schema/             # machine-readable schemas
```

## Current study scope

The validated extraction wedge is narrower:

- Node.js and Python runtime declarations
- comparable execution scopes
- semver / Python range normalization
- explicit CI matrix treatment
- conservative UNKNOWN handling
- cross-declaration conflict classification

Environment variables, ports, dependency resolution, Docker/system-library diagnosis, and automatic fixes are outside the current prevalence study.

## Contribution test

A stranger should be able to contribute a benchmark case in about 10 minutes:

1. Find a real failure with a public source.
2. Pin the repository and failure evidence.
3. Describe the root cause.
4. Mark what is and is not detectable from repository + machine evidence.
5. Add the case YAML.
6. Run schema validation.

## License

Dataset and code licensing will be finalized before the first public benchmark release.

## Project status

This repository is currently a staging repository. The GitHub repository name will be changed to the final project name before the first public release.


## Fixture tests

The repository includes a fixture-only extractor test runner. It generates the control/conflict fixtures locally and does not inspect sampled GitHub repositories.

Run:

```
python tools/test_fixtures.py
```
