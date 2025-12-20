[Runbooks Index](../../index.md) / [Linux](../index.md) / [Podman](index.md)

# Turtle-Sensor Podman + systemd Deployment (Model-B + Digest Recording)

**Model-B:** Operator creates or replaces the named container. Systemd only starts/stops that container—no container creation inside the unit.

**Target:** Hardened RHEL (rootful Podman).

**Conventions:**

- Replace `ALL_CAPS` placeholders before running commands.
- Expected outputs are prefixed with `>` for quick diffing.
- All Podman commands use `sudo` to keep the rootful store consistent.

## 0) Set variables (per host)

```bash
# Harbor registry + image coordinates
export HARBOR_FQDN="HARBOR_FQDN_OR_VIP"
export IMAGE_REPO="turtle/sensor"
export IMAGE_TAG="prod"                 # prod | staging | specific tag
export IMAGE="${HARBOR_FQDN}/${IMAGE_REPO}:${IMAGE_TAG}"

# Service/container name (must be consistent everywhere)
export SVC="turtle-sensor"

# Host paths (per your standard)
export ETC_DIR="/etc/turtle"
export ENV_FILE="${ETC_DIR}/sensor.env"
export OTX_ROOT="/opt/otxapps"
export LOG_DIR="${OTX_ROOT}/turtle-sensor/log"
export DATA_DIR="${OTX_ROOT}/turtle-sensor/data"

# systemd + digest records
export UNIT_FILE="/etc/systemd/system/${SVC}.service"
export DIGEST_FILE="${ETC_DIR}/sensor.image.digest"
export DIGEST_HISTORY_FILE="${ETC_DIR}/sensor.image.digest.history"

# Optional proxy (blank = none)
export HTTPS_PROXY_URL="http://PROXY_HOST:PROXY_PORT"
export NO_PROXY_LIST="localhost,127.0.0.1,.corp.example.com"
```

## 1) Prereqs (packages + baseline checks)

```bash
# Install required packages (podman + tooling used below)
sudo dnf -y install podman jq curl ca-certificates ripgrep openssl
> Complete!

# Confirm runtime versions
podman --version
> podman version X.Y.Z

systemctl --version | head -n 1
> systemd ...

# Confirm SELinux mode (expected Enforcing on hardened RHEL)
getenforce
> Enforcing

# Confirm time sync signals (best-effort check; output varies by host config)
timedatectl status | rg -n "System clock synchronized|NTP service|Time zone" || true
> System clock synchronized: yes
> NTP service: active
```

## 2) Directory layout (host)

```bash
# Create config dir (root-only)
sudo install -d -m 0750 -o root -g root "${ETC_DIR}"
> created (or already exists)

# Ensure /opt/otxapps exists
sudo install -d -m 0755 -o root -g root "${OTX_ROOT}"
> created (or already exists)

# Create persistent log + data directories
sudo install -d -m 0755 -o root -g root "${LOG_DIR}" "${DATA_DIR}"
> created (or already exists)

# Verify paths and perms
ls -ald "${ETC_DIR}" "${OTX_ROOT}" "${LOG_DIR}" "${DATA_DIR}"
> drwxr-x--- root root ... /etc/turtle
> drwxr-xr-xr-x root root ... /opt/otxapps
> drwxr-xr-xr-x root root ... /opt/otxapps/turtle-sensor/log
> drwxr-xr-xr-x root root ... /opt/otxapps/turtle-sensor/data
```

## 3) CA trust (preferred: system trust store)

```bash
# Install internal CA bundle into system trust anchors (stable filename)
sudo cp INTERNAL_CA.pem /etc/pki/ca-trust/source/anchors/turtle-internal-ca.pem
> (no output)

# Rebuild system trust
sudo update-ca-trust
> (no output)

# Validate Harbor TLS chain is trusted by the host CA bundle
openssl s_client -connect "${HARBOR_FQDN}:443" -servername "${HARBOR_FQDN}" </dev/null 2>/dev/null | rg "Verify return code|subject=|issuer="
> Verify return code: 0 (ok)
```

## 4) Registry auth + pull (rootful podman)

> Keep `sudo` on all Podman commands to avoid "container not found" across stores.

```bash
sudo podman login "${HARBOR_FQDN}"
> Login Succeeded!

# Pull the requested tag
sudo podman pull "${IMAGE}"
> ... pulled ...

# Quick sanity check: image appears locally
sudo podman images | head
> REPOSITORY ... TAG ... IMAGE ID ... CREATED ... SIZE
```

## 5) Pin to digest (deterministic deployment)

