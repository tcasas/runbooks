[Runbooks Index](../index.md) / [Git](index.md)

# Roll Back a Commit and Push to GitHub

Use this runbook to revert an unwanted commit in a local Linux repository and publish the fix to GitHub.

## Prerequisites
- Know whether the bad commit was already pushed and whether collaborators may have pulled it. If others pulled it, prefer `git revert` (safe, no history rewrite) over `git reset --hard` (rewrites history).
- A clean working tree (stash or commit any work in progress):
  ```bash
  git status
  git stash push -m "wip: stash before rollback"  # only if needed
  ```
- Access to the repository's GitHub remote (typically `origin`).
- The branch you will update checked out locally.

## 1) Capture Context and Create a Safety Branch (Optional)
1. Confirm the current branch and recent history:
   ```bash
   git branch --show-current
   git log --oneline -n 5
   ```
2. Create a safety branch so you can recover quickly if needed:
   ```bash
   git branch backup/rollback-$(date +%Y%m%d)
   ```
   - This is optional but recommended when you are unsure about the revert scope.

## 2) Identify the Commit to Roll Back
1. Locate the commit hash and message:
   ```bash
   git log --oneline
   ```
2. If the commit is a merge, note the mainline parent for the revert (usually `-m 1`).
3. Double-check that the commit(s) are consecutive if you plan to revert a range. Reverting a non-sequential set of commits may require separate `git revert` commands.

## 3) Revert the Commit Locally
- For a single commit:
  ```bash
  git revert <commit-sha>
  ```
- For multiple sequential commits (inclusive range):
  ```bash
  git revert <oldest-sha>^..<newest-sha>
  ```
- For a merge commit (preserving the mainline parent):
  ```bash
  git revert -m 1 <merge-commit-sha>
  ```

If conflicts occur, resolve them in the affected files, then continue:
```bash
git status  # identify conflicted files
# edit files to resolve conflicts
git add <resolved-files>
git revert --continue
```

## 4) Verify the Rollback
1. Review the new revert commit:
   ```bash
   git show HEAD
   ```
2. Confirm the working tree is clean:
   ```bash
   git status
   ```
3. If the revert touched multiple files, run a quick smoke check (tests, lints, or the minimal verification relevant to the project) to ensure the rollback did not break anything the bad commit fixed.

## 5) Push the Fix to GitHub
1. Push the branch normally (no history rewrite required for `git revert`):
   ```bash
   git push origin <branch-name>
   ```
2. If the branch is protected, open a pull request so the revert can be merged through review.
3. Add clear context in the PR description (e.g., “Revert <sha> because it introduced <issue>”) so reviewers understand why the rollback is needed.

## Alternative: Reset and Force-Push (Use with Caution)
Only use this method on personal or feature branches where rewriting history is acceptable.

1. Reset the branch to the desired commit (moves branch pointer and working tree):
   ```bash
   git reset --hard <target-sha>
   ```
2. Push the rewritten history:
   ```bash
   git push --force-with-lease origin <branch-name>
   ```
3. Notify collaborators that the branch history changed to avoid integrating stale commits.
4. After a force-push, ask collaborators to rebase or reset their local branches to avoid confusion.
