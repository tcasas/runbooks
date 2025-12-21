[Runbooks Index](../../index.md) / [Turtle Sensor](../index.md) / [Setup](index.md)

# Turtle-Sensor Internal CA (Root + Issuer) Bootstrap — OpenSSL-Only (RHEL 9)

This runbook sets up an internal, Turtle-Sensor-only PKI with an offline-ish Root CA and an online Issuing CA, plus example controller and sensor certificates. Revocation/OCSP is intentionally omitted; prefer short-lived sensor certs and renewal.

> **Scope:** Builds on RHEL 9 with OpenSSL 3.

## Table of Contents
- [0) Variables (edit these)](#0-variables-edit-these)
- [1) Prereqs](#1-prereqs)
- [2) Create directories](#2-create-directories)
- [3) Write OpenSSL configs (Root + Issuer)](#3-write-openssl-configs-root--issuer)
- [4) Create Root CA key + cert (OFFLINE ROOT)](#4-create-root-ca-key--cert-offline-root)
- [5) Create Issuer (Intermediate) key + CSR (ONLINE ISSUER)](#5-create-issuer-intermediate-key--csr-online-issuer)
- [6) Sign Issuer CSR with Root CA (do this on Root host)](#6-sign-issuer-csr-with-root-ca-do-this-on-root-host)
- [7) Build full chain bundle (issuer + root)](#7-build-full-chain-bundle-issuer--root)
- [8) Install Root CA into RHEL trust store (run on sensors + controllers)](#8-install-root-ca-into-rhel-trust-store-run-on-sensors--controllers)
- [9) Issue Controller server cert (SAN-enabled)](#9-issue-controller-server-cert-san-enabled)
- [10) Issue Sensor client cert (SAN-enabled, short-lived)](#10-issue-sensor-client-cert-san-enabled-short-lived)
- [11) Quick validation commands](#11-quick-validation-commands)
- [12) Output locations (what you actually deploy)](#12-output-locations-what-you-actually-deploy)

## 0) Variables (edit these)
```bash
# Where to build CA files
export PKI_BASE="/opt/otxapps/pki"
export ROOT_DIR="${PKI_BASE}/root"
export ISSUER_DIR="${PKI_BASE}/issuer"

# Controller identity (server cert)
export CONTROLLER_CN="controller-vip.company.internal"
export CONTROLLER_SANS="DNS:controller-vip.company.internal,DNS:controller-01.company.internal,DNS:controller-02.company.internal"

# Sensor identity (client cert)
export SENSOR_CN="sensor-12345"
export SENSOR_SANS="DNS:sensor-12345.turtle.internal"

# Validity
export ROOT_DAYS="3650"      # 10 years
export ISSUER_DAYS="1095"    # 3 years
export SERVER_DAYS="365"      # 1 year
export CLIENT_DAYS="30"      # 30 days (short-lived is recommended for sensors)

# Key algorithm
# - Use "ec" (recommended) or "rsa"
export KEY_ALGO="ec"

# EC curve if KEY_ALGO=ec
export EC_CURVE="prime256v1"

# Permissions
umask 077
```

## 1) Prereqs
```bash
sudo dnf -y install openssl ca-certificates

openssl version
# > OpenSSL 3.*  (on RHEL 9)
```

## 2) Create directories
```bash
sudo install -d -m 0700 "${ROOT_DIR}"/{certs,crl,newcerts,private,csr}
sudo install -d -m 0700 "${ISSUER_DIR}"/{certs,crl,newcerts,private,csr}

# CA database files
sudo bash -lc "echo 1000 > '${ROOT_DIR}/serial'"
sudo bash -lc "echo 1000 > '${ISSUER_DIR}/serial'"
sudo bash -lc "touch '${ROOT_DIR}/index.txt' '${ISSUER_DIR}/index.txt'"
sudo bash -lc "touch '${ROOT_DIR}/index.txt.attr' '${ISSUER_DIR}/index.txt.attr'"

ls -la "${PKI_BASE}"
# > (you should see root/ and issuer/)
```

## 3) Write OpenSSL configs (Root + Issuer)
```bash
sudo tee "${ROOT_DIR}/openssl-root.cnf" >/dev/null <<'EOF'
[ ca ]
default_ca = CA_default

[ CA_default ]
dir               = .
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
RANDFILE          = $dir/private/.rand

private_key       = $dir/private/root.key
certificate       = $dir/certs/root.crt

default_md        = sha256
name_opt          = ca_default
cert_opt          = ca_default
default_days      = 3650
preserve          = no
policy            = policy_strict

x509_extensions   = v3_root_ca
copy_extensions   = none

[ policy_strict ]
countryName             = optional
stateOrProvinceName     = optional
localityName            = optional
organizationName        = optional
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

[ req ]
default_bits        = 2048
default_md          = sha256
distinguished_name  = dn
x509_extensions     = v3_root_ca
prompt              = no

[ dn ]
CN = Turtle Root CA

[ v3_root_ca ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints       = critical,CA:true,pathlen:1
keyUsage               = critical,keyCertSign,cRLSign
EOF

sudo tee "${ISSUER_DIR}/openssl-issuer.cnf" >/dev/null <<'EOF'
[ ca ]
default_ca = CA_default

[ CA_default ]
dir               = .
certs             = $dir/certs
crl_dir           = $dir/crl
new_certs_dir     = $dir/newcerts
database          = $dir/index.txt
serial            = $dir/serial
RANDFILE          = $dir/private/.rand

private_key       = $dir/private/issuer.key
certificate       = $dir/certs/issuer.crt

default_md        = sha256
name_opt          = ca_default
cert_opt          = ca_default
default_days      = 825
preserve          = no
policy            = policy_loose

x509_extensions   = v3_issued_server
copy_extensions   = copy

[ policy_loose ]
countryName             = optional
stateOrProvinceName     = optional
localityName            = optional
organizationName        = optional
organizationalUnitName  = optional
commonName              = supplied
emailAddress            = optional

[ req ]
default_bits        = 2048
default_md          = sha256
distinguished_name  = dn
prompt              = no

[ dn ]
CN = Turtle Issuing CA

[ v3_intermediate_ca ]
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid:always,issuer
basicConstraints       = critical,CA:true,pathlen:0
keyUsage               = critical,keyCertSign,cRLSign

[ v3_issued_server ]
basicConstraints       = CA:false
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid,issuer
keyUsage               = critical,digitalSignature,keyEncipherment
extendedKeyUsage       = serverAuth
subjectAltName         = @alt_names

[ v3_issued_client ]
basicConstraints       = CA:false
subjectKeyIdentifier   = hash
authorityKeyIdentifier = keyid,issuer
keyUsage               = critical,digitalSignature
extendedKeyUsage       = clientAuth
subjectAltName         = @alt_names

[ alt_names ]
# populated per-request via -extfile and -extensions (see issuance steps)
EOF

sudo ls -l "${ROOT_DIR}/openssl-root.cnf" "${ISSUER_DIR}/openssl-issuer.cnf"
# > (both config files present)
```

## 4) Create Root CA key + cert (OFFLINE ROOT)
```bash
cd "${ROOT_DIR}"

if [[ "${KEY_ALGO}" == "ec" ]]; then
  sudo openssl ecparam -name "${EC_CURVE}" -genkey -noout -out private/root.key
else
  sudo openssl genrsa -out private/root.key 4096
fi
sudo chmod 600 private/root.key

# Self-signed Root CA cert
sudo openssl req -new -x509 \
  -config openssl-root.cnf \
  -key private/root.key \
  -days "${ROOT_DAYS}" \
  -out certs/root.crt

sudo openssl x509 -noout -subject -issuer -in certs/root.crt
# > subject=CN = Turtle Root CA
# > issuer=CN = Turtle Root CA
```

## 5) Create Issuer (Intermediate) key + CSR (ONLINE ISSUER)
```bash
cd "${ISSUER_DIR}"

if [[ "${KEY_ALGO}" == "ec" ]]; then
  sudo openssl ecparam -name "${EC_CURVE}" -genkey -noout -out private/issuer.key
else
  sudo openssl genrsa -out private/issuer.key 4096
fi
sudo chmod 600 private/issuer.key

sudo openssl req -new \
  -config openssl-issuer.cnf \
  -key private/issuer.key \
  -out csr/issuer.csr

sudo openssl req -noout -subject -in csr/issuer.csr
# > subject=CN = Turtle Issuing CA
```

## 6) Sign Issuer CSR with Root CA (do this on Root host)
In real operations, transfer the CSR to the offline root host, sign there, then copy the issuer cert back. For bootstrap simplicity, sign locally:

```bash
cd "${ROOT_DIR}"

sudo openssl ca \
  -config openssl-root.cnf \
  -extensions v3_root_ca \
  -days "${ISSUER_DAYS}" \
  -notext \
  -batch \
  -in "${ISSUER_DIR}/csr/issuer.csr" \
  -out "${ISSUER_DIR}/certs/issuer.crt"

sudo openssl x509 -noout -subject -issuer -in "${ISSUER_DIR}/certs/issuer.crt"
# > subject=CN = Turtle Issuing CA
# > issuer=CN = Turtle Root CA
```

## 7) Build full chain bundle (issuer + root)
```bash
cd "${ISSUER_DIR}"
sudo bash -lc "cat certs/issuer.crt '${ROOT_DIR}/certs/root.crt' > certs/ca-chain.crt"
sudo openssl crl2pkcs7 -nocrl -certfile certs/ca-chain.crt | sudo openssl pkcs7 -print_certs -noout | head
# > subject=CN = Turtle Issuing CA
# > subject=CN = Turtle Root CA
```

## 8) Install Root CA into RHEL trust store (run on sensors + controllers)
```bash
sudo install -D -m 0644 "${ROOT_DIR}/certs/root.crt" /etc/pki/ca-trust/source/anchors/turtle-root-ca.crt
sudo update-ca-trust

# Verify trust store contains it
sudo trust list | grep -i "Turtle Root CA" -n || true
# > (should show Turtle Root CA somewhere in output)
```

## 9) Issue Controller server cert (SAN-enabled)
```bash
cd "${ISSUER_DIR}"

# Create server key + CSR with SANs via extfile
sudo tee "csr/controller.ext" >/dev/null <<EOF
[ req ]
distinguished_name = dn
prompt = no

[ dn ]
CN = ${CONTROLLER_CN}

[ v3_issued_server ]
basicConstraints = CA:false
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth
subjectAltName = ${CONTROLLER_SANS}
EOF

if [[ "${KEY_ALGO}" == "ec" ]]; then
  sudo openssl ecparam -name "${EC_CURVE}" -genkey -noout -out "private/${CONTROLLER_CN}.key"
else
  sudo openssl genrsa -out "private/${CONTROLLER_CN}.key" 2048
fi
sudo chmod 600 "private/${CONTROLLER_CN}.key"

sudo openssl req -new \
  -key "private/${CONTROLLER_CN}.key" \
  -out "csr/${CONTROLLER_CN}.csr" \
  -config "csr/controller.ext"

# Sign via Issuer CA using server extensions
sudo openssl ca \
  -config openssl-issuer.cnf \
  -extensions v3_issued_server \
  -extfile "csr/controller.ext" \
  -days "${SERVER_DAYS}" \
  -notext \
  -batch \
  -in "csr/${CONTROLLER_CN}.csr" \
  -out "certs/${CONTROLLER_CN}.crt"

# Verify SANs + chain
sudo openssl x509 -noout -text -in "certs/${CONTROLLER_CN}.crt" | grep -A1 "Subject Alternative Name"
# > X509v3 Subject Alternative Name:
# >     DNS:controller-vip.company.internal, DNS:controller-01.company.internal, DNS:controller-02.company.internal
```

## 10) Issue Sensor client cert (SAN-enabled, short-lived)
```bash
cd "${ISSUER_DIR}"

sudo tee "csr/sensor.ext" >/dev/null <<EOF
[ req ]
distinguished_name = dn
prompt = no

[ dn ]
CN = ${SENSOR_CN}

[ v3_issued_client ]
basicConstraints = CA:false
keyUsage = critical,digitalSignature
extendedKeyUsage = clientAuth
subjectAltName = ${SENSOR_SANS}
EOF

if [[ "${KEY_ALGO}" == "ec" ]]; then
  sudo openssl ecparam -name "${EC_CURVE}" -genkey -noout -out "private/${SENSOR_CN}.key"
else
  sudo openssl genrsa -out "private/${SENSOR_CN}.key" 2048
fi
sudo chmod 600 "private/${SENSOR_CN}.key"

sudo openssl req -new \
  -key "private/${SENSOR_CN}.key" \
  -out "csr/${SENSOR_CN}.csr" \
  -config "csr/sensor.ext"

sudo openssl ca \
  -config openssl-issuer.cnf \
  -extensions v3_issued_client \
  -extfile "csr/sensor.ext" \
  -days "${CLIENT_DAYS}" \
  -notext \
  -batch \
  -in "csr/${SENSOR_CN}.csr" \
  -out "certs/${SENSOR_CN}.crt"

sudo openssl x509 -noout -purpose -in "certs/${SENSOR_CN}.crt" | head -n 6
# > Certificate purposes:
# > SSL client : Yes
```

## 11) Quick validation commands
```bash
# A) Verify controller cert chains to your root (local file check)
sudo openssl verify -CAfile "${ROOT_DIR}/certs/root.crt" -untrusted "${ISSUER_DIR}/certs/issuer.crt" "${ISSUER_DIR}/certs/${CONTROLLER_CN}.crt"
# > <controller cert path>: OK

# B) Example: curl to controller with sensor client cert (mTLS) — controller must be configured to REQUIRE client certs
# Replace URL path with your real health endpoint
# NOTE: --cacert uses your root CA file (or rely on system trust store once baked in)
# curl -vk --cacert /etc/pki/ca-trust/source/anchors/turtle-root-ca.crt \
#   --cert "${ISSUER_DIR}/certs/${SENSOR_CN}.crt" --key "${ISSUER_DIR}/private/${SENSOR_CN}.key" \
#   "https://${CONTROLLER_CN}/health"
# > expected: TLS handshake succeeds and HTTP 200/OK (depends on endpoint)
```

## 12) Output locations (what you actually deploy)
- Root CA public cert (distribute everywhere): `${ROOT_DIR}/certs/root.crt`
- Issuer cert (needed by some servers as chain): `${ISSUER_DIR}/certs/issuer.crt`
- Full chain (issuer+root): `${ISSUER_DIR}/certs/ca-chain.crt`
- Controller server cert/key (install on controller): `${ISSUER_DIR}/certs/${CONTROLLER_CN}.crt` and `${ISSUER_DIR}/private/${CONTROLLER_CN}.key`
- Sensor client cert/key (install on sensor): `${ISSUER_DIR}/certs/${SENSOR_CN}.crt` and `${ISSUER_DIR}/private/${SENSOR_CN}.key`

```bash
echo "DONE: CA bootstrap complete under ${PKI_BASE}"
```
