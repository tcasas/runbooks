# Runbook: Ensure `httpd` service is appropriately disabled

## Purpose
Resolve the Qualys control (ID 9881) requiring the Apache HTTP Server (`httpd`) to be disabled unless there is a documented business need. Applies to Red Hat Enterprise Linux 8.x systems managed via systemd.

## Preconditions
- Access to the target host with sudo privileges.
- Change window approved if stopping a production service.
- Confirm whether the host is intended to run a web service.

## Procedure
1. **Check current service state**
   ```bash
   sudo systemctl status httpd
   sudo systemctl is-enabled httpd
   ```
   - Expected compliant states: `disabled` or `Service Not Found`.

2. **If `httpd` is NOT required**
   - Stop and disable immediately:
     ```bash
     sudo systemctl disable --now httpd
     ```
   - Optional: remove the package to reduce attack surface:
     ```bash
     sudo dnf remove -y httpd
     ```

3. **If `httpd` IS required**
   - Ensure intentional enablement and start:
     ```bash
     sudo systemctl enable --now httpd
     ```
   - Harden configuration:
     - Restrict listening interfaces/ports (e.g., `Listen 127.0.0.1:8080`).
     - Limit access via firewalld/iptables to authorized sources.
     - Enforce TLS and set `ServerTokens Prod` and `ServerSignature Off` in `httpd.conf`.
     - Keep packages patched: `sudo dnf update httpd`.
     - Maintain SELinux in enforcing mode with correct contexts for served content.
   - Document the business justification and associated exception if scanner requires `disabled` state.

4. **Verification**
   - Re-check service state:
     ```bash
     sudo systemctl is-enabled httpd
     sudo systemctl is-active httpd
     ```
   - Expected results:
     - If not needed: `disabled` (and `inactive`/`failed` if stopped).
     - If needed: `enabled` and `active` with justification recorded.
   - Re-run Qualys or internal compliance check to confirm the finding is resolved or accepted.

## Rollback
- To re-enable a previously disabled service (if business needs change):
  ```bash
  sudo systemctl enable --now httpd
  ```
- To reinstall after removal: `sudo dnf install -y httpd`, then apply hardened configuration before enabling.

## Notes
- Stopping `httpd` on a production host will interrupt any hosted applications; coordinate with stakeholders.
- If configuration management (e.g., Ansible) manages `httpd`, apply changes through the automation to avoid drift.
