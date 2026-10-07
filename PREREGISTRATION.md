# PREREGISTRATION.md

# RunMismatch Static Prevalence Study — Preregistration

**Protocol status:** Pre-data-collection.  
**Protocol date:** 2026-10-07.  
**Protocol version:** 1.0.  
**Time-box:** 7 calendar days from protocol commit.  
**Random seed:** 20261007.

> **[OPINION]** This preregistration is frozen before data collection. After the first sampled repository is inspected, no threshold, sampling rule, conflict definition, scope rule, or tool-detection rule may be changed for the primary analysis.

## 1. Research question

**[OPINION]** The study asks:

> How prevalent are actionable conflicts among repository-declared Node.js/Python runtime configurations in active public GitHub repositories, and how often are those conflicts already detected by existing tools?

**[FACT]** npm already checks `package.json` engine compatibility, and third-party tools such as `check-engine` and `check-engines` also check engine constraints against the current environment. See the verified tool references in Section 12.

**[OPINION]** The study therefore does not assume that runtime-version checking is novel. Its primary hypothesis is narrower: cross-declaration consistency may be an under-served problem.

## 2. Primary outcomes

### 2.1 P_all

**[OPINION]** Define:

`P_all = C / N_all`

where:

- `N_all` = all sampled repositories, including repositories with zero runtime declarations.
- `C` = sampled repositories containing at least one actionable conflict.

**[OPINION]** `P_all` is the headline descriptive prevalence across the entire sampled corpus, but it is **not** the product kill-gate statistic.

### 2.2 P_multi

**[OPINION]** Define:

`P_multi = C / N_multi`

where:

- `N_multi` = sampled repositories containing at least two authoritative runtime declarations for the same runtime family.
- `C` = sampled repositories containing at least one actionable conflict.

**[OPINION]** `P_multi` is the **headline statistic for the product kill gate** because a repository with zero or one runtime declaration has no cross-declaration conflict opportunity. Using `P_multi` avoids diluting the signal with repositories that cannot exhibit the target problem.

**[OPINION]** `P_all` will always be reported alongside `P_multi` so that the study does not hide how common the issue is across all sampled repositories.

## 3. Actionable conflict

**[OPINION]** An actionable conflict is **two or more authoritative declarations for the same runtime family and execution scope that are mutually incompatible and whose resolution would change the runtime/tool version a developer, CI job, or deployment context should use.**

**[OPINION]** A conflict between two declarations that are explicitly scoped to different execution contexts is not counted as a conflict.

Example:

- local development Node 20
- Docker production Node 22

**[OPINION]** This is not automatically a conflict because the contexts differ.

## 4. Declaration sources

**[FACT]** Docker's Dockerfile syntax defines `FROM` as the base image instruction and permits an optional image tag or digest. [Dockerfile reference](https://docs.docker.com/reference/dockerfile/)

**[FACT]** GitHub's `setup-node` supports `node-version` and `node-version-file`, including files such as `.nvmrc`, `.node-version`, `.tool-versions`, `mise.toml`, and `package.json`. It also supports version values through workflow matrices. [setup-node advanced usage](https://github.com/actions/setup-node/blob/main/docs/advanced-usage.md)

**[FACT]** GitHub's `setup-python` supports `python-version`, `python-version-file`, and matrix testing. [setup-python advanced usage](https://github.com/actions/setup-python/blob/main/docs/advanced-usage.md)

