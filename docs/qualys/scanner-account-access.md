[Runbooks Index](../index.md) / [Qualys](index.md)

# Qualys Scanner SSH Authentication Troubleshooting (Hardened Linux)

Use this runbook when a Qualys network scanner suddenly loses SSH access to a hardened Linux host — especially after OS hardening, SELinux enforcement, or PAM changes.

Assumptions:
- SSSD / LDAP / AD accounts
- SELinux enforcing
- TACACS and/or custom PAM
- sudo privilege escalation for scanning

------------------------------------------------------------
Symptoms
------------------------------------------------------------

Possible indicators:

- Qualys shows: UNIX Authentication Failed
- SSH login fails immediately (no password prompt)
- Logs contain:
  pam_sss: authentication failure
  Illegal empty authtok
  Permission denied
- Scanner worked before hardening and now fails

------------------------------------------------------------
Step 0 — Confirm the scanner actually reaches SSH
------------------------------------------------------------

Command:

```bash
# Show sshd activity over the last 30 minutes
sudo journalctl -u sshd --since "30 minutes ago" --no-pager
```

If no entries appear, check network instead:

```bash
# Confirm TCP/22 traffic hits the host from the scanner IP
sudo tcpdump -n -i any port 22
```

No SSH traffic means firewall or routing — fix network before auth.

------------------------------------------------------------
Step 1 — Confirm the username Qualys is using
------------------------------------------------------------

In Qualys UI:
  Scans → Authentication → Unix / SSH Records

Note:
- Login name
- Auth type (password vs key)
- Whether sudo is expected

On host:

```bash
# Validate the account resolves locally or via SSSD/LDAP/AD
id <username>
getent passwd <username>
```

If the account does not resolve, fix SSSD / directory first.

------------------------------------------------------------
Step 2 — Verify interactive SSH works
------------------------------------------------------------

From another system:

```bash
# Force password prompt to match scanner behavior
ssh -o PreferredAuthentications=password -o PubkeyAuthentication=no <username>@<host>
```

While testing, tail logs:

```bash
# Watch sshd logs during the login attempt
sudo journalctl -fu sshd
```

```bash
# Watch SSSD logs for auth failures or backend issues
sudo journalctl -fu sssd
```

Interpretation:

- Prompts for password and accepts → basic auth works
- Prompts but rejects → wrong password stored in Qualys
- Fails before prompting → PAM / SELinux / TACACS interference

------------------------------------------------------------
Step 3 — Check SELinux denials involving sshd
------------------------------------------------------------

Command:

```bash
# Look for recent SELinux denials related to sshd
sudo ausearch -m AVC,USER_AVC -ts recent | grep sshd
```

Look for:

```
avc: denied { name_connect } comm="sshd"
```

Meaning:
SELinux blocked sshd from contacting external auth (often TACACS).

Fix with a small policy module — do not disable SELinux globally.

------------------------------------------------------------
Step 4 — Validate PAM ordering (most common cause)
------------------------------------------------------------

File:
  /etc/pam.d/system-auth

Recommended high-level order:

1) environment / delays
2) TACACS (if used)
3) local UNIX auth
4) SSSD auth
5) explicit deny

Example structure:

```
auth required    pam_env.so
auth required    pam_faildelay.so delay=2000000
auth sufficient  pam_tacplus.so ...   (if TACACS is used)
auth sufficient  pam_unix.so try_first_pass
auth sufficient  pam_sss.so forward_pass use_first_pass
auth required    pam_deny.so
```

If TACACS runs first and returns no password, SSSD logs:
  Illegal empty authtok

Fix ordering, not passwords.

------------------------------------------------------------
Step 5 — Verify sudo escalation (if Qualys uses sudo)
------------------------------------------------------------

Command:

```bash
# List sudo rules for the scanner account
sudo -l -U <username>
```

Expected line:
  (ALL) NOPASSWD: ALL

If sudo requires a password, Qualys fails because it cannot answer prompts.

------------------------------------------------------------
Step 6 — Only then consider password expiration
------------------------------------------------------------

Local /etc/shadow accounts only:

```bash
# Check local password aging details
sudo chage -l <username>
```

If expired:

```bash
# Reset the password and align aging policy to the hardened baseline
sudo passwd <username>
sudo chage -M 90 -W 7 <username>
```

Domain (SSSD) accounts are managed in AD — not affected by local shadow aging.

------------------------------------------------------------
Common root causes (ranked)
------------------------------------------------------------

1) SELinux blocked sshd outbound auth
   Symptom: AVC name_connect denials
   Fix: targeted allow policy

2) PAM ordering broke password handling
   Symptom: Illegal empty authtok
   Fix: correct module order

3) Wrong password stored in Qualys
   Symptom: manual SSH rejects password
   Fix: update authentication record

4) Sudo requires password
   Symptom: sudo prompts during scan
   Fix: NOPASSWD rule

5) Network never reached sshd
   Symptom: no sshd logs
   Fix: firewall / routing

6) Password truly expired (local account)
   Fix: reset + chage

------------------------------------------------------------
Validation checklist
------------------------------------------------------------

- Interactive SSH login succeeds
- No SELinux denials during login
- PAM does not return empty authtok
- sudo escalation works when required
- Qualys authentication record matches reality

------------------------------------------------------------
Notes
------------------------------------------------------------

Prefer:
- domain-backed scanner accounts
- key-based authentication when allowed
- minimal targeted SELinux policies
- documented PAM changes

Avoid:
- disabling SELinux
- globally weakening PAM
- undocumented sshd changes

------------------------------------------------------------
Finding which account Qualys attempted
------------------------------------------------------------

1) Open the Qualys authentication record — check Login value.
2) Review sshd logs around the scan:

```bash
# Show recent sshd entries for the last 15 minutes
sudo journalctl -u sshd --since "15 minutes ago" --no-pager
```

Logs show the username Qualys attempted.

End of runbook.
