[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [SSH Hardening](index.md)

# Runbook: Enforce sshd MaxAuthTries

## Purpose
Set an explicit `MaxAuthTries` directive in `/etc/ssh/sshd_config` so SSH disconnects after a controlled number of failed authentication attempts. Compliance scans (for example, Qualys control 2234) fail when the directive is missing or outside the approved 1–4 range.

## Why this matters
- **Slows brute-force attempts.** Limiting retries forces attackers to reconnect, reducing the speed of password-guessing attacks.
- **Closes audit findings.** Scanners expect a defined value between 1 and 4; an absent directive triggers a failure even if sshd defaults might be acceptable.
- **Documents organizational policy.** Recording the retry threshold clarifies expectations for operations and security teams.

## Preconditions
- Target hosts: RHEL 8.x with sudo/root access to edit `/etc/ssh/sshd_config`.
- Inventory entries for affected hosts (for example, `inventories/vantls/hosts`).
- Change window to reload sshd; keep a second SSH session open to avoid lockout.

## Procedure
1. **Review or override defaults** (the role defaults to 3 attempts within the required 1–4 range):
   ```yaml
   sshd_config_path: /etc/ssh/sshd_config
   sshd_max_auth_tries: 3
   ```
2. **Run the hardening playbook** against the impacted host or group:
   ```bash
   ansible-playbook playbooks/lnx-os-hardening.yml \
     -i inventories/vantls/hosts \
     --limit <target_host_or_group> \
     -e 'sshd_max_auth_tries=3'
   ```
   The `sshd_max_auth_tries.yml` task removes any existing directives, writes `MaxAuthTries <value>` before any `Match` blocks, validates syntax with `sshd -t`, and triggers the `restart sshd` handler.
3. **Validate on a target host** after the play completes:
   ```bash
   grep '^MaxAuthTries' /etc/ssh/sshd_config
   sudo sshd -t -f /etc/ssh/sshd_config
   sudo systemctl reload sshd  # if the handler did not already reload
   ```

## Rollback
- Rerun the play with a different compliant value (1–4) to adjust the threshold.
- To stop enforcing the setting, set `sshd_max_auth_tries` to an empty string and rerun the play, then manually remove the directive and reload sshd if desired.

## Notes
- Keeping the value at or below 4 aligns with common hardening baselines and prevents false positives in compliance scans.
- Consider pairing with `MaxSessions` or connection rate limiting (e.g., firewall rules or fail2ban) if stronger throttling is required.
