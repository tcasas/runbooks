# Runbook: Restrict permissions on `/etc/cron.monthly`

## Purpose
Address Qualys control 7347 for RHEL 8.x that expects the `/etc/cron.monthly` directory to be owned by root with restrictive permissions (`rwx------`). This limits read or execute access to scheduled monthly jobs that can reveal host or network details.

## Preconditions
- Target host: Red Hat Enterprise Linux 8.x.
- Access: sudo/root privileges.
- Confirm whether any non-root accounts must manage monthly jobs; if so, document the exception before tightening permissions.
- Approved change window (cron jobs run automatically and may be sensitive to permission changes).

## Steps
1. **Inspect current ownership and permissions**
   ```bash
   sudo ls -ld /etc/cron.monthly
   sudo find /etc/cron.monthly -maxdepth 1 -type f -printf '%M %u:%g %p\n'
   ```
   - If the directory is missing, document that state for the scanner as an acceptable result.

2. **Set secure ownership and mode**
   ```bash
   sudo chown root:root /etc/cron.monthly
   sudo chmod 700 /etc/cron.monthly
   ```
   - `700` satisfies the Qualys expected pattern `rwx------` while preserving execute permission needed for cron to traverse the directory. Do **not** use `600`, which would block cron from reading entries.

3. **Verify compliance state**
   ```bash
   sudo ls -ld /etc/cron.monthly
   sudo stat -c '%U:%G:%A:%n' /etc/cron.monthly
   ```
   - Expected output example: `root:root:rwx------:/etc/cron.monthly`.

4. **Handle exceptions (if needed)**
   - If business requirements mandate broader access (e.g., automation user), set the minimal necessary permissions (such as `750`) and record the approved exception in the ticket.

5. **Re-run the scan**
   - Trigger the Qualys control 7347 check or your internal compliance job to confirm the finding is resolved or that the documented exception is recognized.

## Rollback
- Restore the previous mode if a documented exception requires it (example: `sudo chmod 750 /etc/cron.monthly`).
- If ownership must differ per policy, reapply it (example: `sudo chown root:wheel /etc/cron.monthly`).

## Notes
- Keep the directory owned by root to prevent tampering with scheduled jobs.
- Review file-level permissions inside `/etc/cron.monthly` if they contain sensitive data; align them to business needs while keeping cron executable by root.
