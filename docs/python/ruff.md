[Runbooks Index](../index.md) / [Python](index.md)

# Ruff: Python Linting Runbook

## 0. Overview

### Goal
- Install Ruff.
- Run checks on a single file, a directory, or the whole project.
- Auto-fix simple issues.
- Wire it into your workflow (optional: pre-commit).

### What is Ruff?
- Ruff is a fast Python linter / formatter.
- It finds style issues, unused imports/vars, some bugs, etc.
- It can auto-fix many problems.

## 1. Verify Python and environment

```bash
# Check Python version (Ruff supports modern Python; 3.8+ is safe)
python --version
# > Python 3.x.y

# (Optional but recommended) Check if you're in a virtualenv
# - If this prints a path, you're likely in a venv.
# - If it prints nothing, you're probably using system Python.
python -c "import sys, os; print(os.getenv('VIRTUAL_ENV') or 'NO_VENV')"
# > /path/to/venv
# OR
# > NO_VENV
```

## 2. Install Ruff

```bash
# If you are using a virtual environment, activate it first.
# Then install Ruff with pip.
python -m pip install --upgrade pip
python -m pip install ruff
# > Successfully installed ruff-<version>

# Confirm Ruff is available
python -m ruff --version
# > ruff <version> (python <version>)

# (Optional) If "python -m ruff" fails:
# - Ensure your PATH and environment are using the correct Python.
# - Try "python3 -m ruff" or explicitly use your venv's python.
```

## 3. Run Ruff on a single file

```bash
# Example: run Ruff on test_loader.py
# Adjust the path to match your project layout.
python -m ruff check apps/turtle-sensor/app/tests/test_loader.py
# > apps/.../test_loader.py:LINE:COL CODE Message...
# > ...
# > Found X errors, Y warnings.

# Notes:
# - "check" means: analyze and report, do NOT modify.
# - If there are no problems:
# > All checks passed!
```

## 4. Run Ruff on a directory or whole repo

```bash
# Run on a directory (e.g. just tests)
python -m ruff check apps/turtle-sensor/app/tests
# > apps/...:LINE:COL CODE Message...
# > ...

# Run on the whole repo (from repo root)
python -m ruff check .
# > apps/...:LINE:COL ...
# > ...

# If Ruff is very noisy:
# - That means it’s finding a lot of style/quality issues.
# - We’ll tame that via configuration later.
```

## 5. Let Ruff auto-fix simple issues

```bash
# Preview fixes without changing files (--diff)
python -m ruff check --diff apps/turtle-sensor/app/tests/test_loader.py
# > --- before  (path/to/file)
# > +++ after   (path/to/file)
# > @@ -1,3 +1,3 @@
# > ...

# Actually apply fixes (--fix)
python -m ruff check --fix apps/turtle-sensor/app/tests/test_loader.py
# > apps/.../test_loader.py:LINE:COL CODE Message... (fixed)
# > 1 fix applied.

# Common auto-fixes:
# - Remove unused imports/variables
# - Reformat some code constructs
# - Sort imports (if configured)
```

## 6. Basic configuration with pyproject.toml

### Goal
- Tell Ruff which rules to use, line length, and target Python version.
- This lives at the root of your repo.

```bash
# Step 6.1: Create pyproject.toml if you don't have one
# (Run this from the repo root; edit if pyproject.toml exists already.)
cat << 'EOF' >> pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py39"

# Common rule sets:
# E,F: pycodestyle + pyflakes (errors)
# I:   import sorting
# B:   bugbear (potential bugs / bad patterns)
select = ["E", "F", "I", "B"]

# You can ignore specific rules globally if needed:
# ignore = ["E501"]  # example: ignore line length

[tool.ruff.lint.isort]
# Optional import-sorting tweaks
combine-as-imports = true
EOF

# Step 6.2: Re-run Ruff with config
python -m ruff check .
# > Ruff will now respect pyproject.toml settings.
```

## 7. Understanding Ruff messages (quick primer)

