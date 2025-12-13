# Runbook: Enforce sshd ClientAliveInterval

## Purpose
Set an explicit `ClientAliveInterval` directive in `/etc/ssh/sshd_config` so SSH sessions receive server keepalives within a compliant timeout window. Compliance scans report a failure when this setting is missing or outside the required range.

## Why this matters
- **Reduces orphaned sessions.** Keepalives allow sshd to detect idle or disconnected clients sooner, avoiding lingering authenticated sessions.
- **Closes audit findings.** The control expects a value between 1 and 300 seconds; omitting the directive triggers a failure even if sshd defaults are acceptable.
- **Documents organizational policy.** Recording the chosen interval in configuration and automation clarifies the intended timeout for operations and security teams.

## Preconditions
- Target hosts: RHEL 8.x with sudo/root access for editing `/etc/ssh/sshd_config`.
- Inventory entries for affected hosts (for example, `inventories/vantls/hosts`).
- Change window to reload sshd; keep a second SSH session open to avoid lockout.

## Procedure
1. **Choose an interval (seconds) between 1 and 300.** The default in the hardening role is `300`. Use a lower value if business requirements demand quicker idle detection.
2. **Run the hardening playbook** against the impacted host or group:
   ```bash
   ansible-playbook playbooks/lnx-os-hardening.yml \
     -i inventories/vantls/hosts \
     --limit <target_host_or_group> \
     -e 'sshd_client_alive_interval=300'
   ```
   - The `sshd_client_alive_interval.yml` task removes any existing directive, writes `ClientAliveInterval <value>` before any `Match` blocks, validates syntax with `sshd -t`, and triggers the `restart sshd` handler.
3. **Validate on a target host** after the play completes:
   ```bash
   grep '^ClientAliveInterval' /etc/ssh/sshd_config
   sudo sshd -t -f /etc/ssh/sshd_config
   sudo systemctl reload sshd  # if the handler did not already reload
   ```
4. **Confirm behavior (optional):** Initiate an SSH session and leave it idle longer than the configured interval to ensure keepalive probes occur and timeouts align with expectations.

## Rollback
- Re-run the play with a different value within 1–300 seconds to adjust the interval.
- To remove enforcement, set `sshd_client_alive_interval` to an empty string and rerun the play; then manually remove the directive and reload sshd.

## Notes
- Keep `ClientAliveInterval` above 0; a value of 0 disables the keepalive and will fail the compliance check.
- Pair this setting with `ClientAliveCountMax` if you need to limit how many unanswered probes are allowed before disconnecting a client.
