[Runbooks Index](../../index.md) / [Linux](../index.md) / [OS Hardening](index.md)

# Runbook: Enable and configure `systemd-journal-upload`

## Purpose
Resolve Qualys control 23777 on RHEL 8 hosts that requires the `systemd-journal-upload` service to be present and enabled so systemd journals can be forwarded to a remote collector.

## Preconditions
- Sudo access to the target host.
- URL for the upstream `systemd-journal-gatewayd` (or compatible) endpoint that should receive uploads (example: `https://logs.example.com:19532/upload`).
- SSL client key/cert configuration if the collector enforces mutual TLS.

## Procedure
1. **Check current service status**
   ```bash
   sudo systemctl status systemd-journal-upload || echo "service missing"
   sudo systemctl is-enabled systemd-journal-upload || echo "service missing"
   ```
   - If the service is missing, install the package in the next step.

2. **Install the service unit**
   ```bash
   sudo dnf install -y systemd-journal-remote
   ```
   - This package provides `systemd-journal-upload.service`.

3. **Configure the upload destination**
   Edit `/etc/systemd/journal-upload.conf`:
   ```ini
   [Upload]
   URL=https://<collector-host>:19532/upload
   # Uncomment and set if mutual TLS is required
   #ServerKeyFile=/etc/ssl/private/journal-upload.key
   #ServerCertificateFile=/etc/ssl/certs/journal-upload.crt
   #TrustedCertificateFile=/etc/ssl/certs/ca-bundle.crt
   ```

4. **Enable and start the service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now systemd-journal-upload
   ```

5. **Verification**
   ```bash
   systemctl is-enabled systemd-journal-upload
   systemctl is-active systemd-journal-upload
   journalctl -u systemd-journal-upload -n 20
   ```
   - Expected: `enabled` and `active` with successful connection logs (no repeated connection errors).

## Rollback
- Stop and disable uploads (e.g., if the collector becomes unavailable):
  ```bash
  sudo systemctl disable --now systemd-journal-upload
  ```
- Remove configuration if decommissioning:
  ```bash
  sudo dnf remove -y systemd-journal-remote
  ```

## Notes
- If the destination URL is unreachable, the service may repeatedly retry; monitor `journalctl -u systemd-journal-upload` for errors.
- Ensure outbound firewall rules permit HTTPS (or chosen protocol/port) to the collector.
- Keep the collector certificate authorities updated so TLS validation succeeds.
