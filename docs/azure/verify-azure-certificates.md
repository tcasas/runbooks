[Runbooks Index](../index.md) / [Azure](index.md)

# Verify Azure Certificates

Use this runbook to validate Azure-issued or imported TLS/SSL certificates, confirm they are bound to services, and identify renewal needs.

## 1️⃣ Identify the Certificate and Source

- **Azure Portal:** Navigate to **Key Vault** > **Certificates** or **App Service** > **TLS/SSL settings** to locate the certificate name.
- **CLI (Key Vault):**
  ```bash
  az keyvault certificate list --vault-name <keyvault> --query "[].{Name:name, Enabled:attributes.enabled, Expires:attributes.expires}" -o table
  az keyvault certificate show --vault-name <keyvault> --name <cert-name>
  ```
- **CLI (App Service bindings):**
  ```bash
  az webapp config ssl list --resource-group <rg> --name <app-name>
  ```
- Note whether the certificate is **Azure App Service Managed**, **Key Vault-backed**, or **manually uploaded**.

## 2️⃣ Check Certificate Validity and Chain

- Export the public certificate to inspect dates and subjects:
  ```bash
  az keyvault certificate download --vault-name <keyvault> --name <cert-name> --file cert.pem
  openssl x509 -in cert.pem -noout -dates -subject -issuer
  ```
- If a certificate is stored as a secret (PFX):
  ```bash
  az keyvault secret download --vault-name <keyvault> --name <cert-name> --file cert.pfx
  openssl pkcs12 -in cert.pfx -nokeys -out cert.pem
  openssl verify -CAfile <ca-bundle.pem> cert.pem
  ```
- Confirm `NotBefore`/`NotAfter` are current, the issuer chain is trusted, and SANs include all expected hostnames.

## 3️⃣ Validate Service Bindings

- **App Service / Function App:**
  ```bash
  az webapp config ssl list --resource-group <rg> --name <app-name> \
    --query "[] | [?hostNames]" -o json
  az webapp config ssl bind --help  # reference for remediation
  ```
  Confirm `hostNames` entries reference the expected thumbprint.

- **Application Gateway (v2):**
  ```bash
  az network application-gateway ssl-cert show --gateway-name <agw> --resource-group <rg> --name <cert-name>
  az network application-gateway http-listener list --gateway-name <agw> --resource-group <rg> \
    --query "[].{Name:name, Cert:sslCertificate.id, Host:hostNames}" -o table
  ```
  Ensure listeners use the intended certificate resource.

- **Front Door / CDN (Standard/Premium):**
  ```bash
  az afd custom-domain show --profile-name <profile> --resource-group <rg> --name <domain> \
    --query "tlsSettings"
  ```
  Verify `certificateType` (ManagedCertificate/CustomerCertificate) and that `secret` points to the correct Key Vault version when customer-managed.

- **API Management:**
  ```bash
  az apim ssl show --resource-group <rg> --name <apim> --type gateway
  ```
  Confirm the gateway certificate matches the expected thumbprint and expiry.

## 4️⃣ Test Endpoint Presentation

- From a client, confirm the served certificate matches the hostname:
  ```bash
  echo | openssl s_client -connect <hostname>:443 -servername <hostname> -showcerts
  ```
- For HTTP(S) response validation:
  ```bash
  curl -I https://<hostname>
  ```
  Expect an HTTP `200/301/302` instead of TLS errors and verify the CN/SAN aligns with `<hostname>`.

## 5️⃣ Monitor and Renewal

- **Auto-rotation (Key Vault-backed):** Check Key Vault certificate `lifetimeActions`:
  ```bash
  az keyvault certificate show --vault-name <keyvault> --name <cert-name> \
    --query "policy.lifetimeActions"
  ```
  Ensure `action.type` is `AutoRenew` and `daysBeforeExpiry` is acceptable.

- **App Service Managed Certificates:** They renew automatically. Confirm custom domains remain validated and that DNS CNAMEs point to the App Service domain so renewal can complete.

- **Alerts:** Implement alert rules on Key Vault `CertificateNearExpiry` or `CertificateExpired` events, or use Azure Monitor scheduled queries against `AzureDiagnostics` for certificate expiry signals.

## 6️⃣ Common Remediations

- **Expired/expiring:** Renew or reissue in Key Vault, then update bound resources to the new version (or ensure `auto-rotate-secret` is enabled for Front Door/CDN).
- **Wrong certificate on endpoint:** Update bindings (App Service SSL binding, Application Gateway listener, Front Door custom domain) to reference the correct certificate or secret version.
- **Hostname mismatch:** Reissue with correct SANs and redeploy bindings.
- **Chain issues:** Import the full chain into Key Vault PFX or use a trusted CA bundle; verify intermediate certificates are present.

## 7️⃣ Document Findings

Capture certificate name/ID, thumbprint, expiry, binding targets (App Service, Application Gateway, Front Door, API Management), validation test results, and any remediation steps taken.
