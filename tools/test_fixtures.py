#!/usr/bin/env python3
"""Run extractor tests on generated local fixtures only."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIX = ROOT / "fixtures"
sys.path.insert(0, str(ROOT / "tools"))
from extract_declarations import classify, extract, parse_range  # noqa: E402

MATRIX = "$" + "{{ matrix.node }}"


def put(case: str, files: dict[str, str]) -> Path:
    path = FIX / case
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True)
    for name, text in files.items():
        target = path / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return path


def pkg(node: str) -> str:
    return json.dumps({"name": "fixture", "engines": {"node": node}}, indent=2)


def check(name: str, files: dict[str, str], status: str, n_multi: int, conflicts: int,
          subtype: str | None = None) -> None:
    path = put(name, files)
    result = classify(extract(path))
    actual = (result["status"], result["N_multi"], len(result["conflicts"]))
    expected = (status, n_multi, conflicts)
    assert actual == expected, "%s actual=%r expected=%r" % (name, actual, expected)
    if subtype is not None:
        got = result["conflicts"][0].get("subtype") if result["conflicts"] else None
        assert got == subtype, "%s subtype=%r expected=%r" % (name, got, subtype)
    print("PASS %s -> %s" % (name, actual))


def main() -> int:
    if FIX.exists():
        shutil.rmtree(FIX)
    (FIX / "controls").mkdir(parents=True)
    (FIX / "conflicts").mkdir(parents=True)

    gha_compatible = (
        "jobs:\n"
        "  test:\n"
        "    strategy:\n"
        "      matrix:\n"
        "        node: [18, 20]\n"
        "    steps:\n"
        "      - uses: actions/setup-node@v4\n"
        "        with:\n"
        "          node-version: " + MATRIX + "\n"
    )
    gha_expected_failure = (
        "jobs:\n"
        "  test:\n"
        "    continue-on-error: true\n"
        "    strategy:\n"
        "      matrix:\n"
        "        node: [18]\n"
        "    steps:\n"
        "      - uses: actions/setup-node@v4\n"
        "        with:\n"
        "          node-version: " + MATRIX + "\n"
    )

    cases = [
        ("controls/CTRL-01-single", {"package.json": pkg(">=18")}, "UNKNOWN", 0, 0, None),
        ("controls/CTRL-02-node-pass", {"package.json": pkg(">=18"), ".nvmrc": "20.11.1\n"}, "PASS", 1, 0, None),
        ("controls/CTRL-03-node-conflict", {"package.json": pkg(">=20"), ".nvmrc": "18.19.0\n"}, "CONFLICT", 1, 1, None),
        ("controls/CTRL-04-python-pass", {
            "pyproject.toml": "[project]\nname='fixture'\nrequires-python='>=3.10,<3.13'\n",
            ".python-version": "3.12.15\n",
        }, "PASS", 1, 0, None),
        ("controls/CTRL-05-python-conflict", {
            "pyproject.toml": "[project]\nname='fixture'\nrequires-python='>=3.13'\n",
            ".python-version": "3.12.15\n",
        }, "CONFLICT", 1, 1, None),
        ("controls/CTRL-06-tool-versions", {
            "package.json": pkg(">=20"), ".tool-versions": "nodejs 20.11.1\n",
        }, "PASS", 1, 0, None),
        ("controls/CTRL-07-mise", {
            "package.json": pkg(">=20"), "mise.toml": "[tools]\nnode='20.11.1'\n",
        }, "PASS", 1, 0, None),
        ("controls/CTRL-08-docker-isolated", {
            "package.json": pkg(">=20"), ".nvmrc": "20.11.1\n", "Dockerfile": "FROM node:20-alpine\n",
        }, "PASS", 1, 0, None),
        ("controls/CTRL-09-ci-pass", {"package.json": pkg(">=18"), ".github/workflows/test.yml": gha_compatible},
         "PASS", 1, 0, None),
        ("controls/CTRL-10-ci-conflict", {"package.json": pkg(">=20"), ".github/workflows/test.yml": gha_compatible},
         "CONFLICT", 1, 1, "CI_ENGINE_CONFLICT"),
        ("controls/CTRL-11-unknown-pin", {"package.json": pkg(">=20"), ".nvmrc": "latest\n"},
         "UNKNOWN", 1, 0, None),
        ("controls/CTRL-12-expected-failure", {"package.json": pkg(">=20"), ".github/workflows/test.yml": gha_expected_failure},
         "PASS", 1, 0, None),
        ("conflicts/CF-01-pin-conflict", {
            "package.json": pkg(">=18"), ".nvmrc": "20.11.1\n", ".node-version": "22.1.0\n",
        }, "CONFLICT", 1, 1, None),
        ("conflicts/CF-02-caret-boundary", {"package.json": pkg("^20"), ".nvmrc": "22.0.0\n"},
         "CONFLICT", 1, 1, None),
        ("conflicts/CF-03-upper-bound", {"package.json": pkg(">=20 <22"), ".nvmrc": "22.0.0\n"},
         "CONFLICT", 1, 1, None),
        ("conflicts/CF-04-python-tool", {
            "pyproject.toml": "[project]\nname='fixture'\nrequires-python='>=3.12'\n",
            ".tool-versions": "python 3.11.9\n",
        }, "CONFLICT", 1, 1, None),
        ("conflicts/CF-05-multiple-scope", {
            "package.json": pkg(">=20"), ".nvmrc": "20.11.1\n",
            "packages/app/package.json": pkg(">=18"), "packages/app/.nvmrc": "17.0.0\n",
        }, "CONFLICT", 1, 1, None),
    ]

    for case in cases:
        check(*case)

    for expr, is_python in [
        (">=18", False), ("^20", False), (">=20 <22", False),
        ("3.12.*", True), (">=3.10,<3.13", True), ("~=3.12", True),
    ]:
        _, status = parse_range(expr, python=is_python)
        assert status == "OK", "range normalization failed: %s -> %s" % (expr, status)
        print("PASS range %s -> %s" % (expr, status))

    print("ALL FIXTURE TESTS PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
