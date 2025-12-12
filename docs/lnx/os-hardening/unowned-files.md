# Runbook: Audit and remediate unowned files

## Purpose
Address Qualys control 7418 (RHEL 8.x) that reports files or directories without an owning user or group (example findings: `/home/bgopal`, `/var/backups/svc_isebackup`). Prevent reuse of orphaned UIDs/GIDs by assigning ownership or removing stale content.

## Preconditions
- Target host: Red Hat Enterprise Linux 8.x.
- Access: sudo/root privileges.
- Inventory or scan output listing unowned paths.
- Approved ownership decisions (e.g., assign to `root:root` or to the service account that should own the files).

## Steps
1. **Collect current unowned paths**
   ```bash
   sudo find / -xdev \( -nouser -o -nogroup \) -printf '%p\n' 2>/dev/null | sort
   ```
   - Compare results with the scanner output. Typical Qualys findings include user home directories left behind after account removal.

2. **Audit with Ansible (no changes)**
   - Adjust search paths or reporting directory if needed:
     ```bash
     cat > unowned-vars.yml <<'VARS'
     unowned_search_paths:
       - "/"
       - "/var/backups"
     unowned_report_dir: "./reports/unowned"
     VARS
     ```
   - Run the playbook in audit mode:
     ```bash
     ansible-playbook -i <inventory> playbooks/lnx-find-unowned-files.yml -e @unowned-vars.yml
     ```
   - Review the per-host report written under `unowned_report_dir`.

3. **Remediate ownership (Ansible)**
   - Decide the target owners. You can set global defaults or per-path overrides:
     ```bash
     cat > unowned-remediate.yml <<'VARS'
     unowned_enforce: true
     unowned_default_owner: root
     unowned_default_group: root
     unowned_owner_map:
       /var/backups/svc_isebackup:
         owner: svc_isebackup
         group: svc_isebackup
     VARS

     ansible-playbook -i <inventory> playbooks/lnx-find-unowned-files.yml -e @unowned-vars.yml -e @unowned-remediate.yml
     ```
   - Files not listed in `unowned_owner_map` use the default owner/group.

4. **Manual cleanup (optional)**
   - Remove obsolete directories if they are no longer required:
     ```bash
     sudo rm -rf /home/bgopal
     ```
   - Alternatively, recreate the intended account before reassigning ownership.

5. **Validate**
   - Re-run the audit command or playbook to confirm no unowned paths remain:
     ```bash
     sudo find / -xdev \( -nouser -o -nogroup \) -printf '%p\n' 2>/dev/null | sort
     ```
   - Ensure the scanner or Qualys control 7418 reports clean results.

## Rollback
- If ownership was set incorrectly, adjust to the correct account:
  ```bash
  sudo chown <owner>:<group> <path>
  ```
- Restore removed directories from backup if needed.

## Notes
- Limit search paths to relevant mounts to reduce scan time on large systems.
- Keep a record of approved ownership mappings to avoid repeated exceptions in future scans.
