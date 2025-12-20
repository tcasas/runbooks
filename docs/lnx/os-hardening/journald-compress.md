[Runbooks Index](../../index.md) / [Linux](../index.md) / [OS Hardening](index.md)

# Runbook: Ensure journald log compression is configured

## Purpose
Set the `Compress` option in `/etc/systemd/journald.conf` on RHEL 8.x systems so that logs are compressed (recommended) or explicitly set per business requirements.

## Preconditions
- Target host: Red Hat Enterprise Linux 8.x with systemd.
- Access: sudo privileges on the host.
- Change window approved (restart of `systemd-journald` briefly interrupts log ingestion but not logging clients).

## Steps
1. **Check current value**
   ```bash
   sudo grep -n '^Compress=' /etc/systemd/journald.conf
   sudo systemd-analyze cat-config systemd/journald.conf | grep Compress
   ```
   - Expect `Compress=yes` or `Compress=no`. If no line is returned, the setting is absent.

2. **Set desired value** (default secure setting is `Compress=yes`)
   ```bash
   sudo sh -c "grep -q '^Compress=' /etc/systemd/journald.conf \
     && sed -i 's/^Compress=.*/Compress=yes/' /etc/systemd/journald.conf \
     || echo 'Compress=yes' >> /etc/systemd/journald.conf"
   ```
   - Replace `Compress=yes` with `Compress=no` only if the business requires uncompressed logs and the exception is documented.

3. **Restart journald**
   ```bash
   sudo systemctl restart systemd-journald
   ```

4. **Verify**
   ```bash
   systemctl is-active systemd-journald
   systemd-analyze cat-config systemd/journald.conf | grep Compress
   sudo journalctl --rotate
   ```
   - Confirm `systemctl` reports `active` and the effective config shows the desired `Compress=` value.

5. **Document and close**
   - Record the chosen value (`yes` or `no`), justification, and time of change in your ticketing system.
   - Re-run the scanner to confirm the control is passing.

## Rollback
- Restore the previous `/etc/systemd/journald.conf` from backup if needed, then `sudo systemctl restart systemd-journald`.

## Notes
- Compression reduces disk growth for large journal entries but does not replace log retention or archival policies.
- If using configuration management (e.g., Ansible), manage `Compress=` via template or lineinfile to keep systems consistent.
