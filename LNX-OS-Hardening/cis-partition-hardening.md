# CIS Partition Hardening and Encrypted /var Implementation (RHEL 8 Jumpboxes)

**Applies to all jumpboxes after validating on all-vantls-m001.** Includes full training-wheels comments for safety and clarity, plus the critical dracut override so the keyfile is bundled into initramfs.

## Execution Checklist — Complete Before Step 0
- [ ] VM snapshot taken (disk only, no memory)
- [ ] Rescue ISO available (RHEL 8.6 DVD)
- [ ] `sudo` access confirmed
- [ ] `/root` has ≥ 100GB free for `var-backup.tar`
- [ ] `/var` usage < 100GB (safe shrink target: 300GB)
- [ ] Operators aware SSH will drop in rescue mode
- [ ] Console access ready (vSphere/iDRAC)
- [ ] Change window approved

> Proceed only when all boxes are checked.

## 0 — Pre-Flight Verification (Ensures Environment Is Safe)
Run the following commands and validate the expectations:

```
hostname                    # Ensure you're on the correct jumpbox
getenforce                  # Should be "Permissive" before major FS changes (sudo setenforce 0)
df -h /var                  # MUST be <100GB used to shrink safely
lsblk -f                    # Verify device → VG → LV layout
pvs                         # Verify PVs and free space
vgs                         # Confirm VG rhel exists
lvs                         # Confirm LVs: rhel/root rhel/var rhel/home
```

> Take the snapshot now (rollback point before destructive steps).

## 1 — Backup /var (Safety Net)
```
systemctl stop rsyslog      # Prevent log writes during backup
cd /
tar -cpvf /root/var-backup.tar /var
```

Expected: `var-backup.tar` grows to ~20–70GB depending on workload.

## 2 — Boot into Rescue Mode Using the RHEL ISO
Boot from ISO → Troubleshooting → Rescue → "3) Skip to shell". This provides a minimal environment with no logs being written, no auditd or SSSD interference, and full access to LVM.

## 3 — Activate LVM Inside Rescue
```
lvm vgscan
lvm vgchange -ay
lvs
```

Expected: All `rhel/*` LVs show `wi-a----` meaning active and writable.

## 4 — Mount the Real Root Filesystem at /mnt/sysroot
```
mkdir -p /mnt/sysroot
mount /dev/rhel/root /mnt/sysroot

# Bind the virtual filesystems so chroot behaves like a live system:
mount --bind /dev  /mnt/sysroot/dev
mount --bind /proc /mnt/sysroot/proc
mount --bind /sys  /mnt/sysroot/sys
mount --bind /run  /mnt/sysroot/run

mount | grep sysroot
```

Expected: Five mountpoints appear under `/mnt/sysroot`. This allows `chroot` to run `dracut` and `systemctl` correctly later.

## 5 — Create Mountpoints for the Encrypted Log Volumes
```
mkdir -p /mnt/sysroot/var/log
mkdir -p /mnt/sysroot/var/log/audit
mkdir -p /mnt/sysroot/var/tmp
```

## 6 — Create the LUKS Keyfile (Critical for Boot Success)
```
dd if=/dev/urandom of=/mnt/sysroot/root/luks-keyfile.bin bs=4096 count=1
chmod 600 /mnt/sysroot/root/luks-keyfile.bin
ls -l /mnt/sysroot/root/luks-keyfile.bin
```

Expected: File is 4096 bytes, mode 600, owned by root. This file will be baked into initramfs in Step 14.

## 7 — luksFormat Both New Log LVs (Destructive by Design)
```
cryptsetup luksFormat /dev/rhel/var_log   /mnt/sysroot/root/luks-keyfile.bin --batch-mode
cryptsetup luksFormat /dev/rhel/var_audit /mnt/sysroot/root/luks-keyfile.bin --batch-mode
```

Expected: `Command successful.` At this point the LVs contain encrypted containers, not filesystems.

## 8 — Open the Encrypted Volumes
```
cryptsetup luksOpen /dev/rhel/var_log   var_log_crypt   --key-file /mnt/sysroot/root/luks-keyfile.bin
cryptsetup luksOpen /dev/rhel/var_audit var_audit_crypt --key-file /mnt/sysroot/root/luks-keyfile.bin

ls -al /dev/mapper | grep crypt
```

