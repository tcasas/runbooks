# Linux User Login Failure — Single-Block Debug Runbook

## How to use this guide
- **Purpose:** Identify why a Linux user cannot log in (local or directory-based).
- **Scope:** Local users, AD/LDAP users via SSSD.
- **Access methods:** Console, SSH, `su`.
- **Prerequisite:** Run as root (or via `sudo`).

---

## Fast triage (run in order)
1. **Confirm user exists (NSS resolution)**  
   Command: `getent passwd <username>`  
   Expected: One passwd entry.  
   If no output, either the local user does not exist or directory services are unreachable.

2. **Check account lock state**  
   Command: `passwd -S <username>`  
   Expected: `P` (password set); `L` means locked and login is denied.

3. **Check account expiration**  
   Command: `chage -l <username>`  
   Expected: `Account expires: never` and `Password expires: <future date>`.

4. **Check login shell**  
   Command: `getent passwd <username> | cut -d: -f7`  
   Expected: `/bin/bash` or another valid shell. `/sbin/nologin` or `/bin/false` denies login.

5. **Check home directory**  
   Command: `ls -ld /home/<username>`  
   Expected: Owned by the user with execute (`x`) permission.  
   Fix if needed: `chown <username>:<username> /home/<username>` and `chmod 700 /home/<username>`.

6. **Check disk space and inodes**  
   Commands: `df -h /` and `df -i /`  
   Expected: Usage below 100% for both space and inodes.

7. **Check for a global login block**  
   Command: `ls -l /etc/nologin`  
   Expected: File does **not** exist (if present, only root can log in).  
   Remove when safe: `rm -f /etc/nologin`.

---

## Authentication & PAM
8. **Review authentication logs**  
   - RHEL / Rocky / Alma: `tail -n 50 /var/log/secure`  
   - Ubuntu / Debian: `tail -n 50 /var/log/auth.log`  
   Look for `pam_unix` / `pam_sss` authentication failures or account lock/expiration messages.

9. **Test local privilege escalation path**  
   Command: `su - <username>`  
   If this works but SSH fails, investigate `sshd` or PAM configuration.

---

## SSH-specific checks (remote login only)
10. **Check sshd allow/deny rules**  
    Command: `grep -E "AllowUsers|DenyUsers|AllowGroups|DenyGroups" /etc/ssh/sshd_config`  
    Expected: No matching deny rules for the user.

11. **Check SSH key permissions (key-based login)**  
    Commands: `chmod 700 /home/<username>/.ssh` and `chmod 600 /home/<username>/.ssh/authorized_keys`.

---

## Directory services (AD / LDAP)
12. **Verify SSSD status**  
    Command: `systemctl status sssd`  
    Expected: `active (running)`.

13. **Test identity lookup**  
    Command: `id <username>`  
    Expected: UID/GID returned. Hang or failure indicates a directory authentication problem.

---

## SELinux (RHEL family)
14. **Check SELinux mode**  
    Command: `getenforce`  
    `Enforcing` is OK, but denials may still block login.

15. **Check recent SELinux denials**  
    Command: `ausearch -m AVC -ts recent`

---

## Summary decision points
- `getent` fails → user or directory issue.
- `passwd -S` shows `L` → account locked.
- `chage` shows expired → account expired.
- Invalid shell → intentional denial.
- Home directory permissions wrong → login fails during session setup.
- Disk full → PAM session creation fails.
- `/etc/nologin` present → global login block.
- `sssd` down → domain users fail.

---

End of runbook.
