[Runbooks Index](../index.md) / [Linux](index.md)

# TACACS+ Fails — SELinux denial fix

## Goal
Prove root cause and remediate TACACS+ authentication failures caused by SELinux denials.

## Scope
- RHEL-family hosts using TACACS+ (TCP/49) for SSH authentication.
- Use when `su` works but SSH logins fail and SELinux is suspected.

## Safety notes
- **Temporary permissive mode is for testing only.** Always re-enable enforcing.
- Collect timestamps of failed SSH attempts to correlate with AVCs.

---

## 1) Confirm SELinux status
```bash
getenforce
```

## 2) Check recent SELinux denials tied to TACACS/SSH
```bash
sudo ausearch -m AVC,USER_AVC -ts recent | grep -Ei 'sshd|tac|49' || echo "no recent AVC"
```

## 3) Temporary permissive test (validation only)
```bash
sudo setenforce 0
# Test SSH login in another terminal, then restore enforcing
sudo setenforce 1
getenforce
```
- If SSH succeeds only while permissive, SELinux policy is the likely root cause.

---

## 4) Firewall and host egress sanity
```bash
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --list-all
sudo firewall-cmd --list-ports
sudo firewall-cmd --list-services
sudo iptables -nvL OUTPUT
sudo iptables -t raw -nvL
sudo iptables -t mangle -nvL
```

## 5) Prove TCP/49 connectivity to TACACS server
```bash
timeout 3 bash -lc "cat < /dev/null > /dev/tcp/10.136.209.62/49" && echo OK || echo FAILED
nc -vz 10.136.209.62 49 || true
ping -c 3 10.136.209.62 || true
```

## 6) Capture TACACS traffic (interface-specific)
```bash
ip -br a
# Identify interface above (example: ens192)
sudo tcpdump -n -i ens192 host 10.136.209.62 and port 49
```

---

## 7) Capture SELinux denials after a failed SSH login
1. Attempt SSH login and let it fail.
2. Immediately run:
```bash
sudo ausearch -m AVC,USER_AVC -ts recent
```

## 8) Build a local SELinux policy from AVCs
```bash
sudo ausearch -m AVC,USER_AVC -ts recent | audit2allow -M tacacs_fix
```
Optional review:
```bash
cat tacacs_fix.te
```

## 9) Install the policy module
```bash
sudo semodule -i tacacs_fix.pp
```

## 10) Confirm the module is loaded
```bash
sudo semodule -l | grep tacacs_fix || echo "module missing"
```

## 11) Re-enable enforcing and retest SSH
```bash
sudo setenforce 1
getenforce
```

---

## 12) Confirm TACACS logging (if available)
```bash
sudo grep tac_connect /var/log/secure | tail -25 || true
```

---

## Success criteria
- SSH authentication succeeds with SELinux enforcing.
- No new TACACS-related AVC denials appear after the fix.

---

End of runbook.
