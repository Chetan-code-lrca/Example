#!/usr/bin/env python3
"""RunMismatch v0.1 declaration extractor.

Deterministic, network-free, conservative:
- unknown syntax stays UNKNOWN;
- CI matrix legs are separate execution scopes;
- expected-failure CI jobs are not conflicts;
- Docker/Heroku declarations do not implicitly compare with local declarations.
"""
from __future__ import annotations

import argparse
import configparser
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

try:
    import tomllib
except ModuleNotFoundError:
    tomllib = None

try:
    import yaml
except ModuleNotFoundError:
    yaml = None

Version = tuple[int, int, int]


@dataclass(frozen=True)
class Bound:
    version: Version | None
    inclusive: bool = True


@dataclass(frozen=True)
class Interval:
    lower: Bound
    upper: Bound


@dataclass
class Declaration:
    family: str
    source: str
    path: str
    field: str
    raw: str
    normalized: list[dict[str, Any]]
    normalize_status: str
    project_scope: str
    execution_scope: str
    scope_kind: str
    subtype: str | None = None
    selection_group: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def cmp(a: Version, b: Version) -> int:
    return (a > b) - (a < b)


def intersect(a: Interval, b: Interval) -> Interval | None:
    lo = a.lower
    if b.lower.version is not None and (lo.version is None or cmp(b.lower.version, lo.version) > 0):
        lo = b.lower
    elif b.lower.version is not None and lo.version is not None and cmp(b.lower.version, lo.version) == 0:
        lo = Bound(lo.version, lo.inclusive and b.lower.inclusive)

    hi = a.upper
    if b.upper.version is not None and (hi.version is None or cmp(b.upper.version, hi.version) < 0):
        hi = b.upper
    elif b.upper.version is not None and hi.version is not None and cmp(b.upper.version, hi.version) == 0:
        hi = Bound(hi.version, hi.inclusive and b.upper.inclusive)

    if lo.version is not None and hi.version is not None:
        c = cmp(lo.version, hi.version)
        if c > 0 or (c == 0 and not (lo.inclusive and hi.inclusive)):
            return None
    return Interval(lo, hi)


def parse_version(token: str) -> tuple[Version, int] | None:
    token = token.strip().lstrip("v").split("+", 1)[0]
    if "-" in token:
        return None
    parts = token.split(".")
    if not 1 <= len(parts) <= 3 or any(not p.isdigit() for p in parts):
        return None
    nums = [int(p) for p in parts]
    while len(nums) < 3:
        nums.append(0)
    return (nums[0], nums[1], nums[2]), len(parts)


def prefix_interval(token: str) -> Interval | None:
    token = token.strip()
    if token in {"*", "x", "X"}:
        return Interval(Bound(None), Bound(None))
    parts = token.split(".")
    nums: list[int] = []
    for p in parts:
        if p in {"*", "x", "X"}:
            break
        if not p.isdigit():
            return None
        nums.append(int(p))
    if not nums:
        return None
    while len(nums) < 3:
        nums.append(0)
    v = tuple(nums)  # type: ignore[assignment]
    concrete = len([p for p in parts if p not in {"*", "x", "X"}])
    if concrete == 1:
        upper = (v[0] + 1, 0, 0)
    elif concrete == 2:
        upper = (v[0], v[1] + 1, 0)
    else:
        upper = (v[0], v[1], v[2] + 1)
    return Interval(Bound(v), Bound(upper, False))


def caret(v: Version) -> Interval:
    if v[0] > 0:
        upper = (v[0] + 1, 0, 0)
    elif v[1] > 0:
        upper = (0, v[1] + 1, 0)
    else:
        upper = (0, 0, v[2] + 1)
    return Interval(Bound(v), Bound(upper, False))


def tilde(v: Version, parts: int) -> Interval:
    upper = (v[0] + 1, 0, 0) if parts == 1 else (v[0], v[1] + 1, 0)
    return Interval(Bound(v), Bound(upper, False))


