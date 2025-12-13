# Restore /var/var_clients from /root/var-backup.tar

## Purpose

Restore the directory `/var/var_clients/` from the backup archive
`/root/var-backup.tar` in a safe, controlled manner.

This runbook assumes:
- Linux system
- root access
- tar-based backup
- SELinux may be enforcing

---

## Step 1 — Inspect the Backup (REQUIRED)

Do NOT extract blindly. First confirm the path exists in the archive.

    tar -tvf /root/var-backup.tar | less

Look for one of the following paths:

    var/var_clients/
    ./var/var_clients/
    var_clients/

Optional targeted check:

    tar -tvf /root/var-backup.tar | grep var_clients

If the path does NOT exist:
- stop
- restore is not possible from this archive

---

## Step 2 — Check Current State of /var/var_clients

    ls -ld /var/var_clients

If the directory exists and contains data:
- decide whether overwrite is intended
- consider restoring to a temporary location first

If the directory does not exist:
- safe to proceed

---

## Step 3 — Restore (Standard Case)

### Use this if the archive contains `var/var_clients/`

    cd /
    tar -xvpf /root/var-backup.tar var/var_clients

This restores:

    /var/var_clients

Flags used:
- x  extract
- v  verbose
- p  preserve permissions
- f  file

---

## Step 4 — Alternate Restore Paths

### Case A — Archive Contains `var_clients/` (No /var Prefix)

    cd /var
    tar -xvpf /root/var-backup.tar var_clients

Resulting path:

    /var/var_clients

---

### Case B — Restore to Temporary Location (Safest)

Use this if you want to inspect contents before overwriting:

    mkdir -p /root/restore-test
    cd /root/restore-test
    tar -xvpf /root/var-backup.tar

Inspect:

    ls -l var/var_clients

Move into place when ready:

    mv var/var_clients /var/

---

## Step 5 — Verify Restore

    ls -l /var/var_clients

Optional detailed check:

    stat /var/var_clients

Confirm:
- expected files present
- ownership and permissions look correct

---

## Step 6 — Restore SELinux Contexts (IMPORTANT)

If SELinux is enforcing (common on hardened systems):

    restorecon -Rv /var/var_clients

Failure to do this may cause:
- service startup failures
- access denials
- audit findings

---

## Step 7 — Post-Restore Validation (Optional)

If applications depend on this directory:
- restart affected services
- validate application functionality
- monitor logs for permission or AVC errors

---

## What NOT To Do

- Do NOT extract the entire archive unless explicitly intended
- Do NOT restore from an arbitrary directory (always cd first)
- Do NOT skip SELinux relabeling
- Do NOT overwrite /var wholesale

---

## Outcome

If all steps complete successfully:
- /var/var_clients is restored
- permissions are preserved
- SELinux contexts are correct
- system is ready for validation or audit
