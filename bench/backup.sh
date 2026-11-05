#!/bin/sh
# backup.sh: the hourly snapshot of a bench repository, on a ref of its own (Michael, 5 Nov 2026,
# lesson L38: "the hourly backup never commits on the working branch again. It writes its
# snapshot to a backup ref of its own ..., pushed to the private remote, and the working branch
# carries only the agent's commits"). From the user's crontab, no root, behind runs/quiet.sh (no
# git work while a plan records, L6):
#
#   17 * * * *  <bench>/runs/quiet.sh sh <method>/bench/backup.sh <bench folder> >> <top>/backup.log 2>&1
#   19 * * * *  <bench>/runs/quiet.sh sh <method>/bench/backup.sh <top> <Claude's memory folder> >> <top>/backup.log 2>&1
#
# Each snapshot is one commit on refs/backup/hourly:
#   - its tree: the working tree as `git add -A` would stage it (HEAD's files, the tracked
#     changes, the untracked files the .gitignore lets in), and each folder named after the
#     repository (Claude's memory) as mirror/<its name>;
#   - its parents: the previous snapshot first, then the working branch's commit (HEAD), so
#     `git log --first-parent refs/backup/hourly` walks the snapshots and
#     `git diff HEAD refs/backup/hourly` is what the last one holds beyond the agent's commits.
# It is built in an index of its own (GIT_INDEX_FILE) and written with write-tree, commit-tree
# and update-ref: the working branch, the repository's own index and the working tree are never
# touched (the mirrored folders are no longer copied into the working tree either). The review
# flag of 3 Nov 2026 is superseded by the same decision: runs/review.flag is not read.
#
# The check: commit-tree runs no hook, so the bench's check (hooks/pre-commit) is run here on the
# snapshot's index before the ref is written. It reads every file the snapshot holds beyond HEAD
# (HEAD's own were checked when they were committed), with rename detection off, so a moved file
# is read as a new one. A refused snapshot writes no ref, leaves nothing staged, and says why.
#
# The push, only for a repository with a remote (the bench folder; the top folder has none and
# never gets one, bench/README.md): the snapshot to the same ref there, never forced. The working
# branch is the agent's to push (the snapshot carries HEAD as a parent, so the agent's commits reach
# the private repository with it either way).
#
# Nothing new since the last snapshot (the same tree, HEAD already inside it): no snapshot and no
# output, as before; a snapshot an earlier push left behind is pushed again then, and only a refusal
# is said.
#
# lessons_read = "terms: backup, commit, hook, push, flag, snapshot; lessons: L38, L2, L9, L20, L40, L33, L37, L10, L22, L32, L24; 5 Nov 2026"

set -eu
here=$(cd "$(dirname "$0")" && pwd)
start=$(pwd)
repo=$1
shift

ref=refs/backup/hourly      # the snapshot's ref in the repository
remote_ref=$ref             # and on the remote; if the remote refuses a ref outside refs/heads,
                            # refs/heads/backup/hourly (a branch of its own) instead
now=$(date -u +%Y-%m-%dT%H:%MZ)

# A caller's git settings never steer the snapshot (cron sets none; a shell might).
unset GIT_DIR GIT_WORK_TREE GIT_INDEX_FILE GIT_OBJECT_DIRECTORY
cd "$repo"
cd "$(git rev-parse --show-toplevel)"

work=$(mktemp -d "${TMPDIR:-/tmp}/backup.XXXXXX")
trap 'rm -rf "$work"' EXIT
trap 'exit 1' HUP INT TERM
index=$work/index

head=$(git rev-parse -q --verify 'HEAD^{commit}' || true)
own=$(git rev-parse --git-path index)

# The snapshot's index starts as a copy of the repository's own: its stat data spare hashing every
# file again. Whatever the copy has staged or not, `git add -A` then takes the working tree for
# every path. The copy keeps the index's own time (cp -p): git reads again any file changed in the
# same second as the index was written, judged against that time, and a copy made newer took a
# same-size change in that second as unchanged (the snapshot kept HEAD's file; the method's
# test_backup_leaves_the_working_branch_alone, 5 Nov 2026). No index yet: HEAD's tree, or nothing
# (a repository with no commit).
if [ -f "$own" ]; then
    cp -p "$own" "$index"
