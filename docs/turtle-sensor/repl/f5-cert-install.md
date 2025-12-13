# F5Cert REPL helper usage (IPython)

Use this helper to drive a one-off certificate install against a BIG-IP CSSL profile. It loads test PEMs, verifies device connectivity, and can push a single install when asked.

## Quickstart
1. **Start IPython** from the repository root so relative imports resolve:
   ```bash
   ipython
   ```
2. **Run the helper inside IPython** with the `%run` magic (dry-run by default):
   ```python
   %run app/tests/repl/f5_cert_install.py
   ```
   - To execute an install, pass flags after a `--` separator:
     ```python
     %run app/tests/repl/f5_cert_install.py -- --install --log-level DEBUG
     ```
3. **Drive individual steps manually** if you want to poke at the objects:
   ```python
   device = lookup_device()
   f5cert = build_cert_attachment(device)
   log_readiness(f5cert)
   f5cert.install()  # optional if you want to execute the push
   ```

## Notes
- The helper script lives at `app/tests/repl/f5_cert_install.py` and defaults to a dry run unless `--install` is provided.
- Adjust `CSSL_PROF`, `PROJECT_ID`, and `CN` constants in the helper to match your target profile and certificate.
- `lookup_device()` uses `get_device(name="lit-elb05-p001")`; change it for other inventories.
- The helper expects `get_crt_pem`, `get_key_pem`, and `get_chain_pem` to be available from `conftest` for loading test materials.

## Suggested improvements for future integration tests
- Add CLI arguments (device name, profile, PEM paths) so the helper can be executed without editing constants.
- Emit structured readiness reports (JSON/YAML) to capture evidence in CI logs.
- Include exception handling around `install()` to surface BIG-IP API errors with actionable messages.
- Hook the helper into CI smoke tests so the dry-run readiness checks run automatically against test fixtures.
