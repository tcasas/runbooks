# Turtle-Sensor Podman + systemd Deployment (Production-Ready)
# Target: Hardened RHEL 9
# Goal: Deploy Turtle-Sensor as a Podman-managed systemd service with secure defaults, deterministic upgrades, and clean ops.
#
# Replace ALL_CAPS values before running.
# Expected outputs are prefixed with ">" on each line (diff-friendly).

## Index: 0) Variables (set once per host)

### Registry / image / service

```bash
# Harbor registry + image
export HARBOR_FQDN="HARBOR_FQDN_OR_VIP"
export IMAGE_REPO="turtle/sensor"
export IMAGE_TAG="prod"                # prod | staging | specific tag
export IMAGE="${HARBOR_FQDN}/${IMAGE_REPO}:${IMAGE_TAG}"

# Names
export SVC="turtle-sensor"

# Layout (per your standard)
export ETC_DIR="/etc/turtle"
export ENV_FILE="${ETC_DIR}/sensor.env"
export OTX_ROOT="/opt/otxapps"
export LOG_DIR="${OTX_ROOT}/turtle-sensor/log"
export DATA_DIR="${OTX_ROOT}/turtle-sensor/data"
export UNIT_FILE="/etc/systemd/system/${SVC}.service"

# Optional proxy (blank = none)
export HTTPS_PROXY_URL="http://PROXY_HOST:PROXY_PORT"
export NO_PROXY_LIST="localhost,127.0.0.1,.corp.example.com"
```

## Index: 1) Prerequisites

### Packages + baseline checks

```bash
sudo dnf -y install podman jq curl ca-certificates ripgrep
> Complete!

podman --version
> podman version X.Y.Z

systemctl --version | head -n 1
> systemd ...

getenforce
> Enforcing

timedatectl status | rg -n "System clock synchronized|NTP service|Time zone" || true
> System clock synchronized: yes
> NTP service: active
```

## Index: 2) Directory layout

### /etc + /opt

```bash
sudo install -d -m 0750 -o root -g root "${ETC_DIR}"
> created (or already exists)

sudo install -d -m 0755 -o root -g root "${OTX_ROOT}"
> created (or already exists)

sudo install -d -m 0755 -o root -g root "${LOG_DIR}" "${DATA_DIR}"
> created (or already exists)

ls -ald "${ETC_DIR}" "${OTX_ROOT}" "${LOG_DIR}" "${DATA_DIR}"
> drwxr-x--- root root ... /etc/turtle
> drwxr-xr-x root root ... /opt/otxapps
> drwxr-xr-x root root ... /opt/otxapps/turtle-sensor/log
> drwxr-xr-x root root ... /opt/otxapps/turtle-sensor/data
```

## Index: 3) CA trust configuration

### Option A (preferred): system trust store

```bash
# Copy your internal CA bundle (PEM) to anchors (name it something stable)
# Example filename: turtle-internal-ca.pem
sudo cp INTERNAL_CA.pem /etc/pki/ca-trust/source/anchors/turtle-internal-ca.pem
> (no output)

sudo update-ca-trust
> (no output)
```

### Option B (alternate): registry-specific trust (containers)

```bash
# NOTE: Use this only if you *cannot* use system trust store.
# sudo install -d -m 0755 "/etc/containers/certs.d/${HARBOR_FQDN}"
# sudo cp INTERNAL_CA.pem "/etc/containers/certs.d/${HARBOR_FQDN}/ca.crt"
# > installed
```

### Validate CA (Harbor TLS)

```bash
openssl s_client -connect "${HARBOR_FQDN}:443" -servername "${HARBOR_FQDN}" </dev/null 2>/dev/null | rg "Verify return code|subject=|issuer="
> Verify return code: 0 (ok)
```

## Index: 4) Registry authentication

### Login + pull

```bash
podman login "${HARBOR_FQDN}"
> Login Succeeded!

podman pull "${IMAGE}"
> ... pulled ...

podman images | head
> REPOSITORY ... TAG ... IMAGE ID ... CREATED ... SIZE
```

## Index: 5) (Recommended) Pin deployment to a digest

### Deterministic image reference

```bash
# Capture the pulled image's RepoDigest and pin to it for *this* deployment.
# This avoids "tag moved" surprises and makes rollback/audit easier.
export IMAGE_DIGEST="$(podman image inspect "${IMAGE}" --format '{{index .RepoDigests 0}}')"
echo "${IMAGE_DIGEST}"
> HARBOR_FQDN/turtle/sensor@sha256:...

# From here on, use IMAGE_REF as the pinned reference.
export IMAGE_REF="${IMAGE_DIGEST}"
```

## Index: 6) Environment file

### /etc/turtle/sensor.env

