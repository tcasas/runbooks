# Runbook: Review and remediate unexpected SGID files

## Purpose
Address Qualys control 8326 (RHEL 8.x) that flags SGID files granting elevated group privileges. Review and remove the `setgid` bit from executables that are not explicitly required by the business (example findings: `/usr/bin/write`, `/usr/bin/locate`).

## Preconditions
- Target host: Red Hat Enterprise Linux 8.x.
- Access: sudo/root privileges.
- Approved change window (removing SGID may impact utilities that rely on group elevation).
- List of SGID files provided by the scanner or security team.

## Steps
1. **Inventory current SGID files**
   ```bash
   sudo find / -xdev -type f -perm -2000 -printf '%u:%g:%M:%p\n' 2>/dev/null | sort
   ```
   - Compare results to approved exceptions. Typical flagged examples from Qualys: `root:tty:rwxr-sr-x:/usr/bin/write`, `root:slocate:rwx--s--x:/usr/bin/locate`.

2. **Validate package ownership (optional)**
   ```bash
   rpm -qf /usr/bin/write
   rpm -qf /usr/bin/locate
   ```
   - Confirms which package delivered the file before changing permissions.

3. **Remove SGID bit for unapproved files**
   ```bash
   sudo chmod g-s /usr/bin/write /usr/bin/locate
   ```
   - Adjust the file list to match the findings. If only one file needs change, target it individually.

4. **Verify permissions are cleared**
   ```bash
   stat -c '%A %n' /usr/bin/write /usr/bin/locate
   sudo find / -xdev -type f -perm -2000 -printf '%p\n' 2>/dev/null
   ```
   - Expect the files to no longer show the `s` bit and the final `find` output to contain only approved exceptions.

5. **Re-run compliance scan (if available)**
   - Trigger the Qualys control 8326 check or run your internal scan to confirm the finding is resolved.

## Rollback
- Reapply SGID if required for a documented exception:
  ```bash
  sudo chmod g+s <path>
  ```
- Record the justification and exception approval in the ticket.

## Notes
- Keep a centralized allowlist of SGID files that are business-approved to avoid repeated false positives.
- For fleet-wide enforcement, manage permissions via configuration management (e.g., Ansible `file` module with `mode: 'u=rwxs,g=rx,o=rx'`).