def bare_interval(token: str) -> Interval | None:
    if any(p in token for p in ("*", "x", "X")):
        return prefix_interval(token)
    parsed = parse_version(token)
    if not parsed:
        return None
    v, parts = parsed
    if parts < 3:
        return Interval(Bound(v), Bound((v[0] + 1, 0, 0) if parts == 1 else (v[0], v[1] + 1, 0), False))
    return Interval(Bound(v), Bound(v))


def parse_range(expr: str, python: bool = False) -> tuple[list[Interval], str]:
    expr = str(expr).strip()
    if not expr or expr.lower() in {"latest", "lts", "lts/*", "stable"}:
        return [], "UNKNOWN"

    result: list[Interval] = []
    for branch in expr.split("||"):
        current = [Interval(Bound(None), Bound(None))]
        tokens = [x for x in re.split(r"\s+|,", branch.strip()) if x]
        for token in tokens:
            m = re.match(r"^(>=|<=|>|<|==|=|\^|~|~=)?(.+)$", token)
            if not m:
                return [], "UNKNOWN"
            op, value = m.group(1) or "", m.group(2).strip()

            if op == "^":
                p = parse_version(value)
                if not p:
                    return [], "UNKNOWN"
                current = [x for a in current for x in [intersect(a, caret(p[0]))] if x]
                continue

            if op in {"~", "~="}:
                p = parse_version(value)
                if not p:
                    return [], "UNKNOWN"
                current = [x for a in current for x in [intersect(a, tilde(p[0], p[1]))] if x]
                continue

            if op:
                p = parse_version(value)
                if not p and python and op == "==" and any(x in value for x in ("*", "x", "X")):
                    pfx = prefix_interval(value)
                    if pfx is None:
                        return [], "UNKNOWN"
                    current = [x for a in current for x in [intersect(a, pfx)] if x]
                    continue
                if not p:
                    return [], "UNKNOWN"
                v, parts = p
                if op == "==":
                    op = "="
                if op == ">=":
                    bound = Interval(Bound(v, True), Bound(None))
                elif op == ">":
                    bound = Interval(Bound(v, False), Bound(None))
                elif op == "<":
                    bound = Interval(Bound(None), Bound(v, False))
                elif op == "<=":
                    if parts < 3:
                        return [], "UNKNOWN"
                    bound = Interval(Bound(None), Bound(v, True))
                else:
                    bound = Interval(Bound(v, True), Bound(v, True))
            else:
                bound = bare_interval(value)
                if bound is None:
                    return [], "UNKNOWN"

            current = [x for a in current for x in [intersect(a, bound)] if x]

        result.extend(current)

    return result, "OK" if result else "UNKNOWN"


def norm_json(items: list[Interval]) -> list[dict[str, Any]]:
    def b(x: Bound) -> dict[str, Any]:
        return {"version": list(x.version) if x.version else None, "inclusive": x.inclusive}
    return [{"lower": b(i.lower), "upper": b(i.upper)} for i in items]


def make_decl(root: Path, path: Path, family: str, source: str, field: str, raw: Any,
              project_scope: str | None = None, execution_scope: str | None = None,
              scope_kind: str = "local", subtype: str | None = None,
              selection_group: str | None = None) -> Declaration:
    text = str(raw).strip()
    intervals, status = parse_range(text, python=family == "python")
    local = path.parent.relative_to(root).as_posix() or "."
    ps = project_scope or "local:%s" % local
    es = execution_scope or ps
    return Declaration(
        family, source, path.relative_to(root).as_posix(), field, text,
        norm_json(intervals), status, ps, es, scope_kind, subtype, selection_group
    )


