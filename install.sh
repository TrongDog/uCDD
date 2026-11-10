#!/bin/sh
# Turn the commit-msg hook on in chosen uCDD worktrees only, and show how to
# give Claude Code the skill and the guard.
#
#   sh install.sh WORKTREE ...            the hook in these worktrees
#   sh install.sh --remove WORKTREE ...   the hook out of them again
#   sh install.sh --claude DIR            the skill linked into DIR/.claude,
#                                         and the settings lines to add there
#   sh install.sh --bench REPO            the bench's check linked into a
#                                         bench repository's .git/hooks, with
#                                         its commit-msg and pre-push (r3.10)
#   sh install.sh --shared REPO           commit-msg and pre-push linked into a
#                                         uCDD clone's own .git/hooks, for the
#                                         worktrees with no hooks path of their
#                                         own (the notes, the references): r3.10
#
# All worktrees share one hooks directory, so the hook is set per worktree
# (git config --worktree core.hooksPath) and the others never see it.

set -eu
here=$(cd "$(dirname "$0")" && pwd)
remove=0

python3 -c 'import sys, tomllib; sys.exit(sys.version_info < (3, 11))' 2>/dev/null ||
    { echo "install.sh: the hook needs Python 3.11 or later (tomllib)" >&2; exit 1; }

claude() {
    skills="$1/.claude/skills"
    mkdir -p "$skills"
    if [ -e "$skills/change-loop" ] && [ ! -L "$skills/change-loop" ]; then
        echo "$skills/change-loop exists and is not a link; left alone" >&2
    else
        ln -sfn "$here/skills/change-loop" "$skills/change-loop"
        echo "skill: $skills/change-loop -> $here/skills/change-loop"
    fi
    cat <<EOF

Add this to $1/.claude/settings.json (merge it with what is there):

{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash|Write|Edit|MultiEdit|NotebookEdit|mcp__github__.*",
        "hooks": [{ "type": "command", "command": "python3 $here/guard/guard.py" }]
      }
    ]
  }
}
EOF
}

# A bench repository reads its check from .git/hooks. core.hooksPath is left
# alone: the guard refuses any change to it, as a moved hooks path is how a
# uCDD commit would skip its hook.
bench() {
    if path=$(git -C "$1" config core.hooksPath); then
        echo "install.sh: $1: core.hooksPath is set ($path), so git does not read" \
             ".git/hooks there; the backup still runs the check itself" >&2
        exit 1
    fi
    hooks=$(cd "$1" && cd "$(git rev-parse --git-common-dir)" && pwd)/hooks
    mkdir -p "$hooks"
    if [ -e "$hooks/pre-commit" ] && [ ! -L "$hooks/pre-commit" ]; then
        echo "$hooks/pre-commit exists and is not a link; left alone" >&2
        exit 1
    fi
    ln -sfn "$here/bench/hooks/pre-commit" "$hooks/pre-commit"
    echo "bench check: $hooks/pre-commit -> $here/bench/hooks/pre-commit"
    # nothing personal goes to GitHub (the owner, 10 Nov 2026; tightening r3.10)
    link_hooks "$hooks" "$here/bench/hooks" commit-msg pre-push
}

# link_hooks DIR FROM NAME ...: each hook linked into DIR; one that is there and not a link is left
link_hooks() {
    dir=$1; from=$2; shift 2
    for name in "$@"; do
        if [ -e "$dir/$name" ] && [ ! -L "$dir/$name" ]; then
            echo "$dir/$name exists and is not a link; left alone" >&2
            exit 1
        fi
        ln -sfn "$from/$name" "$dir/$name"
        echo "hook: $dir/$name -> $from/$name"
    done
}

# A uCDD clone's own .git/hooks, read by every worktree that has no hooks path of its own (the
# notes, the references, the clone's main worktree): the [[banned]] list on their commits and
# pushes. The worktrees with a hooks path (the code worktrees, the method) have theirs there.
shared() {
    hooks=$(cd "$1" && cd "$(git rev-parse --git-common-dir)" && pwd)/hooks
    mkdir -p "$hooks"
    link_hooks "$hooks" "$here/hooks/shared" commit-msg pre-push
}

worktree() {
    top=$(git -C "$1" rev-parse --show-toplevel)
    if [ "$(git -C "$top" config --bool core.bare || echo false)" = true ] ||
       git -C "$top" config core.worktree >/dev/null; then
        echo "install.sh: $top: core.bare or core.worktree is set in the shared config;" \
             "move it to the main worktree's config.worktree first (git help worktree)" >&2
        exit 1
    fi
    git -C "$top" config extensions.worktreeConfig true
    if [ "$remove" = 1 ]; then
        git -C "$top" config --worktree --unset core.hooksPath || true
        echo "hook off: $top"
    else
        git -C "$top" config --worktree core.hooksPath "$here/hooks"
        echo "hook on:  $top ($(git -C "$top" symbolic-ref -q --short HEAD || echo detached))"
    fi
}

[ $# -gt 0 ] || { sed -n '2,19p' "$0" | sed 's/^# \{0,1\}//'; exit 1; }
while [ $# -gt 0 ]; do
    case "$1" in
        --remove) remove=1 ;;
        --claude) shift; claude "$1" ;;
        --bench) shift; bench "$1" ;;
        --shared) shift; shared "$1" ;;
        *) worktree "$1" ;;
    esac
    shift
done
