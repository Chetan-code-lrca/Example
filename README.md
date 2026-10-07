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

## v0.1 build gate

The first benchmark snapshot will contain 15 real-world cases.

We will build the reference implementation only if it achieves, on the frozen 15-case set:

- at least **8 correctly diagnosed detectable cases**
- at most **1 false positive**

We will publish precision, recall, false negatives, non-detectable cases, and ambiguous cases rather than a single accuracy number.

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
benchmark/
  cases/          # real failure cases
  environments/   # redacted machine snapshots
rules/             # declarative diagnostic rules
schema/            # machine-readable schemas
evaluator/         # benchmark scoring
```

## Current scope

The initial wedge is deliberately narrow:

- Node.js version/range declarations
- Python version/range declarations
- environment-variable presence
- host/container port mapping and conflicts
- declared runtime/tool presence

No automatic environment modification is planned for v0.1.

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