Expected: `var_log_crypt` and `var_audit_crypt` exist. These are what you format and mount — not the raw LV devices.

## 9 — Create XFS Filesystems Inside the Encrypted Volumes
```
mkfs.xfs -f /dev/mapper/var_log_crypt
mkfs.xfs -f /dev/mapper/var_audit_crypt
```

## 10 — Mount the New Encrypted Filesystems
```
mount /dev/mapper/var_log_crypt   /mnt/sysroot/var/log
mount /dev/mapper/var_audit_crypt /mnt/sysroot/var/log/audit
mount /dev/rhel/var_tmp           /mnt/sysroot/var/tmp

mount | grep sysroot
```

Expected: Three new mounts under `/mnt/sysroot/var/*`.

## 11 — Restore /var (Excluding Large Log and tmp Directories)
```
cd /mnt/sysroot
tar -xpvf /mnt/sysroot/root/var-backup.tar \
    --exclude='var/log' \
    --exclude='var/log/*' \
    --exclude='var/log/audit' \
    --exclude='var/log/audit/*' \
    --exclude='var/tmp' \
    -C /mnt/sysroot
```

You now have a complete `/var` except for logs and tmp, which now live on encrypted filesystems.

## 12 — Update /etc/crypttab (Ensures Auto-Decryption at Boot)
```
sed -i '/var_log_crypt/d'   /mnt/sysroot/etc/crypttab
sed -i '/var_audit_crypt/d' /mnt/sysroot/etc/crypttab

cat <<'EOC' >> /mnt/sysroot/etc/crypttab
var_log_crypt   UUID=$(blkid -s UUID -o value /dev/rhel/var_log)     /root/luks-keyfile.bin  luks
var_audit_crypt UUID=$(blkid -s UUID -o value /dev/rhel/var_audit)   /root/luks-keyfile.bin  luks
EOC

cat /mnt/sysroot/etc/crypttab
```

Expected: Exactly two correct lines showing real UUIDs.

## 13 — Update /etc/fstab (Remove Old Entries, Add Correct Ones)
```
sed -i '/rhel\/var_log/d'   /mnt/sysroot/etc/fstab
sed -i '/rhel\/var_audit/d' /mnt/sysroot/etc/fstab
sed -i '/rhel\/var_tmp/d'   /mnt/sysroot/etc/fstab

cat <<'EOF_FSTAB' >> /mnt/sysroot/etc/fstab
/dev/mapper/var_log_crypt     /var/log        xfs  rw,nodev,noexec,nosuid  0 2
/dev/mapper/var_audit_crypt   /var/log/audit  xfs  rw,nodev,noexec,nosuid  0 2
/dev/rhel/var_tmp             /var/tmp        xfs  rw,nodev,noexec,nosuid  0 2
EOF_FSTAB

cat /mnt/sysroot/etc/fstab
```

Critical that only encrypted log volumes appear.

## 14 — Ensure dracut Includes the Keyfile in initramfs (Critical)
```
mkdir -p /mnt/sysroot/etc/dracut.conf.d

cat <<'EOF_DRACUT' > /mnt/sysroot/etc/dracut.conf.d/luks-keyfile.conf
install_items+=" /root/luks-keyfile.bin "
EOF_DRACUT

# Rebuild initramfs inside chroot:
chroot /mnt/sysroot dracut -f

# Verify keyfile was bundled:
chroot /mnt/sysroot lsinitrd | grep luks-keyfile.bin
```

Expected: A line showing `luks-keyfile.bin` inside initramfs. If missing, the system will not boot normally.

## 15 — Mark for SELinux Relabel
```
touch /mnt/sysroot/.autorelabel
```

## 16 — Cleanly Unmount and Reboot
```
umount /mnt/sysroot/run
umount /mnt/sysroot/dev
umount /mnt/sysroot/proc
umount /mnt/sysroot/sys
umount /mnt/sysroot/var/log/audit
umount /mnt/sysroot/var/log
umount /mnt/sysroot/var/tmp
umount /mnt/sysroot

reboot
```

Expected: System boots normally (no emergency mode). `/var/log`, `/var/log/audit`, and `/var/tmp` now reside on encrypted, CIS-compliant filesystems.
