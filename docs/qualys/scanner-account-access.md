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

---

## Validation Checklist

- Scanner account can authenticate via the intended method (password or SSH key).
- `/etc/shadow` shows either a non-expired password entry or a locked password for the Qualys account.
- The Qualys authentication record is updated to match the host credential (new password or SSH key).
- A follow-up Qualys scan reports successful authentication.

---

## Notes

- Options 1 and 2 keep the hardening policy aligned for all other users.
- Prefer key-based authentication when feasible to avoid future password aging events.

### Can the host update the Qualys authentication record?

No. The record that tells scanners which credential to use lives in the Qualys platform and must be updated there (via the UI or Qualys APIs). The Qualys Cloud Agent on the target host does not sync local password changes back to the scanner authentication record.
