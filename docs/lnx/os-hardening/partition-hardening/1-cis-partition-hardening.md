[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [Partition Hardening](index.md)

# CIS Post-Hardening Verification Runbook (RHEL 8 Jumpboxes)

## Purpose

Verify that encrypted `/var/log`, `/var/log/audit`, and `/var/tmp` were created, mounted, auto-unlocked at boot, and are actively serving logging and auditing.  
Also confirms SELinux relabel completed and `rsyslog` / `auditd` are healthy.

---

## Where to Run

- ✔ **ONLY** from a normally booted system  
- ✔ Run after completing the CIS Partition Hardening procedure  
- ✘ **Do NOT** run from rescue ISO or maintenance shell  

---

## 1 — Confirm System Boot State  
*(Ensure we are not in emergency mode)*

    systemctl is-system-running
    > expected: running      # perfect
    > or:       degraded     # acceptable (a service failed but OS is usable)
    > NOT OK:   maintenance / emergency / starting

### Follow-up if NOT OK

- Boot from rescue ISO → examine `/etc/fstab` and `/etc/crypttab`
- Ensure keyfile included in `initramfs` (see Step 4)
- Confirm encrypted LVs exist and can be opened manually

---

## 2 — Verify Encrypted Volumes Are Mounted Correctly

    mount | grep -E "var/log|var/tmp|audit"

    > expected:
    > /dev/mapper/var_log_crypt    /var/log
    > /dev/mapper/var_audit_crypt  /var/log/audit
    > /dev/rhel/var_tmp            /var/tmp

    findmnt /var/log
    findmnt /var/log/audit
    findmnt /var/tmp

### Follow-up if NOT OK

- Check `/etc/fstab` entries for typos
- Confirm `cryptsetup` auto-unlocked devices (see Step 3)

---

## 3 — Verify LUKS Devices Unlocked Automatically

    cryptsetup status var_log_crypt
    cryptsetup status var_audit_crypt

    > expected output:
    >   type: LUKS2
    >   active device: yes
    >   key location: keyring
    >   backing device: /dev/rhel/var_log (or var_audit)

### Follow-up if NOT OK

- Inspect `/etc/crypttab` for UUID mismatches
- Ensure `/root/luks-keyfile.bin` exists and matches `initramfs`
- Rebuild initramfs if required:
  
        dracut -f

---

## 4 — Confirm Keyfile Was Included in initramfs

    lsinitrd /boot/initramfs-$(uname -r).img | grep luks-keyfile.bin
    > expected: printed path showing luks-keyfile.bin inside initramfs

### Follow-up if NOT OK

- Fix dracut config:

        mkdir -p /etc/dracut.conf.d
        echo 'install_items+=" /root/luks-keyfile.bin "' \
          > /etc/dracut.conf.d/luks-keyfile.conf

- Rebuild:

        dracut -f

- Reboot and retest

---

## 5 — Confirm SELinux Relabel Completed After Reboot

    test -e /.autorelabel && echo "Still pending!" || echo "Relabel completed ✔"

    getenforce
    > expected: Enforcing

### Follow-up if NOT OK

- Boot may not have completed relabel
- If `.autorelabel` still present → reboot again
- Check `/var/log/audit/audit.log` for denials

---

## 6 — Verify rsyslog Is Actively Writing to Encrypted /var/log

    logger "CIS test message — $(date)"

    grep "CIS test message" /var/log/messages
    > expected: line found ✔

### Follow-up if NOT OK

- Check rsyslog status:

        systemctl status rsyslog

- Ensure `/var/log` permissions survived restore:

        ls -ld /var/log

---

## 7 — Verify auditd Writes to Encrypted /var/log/audit

    ausearch -ts today | head
    > expected: visible audit records

### Follow-up if NOT OK

- Ensure auditd running:

        systemctl status auditd

- Ensure `/var/log/audit` permissions correct:

        ls -ld /var/log/audit

---

## 8 — Confirm Disk Usage Looks Correct After Migration

    df -h | grep -E "var$|log$|audit$|tmp$"

    > expected:
    >   /var              ≈ 300G
    >   /var/log          ≈ 20G (encrypted)
    >   /var/log/audit    ≈ 10G (encrypted)
    >   /var/tmp          ≈ 20G

### Follow-up if NOT OK

- Validate LVs with `lvs`
- Confirm encrypted mounts (Step 2)

---

## 9 — Verify logrotate Still Works

    logrotate -d /etc/logrotate.conf
    > expected: no errors, shows dry-run of log rotation

### Follow-up if NOT OK

- Check permissions on `/var/log` and subdirectories
- Ensure `logrotate.d` scripts survived migration

---

## 10 — Final Health Summary  
*(Quick executive output)*

    echo "==== CIS Hardened Filesystem Status ===="
    echo "System state:        $(systemctl is-system-running)"
    echo "SELinux mode:        $(getenforce)"
    echo "var/log mounted:     $(findmnt -n -o SOURCE /var/log)"
    echo "var/log/audit:       $(findmnt -n -o SOURCE /var/log/audit)"
    echo "var/tmp mounted:     $(findmnt -n -o SOURCE /var/tmp)"
    echo "LUKS var_log:        $(cryptsetup status var_log_crypt | grep 'type')"
    echo "LUKS var_audit:      $(cryptsetup status var_audit_crypt | grep 'type')"
    echo "Audit events today:  $(ausearch -ts today 2>/dev/null | wc -l)"
    echo "=========================================="

### Follow-up if Anything Is Unexpected

- Start with **Step 2** (mount problems)
- Then **Step 3** (LUKS unlock)
- Then **Step 4** (initramfs keyfile)
- If still stuck → use **Emergency-Mode Repair Runbook**

---

*** End of CIS Post-Hardening Verification Runbook ***
