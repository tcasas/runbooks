[Runbooks Index](../../index.md) / [Turtle Sensor](../index.md) / [REPL](index.md)

# Source Inspection Runbook (line-accurate, diff-friendly)

- **Target:** Linux / RHEL / containers / CI shells  
- **Goal:** Show exact file slices with stable line numbers (including blank lines)

## Safety + conventions
- Use READ-ONLY commands only (`cat`, `nl`, `sed`, `awk`, `less`, `rg`).
- Prefer absolute paths or `cd` into repo root before referencing relative paths.
- Use `nl -ba` so blank lines are counted (matches editor line numbers).

## Workspace variables (optional but recommended)
Set once per shell session (adjust to your repo):
```bash
export REPO_ROOT="/workspace/turtle-sensor"
export SRC_FILE="app/tests/repl/cert_workflow.py"
```

Verify targets exist (expected: no output):
```bash
test -d "${REPO_ROOT}"
test -f "${REPO_ROOT}/${SRC_FILE}"
```

## Repo root validation
Confirm you are in the repo and see expected structure:
```bash
cd "${REPO_ROOT}" && pwd
```
Expected: `/workspace/turtle-sensor`

```bash
cd "${REPO_ROOT}" && ls -la | head
```
Expected: repo top-level files/dirs listed.

## Show a line slice (canonical)
Print numbered lines 180–270 (includes blank lines):
```bash
cd "${REPO_ROOT}" && nl -ba "${SRC_FILE}" | sed -n '180,270p'
```
Expected: lines prefixed with numbers 180..270 (blank lines still numbered).

## Show a line slice with context
Print target range plus +/- context around it:
```bash
cd "${REPO_ROOT}" && nl -ba "${SRC_FILE}" | sed -n '170,280p'
```
Expected: numbered lines 170..280.

## Search then open slice
Find pattern line numbers, then print around match:
```bash
cd "${REPO_ROOT}" && rg -n --hidden --no-ignore-vcs "PATTERN_HERE" "${SRC_FILE}"
```
Expected: `app/tests/repl/cert_workflow.py:<line>:<matching line>`

Print around a specific line (example: 250 +/- 20):
```bash
cd "${REPO_ROOT}" && nl -ba "${SRC_FILE}" | sed -n '230,270p'
```
Expected: numbered lines 230..270.

## View safely in a pager
Use `less` for interactive inspection (jump to line N):
```bash
cd "${REPO_ROOT}" && nl -ba "${SRC_FILE}" | less -SR
```
Expected: pager opens. Type `250g` to jump to line 250, `/PATTERN` then Enter to search, `q` to quit.

## Show function/class boundaries quickly
Identify defs/classes and their approximate locations:
```bash
cd "${REPO_ROOT}" && rg -n "^(def |class )" "${SRC_FILE}"
```
Expected: list of definitions with line numbers.

## Show surrounding git context
Confirm file version and show blame around a line range:
```bash
cd "${REPO_ROOT}" && git status --porcelain
```
Expected: empty output if clean or changed files listed.

```bash
cd "${REPO_ROOT}" && git log -n 1 -- "${SRC_FILE}"
```
Expected: latest commit touching the file.

```bash
cd "${REPO_ROOT}" && sed -n '180,270p' "${SRC_FILE}" | nl -ba -w1 -s$'\t' >/dev/null
```
Expected: no output (sanity check; optional).

```bash
cd "${REPO_ROOT}" && git blame -L 180,270 -- "${SRC_FILE}"
```
Expected: each line annotated with commit/author/time.

## Shell hygiene / common pitfalls
- **Problem:** "No such file" due to wrong `cwd`.  
  **Fix:** always anchor with `cd "${REPO_ROOT}" && test -f "${SRC_FILE}"`.

- **Problem:** blank lines not numbered.  
  **Fix:** use `nl -ba` (NOT plain `nl`).

- **Problem:** command needs a consistent environment (`PATH`, venv, etc.).  
  **Fix:** run via login shell:  
  ```bash
  /bin/bash -lc "cd ${REPO_ROOT} && nl -ba ${SRC_FILE} | sed -n '180,270p'"
  ```
