# B7 Command Not Found — Login Noise Debug

## Scope and goal
Use this runbook to track down unexpected `command not found` or control-character noise during login. Steps focus on finding problematic startup files and MOTD scripts.

## 1) Confirm the shell being used
- Command: `echo $SHELL`
- Expected: `/bin/bash`

## 2) Reproduce with a clean environment
- Command: `env -i bash --noprofile --norc`
- Expected: No `B7` errors or other login noise. If the clean shell is quiet, a startup file is the likely culprit.

## 3) Identify whether the shell is a login shell
- Command: `set -o | grep login_shell`
- Purpose: Determines which startup files (`.bash_profile` vs `.bashrc`) are sourced.

## 4) Inspect user startup files
Run the following to check for stray control characters, `echo -e`, `printf` with escapes, or other non-printing bytes.
- `sed -n '1,200p' ~/.bash_profile`
- `sed -n '1,200p' ~/.bashrc`
- `sed -n '1,200p' ~/.bash_logout`
- `sed -n '1,200p' ~/.zshrc`

## 5) Inspect system-wide profiles
- `sed -n '1,200p' /etc/profile`
- `ls -l /etc/profile.d`
- `sed -n '1,200p' /etc/profile.d/*.sh`

## 6) Check the message of the day (MOTD)
- `ls -l /etc/motd`
- `ls -l /etc/update-motd.d`
- `sed -n '1,200p' /etc/motd`

## 7) Detect non-printing characters (important)
Look specifically for `^[`, `\033`, or `$'\e'` sequences that could emit control characters.
- `cat -A ~/.bashrc`
- `cat -A ~/.bash_profile`
- `cat -A /etc/profile`

## 8) Decide and fix
- If the clean shell is quiet but a normal login is noisy, comment out or remove the offending lines in the identified startup file.
- Re-test by opening a new shell after each change to confirm the noise is gone.

End.