elif [ -n "$head" ]; then
    GIT_INDEX_FILE=$index git read-tree "$head"
fi
export GIT_INDEX_FILE="$index"
git add -A

# Folders that live elsewhere (Claude's memory) go into the snapshot as mirror/<name>, straight
# from where they are: each file hashed into the repository and named in the snapshot's index.
# A file gone from the folder is gone from the snapshot. Written to a list first, not through a
# pipe, so a failed hash stops the script (sh has no pipefail).
for folder in "$@"; do
    case $folder in /*) ;; *) folder=$start/$folder ;; esac
    if [ ! -d "$folder" ]; then
        echo "$now $repo not backed up: $folder is not a folder" >&2
        exit 1
    fi
    name=mirror/$(basename "$folder")
    git rm -r -q -f --cached --ignore-unmatch -- "$name"
    (cd "$folder" && find . -type f) > "$work/files"
    : > "$work/info"
    while IFS= read -r file; do
        file=${file#./}
        blob=$(git hash-object -w --no-filters -- "$folder/$file")
        mode=100644
        if [ -x "$folder/$file" ]; then mode=100755; fi
        printf '%s blob %s\t%s\n' "$mode" "$blob" "$name/$file" >> "$work/info"
    done < "$work/files"
    git update-index --index-info < "$work/info"
done

tree=$(git write-tree)
prev=$(git rev-parse -q --verify "$ref^{commit}" || true)
if [ -n "$prev" ] && [ "$tree" = "$(git rev-parse "$prev^{tree}")" ]; then
    if [ -z "$head" ] || git merge-base --is-ancestor "$head" "$prev"; then
        # nothing new: only a snapshot an earlier push left behind goes again (quiet when it is there)
        if git remote get-url origin >/dev/null 2>&1 && ! git push -q origin "$ref:$remote_ref"; then
            echo "$now $repo: snapshot $(git rev-parse --short "$prev") still not pushed to origin's $remote_ref" >&2
            exit 1
        fi
        exit 0
    fi
fi

# The bench's check on the snapshot's index (GIT_INDEX_FILE is exported, so the hook's own git
# calls read it): every file beyond HEAD. diff.renames off for it: the hook keeps the A and M
# entries of `git diff --cached`, and a rename (R) would pass unread.
if ! GIT_CONFIG_COUNT=1 GIT_CONFIG_KEY_0=diff.renames GIT_CONFIG_VALUE_0=false \
        python3 "$here/hooks/pre-commit"; then
    echo "$now $repo not backed up: the bench's check refused the snapshot (above); no ref written" >&2
    exit 1
fi

parents=
if [ -n "$prev" ]; then parents="-p $prev"; fi
if [ -n "$head" ]; then parents="$parents -p $head"; fi
branch=$(git symbolic-ref -q --short HEAD || echo "a detached HEAD")
if [ -n "$head" ]; then
    over="$branch at $(git rev-parse --short "$head")"
else
    over="$branch, no commit yet"
fi
beyond=$(git diff --cached --no-renames --name-only | wc -l | tr -d ' ')
snap=$(git commit-tree "$tree" $parents \
    -m "Backup: $now" \
    -m "The working tree over $over, $beyond paths beyond it; the method's bench/backup.sh, on $ref (the working branch is not touched).")
# "$prev" empty: the ref must not exist yet; otherwise it must still be $prev (two backups of one
# repository at once cannot lose a snapshot)
git update-ref -m "backup: $now" "$ref" "$snap" "$prev"

status=0
if git remote get-url origin >/dev/null 2>&1 && ! git push -q origin "$ref:$remote_ref"; then
    echo "$now $repo: snapshot $(git rev-parse --short "$snap") kept here, not pushed to origin's $remote_ref" >&2
    status=1
fi
echo "$now $repo backed up $(git rev-parse --short "$snap") on $ref ($beyond paths beyond $over)"
exit $status
