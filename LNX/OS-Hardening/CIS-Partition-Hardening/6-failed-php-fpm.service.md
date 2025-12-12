# php-fpm.service FAILED — Missing Log Directory After CIS /var Hardening
**Host:** all-vantls-m001

---

## Initial Status

```text
● php-fpm.service - The PHP FastCGI Process Manager
   Loaded: loaded (/usr/lib/systemd/system/php-fpm.service; disabled; vendor preset: disabled)
   Active: failed (Result: exit-code) since Thu 2025-12-11 21:12:43 GMT; 15h ago
  Process: 1716 ExecStart=/usr/sbin/php-fpm --nodaemonize (code=exited, status=78)
 Main PID: 1716 (code=exited, status=78)
```

```bash
sudo journalctl -u php-fpm.service
```

```text
-- Logs begin at Thu 2025-12-11 21:12:35 GMT, end at Fri 2025-12-12 12:47:40 GMT. --
Dec 11 21:12:43 all-vantls-m001 systemd[1]: Starting The PHP FastCGI Process Manager...
Dec 11 21:12:43 all-vantls-m001 php-fpm[1716]: [11-Dec-2025 21:12:43] ERROR: failed to open error_log (/var/log/php-fpm/error.log): No such file or directory (2)
Dec 11 21:12:43 all-vantls-m001 php-fpm[1716]: [11-Dec-2025 21:12:43] ERROR: failed to post process the configuration
Dec 11 21:12:43 all-vantls-m001 php-fpm[1716]: [11-Dec-2025 21:12:43] ERROR: FPM initialization failed
Dec 11 21:12:43 all-vantls-m001 systemd[1]: php-fpm.service: Main process exited, code=exited, status=78/CONFIG
Dec 11 21:12:43 all-vantls-m001 systemd[1]: php-fpm.service: Failed with result 'exit-code'.
Dec 11 21:12:43 all-vantls-m001 systemd[1]: Failed to start The PHP FastCGI Process Manager.
```

---

## Context

- `/var` was hardened and encrypted per CIS
- `php-fpm` expects `/var/log/php-fpm` to exist **before startup**
- The directory did not exist after `/var` migration
- `php-fpm` **fails fast by design** when `error_log` cannot be opened

This is **NOT** a PHP configuration error.  
This is **NOT** an SELinux denial.  
This is a **filesystem expectation exposed by CIS hardening**.

---

## Root Cause

- `/var/log/php-fpm` directory was missing
- `php-fpm` could not open `/var/log/php-fpm/error.log`
- Configuration post-processing failed
- Service exited with **status=78 (CONFIG)**

---

## Remediation Applied (RHEL 8–Supported)

### Create expected log directory

```bash
sudo mkdir -p /var/log/php-fpm
sudo chown root:root /var/log/php-fpm
sudo chmod 755 /var/log/php-fpm
```

### Restore SELinux context (REQUIRED after encrypted `/var`)

```bash
sudo restorecon -Rv /var/log/php-fpm
```

---

## Service Recovery

```bash
sudo systemctl start php-fpm
systemctl status php-fpm
```

```text
> Expected:
>   Active: active (running)
```

---

## Final Verification

### Log directory exists and is labeled correctly

```bash
ls -ald /var/log/php-fpm
ls -alZ /var/log/php-fpm | head
```

```text
> Expected:
>   drwxr-xr-x root root /var/log/php-fpm
>   system_u:object_r:httpd_log_t:s0
```

### php-fpm socket/process check

```bash
sudo ss -lntup | grep php-fpm || true
pgrep -a php-fpm
```

```text
> Expected:
>   php-fpm master + worker processes present
```

---

## Notes for Audit / Closure

- Failure cause: missing `/var/log/php-fpm` after CIS `/var` hardening
- php-fpm behavior is expected and documented
- Resolution aligns with RHEL + SELinux best practices
- No rollback required
