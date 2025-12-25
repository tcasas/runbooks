[Runbooks Index](../index.md) / [Linux](index.md)

# Rsync Usage

## Scope and goal
Use this runbook to transfer, synchronize, and validate files or directories with `rsync` over local or remote paths.

## 1) Confirm rsync availability
- Command: `rsync --version | head -n 1`
- Expected: Version output (for example, `rsync 3.x`).
- If missing: Install with the OS package manager (for example, `apt install rsync`, `yum install rsync`, `apk add rsync`).

## 2) Dry-run a sync before making changes
- Purpose: Preview changes without writing to disk.
- Command: `rsync -av --dry-run /source/path/ /dest/path/`
- Expected: A list of files that would be copied or updated.
- Tip: Add `--delete` to preview removals on the destination when mirroring.

## 3) Local directory sync
- Purpose: Mirror a local directory to another local path.
- Command: `rsync -av /source/path/ /dest/path/`
- Expected: Files copied with permissions and timestamps preserved.
- Note: Trailing slashes matter.
  - `/source/path/` syncs contents into `/dest/path/`.
  - `/source/path` creates `/dest/path/path` (the directory itself).

## 4) Remote sync over SSH
- Purpose: Transfer data to or from a remote host securely.
- Commands:
  - Local to remote: `rsync -av -e "ssh" /source/path/ user@host:/dest/path/`
  - Remote to local: `rsync -av -e "ssh" user@host:/source/path/ /dest/path/`
- Tip: Use a specific key or port with `-e "ssh -i /path/key -p 2222"`.

## 5) Bandwidth and compression controls
- Purpose: Limit impact on production links or speed up WAN transfers.
- Commands:
  - Limit bandwidth: `rsync -av --bwlimit=20m /source/path/ /dest/path/`
  - Enable compression: `rsync -av -z -e "ssh" /source/path/ user@host:/dest/path/`

## 6) Mirror mode with deletions
- Purpose: Make the destination match the source exactly.
- Command: `rsync -av --delete /source/path/ /dest/path/`
- Expected: Files not present in the source are removed from the destination.
- Caution: Always run with `--dry-run` first to verify deletions.

## 7) Preserve ownerships and ACLs (privileged)
- Purpose: Maintain metadata for system migrations.
- Command: `sudo rsync -aAXH /source/path/ /dest/path/`
- Notes:
  - `-A` preserves ACLs, `-X` preserves extended attributes, `-H` preserves hard links.
  - Requires root on both ends if syncing system directories remotely.

## 8) Verify transfer integrity
- Purpose: Confirm the destination matches the source.
- Commands:
  - Quick comparison: `rsync -avc --dry-run /source/path/ /dest/path/`
  - Checksum spot check: `sha256sum /source/path/file /dest/path/file`
- Notes:
  - `-c` uses checksums instead of timestamps/size; it is slower.

## 9) Cleanup and safety
- Use `--dry-run` for every destructive or large change.
- Avoid syncing sensitive data over untrusted networks without SSH.
- Document the exact command used for audit and rollback.
