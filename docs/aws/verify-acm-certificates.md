[Runbooks Index](../index.md) / [AWS](index.md)

# Verify AWS Certificate Manager (ACM) Certificates

Use this runbook to validate that AWS Certificate Manager certificates are properly issued, validated, and attached to workloads.

## 1️⃣ Confirm the Certificate Exists

- List certificates in the target account/region:
  ```bash
  aws acm list-certificates --region <region>
  ```
- Retrieve details for the certificate you care about (use the ARN from the previous command):
  ```bash
  aws acm describe-certificate --certificate-arn <arn> --region <region>
  ```
  Key fields:
  - `DomainName` and `SubjectAlternativeNames`
  - `Status` (Issued, PendingValidation, Inactive, Expired, Revoked, ValidationTimedOut, ValidationFailed)
  - `NotBefore` / `NotAfter` validity window
  - `Type` (AMAZON_ISSUED or IMPORTED)

## 2️⃣ Check Validation Status

- For DNS validation, confirm each record exists and matches the required value. The `ResourceRecord` block shows the expected CNAME:
  ```bash
  aws acm describe-certificate --certificate-arn <arn> --query "Certificate.DomainValidationOptions[].ResourceRecord" --region <region>
  ```
- Verify DNS records resolve publicly:
  ```bash
  dig <cname-record> +short
  ```
  Expect the response to match the `ResourceRecord.Value`.
- For email validation (legacy), ensure the approval email was received and approved for the listed domain contacts.

## 3️⃣ Confirm Certificate in Use

- **Elastic Load Balancer (ALB/NLB):**
  ```bash
  aws elbv2 describe-listeners --load-balancer-arn <lb-arn> --region <region> \
    --query "Listeners[].Certificates[].CertificateArn"
  ```
  Ensure the target certificate ARN is present.

- **API Gateway (Regional/Edge):**
  ```bash
  aws apigateway get-domain-name --domain-name <custom-domain> --region <region> \
    --query "regionalCertificateArn || certificateArn"
  ```
  Confirm the ARN matches.

- **CloudFront:**
  ```bash
  aws cloudfront list-distributions --query "DistributionList.Items[].{Id:Id,Cert:ViewerCertificate.ACMCertificateArn,Domain:Aliases.Items}"
  ```
  Identify the distribution using the domain and verify `ViewerCertificate.ACMCertificateArn`.

- **Other services (ACM Private CA, EKS Ingress Controller, etc.):**
  - Inspect service-specific configuration to ensure the ACM ARN is referenced.

## 4️⃣ Validate Certificate Chain and Expiry

- Download the certificate chain to a file:
  ```bash
  aws acm get-certificate --certificate-arn <arn> --region <region> \
    --query Certificate --output text > cert.pem
  ```
- Inspect validity dates and subject information:
  ```bash
  openssl x509 -in cert.pem -noout -dates -subject -issuer
  ```
- Check full chain:
  ```bash
  aws acm get-certificate --certificate-arn <arn> --region <region> \
    --query CertificateChain --output text > chain.pem
  openssl verify -CAfile chain.pem cert.pem
  ```

## 5️⃣ Test Endpoint Presentation

- For HTTPS endpoints behind ALB/NLB/API Gateway/CloudFront:
  ```bash
  curl -I https://<hostname>
  ```
  Validate:
  - `200`/`301`/`302` responses instead of TLS errors.
  - Expected certificate presented (verify CN/SAN and issuer).
- To inspect the served certificate:
  ```bash
  echo | openssl s_client -connect <hostname>:443 -servername <hostname> -showcerts
  ```

## 6️⃣ Monitor for Expiration

- Create or confirm a CloudWatch alarm on ACM `ExpiredCertificate` events:
  ```bash
  aws cloudwatch describe-alarms --query "MetricAlarms[?MetricName=='ExpiredCertificate']"
  ```
- Optionally enable AWS Health or Security Hub notifications for certificate expiry findings.
- For imported certificates, set calendar reminders at least 30 days before `NotAfter`.

## 7️⃣ Remediate Common Issues

- **PendingValidation / ValidationFailed:** Fix DNS CNAMEs or re-request validation emails, then re-run validation commands.
- **Wrong certificate on endpoint:** Update listener or distribution to reference the correct ACM ARN, then re-test.
- **Expired or expiring:** Request a new ACM certificate and swap the ARN on all consuming services, then validate.
- **Chain/hostname mismatch:** Re-issue the certificate with correct SANs or ensure the endpoint uses the matching hostname via SNI.

## 8️⃣ Document Findings

- Record certificate ARN, domains, validation status, expiry date, and where it is attached (ALB/API Gateway/CloudFront/etc.).
- Note any remediation steps taken and validation evidence (command outputs, screenshots where applicable).
