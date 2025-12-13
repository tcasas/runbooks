F5Cert REPL Runbook (single install)
====================================

Use this diff-friendly format to exercise one certificate install against a dedicated CSSL profile on a BIG-IP. Everything below is copy/paste-ready for editors like Notepad++.

.. code-block:: diff

   # F5Cert REPL Runbook (single install)


   Index: Scope and prerequisites
   *** Safety limits

   # Allowed targets and credential expectations
   - Touch only the designated test CSSL profile on the chosen BIG-IP.
   - Avoid any production profiles or devices.
   - Ensure you hold credentials for the target device and any required proxy.

   Index: Session setup
   *** Python environment

   # Start a REPL and prepare logging plus imports.

   >>> python
    import logging
    from pathlib import Path
    from app.device.device import make_device
    from app.cert.model import F5Cert
    logger = logging.getLogger("repl-f5cert")

   Index: Inputs
   *** Variable setup

   # Variables for device, profile, and PEM sources
   # Collect all device details and PEM paths in one place.

   >>> python
    DEVICE_NAME = "ltm01-p001"              # controller/inventory name
    DEVICE_FQDN = "ltm01-p001.example.com"  # mgmt hostname or IP
    DEVICE_USER = "svc_user"
    DEVICE_PASS = "super-secret"
    DEVICE_PROXY = "http://proxy:3128"      # set to None/"" if direct
    CSSL_PROF = "/Common/www"                # profile to update
    PROJECT_ID = "Common"                    # partition; defaults from cssl_prof if omitted

    CERT_PATH = Path("./certs/www.crt")
    KEY_PATH = Path("./certs/www.key")
    CHAIN_PATH = Path("./certs/www.chain")
    CN = "www.example.com"                  # subject CN for filename generation

   Index: Resolve device
   *** Build or fetch device

   # Construct the device manually; replace with get_device(name=DEVICE_NAME) if available.

   >>> python
    device = make_device(
        name=DEVICE_NAME,
        dtype="ltm",
        fqdn=DEVICE_FQDN,
        addr=DEVICE_FQDN,
        user=DEVICE_USER,
        pwd=DEVICE_PASS,
        proxy=DEVICE_PROXY,
    )

   Index: Prepare PEMs
   *** Load certificate materials

   # Read PEM content from disk.

   >>> python
    crt_pem = CERT_PATH.read_text()
    key_pem = KEY_PATH.read_text()
    chain_pem = CHAIN_PATH.read_text()

   Index: Construct placeholder cert
   *** Seed CertFile and attachment

   # Create the attachment with a provisional scope and CSSL profile.

   >>> python
    f = F5Cert(
        device=device,
        project_id=PROJECT_ID,
        cssl_prof=CSSL_PROF,
        certfile={"scope_key": "tmp:repl", "cn": CN},
    )
    f.logger = logger

   Index: Promote scope and attach PEMs
   *** Fingerprint and update certfile

   # Fingerprint the leaf cert, promote scope to fp:..., and attach PEMs.

   >>> python
    fp = f.cert_fingerprint_sha256(crt_pem)
    f.certfile = {
        "scope_key": f"fp:{fp}",
        "cn": CN,
        "crt_pem": crt_pem,
        "key_pem": key_pem,
        "chain_pem": chain_pem,
    }
    f.scope_key = f.certfile.scope_key

   Index: Confirm target
   *** Safety check

   # Final confirmation before install
   # Double-check the device and profile before performing the single install.

   >>> python
    print("DEVICE:", device.fqdn)
    print("CSSL_PROF:", f.cssl_prof)
    print("SCOPE:", f.certfile.get("scope_key"))

   Index: Execute install
   *** Validate and attach

   # Perform one install call; it validates inputs, uploads PEMs, and updates the CSSL profile.

   >>> python
    result = f.install()
    print(result)
   > (True, "install complete")

   Index: Cleanup
   *** Exit REPL

    Leave the REPL and drop temporary material

Notes
-----

- Keep the test CSSL profile isolated from production resources.
- If you need to point at a different profile or device, update ``CSSL_PROF`` and ``DEVICE_*`` but still run exactly one install per session.
- For a dry run without touching the BIG-IP, temporarily monkeypatch ``f.install`` to log inputs only; restore the original method before running the single intended install.
