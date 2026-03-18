# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

**Install dependencies:**
```bash
pip install -e ".[develop]"
```

**Auto-format code (black, docformatter, isort):**
```bash
./run_autoformat.sh
```

**Run all CI checks locally (format + typecheck + lint + tests):**
```bash
./run_ci_checks.sh
```

**Individual checks:**
```bash
mypy .                                              # static type checking (strict mode)
pytest . --pylint -m pylint --pylint-rcfile=.pylintrc  # lint only
pytest tests/                                       # unit tests only
pytest tests/test_utils.py::test_get_good_dogs_of_breed  # single test
```

## Architecture

This is a Python 3.11+ package (`src/` layout) for an HRI (Human-Robot Interaction) course project.

```
src/hri_final_project/
    structs.py   # dataclass definitions
    utils.py     # functions operating on those structs
tests/
    test_utils.py
```

**Code quality stack:** mypy (strict), pylint (`.pylintrc`), black (line-length=88), isort (black profile), docformatter. The same checks run in GitHub Actions CI (`.github/workflows/ci.yml`) across 4 parallel jobs.

**Mypy is in strict mode** — all functions need type annotations; matplotlib is exempted from type checking in `pyproject.toml`.
