# Runbook: Audit and remediate SUID/SGID binaries

## Purpose
Use the `playbooks/lnx-manage-suid-sgid.yml` playbook to inventory setuid/setgid executables, compare them to an allowlist with business justifications, and optionally remediate unexpected entries.

## Preconditions
- Inventory/scan results that list flagged SUID/SGID files.
- Access to the Ansible controller with the repository checked out.
- Privileged access on target hosts (sudo/root) and approved change window when enabling enforcement.
- Python and `ansible-core` installed on the controller.

## Steps
1. **Review/adjust allowlist and scope**
   - Baseline allowlist and justifications live in `suid_sgid_baseline` inside `playbooks/lnx-manage-suid-sgid.yml`.
   - Override or extend defaults via inventory/extra vars:
     ```bash
     cat > extra-suid-sgid.yml <<'VARS'
     suid_sgid_search_paths:
       - "/"
       - "/usr/local"
     suid_sgid_additional_allowed:
       /usr/local/bin/custom-helper: "Required by legacy backup tooling"
     suid_sgid_report_dir: "./reports"
     VARS
     ```

2. **Run in audit mode (no changes)**
   ```bash
   ansible-playbook playbooks/lnx-manage-suid-sgid.yml -i <inventory> -e @extra-suid-sgid.yml
   ```
   - Output lists unexpected and retained binaries per host and saves a report per host to `suid_sgid_report_dir`.

3. **Enable enforcement (optional)**
   - Turn on remediation to strip privilege bits and optionally remove packages delivering unwanted binaries:
     ```bash
     cat > enforce-suid-sgid.yml <<'VARS'
     suid_sgid_enforce: true
     suid_sgid_removal_packages:
       - polkit
       - krb5-workstation
     VARS

     ansible-playbook playbooks/lnx-manage-suid-sgid.yml -i <inventory> -e @extra-suid-sgid.yml -e @enforce-suid-sgid.yml
     ```
   - Verify change approvals before removing packages; adjust package list to match findings.

4. **Validate remediation**
   - Re-run the playbook in audit mode or run a manual check on a sample host:
     ```bash
     sudo find / -xdev -perm /6000 -type f -printf '%p\n' 2>/dev/null | sort
     ```
   - Confirm only approved binaries remain and reports show empty unexpected lists.

5. **Document exceptions**
   - For binaries that must retain SUID/SGID, record the justification in `suid_sgid_additional_allowed` (inventory vars) so future runs treat them as expected.

## Rollback
- Reapply SUID/SGID bits for a reverted change if required by policy:
  ```bash
  sudo chmod u+s /path/to/binary
  sudo chmod g+s /path/to/binary
  ```
- Reinstall removed packages when justified:
  ```bash
  sudo yum install <package>
  ```

## Notes
- Keep reports under version control or attach them to the change record for auditability.
- When scanning large filesystems, limit `suid_sgid_search_paths` to relevant mount points (e.g., `/`, `/usr`, `/opt`) to reduce runtime.

## Recommended remediation approach
- **Assess necessity per binary:** Many SUID/SGID utilities (e.g., `passwd`, `su`, `sudo`, `crontab`, `mount`, `umount`) are commonly required. Remove SUID/SGID only when the functionality is unnecessary for your environment.
- **Remove SUID/SGID where appropriate:**
  - Remove SUID bit (owner): `chmod u-s <path>`
  - Remove SGID bit (group): `chmod g-s <path>`
  - Example: `chmod u-s /usr/bin/pkexec` if polkit-based escalation is not needed.
- **Harden sudo instead of removing it:** If `sudo` must stay, restrict privileges in `/etc/sudoers` (least privilege, require TTY, logging, restricted command sets) instead of stripping the SUID bit.
- **Consider removing unneeded packages:** If a privileged tool is unnecessary, remove or disable the delivering package (e.g., `polkit`, `qemu-bridge-helper`, FUSE utilities, `mount.nfs`, `ksu`, `staprun`, `cockpit-session`). Adjust to match your environment and approvals.
- **Preserve system integrity:** Some binaries (e.g., `unix_chkpwd`, `pam_timestamp_check`, `mount`/`umount`) support PAM or core utilities—removing SUID/SGID can break authentication or mounting. Validate changes in staging before broad rollout.
- **Monitor for drift:** Schedule a periodic inventory of SUID/SGID files (e.g., `find / -xdev \( -perm -4000 -o -perm -2000 \) -type f -print`) and alert on unexpected additions.
- **Re-validate after changes:** Re-run this playbook or a vulnerability scan to confirm only approved binaries remain and host functionality is intact.
