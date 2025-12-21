[Runbooks Index](../index.md) / [GCP](index.md)

# Verify TLS Certificate After Installation

Use this runbook to validate that a newly installed TLS certificate on a GCP workload (Compute Engine VM, GKE Ingress, or Cloud Run custom domain) is correctly served, trusted, and not nearing expiration.

## 1️⃣ Prerequisites
- **Inputs**: target FQDN (e.g., `app.example.com`), expected certificate issuer, and minimum validity window.
- **Tools**: `openssl` (for direct TLS handshakes) and `curl` (for HTTP verification).
- **Network**: ensure you can reach the public endpoint or have VPN access for internal load balancers.

## 2️⃣ Resolve the Endpoint
- Confirm DNS resolution:
  ```bash
  dig +short app.example.com
  ```
  - ✅ Expect at least one A/AAAA record.
  - ⚠️ If empty, check Cloud DNS or the delegated DNS provider for missing records.

## 3️⃣ Inspect the Served Certificate
- Perform a TLS handshake and capture the certificate chain:
  ```bash
  openssl s_client -connect app.example.com:443 -servername app.example.com -showcerts </dev/null
  ```
  - Look for `Verify return code: 0 (ok)`.
  - Confirm the **CN/SAN** contains the target FQDN.
  - Verify the **issuer** matches the expected CA (e.g., Google Trust Services, Let’s Encrypt).
  - Note the **Not Before/Not After** dates.

## 4️⃣ Validate Chain and Expiry
- Extract the end-entity certificate for detailed checks:
  ```bash
  openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null \
    | openssl x509 -noout -subject -issuer -dates -ext subjectAltName
  ```
  - Ensure the certificate is not expiring within your policy window (e.g., 15–30 days).
  - If `unable to get local issuer certificate`, ensure intermediate CAs are presented by the load balancer or add the full chain.

## 5️⃣ Application-Level Verification
- Confirm HTTPS response and server-provided certificate match:
  ```bash
  curl -vI https://app.example.com
  ```
  - Expect HTTP 200/301/302.
  - If you see certificate errors, validate the DNS name, chain, and trust store.

## 6️⃣ GCP Deployment Checks (by surface)
- **Compute Engine / TCP Load Balancer**
  - Verify target proxy and SSL certificate binding:
    ```bash
    gcloud compute target-https-proxies describe <proxy-name> --format='value(sslCertificates)'
    gcloud compute ssl-certificates describe <cert-name> --format='yaml(name,expireTime,subjectAlternativeNames)'
    ```
  - Ensure the active certificate is the latest version and not pending provisioning.
- **GKE Ingress (GCLB)**
  - Inspect Ingress status for the managed certificate:
    ```bash
    kubectl describe ingress <name> | grep -A3 \"Managed Certificates\"
    kubectl describe managedcertificate <cert-name>
    ```
  - Status should be `Active` with a valid `ExpireTime`.
- **Cloud Run Custom Domain**
  - Confirm domain mapping and certificate state:
    ```bash
    gcloud run domain-mappings describe app.example.com --platform managed --format='yaml(status,certificateMode)'
    ```
  - Certificate should show `Ready` and `AUTO_MANAGED`.

## 7️⃣ Troubleshooting
- **Stuck in provisioning**: Verify DNS A/AAAA records point to the load balancer IP; CAA records allow the issuer (e.g., `0 issue \"pki.goog\"`).
- **Old certificate still served**: Check for multiple target proxies or backends; ensure traffic is hitting the updated frontend.
- **Mutual TLS failures**: Confirm client certificate requirements on the backend service and that the trust store includes the issuing CA.
- **Intermediate missing**: Re-upload certificate with full chain or use Google-managed certificates to avoid chain gaps.

## 8️⃣ Success Criteria
- Endpoint resolves correctly.
- TLS handshake succeeds with the expected issuer and hostname.
- Certificate validity exceeds your minimum window.
- HTTP responses succeed without certificate warnings.
