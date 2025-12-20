[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [Partition Hardening](index.md)

# auditd.service FAILED — Post-CIS Hardening Remediation
**Host:** all-vantls-m001

---

## Initial Status

```text
● auditd.service - Security Auditing Service
   Loaded: loaded (/usr/lib/systemd/system/auditd.service; enabled; vendor preset: enabled)
   Active: failed (Result: exit-code) since Thu 2025-12-11 21:12:43 GMT; 15h ago
     Docs: man:auditd(8)
           https://github.com/linux-audit/audit-documentation
  Process: 1661 ExecStart=/sbin/auditd (code=exited, status=6)
```

```bash
sudo journalctl -u auditd.service
```

```text
-- Logs begin at Thu 2025-12-11 21:12:35 GMT, end at Fri 2025-12-12 12:41:13 GMT. --
Dec 11 21:12:42 all-vantls-m001 systemd[1]: Starting Security Auditing Service...
Dec 11 21:12:42 all-vantls-m001 systemd[1]: auditd.service: Control process exited, code=exited status=6
Dec 11 21:12:42 all-vantls-m001 systemd[1]: auditd.service: Failed with result 'exit-code'.
Dec 11 21:12:42 all-vantls-m001 systemd[1]: Failed to start Security Auditing Service.
Dec 11 21:12:42 all-vantls-m001 systemd[1]: auditd.service: Service RestartSec=100ms expired, scheduling restart.
Dec 11 21:12:42 all-vantls-m001 systemd[1]: auditd.service: Scheduled restart job, restart counter is at 1.
Dec 11 21:12:42 all-vantls-m001 systemd[1]: Stopped Security Auditing Service.
```

---

## Context

- After **CIS `/var` hardening**, `auditd` service often fails due to missing or incorrectly labeled files.
- **First boot behavior**: SELinux relabeling on encrypted `/var` mounts doesn't always finish in time, leading to a mismatch.
- **Expected behavior**: `auditd` cannot start because `/var/log/audit` has **not been labeled** yet (relabeled on restart).

---

## Root Cause

- **Incomplete SELinux relabeling** after `/var` encryption.
- Missing SELinux context for `/var/log/audit`.
- **auditd** requires this directory to be labeled correctly to log events.
- Service exited with **status 6**, and the system showed **degraded**.

---

## Remediation Applied (RHEL 8–Supported)

### Step 1 — Restore correct SELinux labels

```bash
sudo restorecon -Rv /var/log /var/log/audit
```

### Step 2 — Start auditd via dependency chain (manual restart blocked)

```bash
sudo systemctl restart audit.target
```

### Step 3 — One clean reboot performed (recommended post-relabel)

> **NOTE**: If reboot has already happened, this step is informational.

```bash
sudo reboot
```

---

## Service Recovery

```bash
sudo systemctl start auditd
systemctl status auditd
```

```text
> Expected:
>   Active: active (running)
```

---

## Final Verification

### SELinux contexts are correct

```bash
sudo ls -lZ /var/log /var/log/audit
```

```text
> Expected:
>   /var/log        → system_u:object_r:var_log_t:s0
>   /var/log/audit  → system_u:object_r:auditd_log_t:s0
```

### Encrypted audit filesystem is mounted

```bash
mount | grep audit
```

```text
> Expected:
>   /dev/mapper/var_audit_crypt on /var/log/audit
```

### Audit logging is functional

```bash
sudo ausearch -ts recent | head
sudo ls -l /var/log/audit/audit.log
```

### Clear any residual degraded state

```bash
sudo systemctl reset-failed
systemctl is-system-running
```

```text
> Expected: running
> Acceptable: degraded (ONLY if unrelated application services remain down)
```

---

## Notes for Audit / Closure

- Failure cause: missing `/var/log/audit` after CIS `/var` hardening.
- `auditd` failing due to missing SELinux context on first boot after encryption.
- Resolution aligns with RHEL + SELinux best practices.
- **No rollback required.**
