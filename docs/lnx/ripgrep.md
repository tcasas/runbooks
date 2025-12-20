[Runbooks Index](../index.md) / [Linux](index.md)

# Ripgrep (`rg`)

## Purpose
Fast, recursive text search for code, configuration files, and logs. All commands are copy/paste-ready.

## Prerequisites
- Verify `rg` is installed:
  ```bash
  rg --version
  ```
  Expected: `ripgrep <version>`
- Install on RHEL-like systems if missing:
  ```bash
  sudo dnf install -y ripgrep
  ```
  Expected: `Installed: ripgrep-...`

## Core syntax
```bash
rg [options] <PATTERN> [PATH...]
```
`PATTERN` is required.

## Basic searches
- Search current tree:
  ```bash
  rg "READONLY_KEYS"
  ```
- Search a specific file:
  ```bash
  rg "READONLY_KEYS" app/loader/loader.py
  ```
- Search a specific directory:
  ```bash
  rg "READONLY_KEYS" app/loader/
  ```
- Case-insensitive match:
  ```bash
  rg -i "readonly_keys" app/
  ```
- Whole-word only:
  ```bash
  rg -w "READONLY_KEYS" app/
  ```

## Context output
- Two lines before and after:
  ```bash
  rg -C 2 "READONLY_KEYS" app/
  ```
- After only:
  ```bash
  rg -A 3 "READONLY_KEYS" app/
  ```
- Before only:
  ```bash
  rg -B 3 "READONLY_KEYS" app/
  ```

## Literal vs. regex
- Literal (no regex):
  ```bash
  rg -F "READONLY_KEYS=" app/
  ```
- Regex example:
  ```bash
  rg 'READONLY_KEYS\s*=' app/
  ```

## File and path filtering
- Only Python files:
  ```bash
  rg "READONLY_KEYS" -g "*.py" app/
  ```
- Exclude directories:
  ```bash
  rg "READONLY_KEYS" app/ -g '!**/venv/**' -g '!**/__pycache__/**'
  ```

## Definitions and tracing
- Constant definition:
  ```bash
  rg -n '^\s*READONLY_KEYS\s*=' app/
  ```
- Function definition:
  ```bash
  rg -n '^\s*def\s+get_all\b' app/
  ```
- Class definition:
  ```bash
  rg -n '^\s*class\s+Loader\b' app/
  ```

## Multiple terms
- OR match:
  ```bash
  rg -n '(READONLY_KEYS|WRITEONLY_KEYS)' app/
  ```

## Files vs. matches
- Files containing a match:
  ```bash
  rg -l "READONLY_KEYS" app/
  ```
- Files without a match:
  ```bash
  rg -L "READONLY_KEYS" app/
  ```
- Count matches per file:
  ```bash
  rg -c "READONLY_KEYS" app/
  ```

## `bash -lc` gotcha
When wrapping `rg` in `bash -lc`, quote the entire command to avoid dropping arguments:

- Incorrect:
  ```bash
  /bin/bash -lc rg "READONLY_KEYS" app/loader/loader.py
  ```
  Error: `rg: ripgrep requires at least one pattern to execute a search`

- Correct:
  ```bash
  /bin/bash -lc 'rg "READONLY_KEYS" app/loader/loader.py'
  ```

## Handy defaults
- Use `-C` for context, `-F` for literals, `-g` for include/exclude patterns.
- `-l` outputs only filenames; `-c` outputs match counts per file.
