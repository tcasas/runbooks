# httpd.service FAILED — Missing Log Directory + Stale DocumentRoot After CIS /var Hardening
**Host:** all-vantls-m001

---

## Initial Status

```text
● httpd.service - The Apache HTTP Server
   Loaded: loaded (/usr/lib/systemd/system/httpd.service; enabled; vendor preset: disabled)
  Drop-In: /usr/lib/systemd/system/httpd.service.d
           └─php-fpm.conf
   Active: failed (Result: exit-code) since Thu 2025-12-11 21:12:44 GMT; 15h ago
     Docs: man:httpd.service(8)
  Process: 2248 ExecStart=/usr/sbin/httpd $OPTIONS -DFOREGROUND (code=exited, status=1/FAILURE)
 Main PID: 2248 (code=exited, status=1/FAILURE)
   Status: "Reading configuration..."
```

```bash
sudo journalctl -u httpd.service
```

```text
-- Logs begin at Thu 2025-12-11 21:12:35 GMT, end at Fri 2025-12-12 12:44:17 GMT. --
Dec 11 21:12:44 all-vantls-m001 systemd[1]: Starting The Apache HTTP Server...
Dec 11 21:12:44 all-vantls-m001 httpd[2248]: AH00112: Warning: DocumentRoot [/clients/bladelogic/platform/htdoc] does not exist
Dec 11 21:12:44 all-vantls-m001 httpd[2248]: (2)No such file or directory: AH02291: Cannot access directory '/etc/httpd/logs/' for main error log
Dec 11 21:12:44 all-vantls-m001 httpd[2248]: (2)No such file or directory: AH02291: Cannot access directory '/etc/httpd/logs/' for error log of vhost defined at /etc/httpd/conf/httpd.conf
Dec 11 21:12:44 all-vantls-m001 httpd[2248]: AH00014: Configuration check failed
Dec 11 21:12:44 all-vantls-m001 systemd[1]: httpd.service: Main process exited, code=exited, status=1/FAILURE
Dec 11 21:12:44 all-vantls-m001 systemd[1]: httpd.service: Failed with result 'exit-code'.
Dec 11 21:12:44 all-vantls-m001 systemd[1]: Failed to start The Apache HTTP Server.
```

---

## Context

After CIS `/var` hardening (encrypted `/var`):

- Apache relies on legacy filesystem paths that must exist at startup
- `/etc/httpd/logs` is a symlink to `/var/log/httpd`
- The symlink existed, but the **target directory did not**
- A stale global `DocumentRoot` from BladeLogic was still configured

This is **NOT** a CIS failure.  
This is Apache enforcing filesystem + config correctness.

---

## Root Causes

1. **Missing Apache log target**
   - `/etc/httpd/logs` → `/var/log/httpd`
   - `/var/log/httpd` did not exist
   - Result: fatal `AH02291` errors

2. **Stale global DocumentRoot**
   - `/clients/bladelogic/platform/htdoc` no longer exists
   - Logged as `AH00112` (warning)
   - Not fatal by itself, but must be corrected

---

## Remediation Applied (RHEL 8–Supported)

### Step 1 — Restore expected Apache log directory

```bash
sudo mkdir -p /var/log/httpd
sudo chown root:root /var/log/httpd
sudo chmod 755 /var/log/httpd
```

### Step 2 — Restore SELinux context (REQUIRED after encrypted `/var`)

```bash
sudo restorecon -Rv /var/log/httpd
```

---

### Step 3 — Replace stale global DocumentRoot

#### Create standard web root (safe even if empty)

```bash
sudo mkdir -p /var/www/html
sudo chown -R root:root /var/www
sudo chmod 755 /var/www
sudo chmod 755 /var/www/html
```

#### Backup and update `httpd.conf`

```bash
sudo cp -a /etc/httpd/conf/httpd.conf \
/etc/httpd/conf/httpd.conf.bak.$(date +%F_%H%M%S)
```

```bash
sudo sed -i \
-e 's#^\(\s*DocumentRoot\)\s\+/clients/bladelogic/platform/htdoc#\1 "/var/www/html"#' \
-e 's#<Directory "/clients/bladelogic/platform/htdoc">#<Directory "/var/www/html">#' \
/etc/httpd/conf/httpd.conf
```

### Step 4 — Fix SELinux labels

```bash
sudo restorecon -Rv /var/www
sudo restorecon -Rv /etc/httpd
```

---

## Validate Configuration

```bash
sudo apachectl configtest
```

```text
> Expected:
>   Syntax OK
```

---

## Service Recovery

```bash
sudo systemctl start httpd
systemctl status httpd
```

```text
> Expected:
>   Active: active (running)
```

---

## Final Verification

### Log path resolution

```bash
readlink -f /etc/httpd/logs
ls -ald /var/log/httpd
```

```text
> Expected:
>   /var/log/httpd
>   drwxr-xr-x root root /var/log/httpd
```

### Apache is listening

```bash
sudo ss -lntp | egrep '(:80|:443)\b' || true
```

```text
> Expected:
>   LISTEN on :80 and/or :443 with process "httpd"
```

### Local HTTP response

```bash
curl -sS -I http://127.0.0.1/ | head -n 5
```

```text
> Expected:
>   HTTP/1.1 200 OK
>   HTTP/1.1 301/302
>   HTTP/1.1 403 Forbidden
```

---

## Notes for Audit / Closure

- Failure cause: missing `/var/log/httpd` after CIS `/var` hardening **plus** stale BladeLogic `DocumentRoot`
- CIS hardening correctly exposed misconfiguration
- Resolution aligns with RHEL + SELinux best practices
- No rollback required
