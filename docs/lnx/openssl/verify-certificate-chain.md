# Verify certificate chain

Use this runbook to confirm a certificate chains cleanly to trusted roots. It covers local PEM validation and remote endpoint checks to spot missing intermediates or hostname issues.

## Prerequisites

- OpenSSL installed on a Linux host.
- PEM files for the server certificate and any intermediate certificates (if validating locally).
- Access to the target host and port (if validating a live endpoint).

## Procedure (local PEM files)

1. **Normalize the certificate bundle**
   - Concatenate the server certificate followed by its intermediates into a single PEM file (for example `chain.pem`):
     ```bash
     cat server.pem intermediate1.pem intermediate2.pem > chain.pem
     ```

2. **Verify the chain against a CA bundle**
   - Run OpenSSL `verify` with an explicit CA file or directory:
     ```bash
     # -CAfile: path to the trusted CA bundle to validate against
     openssl verify -CAfile ca-bundle.pem chain.pem
     ```
   - Success outputs `chain.pem: OK`. Any missing or expired issuers will be reported in the failure message.

3. **Inspect the detailed path (optional)**
   - Use `-show_chain` to confirm each hop resolves to a trusted root:
     ```bash
     # -CAfile: path to the trusted CA bundle
     # -show_chain: print the verified chain from leaf to root
     openssl verify -CAfile ca-bundle.pem -show_chain chain.pem
     ```
   - Confirm the final certificate in the chain is a root you intend to trust.

## Procedure (remote endpoint)

1. **Fetch the presented chain**
   - Capture the certificate chain from the endpoint using `s_client`:
     ```bash
     # -connect: target host and port
     # -servername: SNI value (usually the hostname)
     # -showcerts: print the full certificate chain the server presents
     openssl s_client \
       -connect www.example.com:443 \
       -servername www.example.com \
       -showcerts \
       </dev/null 2>/dev/null \
       > endpoint_chain.txt
     ```

2. **Check hostname and validation status**
   - Let OpenSSL perform full verification using system trust:
     ```bash
     # -connect: target host and port
     # -servername: SNI value
     # -verify_return_error: exit non-zero on verification failure instead of continuing
     openssl s_client \
       -connect www.example.com:443 \
       -servername www.example.com \
       -verify_return_error \
       </dev/null
     ```
   - Verify the output includes `Verify return code: 0 (ok)` and no `hostname mismatch` warnings.

3. **Re-run with custom trust (if needed)**
   - If the endpoint uses a private CA, supply the appropriate trust store:
     ```bash
     # -connect: target host and port
     # -servername: SNI value
     # -CAfile: custom trust bundle for verification
     # -verify_return_error: exit non-zero on verification failure
     openssl s_client \
       -connect www.example.com:443 \
       -servername www.example.com \
       -CAfile ca-bundle.pem \
       -verify_return_error \
       </dev/null
     ```
   - Confirm the verify return code is `0`. A code of `20` typically indicates a missing intermediate; `21` indicates an expiration problem.

## Troubleshooting tips

- If verification fails with `unable to get local issuer certificate`, add the missing intermediate to the bundle and retry.
- For OCSP or CRL issues, temporarily disable revocation checks only when debugging, never as a permanent workaround.
- When diagnosing TLS applications behind load balancers, test each backend directly to ensure the full chain is installed everywhere.
