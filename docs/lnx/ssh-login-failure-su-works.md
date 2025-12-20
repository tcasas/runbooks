[Runbooks Index](../index.md) / [Linux](index.md)

# SSH Login Failure — `su` Works but SSH Fails

## Symptom
- `sudo su - <user>` → **SUCCESS**
- `ssh <user>@host` → **FAIL**
- Interpretation: Authentication works; SSH is blocking the login (policy, shell, key, or PAM).

> **Run these steps as `root` on the target host.**

---

## Confirm SSH Attempt Is Reaching Host

1. **Watch SSH auth log live (most important)**
   - RHEL / Rocky / Alma: `tail -f /var/log/secure`
   - Ubuntu / Debian: `tail -f /var/log/auth.log`
   - In another terminal, attempt the SSH login and capture the exact error line.

---

## Common SSH Policy Blocks

2. **Check sshd allow/deny rules**
   - Command: `grep -E "^(AllowUsers|DenyUsers|AllowGroups|DenyGroups)" /etc/ssh/sshd_config`
   - Expected: No deny rules matching the user (example: `svc_VAScanner`).

3. **Check if SSH password auth is disabled**
   - Command: `grep -E "^(PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config`
   - Expected: `PasswordAuthentication yes` (or a working key-based login configuration).

4. **Check if account is blocked by Match blocks**
   - Command: `grep -n "^Match" /etc/ssh/sshd_config`
   - Inspect any `Match User` or `Match Group` blocks that might override defaults.

---

## Shell & Account Constraints (very common)

5. **Verify login shell**
   - Command: `getent passwd <user> | cut -d: -f7`
   - Expected: `/bin/bash`.
   - `/sbin/nologin` or `/bin/false` causes SSH denial.

6. **Check for non-interactive service account protection**
   - Command: `grep <user> /etc/shells`
   - Shell must be listed in `/etc/shells` for SSH to allow login.

---

## SSH Key Authentication (if used)

7. **Check `.ssh` permissions**
   - Commands:
     - `ls -ld /home/<user>/.ssh`
     - `ls -l /home/<user>/.ssh/authorized_keys`
   - Expected permissions and ownership:
     - `.ssh` directory: `700`, owned by the user.
     - `authorized_keys`: `600`, owned by the user.
   - Fix if needed:
     - `chown -R <user>:<user> /home/<user>/.ssh`
     - `chmod 700 /home/<user>/.ssh`
     - `chmod 600 /home/<user>/.ssh/authorized_keys`

---

## PAM + SSH Integration

8. **Check PAM sshd stack**
   - Command: `sed -n '1,200p' /etc/pam.d/sshd`
   - Look for modules that may block login, such as `pam_access.so`, `pam_nologin.so`, `pam_sepermit.so`, or `pam_sss.so`.

---

## SELinux (SSH-specific)

9. **Check SELinux denials**
   - Command: `ausearch -m AVC -ts recent | grep ssh`
   - Quick test (temporary only):
     - `setenforce 0`
     - Retry SSH
     - `setenforce 1`

---

## SSH Debug from Client (authoritative)

10. **Collect SSH debug from client**
    - Command: `ssh -vvv <user>@<host>`
    - Review for messages such as `Authentication refused`, `No supported authentication methods`, `Account expired`, or `Permission denied (publickey)`.

---

## Most Common Root Causes (ranked)

1. `DenyUsers` / `DenyGroups` in `sshd_config`.
2. Shell set to `nologin` or not listed in `/etc/shells`.
3. `PasswordAuthentication` disabled.
4. Missing or incorrect SSH key permissions.
5. `pam_access` or `pam_sepermit` restriction.
6. SELinux SSH denial.
7. `Match User` block overriding defaults.

---

End of runbook.
