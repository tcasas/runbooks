[Runbooks Index](../index.md) / [Python](index.md)

# pyenv Install & Usage Runbook (RHEL 8)

Install `pyenv` to manage modern Python versions (3.10+) without modifying system Python.

---

## What is pyenv (context)

- Installs Python versions in user space (`~/.pyenv`)
- Does NOT modify `/usr/bin/python`
- Safe for RHEL production hosts
- Used only to select which Python is used to create virtualenvs

System layout:

```
OS Python        → /usr/bin/python
pyenv Python     → ~/.pyenv/versions/3.11.x/bin/python
project runtime → .venv/bin/python
```

---

## Install pyenv

### 1. Install build dependencies

```bash
sudo dnf -y install \
  gcc make patch zlib-devel bzip2 bzip2-devel readline-devel \
  sqlite sqlite-devel openssl-devel tk-devel libffi-devel xz-devel \
  curl git
```

### 2. Install pyenv

```bash
curl -fsSL https://pyenv.run | bash
```

Optional (turtle-suite): use a dedicated service user so pyenv and venv ownership stay clean and reproducible. Create a user (example: `turtle`), install pyenv under `/home/turtle/.pyenv`, and create the project venv under `/opt/otxapps/turtle-suite/.venv`. systemd should run `/opt/otxapps/turtle-suite/.venv/bin/python` directly, without relying on pyenv initialization.

### 3. Enable pyenv in shell (bash)

```bash
# Login shells
cat >> ~/.bash_profile <<'EOF'

# --- pyenv ---
export PYENV_ROOT="$HOME/.pyenv"
[[ -d $PYENV_ROOT/bin ]] && export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init - bash)"
EOF

# Interactive shells
cat >> ~/.bashrc <<'EOF'

# pyenv-virtualenv
eval "$(pyenv virtualenv-init -)"
EOF
```

Note: this shell setup is only needed to install Python versions, create virtualenvs, activate them manually, and do day-to-day development work. systemd services should always use the virtualenv's full Python path and do not rely on pyenv initialization.

Verify:

```bash
pyenv --version
```

---

## Install Python 3.11 using pyenv

```bash
pyenv install 3.11.9
pyenv local 3.11.9      # per-project (recommended)
# or:
# pyenv global 3.11.9   # per-user default

python -V
which python
```

Expected:

```
Python 3.11.x
~/.pyenv/versions/3.11.x/bin/python
```

---

## Use with virtualenv (normal workflow)

```bash
python -m venv .venv
source .venv/bin/activate

python -V
```

Install project packages as usual.

---

## Common commands

```bash
pyenv versions
pyenv install 3.11.9
pyenv local 3.11.9
pyenv global 3.11.9
pyenv which python
```

---

## Important notes

- pyenv affects **shell Python only**
- systemd services must always use full paths:

```
/opt/otxapps/.../.venv/bin/python
```

- Removing pyenv does not affect projects once venvs exist

---

## Removal (if needed)

```bash
rm -rf ~/.pyenv
sed -i '/pyenv/d' ~/.bashrc
```

---

## Policy

On RHEL hosts, install Python ≥3.10 using **pyenv**.  
Always run applications from their virtualenv.

---
