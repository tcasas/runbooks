# Verify certificate fingerprint

Use this procedure to confirm a certificate file or live endpoint matches an expected SHA-256 fingerprint. Normalizing fingerprints (uppercase, no colons) avoids formatting differences between tools.

## Prerequisites
- Path to the certificate you want to validate (PEM or DER format).
- The expected SHA-256 fingerprint from a trusted source (release notes, device UI, vendor ticket, etc.).
- OpenSSL available on the host performing the validation.

## Steps
1. **Normalize the expected fingerprint** so you can compare it reliably:
   ```bash
   EXPECTED_FP=$(echo "ab:cd:ef:12:34:56:78:90:ab:cd:ef:12:34:56:78:90:ab:cd:ef:12:34:56:78:90:ab:cd:ef:12:34:56:78:90" \
     | tr -d ': ' \
     | tr '[:lower:]' '[:upper:]')
   ```
2. **Compute the fingerprint of a local certificate file** (PEM or DER):
   ```bash
   ACTUAL_FP=$(openssl x509 -in server.crt -noout -fingerprint -sha256 \
     | cut -d '=' -f2 \
     | tr -d ':' \
     | tr '[:lower:]' '[:upper:]')
   ```
   - For DER files, add `-inform DER` to the `openssl x509` command.
3. **Compare the normalized values**:
   ```bash
   if [ "$EXPECTED_FP" = "$ACTUAL_FP" ]; then
     echo "Fingerprint match"
   else
     echo "Fingerprint mismatch" >&2
   fi
   ```
4. **Validate a certificate presented by a live endpoint** (optional):
   ```bash
   ACTUAL_FP=$(openssl s_client -connect example.com:443 -servername example.com -showcerts </dev/null 2>/dev/null \
     | openssl x509 -noout -fingerprint -sha256 \
     | cut -d '=' -f2 \
     | tr -d ':' \
     | tr '[:lower:]' '[:upper:]')
   ```
   - Replace the host and port with the service you are checking.
   - Use `-CAfile` or `-verify_return_error` flags on `openssl s_client` if you also need full chain validation.

## Troubleshooting
- If `openssl s_client` hangs, add `-connect host:port -servername host -brief` and ensure firewalls allow outbound TLS to the target.
- A mismatch may indicate the certificate was rotated, the wrong file was selected, or the expected fingerprint source is stale.
- For certificates stored in hardware security modules or PKCS#11 devices, export the public certificate first, then re-run the fingerprint commands on the exported PEM.
