[Runbooks Index](../../index.md) / [Linux](../index.md) / [OS Hardening](index.md)

# Runbook: Ensure journald storage is configured

## Purpose
Set the `Storage` option in `/etc/systemd/journald.conf` on RHEL 8.x systems so that logs are stored according to business requirements (default: `persistent`).

## Preconditions
- Target host: Red Hat Enterprise Linux 8.x with systemd.
- Access: sudo privileges on the host.
- Change window approved (restarting `systemd-journald` briefly interrupts log ingestion but not logging clients).

## Steps
1. **Check current value**
   ```bash
   sudo grep -n '^Storage=' /etc/systemd/journald.conf
   sudo systemd-analyze cat-config systemd/journald.conf | grep Storage
   ```
   - Expect `Storage=persistent`, `Storage=volatile`, or `Storage=auto`. If no line is returned, the setting is absent.

2. **Set desired value** (default secure setting is `Storage=persistent`)
   ```bash
   sudo sh -c "grep -q '^Storage=' /etc/systemd/journald.conf \
     && sed -i 's/^Storage=.*/Storage=persistent/' /etc/systemd/journald.conf \
     || echo 'Storage=persistent' >> /etc/systemd/journald.conf"
   ```
   - Adjust `Storage=` to `volatile` or `auto` only if the business requires that behavior and the exception is documented.

3. **Restart journald**
   ```bash
   sudo systemctl restart systemd-journald
   ```

4. **Verify**
   ```bash
   systemctl is-active systemd-journald
   systemd-analyze cat-config systemd/journald.conf | grep Storage
   sudo journalctl --rotate
   ```
   - Confirm `systemctl` reports `active` and the effective config shows the desired `Storage=` value.

5. **Document and close**
   - Record the chosen value, justification, and time of change in your ticketing system.
   - Re-run the scanner to confirm the control is passing.

## Rollback
- Restore the previous `/etc/systemd/journald.conf` from backup if needed, then `sudo systemctl restart systemd-journald`.

## Notes
- `Storage=persistent` keeps journal logs across reboots. `volatile` keeps them only in memory; `auto` uses `/var/log/journal` if it exists otherwise RAM.
- If using configuration management (e.g., Ansible), manage `Storage=` via template or lineinfile to keep systems consistent.
