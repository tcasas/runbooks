# Login Noise Debug — Escape-sequence noise (e.g., B7)

## How to use this guide
- **Purpose:** Eliminate unexpected `command not found` or control-character noise (e.g., `B7`, `OB`, `ESC[...`) that appears when a user logs in. A literal `B7` in the output is not a real command; it is usually a byte from an escape sequence being misread as a command name because a startup script printed raw control characters.
- **Scope:** Bash login or interactive shells on Linux; focus on startup files and MOTD scripts.
- **Goal:** Identify which script prints the noise, then remove or fix the offending line.

---

## Fast triage (run in order)
1) **Confirm the active shell**  
Command: `echo $SHELL`  
Expected: `/bin/bash`. If different, adjust paths below accordingly.

2) **Reproduce with a clean environment**  
Command: `env -i bash --noprofile --norc`  
Expected: **No** `B7` messages or other noise. Silence here means a startup script is responsible.

3) **Detect login vs interactive mode**  
Command: `set -o | grep login_shell`  
Purpose: Determines whether Bash read `.bash_profile`/`.profile` (login) or `.bashrc` (interactive only).

4) **Trace what gets sourced (important)**  
Command: `PS4='+${BASH_SOURCE}:${LINENO}: ' bash -lxic 'exit' 2>/tmp/bash-startup.trace`  
Then: `sed -n '1,120p' /tmp/bash-startup.trace`  
Outcome: Shows each line executed during startup and which file it came from. Scroll to the lines just before the `command not found` noise.

---

## Inspect user startup files (match to login vs interactive)
- `sed -n '1,200p' ~/.bash_profile`
- `sed -n '1,200p' ~/.bashrc`
- `sed -n '1,200p' ~/.profile`
- `sed -n '1,200p' ~/.bash_logout`

Look for:
- `echo -e` or `printf` calls with escape sequences (`\e[`, `\033`, `^[`).
- Unquoted terminal control strings in prompts (`PS1`) missing `\[`/`\]` guards.
- Binary bytes when `cat -A ~/.bashrc` shows `M-` or `^` sequences.

---

## Inspect system-wide startup and MOTD content
1) **Profiles and Bash RC**  
- `sed -n '1,200p' /etc/profile`  
- `sed -n '1,200p' /etc/bash.bashrc` (Debian/Ubuntu)  
- `ls -l /etc/profile.d && sed -n '1,160p' /etc/profile.d/*.sh`

2) **MOTD (common culprit for stray bytes)**  
- `ls -l /etc/motd && sed -n '1,200p' /etc/motd`  
- `ls -l /etc/update-motd.d` and inspect any executable scripts.  
Look for `printf '\e'`, color prompts, or `tput` calls emitting control characters when stdout is not a terminal.

3) **Login banners**  
- `sed -n '1,200p' /etc/issue` and `sed -n '1,200p' /etc/issue.net`

---

## Clean up and retest
- Comment or remove the specific line identified in the trace (often a stray escape sequence, color prompt, or non-printable byte pasted into a banner).
- If the noise came from `PS1`, ensure escape sequences are wrapped in `\[` and `\]` so Bash does not treat them as literal characters.
- Re-run `env -i bash --noprofile --norc` (expect silence), then a normal login shell (expect silence) to confirm the fix.

End.