**[FACT]** tox supports Python environment selection through `envlist` and `basepython`; newer tox versions also support `base_python_file`. [tox configuration](https://tox.wiki/en/stable/how-to/usage.html) [tox reference](https://tox.wiki/en/4.64.2/reference/config.html)

**[FACT]** Heroku's current documentation says `runtime.txt` is deprecated and recommends `.python-version`; Heroku's classic Python buildpack still documents `runtime.txt` as an input with precedence above `.python-version`. [Heroku runtime docs](https://devcenter.heroku.com/articles/python-runtimes) [Heroku buildpack](https://github.com/heroku/heroku-buildpack-python)

**[FACT]** Python packaging documentation says Python-version classifiers are used for PyPI searching/browsing and that `requires-python` is the field intended to restrict installable Python versions. [PyPA packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

### 4.1 Authoritative declarations

**[OPINION]** The following are authoritative for conflict analysis, but only within the scope stated:

| Source | Authority | Execution scope |
|---|---|---|
| `package.json` `engines.node`, `engines.npm` | Authoritative compatibility declaration | Project/package scope |
| `package.json` `devEngines.runtime` | Authoritative development-runtime declaration | Project/package scope |
| `package.json` `volta.node` | Authoritative pinned runtime declaration | Project/workspace scope |
| `.nvmrc` | Authoritative runtime selection declaration | Repository/local development scope |
| `.node-version` | Authoritative runtime selection declaration | Repository/local development scope |
| `.python-version` | Authoritative runtime selection declaration | Repository/local development scope |
| `.tool-versions` | Authoritative tool-version declaration | Repository/local development scope |
| `mise.toml` tool declarations | Authoritative tool-version declaration | Repository/tool-environment scope |
| Dockerfile `FROM node[:tag]` / `FROM python[:tag]` / digest | Authoritative container base-runtime declaration | Container build/run scope |
| GitHub Actions `setup-node` `node-version` | Authoritative CI runtime declaration | Individual CI job/matrix leg |
| GitHub Actions `setup-node` `node-version-file` | Authoritative CI runtime declaration after file resolution | Individual CI job/matrix leg |
| GitHub Actions `setup-python` `python-version` | Authoritative CI runtime declaration | Individual CI job/matrix leg |
| GitHub Actions `setup-python` `python-version-file` | Authoritative CI runtime declaration after file resolution | Individual CI job/matrix leg |
| `tox.ini` `envlist` / `basepython` | Authoritative tox test-environment declaration | Individual tox environment |
| `runtime.txt` | Authoritative for Heroku deployment context | Heroku build/deploy scope |

**[OPINION]** A declaration with an unversioned or moving value such as a Docker image tag of `latest` remains authoritative but may be classified as non-comparable rather than converted into a false conflict.

### 4.2 Informational declarations

**[OPINION]** The following do not create conflicts by themselves:

- `pyproject.toml` Python classifiers.
- README prose.
- Comments.
- Issue/PR text.
- CI log text.
- Arbitrary documentation stating a preferred version without a machine-readable declaration.

**[FACT]** PyPA explicitly states that Python-version classifiers are for searching/browsing and that `requires-python` is the actual installation constraint. [PyPA packaging guide](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)

## 5. Conflict rules

**[OPINION]** Apply the following rules in this order:

1. Parse each authoritative declaration into a normalized constraint or selected version.
2. Assign every declaration to an execution scope.
3. Compare declarations only within the same runtime family.
4. Compare declarations that apply to the same execution scope.
5. If two authoritative declarations are compatible, record **no conflict**.
6. If two authoritative declarations are mutually incompatible, record **one conflict for the repository**.
7. If the scope or semantics cannot be established without unsupported inference, record **ambiguous** and do not count it as a conflict.
8. A repository may contain multiple conflicting pairs, but it contributes at most one repository to `C`.
9. Dependency/transitive-engine requirements are excluded from this study because they require dependency resolution.
10. Machine versions are not needed for the static prevalence study.

**[OPINION]** Conflict analysis is declaration-versus-declaration; it is not a runtime-failure prediction.

## 6. Sampling plan

### 6.1 Population

**[OPINION]** The target population is public GitHub repositories whose primary language is JavaScript or Python, excluding forks and archived repositories.

### 6.2 Sample size

**[OPINION]** Target sample:

- 200 JavaScript repositories.
- 200 Python repositories.
- 400 total repositories.

**[FACT]** A binomial proportion with `n=400` has a worst-case two-sided 95% Wilson half-width of about 4.9 percentage points when the observed proportion is near 50%.

**[OPINION]** This is adequate for a one-week descriptive product-triage study, not a definitive estimate of all GitHub repositories.

**[OPINION]** `P_multi` will use its exact observed denominator `N_multi`; its Wilson interval will therefore be reported separately from the `P_all` interval.

### 6.3 Fixed star bands

**[OPINION]** Each language uses these fixed star bands:

1. 100–999 stars.
2. 1,000–4,999 stars.
3. 5,000–19,999 stars.
4. 20,000+ stars.

**[OPINION]** Target allocation is 50 repositories per band per language.

**[OPINION]** If a band has fewer than 50 eligible repositories, all eligible repositories in that band are included and the shortfall is **not** reallocated to another band.

### 6.4 Candidate-pool queries

**[OPINION]** Use GitHub repository search with language, star-band, `fork:false`, and `archived:false` filters equivalent to:

`language:JavaScript stars:100..999 fork:false archived:false`

and analogous queries for the other three JavaScript bands and four Python bands.

**[OPINION]** The exact query strings, retrieval timestamp, result counts, and any GitHub pagination limits encountered must be recorded before sampling.

### 6.5 Seeded selection

**[OPINION]** For each language and star band:

1. Freeze the eligible candidate pool at the recorded retrieval timestamp.
2. Sort candidate repositories by canonical `owner/name`.
3. Seed the PRNG with `20261007`.
4. Sample without replacement.
5. Record the seed and the selected repository list.
6. Do not replace a selected repository because its contents are inconvenient to inspect.

**[OPINION]** If a selected repository becomes unavailable during the week, mark it unavailable and retain the observed denominator rather than substituting another repository.

### 6.6 Repositories with zero declarations

**[OPINION]** Keep repositories with zero supported authoritative runtime declarations in the sample.

They:

- remain in `N_all`,
- do not enter `N_multi`,
- cannot contribute to `C`.

## 7. Monorepos

**[OPINION]** The repository remains the sampling unit, but declarations are analyzed by execution scope.

**[OPINION]** A repository is classified as a monorepo when it contains a root workspace/monorepo declaration or two or more distinct project/package roots with supported runtime manifests.

**[OPINION]** For monorepos:

- Treat each independently runnable package/project directory as a separate execution scope.
- Keep the repository as one sampling unit.
- Compare declarations only when their standard semantics place them in the same scope.
- Record the number of runtime scopes.
- A repository with any actionable conflict contributes one to `C`, regardless of the number of conflicting scopes.
- If inheritance between root and child declarations cannot be established without unsupported inference, classify that relationship as ambiguous rather than forcing a conflict.

**[OPINION]** This conservative rule is intended to reduce false positives from legitimate multi-project repositories.

## 8. Exact fields to record

**[OPINION]** Record the following for every sampled repository:

```yaml
repository:
  owner:
  name:
  url:
  primary_language:
  stars_at_sampling:
  forks_at_sampling:
  archived:
  fork:
  last_default_branch_commit:
  monorepo:

sampling:
  language_stratum:
  star_band:
  seed:
  pool_retrieved_at:
  selected_by_rng:

declarations:
  count_authoritative:
  count_authoritative_node:
  count_authoritative_python:
  items:
    - file:
      line_or_key:
      runtime_family:
      declaration_type:
      raw_value:
      normalized_value:
      execution_scope:
      authority:

classification:
  has_zero_declarations:
  is_multi_declaration:
  conflict_count:
  actionable_conflict: true|false
  ambiguous_relationships:

harm:
  issue_or_pr_version_mismatch_reference: true|false
  ci_version_mismatch_reference: true|false
  evidence_urls:

tool_coverage:
  mise_doctor:
  check_engine:
  check_engines:
  npm_install_checks:
  installed_check:
  npm_check_engines:
```

**[OPINION]** Do not record secrets, environment-variable values, authentication material, or private repository data.

## 9. Secondary harm measure

**[OPINION]** Among repositories classified as conflicting, record whether the repository has public evidence within the previous 24 months that a version mismatch caused or contributed to developer/CI pain.

**[OPINION]** A repository counts as having harm evidence when at least one public issue, pull request, or CI failure explicitly references a runtime/tool version mismatch, incompatibility, unsupported version, or equivalent diagnosis.

### 9.1 Issue/PR search method

**[OPINION]** For each conflicting repository, search repository-scoped GitHub issues and pull requests for combinations of these terms:

```text
"node version"
"python version"
"version mismatch"
"unsupported node"
"unsupported python"
"requires node"
"requires-python"
"engines.node"
"EBADENGINE"
".nvmrc"
".node-version"
".python-version"
".tool-versions"
"wrong node"
"wrong python"
"CI node"
"CI python"
```

**[OPINION]** Inspect matching issues/PRs manually and count evidence only when the text explicitly connects the failure/problem to a version mismatch or incompatible runtime selection.

### 9.2 CI search method

**[OPINION]** For GitHub Actions, inspect failed workflow runs in the previous 24 months and search job output/annotations for the same version-mismatch terms.

**[OPINION]** A generic failed CI run with no explicit runtime-version mismatch reference does not count as harm evidence.

### 9.3 Harm statistic

**[OPINION]** Report:

`H = conflicting repositories with qualifying harm evidence / conflicting repositories`.

**[OPINION]** `H` is secondary evidence and is not itself a build/kill gate.

## 10. Existing-tool coverage test

### 10.1 Definition of "detect"

**[OPINION]** An existing tool is credited with detecting a conflict only when, using the repository state and documented command/interface, it produces a user-visible finding that identifies the same incompatibility at approximately the same semantic level as the study classification.

**[OPINION]** The following do **not** count as detection of a declaration conflict:

- merely selecting one runtime,
- merely installing a missing runtime,
- warning that the current runtime violates one constraint without identifying the conflicting repository declarations,
- resolving a transitive dependency problem that is outside this study,
- requiring manual interpretation that the two declarations disagree.

### 10.2 Test procedure

**[OPINION]** For every observed actionable conflict:

1. Reproduce the exact repository revision used for the observation.
2. Run each applicable tool with its documented/default command.
3. Do not edit the repository to help the tool.
4. Record stdout/stderr/exit status.
5. Mark `DETECTED` only if the tool identifies the conflict under Section 10.1.
6. Otherwise mark `NOT_DETECTED`.
7. If the tool does not apply to that runtime or declaration type, mark `NOT_APPLICABLE`.

**[OPINION]** The primary existing-tool coverage statistic is:

`ToolCoverage = conflicting repositories detected by >=1 tested tool / conflicting repositories tested`.

### 10.3 Verified tool capabilities

**[FACT]** `check-engine` reads a `package.json` engine object and validates the local system against the declared tool requirements. [npm](https://www.npmjs.com/package/check-engine)

**[FACT]** `check-engines` verifies engine versions against semver constraints in `package.json`. [npm](https://www.npmjs.com/package/check-engines)

**[FACT]** npm's `npm-install-checks` library checks `engines.node`/`engines.npm`, platform fields, and `devEngines` against the current system. [npm](https://www.npmjs.com/package/npm-install-checks)

**[FACT]** `installed-check` checks installed modules against `package.json` requirements and can check whether installed dependencies have stricter engine requirements; it also covers workspaces. [npm](https://www.npmjs.com/package/installed-check)

**[FACT]** `npm-check-engines` checks whether dependency engine requirements are compatible with a project's supported engines. [GitHub](https://github.com/jgillich/npm-check-engines)

**[FACT]** mise documentation recommends using `mise doctor` and related commands when diagnosing wrong tool versions, configuration sources, and PATH conflicts. [mise troubleshooting](https://mise.jdx.dev/troubleshooting.html)

**[FACT]** Volta pins project Node and package-manager versions in `package.json` and automatically uses the pinned version in the project context. [Volta guide](https://docs.volta.sh/guide/understanding)

**[OPINION]** Volta is treated as an environment-management baseline, not presumed to be a declaration-conflict detector.

## 11. Statistical analysis

### 11.1 Wilson intervals

**[OPINION]** For `P_all` and `P_multi`, report a two-sided 95% Wilson interval.

For an observed proportion `p=x/n`:

```text
center = (p + z²/(2n)) / (1 + z²/n)

half_width =
  z / (1 + z²/n) *
  sqrt( p(1-p)/n + z²/(4n²) )

where z = 1.96
```

**[FACT]** With 400 observations, the worst-case Wilson half-width is approximately 4.9 percentage points.

**[FACT]** A perfect 30/30 proportion has a two-sided 95% Wilson lower bound of about 88.6%, so a 30-case benchmark cannot statistically establish a population rate above 90%.

**[OPINION]** The study will report point estimates and intervals without pretending that this one-week sample is a random sample of every GitHub repository.

### 11.2 No post-hoc threshold changes

**[OPINION]** Thresholds, definitions, sample allocation, star bands, search terms, harm criteria, and tool-detection criteria are fixed by this document.

**[OPINION]** Any deviation caused by unavailable repositories, GitHub limitations, or tool incompatibility must be documented as a protocol deviation and excluded from primary scoring where necessary; it must not trigger retrospective reclassification.

## 12. Pre-registered decision rules

**[OPINION]** These rules are mutually exclusive and exhaustive.

Let:

- `N_multi` = number of sampled repositories with at least two authoritative runtime declarations for the same runtime family.
- `P_multi` = `C / N_multi`.
- `D` = number of distinct sampled repositories containing at least one actionable conflict.
- `ToolCoverage` = fraction of conflicting repositories detected by at least one tested existing tool.

### STOP

**[OPINION]** STOP the standalone CLI project if **any** of these conditions holds:

```text
N_multi < 100
OR
P_multi < 2%
OR
D < 5
```

**[OPINION]** Interpretation: there is not enough observed multi-declaration exposure, prevalence, or distinct-repository evidence to justify a standalone CLI.

### BUILD

**[OPINION]** BUILD a first CLI prototype only when **all** conditions hold:

```text
N_multi >= 100
AND
P_multi >= 5%
AND
D >= 20
AND
ToolCoverage < 50%
```

**[OPINION]** Interpretation: the problem is common enough in multi-declaration repositories, spans enough independent projects, and is insufficiently covered by tested alternatives.

### PIVOT

**[OPINION]** PIVOT to a measurement study plus a small static linter when neither STOP nor BUILD applies.

**[OPINION]** Because STOP and BUILD are defined as complete Boolean conditions and PIVOT is their complement after STOP is evaluated, there is no numerical gap between outcomes.

## 13. What the possible pivot means

**[OPINION]** A PIVOT result means the repository evidence is interesting enough to preserve as a dataset/linter, but not strong enough to justify a standalone runtime-diagnosis CLI.

**[OPINION]** The likely pivot target is a small static analyzer that reports:

```text
Repository declaration conflict
    ↓
file A + constraint
file B + constraint
scope
    ↓
recommended human resolution
```

**[OPINION]** Dependency resolution, automatic environment installation, Docker/system-library diagnosis, and application debugging remain outside the study.

## 14. One-week schedule

**[OPINION]** The study is limited to seven calendar days:

### Day 1
- Freeze this protocol.
- Freeze candidate pools.
- Record retrieval timestamps and seed.
- Draw samples.

### Day 2
- Record repository metadata.
- Identify runtime declarations.

### Days 3–4
- Normalize declarations.
- Classify scopes.
- Classify conflicts and ambiguous cases.
- Run duplicate checks.

### Day 5
- Perform issue/PR/CI harm search.
- Recheck conflict classifications.

### Day 6
- Run existing-tool coverage tests on every conflict where the tool applies.
- Preserve raw outputs.

### Day 7
- Compute `P_all`, `P_multi`, Wilson intervals, `D`, harm `H`, and `ToolCoverage`.
- Apply the pre-registered STOP/PIVOT/BUILD decision.
- Publish the raw dataset and analysis.

**[OPINION]** Data collection ends after Day 6; Day 7 is analysis only.

## 15. Data-quality rules

**[OPINION]** Every repository observation must preserve:

- repository URL,
- sampling timestamp,
- star band,
- star count at sampling,
- selected commit,
- declaration file paths,
- exact declaration text/value,
- normalized interpretation,
- scope,
- conflict classification,
- ambiguity notes where applicable.

**[OPINION]** No repository may be reclassified solely because its classification changes the STOP/PIVOT/BUILD result.

**[OPINION]** When an interpretation is genuinely uncertain, classify it as ambiguous and do not count it as an actionable conflict.

## 16. Expected final deliverable

**[OPINION]** The one-week study output must contain:

```text
data/
  repositories.csv
  declarations.csv
  conflicts.csv
  harm.csv
  tool_coverage.csv

analysis/
  prevalence.md
  prevalence.json
  wilson_intervals.json

protocol/
  PREREGISTRATION.md
  deviations.md
```

**[OPINION]** The final report must state:

- `N_all`
- `N_multi`
- `C)
- `D)
- `P_all)
- `P_multi)
- 95% Wilson intervals
- harm proportion `H)
- existing-tool coverage
- final STOP/PIVOT/BUILD result
- any protocol deviations

## 17. Final pre-study decision

**[OPINION]** The best current strategy is **not to build the CLI now**.

**[OPINION]** The best immediate artifact is a **measurement study with a small static linter/data extractor**. The CLI becomes justified only if the pre-registered BUILD condition is satisfied.

**[FACT]** Existing tooling already covers substantial portions of simple engine checking and runtime selection: npm engine checks, `check-engine`, `check-engines`, `npm-install-checks`, dependency-engine checkers, mise diagnostics, and Volta project pinning. [npm check-engine](https://www.npmjs.com/package/check-engine) [npm check-engines](https://www.npmjs.com/package/check-engines) [npm-install-checks](https://www.npmjs.com/package/npm-install-checks) [mise troubleshooting](https://mise.jdx.dev/troubleshooting.html) [Volta guide](https://docs.volta.sh/guide/understanding)

**[OPINION]** The study is therefore testing a specific remaining hypothesis—cross-declaration conflict prevalence and coverage—not assuming a vacant product category.

## 18. Protocol freeze

**[OPINION]** No primary-analysis criterion in this document may be changed after the first repository is inspected.

**[OPINION]** Any proposed change must be recorded in `deviations.md`, dated, justified, and excluded from the primary analysis unless it merely corrects a clerical/data-entry error without changing eligibility, classification, or outcome definitions.


---
# Version 1.1 amendment — pre-data

**Protocol version:** 1.1  
**Amendment date:** 2026-10-07  
**Status:** Pre-data; no repository from the study has been inspected.

## A1. Decision-rule reconciliation

**[FACT]** v1.0 required both `P_multi >= 5%` and `D >= 20`.

**[FACT]** At `P_multi = 5%`, observing `D = 20` requires at least `N_multi = 400` because 5% of 400 is 20.

**[OPINION]** This is mathematically consistent, but it means the previous minimum exposure of 150 comparable repositories was insufficient to make both thresholds attainable at the boundary prevalence.

**[OPINION]** v1.1 therefore separates exposure sufficiency from the product decision:
1. Continue sampling until `N_multi >= 150` unless the hard cap or seven-day time-box is reached.
2. Do not stop merely when `N_multi = 150`.
3. If `P_multi >= 5%` but `D < 20`, continue sampling while the cap permits.
4. BUILD still requires `P_multi >= 5%` and `D >= 20` plus low existing-tool coverage.
5. At exactly 5% prevalence, BUILD cannot occur before approximately `N_multi = 400`.
6. At `N_multi = 150`, BUILD requires at least 20 conflicts, or 13.34% prevalence.
7. This is intentional: the study requires both prevalence and replication across distinct repositories.

**[OPINION]** `D >= 20` is a replication requirement, not a prevalence substitute.

## A2. Sequential sampling and cap

**[OPINION]** Replace the fixed 400-repository target with sequential sampling.

- Minimum comparable-declaration exposure: `N_multi >= 150`.
- Hard cap: `N_all <= 1000` sampled repositories.
- Continue sampling after 150 when needed to resolve the preregistered decision.
- Stop at the earliest point at which:
  - a STOP condition is mathematically irreversible under the remaining cap;
  - all BUILD conditions are satisfied;
  - `N_all = 1000`;
  - seven calendar days have elapsed.
- If the cap/time-box is reached without BUILD, apply the final STOP/PIVOT rules below.

**[OPINION]** This avoids declaring low prevalence merely because the first 150 comparable repositories contain few conflicts.

## A3. Exhaustive final decision rules

**[OPINION]** Apply exactly one outcome in this order.

### STOP

STOP the standalone CLI if either:

`
N_multi < 150
AND
the 1000-repository cap or seven-day time-box was reached

OR

N_multi >= 150
AND
P_multi < 2%
`

### BUILD

BUILD the CLI prototype only if all are true:

`
N_multi >= 150
AND
P_multi >= 5%
AND
D >= 20
AND
ToolCoverage < 50%
`

### PIVOT

PIVOT to a measurement study plus small static linter in every remaining case.

**[OPINION]** STOP, BUILD, and PIVOT are exhaustive and non-overlapping because STOP is evaluated first, BUILD second, and PIVOT is the complement.

**[OPINION]** The interval `2% <= P_multi < 5%` is deliberately a pivot zone. The 5% threshold is an engineering/product threshold, not a claim of statistical significance.

## A4. GitHub search pools and the 1,000-result ceiling

**[FACT]** GitHub documents repository search by star ranges and the `pushed` qualifier. citeturn0search1turn0search3

**[OPINION]** Never freeze a candidate pool by taking the first 1,000 results of an over-cap query.

For each language:

1. Start with the fixed v1.0 star bands.
2. Add `fork:false`, `archived:false`, and `pushed:>=YYYY-MM-DD`, where the date is exactly 12 months before pool freeze.
3. If a query returns fewer than 1,000 results, freeze that result set.
4. If it reaches the search ceiling, split its integer star interval into two non-overlapping ranges and query both.
5. Recursively split any range that still reaches the ceiling.
6. Deduplicate by canonical `owner/name`.
7. Record every leaf query, timestamp, result count, and split boundary.

**[OPINION]** Split boundaries are determined only by the search ceiling, never by runtime declarations or conflict status. This prevents declaration-dependent sampling.

**[OPINION]** If a single integer star value itself remains over the ceiling and the chosen GitHub search interface provides no deterministic secondary partition, that star value is recorded as an unresolvable stratum and excluded rather than truncated.

## A5. Activity filter

**[FACT]** GitHub documents `pushed` as the qualifier for repositories updated by a push after a specified date. citeturn0search1

**[OPINION]** Eligibility requires:
`
public
fork:false
archived:false
pushed_at >= pool_freeze_date - 12 months
`

Record the exact `pushed_at` value returned at pool freeze.

## A6. Revised N_multi

**[OPINION]** `N_multi` is the number of sampled repositories containing two or more authoritative runtime declarations for the same runtime family **within a comparable execution scope**.

Examples:
- `.nvmrc` + `package.json engines.node` for the same local project scope: comparable.
- `.python-version` + `pyproject.toml requires-python` for the same Python project scope: comparable.
- Production Docker Node 22 + local-development `.nvmrc` Node 20: not comparable merely because both are in one repository.
- Root and child declarations are comparable only when repository semantics establish that they govern the same execution scope.

**[OPINION]** A repository enters `N_multi` once if at least one runtime family/scope contains 2+ comparable authoritative declarations.

## A7. CI matrix legs versus engines

**[OPINION]** A GitHub Actions matrix creates separate CI execution scopes.

Example:
`
strategy:
  matrix:
    node: [18, 20, 22]
steps:
  - uses: actions/setup-node
    with:
      node-version: ${{ matrix.node }}
`

This is three CI runtime selections, not a single declaration.

**[OPINION]** Compare a root `package.json engines.node` constraint against each CI leg only when that job executes the same project/package scope.

Rules:
1. Each matrix leg is a separate CI scope.
2. A matrix containing 18, 20, and 22 is not itself a conflict.
3. `engines.node >=20` versus CI Node 18 is a conflict for that scope.
4. `engines.node >=20` versus CI Node 20 or 22 is not a conflict.
5. Explicit expected-failure/compatibility-test legs are not conflicts when that status is machine-readable.
6. If expected-failure semantics cannot be established, classify as ambiguous.

## A8. Second existing-tool metric

**[OPINION]** Add `OwnMachineFailureCoverage`:

`
conflicting repositories where an applicable tool surfaces
the same conflict as an error/failure in the project's own
machine context
/
tested conflicting repositories
`

**[OPINION]** A failure means a non-success exit status or explicitly documented error/failure result identifying the relevant runtime incompatibility. A warning alone does not count.

Report both:
- `ToolCoverage`: any qualifying user-visible detection.
- `OwnMachineFailureCoverage`: qualifying detection surfaced as failure/error in the project's own machine context.

**[OPINION]** BUILD uses `ToolCoverage`; the second metric is a secondary user-impact measure.

## A9. Exact PRNG and library

**[FACT]** Python's `random.Random` uses Mersenne Twister, and `random.sample` samples without replacement. citeturn0search4turn0search6

**[OPINION]** Primary sampling environment:
`
Python 3.12.15
stdlib random.Random
PRNG core: MT19937 / Mersenne Twister
seed: 20261007
sampling: Random.sample(population, k)
`

Sort candidates by canonical `owner/name` before sampling. Record the exact interpreter version. Use one documented deterministic seed-derivation method for strata and commit it before sampling.

## A10. Ten-percent second-rater check

**[OPINION]** A second independent rater reviews 10% of sampled repositories, rounded up, with a minimum of 20 repositories.

The second rater independently records declarations, comparable scope, `N_multi` eligibility, conflict classification, harm evidence, and applicable tool detection.

The primary rater's labels remain hidden until the independent record is complete.

Report agreement separately for:
`
N_multi eligibility
conflict classification
harm classification
tool detection
`

Disagreements are documented and adjudicated using the frozen definitions.

## A11. Same-runtime harm requirement

**[OPINION]** Harm evidence counts only when the issue, PR, or CI failure concerns the **same runtime family and comparable execution scope** as the observed conflict.

Node conflict + Node-version failure: qualifying.  
Python conflict + unrelated Java failure: non-qualifying.  
Node conflict + generic dependency failure without a Node-version connection: non-qualifying.

The existing 24-month harm-search window remains unchanged.

## A12. Verified and unverified tool claims

**[FACT]** `check-engine` says it uses the `engines` object in `package.json` to validate installed tools and supports Node.js, npm, Yarn, and pnpm among other tools. citeturn0search0

**[FACT]** `check-engines` says it verifies engine versions against semver constraints in `package.json`. citeturn0search8

**[FACT]** npm's `npm-install-checks` exposes checks for `engines.node`, `engines.npm`, platform fields, and `devEngines`, with engine failures represented as errors. citeturn0search5turn0search12

**[FACT]** `npm-check-engines` describes checking whether dependencies support the project's supported engine range. citeturn0search10

**[FACT]** mise's current documentation recommends `mise doctor` for checking a mise setup. citeturn0search2

**[FACT]** Current mise documentation distinguishes ordinary `mise doctor` diagnostics from configurable project checks; ordinary `mise doctor` does not automatically run project checks. citeturn0search14

**[UNVERIFIED]** Do not claim that any of these tools detect cross-file declaration conflicts until the study runs the empirical detection test in A8.

## A13. Section 16 correction

**[FACT]** v1.0 contained malformed backticks in the expected-deliverable block.

**[OPINION]** The corrected block is:
`
data/
  repositories.csv
  declarations.csv
  conflicts.csv
  harm.csv
  tool_coverage.csv

analysis/
  prevalence.md
  prevalence.json
  wilson_intervals.json

protocol/
  PREREGISTRATION.md
  deviations.md
`

The final report must state:
`
N_all
N_multi
C
D
P_all
P_multi
95% Wilson intervals
harm proportion H
ToolCoverage
OwnMachineFailureCoverage
final STOP/PIVOT/BUILD result
protocol deviations
`

## A14. Diff-style changelog

**[FACT]** v1.1 is a pre-data amendment.

```diff
- fixed 400-repository target
+ sequential sampling until N_multi >= 150, with N_all <= 1000 cap

- treated N_multi < 100 as a standalone STOP trigger
+ require N_multi >= 150 unless cap/time-box prevents it

+ explicitly reconcile P_multi >= 5% with D >= 20
+ at 5% prevalence, D >= 20 requires N_multi >= 400

+ add pushed-within-12-months eligibility filter
+ add recursive star-range slicing for over-cap GitHub search queries
+ redefine N_multi as 2+ comparable authoritative declarations in one scope
+ define CI matrix legs as separate execution scopes
+ add OwnMachineFailureCoverage
+ pin Python 3.12.15 stdlib random.Random / Mersenne Twister
+ add second-rater review of 10% of sampled repositories, minimum 20
+ require harm evidence to concern the same runtime family and scope
+ repair Section 16 backticks
+ mark cross-file detection claims UNVERIFIED until empirically tested
`

## A15. Amendment freeze

**[OPINION]** v1.1 is frozen before data collection. After the first repository is inspected, no primary eligibility, sampling, classification, harm, tool-detection, or decision criterion may be changed.

**[OPINION]** Any substantive later change must be recorded as a protocol deviation and excluded from the primary analysis.