```bash
sudo tee "${ENV_FILE}" >/dev/null <<'EOF'
# Turtle-Sensor runtime config

# Controller discovery / naming (examples)
CONTROLLER_PRIMARY_NAME=primary-controller
CONTROLLER_SECONDARY_NAME=secondary-controller

# Optional fixed URLs (leave commented if you rely on VIP/redirect discovery)
# CONTROLLER_PRIMARY_URL=https://controller-dc1.example.com
# CONTROLLER_SECONDARY_URL=https://controller-dc2.example.com

# Trust bundle for requests
REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

# Optional proxy
HTTPS_PROXY=__HTTPS_PROXY_URL__
NO_PROXY=__NO_PROXY_LIST__

# App paths (host-mounted)
OTX_ROOT=/opt/otxapps
SENSOR_LOG_DIR=/opt/otxapps/turtle-sensor/log
SENSOR_DATA_DIR=/opt/otxapps/turtle-sensor/data

# Runtime
LOG_LEVEL=INFO
SENSOR_MODE=run
EOF
> wrote

sudo sed -i \
  -e "s|__HTTPS_PROXY_URL__|${HTTPS_PROXY_URL}|g" \
  -e "s|__NO_PROXY_LIST__|${NO_PROXY_LIST}|g" \
  "${ENV_FILE}"
> updated

sudo chmod 0640 "${ENV_FILE}"
sudo chown root:root "${ENV_FILE}"
> secured

sudo rg -n "CONTROLLER_|REQUESTS_CA_BUNDLE|HTTPS_PROXY|NO_PROXY|OTX_ROOT|SENSOR_|LOG_LEVEL|SENSOR_MODE" "${ENV_FILE}"
> ... shows configured values ...
```

## Index: 7) Create (or replace) the container

### Podman create (journald logging, SELinux-safe mounts)

```bash
sudo podman rm -f "${SVC}" 2>/dev/null || true
> removed (or none)

sudo podman create \
  --name "${SVC}" \
  --replace \
  --log-driver=journald \
  --env-file "${ENV_FILE}" \
  -v "${OTX_ROOT}:${OTX_ROOT}:Z" \
  "${IMAGE_REF}"
> container created

sudo podman ps -a --filter "name=${SVC}"
> ... STATUS: Created
```

## Index: 8) Generate & install systemd unit

### Generate unit + enable service

```bash
sudo podman generate systemd \
  --new \
  --name "${SVC}" \
  > "${UNIT_FILE}"
> wrote unit

# Recommended: harden the systemd unit (drop-in) rather than editing the generated file
sudo install -d -m 0755 "/etc/systemd/system/${SVC}.service.d"
> created

sudo tee "/etc/systemd/system/${SVC}.service.d/10-hardening.conf" >/dev/null <<'EOF'
[Service]
Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true
ProtectSystem=strict
EOF
> wrote drop-in

sudo systemctl daemon-reload
> reloaded

sudo systemctl enable --now "${SVC}.service"
> enabled
> started
```

## Index: 9) Verification

### Service, logs, container state, env

```bash
systemctl status "${SVC}.service" --no-pager
> Active: active (running)

journalctl -u "${SVC}.service" -n 200 --no-pager
> ... startup logs (no TLS/CA errors) ...

podman ps --filter "name=${SVC}"
> ... STATUS: Up ...

podman exec "${SVC}" /bin/bash -lc 'env | rg "SENSOR_|OTX_ROOT|LOG_LEVEL|HTTPS_PROXY|NO_PROXY|CONTROLLER_" | sort'
> ... expected vars present ...
```

## Index: 10) Upgrade procedure (safe)

### Pull (tag) → repin (digest) → recreate → restart

```bash
# Pull latest tag
sudo podman pull "${IMAGE}"
> ... pulled ...

# Repin to digest
export IMAGE_DIGEST="$(sudo podman image inspect "${IMAGE}" --format '{{index .RepoDigests 0}}')"
echo "${IMAGE_DIGEST}"
> HARBOR_FQDN/turtle/sensor@sha256:...

export IMAGE_REF="${IMAGE_DIGEST}"

# Recreate container with pinned digest
sudo podman rm -f "${SVC}" 2>/dev/null || true
sudo podman create \
  --name "${SVC}" \
  --replace \
  --log-driver=journald \
  --env-file "${ENV_FILE}" \
  -v "${OTX_ROOT}:${OTX_ROOT}:Z" \
  "${IMAGE_REF}"
> container created

# Restart service
sudo systemctl restart "${SVC}.service"
> restarted

sudo podman ps --filter "name=${SVC}" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
> turtle-sensor  HARBOR_FQDN/turtle/sensor@sha256:...  Up ...
```

## Index: 11) Rollback procedure (two options)

### Option A: Podman rollback (if supported / configured)

```bash
sudo podman rollback "${SVC}" || true
> rolled back (if supported)  (or)  > error/unsupported

sudo systemctl restart "${SVC}.service"
> restarted
```

### Option B: Roll back by pinning to the previous recorded digest (always works)

```bash
# Set IMAGE_REF to your previously recorded digest and re-create container:
# export IMAGE_REF="HARBOR_FQDN/turtle/sensor@sha256:PREVIOUS..."
# then run the same recreate + restart steps from Index: 10.
```

## Index: 12) Uninstall / cleanup

### Remove service + container (keeps /opt/otxapps data unless you delete it)

```bash
sudo systemctl disable --now "${SVC}.service" 2>/dev/null || true
> disabled (or none)

sudo rm -f "${UNIT_FILE}"
sudo rm -rf "/etc/systemd/system/${SVC}.service.d"
sudo systemctl daemon-reload
> reloaded

sudo podman rm -f "${SVC}" 2>/dev/null || true
> removed

# Optional: CA cleanup (only if you installed it specifically for this)
# sudo rm -f /etc/pki/ca-trust/source/anchors/turtle-internal-ca.pem
# sudo update-ca-trust
```

## Index: 13) Operator checklist

### Before / After

```bash
# Before:
# - Host hardened; SELinux Enforcing
# - CA trust installed + validated against Harbor
# - Harbor login works
# - Controllers reachable (direct or via proxy)
# - /opt/otxapps created
# - /etc/turtle/sensor.env validated

# After:
# - service running
# - logs clean (no TLS/CA errors)
# - sensor registers / checks in
# - image digest recorded (RepoDigest)
```