def parse_package(path: Path, root: Path) -> list[Declaration]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    scope = "local:%s" % (path.parent.relative_to(root).as_posix() or ".")
    out: list[Declaration] = []
    engines = data.get("engines", {})
    if isinstance(engines, dict):
        for key in ("node", "npm"):
            if key in engines:
                out.append(make_decl(root, path, "node" if key == "node" else "npm",
                                     "package.json", "engines.%s" % key, engines[key], scope))
    dev = data.get("devEngines", {})
    runtime = dev.get("runtime") if isinstance(dev, dict) else None
    items = runtime if isinstance(runtime, list) else ([runtime] if runtime is not None else [])
    for i, item in enumerate(items):
        if isinstance(item, dict) and str(item.get("name", "")).lower() == "node" and "version" in item:
            out.append(make_decl(root, path, "node", "package.json",
                                 "devEngines.runtime[%d].version" % i, item["version"], scope))
    volta = data.get("volta", {})
    if isinstance(volta, dict) and "node" in volta:
        out.append(make_decl(root, path, "node", "package.json", "volta.node", volta["node"], scope))
    return out


def parse_version_file(path: Path, root: Path, family: str, source: str) -> list[Declaration]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    return [make_decl(root, path, family, source, "content", text.splitlines()[0])]


def parse_tool_versions(path: Path, root: Path) -> list[Declaration]:
    out: list[Declaration] = []
    scope = "local:%s" % (path.parent.relative_to(root).as_posix() or ".")
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        parts = line.strip().split()
        if len(parts) < 2 or parts[0].startswith("#"):
            continue
        tool = parts[0]
        if tool not in {"node", "nodejs", "npm", "python"}:
            continue
        family = "npm" if tool == "npm" else ("node" if tool in {"node", "nodejs"} else "python")
        for i, value in enumerate(parts[1:]):
            out.append(make_decl(root, path, family, ".tool-versions", "%s[%d]" % (tool, i),
                                 value, scope, selection_group="tool:%s" % tool))
    return out


def parse_mise(path: Path, root: Path) -> list[Declaration]:
    if tomllib is None:
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    tools = data.get("tools", {})
    scope = "local:%s" % (path.parent.relative_to(root).as_posix() or ".")
    out: list[Declaration] = []
    if isinstance(tools, dict):
        for tool, value in tools.items():
            if tool not in {"node", "nodejs", "npm", "python"}:
                continue
            vals = value if isinstance(value, list) else [value]
            family = "python" if tool == "python" else ("npm" if tool == "npm" else "node")
            for i, item in enumerate(vals):
                raw = item.get("version", item) if isinstance(item, dict) else item
                out.append(make_decl(root, path, family, "mise.toml", "tools.%s[%d]" % (tool, i),
                                     raw, scope, selection_group="mise:%s" % tool))
    return out


def parse_pyproject(path: Path, root: Path) -> list[Declaration]:
    if tomllib is None:
        return []
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    project = data.get("project", {})
    req = project.get("requires-python") if isinstance(project, dict) else None
    if req is None:
        return []
    scope = "local:%s" % (path.parent.relative_to(root).as_posix() or ".")
    return [make_decl(root, path, "python", "pyproject.toml",
                      "project.requires-python", req, scope)]


def parse_runtime(path: Path, root: Path) -> list[Declaration]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    raw = re.sub(r"^python-", "", text.splitlines()[0].strip(), flags=re.I)
    scope = "heroku:%s" % (path.parent.relative_to(root).as_posix() or ".")
    return [make_decl(root, path, "python", "runtime.txt", "content", raw, scope, scope, "heroku")]


def parse_tox(path: Path, root: Path) -> list[Declaration]:
    parser = configparser.ConfigParser()
    try:
        parser.read(path, encoding="utf-8")
    except Exception:
        return []
    base = "local:%s" % (path.parent.relative_to(root).as_posix() or ".")
    envs: list[str] = []
    if parser.has_section("tox") and parser.has_option("tox", "envlist"):
        envs = [x for x in re.split(r"[,\s]+", parser.get("tox", "envlist")) if x]
    out: list[Declaration] = []
    basepython = parser.get("testenv", "basepython", fallback="").strip()
    if basepython:
        m = re.search(r"python(?:3)?[\s-]?(\d)(\d{1,2})", basepython, re.I)
        if m:
            raw = "%s.%s" % (m.group(1), m.group(2))
            for env in envs or ["default"]:
                out.append(make_decl(root, path, "python", "tox.ini", "testenv.basepython",
                                     raw, base, "tox:%s:%s" % (path.relative_to(root), env), "tox"))
            return out
    for env in envs:
        m = re.fullmatch(r"py(\d)(\d{1,2})", env, re.I)
        if m:
            raw = "%s.%s" % (m.group(1), m.group(2))
            out.append(make_decl(root, path, "python", "tox.ini", "tox.envlist",
                                 raw, base, "tox:%s:%s" % (path.relative_to(root), env),
                                 "tox", selection_group="tox:%s" % env))
    return out


