[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [Partition Hardening](index.md)

# squid.service FAILED — Missing Log Directory + Missing ACL File After CIS /var Hardening
**Host:** all-vantls-m001

---

## Initial Status

```text
● squid.service - Squid caching proxy
   Loaded: loaded (/usr/lib/systemd/system/squid.service; enabled; vendor preset: disabled)
   Active: failed (Result: exit-code) since Thu 2025-12-11 21:12:44 GMT; 15h ago
     Docs: man:squid(8)
  Process: 2282 ExecStart=/usr/sbin/squid --foreground $SQUID_OPTS -f ${SQUID_CONF} (code=exited, status=1/FAILURE)
  Process: 2253 ExecStartPre=/usr/libexec/squid/cache_swap.sh (code=exited, status=0/SUCCESS)
 Main PID: 2282 (code=exited, status=1/FAILURE)
```

```bash
sudo journalctl -u squid.service
```

```text
-- Logs begin at Thu 2025-12-11 21:12:35 GMT, end at Fri 2025-12-12 12:48:43 GMT. --
Dec 11 21:12:44 all-vantls-m001 systemd[1]: Starting Squid caching proxy...
Dec 11 21:12:44 all-vantls-m001 squid[2282]: 2025/12/11 21:12:44| ERROR: Can not open file /etc/squid/whitelist_sites.acl for reading
Dec 11 21:12:44 all-vantls-m001 squid[2282]: 2025/12/11 21:12:44| Warning: empty ACL: acl whitelist_sites dstdomain "/etc/squid/whitelist_sites.acl"
Dec 11 21:12:44 all-vantls-m001 squid[2282]: WARNING: Cannot write log file: /var/log/squid/cache.log
Dec 11 21:12:44 all-vantls-m001 squid[2282]: /var/log/squid/cache.log: No such file or directory
Dec 11 21:12:44 all-vantls-m001 squid[2282]:          messages will be sent to 'stderr'.
Dec 11 21:12:44 all-vantls-m001 (squid-1)[2352]: FATAL: Cannot open '/var/log/squid/access.log' because
                                                 the parent directory does not exist.
                                                 Please create the directory.
Dec 11 21:12:44 all-vantls-m001 squid[2282]: Squid Parent: squid-1 process 2490 will not be restarted for 3600 seconds due to repeated, frequent failures
Dec 11 21:12:44 all-vantls-m001 squid[2282]: Exiting due to repeated, frequent failures
Dec 11 21:12:44 all-vantls-m001 systemd[1]: squid.service: Main process exited, code=exited, status=1/FAILURE
Dec 11 21:12:44 all-vantls-m001 systemd[1]: squid.service: Failed with result 'exit-code'.
Dec 11 21:12:44 all-vantls-m001 systemd[1]: Failed to start Squid caching proxy.
Dec 11 21:12:44 all-vantls-m001 systemd[1]: squid.service: Unit cannot be reloaded because it is inactive.
```

---

## Context

After CIS `/var` hardening (encrypted `/var`), Squid can fail if:

- expected log directories under `/var/log` are missing, and/or
- locally referenced ACL include files under `/etc/squid` are missing

In this case, **both** conditions are present.

---

## Root Causes

1. **Missing ACL file**
   - `/etc/squid/whitelist_sites.acl` referenced by `acl whitelist_sites dstdomain "/etc/squid/whitelist_sites.acl"`
   - Squid logs: `ERROR: Can not open file ... for reading`
   - Result: ACL becomes empty (warning), and config may be considered invalid depending on policy

2. **Missing log directory**
   - `/var/log/squid` does not exist
   - Squid cannot write:
     - `/var/log/squid/cache.log`
     - `/var/log/squid/access.log`
   - Result: **FATAL** and repeated child failures → service exits

---

## Remediation Applied (RHEL 8–Supported)

### Step 1 — Restore expected Squid log directory

```bash
sudo mkdir -p /var/log/squid
sudo chown -R squid:squid /var/log/squid
sudo chmod 750 /var/log/squid
```

### Step 2 — Restore SELinux context (REQUIRED after encrypted `/var`)

```bash
sudo restorecon -Rv /var/log/squid
```

### Step 3 — Address missing ACL include file

#### Option A (preferred) — Restore the file from baseline / config management

```bash
sudo ls -l /etc/squid/whitelist_sites.acl
```

```text
> Expected:
>   -rw-r--r-- 1 root root ... /etc/squid/whitelist_sites.acl
```

If it should exist (per baseline), restore it via your config source (BladeLogic/Ansible/etc).

#### Option B (safe placeholder to unblock startup) — Create an empty file

> Use only if you confirm the ACL is optional and an empty list is acceptable.

```bash
sudo install -o root -g root -m 0644 /dev/null /etc/squid/whitelist_sites.acl
sudo restorecon -v /etc/squid/whitelist_sites.acl
```

---

## Validate Configuration

```bash
sudo squid -k parse
```

```text
> Expected:
>   (no fatal errors)
```

If your build does not support `-k parse`, use:

```bash
sudo squid -z -N
```

```text
> Expected:
>   (no fatal errors about missing directories/files)
```

---

## Service Recovery

```bash
sudo systemctl start squid
systemctl status squid
```

```text
> Expected:
>   Active: active (running)
```

---

## Final Verification

### Logs are writable

```bash
sudo -u squid test -w /var/log/squid && echo "logdir writable"
sudo ls -l /var/log/squid | head
```

```text
> Expected:
>   logdir writable
>   cache.log and access.log present (or created shortly after start)
```

### Squid is listening (default 3128)

```bash
sudo ss -lntp | egrep '(:3128)\b' || true
```

```text
> Expected:
>   LISTEN on :3128 with process "squid"
```

### Quick local proxy check (optional)

```bash
curl -sS -I -x http://127.0.0.1:3128 http://example.com/ | head -n 5
```

```text
> Expected:
>   HTTP/1.1 200 OK   (or)
>   HTTP/1.1 3xx/4xx depending on policy (still proves proxy is responding)
```

---

## Notes for Audit / Closure

- Failure cause: missing `/var/log/squid` after CIS `/var` hardening **plus** missing `/etc/squid/whitelist_sites.acl`
- CIS hardening exposed legacy filesystem/config assumptions; no rollback required
- Resolution aligns with RHEL permissions + SELinux best practices
