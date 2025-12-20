[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [File Hardening](index.md)

# Runbook: Review and remediate unexpected SUID files (Qualys 8325)

## Purpose
Address Qualys control 8325 on Red Hat Enterprise Linux 8.x hosts, which flags executables with the `setuid` bit enabled. Use this runbook to verify the flagged files, remove the SUID bit where not justified, and document approved exceptions.

## Preconditions
- Target host: Red Hat Enterprise Linux 8.x.
- Access: sudo/root privileges.
- Approved change window (removing SUID may impact utilities that rely on elevated privileges).
- List of SUID files from the scanner or security team (example findings from Qualys: `/usr/bin/chage`, `/usr/bin/gpasswd`, `/usr/bin/newgrp`, `/usr/bin/mount`, `/usr/bin/su`, `/usr/bin/umount`, `/usr/bin/pkexec`, `/usr/bin/crontab`, `/usr/bin/sudo`, `/usr/bin/passwd`, `/usr/bin/chfn`, `/usr/bin/chsh`, `/usr/bin/at`, `/usr/bin/fusermount`, `/usr/bin/ksu`, `/usr/bin/staprun`, `/usr/sbin/grub2-set-bootflag`, `/usr/sbin/pam_timestamp_check`, `/usr/sbin/unix_chkpwd`, `/usr/sbin/userhelper`, `/usr/sbin/mount.nfs`, `/usr/libexec/cockpit-session`, `/usr/libexec/qemu-bridge-helper`).

## Steps
1. **Inventory current SUID files**
   ```bash
   sudo find / -xdev -type f -perm -4000 -printf '%u:%g:%M:%p\n' 2>/dev/null | sort
   ```
   - Compare output to your approved allowlist and the scanner's findings.

2. **Validate package ownership (optional but recommended)**
   ```bash
   rpm -qf /usr/bin/pkexec
   rpm -qf /usr/libexec/qemu-bridge-helper
   ```
   - Identify which packages delivered the binaries before changing permissions or removing packages.

3. **Remove SUID bit for unapproved files**
   ```bash
   sudo chmod u-s /usr/bin/pkexec /usr/libexec/qemu-bridge-helper /usr/bin/ksu /usr/bin/staprun
   ```
   - Adjust the file list to match your findings. If only one file needs change, target it individually (e.g., `chmod u-s /usr/bin/pkexec`).
   - For fleet-wide automation, use the existing Ansible playbook `playbooks/lnx-manage-suid-sgid.yml` with `suid_sgid_enforce: true` and an allowlist (`suid_sgid_additional_allowed`) matching approved exceptions.

4. **Verify permissions are cleared**
   ```bash
   stat -c '%A %n' /usr/bin/pkexec /usr/libexec/qemu-bridge-helper /usr/bin/ksu /usr/bin/staprun
   sudo find / -xdev -type f -perm -4000 -printf '%p\n' 2>/dev/null
   ```
   - Expect cleared SUID bits (`-rwxr-xr-x`) and the final `find` output to show only approved entries.

5. **Re-run compliance scan (if available)**
   - Trigger Qualys control 8325 or your internal scan to confirm the finding is resolved.

## Rollback
- Reapply SUID if required for a documented exception:
  ```bash
  sudo chmod u+s <path>
  ```
- Record the justification and exception approval in the ticket.

## Notes
- Maintain a centralized allowlist with business justifications to reduce repeated false positives.
- Removing SUID from core utilities (e.g., `su`, `passwd`, `sudo`, `mount`, `umount`, `crontab`) can disrupt normal operations; ensure business approval before modifying them.
- If a privileged helper is unnecessary, consider removing the delivering package instead (e.g., `polkit` for `/usr/bin/pkexec`, `qemu-kvm`/libvirt for `qemu-bridge-helper`, SystemTap packages for `staprun`).
