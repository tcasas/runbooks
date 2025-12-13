# F5Cert REPL helper usage

This helper script streamlines one-off certificate installs against a BIG-IP CSSL profile. Use it to load test PEMs, verify device connectivity, and perform a single install.

## Files
- `f5_cert_install.py`: REPL-friendly helper that prepares a certificate attachment, prints readiness checks, and can be run directly as a script.

## Quickstart
1. **Open a Python REPL** in the project environment.
2. **Copy/paste** the contents of `f5_cert_install.py` or run it directly:
   ```bash
   python docs/turtle-sensor/repl/f5_cert_install.py
   ```
3. **Fetch the target device**:
   ```python
   device = lookup_device()
   ```
4. **Build the certificate attachment and review readiness**:
   ```python
   f5cert = build_cert_attachment(device)
   log_readiness(f5cert)
   ```
5. **Perform the install** (once everything looks correct):
   ```python
   result = f5cert.install()
   print(result)
   ```

## Notes
- Update `CSSL_PROF`, `PROJECT_ID`, and `CN` constants in `f5_cert_install.py` to match your target profile and certificate.
- `lookup_device()` uses `get_device(name="lit-elb05-p001")`; adjust as needed for other inventories.
- The helper expects `get_crt_pem`, `get_key_pem`, and `get_chain_pem` to be available from `conftest` for loading test materials.

## Suggested improvements for future integration tests
- Add CLI arguments (device name, profile, PEM paths) so the helper can be executed without editing constants.
- Wire a dry-run mode that only logs readiness results and planned actions without calling `install()`.
- Emit structured readiness reports (JSON/YAML) to capture evidence in CI logs.
- Include exception handling around `install()` to surface BIG-IP API errors with actionable messages.
