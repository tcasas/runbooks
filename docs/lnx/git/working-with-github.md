# Working with GitHub

Follow these steps to connect local repositories to GitHub, collaborate through forks, and submit pull requests.

## Authenticate to GitHub
- Create a personal access token (PAT) with `repo` scope from GitHub **Settings → Developer settings → Personal access tokens**.
- Store the PAT in a credential helper:
  ```bash
  git config --global credential.helper store
  git credential-store --file ~/.git-credentials store
  ```
- For SSH access, add your key to the agent and test connectivity:
  ```bash
  eval "$(ssh-agent -s)"
  ssh-add ~/.ssh/id_rsa
  ssh -T git@github.com
  ```

## Connect a Local Repository to GitHub
1. Confirm the repository has no remote configured or remove incorrect entries:
   ```bash
   git remote -v
   git remote remove origin  # only if the remote is wrong
   ```
2. Add the GitHub remote and push the default branch:
   ```bash
   git remote add origin git@github.com:<org>/<repo>.git
   git push -u origin main
   ```
3. Verify branch tracking and upstream configuration:
   ```bash
   git branch -vv
   ```

## Fork and Work from Your Copy
1. Fork the upstream repository in GitHub.
2. Clone your fork locally:
   ```bash
   git clone git@github.com:<username>/<repo>.git
   cd <repo>
   ```
3. Add the upstream remote to stay current:
   ```bash
   git remote add upstream git@github.com:<org>/<repo>.git
   git remote -v
   ```
4. Create a feature branch from the upstream default branch and rebase regularly:
   ```bash
   git fetch upstream
   git checkout -b <feature-branch> upstream/main
   git rebase upstream/main
   ```

## Submit a Pull Request
1. Push your branch to your fork:
   ```bash
   git push -u origin <feature-branch>
   ```
2. Open a pull request in GitHub targeting `upstream/main` or the repository default branch. Include:
   - A clear title and summary of changes.
   - Testing performed and any known limitations.
   - Links to related issues or tickets.
3. Respond to review feedback by amending commits and force-pushing the branch:
   ```bash
   git commit --amend
   git push --force-with-lease
   ```

## Keep Forks in Sync
1. Fetch upstream changes and rebase your work:
   ```bash
   git fetch upstream
   git checkout main
   git rebase upstream/main
   ```
2. Update your forked default branch on GitHub:
   ```bash
   git push --force-with-lease origin main
   ```
3. Rebase any feature branches on top of the refreshed `main`:
   ```bash
   git checkout <feature-branch>
   git rebase main
   ```

## Cleanup After Merging
- Delete merged branches locally and on GitHub:
  ```bash
  git branch -d <feature-branch>
  git push origin --delete <feature-branch>
  ```
- Prune stale remote-tracking branches:
  ```bash
  git fetch --prune
  ```
- Archive release artifacts or tags as required by project policy.
