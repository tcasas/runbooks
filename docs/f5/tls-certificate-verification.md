[Runbooks Index](../index.md) / [F5](index.md)

# Verify TLS Certificate on F5 (BIG-IP)

Use this runbook to validate that a newly installed TLS certificate on an F5 BIG-IP device is served correctly, trusted, and not nearing expiration.

## 1️⃣ Prerequisites
- **Inputs**: Virtual server (VIP) address/hostname, expected certificate Common Name/SAN, issuer, and minimum validity window.
- **Access**: SSH to the BIG-IP or UI access with privileges to view configuration.
- **Tools**: `tmsh`, `openssl`, `curl`.
- **Network**: Ability to reach the VIP from a test host.

## 2️⃣ Identify the Active Client SSL Profile
1. List the SSL profiles on the virtual server:
   ```bash
   tmsh list ltm virtual <vs-name> profiles
   ```
2. Note the client SSL profile (commonly `clientssl` or a custom profile) attached to the virtual server.

## 3️⃣ Confirm Certificate and Key Bound to the Profile
1. Inspect the client SSL profile to see the certificate and key objects in use:
   ```bash
   tmsh list ltm profile client-ssl <profile-name> cert key chain
   ```
2. Ensure the intended certificate/key are referenced (e.g., `cert foo.example.com.crt`, `key foo.example.com.key`).
3. If using a cert/key chain, verify the correct chain file is configured.

## 4️⃣ Check Certificate Details and Expiry on the Device
1. Display certificate metadata:
   ```bash
   tmsh list sys file ssl-cert <cert-object-name>
   ```
2. For validity dates and SANs, output the PEM and parse with openssl:
   ```bash
   tmsh show sys file ssl-cert <cert-object-name> | sed -n '/^-----BEGIN CERTIFICATE-----/,$p' \
     | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
   ```
3. Ensure `Not After` exceeds your policy window (e.g., >30 days) and SANs include the VIP hostname.

## 5️⃣ Validate Chain Presentation from the VIP
Run a TLS handshake from a test host against the VIP:
```bash
openssl s_client -connect <vip-hostname>:443 -servername <vip-hostname> -showcerts </dev/null
```
- Look for `Verify return code: 0 (ok)`.
- Confirm CN/SAN matches the VIP hostname and issuer matches expectations.
- Check intermediate certificates are presented; if missing, update the chain on the client SSL profile.

## 6️⃣ HTTP Response Check
Verify the application responds with the expected certificate:
```bash
curl -vI https://<vip-hostname>
```
- Expect 200/301/302.
- If certificate warnings occur, confirm the client SSL profile uses the correct cert/chain and DNS points to this VIP.

## 7️⃣ Common Remediation Steps
- **Wrong certificate served**: Re-bind the correct certificate/key (and chain) to the client SSL profile, then sync the device group if in an HA pair.
- **Missing intermediate**: Upload the full chain, update the profile’s chain reference, and save the config (`tmsh save sys config`).
- **Expired/near-expiry**: Upload a renewed certificate/key, update the profile, validate, and sync.
- **SNI-mapped profiles**: If multiple certs are used via SNI, ensure the SNI map includes the hostname being tested.

## 8️⃣ Success Criteria
- TLS handshake succeeds with `Verify return code: 0 (ok)`.
- Certificate CN/SAN and issuer are correct and validity exceeds your minimum window.
- HTTP requests succeed without certificate warnings.

