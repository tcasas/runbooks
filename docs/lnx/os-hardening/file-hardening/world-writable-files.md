[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [File Hardening](index.md)

# Runbook: Audit and remediate world-writable files

## Purpose
Use the os-hardening role's world-writable task set (or the `playbooks/lnx-audit-world-writable.yml` playbook) to locate world-writable files, compare them to an allowlist with documented justifications, optionally strip other-write permissions, and persist per-host reports.

## Preconditions
- Inventory or vulnerability scan that flags world-writable files.
- Access to the Ansible controller with this repository checked out.
- Privileged access on target hosts (sudo/root) and an approved change window when enabling enforcement.
- Python and `ansible-core` installed on the controller.

## Steps
1. **Adjust scope and allowlist**
   - Defaults (used by the role and the standalone playbook):
     - `world_writable_search_paths`: `["/"]`
     - `world_writable_allow_map`: `{}` (map of path -> justification)
     - `world_writable_enforce`: `false`
     - `world_writable_report_dir`: `/tmp`
   - Override via inventory or extra vars:
     ```bash
     cat > world-writable-vars.yml <<'VARS'
     world_writable_search_paths:
       - "/"
       - "/opt"
     world_writable_allow_map:
       /tmp/custom.sock: "Socket required by in-house agent"
     world_writable_enforce: false  # set true to remove other-write
     world_writable_report_dir: "./reports/world-writable"
     VARS
     ```

2. **Run in audit mode (no changes)**
   - Using the role within your playbook inventory:
     ```bash
     ansible-playbook -i <inventory> playbooks/site.yml -e @world-writable-vars.yml --tags world_writable
     ```
   - Or run the standalone playbook:
     ```bash
     ansible-playbook playbooks/lnx-audit-world-writable.yml -i <inventory> -e @world-writable-vars.yml
     ```
   - Output highlights unexpected vs allowed files and writes a report per host under `world_writable_report_dir`.

3. **Enable enforcement (optional)**
   - Turn on enforcement to remove other-write permissions from unexpected files:
     ```bash
     cat > world-writable-enforce.yml <<'VARS'
     world_writable_enforce: true
     VARS

     ansible-playbook playbooks/lnx-audit-world-writable.yml -i <inventory> -e @world-writable-vars.yml -e @world-writable-enforce.yml
     ```
   - Review approvals before enabling enforcement and verify allowlist coverage to avoid disrupting legitimate workflows.

4. **Validate results**
   - Re-run in audit mode to confirm the unexpected list is empty, or manually sample a host:
     ```bash
     sudo find / -xdev -type f -perm -0002 -printf '%p\n' 2>/dev/null | sort
     ```
   - Confirm reports reflect the updated state and that critical applications continue to function.

5. **Document exceptions**
   - Record approved world-writable paths with justifications in `world_writable_allow_map` (inventory or vars files) so future runs treat them as expected.

## Rollback
- Restore other-write permission for a reverted change if required by policy:
  ```bash
  sudo chmod o+w /path/to/file
  ```
- If enforcement caused application issues, re-apply permissions for the affected files and update the allowlist with rationale.

## Notes
- Limit `world_writable_search_paths` to relevant mount points (e.g., `/`, `/var`, `/opt`) to reduce scan time on large systems.
- Reports are written on the controller; version them or attach to change tickets for auditability.
- The task set is tagged `world_writable` inside the os-hardening role to allow targeted execution.
