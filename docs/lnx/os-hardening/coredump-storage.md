[Runbooks Index](../../index.md) / [Linux](../index.md) / [OS Hardening](index.md)

# Runbook: Configure systemd coredump storage to `none`

This runbook explains how to apply the Red Hat Enterprise Linux hardening task that disables persistent coredump storage by setting `Storage=none` and limits coredump processing with `ProcessSizeMax=0` in `/etc/systemd/coredump.conf` via Ansible.

## Prerequisites
- Control node has Ansible installed.
- Target hosts are reachable over SSH and listed in `inventory/hosts` with valid credentials.
- Remote user can escalate privileges (`become: true`) to write `/etc/systemd/coredump.conf`.
- The repository files are present on the control node.

## Procedure
1. **Review inventory**
   - Ensure the target hosts are listed under the desired group in `inventory/hosts` and have the correct `ansible_user` and `ansible_become` settings.

2. **Run only the coredump task** (recommended for focused rollout)
   ```bash
   ansible-playbook -i inventory/hosts playbooks/lnx-os-hardening.yml --tags coredump
   ```

3. **Run the full hardening playbook** (if broader changes are desired)
   ```bash
   ansible-playbook -i inventory/hosts playbooks/lnx-os-hardening.yml
   ```

4. **Optional dry-run**
   - Append `--check` to either command above to preview changes without applying them.

## Verification
- On the target host, confirm the settings:
  ```bash
  sudo grep -E '^(Storage=none|ProcessSizeMax=0)$' /etc/systemd/coredump.conf
  ```
  The command should return both `Storage=none` and `ProcessSizeMax=0` under the `[Coredump]` section. If the file is missing or the lines are absent, re-run step 2.

## Troubleshooting
- **Playbook fails due to missing Ansible modules**: Install Ansible on the control node (e.g., `pip install ansible`).
- **Permission denied writing `/etc/systemd/coredump.conf`**: Verify the remote user can use `sudo` or set `become: true` with proper credentials in the inventory.
- **Setting not applied**: Re-run with `-vvv` for verbose output and ensure no host-specific overrides of `common_hardening_tasks` omit `coredump.yml`.
