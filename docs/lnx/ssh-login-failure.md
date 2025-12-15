# SSH Login Failure — su Works but SSH Fails

## Symptom
- `sudo su - <user>` → SUCCESS
- `ssh <user>@host` → FAIL

**Meaning:** Authentication works; SSH is blocking the login (policy, shell, key, or PAM). Run as root on the target host.

---

## Index: Confirm SSH Attempt Is Reaching Host
1. **Watch SSH auth log live (MOST IMPORTANT)**
   - RHEL / Rocky / Alma: `tail -f /var/log/secure`
   - Ubuntu / Debian: `tail -f /var/log/auth.log`
   - In another terminal, attempt SSH login and capture the exact error line.

---

## Index: Common SSH Policy Blocks
2. **Check sshd allow/deny rules**
   - Command: `grep -E "^(AllowUsers|DenyUsers|AllowGroups|DenyGroups)" /etc/ssh/sshd_config`
   - Expected: No deny rules matching `svc_VAScanner`.

3. **Check if SSH password auth is disabled**
   - Command: `grep -E "^(PasswordAuthentication|PubkeyAuthentication)" /etc/ssh/sshd_config`
   - Expect `PasswordAuthentication yes` or key-based login configured.

4. **Check if account is explicitly blocked by Match blocks**
   - Command: `grep -n "^Match" /etc/ssh/sshd_config`
   - Inspect any `Match User` / `Match Group` blocks.

---

## Index: Shell & Account Constraints (VERY COMMON)
5. **Verify login shell**
   - Command: `getent passwd svc_VAScanner | cut -d: -f7`
   - Expected: `/bin/bash`; `/sbin/nologin` or `/bin/false` causes SSH denial.

6. **Check for non-interactive service account protection**
   - Command: `grep svc_VAScanner /etc/shells`
   - Expected: Shell must be listed in `/etc/shells`.

---

## Index: SSH Key Authentication (if used)
7. **Check .ssh permissions**
   - Commands:
     - `ls -ld /home/svc_vascanner/.ssh`
     - `ls -l  /home/svc_vascanner/.ssh/authorized_keys`
   - Expected:
     - `.ssh` `700`
     - `authorized_keys` `600`
     - Owned by `svc_vascanner`.
   - Fix if needed:
     - `chown -R svc_vascanner:svc_vascanner /home/svc_vascanner/.ssh`
     - `chmod 700 /home/svc_vascanner/.ssh`
     - `chmod 600 /home/svc_vascanner/.ssh/authorized_keys`

---

## Index: PAM + SSH Integration
8. **Check PAM sshd stack**
   - Command: `sed -n '1,200p' /etc/pam.d/sshd`
   - Look for:
     - `pam_access.so`
     - `pam_nologin.so`
     - `pam_sepermit.so`
     - `pam_sss.so`

---

## Index: SELinux (SSH-SPECIFIC)
9. **Check SELinux denials**
   - Command: `ausearch -m AVC -ts recent | grep ssh`

   **Quick test (TEMPORARY ONLY):**
   - `setenforce 0`
   - Retry SSH
   - `setenforce 1`

---

## Index: SSH Debug From Client (AUTHORITATIVE)
10. **From client machine**
    - Command: `ssh -vvv svc_VAScanner@host`
    - Look for:
      - Authentication refused
      - No supported authentication methods
      - Account expired
      - Permission denied (publickey)

---

## Index: Most Common Root Causes (Ranked)
1. DenyUsers / DenyGroups in `sshd_config`
2. Shell set to `nologin` or not in `/etc/shells`
3. `PasswordAuthentication` disabled
4. Missing or wrong SSH key permissions
5. `pam_access` or `pam_sepermit` restriction
6. SELinux SSH denial
7. `Match User` block overriding defaults

---

End of runbook.