```bash
# Derive a pinned digest reference from the pulled tag.
# Expected result format: HARBOR_FQDN/turtle/sensor@sha256:...

export IMAGE_DIGEST="$(
  sudo podman image inspect "${IMAGE}" --format '{{json .RepoDigests}}' \
  | jq -r '.[]' \
  | rg -m 1 "^${HARBOR_FQDN}/${IMAGE_REPO}@sha256:"
)"

# Fail fast if digest did not resolve (prevents creating a container from an empty ref)
test -n "${IMAGE_DIGEST}"
> (no output)

echo "${IMAGE_DIGEST}"
> HARBOR_FQDN/turtle/sensor@sha256:...

# Use IMAGE_REF everywhere below
export IMAGE_REF="${IMAGE_DIGEST}"
```

## 6) Record digest on-host (audit + rollback)

```bash
# Overwrite "current" digest file (single line)
echo "${IMAGE_REF}" | sudo tee "${DIGEST_FILE}" >/dev/null
> wrote

# Append to history with ISO timestamp, service name, and digest
echo "$(date -Is) ${SVC} ${IMAGE_REF}" | sudo tee -a "${DIGEST_HISTORY_FILE}" >/dev/null
> appended

# Lock down files
sudo chmod 0640 "${DIGEST_FILE}" "${DIGEST_HISTORY_FILE}"
sudo chown root:root "${DIGEST_FILE}" "${DIGEST_HISTORY_FILE}"
> secured

# Verify last entry
sudo tail -n 3 "${DIGEST_HISTORY_FILE}"
> 2025-12-20T06:12:34-06:00 turtle-sensor HARBOR_FQDN/turtle/sensor@sha256:...
```

## 7) Environment file (`/etc/turtle/sensor.env`)

```bash
# Write base env file (use placeholders for proxy injection)
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
SENSOR_LOG_DIR=/opt/otxapps/turtle-sensor/log
SENSOR_DATA_DIR=/opt/otxapps/turtle-sensor/data

# Runtime
LOG_LEVEL=INFO
SENSOR_MODE=run
EOF
> wrote

# Escape '&' for sed replacement safety
export HTTPS_PROXY_URL_ESCAPED="${HTTPS_PROXY_URL//&/\\&}"
export NO_PROXY_LIST_ESCAPED="${NO_PROXY_LIST//&/\\&}"

# Inject proxy values (blank is allowed)
sudo sed -i \
  -e "s|__HTTPS_PROXY_URL__|${HTTPS_PROXY_URL_ESCAPED}|g" \
  -e "s|__NO_PROXY_LIST__|${NO_PROXY_LIST_ESCAPED}|g" \
  "${ENV_FILE}"
> updated

# Lock down env file (contains operational settings; may contain sensitive endpoints)
sudo chmod 0640 "${ENV_FILE}"
sudo chown root:root "${ENV_FILE}"
> secured

# Sanity-check key settings rendered as expected
sudo rg -n "CONTROLLER_|REQUESTS_CA_BUNDLE|HTTPS_PROXY|NO_PROXY|SENSOR_|LOG_LEVEL|SENSOR_MODE" "${ENV_FILE}"
> ... shows configured values ...
```

## 8) Create/replace container (authoritative; systemd does **not** create)

```bash
# Stop service first if it exists (prevents "resource busy" surprises)
sudo systemctl stop "${SVC}.service" 2>/dev/null || true
> stopped (or none)

# Remove existing container definition (safe if missing)
sudo podman rm -f "${SVC}" 2>/dev/null || true
> removed (or none)

# Create container using pinned digest and least-privilege mounts (only log/data)
sudo podman create \
  --name "${SVC}" \
  --replace \
  --log-driver=journald \
  --env-file "${ENV_FILE}" \
  -v "${LOG_DIR}:${LOG_DIR}:Z" \
  -v "${DATA_DIR}:${DATA_DIR}:Z" \
  "${IMAGE_REF}"
> container created

# Verify container is present and in Created state
sudo podman ps -a --filter "name=${SVC}"
> ... STATUS: Created
```

## 9) Generate & install systemd unit (no `--new`)

```bash
# Generate a unit that manages the EXISTING named container
sudo podman generate systemd \
  --name "${SVC}" \
  > "${UNIT_FILE}"
> wrote unit

# Secure unit file permissions
sudo chmod 0644 "${UNIT_FILE}"
sudo chown root:root "${UNIT_FILE}"
> secured

# Reload systemd to pick up the new unit
sudo systemctl daemon-reload
> reloaded
```

## 10) Enable + start

```bash
sudo systemctl enable --now "${SVC}.service"
> enabled
> started
```

## 11) Verification (consistent + actionable)

