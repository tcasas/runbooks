# Ensure /tmp is mounted with security options

This runbook enables and configures the `tmp.mount` systemd unit so `/tmp` is mounted as a `tmpfs` with `noexec`, `nosuid`, and `nodev` options. It aligns with controls that require `/tmp` to be on a separate partition with restrictive mount flags.

## Playbook
- `playbooks/lnx-enable-tmp-mount.yml`
  - Runs the `lnx-os-hardening` role limited to the `tmp_mount.yml` task list.
  - Default mount options come from `roles/lnx-os-hardening/defaults/main.yml` and can be overridden with `tmp_mount_options`.

## Usage
1. Update your inventory to target the desired hosts.
2. Run the playbook with elevated privileges:
   ```bash
   ansible-playbook playbooks/lnx-enable-tmp-mount.yml --become
   ```
3. Verify `/tmp` is mounted with the expected options on the target hosts:
   ```bash
   ansible -m command -a "findmnt -n /tmp" <inventory_target>
   ```

## Notes
- The playbook un-masks, enables, and starts `tmp.mount`, and then confirms that `/tmp` is mounted as `tmpfs` with `noexec`, `nosuid`, and `nodev` flags.
- Override the mount options if business requirements differ:
  ```yaml
  tmp_mount_options: mode=1777,strictatime,noexec,nodev,nosuid
  ```
