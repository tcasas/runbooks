# Cert Workflow Runner (Checkpointed) — Runbook

## Synopsis

### What this is
- A chained workflow runner that executes multiple certificate stages in order.
- Persists progress to a JSON state file so you can safely stop/resume between steps.
- Supports:
  - listing steps (no execution)
  - listing CertFile scope keys with context (no execution)
  - starting from any step
  - pausing between steps
  - overriding issuance/install inputs via CLI flags

### Step sequence (fixed order)
1. `issue_sectigo_cert`
2. `exercise_load_by_scope_key`
3. `install_f5_cert`
4. `install_gcp_cert`

### State file fields
- `last_completed`: last step that completed successfully
- `last_status`: "success" or "failed"
- `last_message`: the last step’s message


## Safety & Scope

### Safety limits
This runner can touch real systems depending on config:
- Sectigo issuance (real order/issue actions)
- Controller reads (`load_by_scope_key`)
- F5 installs
- GCP installs

### Best practice
- Use dedicated test CN / profiles / partitions.
- Explicitly pass device/project/region/proxy when skipping/resuming steps.
- Store state files someplace controlled; they can contain identifiers (`scope_key`, CN, etc.).


## Location & Invocation

Run as a module:
```bash
python -m app.tests.repl.cert_workflow
```

Expected:
- INFO logs via `basicConfig`.
- State file created/updated.
- Steps run in order (or resumed).

Quick usage examples (mirrors the script docstring):
```bash
# Run the full workflow, resuming from the default state file if it exists
python -m app.tests.repl.cert_workflow

# List known CertFile scope keys with context
python -m app.tests.repl.cert_workflow --list-scope-keys

# Force a fresh run from the beginning and store progress in a custom location
python -m app.tests.repl.cert_workflow --no-resume --state-file /tmp/cert_state.json

# Start at load_by_scope_key with explicit inputs for the CertFile hydration step
python -m app.tests.repl.cert_workflow --start-from exercise_load_by_scope_key \
  --scope-key your_scope_key_here --controller-name your_controller

# Override issuance settings while pausing between steps
python -m app.tests.repl.cert_workflow --pause --device my-f5 --cn example.com \
  --workflow-mode CSR_ISSUE_INSTALL --subject-city "New York"

# Inspect the sequence without executing anything
python -m app.tests.repl.cert_workflow --list-steps

# Resume a stopped run using a saved state and skip straight to installation
python -m app.tests.repl.cert_workflow --state-file /tmp/cert_state.json \
  --start-from install_f5_cert --device f5-ltm-01 --cn api.example.com

# Run only the GCP install stage with regional proxy overrides
python -m app.tests.repl.cert_workflow --no-resume --start-from install_gcp_cert \
  --project-id my-gcp-project --region us-west1 --proxy-name example-proxy
```


## Inspect (No Execution)

List the configured steps (no API calls, no state changes):
```bash
python -m app.tests.repl.cert_workflow --list-steps
```

Expected:
- `issue_sectigo_cert`: Issue a Sectigo certificate using existing REPL helper.
- `exercise_load_by_scope_key`: Hydrate a CertFile via `load_by_scope_key()`.
- `install_f5_cert`: Install certificate to F5 using REPL helper.
- `install_gcp_cert`: Install certificate to GCP using REPL helper.

List known CertFile scope keys (no execution):
```bash
python -m app.tests.repl.cert_workflow --list-scope-keys
```

Behavior:
- Queries `CertFiles().get_all(lazy_load=True, reset_items=True)`.
- When `--controller-name` is provided, switches to eager load for that controller.
- Prints per-controller sections with scope key, CN, and expiry.
- Returns exit code 1 if CertFiles retrieval fails.
- Prints `No CertFiles found.` when the collection is empty.


## State File Behavior

### Default state file
Defaults to a local file in the current working directory (relative path):
```
.cert_workflow_state.json
```

### Resume semantics (default: enabled)
- If `--resume=true` and `last_completed` exists: start from the step AFTER `last_completed`.
- Otherwise: start from step 0.

### Force a fresh run (ignore any existing progress)
```bash
python -m app.tests.repl.cert_workflow --no-resume
```
Expected: starts at `issue_sectigo_cert` regardless of saved state.

### Use a custom state file path
```bash
python -m app.tests.repl.cert_workflow --no-resume --state-file /tmp/cert_state.json
```
Expected: state created/updated at `/tmp/cert_state.json`; parent directory created if missing.

### What happens if the state file is corrupted/unreadable
`_load_state()` catches exceptions and resets progress. A warning is emitted and execution begins from scratch (unless `--start-from` is used).
Expected log:
```
State file <path> is unreadable; resetting progress
```


## Starting From a Specific Step

Start from a specific step (overrides resume logic). Choices are exactly:
- `issue_sectigo_cert`
- `exercise_load_by_scope_key`
- `install_f5_cert`
- `install_gcp_cert`

Example:
```bash
python -m app.tests.repl.cert_workflow --start-from install_f5_cert --device f5-ltm-01 --cn api.example.com
```

Expected:
- Runner begins at `install_f5_cert`.
- Earlier steps are **not** executed.
- State `last_completed` updates only after successful step completion.

Resume a stopped run and jump ahead anyway:
```bash
python -m app.tests.repl.cert_workflow --state-file /tmp/cert_state.json --start-from install_gcp_cert --project-id my-gcp-project --region us-west1 --proxy-name example-proxy --cn api.example.com
```
Expected: starts at `install_gcp_cert` regardless of saved `last_completed`.


