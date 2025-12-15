# Linux User Login Failure — Single-Block Debug Runbook
# =====================================================
#
# Purpose:
#   Identify why a Linux user cannot log in (local or directory-based).
#
# Scope:
#   - Local users
#   - AD / LDAP users via SSSD
#   - Console, SSH, su
#
# Run as root (or via sudo).
#
# -----------------------------------------------------

Index: Fast Triage (run in order)

# 1. Confirm user exists (NSS resolution)
getent passwd <username>
> expected: one passwd entry returned

# If no output:
# - local user does not exist OR
# - directory services unreachable

# 2. Check account lock state
passwd -S <username>
> expected: P (password set)
> L = locked (login denied)

# 3. Check account expiration
chage -l <username>
> expected:
>   Account expires: never
>   Password expires: future date

# 4. Check login shell
getent passwd <username> | cut -d: -f7
> expected: /bin/bash (or other valid shell)
> /sbin/nologin or /bin/false = login denied

# 5. Check home directory
ls -ld /home/<username>
> expected: owned by user, execute (x) permission present

# Fix if needed:
# chown <username>:<username> /home/<username>
# chmod 700 /home/<username>

# 6. Check disk space and inodes
df -h /
df -i /
> expected: < 100% usage

# 7. Check for global login block
ls -l /etc/nologin
> expected: file does NOT exist
> if exists: only root can log in

# Remove when safe:
# rm -f /etc/nologin

Index: Authentication & PAM

# 8. Review authentication logs
# RHEL / Rocky / Alma:
tail -n 50 /var/log/secure

# Ubuntu / Debian:
tail -n 50 /var/log/auth.log

> look for:
>   pam_unix authentication failure
>   pam_sss authentication failure
>   account locked / expired

# 9. Test local privilege escalation path
su - <username>
> if this works but SSH fails → sshd or PAM issue

Index: SSH-Specific Checks (remote login only)

# 10. Check sshd allow/deny rules
grep -E "AllowUsers|DenyUsers|AllowGroups|DenyGroups" /etc/ssh/sshd_config
> expected: no matching deny rules for user

# 11. Check SSH key permissions (key-based login)
chmod 700 /home/<username>/.ssh
chmod 600 /home/<username>/.ssh/authorized_keys

Index: Directory Services (AD / LDAP)

# 12. Verify SSSD status
systemctl status sssd
> expected: active (running)

# 13. Test identity lookup
id <username>
> expected: uid/gid returned
> hang or failure = directory auth problem

Index: SELinux (RHEL family)

# 14. Check SELinux mode
getenforce
> Enforcing is OK, but denials may block login

# 15. Check recent SELinux denials
ausearch -m AVC -ts recent

Index: Summary Decision Points

# - getent fails → user / directory issue
# - passwd -S shows L → account locked
# - chage expired → account expired
# - bad shell → intentional denial
# - home perms wrong → login drops
# - disk full → PAM session fails
# - /etc/nologin present → global block
# - sssd down → domain users fail

# End of runbook
# -----------------------------------------------------
