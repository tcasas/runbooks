# Verify F5 certificate install test

Use this runbook to validate the REPL-based certificate install helper (`app/tests/repl/f5_cert_install.py`). It captures the expected console flow, sanity checks, and success indicators for a single installation run against a BIG-IP CSSL profile.

## Prerequisites
- Access to the Turtle Sensor repository with test PEM material available to the helper (`get_crt_pem`, `get_key_pem`, `get_chain_pem`).
- IPython available in the project environment.
- Network access to the target BIG-IP environment and the cert redirector endpoint referenced in the helper.

## Steps
1. **Launch IPython** from the project root.
2. **Execute the helper** to load the utility functions and PEM fixtures:
   ```python
   %run app/tests/repl/f5_cert_install.py
   ```
3. **Resolve the target device** (update the helper constants first if you need a different CSSL profile or device):
   ```python
   device = lookup_device()
   ```
   - Confirm the logs show the expected cert redirector URL and VIP resolution for the device.
4. **Build the certificate attachment** (and review readiness logs if desired):
   ```python
   f5cert = build_cert_attachment(device)
   # Optional: log_readiness(f5cert)
   ```
5. **Run the install**:
   ```python
   result = f5cert.install()
   print(result)
   ```
   - A successful run should return `(True, "install complete")`.
6. **Inspect the loaded certificate** to ensure the fingerprint and scope key were populated:
   ```python
   vars(f5cert.certfile)
   ```
   - Verify `_cert_fingerprint_sha256` matches the expected PEM, `_scope_key_proposal` is prefixed with `fp:`, and `pending_state` is `ready_to_install`. Use the [OpenSSL fingerprint verification runbook](../../lnx/openssl/verify-certificate-fingerprint.md) if you need to normalize or compare fingerprints.

## Evidence to capture
- IPython console output showing device lookup, VIP resolution, and the `(True, "install complete")` tuple.
- The `vars(f5cert.certfile)` dictionary with the fingerprint (`_cert_fingerprint_sha256`) and scope key values for the installed certificate.

## Troubleshooting tips
- If `lookup_device()` fails, confirm the device name and controller inventory in `f5_cert_install.py` are correct for your environment.
- For VIP resolution errors, verify DNS or override the cert redirector URL to point at the correct staging or production endpoint.
- If `install()` raises an error, re-run `log_readiness(f5cert)` to confirm the helper gathered PEM material and targeted the correct CSSL profile before retrying.
