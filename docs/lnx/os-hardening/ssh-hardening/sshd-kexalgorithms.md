[Runbooks Index](../../../index.md) / [Linux](../../index.md) / [OS Hardening](../index.md) / [SSH Hardening](index.md)

# Runbook: Configure SSH daemon key exchange (KexAlgorithms)

## Purpose
Add an explicit `KexAlgorithms` directive to `/etc/ssh/sshd_config` so sshd negotiates only modern key exchange methods and satisfies compliance scans flagging the setting as missing or weak.

**What are key exchange algorithms?**
- They establish a shared session key securely during SSH handshake. Weak algorithms (e.g., `diffie-hellman-group1-sha1`) allow downgrade or man-in-the-middle attacks.
- Setting `KexAlgorithms` restricts sshd to strong methods like curve25519 and modern Diffie-Hellman groups.

## Preconditions
- Target host: RHEL 8.x (systemd with `/usr/sbin/sshd`).
- Access: SSH plus sudo/root to edit `/etc/ssh/sshd_config` and reload sshd.
- Change window: restarting/reloading sshd can drop incompatible clients; keep a second session open.

## Approved baseline
Place the algorithms strongest-first and remove legacy SHA1 groups:
```
KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256
```
Adjust only if the business documents a different set.

## Procedure
1. **Back up the current config**
   ```bash
   sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak.$(date +%F)
   ```

2. **Remove any existing weak directives**
   - Delete or comment lines containing `diffie-hellman-group1-sha1`, `diffie-hellman-group14-sha1`, or `diffie-hellman-group-exchange-sha1`.

3. **Set the approved list**
   ```bash
   sudo sh -c "grep -q '^KexAlgorithms' /etc/ssh/sshd_config \
     && sed -i 's/^KexAlgorithms.*/KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256/' /etc/ssh/sshd_config \
     || echo "KexAlgorithms curve25519-sha256,curve25519-sha256@libssh.org,diffie-hellman-group14-sha256,diffie-hellman-group16-sha512,diffie-hellman-group18-sha512,ecdh-sha2-nistp521,ecdh-sha2-nistp384,ecdh-sha2-nistp256,diffie-hellman-group-exchange-sha256" | sudo tee -a /etc/ssh/sshd_config"
   ```
   - Ensure the directive appears **before** any `Match` blocks; sshd rejects `KexAlgorithms` inside `Match`.

4. **Validate and reload sshd**
   ```bash
   sudo sshd -t -f /etc/ssh/sshd_config
   sudo systemctl reload sshd
   ```
   - If validation fails, restore the backup and re-apply.

5. **Verify effective settings**
   ```bash
   sudo sshd -T | grep kexalgorithms
   ssh -vv <host> | grep -i kex  # from a client, confirm negotiation uses an approved method
   ```

## Ansible option (one-off play)
If you prefer automation, run against the target host/group:
```bash
ansible-playbook playbooks/lnx-os-hardening.yml \
  -i inventories/vantls/hosts \
  --limit <target_host_or_group> \
  -e 'sshd_config_path=/etc/ssh/sshd_config sshd_kexalgorithms=["curve25519-sha256","curve25519-sha256@libssh.org","diffie-hellman-group14-sha256","diffie-hellman-group16-sha512","diffie-hellman-group18-sha512","ecdh-sha2-nistp521","ecdh-sha2-nistp384","ecdh-sha2-nistp256","diffie-hellman-group-exchange-sha256"]'
```
Implement a task similar to `roles/lnx-os-hardening/tasks/sshd_macs.yml` (use `lineinfile` with `insertbefore: '^Match'`) if it is not present already.

## Rollback
```bash
sudo cp /etc/ssh/sshd_config.bak.<date> /etc/ssh/sshd_config
sudo systemctl reload sshd
```

## Notes
- Keep another SSH session active during reloads to avoid lockout.
- Document any deviations from the baseline list and schedule a follow-up scan to confirm the control now passes.
