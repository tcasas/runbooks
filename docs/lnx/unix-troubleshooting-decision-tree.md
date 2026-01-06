[Runbooks Index](../index.md) / [Linux](index.md)

# UNIX Troubleshooting Decision Tree

Goal: avoid guessing — follow the tree in order.

```mermaid
flowchart TD
    A[Problem observed] --> B{Failure type?}

    B -->|Network connectivity| C{Can hostname resolve?}
    C -->|No| C1[Fix DNS]
    C -->|Yes| D{Can host be reached?<br/>ICMP or alternative}
    D -->|No| D1[Routing / firewall]
    D -->|Yes| E{Can service port be reached?}
    E -->|No| E1[Host firewall / upstream firewall / SELinux port label]
    E -->|Yes| F[Go to Authentication checks]

    B -->|Authentication failing| F
    F --> G{Does TCP connect succeed?}
    G -->|No| C
    G -->|Yes| H[Check login failure causes]
    H --> H1[Wrong username?]
    H --> H2[Wrong password or SSH key?]
    H --> H3[Account disabled or expired?]
    H --> H4[SSH restrictions (AllowUsers / DenyUsers)?]
    H --> H5[SELinux blocked connection?]
    H --> H6[Needs sudo privileges (Qualys)?]

    B -->|Authorization failing| I{Can user run required commands?}
    I -->|No| I1[TACACS role / sudo policy / permissions issue]
    I -->|Yes| J[Proceed to service checks]

    B -->|Application / service failing| J
    J --> K{Is service running?}
    K -->|No| K1[Start service, check logs]
    K -->|Yes| K2[Investigate cause]
    K2 --> K3[Bad configuration]
    K2 --> K4[Wrong permissions]
    K2 --> K5[SELinux denial]
    K2 --> K6[Version mismatch]
    K2 --> K7[Broken integration]
```

## Helpful commands

### Network connectivity
- `dig HOST`
- `ping HOST`
- `nc -vz HOST PORT`
- `firewall-cmd --list-all`
- `ausearch -m AVC -ts recent`

### Authentication (SSH / TACACS / Qualys)
- `grep sshd /var/log/secure`
- `id USER`
- `chage -l USER`
- `passwd -S USER`
- Inspect `/etc/ssh/sshd_config` for `Allow*` / `Deny*`
- `ausearch -m AVC -ts recent`
- `sudo -l -U USER`

### Authorization (Roles, sudo, TACACS)
- Review sudo rights
- Validate TACACS role mapping
- Check local / centralized access policies

### Application / service behavior
- `systemctl status SERVICE`
- `journalctl -u SERVICE`
- `ausearch -m AVC -ts recent`
- `ls -l PATH`

## Rules of the road
1. Never jump ahead — follow branches in order.
2. Change one thing at a time.
3. Re-test after each fix.
4. Document what you tested and why.
