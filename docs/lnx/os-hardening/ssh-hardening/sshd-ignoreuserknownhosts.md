# Runbook: Enforce sshd IgnoreUserKnownHosts

## Purpose
Explain why and how to enforce `IgnoreUserKnownHosts` in `/etc/ssh/sshd_config` using the `lnx-os-hardening` role. Compliance scans flag a missing or unset `IgnoreUserKnownHosts` directive because host-based authentication may otherwise consume per-user host key trust decisions, creating inconsistent access expectations and widening the attack surface. Setting this value explicitly ensures sshd either **ignores** or **honors** user `~/.ssh/known_hosts` according to policy (default in this role: `yes`, to ignore) and documents the intent.

## Why this is necessary
- **Control the trust anchor for host-based authentication.** Without an explicit directive, sshd may consider user-maintained host key entries during `HostbasedAuthentication`, allowing users to influence server-level trust.
- **Reduce false positives in audits.** Scanners report the directive as missing; explicitly setting it closes the finding and signals deliberate configuration.
- **Match organizational hardening policy.** The role defaults to `IgnoreUserKnownHosts: yes`, ensuring only system-wide host keys govern host-based authentication, aligning with least-privilege expectations.

## Preconditions
- Ansible control node with SSH access to targets.
- Sudo privileges on managed hosts.
- Inventory entries for the target hosts (for example `inventories/vantls/hosts`).
- Optional: Override `sshd_ignore_user_known_hosts` or `sshd_config_path` in inventory/group vars if your policy differs.

## Procedure
1. **Review defaults** (override if needed):
   ```yaml
   sshd_config_path: /etc/ssh/sshd_config
   sshd_ignore_user_known_hosts: "yes"
   ```
2. **Run the hardening playbook** for the relevant hosts or group:
   ```bash
   ansible-playbook playbooks/lnx-os-hardening.yml \
     -i inventories/vantls/hosts \
     --limit <target_host_or_group>
   ```
   The `sshd_ignore_user_known_hosts.yml` task removes any existing directives, writes a single `IgnoreUserKnownHosts <value>` line, validates syntax with `sshd -t`, and triggers the `restart sshd` handler.
3. **Customize per run (optional)**: supply a different setting at runtime without editing files:
   ```bash
   ansible-playbook playbooks/lnx-os-hardening.yml \
     -i inventories/vantls/hosts \
     --limit <target_host_or_group> \
     -e 'sshd_ignore_user_known_hosts=no'
   ```

## Verification
- Confirm the directive on a target host:
  ```bash
  grep '^IgnoreUserKnownHosts' /etc/ssh/sshd_config
  ```
- Validate sshd syntax and service state:
  ```bash
  sudo sshd -t -f /etc/ssh/sshd_config
  systemctl status sshd
  ```
- If host-based authentication is used, attempt an SSH connection and verify behavior aligns with the configured setting (e.g., known host prompts should not appear when set to `yes`).

## Troubleshooting
- **`sshd -t` fails**: check for stray `IgnoreUserKnownHosts` lines inside `Match` blocks; ensure the role’s task can remove them or adjust manually, then rerun.
- **Unexpected prompts**: confirm `HostbasedAuthentication` is enabled/disabled as intended; `IgnoreUserKnownHosts` only affects host-based workflows, not standard password/key auth.

## Rollback
- Set `sshd_ignore_user_known_hosts: ""` or remove the variable to stop enforcing the directive, then rerun the playbook (the task will delete existing lines).
- Manually edit `/etc/ssh/sshd_config` to restore prior behavior and restart sshd.