```bash
# Typical message format:
# PATH:LINE:COL CODE Message
# Example:
# > apps/turtle-sensor/app/tests/test_loader.py:42:5 F401 `os` imported but unused

# Breakdown:
# - FILE: apps/.../test_loader.py
# - LINE: 42
# - COL: 5
# - CODE: F401  (unused import)
# - Message: `os` imported but unused

# Common codes you’ll see a lot:
# - F401: imported but unused
# - F841: local variable assigned but never used
# - E501: line too long
# - B007/B008/etc: bugbear “this might be a bug” patterns
# - Ixxx: import sorting issues
```

## 8. Focus on a single rule (triage mode)

```bash
# If Ruff outputs too much, you can focus on one rule at a time.

# Example: find only unused imports (F401)
python -m ruff check --select F401 .
# > ... F401 `x` imported but unused

# Example: show only bugbear rules (B)
python -m ruff check --select B .
# > ... B007 Loop control variable not used within loop body

# Example: show everything except a particular rule:
python -m ruff check --ignore E501 .
# > All codes except E501 (line length) will show.
```

## 9. Using Ruff as a formatter (optional)

```bash
# Ruff can also format code (similar to black) via "format" subcommand.
# This is separate from "check". Only do this if you want Ruff to OWN formatting.

# Preview formatting changes on a file:
python -m ruff format apps/turtle-sensor/app/tests/test_loader.py --diff
# > --- before
# > +++ after
# > ...

# Apply formatting:
python -m ruff format apps/turtle-sensor/app/tests/test_loader.py
# > 1 file reformatted.

# You can also run on the entire repo:
python -m ruff format .
# > N files reformatted.
```

## 10. Integrate Ruff into pre-commit (optional, but powerful)

```bash
# If you use pre-commit, this will run Ruff automatically on staged files.

# Step 10.1: Install pre-commit (if not already)
python -m pip install pre-commit

# Step 10.2: Create or edit .pre-commit-config.yaml at repo root
cat << 'EOF' >> .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.0  # Check Ruff docs for latest stable version
    hooks:
      - id: ruff
        args: [ "check", "--fix" ]
      - id: ruff-format
EOF

# Step 10.3: Install the git hooks
pre-commit install
# > pre-commit installed at .git/hooks/pre-commit

# Step 10.4: Test it
# - Change a Python file, stage it, and attempt a commit.
git add apps/turtle-sensor/app/tests/test_loader.py
git commit -m "Test Ruff hook"
# > Ruff.............................................................[FAIL]
# > ...
# If it fails:
# - Fix issues or let Ruff --fix do its job, then recommit.
```

## 11. Typical daily workflow

```bash
# From repo root, do:

# 1) Quick smoke check on modified files:
python -m ruff check apps/turtle-sensor/app/tests/test_loader.py

# 2) Auto-fix low-risk issues:
python -m ruff check --fix apps/turtle-sensor/app/tests/test_loader.py

# 3) Before PR / big change:
python -m ruff check .
python -m ruff format .    # if using Ruff as formatter

# 4) Let pre-commit act as guardrail (if enabled):
git commit -m "Some change"
# > Ruff ... [OK]
# > Ruff-format ... [OK]
```

## 12. Troubleshooting

```bash
# Ruff command not found / module error:
# - Ensure Ruff is installed in the environment whose "python" you are invoking.
python -m pip show ruff
# > Name: ruff
# > Location: /path/to/site-packages

# If not installed:
python -m pip install ruff

# "Too many errors" or overwhelming output:
# - Use --select to focus on specific rule families.
# - Use --ignore in pyproject.toml for rules you truly don’t care about.
# - Start with a smaller scope (one directory or file) and expand gradually.

# Ruff disagrees with your preferred style:
# - Tweak pyproject.toml: line-length, select/ignore, import settings, etc.
# - Only enable rule sets that match your standards (e.g., just E,F at first).

# Unsure what a rule code means:
# - Search "Ruff <CODE>", e.g., "Ruff F401", to see docs and examples.
```

## 13. Minimal quick-start (cheat sheet)

```bash
# From repo root:

# 1) Install Ruff
python -m pip install ruff

# 2) Basic config
cat << 'EOF' >> pyproject.toml
[tool.ruff]
line-length = 100
target-version = "py39"
select = ["E", "F", "I", "B"]
EOF

# 3) Run check on everything
python -m ruff check .

# 4) Auto-fix low-hanging fruit
python -m ruff check --fix .

# 5) (Optional) Format
python -m ruff format .
```