## Pause / Manual Stop Between Steps

Pause between steps:
```bash
python -m app.tests.repl.cert_workflow --pause
```

Behavior:
- After each successful step (except the last), you're prompted: `Completed <step>. Press Enter to continue or 'q' to stop:`
- Enter => continue.
- `q` => stop cleanly (progress saved, exit 0).


## Parameters & Overrides

### Core runner flags (resume behavior)
```
--resume / --no-resume
--state-file <path>
--start-from <step>
--pause
--list-steps
--list-scope-keys
```

### CertFile hydration flags (`exercise_load_by_scope_key`)
```
--scope-key <scope_key>            # REQUIRED when running exercise_load_by_scope_key
--controller-name <controller>     # Optional controller override
```

Note: if `exercise_load_by_scope_key` runs without `--scope-key`, the script exits immediately:
```
raise SystemExit("--scope-key is required ...")
```

### Sectigo issuance override flags (used by `issue_sectigo_cert` step)
```
--device <name>            # default comes from issue_sectigo_cert.DEVICE
--cssl-prof <profile>      # default issue_sectigo_cert.CSSL_PROF
--project-id <id>          # default issue_sectigo_cert.PROJECT_ID
--cn <common-name>         # default issue_sectigo_cert.CN
--san "<san1 san2,...>"    # comma/space separated SANs passed through to CSR inputs
--workflow-mode <mode>     # choices: issue_sectigo_cert.MODE_CHOICES
--csr-policy <name>
--subject-country <val>
--subject-state <val>
--subject-city <val>
--subject-org <val>
--subject-ou <val>
```

Subject override behavior:
- Only non-empty overrides are included in `subject_overrides`.
- Empty args are ignored.

### F5 install flags (`install_f5_cert` step)
```
--device <name>
--cssl-prof <profile>
--project-id <id>
--cn <common-name>
```

### GCP install flags (`install_gcp_cert` step)
```
--project-id <gcp-project>
--proxy-name <proxy>     # default install_gcp_cert.PROXY_NAME
--region <region>        # default install_gcp_cert.REGION
--cn <common-name>
```


## Common Execution Patterns

### Pattern A — Full workflow, auto-resume (default)
```bash
python -m app.tests.repl.cert_workflow
```
Expected: if state exists and `last_completed` set, resumes at next step; otherwise starts at `issue_sectigo_cert`.

### Pattern B — Fresh run + custom state file
```bash
python -m app.tests.repl.cert_workflow --no-resume --state-file /tmp/cert_state.json
```
Expected: starts from `issue_sectigo_cert`; writes progress to `/tmp/cert_state.json`.

### Pattern C — Run ONLY CertFile hydration (controller lookup)
```bash
python -m app.tests.repl.cert_workflow \
  --no-resume \
  --start-from exercise_load_by_scope_key \
  --scope-key <scope_key> \
  --controller-name <controller>
```
Expected: executes `load_by_scope_key`; continues into install steps unless you stop (or use `--pause` + `q`).

### Pattern D — Resume and install to F5 only
```bash
python -m app.tests.repl.cert_workflow \
  --state-file /tmp/cert_state.json \
  --start-from install_f5_cert \
  --device <f5-device-name> \
  --cn api.example.com \
  --project-id <id> \
  --cssl-prof <profile>
```
Expected: runs `install_f5_cert` (and then `install_gcp_cert` unless stopped).

### Pattern E — GCP-only install with regional proxy overrides
```bash
python -m app.tests.repl.cert_workflow \
  --no-resume \
  --start-from install_gcp_cert \
  --project-id my-gcp-project \
  --region us-west1 \
  --proxy-name example-proxy \
  --cn api.example.com
```
Expected: runs only `install_gcp_cert` (then completes).


## Logging & Return Codes

### Logging
Uses module logger name `cert-workflow`. Emits INFO-level logs by default:
```python
logging.basicConfig(level=logging.INFO)
```

Expected log lines:
```
INFO cert-workflow Running step <step>
INFO cert-workflow Step <step> result: ok=True msg=<...>
```

### Exit codes
- 0 : workflow complete OR stopped by user during `--pause`.
- 1 : a step returned `ok=False` (workflow stops immediately).
- 2 : (typical argparse) invalid args / unknown flags.
- Immediate exit: missing `--scope-key` when `exercise_load_by_scope_key` runs.

### Failure behavior
If a step fails (`ok=False`):
- `last_status = "failed"`
- `last_message = <step message>`
- Workflow stops and exits 1
- `last_completed` is **not** advanced

Expected log:
```
ERROR cert-workflow Stopping workflow because <step> failed
```


## Troubleshooting

### "State file is unreadable; resetting progress"
- State JSON is corrupt / partially written / invalid.
- Fix by deleting or replacing the file:
  ```bash
  rm -f .cert_workflow_state.json
  ```
- Expected: next run starts from step 0.

### "KeyError" on --start-from
- `--start-from` choices are constrained by argparse, so this generally occurs only if code changes and step names drift.
- Verify:
  ```bash
  python -m app.tests.repl.cert_workflow --list-steps
  ```

### Missing required data when skipping steps
- If you skip issuance and start at install steps, you must provide:
  - `--device` / `--project-id` / `--cn` / (and GCP: `--region` / `--proxy-name` as needed)
- If you start at `exercise_load_by_scope_key`, you must provide `--scope-key`.

## End of Runbook
