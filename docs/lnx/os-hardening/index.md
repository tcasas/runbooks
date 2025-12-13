# OS Hardening Runbooks

## Overview
These runbooks document the Linux OS hardening role and its supporting tasks. Use them to plan, execute, and validate updates when applying the role via the primary playbook `playbooks/lnx-os-hardening.yml`. Run the playbook end-to-end for full coverage or target specific controls with `--tags` to apply only the desired changes.

## Prerequisites
### Controller requirements
- Ansible controller with access to the target inventory and required collections/roles for the hardening tasks.
- Network reachability to managed nodes and access to any referenced Ansible Vault secrets.

### Privilege expectations
- SSH access with privilege escalation (sudo) to apply system-level changes.
- Ability to run commands that inspect services, mount points, and file permissions for verification.

## Execution patterns
### Full run
Execute the entire hardening role:

```bash
ansible-playbook -i <inventory> playbooks/lnx-os-hardening.yml
```

### Targeted tags
Focus on specific controls using tags:

```bash
# Run only SSH-related hardening
ansible-playbook -i <inventory> playbooks/lnx-os-hardening.yml --tags "ssh-hardening"

# Apply multiple controls together
ansible-playbook -i <inventory> playbooks/lnx-os-hardening.yml --tags "journald,sgid"
```

## Verification and rollback
Each runbook below lists verification guidance and rollback references. Follow the linked runbooks after execution to confirm the expected state, and use the restore guidance where provided to roll back changes safely.

## Runbook index
### General hardening guides
| Runbook | Purpose | Playbook/Tag | Verification |
| --- | --- | --- | --- |
| [Ansible Vault](ansible-vault.md) | Manage secrets required for the hardening role. | `playbooks/lnx-os-hardening.yml` (`--tags ansible-vault`) | Validate vault access and variables per runbook steps. |
| [Chronyd Options](chronyd-options.md) | Enforce Chrony configuration baselines. | `playbooks/lnx-os-hardening.yml` (`--tags chronyd`) | Check Chronyd status and config as described. |
| [Coredump Storage](coredump-storage.md) | Control coredump handling and storage limits. | `playbooks/lnx-os-hardening.yml` (`--tags coredump`) | Confirm coredump settings and retention checks in runbook. |
| [Cron Monthly Permissions](cron-monthly-permissions.md) | Ensure secure permissions on cron.monthly jobs. | `playbooks/lnx-os-hardening.yml` (`--tags cron-monthly`) | Revalidate permissions per runbook checklist. |
| [HTTPD Service](httpd-service.md) | Harden Apache service defaults. | `playbooks/lnx-os-hardening.yml` (`--tags httpd`) | Verify service state and configs outlined in runbook. |
| [Journald Compression](journald-compress.md) | Configure journald compression policy. | `playbooks/lnx-os-hardening.yml` (`--tags journald-compress`) | Confirm journal rotation/compression behavior as noted. |
| [Journald Storage](journald-storage.md) | Define journald storage location and limits. | `playbooks/lnx-os-hardening.yml` (`--tags journald-storage`) | Validate storage location and limits per runbook. |
| [Password Maximum Age](password-max-age.md) | Enforce password expiry policies. | `playbooks/lnx-os-hardening.yml` (`--tags password-age`) | Check account password aging details as described. |
| [SGID Files](sgid-files.md) | Audit and remediate SGID files. | `playbooks/lnx-os-hardening.yml` (`--tags sgid`) | Use runbook verification to confirm file ownership and permissions. |
| [SUID Files](suid-files.md) | Audit and remediate SUID files. | `playbooks/lnx-os-hardening.yml` (`--tags suid`) | Follow runbook checks to validate file lists and remediation. |
| [SUID/SGID Audit](suid-sgid-audit.md) | Perform combined SUID/SGID auditing. | `playbooks/lnx-os-hardening.yml` (`--tags suid-sgid-audit`) | Review audit output and reconcile deviations per runbook. |
| [Systemd Journal Upload](systemd-journal-upload.md) | Configure journal upload settings. | `playbooks/lnx-os-hardening.yml` (`--tags journal-upload`) | Confirm upload targets and service status as documented. |
| [Temporary /tmp Mount](tmp-mount.md) | Harden /tmp mount options. | `playbooks/lnx-os-hardening.yml` (`--tags tmp-mount`) | Verify mount flags and stability following runbook guidance. |
| [Unowned Files](unowned-files.md) | Identify and correct unowned files. | `playbooks/lnx-os-hardening.yml` (`--tags unowned-files`) | Validate file ownership corrections per runbook. |
| [World-Writable Files](world-writable-files.md) | Detect and remediate world-writable files. | `playbooks/lnx-os-hardening.yml` (`--tags world-writable`) | Confirm permissions and exceptions outlined in runbook. |

### SSH hardening guides
| Runbook | Purpose | Playbook/Tag | Verification |
| --- | --- | --- | --- |
| [SSH Authentication and Vault](ssh-hardening/ssh-auth-and-vault.md) | Secure SSH authentication methods and related secrets. | `playbooks/lnx-os-hardening.yml` (`--tags ssh-auth`) | Validate authentication paths and vault usage from runbook. |
| [sshd ClientAliveInterval](ssh-hardening/sshd-clientaliveinterval.md) | Set idle timeout controls for SSH sessions. | `playbooks/lnx-os-hardening.yml` (`--tags ssh-clientaliveinterval`) | Confirm `ClientAliveInterval` values as described. |
| [sshd IgnoreUserKnownHosts](ssh-hardening/sshd-ignoreuserknownhosts.md) | Configure host key checking behavior. | `playbooks/lnx-os-hardening.yml` (`--tags ssh-ignoreknownhosts`) | Check sshd configs and reload status per runbook. |
| [sshd KexAlgorithms](ssh-hardening/sshd-kexalgorithms.md) | Enforce approved key exchange algorithms. | `playbooks/lnx-os-hardening.yml` (`--tags ssh-kexalgorithms`) | Verify algorithm list and session negotiation results. |
| [sshd MACs](ssh-hardening/sshd-macs.md) | Define allowed MAC ciphers. | `playbooks/lnx-os-hardening.yml` (`--tags ssh-macs`) | Validate MAC list via runbook tests. |
| [sshd MaxAuthTries](ssh-hardening/sshd-maxauthtries.md) | Limit failed authentication attempts. | `playbooks/lnx-os-hardening.yml` (`--tags ssh-maxauthtries`) | Review MaxAuthTries setting and restart status as noted. |

### CIS partition hardening walkthrough
| Runbook | Purpose | Playbook/Tag | Verification |
| --- | --- | --- | --- |
| [CIS Partition Hardening Index](partition-hardening/index.md) | Plan and apply CIS-aligned partition controls. | `playbooks/lnx-os-hardening.yml` (`--tags partition-hardening`) | Validate partition layout and mount options per walkthrough. |

### Partition restore runbooks
| Runbook | Purpose | Playbook/Tag | Verification |
| --- | --- | --- | --- |
| [Restore /var/var_clients from tar backup](partition-restore/restore-from-var-backups.tar.md) | Recover partition data from tar backups. | `playbooks/lnx-os-hardening.yml` (`--tags partition-restore`) | Follow restore validation steps in runbook to confirm recovery. |
