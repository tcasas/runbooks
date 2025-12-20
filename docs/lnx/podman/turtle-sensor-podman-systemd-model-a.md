[Runbooks Index](../../index.md) / [Linux](../index.md) / [Podman](index.md)

# Turtle-Sensor Podman + systemd Deployment (Model-A: systemd Owns Container)

**Model-A:** `systemd` creates and manages the container lifecycle. There is **no** persistent named container created manually; all container settings live in the unit file.

**Target:** Hardened RHEL (rootful Podman).

**Conventions:**

- Replace `ALL_CAPS` placeholders before running commands.
- Expected outputs are prefixed with `>` for quick diffing.
- All Podman commands use `sudo` to keep the rootful store consistent.

## 0) Set variables (per host)

```bash
# Registry + image coordinates
export HARBOR_FQDN="HARBOR_FQDN_OR_VIP"
export IMAGE_REPO="turtle/sensor"
export IMAGE_TAG="prod"                 # prod | staging | specific tag
export IMAGE="${HARBOR_FQDN}/${IMAGE_REPO}:${IMAGE_TAG}"

# Service name (systemd unit)
export SVC="turtle-sensor"

# Paths
export ETC_DIR="/etc/turtle"
export ENV_FILE="${ETC_DIR}/sensor.env"
export OTX_ROOT="/opt/otxapps"
export LOG_DIR="${OTX_ROOT}/turtle-sensor/log"
export DATA_DIR="${OTX_ROOT}/turtle-sensor/data"

# systemd unit
export UNIT_FILE="/etc/systemd/system/${SVC}.service"
```

## 1) Prereqs (baseline)

```bash
sudo dnf -y install podman jq curl ca-certificates ripgrep openssl
> Complete!

podman --version
> podman version X.Y.Z

getenforce
> Enforcing

timedatectl status | rg -n "System clock synchronized|NTP service" || true
> System clock synchronized: yes
```

## 2) Directory layout (host)

```bash
sudo install -d -m 0750 -o root -g root "${ETC_DIR}"
sudo install -d -m 0755 -o root -g root "${OTX_ROOT}"
sudo install -d -m 0755 -o root -g root "${LOG_DIR}" "${DATA_DIR}"
> created

ls -ald "${ETC_DIR}" "${LOG_DIR}" "${DATA_DIR}"
> drwxr-x--- root root /etc/turtle
> drwxr-xr-xr-x root root /opt/otxapps/turtle-sensor/log
> drwxr-xr-xr-x root root /opt/otxapps/turtle-sensor/data
```

## 3) CA trust (system-wide)

```bash
sudo cp INTERNAL_CA.pem /etc/pki/ca-trust/source/anchors/turtle-internal-ca.pem
sudo update-ca-trust
> updated

openssl s_client -connect "${HARBOR_FQDN}:443" -servername "${HARBOR_FQDN}" </dev/null 2>/dev/null | rg "Verify return code"
> Verify return code: 0 (ok)
```

## 4) Registry auth + pull (for digest resolution)

```bash
# Rootful podman
sudo podman login "${HARBOR_FQDN}"
> Login Succeeded!

sudo podman pull "${IMAGE}"
> ... pulled ...
```

## 5) Resolve and pin image digest (authoritative)

```bash
# Resolve the digest that backs the tag
export IMAGE_DIGEST="$(
  sudo podman image inspect "${IMAGE}" --format '{{json .RepoDigests}}' \
  | jq -r '.[]' \
  | rg -m 1 "^${HARBOR_FQDN}/${IMAGE_REPO}@sha256:"
)"

test -n "${IMAGE_DIGEST}"
> (no output)

echo "${IMAGE_DIGEST}"
> HARBOR_FQDN/turtle/sensor@sha256:...

# From here on, the UNIT FILE uses this pinned reference
```

## 6) Environment file (`/etc/turtle/sensor.env`)

```bash
sudo tee "${ENV_FILE}" >/dev/null <<'EOF'
# Turtle-Sensor runtime config

CONTROLLER_PRIMARY_NAME=primary-controller
CONTROLLER_SECONDARY_NAME=secondary-controller

REQUESTS_CA_BUNDLE=/etc/pki/tls/certs/ca-bundle.crt

# Optional proxy
HTTPS_PROXY=
NO_PROXY=localhost,127.0.0.1

SENSOR_LOG_DIR=/opt/otxapps/turtle-sensor/log
SENSOR_DATA_DIR=/opt/otxapps/turtle-sensor/data

LOG_LEVEL=INFO
SENSOR_MODE=run
EOF
> wrote

sudo chmod 0640 "${ENV_FILE}"
sudo chown root:root "${ENV_FILE}"
> secured
```

## 7) Create systemd unit (container is created at service start)

> This unit uses `podman run` directly. `systemd` is now the single source of truth.

```bash
sudo tee "${UNIT_FILE}" >/dev/null <<EOF
[Unit]
Description=Turtle Sensor (Podman, systemd-owned)
Wants=network-online.target
After=network-online.target

[Service]
Type=notify
NotifyAccess=all

# Hard stop before re-create
ExecStartPre=/usr/bin/podman rm -f ${SVC}

# Create + run container
ExecStart=/usr/bin/podman run \\
  --name ${SVC} \\
  --rm \\
  --log-driver=journald \\
  --env-file ${ENV_FILE} \\
  -v ${LOG_DIR}:${LOG_DIR}:Z \\
  -v ${DATA_DIR}:${DATA_DIR}:Z \\
  ${IMAGE_DIGEST}

ExecStop=/usr/bin/podman stop ${SVC}

Restart=on-failure
RestartSec=5
NoNewPrivileges=true
PrivateTmp=true
ProtectHome=true

[Install]
WantedBy=multi-user.target
EOF
> wrote unit
```

## 8) Enable + start

```bash
sudo systemctl daemon-reload
> reloaded

sudo systemctl enable --now "${SVC}.service"
> enabled
> started
```

## 9) Verification

```bash
systemctl status "${SVC}.service" --no-pager
> Active: active (running)

journalctl -u "${SVC}.service" -n 200 --no-pager
> ... startup logs ...

# Verify running container + pinned image
sudo podman ps --format "table {{.Names}}\t{{.Image}}\t{{.Status}}"
> turtle-sensor  HARBOR_FQDN/turtle/sensor@sha256:...  Up ...
```

## 10) Upgrade (Model-A)

```bash
# Pull tag
sudo podman pull "${IMAGE}"
> ... pulled ...

# Resolve NEW digest
export IMAGE_DIGEST="$(
  sudo podman image inspect "${IMAGE}" --format '{{json .RepoDigests}}' \
  | jq -r '.[]' \
  | rg -m 1 "^${HARBOR_FQDN}/${IMAGE_REPO}@sha256:"
)"

# Update unit file IMAGE_DIGEST value
sudo sed -i "s|@sha256:.*|${IMAGE_DIGEST#*@}|g" "${UNIT_FILE}"
> updated

sudo systemctl daemon-reload
sudo systemctl restart "${SVC}.service"
> restarted
```

## 11) Rollback (Model-A)

```bash
# Edit the unit file and restore a previous digest
sudo sed -i "s|@sha256:.*|sha256:PREVIOUS...|g" "${UNIT_FILE}"

sudo systemctl daemon-reload
sudo systemctl restart "${SVC}.service"
> restarted
```

## 12) Uninstall

```bash
sudo systemctl disable --now "${SVC}.service"
sudo rm -f "${UNIT_FILE}"
sudo systemctl daemon-reload
> removed
```
