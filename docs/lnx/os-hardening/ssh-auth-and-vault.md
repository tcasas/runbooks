# Runbook: SSH authentication and Vault usage in Ansible

## Purpose
Clarify how Ansible CLI flags interact with SSH authentication variables and Vault, and provide safe, repeatable steps to avoid `--ask-pass` prompts while keeping SSH credentials protected.

## Preconditions
- Ansible installed locally and able to reach target hosts over SSH.
- Access to edit inventory and group/host variable files.
- A secure vault password file outside Git (for example `~/.ansible_vault_pass`).

## Procedure

1. **Understand what each CLI flag does**
   - `-u <user>` overrides `ansible_user` and defaults; it sets the SSH username.
   - `--ask-pass` prompts for the SSH password defined by `ansible_password` / `ansible_ssh_pass`.
   - `--vault-password-file` (or `--ask-vault-pass`) decrypts Vault content; it is unrelated to SSH authentication.

2. **Know the correct SSH variables**
   - Use `ansible_user` for the SSH user.
   - Use `ansible_password` (alias: `ansible_ssh_pass`) for the SSH password.
   - Do **not** use `ansible_default_password`; it is not an Ansible variable.

3. **Temporary approach: store SSH vars directly in inventory (not recommended for Git)**
   - Example inventory entry:
     ```ini
     [vantls_jumpboxes]
     all-vantls-m001 ansible_host=all-vantls-m001 ansible_user=root ansible_password=YOUR_SSH_PASSWORD
     ```
   - Run with only the Vault flag if other encrypted vars are needed:
     ```bash
     ansible vantls_jumpboxes \
       -i inventories/vantls/hosts \
       -m ping \
       --vault-password-file ~/.ansible_vault_pass
     ```

4. **Preferred approach: move SSH credentials into Vaulted vars**
   - Create an encrypted group vars file:
     ```bash
     ansible-vault create inventories/vantls/group_vars/all/vault.yml \
       --vault-password-file ~/.ansible_vault_pass
     ```
   - Edit the encrypted file later with the same vault password file:
     ```bash
     ansible-vault edit inventories/vantls/group_vars/all/vault.yml \
       --vault-password-file ~/.ansible_vault_pass
     ```
   - Inside `vault.yml` (encrypted):
     ```yaml
     ansible_user: root
     ansible_password: YOUR_SSH_PASSWORD
     ```
   - Run commands without `--ask-pass`, unlocking Vault once:
     ```bash
     ansible vantls_jumpboxes \
       -i inventories/vantls/hosts \
       -m ping \
       --vault-password-file ~/.ansible_vault_pass

     ansible-playbook playbooks/lnx-os-hardening.yml \
       -i inventories/vantls/hosts \
       --limit all-vantls-m001 \
       --vault-password-file ~/.ansible_vault_pass
     ```

5. **Remember precedence rules**
   - SSH user: CLI `-u <user>` overrides `ansible_user` and the local `$USER`.
   - SSH password: `--ask-pass` overrides `ansible_password` / `ansible_ssh_pass`.
   - Vault: controlled only by `--vault-password-file` or `--ask-vault-pass` (separate from SSH).

## Verification
- Run `ansible <group> -m ping` with `--vault-password-file`; confirm no SSH password prompt appears and hosts respond.
- If `--ask-pass` is specified, confirm the prompt appears and accepts the SSH password when provided.

## Rollback
- If SSH credentials were placed in inventory, remove them and rely on vaulted variables.
- If Vault files become corrupted, restore from Git history and re-run `ansible-vault create/edit` as needed.

## Best practices
- Keep SSH credentials in Vault-protected `group_vars` or `host_vars` files instead of plaintext inventories.
- Restrict permissions on the vault password file (`chmod 600`) and never commit it to Git.
- Use `--vault-password-file` for non-interactive runs; reserve `--ask-pass` only for ad-hoc troubleshooting.
