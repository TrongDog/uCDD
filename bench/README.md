# The bench's backups

On 22 Oct 2026 the bench machine failed and its bench folder was lost with
it: none of it was in git. The bench is now kept in three places, by what
each part holds:

| What | Where | Why there |
|---|---|---|
| The bench folder: the runners and their wiring, the test programs' sources, the 86Box machine configurations (text), the kit scripts | its own git repository on the private `TrongDog/ucdd-bench`: the agent's commits, pushed by the agent, and each hour a snapshot of the working tree on `refs/backup/hourly` | the costliest part to rebuild, and it holds nothing about the owner; off the machine, so it survives losing the machine and the disk together |
| The notes (CONTEXT, HANDOFF, STATE, LESSONS and lessons.py), Claude's settings (`.claude/`), Claude's memory (mirrored in), the ledger, the bench's method.local.toml | a git repository at the top folder with **no remote**: the agent's commits, and each hour a snapshot of its working tree on its own `refs/backup/hourly`, on this machine only | they hold local paths, the old machine's account name and details about the owner, so they do not leave the machine, private repository or not. An hourly push would also send whatever an agent wrote, unread |
| The games, disc images, recordings, ROMs and machine images | the backup disk only | game content or licensed software, never in any repository |

The nightly snapshot to the backup disk copies both repositories with their
`.git` folders, so the disk holds their history and their snapshot refs too.
The local history is worth having on its own: `git log -p` on LESSONS.md
shows each commit that changed it, and `git log -p refs/backup/hourly --
<path>` each hour's state of it.

## The hourly snapshot

`backup.sh` never commits on the working branch (the owner, 5 Nov 2026): the
working branch carries only the agent's commits. Each hour it writes one
commit to `refs/backup/hourly`: the working tree as `git add -A` would stage
it, and the folders named after the repository (Claude's memory) as
`mirror/<name>`, built in an index of its own, so the branch, the index and
the working tree are never touched. Its parents are the previous snapshot,
then HEAD: `git log --first-parent refs/backup/hourly` walks the snapshots,
and `git diff HEAD refs/backup/hourly` shows what the last one holds beyond
the commits. Nothing new since the last one (same tree, HEAD inside it): no
snapshot. A repository with a remote (the bench) pushes the ref to the same
name there, never forced; a snapshot whose push was refused goes again the
next hour. The agent pushes its own branch. A clone does not fetch the ref:
`git fetch origin refs/backup/hourly:refs/backup/hourly`. The review flag of
3 Nov 2026 is retired with this: nothing reads `runs/review.flag`.

**What this does not cover:** losing the machine and the disk together
(theft, fire, a surge through both). The bench folder then comes back from
GitHub; the notes do not. If that matters, add an off-site copy of the top
folder that is encrypted before it leaves the machine (restic or borg to
remote storage, or a second disk kept elsewhere), not GitHub.

## The check

The pre-commit check (`bench/hooks/pre-commit`, settings in `bench.toml`)
refuses game, program, disc, recording and image files and anything over
20 MB, an absolute home path in a repository with a remote (2 Nov 2026), and
any commit while a plan records (4 Nov 2026). `backup.sh` runs it on every
snapshot before the ref is written (git commit-tree runs no hook), on the
files the snapshot holds beyond HEAD, a moved file read as a new one, so the
hourly path does not depend on a hook being installed. `install.sh --bench`
links it into a repository's `.git/hooks` for commits made by hand.

Neither ever moves `core.hooksPath`: the guard refuses that, and must keep
refusing it, since a moved hooks path is how a uCDD commit would skip its
hook.

An exception goes in `.bench-allow` at the top of that repository, one shell
glob a line, with a comment saying why. The DOS tools whose sources were lost
are the case it is for:

    <folder>/MEMFIND.COM   # our own probe; its source was lost, the binary is all there is

## Setting it up, once

1. The bench folder is already a repository with `ucdd-bench` as `origin`.
   Give it the check:

       sh <method>/install.sh --bench <bench folder>

2. The top folder, the one holding the bench folder and the notes:

       cd <top>
       git init -b main
       cp <method>/bench/gitignore .gitignore     # then name the folders it keeps
       sh <method>/install.sh --bench <top>

   Add no remote. Name the notes, `.claude/`, `ledger/` and `mirror/` in the
   .gitignore. Never name the bench folder, or any other folder that is its
   own repository: git would record only a bare link to it. Such a folder
   (one with no remote of its own, say) is covered by the disk alone, or gets
   a private repository of its own if it holds only code.
3. Move the bench's own settings in, so a restore brings them back:
   - the ledger: `[ledger] path = "<top>/ledger"` in method.local.toml, and
     move the ledger's files there if it has any;
   - method.local.toml itself: move it to `<top>/method.local.toml` and set
     `UCDD_METHOD_LOCAL` to that path where the hook, the guard and the
     runners run.
4. Look before the first commit: `git status --short` must list nothing from
   the bench folder or a game library, no recording, no build output. Then:

       git add -A && git commit -m "Notes: first commit"

5. The hourly backups, from the user's crontab (`crontab -e`, no root
   needed):

       17 * * * * sh <method>/bench/backup.sh <bench folder> >> <top>/backup.log 2>&1
       19 * * * * sh <method>/bench/backup.sh <top> <Claude's memory folder> >> <top>/backup.log 2>&1

   An hour later `backup.log` names a snapshot for each ("backed up <hash>
   on refs/backup/hourly", or nothing when nothing changed), and
   `git ls-remote origin refs/backup/hourly` in the bench folder shows the
   bench's.
6. The backup disk: check that the nightly snapshot takes both `.git`
   folders (some tools skip hidden folders). Prefer a snapshot that keeps
   old copies (restic, borg, rsnapshot, btrfs or zfs snapshots) to a plain
   mirror: a mirror copies a mistake the next night. With git inside, a
   deleted note is still in the history; a deleted repository is not.

The method guard refuses shell commands that name the ledger's files.
`backup.sh` takes the ledger into each snapshot with `git add -A` into its own
index and runs as a script, so it is not refused. The working branch's copy
of the ledger is no longer committed hourly: it stays at its last commit
while the file grows, so a `git checkout -- .`, `git restore .`, `git stash`
or `git reset --hard` in the top folder would throw away its newer lines (the
snapshot keeps them). Never check out, reset or revert the ledger: it only
grows.

## On a new machine

1. Restore the top folder from the backup disk, `.git` folders included.
   Each working tree's last hour is its snapshot: `git -C <repo> restore
   --source=refs/backup/hourly --worktree -- .` (HEAD and the index stay;
   `git status` then shows the uncommitted work as it was). Copy
   `mirror/<memory>` back to Claude's memory folder from there
   (`git -C <top> archive refs/backup/hourly mirror | tar -x -C <scratch>`).
   For the bench, GitHub has the last hour: `git -C <bench folder> pull` and
   `git -C <bench folder> fetch origin refs/backup/hourly:refs/backup/hourly`
   (refused, rightly, when the disk's is the newer). If the disk is lost too, clone the bench folder from
   `https://github.com/TrongDog/ucdd-bench.git` and start the notes again.
2. Clone the fork, add the method branch as a worktree, and run `install.sh`
   for the worktrees, for Claude, and with `--bench` for both bench
   repositories (see the method README).
3. Set `UCDD_METHOD_LOCAL`, `GAMES` and `PATH` (NASM), put the crontab lines
   back, and run the self-tests: none may skip.
4. Restore the games, recordings and images from the disk.
