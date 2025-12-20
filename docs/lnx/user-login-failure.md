[Runbooks Index](../index.md) / [Linux](index.md)

# User Login Failure — Single-Host Debug Runbook

## How to use this guide
- **Purpose:** Identify why a user cannot log in (local or directory-backed) and restore access safely.
- **Scope:** Local Linux users plus AD/LDAP identities via SSSD.
- **Access methods:** Console, SSH, and `su`.
- **Prerequisite:** Run as root (or via `sudo`). Capture timestamps of the failed login attempt for log review.

---

## Fast triage (run in order)
1. **Confirm user exists (NSS resolution)**  
   `getent passwd <username>`  
   Expected: Exactly one passwd entry. No output → local account missing or directory lookups are failing.

2. **Check account lock or failure counters**  
   - `passwd -S <username>` → `P` is set, `L` is locked.  
   - On RHEL-like systems: `faillock --user <username>` → ensure no deny lockout; clear when appropriate with `faillock --user <username> --reset`.

3. **Check account expiration**  
   `chage -l <username>`  
   Expected: `Account expires: never` and `Password expires: <future date>`.

4. **Check login shell**  
   `getent passwd <username> | cut -d: -f7`  
   Expected: Valid shell like `/bin/bash`. `/sbin/nologin` or `/bin/false` denies login.

5. **Check home directory**  
   `ls -ld /home/<username>`  
   Expected: Owned by the user with execute (`x`) permission.  
   Fix: `chown <username>:<username> /home/<username>` and `chmod 700 /home/<username>`.

6. **Check disk space and inodes**  
   `df -h /` and `df -i /`  
   Expected: Usage below 100% for both space and inodes.

7. **Check for a global login block**  
   `ls -l /etc/nologin`  
   Expected: File does **not** exist (if present, only root can log in). Remove when safe: `rm -f /etc/nologin`.

---

## Authentication & PAM
8. **Review authentication logs**  
   - RHEL / Rocky / Alma: `tail -n 50 /var/log/secure`  
   - Ubuntu / Debian: `tail -n 50 /var/log/auth.log`  
   Look for `pam_unix`, `pam_sss`, lockout messages, or account expiration errors.

9. **Test local privilege escalation path**  
   `su - <username>`  
   If `su` works but SSH fails, focus on `sshd`/PAM configuration (e.g., `/etc/pam.d/sshd` changes).

10. **Validate PAM modules for recent edits**  
    `grep -R \"auth\" /etc/pam.d/sshd /etc/pam.d/system-auth /etc/pam.d/common-auth`  
    Look for newly added modules or ordering changes that could deny access.

---

## SSH-specific checks (remote login only)
11. **Check sshd allow/deny rules**  
    `grep -E \"AllowUsers|DenyUsers|AllowGroups|DenyGroups\" /etc/ssh/sshd_config`  
    Expected: No matching deny rules for the user or their group.

12. **Check SSH key permissions (key-based login)**  
    `chmod 700 /home/<username>/.ssh` and `chmod 600 /home/<username>/.ssh/authorized_keys`.

13. **Confirm service is reachable**  
    - Verify port: `ss -tlnp | grep sshd`  
    - Check banner: `ssh -vv <hostname>` to see where negotiation fails.

---

## Directory services (AD / LDAP)
14. **Verify SSSD status**  
    `systemctl status sssd`  
    Expected: `active (running)`.

15. **Test identity lookup**  
    `id <username>`  
    Expected: UID/GID returned. Hang or failure indicates a directory authentication problem.

16. **Check domain health (SSSD/AD)**  
    - `sssctl domain-status <domain>` for online/offline state.  
    - `realm list` to confirm the host is still joined to the domain.

---

## SELinux (RHEL family)
17. **Check SELinux mode**  
    `getenforce`  
    `Enforcing` is OK, but denials may still block login.

18. **Check recent SELinux denials**  
    `ausearch -m AVC -ts recent`

---

## Summary decision points
- `getent` fails → user or directory issue.
- `passwd -S` shows `L` or `faillock` shows denies → account locked.
- `chage` shows expired → account expired.
- Invalid shell → intentional denial.
- Home directory permissions wrong → login fails during session setup.
- Disk full → PAM session creation fails.
- `/etc/nologin` present → global login block.
- `sssd` down or offline → domain users fail.
- PAM edits or sshd allow/deny rules → targeted login denial.

---

End of runbook.
