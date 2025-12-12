# Runbook: Configure SSH daemon MAC algorithms

## Purpose
Provide repeatable steps to enforce approved SSH MAC algorithms using the `lnx-os-hardening` role. This addresses compliance findings where `MACs` is unset or weak in `/etc/ssh/sshd_config`.

**What are MACs?**
- **MAC stands for “Message Authentication Code,”** a keyed digest that provides packet integrity and authenticity. In SSH, the `MACs` directive selects the algorithms used to protect each packet’s integrity.
- The approved algorithms in this runbook (for example, `hmac-sha2-512-etm@openssh.com` and `hmac-sha2-256-etm@openssh.com`) ensure sshd negotiates strong integrity checks during session setup.

## Preconditions
- Ansible control node with access to target hosts via SSH.
- Inventory entry for the target hosts (example: `inventories/vantls/hosts`).
- Privileged escalation (sudo) permitted on the targets.
- Optional: customize MAC algorithms or the SSH config path via variables.

## Procedure
1. **Review or adjust defaults if needed**
   - Default SSH config path: `sshd_config_path: /etc/ssh/sshd_config`.
   - Default MAC algorithms (ordered strongest first):
     ```yaml
     sshd_macs:
       - hmac-sha2-512-etm@openssh.com
       - hmac-sha2-256-etm@openssh.com
       - hmac-sha2-512
       - hmac-sha2-256
     ```
   - Override per environment in `group_vars` or via `-e` if different MACs or config path are required.

2. **Run the hardening playbook**
   - Execute against the relevant hosts or group:
     ```bash
     ansible-playbook playbooks/lnx-os-hardening.yml \
       -i inventories/vantls/hosts \
       --limit <target_host_or_group>
     ```
   - The `sshd_macs.yml` task removes any existing `MACs` lines, writes a single directive with the approved algorithms **before any `Match` blocks** (to avoid invalid placement), and triggers the `restart sshd` handler after syntax validation (`sshd -t`).

3. **Customize on the command line (optional)**
   - To test different MACs without editing vars files:
     ```bash
     ansible-playbook playbooks/lnx-os-hardening.yml \
       -i inventories/vantls/hosts \
       --limit <target_host_or_group> \
       -e 'sshd_macs=["hmac-sha2-512-etm@openssh.com","hmac-sha2-256-etm@openssh.com"]'
     ```

## Verification
- On a target host, confirm the `MACs` directive:
  ```bash
  grep '^MACs' /etc/ssh/sshd_config
  ```
- Validate SSHD configuration and service state:
  ```bash
  sudo sshd -t -f /etc/ssh/sshd_config
  systemctl status sshd
  ```
- Attempt an SSH connection and verify negotiation uses one of the approved MACs (e.g., `ssh -vv <host>` and check `MAC` in debug output).

## Troubleshooting
- If the validation task fails with an error like `Directive 'MACs' is not allowed within a Match block`, ensure all existing `MACs` lines are removed and that the `MACs` directive is placed **before** the first `Match` block. Re-run the playbook after correcting placement.

## Rollback
- Restore previous SSH configuration from backup or version control if available.
- To remove enforced MACs, set `sshd_macs: []` and rerun the playbook; the task will delete any existing `MACs` directives, or manually edit `/etc/ssh/sshd_config` and restart sshd.

## Notes
- The handler restarts `sshd` after validation to apply changes immediately.
- Ensure SSH session persistence (e.g., use a second session) when restarting `sshd` on remote systems.
