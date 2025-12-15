# Qualys Scanner Account Access Troubleshooting

Use this runbook when a Qualys network scanner account suddenly loses SSH access to a hardened Linux host.

---

## Symptoms

- Qualys scan results show authentication failed for the scanner account.
- Manual SSH login with the scanner credentials prompts for a password reset or rejects the password entirely.

---

## Likely Cause

An OS-hardening role enforces maximum password age on every account with an active password hash. The default policy sets:

- Maximum password age: **90 days**
- Warning period: **7 days**

The hardening task loops over `/etc/shadow` entries and applies these values to every user that has an active hash. The Qualys service account password likely expired after the hardening run.

### Where is the maximum password age enforced?

- `/etc/login.defs` is templated to set `PASS_MAX_DAYS` (defaults to 90) as the global maximum.
- The hardening role also runs `password_expire_max` against each `/etc/shadow` entry that has an active hash to ensure every user matches the policy.
- See the [maximum password age runbook](../lnx/os-hardening/password-max-age.md) for the end-to-end control and verification steps.

---

## Recovery Options

Choose one of the options below to restore scanner access while keeping the hardening policy intact.

### Option 1 — Reset or Unexpire the Password (Recommended)

1. Reset the Qualys scanner account password on the host:

       sudo passwd <qualys_user>

2. Align the account with the enforced aging settings (adjust values if your policy differs):

       sudo chage -M 90 -W 7 <qualys_user>

3. Update the Qualys authentication record with the new password so the scanner uses the fresh credentials on the next run (for example, in VMDR: **Scans → Authentication → New/Edit Record → Password**).
4. Re-run the Qualys scan to confirm authentication succeeds.

### Option 2 — Use Key-Only Authentication (Avoids Password Aging)

1. Lock the password in `/etc/shadow` so the hardening task skips the account (the `!` prefix marks a locked password):

       sudo usermod -p '!*' <qualys_user>

2. Configure SSH key-based authentication for the scanner account.
3. Re-run the scan to verify key-based login works.

### Option 3 — Exempt the Account from Password Aging (Use Sparingly)

1. Customize the OS-hardening role locally so it drops the Qualys account before enforcing maximum age. For example:

       password_users: "{{ password_users | difference(['qualys']) }}"

2. Document the exception so it can be revisited after scanner access is restored.

### If the scanner uses a domain account (not in `/etc/shadow`)

Some hardened baselines also tighten SSH and PAM controls for centrally managed accounts. If your scanner authenticates with a domain user (for example, through SSSD/LDAP) and is now blocked:

1. Confirm the account and group mappings resolve correctly:

       id <domain_user>

2. Review recent hardening changes to SSH restrictions and ensure the domain account (or its group) is permitted:
   - `AllowUsers` / `AllowGroups` in `/etc/ssh/sshd_config`
   - `sssd.conf` access controls (for example, `simple_allow_groups` / `simple_allow_users`)
3. Check PAM access rules that may have started denying the scanner:
   - `/etc/security/access.conf` (often driven by `pam_access`)
   - `/etc/pam.d/sshd` for new modules such as `pam_access` or `pam_faillock`
4. Add the scanner account or a dedicated group to the approved lists, then restart SSH if `sshd_config` was updated.
5. Re-run the scan to confirm authentication now succeeds.

---

## Validation Checklist

- Scanner account can authenticate via the intended method (password or SSH key).
- `/etc/shadow` shows either a non-expired password entry or a locked password for the Qualys account.
- The Qualys authentication record is updated to match the host credential (new password or SSH key).
- A follow-up Qualys scan reports successful authentication.

### How to confirm which account the scanner is using

1. In the Qualys UI, open the authentication record tied to the target host (for example, in VMDR: **Scans → Authentication → Unix Records**). The **Login** field shows the username the scanner will attempt.
2. If you manage records by API, call the Authentication Records endpoint to list the relevant entry and verify its configured login.
3. On the host, review recent SSH logs (for example, `/var/log/auth.log` or `/var/log/secure`) for attempts from the scanner IP. The log entries include the username the scanner tried when authentication failed.

---

## Notes

- Options 1 and 2 keep the hardening policy aligned for all other users.
- Prefer key-based authentication when feasible to avoid future password aging events.

### Can the host update the Qualys authentication record?

No. The record that tells scanners which credential to use lives in the Qualys platform and must be updated there (via the UI or Qualys APIs). The Qualys Cloud Agent on the target host does not sync local password changes back to the scanner authentication record.

---

## Useful Links

- [Cloud Agent Getting Started Guide](https://docs.qualys.com/en/ca/getting-started-guide/configuration/change_ca_configuration.htm)
- [Qualys Cloud Agent Documentation (OpenText Confluence)](https://confluence.opentext.com/display/GITVM/Cloud+Agent)
- [Self-Service Portal](https://wlsoneprd01.opentext.net/Qualys-Agent-Status-Query)
- [Security Self-Service Scanner](https://intranet.opentext.com/intranet/llisapi.dll/displayform/125249359/125243474/?viewid=125250622&readonly=true&sedit=false&objId=125245395&objAction=EditForm&nexturl=https%3A%2F%2Fintranet%2Eopentext%2Ecom%2Fintranet%2Fllisapi%2Edll)
- [Cloud Agent Downloads](https://intranet.opentext.com/intranet/llisapi.dll?func=ll&objId=178461660&objAction=browse&viewType=1)
- [Cloud Agent Platform Availability Matrix (PAM)](https://success.qualys.com/customersupport/s/cloud-agent-pam)