```bash
# 11a) systemd health
systemctl is-active "${SVC}.service"
> active

systemctl status "${SVC}.service" --no-pager
> Active: active (running)

# 11b) service logs (look for TLS/CA/proxy/controller errors)
journalctl -u "${SVC}.service" -n 200 --no-pager
> ... startup logs (no TLS/CA errors) ...

# 11c) container state + pinned image reference (must show @sha256)
sudo podman ps --filter "name=${SVC}" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
> turtle-sensor  HARBOR_FQDN/turtle/sensor@sha256:...  Up ...

# 11d) confirm env was loaded into container
sudo podman exec "${SVC}" /bin/bash -lc 'env | rg "SENSOR_|LOG_LEVEL|HTTPS_PROXY|NO_PROXY|CONTROLLER_" | sort'
> ... expected vars present ...

# 11e) confirm the on-host recorded digest matches the running container image
echo "recorded=$(sudo cat "${DIGEST_FILE}")"
> recorded=HARBOR_FQDN/turtle/sensor@sha256:...

echo "running=$(sudo podman inspect "${SVC}" --format '{{.ImageName}}')"
> running=HARBOR_FQDN/turtle/sensor@sha256:...
```

## 12) Upgrade (safe): pull tag → repin digest → record → recreate → restart → verify

```bash
# Pull latest for the chosen tag
sudo podman pull "${IMAGE}"
> ... pulled ...

# Recompute digest ref
export IMAGE_DIGEST="$(
  sudo podman image inspect "${IMAGE}" --format '{{json .RepoDigests}}' \
  | jq -r '.[]' \
  | rg -m 1 "^${HARBOR_FQDN}/${IMAGE_REPO}@sha256:"
)"
test -n "${IMAGE_DIGEST}"
> (no output)

export IMAGE_REF="${IMAGE_DIGEST}"
echo "${IMAGE_REF}"
> HARBOR_FQDN/turtle/sensor@sha256:...

# Record digest (current + history)
echo "${IMAGE_REF}" | sudo tee "${DIGEST_FILE}" >/dev/null
> wrote
echo "$(date -Is) ${SVC} ${IMAGE_REF}" | sudo tee -a "${DIGEST_HISTORY_FILE}" >/dev/null
> appended

# Recreate container from pinned digest
sudo systemctl stop "${SVC}.service"
> stopped

sudo podman rm -f "${SVC}" 2>/dev/null || true
> removed (or none)

sudo podman create \
  --name "${SVC}" \
  --replace \
  --log-driver=journald \
  --env-file "${ENV_FILE}" \
  -v "${LOG_DIR}:${LOG_DIR}:Z" \
  -v "${DATA_DIR}:${DATA_DIR}:Z" \
  "${IMAGE_REF}"
> container created

# Restart service and verify image pin
sudo systemctl start "${SVC}.service"
> started

sudo podman ps --filter "name=${SVC}" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
> turtle-sensor  HARBOR_FQDN/turtle/sensor@sha256:...  Up ...
```

## 13) Rollback (always works): choose digest → record → recreate → restart

```bash
# Option A: roll back to the last "current" recorded digest
export IMAGE_REF="$(sudo cat "${DIGEST_FILE}")"
test -n "${IMAGE_REF}"
> (no output)

# Option B: pick an older digest from history and set IMAGE_REF manually
sudo tail -n 20 "${DIGEST_HISTORY_FILE}"
> 2025-... turtle-sensor HARBOR_FQDN/turtle/sensor@sha256:OLDER...

# If selecting a specific older digest, set it like:
# export IMAGE_REF="HARBOR_FQDN/turtle/sensor@sha256:PREVIOUS..."

# Record the rollback choice (so host state matches reality)
echo "${IMAGE_REF}" | sudo tee "${DIGEST_FILE}" >/dev/null
> wrote
echo "$(date -Is) ${SVC} ${IMAGE_REF}" | sudo tee -a "${DIGEST_HISTORY_FILE}" >/dev/null
> appended

# Recreate container + restart
sudo systemctl stop "${SVC}.service"
> stopped

sudo podman rm -f "${SVC}" 2>/dev/null || true
> removed (or none)

sudo podman create \
  --name "${SVC}" \
  --replace \
  --log-driver=journald \
  --env-file "${ENV_FILE}" \
  -v "${LOG_DIR}:${LOG_DIR}:Z" \
  -v "${DATA_DIR}:${DATA_DIR}:Z" \
  "${IMAGE_REF}"
> container created

sudo systemctl start "${SVC}.service"
> started

sudo podman ps --filter "name=${SVC}" --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
> turtle-sensor  HARBOR_FQDN/turtle/sensor@sha256:...  Up ...
```

## 14) Uninstall / cleanup (keeps `/opt/otxapps` data unless removed)

```bash
# Stop + disable the service
sudo systemctl disable --now "${SVC}.service" 2>/dev/null || true
> disabled (or none)

# Remove unit + reload systemd
sudo rm -f "${UNIT_FILE}"
sudo systemctl daemon-reload
> reloaded

# Remove container definition (data remains on host)
sudo podman rm -f "${SVC}" 2>/dev/null || true
> removed

# Optional: CA cleanup (only if installed specifically for this host/app)
# sudo rm -f /etc/pki/ca-trust/source/anchors/turtle-internal-ca.pem
# sudo update-ca-trust
```
