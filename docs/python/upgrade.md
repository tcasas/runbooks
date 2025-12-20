[Runbooks Index](../index.md) / [Python](index.md)

# Python Upgrade Runbook (virtualenv focused)

This runbook guides you through upgrading Python while keeping projects isolated with `venv`.

## Table of contents
- [Prerequisites](#prerequisites)
- [Prepare the environment](#prepare-the-environment)
- [Install the new Python version](#install-the-new-python-version)
- [Create a fresh virtual environment](#create-a-fresh-virtual-environment)
- [Re-install project dependencies](#re-install-project-dependencies)
- [Validate the upgrade](#validate-the-upgrade)
- [Migrate existing shells and tools](#migrate-existing-shells-and-tools)
- [Rollback plan](#rollback-plan)

## Prerequisites
- Shell access with permissions to install Python (system package manager, `pyenv`, or installer).
- `python3-venv`/`python3.X-venv` package available if using OS packages.
- Backup of your current `requirements.txt`, `poetry.lock`, or `pip-tools` output.
- Optional: `pyenv` for managing multiple Python installations side by side.

## Prepare the environment
- Confirm the current Python version:
  ```bash
  python3 --version
  which python3
  ```
- Capture active virtual environments you need to recreate (names and paths).
- Freeze existing dependencies for reference:
  ```bash
  source .venv/bin/activate  # adjust to your env path
  python -m pip freeze > requirements.freeze.txt
  deactivate
  ```

## Install the new Python version
- OS package managers:
  ```bash
  # Debian/Ubuntu example
  sudo apt-get update
  sudo apt-get install python3.12 python3.12-venv python3.12-distutils
  ```
- `pyenv` (isolated, per-user):
  ```bash
  pyenv install 3.12.4
  pyenv global 3.12.4  # or `local` inside a project
  ```
- Verify install and ensure the new binary is first on `PATH`:
  ```bash
  python3 --version
  which python3
  ```

## Create a fresh virtual environment
- Create a project-local environment using the new interpreter:
  ```bash
  python3 -m venv .venv
  source .venv/bin/activate
  python -m pip install --upgrade pip
  ```
- For multiple projects, repeat per project to keep dependencies isolated.
- If using `pyenv`, ensure the project’s `.python-version` points to the upgraded version before creating the venv:
  ```bash
  pyenv local 3.12.4
  python -m venv .venv
  ```

## Re-install project dependencies
- Install from your lockfile or requirements snapshot:
  ```bash
  # requirements.txt
  python -m pip install -r requirements.txt

  # pip-tools
  pip-compile --upgrade
  python -m pip install -r requirements.txt

  # Poetry
  poetry env use $(which python)
  poetry install
  ```
- Rebuild any native extensions that may depend on the Python ABI (happens automatically during install).

## Validate the upgrade
- Run project smoke tests inside the new virtual environment:
  ```bash
  source .venv/bin/activate
  python -m pytest -q  # replace with project’s test entrypoint
  ```
- Check key CLIs resolve to the new interpreter:
  ```bash
  python --version
  pip --version
  which python
  ```
- Validate runtime behavior for entrypoints or scripts you ship (e.g., `python -m myapp --version`).

## Migrate existing shells and tools
- Update shell init files if they pin the old interpreter (e.g., `PATH` exports, aliases).
- Refresh environment activation in terminals or IDEs so they pick up the new `.venv`.
- For Jupyter/IPython, register the new kernel:
  ```bash
  python -m ipykernel install --user --name project-venv --display-name "Python (project)"
  ```
- If using systemd or cron jobs, update unit files or scripts to point at `.venv/bin/python`.

## Rollback plan
- Keep the previous interpreter installed until validation completes.
- Preserve the frozen dependency file (`requirements.freeze.txt`) to recreate the old environment:
  ```bash
  python -m venv .venv-old
  source .venv-old/bin/activate
  python -m pip install -r requirements.freeze.txt
  ```
- If issues arise, switch back by reactivating the old environment or updating `pyenv local` to the prior version.
