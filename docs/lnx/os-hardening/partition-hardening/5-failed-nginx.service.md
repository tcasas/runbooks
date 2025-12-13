# nginx.service FAILED — Missing Log Directory After CIS /var Hardening
**Host:** all-vantls-m001

---

## Initial Status

```text
● nginx.service - The nginx HTTP and reverse proxy server
   Loaded: loaded (/usr/lib/systemd/system/nginx.service; enabled; vendor preset: disabled)
  Drop-In: /usr/lib/systemd/system/nginx.service.d
           └─php-fpm.conf
   Active: failed (Result: exit-code) since Thu 2025-12-11 21:12:44 GMT; 15h ago
  Process: 2271 ExecStartPre=/usr/sbin/nginx -t (code=exited, status=1/FAILURE)
  Process: 2251 ExecStartPre=/usr/bin/rm -f /run/nginx.pid (code=exited, status=0/SUCCESS)
```

```bash
sudo journalctl -u nginx.service
```

```text
-- Logs begin at Thu 2025-12-11 21:12:35 GMT, end at Fri 2025-12-12 12:46:11 GMT. --
Dec 11 21:12:44 all-vantls-m001 systemd[1]: Starting The nginx HTTP and reverse proxy server...
Dec 11 21:12:44 all-vantls-m001 nginx[2271]: nginx: [alert] could not open error log file: open() "/var/log/nginx/error.log" failed (2: No such file or directory)
Dec 11 21:12:44 all-vantls-m001 nginx[2271]: nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
Dec 11 21:12:44 all-vantls-m001 nginx[2271]: 2025/12/11 21:12:44 [emerg] 2271#0: open() "/var/log/nginx/error.log" failed (2: No such file or directory)
Dec 11 21:12:44 all-vantls-m001 nginx[2271]: nginx: configuration file /etc/nginx/nginx.conf test failed
Dec 11 21:12:44 all-vantls-m001 systemd[1]: nginx.service: Control process exited, code=exited status=1
Dec 11 21:12:44 all-vantls-m001 systemd[1]: nginx.service: Failed with result 'exit-code'.
Dec 11 21:12:44 all-vantls-m001 systemd[1]: Failed to start The nginx HTTP and reverse proxy server.
```

---

## Context

- `/var` was hardened and encrypted per CIS
- nginx expects `/var/log/nginx` to exist **before startup**
- The directory was missing at service start
- nginx **fails fast by design** when log paths are unavailable

This is **NOT** a configuration syntax issue.  
This is **NOT** an nginx bug.  
This is a **filesystem expectation exposed by CIS hardening**.

---

## Root Cause

- `/var/log/nginx` directory did not exist
- nginx could not open `/var/log/nginx/error.log`
- Startup aborted during `ExecStartPre` (`nginx -t`)

---

## Remediation Applied (RHEL 8–Supported)

### Create expected log directory

```bash
sudo mkdir -p /var/log/nginx
sudo chown root:root /var/log/nginx
sudo chmod 755 /var/log/nginx
```

### Restore SELinux context (REQUIRED after encrypted `/var`)

```bash
sudo restorecon -Rv /var/log/nginx
```

---

## Service Recovery

```bash
sudo systemctl start nginx
systemctl status nginx
```

```text
> Expected:
>   Active: active (running)
```

---

## Final Verification

### Log directory exists and is labeled correctly

```bash
ls -ald /var/log/nginx
ls -alZ /var/log/nginx | head
```

```text
> Expected:
>   drwxr-xr-x root root /var/log/nginx
>   system_u:object_r:httpd_log_t:s0
```

### nginx is listening

```bash
sudo ss -lntp | egrep '(:80|:443)\b' || true
```

```text
> Expected:
>   LISTEN on :80 and/or :443 with process "nginx"
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

- Failure cause: missing `/var/log/nginx` after CIS `/var` hardening
- nginx behavior is expected and documented
- Resolution aligns with RHEL + SELinux best practices
- No rollback required
