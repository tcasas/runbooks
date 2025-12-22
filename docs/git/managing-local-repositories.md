[Runbooks Index](../index.md) / [Git](index.md)

# Managing Local Git Repositories

Use these procedures to create, update, and troubleshoot local Git repositories on Linux workstations.

## Configure a New Repository
1. Install Git and verify the version:
   ```bash
   sudo apt-get update && sudo apt-get install -y git
   git --version
   ```
2. Set your identity and preferred editor (only needed once per workstation):
   ```bash
   git config --global user.name "<full-name>"
   git config --global user.email "<email@example.com>"
   git config --global core.editor "nano"  # or vim
   ```
3. Initialize the repository in the project directory:
   ```bash
   cd /path/to/project
   git init
   git add .
   git commit -m "Initial commit"
   ```

## Clone an Existing Repository
1. Ensure you can reach the remote (HTTPS or SSH). For SSH, confirm your key is loaded:
   ```bash
   ssh-add -l
   ```
2. Clone the repository and enter it:
   ```bash
   git clone <remote-url>
   cd <repo-name>
   ```
3. Verify the default remote:
   ```bash
   git remote -v
   ```

## Keep the Working Tree Clean
- Check status frequently before switching branches:
  ```bash
  git status
  ```
- Discard local changes you do not need:
  ```bash
  git restore <file>
  git clean -fd    # remove untracked files/directories
  ```
- Stash work in progress before pulling or switching branches:
  ```bash
  git stash push -m "wip: <context>"
  git stash list
  ```

## Branching and Committing
1. Create a new branch from the latest default branch (commonly `main`):
   ```bash
   git checkout main
   git pull --ff-only
   git checkout -b <feature-branch>
   ```
2. Stage and commit logical changes with descriptive messages:
   ```bash
   git add <files>
   git commit -m "<summary of change>"
   ```
3. Inspect commit history and diffs when verifying work:
   ```bash
   git log --oneline --graph -n 10
   git diff        # working tree vs. index
   git diff --cached  # staged changes
   ```

## Synchronize with the Default Branch
1. Fetch the latest changes:
   ```bash
   git fetch origin
   ```
2. Rebase your branch on the updated default branch to keep history linear:
   ```bash
   git checkout <feature-branch>
   git rebase origin/main
   ```
3. Resolve conflicts, then continue the rebase:
   ```bash
   git status  # review conflicted files
   # edit files to resolve conflicts
   git add <resolved-files>
   git rebase --continue
   ```
4. If necessary, abort and restart the rebase:
   ```bash
   git rebase --abort
   ```

## Troubleshooting
- Remove an incorrect last commit while keeping the changes staged:
  ```bash
  git reset --soft HEAD~1
  ```
- Drop the last commit and its changes entirely (use with caution):
  ```bash
  git reset --hard HEAD~1
  ```
- View which files are ignored and why:
  ```bash
  git status --ignored
  git check-ignore -v <file>
  ```
- Verify repository health:
  ```bash
  git fsck
  git gc
  ```