def parse_docker(root: Path) -> list[Declaration]:
    out: list[Declaration] = []
    for path in root.rglob("*Dockerfile*"):
        if not path.is_file():
            continue
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            m = re.match(r"^\s*FROM\s+([^\s]+)", line, re.I)
            if not m:
                continue
            image = m.group(1)
            im = re.match(r"^(node|python):([^@]+)$", image, re.I)
            if not im:
                continue
            family, tag = im.group(1).lower(), im.group(2)
            version = re.match(r"^\d+(?:\.\d+){0,2}", tag)
            raw = version.group(0) if version else tag
            scope = "container:%s:%d" % (path.relative_to(root).as_posix(), line_no)
            out.append(make_decl(root, path, family, "Dockerfile", "FROM[%d]" % line_no, raw,
                                 scope, scope, "container"))
    return out


def parse_workflows(root: Path) -> list[Declaration]:
    if yaml is None:
        return []
    out: list[Declaration] = []
    workflow_paths = list(root.glob(".github/workflows/*.yml")) + list(root.glob(".github/workflows/*.yaml"))
    for path in workflow_paths:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        except Exception:
            continue
        jobs = data.get("jobs", {})
        if not isinstance(jobs, dict):
            continue
        for job_id, job in jobs.items():
            if not isinstance(job, dict):
                continue
            matrix = (job.get("strategy") or {}).get("matrix") or {}
            expected_failure = job.get("continue-on-error") is True
            defaults = job.get("defaults") or {}
            run_defaults = defaults.get("run") if isinstance(defaults, dict) else {}
            working_dir = run_defaults.get("working-directory") if isinstance(run_defaults, dict) else None
            if isinstance(working_dir, str) and working_dir and not working_dir.startswith("/") and "${" not in working_dir:
                project_scope = "local:%s" % Path(working_dir).as_posix().strip(".")
                if project_scope == "local:":
                    project_scope = "local:."
            else:
                project_scope = "local:."
            steps = job.get("steps") or []
            if not isinstance(steps, list):
                continue
            for idx, step in enumerate(steps):
                if not isinstance(step, dict) or not isinstance(step.get("with"), dict):
                    continue
                use = str(step.get("uses", ""))
                with_ = step["with"]
                if use.startswith("actions/setup-node"):
                    version_keys = [("node-version", "node"), ("node-version-file", "node-file")]
                    family = "node"
                elif use.startswith("actions/setup-python"):
                    version_keys = [("python-version", "python"), ("python-version-file", "python-file")]
                    family = "python"
                else:
                    continue
                for key, label in version_keys:
                    if key not in with_:
                        continue
                    raw = with_[key]
                    values: list[str] = []
                    if key.endswith("-file"):
                        target = (root / Path(str(raw))).resolve()
                        if target.is_file() and root in target.parents:
                            txt = target.read_text(encoding="utf-8").strip()
                            if txt:
                                values = [txt.splitlines()[0].strip()]
                    elif isinstance(raw, str) and "matrix." in raw:
                        matrix_key = raw.split("matrix.", 1)[1].split("}", 1)[0].strip()
                        values = [str(x) for x in matrix.get(matrix_key, [])] if isinstance(matrix.get(matrix_key, []), list) else []
                    elif isinstance(raw, (str, int, float)):
                        values = [str(raw)]
                    for leg_i, value in enumerate(values):
                        leg_scope = "ci:%s:%s:%s:%d" % (
                            path.relative_to(root).as_posix(), job_id, label, leg_i
                        )
                        subtype = "EXPECTED_FAILURE_LEG" if expected_failure else "CI_ENGINE_CONFLICT"
                        out.append(make_decl(root, path, family, "github-actions",
                                             "jobs.%s.steps[%d].with.%s" % (job_id, idx, key),
                                             value, project_scope, leg_scope, "ci", subtype,
                                             selection_group="gha:%s:%s:%s" % (path, job_id, label)))
    return out


