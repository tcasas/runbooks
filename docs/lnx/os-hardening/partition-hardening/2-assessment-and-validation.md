# System Running State = DEGRADED — Assessment & Validation Runbook

**Host:** `all-vantls-m001`

---

## Purpose

Determine whether a `degraded` system state represents:

- a real, current problem
- or a harmless post-hardening artifact

Designed for **post–CIS filesystem + SELinux changes**.

---

## Meaning of `DEGRADED`

- System booted successfully
- One or more `systemd` units failed at boot
- **NOT** a fatal condition

> `DEGRADED` is expected after major `/var` filesystem surgery.

---

## Step 1 — List Failed Units

```bash
systemctl --failed
```

```text
> expected:
> - 1–3 failed units
> - Common examples: tmpfiles, journal flush, chronyd
```

Record the **FAILED** unit names.

---

## Step 2 — Inspect Each Failed Unit

Repeat for each failed unit.

```bash
systemctl status <unit>
sudo journalctl -u <unit> -b
```

Look for:
- mount failures
- crypt/LUKS errors
- SELinux denials
- services expecting old `/var` paths

---

## Step 3 — Verify Hardened Filesystems Are Mounted

```bash
mount | grep -E "var/log|var/tmp|audit"
findmnt /var/log
findmnt /var/log/audit
findmnt /var/tmp
```

```text
> expected:
> - all mounts present
> - correct mountpoints
```

If mounted correctly, encryption is **NOT** the problem.

---

## Step 4 — Verify LUKS Auto-Unlock Status

```bash
sudo cryptsetup status var_log_crypt
sudo cryptsetup status var_audit_crypt
```

```text
> expected:
>   type: LUKS2
>   active: yes
```

Inactive = crypttab issue  
Successful boot = no immediate risk

---

## Step 5 — Verify SELinux Relabel Completion

```bash
test -e /.autorelabel && echo "Relabel still pending" || echo "Relabel completed ✔"
getenforce
```

```text
> expected: Enforcing
```

First reboot after CIS hardening is always slower due to relabeling.

---

## Step 6 — Known Harmless Causes of `DEGRADED`

Common and **NON-FATAL** after filesystem changes:

- systemd-tmpfiles-clean.service
- systemd-journal-flush.service
- chronyd.service (network timing)
- user@UID.service (transient login)

These do **NOT** indicate encrypted `/var` failure.

---

## Step 7 — If a Mount Unit Failed

```bash
grep -E "var_log|var_audit|var_tmp" /etc/fstab
sudo cat /etc/crypttab
```

Verify:
- mapper names
- mountpoints
- options

If correct, failure is likely transient or unrelated.

---

## Step 8 — Clear Transient Failures and Recheck State

```bash
sudo systemctl reset-failed
systemctl is-system-running
```

```text
> expected: running
```

`reset-failed` does **NOT** hide new or recurring failures.

---

## Step 9 — Trigger Common Failure Points (No Reboot)

```bash
systemctl restart rsyslog
systemctl status rsyslog
```

```text
> expected: active (running)
```

Confirms `/var/log` is writable and healthy.

---

## Step 10 — Check for NEW Errors After Reset

```bash
journalctl -p err..alert -b
```

```text
> expected:
> - no new mount, LUKS, SELinux, or audit errors
```

---

## Step 11 — OPTIONAL but STRONG Validation (Reboot)

```bash
sudo reboot
```

After reboot:

```bash
systemctl is-system-running
systemctl --failed
```

```text
> expected:
> - running
> - no failed units (or only known non-critical ones)
```

---

## Decision Point — Do We Still Have a Problem?

If **ALL** are true:
- auditd running
- encrypted mounts present
- SELinux enforcing
- rsyslog restarts cleanly
- no new errors after reset-failed
- clean post-reboot state

```text
✔ No remaining problem
✔ reset-failed did NOT mask anything
✔ CIS hardening is stable
```

---

## If ANY Step Fails

That failure is **real and current**.

Capture:

```bash
systemctl status <unit>
journalctl -u <unit> -b
```

Investigate directly — **do NOT rely on `reset-failed`**.

---

## Next Action

Run:

```bash
systemctl --failed
```

…so the exact unit causing `degraded` can be identified and assessed.
