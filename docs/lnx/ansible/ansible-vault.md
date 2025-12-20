[Runbooks Index](../../index.md) / [Linux](../index.md) / [Ansible](index.md)

# Runbook: Using Ansible Vault for secrets management

## Purpose
Provide concise, repeatable steps for creating, using, and maintaining encrypted secrets with Ansible Vault. Applies to any playbooks or inventories stored in Git where secrets must remain protected at rest.

## Preconditions
- Ansible installed locally with access to the target repository.
- A secure location to store vault password files (never committed to Git).
- Appropriate access to edit inventory or group/host variable files.

## Procedure

1. **Create a vault password file (recommended for automation)**
   ```bash
   echo "SUPER-SECRET-PASSWORD" > ~/.ansible_vault_pass
   chmod 600 ~/.ansible_vault_pass
   ```
   - File permissions must be restrictive (`600`).
   - Do **not** commit this file to Git.

2. **Create a new encrypted variables file**
   ```bash
   ansible-vault create group_vars/all/vault.yml --vault-password-file ~/.ansible_vault_pass
   ```
   - When the editor opens, enter YAML such as:
     ```yaml
     db_user: myuser
     db_password: super-secret
     api_token: abc123
     ```

3. **View or edit an encrypted file**
   - View only:
     ```bash
     ansible-vault view group_vars/all/vault.yml --vault-password-file ~/.ansible_vault_pass
     ```
   - Edit in place:
     ```bash
     ansible-vault edit group_vars/all/vault.yml --vault-password-file ~/.ansible_vault_pass
     ```

4. **Encrypt an existing plaintext file**
   ```bash
   ansible-vault encrypt group_vars/all/secret.yml --vault-password-file ~/.ansible_vault_pass
   ```
   - Expected output: `Encryption successful`.

5. **Decrypt an encrypted file (temporary access)**
   ```bash
   ansible-vault decrypt group_vars/all/secret.yml --vault-password-file ~/.ansible_vault_pass
   ```
   - Expected output: `Decryption successful`.

6. **Rotate the vault password (rekey)**
   ```bash
   ansible-vault rekey group_vars/all/secret.yml
   ```
   - Prompts for old/new passwords unless `--vault-password-file` is provided.

7. **Encrypt a single variable inline**
   ```bash
   ansible-vault encrypt_string --vault-password-file ~/.ansible_vault_pass 'super-secret-password' --name 'db_password'
   ```
   - Example output to paste into YAML:
     ```yaml
     db_password: !vault |
           $ANSIBLE_VAULT;1.1;AES256
           39393765...
     ```

8. **Use vault files in playbooks**
   - Example encrypted vars file (`group_vars/all/vault.yml`):
     ```yaml
     db_user: myuser
     db_password: super-secret
     ```
   - Example playbook:
     ```yaml
     ---
     - hosts: dbservers
       vars_files:
         - group_vars/all/vault.yml

       tasks:
         - name: Show db vars
           debug:
             msg: "Connecting as {{ db_user }} / {{ db_password }}"
     ```
   - Run with vault password file:
     ```bash
     ansible-playbook site.yml --vault-password-file ~/.ansible_vault_pass
     ```
   - Or interactively prompt:
     ```bash
     ansible-playbook site.yml --ask-vault-pass
     ```

9. **Handle multiple vault IDs (optional)**
   ```bash
   ansible-playbook site.yml \
     --vault-id dev@~/.ansible_vault_pass_dev \
     --vault-id prod@~/.ansible_vault_pass_prod
   ```

## Verification
- Run a playbook that references the vault file and confirm it executes without prompting for missing variables.
- If `--vault-password-file` is used, ensure no prompt appears; if `--ask-vault-pass` is used, ensure the prompt appears and accepts the password.

## Rollback
- To remove vault encryption from a file, run `ansible-vault decrypt <file>` with the correct password file.
- Restore from Git history if an encrypted file becomes corrupted.

## Best practices
- Never commit vault password files or share them over insecure channels.
- Enforce strict permissions (`chmod 600`) on password files.
- Store secrets in `group_vars/`, `host_vars/`, or `vars/` directories and keep plaintext secrets out of Git.
- Vault protects secrets at rest; combine with access controls and auditing for comprehensive security.
