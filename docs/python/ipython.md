[Runbooks Index](../index.md) / [Python](index.md)

# IPython Quickstart

Use this runbook to install IPython, launch sessions, and lean on core features for fast Python exploration.

## Table of contents
- [Prerequisites](#prerequisites)
- [Install IPython](#install-ipython)
- [Launch a session](#launch-a-session)
- [Session essentials](#session-essentials)
- [Handy magic commands](#handy-magic-commands)
- [Debugging and tracing](#debugging-and-tracing)
- [Working with notebooks](#working-with-notebooks)
- [Configure IPython](#configure-ipython)
- [Tips for productivity](#tips-for-productivity)

## Prerequisites
- Python 3.8+ installed.
- Access to a virtual environment (recommended for project work).
- Ability to install packages with `pip` or `pipx`.

## Install IPython
- Install globally with `pipx`:
  ```bash
  pipx install ipython
  ```
- Or install in an active virtual environment:
  ```bash
  python -m pip install ipython
  ```
- Verify installation:
  ```bash
  ipython --version
  ```

## Launch a session
- Default shell:
  ```bash
  ipython
  ```
- Start with a specific virtual environment (after activation):
  ```bash
  source .venv/bin/activate
  ipython
  ```
- Run a script then drop to an interactive shell:
  ```bash
  ipython -i script.py
  ```

## Session essentials
- Auto-complete and object info:
  - Press `Tab` to complete.
  - Append `?` for help: `json.dumps?`
  - Append `??` to view source when available: `requests.get??`
- Command history:
  - `up/down` arrows cycle history.
  - `%history -n -5` shows the last five commands with numbers.
  - `%rerun 12-15` re-executes commands 12 through 15.
- Quick variables:
  - `_` last result, `__` second-to-last, `_i` last input, `_ih` full history list.
- Paste blocks safely:
  - `cpaste` enters a paste-friendly mode for indented code:
    ```python
    %cpaste
    # paste code here, then press Ctrl-D
    ```

## Handy magic commands
- `%run script.py`: Execute a local script in the current namespace.
- `%edit my_func`: Open the current editor (`$EDITOR`) to edit and re-run code.
- `%timeit expression`: Benchmark a single expression. Example:
  ```python
  %timeit sum(range(1_000_000))
  ```
- `%%timeit` cell magic to benchmark multi-line blocks.
- `%who` / `%whos`: Show variables in scope.
- `%store var_name`: Persist a variable between sessions; retrieve with `%store -r`.
- `!command`: Run shell commands. Example: `!ls -l data/`.
- `%env`: View or set environment variables. Examples:
  ```python
  %env
  %env MY_FLAG=1
  ```
- `%load`: Pull code from a URL or local file directly into the session:
  ```python
  %load https://raw.githubusercontent.com/pallets/flask/main/src/flask/__init__.py
  ```

## Debugging and tracing
- Start the built-in debugger at an exception:
  ```python
  %debug
  ```
- Set a manual breakpoint:
  ```python
  import pdb; pdb.set_trace()
  ```
- Trace a single statement and its execution:
  ```python
  %prun my_func()
  ```
- Profile line-by-line to find hot spots:
  ```python
  %load_ext line_profiler
  %lprun -f my_func my_func()
  ```

## Working with notebooks
- Convert notebooks to scripts and back:
  ```bash
  jupyter nbconvert --to script notebook.ipynb
  jupyter nbconvert --to notebook script.py
  ```
- Open a notebook in an interactive console session:
  ```bash
  ipython kernel
  ```
  Then connect via Jupyter or `jupyter console --existing`.

## Configure IPython
- Generate a default profile in `~/.ipython/profile_default/`:
  ```bash
  ipython profile create
  ```
- Set defaults in `ipython_config.py`, for example:
  ```python
  c = get_config()
  c.TerminalInteractiveShell.colors = "Linux"  # or 'Neutral', 'NoColor'
  c.InteractiveShellApp.extensions = ["autoreload"]
  ```
- Auto-reload modules during development by adding to `~/.ipython/profile_default/ipython_config.py`:
  ```python
  c.InteractiveShellApp.exec_lines = ["%load_ext autoreload", "%autoreload 2"]
  ```

## Tips for productivity
- Use virtual environments per project to avoid dependency conflicts.
- Keep a startup script in `~/.ipython/profile_default/startup/` for imports you always use (for example, `import pathlib as P`).
- Combine shell and Python: `files = !ls *.py` returns a list you can iterate over.
- Keep sessions reproducible: record key commands with `%history -g > notes.txt`.
- Store and reuse snippets with `%alias` and `%macro`:
  ```python
  %alias ll ls -l
  %macro load_data 3-6  # saves inputs 3-6 to reuse later
  ```
- Capture and reuse stdout:
  ```python
  output = !python script.py
  print(output.n)  # line count
  ```
