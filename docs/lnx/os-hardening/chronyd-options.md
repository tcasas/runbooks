# Runbook: Configure `OPTIONS` in `/etc/sysconfig/chronyd`

## Purpose
Remediate Qualys finding 10664 by configuring the `OPTIONS` setting in `/etc/sysconfig/chronyd` so the `chronyd` service runs under the `chrony` user with business-approved flags.

`chronyd` is the Network Time Protocol (NTP) daemon on Red Hat Enterprise Linux. It continuously disciplines the system clock using authoritative time sources (NTP servers, hardware clocks, or other peers), even on hosts with unstable networks or intermittent connectivity. Keeping the clock synchronized is critical for log integrity, Kerberos authentication, certificates, and other security controls that depend on accurate timestamps.

## Preconditions
- Red Hat Enterprise Linux 8.x host with `chronyd` installed.
- Root or sudo privileges.
- Business-approved list of required chronyd options (at minimum, `-u chrony`).

## Procedure
1. **Inspect current configuration**
   ```bash
   sudo grep -n "^OPTIONS" /etc/sysconfig/chronyd || echo "OPTIONS not set"
   sudo systemctl cat chronyd | grep -n "EnvironmentFile"
   ```

2. **Update `/etc/sysconfig/chronyd`**
   - Edit the file and set the `OPTIONS` line. Minimum hardening:
     ```bash
     sudo sh -c 'echo "OPTIONS=\"-u chrony\"" > /etc/sysconfig/chronyd'
     ```
   - If additional flags are required, append them inside the quotes (e.g., `-s` to step clock on start, `-r` for RTC compensation).
   - Ensure ownership and permissions:
     ```bash
     sudo chown root:root /etc/sysconfig/chronyd
     sudo chmod 0644 /etc/sysconfig/chronyd
     ```

3. **Restart and validate**
   ```bash
   sudo systemctl restart chronyd
   sudo systemctl status --no-pager chronyd
   ps -C chronyd -o user,cmd
   ```

4. **Confirm effective options**
   ```bash
   ps -C chronyd -o args=
   sudo grep -n "^OPTIONS" /etc/sysconfig/chronyd
   ```
   - Verify the process is running as `chrony` and the command line reflects the configured options.

## Verification
- `grep` shows `OPTIONS="-u chrony ..."` in `/etc/sysconfig/chronyd`.
- `ps -C chronyd -o user,cmd` lists `chrony` as the user.
- `systemctl status chronyd` reports `active (running)` with no errors.
- Qualys or manual check confirms the expected option string.

## Rollback
- Restore the previous `/etc/sysconfig/chronyd` from backup or version control.
- Restart the service: `sudo systemctl restart chronyd`.

## Notes
- Do not remove options required by your environment (e.g., time stepping or RTC flags).
- If the service is managed by a configuration tool (Ansible, Puppet, etc.), update the corresponding templates to keep the setting enforced.
