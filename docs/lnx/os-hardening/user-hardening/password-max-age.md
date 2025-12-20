[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [User Hardening](index.md)

# Runbook: Enforce maximum password age for Linux accounts

## Purpose
Address Qualys control 10732 requiring a maximum password age for users with local passwords on Red Hat Enterprise Linux 8.x. Ensures passwords expire within the policy window (default 90 days) using `login.defs` defaults and per-account settings.

## Preconditions
- Sudo/root access to the target host.
- Confirm the required password age policy (e.g., 90 days) with security/ops.
- Change window if widespread password expirations could impact users.

## Procedure
1. **Check global defaults**
   ```bash
   sudo grep -E '^PASS_MAX_DAYS' /etc/login.defs
   ```
   - Expected compliant value: `PASS_MAX_DAYS` set to the policy limit (default 90).

2. **Identify accounts with local passwords**
   ```bash
   sudo awk -F: '$2 !~ /^(!|\*)/ {print $1}' /etc/shadow
   ```
   - Review the list for service/system accounts that should remain locked.

3. **Inspect current password age per user**
   ```bash
   sudo chage --list <username>
   ```
   - `Maximum number of days between password change` should match policy.

4. **Remediate manually (per user)**
   ```bash
   sudo chage -M <max_days> <username>
   sudo chage -d 0 <username>   # (optional) force change at next login
   ```
   - Repeat for all users requiring compliance.

5. **Remediate via Ansible (preferred)**
   - In inventory or extra vars, set `password_max_days=<value>` if deviating from default 90.
   - Apply the hardening role:
     ```bash
     ansible-playbook -i <inventory> playbooks/lnx-os-hardening.yml --limit <host>
     ```
   - The role templates `/etc/login.defs` and enforces `password_expire_max` for each account with a password.

6. **Verify compliance**
   - Re-check steps 1 and 3 after remediation.
   - Re-run Qualys or internal scan to confirm the finding is cleared.

## Rollback
- To relax the maximum age for a user: `sudo chage -M <new_value> <username>`.
- To revert to previous `login.defs`, restore from backup or package default and rerun configuration management.

## Notes
- For accounts that should not allow interactive logins, lock them instead of extending password age: `sudo usermod -L <username>`.
- Coordinate with application owners before forcing password changes on service accounts to avoid outages.