def extract(root: Path) -> list[Declaration]:
    out: list[Declaration] = []
    for p in root.rglob("package.json"):
        out.extend(parse_package(p, root))
    for p in root.rglob(".nvmrc"):
        out.extend(parse_version_file(p, root, "node", ".nvmrc"))
    for p in root.rglob(".node-version"):
        out.extend(parse_version_file(p, root, "node", ".node-version"))
    for p in root.rglob(".python-version"):
        out.extend(parse_version_file(p, root, "python", ".python-version"))
    for p in root.rglob(".tool-versions"):
        out.extend(parse_tool_versions(p, root))
    for p in root.rglob("mise.toml"):
        out.extend(parse_mise(p, root))
    for p in root.rglob("pyproject.toml"):
        out.extend(parse_pyproject(p, root))
    for p in root.rglob("runtime.txt"):
        out.extend(parse_runtime(p, root))
    for p in root.rglob("tox.ini"):
        out.extend(parse_tox(p, root))
    out.extend(parse_docker(root))
    out.extend(parse_workflows(root))
    return out


def reconstruct(items: list[dict[str, Any]]) -> list[Interval]:
    out: list[Interval] = []
    for item in items:
        lo = item["lower"]
        hi = item["upper"]
        out.append(Interval(
            Bound(tuple(lo["version"]) if lo["version"] is not None else None, lo["inclusive"]),
            Bound(tuple(hi["version"]) if hi["version"] is not None else None, hi["inclusive"]),
        ))
    return out


def compatible(a: Declaration, b: Declaration) -> bool:
    for x in reconstruct(a.normalized):
        for y in reconstruct(b.normalized):
            if intersect(x, y) is not None:
                return True
    return False


def classify(decls: list[Declaration]) -> dict[str, Any]:
    conflicts: list[dict[str, Any]] = []
    unresolved = False
    comparable_scopes: set[tuple[str, str]] = set()
    for i, a in enumerate(decls):
        for b in decls[i + 1:]:
            if a.family != b.family or a.project_scope != b.project_scope:
                continue
            if a.selection_group and b.selection_group and a.selection_group == b.selection_group:
                continue
            if a.scope_kind == "ci" and b.scope_kind == "ci":
                continue
            if a.scope_kind == "container" or b.scope_kind == "container":
                continue
            comparable_scopes.add((a.family, a.project_scope))
            if a.subtype == "EXPECTED_FAILURE_LEG" or b.subtype == "EXPECTED_FAILURE_LEG":
                continue
            if a.normalize_status != "OK" or b.normalize_status != "OK":
                unresolved = True
                continue
            if not compatible(a, b):
                conflicts.append({
                    "family": a.family,
                    "project_scope": a.project_scope,
                    "a": a.to_dict(),
                    "b": b.to_dict(),
                    "subtype": a.subtype or b.subtype,
                })
    n_multi = 1 if comparable_scopes else 0
    status = "CONFLICT" if conflicts else ("UNKNOWN" if unresolved else ("PASS" if n_multi else "UNKNOWN"))
    return {"N_multi": n_multi, "status": status, "conflicts": conflicts}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fixtures-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if not root.is_dir():
        print("error: not a directory", file=sys.stderr)
        return 2
    if args.fixtures_only and "fixtures" not in root.parts:
        print("error: --fixtures-only refuses paths outside a fixtures directory", file=sys.stderr)
        return 2
    decls = extract(root)
    result = {"root": str(root), "declarations": [d.to_dict() for d in decls], "classification": classify(decls)}
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else
          "declarations=%d N_multi=%d status=%s conflicts=%d" % (
              len(decls), result["classification"]["N_multi"],
              result["classification"]["status"], len(result["classification"]["conflicts"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
