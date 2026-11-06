#!/usr/bin/env python3
"""A Claude Code PreToolUse hook: the method's seatbelts.

Refuses, with exit 2 and the reason shown to Claude:
- a git command that skips or moves the hooks: commit -n or --no-verify,
  merge --no-verify, core.hooksPath on the command line or set with config;
- a write to the results ledger other than by a runner: an edit of its
  files, a shell command that names them, ledger.py record or commit-runs
  typed by hand, and the runners' token (RUNNER_TOKEN) set by hand;
- a git command that stages, restores or checks out a path the guard
  protects, the ledger's folder or the game library (git_write_refusal);
- anything that reaches the upstream author: a push to his repository, a
  pull request, issue or comment there (gh or the GitHub tools), and a gh
  pr create that does not name the fork;
- a write into the game library (method.toml [games] paths): we never patch
  or alter game code, so nothing there is edited, moved, removed or
  overwritten; reading and copying out are fine;
- a commit made through the GitHub tools, which skips the commit-msg hook.
A person who needs the escape types the command in their own shell.

A shell line is read command by command (bash_refusal), with the shell's own
line structure first made plain (shell_text: an unquoted newline is a command
break, a backslash-newline is joined, comments and here-document bodies are
taken out, so a second line and an apostrophe in a body no longer hide a
command). The line's own variables (NAME=VALUE alone, export NAME=VALUE and
the like) are read into the words of the commands after them, then the
guard's environment, the program's name among them (G=git; $G add -A); PWD
and OLDPWD follow the line's cd. cd, pushd, popd and env -C are followed; where
the guard cannot follow (cd -, popd, a folder still unknown, after eval or
source) the folder is UNKNOWN. A command substitution ($( ), <( ), >( )) is
a command of its own, and the word it stood in is unknown. Shell keywords
(if, then, do, '{' ...) and launchers (env, nohup ...) are taken off before
the program. Code given to a shell with -c or to eval is read as a line of
its own, with the line's variables and again with only the command's own (a
child shell sees only what is exported). The rules other than git's read
each word as the shell will pass it.

Git writes (Michael's decision of 6 Nov 2026 on question 67 (7): "the guard
treats a git command that stages, restores or checks out a guard-protected
path as a write to it"). A git command is read from its words, the folder it
runs in (the hook's cwd, a cd earlier on the same line, env -C, -C) and its
work tree's top (git rev-parse; --work-tree or GIT_WORK_TREE when given).
What it reaches: its pathspecs (git's ':/', ':!' and ':(...)' magic read; a
pattern read as the folder its fixed part names, ':(icase)' as its root),
and for a whole-tree form the whole work tree (add -A, -u, -p with no path;
commit -a; a branch checkout or switch; checkout -f; reset with no path,
with a commit alone (--soft too) or with --hard; stash) or the folder it
runs in (clean). The commands that write the work tree from commits (merge,
rebase, cherry-pick, revert, pull, am, apply) reach the whole of it. With a
git dir (--git-dir, GIT_DIR) the repository it names is reached as well:
its index takes the paths. Dry runs and the read-only commands (log, show,
diff, status, cat-file, ls-files, blame ...) reach nothing. A command that
reaches a protected path is refused; so in the top folder, which holds the
ledger and the libraries, no whole-tree form passes and files are named.
Where the words cannot say, the reading is wide, never narrow (this reading,
the bare reset and reset --soft, and the commands that write from commits:
the agent's choice, confirmed by Michael 6 Nov 2026 (68.1), applied): a word
that may be a branch or a path reaches the whole tree unless it is a path that
exists; an exclusion frees only a path it names literally (':!*.md' frees
nothing); a writing command whose folder, git dir or a path is not known
before the line runs (a variable the line does not set, a substitution, a
backquote, UNKNOWN, a git dir not named .git) is refused; a GIT_WORK_TREE or
GIT_DIR the line sets is read with it and without it (git sees it only when
it is exported, which the guard does not follow). The index, the .gitignore
and what is changed are not read (the runs file is changed between plans
nearly always). A redirect into the ledger's files on a git command line is
refused as the other shell commands' are. Not read: git aliases and shell
aliases, a pathspec file's contents (refused as wide), launchers other than
LAUNCHERS (sudo, xargs, find -exec, timeout ...), the code of a substitution
inside double quotes or of a backquote (the word itself is unknown), git
init or clone into a library, commit --amend over a runs file commit, a push
from a folder the guard cannot read (judged by the remote's name alone), a
program named by a variable the line does not set ($EDITOR), and a launcher
named by one.

The runners' token (the same decision: "`ledger.py commit-runs` refuses to
run unless invoked by calbatch (a token calbatch sets), so a hand invocation
fails"): the runners set RUNNER_TOKEN for their own commit-runs call. A shell
command that sets it (before a command, through env, export or declare, or
in code given to a shell or an interpreter) and ledger.py commit-runs typed
by hand are refused; ledger.py itself refuses a token that does not name its
parent runner. Built, not run (6 Nov 2026; revised the same day on the
review: pattern exclusions, the line's variables, unknown folders and paths,
sh -c and eval, the git dir's repository; and again with the agent's choices
confirmed by Michael 6 Nov 2026 (68.1) applied: a program named by a variable
the line sets).

lessons_read = "terms: guard, git, ledger, token, runner, commit, hook, shell, variable; lessons: L38, L1, L9, L20, L40, L33, L10, L21, L22, L39, L31, L32, L24, L36, L23; 6 Nov 2026"
"""

from pathlib import Path
import json
import os
import re
import shlex
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
import methodlib  # noqa: E402

DECISION_67 = "Michael's decision of 6 Nov 2026 on question 67 (7)"
# The runners' token: tools/ledger.py's RUNNER_TOKEN, the same name (tests/test_commit_token.py
# checks that the two agree).
RUNNER_TOKEN = 'UCDD_LEDGER_RUNNER'

WHY = 'Refused by the method guard: {what}. {advice}'
HOOKS = ('Commits go through the commit-msg hook. If the hook is wrong, say so and fix '
         'the hook, or ask Michael to make the commit in his own shell.')
LEDGER = ('Only the runners write the ledger, after a run is judged. Read it with '
          'ledger.py show, spot or audit.')
GIT_LEDGER = (f'A git command that stages, restores or checks out a path the guard protects is a '
              f'write to it ({DECISION_67}). The runners commit the runs file (ledger.py '
              "commit-runs, at a plan's end) and plan.py --save commits a saved plan (ledger.py "
              'commit-plan TAG, when that commit was refused). In the top folder name the files you '
              'stage, restore or commit (git add FILE, git restore --staged FILE, git commit -m MSG '
              '-- FILE): a whole-tree form (-a, -A, ., stash, a reset with no path, a branch '
              'checkout) reaches the ledger too. Michael can run it in his own shell.')
# advice text is formatted with fork=: no braces in it
GIT_UNREAD = ('A git command that stages, restores or checks out is read before it runs '
              f'({DECISION_67}); where its folder, its git dir or a path is not known until then (a '
              'variable the line does not set, a command substitution, a backquote, cd - or popd, '
              'a cd after eval or source, a git dir not named .git) it may reach the ledger or a '
              'game library, so it is refused. Name the folder and the files in the command '
              'itself, or set the variable earlier on the same line.')
TOKEN = (f'The runners (calbatch.py, plan_run.py, sndreg) set {RUNNER_TOKEN} for their own '
         "commit-runs call at a plan's end; a hand commit of the runs file fails "
         f'({DECISION_67}: "`ledger.py commit-runs` refuses to run unless invoked by calbatch (a '
         'token calbatch sets), so a hand invocation fails"). Michael can commit it in his own shell.')
UPSTREAM = ('Nothing from this fork goes to the upstream author (Michael, 20 Oct 2026). '
            'Pull requests, if any, go to {fork} only.')
GAMES = ('We never patch or alter game code (Michael, 20 Oct 2026): every game runs as it was '
         'sold. Copy what you need to study out of the library; the fix belongs in the driver.')
GITHUB_FILES = ('Commits go through git on the bench, where the commit-msg hook checks them; the '
                'GitHub tools would skip it.')
# Commands that change the files they are given, and those that change only
# their last argument.
CHANGES_ARGS = {'rm', 'mv', 'truncate', 'touch', 'chmod', 'chown', 'tee', 'patch', 'shred', 'ln'}
CHANGES_LAST = {'cp', 'install', 'rsync', 'xxd'}
EDITS_IN_PLACE = {'sed', 'perl', 'ruby'}
# git commit's short options that take a value: the rest of the cluster is
# that value, so an "n" after one of them is not --no-verify.
COMMIT_VALUE_OPTIONS = set('mFCctSu')
GH_WRITES = {'create', 'comment', 'edit', 'close', 'reopen', 'merge', 'review', 'ready',
             'lock', 'unlock', 'delete', 'transfer', 'pin', 'develop'}
READ_PREFIXES = ('get_', 'list_', 'search_')
OWNER = methodlib.CONFIG['upstream']['owner'].lower()
FORK = methodlib.CONFIG['upstream']['fork']

PUNCTUATION = ';&|()'
# A here-document's operator and its delimiter word (<<WORD, <<-WORD, <<'WORD', << "WORD", <<\WORD)
HEREDOC = re.compile(r"<<(-?)[ \t]*\\?(['\"]?)([A-Za-z_][\w.-]*)\2")
# A shell variable in a word, $NAME or ${NAME}; any other $ form ($1, ${X:-y}) stays as written.
VARIABLE = re.compile(r'\$(?:([A-Za-z_]\w*)|\{([A-Za-z_]\w*)\})')
NAME = re.compile(r'[A-Za-z_]\w*\Z')
# What stands in a word for a command substitution, and the folder after a cd the guard cannot
# follow: neither is known before the line runs (unread() says so of any word holding a $ or a `).
SUBSTITUTED = '${...}'
UNKNOWN = SUBSTITUTED
# Shell keywords that can stand before a command's program.
RESERVED = {'!', '{', '}', 'if', 'then', 'else', 'elif', 'fi', 'do', 'done', 'while', 'until'}
# Launchers that run the command after them: taken off with their options before the program is
# read, each with its options that take a value (env's NAME=VALUE words count as assignments, env
# -C moves the folder, env -S's string is the command).
LAUNCHERS = {'env': {'-u', '--unset', '-C', '--chdir', '-S', '--split-string'},
             'command': set(), 'builtin': set(), 'exec': {'-a'}, 'nohup': set(), 'setsid': set(),
             'time': {'-o', '--output', '-f', '--format'}}
# Builtins that set a variable, and the shells and interpreters whose code can (with python*).
ASSIGNERS = {'export', 'declare', 'typeset', 'local', 'readonly'}
SHELLS = {'sh', 'bash', 'dash', 'zsh', 'ksh'}
INTERPRETERS = SHELLS | {'perl', 'ruby', 'node'}
SHELL_VALUES = {'-o', '+o', '-O', '+O', '--rcfile', '--init-file'}     # bash -o pipefail -c ...

# git subcommands that stage, restore or check out the paths they reach: {name: (short options
# that take a value, short options whose value is only the rest of their cluster, long options
# that take a value)}. How each one's words are read is git_reach's.
PATH_WRITES = {
    'add': ('', '', {'--chmod', '--pathspec-from-file'}),
    'stage': ('', '', {'--chmod', '--pathspec-from-file'}),
    'rm': ('', '', {'--pathspec-from-file'}),
    'mv': ('', '', set()),
    'restore': ('s', '', {'--source', '--conflict', '--pathspec-from-file'}),
    'checkout': ('bB', '', {'--orphan', '--conflict', '--pathspec-from-file'}),
    'switch': ('cC', '', {'--create', '--force-create', '--orphan', '--conflict'}),
    'reset': ('', '', {'--pathspec-from-file'}),
    'stash': ('m', '', {'--message', '--pathspec-from-file'}),
    'clean': ('e', '', {'--exclude'}),
    'commit': ('mFCct', 'Su', {'--message', '--file', '--reuse-message', '--reedit-message',
                               '--fixup', '--squash', '--template', '--author', '--date',
                               '--cleanup', '--trailer', '--pathspec-from-file'}),
    'update-index': ('', '', {'--cacheinfo', '--chmod'}),
    'checkout-index': ('', '', {'--prefix', '--stage'}),
}
# git subcommands that write the work tree from commits, whatever paths they name
TREE_WRITES = {'merge', 'rebase', 'cherry-pick', 'revert', 'pull', 'am', 'apply'}
APPLY_READS = {'--check', '--stat', '--numstat', '--summary'}     # git apply that writes nothing
WHOLE, HERE = object(), object()     # a command reaches the whole work tree, the folder it runs in


def read_bodies(line, at, bodies):
    """The here-document bodies that start at AT, one per (word, dash) in BODIES, each ending at a
    line that is its word (its leading tabs taken off with <<-): (where LINE goes on after them,
    their texts)."""
    texts = []
    for word, dash in bodies:
        lines = []
        while at < len(line):
            end = line.find('\n', at)
            end = len(line) if end < 0 else end
            text, at = line[at:end], end + 1
            if (text.lstrip('\t') if dash else text) == word:
                break
            lines.append(text)
        texts.append('\n'.join(lines))
    return min(at, len(line)), texts


def quoted(text):
    """TEXT as one single-quoted shell word."""
    return "'" + text.replace("'", "'\\''") + "'"


def shell_text(line):
    """LINE as shlex should read it: each unquoted newline a ';' (the shell's own command break,
    which shlex reads as a space), a backslash-newline joined, comments taken out, and each
    here-document's body made one word after its operator, '<<WORD' and its lines (a body is the
    command's input, not commands, and an apostrophe in one would leave shlex a quote it cannot
    close; the git rules skip the word, the token and ledger rules read it). Quotes are followed
    as the shell does; a here-document inside double quotes ("$(cat <<'EOF' ...)") stays as it
    is."""
    out, quote, start, bodies, index = [], None, True, [], 0
    while index < len(line):
        char = line[index]
        if quote == "'":
            quote = None if char == "'" else quote
        elif char == '\\' and index + 1 < len(line):
            if line[index + 1] != '\n':
                out.append(line[index:index + 2])
            index, start = index + 2, False
            continue
        elif quote == '"':
            quote = None if char == '"' else quote
        elif char in '\'"':
            quote = char
        elif char == '#' and start:
            end = line.find('\n', index)
            index = len(line) if end < 0 else end
            continue
        elif char == '<' and line.startswith('<<<', index):
            out.append('<<<')                           # a here-string: no body
            index, start = index + 3, False
            continue
        elif char == '<' and HEREDOC.match(line, index):
            found = HEREDOC.match(line, index)
            bodies.append((found.group(3), bool(found.group(1)), len(out)))
            out.append(found.group(0))
            index, start = found.end(), False
            continue
        elif char == '\n':
            index, texts = read_bodies(line, index + 1, [(word, dash) for word, dash, _ in bodies])
            for (word, _, position), text in zip(bodies, texts):
                out[position] += ' ' + quoted(f'<<{word}\n{text}')
            out.append(' ; ')
            bodies, start = [], True
            continue
        out.append(char)
        start = quote is None and char in ' \t;&|()'
        index += 1
    return ''.join(out)


def commands(line):
    """The words of each simple command in a shell line (shell_text's). A command substitution
    ($( ), and <( ) and >( )) is a command of its own, yielded when it closes, and leaves
    SUBSTITUTED in the word it stood in: its output is not known before the line runs. (One
    inside double quotes stays in its word as written, its $ with it.)"""
    lexer = shlex.shlex(shell_text(line), posix=True, punctuation_chars=PUNCTUATION)
    lexer.whitespace_split = True
    lexer.commenters = ''           # shell_text took the comments out; a # inside a word is the word's
    words, opened = [], []      # opened: per open parenthesis, the words a substitution interrupted, or None
    for token in lexer:
        if not token or not all(char in PUNCTUATION for char in token):
            words.append(token)
            continue
        for char in token:
            if char == '(' and words and words[-1].endswith(('$', '<', '>')):
                opened.append(words[:-1] + [words[-1][:-1] + SUBSTITUTED])
                words = []
                continue
            if words:
                yield words
            words = []
            if char == '(':
                opened.append(None)
            elif char == ')' and opened:
                words = opened.pop() or []
    if words:
        yield words


def unread(word):
    """Whether a word still holds a $ or a ` once its variables are read: what it names is not
    known before the line runs."""
    return '$' in word or '`' in word


def expand(word, names):
    """WORD with its $NAME and ${NAME} read from NAMES (the line's own variables), else from the
    guard's environment, and a leading ~; a variable neither holds stays as written (unread)."""
    def value(match):
        name = match.group(1) or match.group(2)
        found = names.get(name, os.environ.get(name))
        return match.group(0) if found is None else found
    return os.path.expanduser(VARIABLE.sub(value, word))


def program_words(words):
    """A simple command's leading NAME=VALUE words, its shell keywords (RESERVED) and its
    launchers (LAUNCHERS, with their options and those options' values) taken off: ({name: value}
    of the assignments, the words from its program on, the folder env -C runs it in or None).
    env -S's string is split into the words it runs."""
    assigned, chdir, words = {}, None, list(words)
    while words:
        word = words.pop(0)
        name, given, value = word.partition('=')
        if word in RESERVED:
            continue
        if given and NAME.match(name):
            assigned[name] = value
            continue
        values = LAUNCHERS.get(word.split('/')[-1])
        if values is None:
            words.insert(0, word)
            break
        while words and words[0].startswith('-'):
            option = words.pop(0)
            if option == '--':
                break
            key, given, value = option.partition('=')
            if not option.startswith('--') and option[:2] in values and len(option) > 2:
                key, value = option[:2], option[2:]          # -CDIR: the value attached
            elif key in values and not given:
                value = words.pop(0) if words else ''
            if key in ('-C', '--chdir'):
                chdir = value
            elif key in ('-S', '--split-string'):
                words = shlex.split(value) + words
    return assigned, words, chdir


def moved(cwd, command, args, names):
    """Where cd, pushd, popd or env -C leaves the commands after it: its operand ($NAME read from
    the line's variables NAMES, then the guard's environment; ~) against the folder before.
    UNKNOWN where the guard cannot follow it: popd, cd - and pushd's stack forms (the folder they
    go to is the shell's, not the line's), an operand still unread, a relative operand from an
    unknown folder. Unchanged for a folder that does not exist (the cd fails: with ';' the next
    command runs where the shell was, with '&&' not at all)."""
    operands = [word for word in args if word == '-' or not word.startswith(('-', '+'))]
    stack = (command == 'popd' or command == 'pushd' and not operands
             or any(word.startswith('+') for word in args))
    if stack or '-' in operands:
        return UNKNOWN
    target = expand(operands[0] if operands else '~', names)
    if unread(target) or (cwd == UNKNOWN and not Path(target).is_absolute()):
        return UNKNOWN
    path = Path(cwd or os.getcwd()) / target
    return str(path) if path.is_dir() else cwd


def upstream_remote(name, cwd):
    if OWNER in name.lower():
        return True
    try:
        url = subprocess.run(['git', 'remote', 'get-url', name], cwd=cwd or None,
                             capture_output=True, text=True).stdout
    except OSError:
        return False            # no such folder (UNKNOWN, a -C that does not exist): git fails there too
    return OWNER in url.lower()


def git_refusal(args, cwd, names=None):
    while args and args[0].startswith('-'):
        option = args.pop(0)
        value = option.split('=', 1)[1] if '=' in option else (
            args.pop(0) if option in ('-c', '-C', '--git-dir', '--work-tree') and args else '')
        if option.startswith('-c') and value.lower().startswith('core.hookspath'):
            return 'core.hooksPath set on the command line', HOOKS
        if option == '-C':
            cwd = str(Path(cwd or os.getcwd()) / expand(value, names or {}))
    if not args:
        return None
    command, rest = args[0], args[1:]
    reading = {'--get', '--get-all', '--get-regexp', '-l', '--list', 'get', 'list'}
    if (command == 'config' and any(word.lower() == 'core.hookspath' for word in rest)
            and not reading & set(rest)):
        return 'a change to core.hooksPath', HOOKS
    if command in ('commit', 'merge', 'pull', 'cherry-pick', 'revert', 'am') and '--no-verify' in rest:
        return f'git {command} --no-verify', HOOKS
    if command == 'commit':
        for word in rest:
            if word == '--':
                break
            if word.startswith('-') and not word.startswith('--'):
                for char in word[1:]:
                    if char == 'n':
                        return 'git commit -n (--no-verify)', HOOKS
                    if char in COMMIT_VALUE_OPTIONS:
                        break
    if command == 'push':
        targets = [word for word in rest if not word.startswith('-')]
        if targets and upstream_remote(targets[0], cwd):
            return f'a push to {targets[0]}, the upstream repository', UPSTREAM
    return None


def git_place(args, cwd, env, names):
    """git's global options read, with the line's variables (NAMES) and the command's environment
    (ENV: its GIT_WORK_TREE and GIT_DIR): (the folder the command runs in, its work tree's top
    when the command sets it, else None, the repository a git dir names, else None, the
    subcommand or None, the subcommand's words). --work-tree or GIT_WORK_TREE sets the top; a git
    dir alone makes it the folder git runs in, as git's own rule has it. The repository a git dir
    names is the folder holding it when it is named .git, else UNKNOWN (a bare one's or a
    worktree's: the guard does not read where their files are)."""
    base = Path(cwd or os.getcwd())
    work_tree, git_dir = env.get('GIT_WORK_TREE'), env.get('GIT_DIR')
    args = list(args)
    while args and args[0].startswith('-'):
        name, given, value = args.pop(0).partition('=')
        if name in ('-C', '-c', '--git-dir', '--work-tree', '--namespace') and not given:
            value = args.pop(0) if args else ''
        if name == '-C':
            base = base / expand(value, names)
        elif name == '--work-tree':
            work_tree = value
        elif name == '--git-dir':
            git_dir = value
    if not args:
        return base, None, None, None, []
    top = repository = None
    if git_dir:
        found = (base / expand(git_dir, names)).resolve()
        repository = found.parent if found.name == '.git' else Path(UNKNOWN)
        top = base.resolve()
    if work_tree:
        top = (base / expand(work_tree, names)).resolve()
    return base, top, repository, args[0], args[1:]


def work_tree_top(base):
    """The top of the work tree that holds BASE (git rev-parse), or None outside one. A caller's
    git settings never steer it."""
    env = {key: value for key, value in os.environ.items() if not key.startswith('GIT_')}
    try:
        found = subprocess.run(['git', '-C', str(base), 'rev-parse', '--show-toplevel'],
                               capture_output=True, text=True, env=env, timeout=20)
    except (OSError, subprocess.SubprocessError):
        return None
    line = found.stdout.strip()
    return Path(line).resolve() if found.returncode == 0 and line else None


def split_options(words, values='', attached='', long_values=()):
    """A git subcommand's words: (its options, its operands before '--', its operands after '--'
    or None when it has none). A short option in VALUES takes the rest of its cluster or else the
    next word; one in ATTACHED only the rest of its cluster (commit -S, -u); a long option in
    LONG_VALUES its '=' part or else the next word."""
    options, operands, after = set(), [], None
    words = iter(words)
    for word in words:
        if after is not None:
            after.append(word)
        elif word == '--':
            after = []
        elif word.startswith('--'):
            name = word.split('=', 1)[0]
            options.add(name)
            if name in long_values and '=' not in word:
                next(words, None)
        elif word.startswith('-') and word != '-':
            for position, char in enumerate(word[1:], 1):
                options.add('-' + char)
                if char in values or char in attached:
                    if char in values and position == len(word) - 1:
                        next(words, None)
                    break
        else:
            operands.append(word)
    return options, operands, after


def git_reach(command, rest, is_path):
    """What a git subcommand stages, restores or checks out: a list of its pathspecs and WHOLE
    (the whole work tree) or HERE (the folder it runs in); empty for a command that writes no
    tracked path (log, show, diff, status, cat-file ...) or only says what it would do (a dry
    run). IS_PATH(word) says whether an operand that may be a branch or a commit names a path."""
    if command in TREE_WRITES:
        reads = command == 'apply' and APPLY_READS & set(rest) and '--apply' not in rest
        return [] if reads else [WHOLE]
    if command not in PATH_WRITES:
        return []
    if command == 'stash':
        sub = rest[0] if rest and not rest[0].startswith('-') else 'push'
        if sub in ('list', 'show', 'create', 'store', 'drop', 'clear'):
            return []
        if sub != 'push':
            return [WHOLE]              # pop, apply, save, branch: the work tree to a stash or from one
        rest = rest[1:] if rest[:1] == ['push'] else rest
    options, operands, after = split_options(rest, *PATH_WRITES[command])
    paths = operands + (after or [])
    if '--pathspec-from-file' in options:
        return [WHOLE]                  # paths in a file the guard does not read
    if (command in ('add', 'stage', 'rm', 'mv', 'clean') and options & {'-n', '--dry-run'}
            or command == 'commit' and '--dry-run' in options):
        return []
    if command in ('add', 'stage'):
        whole = {'-A', '--all', '-u', '--update', '--no-ignore-removal', '-p', '--patch',
                 '-i', '--interactive', '-e', '--edit'}
        return paths or ([WHOLE] if options & whole else [])
    if command == 'commit':
        return paths + ([WHOLE] if options & {'-a', '--all', '-p', '--patch', '--interactive'} else [])
    if command in ('rm', 'mv', 'restore'):
        return paths                    # with no path git does nothing
    if command == 'clean':
        return paths or [HERE]
    if command == 'stash':
        return paths or [WHOLE]
    if command == 'switch':
        return [WHOLE] if operands or '--orphan' in options else []
    if command in ('update-index', 'checkout-index'):
        whole = {'--stdin', '--index-info', '--cacheinfo', '--again', '-g', '-a', '--all'}
        return paths + ([WHOLE] if options & whole else [])
    if command == 'checkout':
        forced = bool(options & {'-f', '--force', '-m', '--merge'})
        if after is not None:           # [<tree-ish>] -- <paths>
            return after or ([WHOLE] if operands or forced else [])
        if not operands:                # -b NAME alone keeps the tree; -f alone throws changes away
            return [WHOLE] if forced else []
        if options & {'-b', '-B', '--orphan'}:
            return [WHOLE]              # a start point: the tree becomes it
        return operands + ([] if is_path(operands[0]) else [WHOLE])
    # reset
    if options & {'--hard', '--merge', '--keep'}:
        return [WHOLE]
    if after is not None:               # [<commit>] -- <paths>
        return after or [WHOLE]
    if not operands or is_path(operands[0]):
        return operands or [WHOLE]      # no path: the whole index from HEAD
    # <commit> <paths>: those paths. <commit> alone moves HEAD, with --soft too: what HEAD had
    # then reads as staged against it (over a commit-runs commit, the runs file): refused with the
    # bare reset, the agent's choice, confirmed by Michael 6 Nov 2026 (68.1).
    return operands[1:] or [WHOLE]


def is_path(word, base, names):
    """Whether an operand that may be a branch or a commit names a path: a path's marks (., /, ~,
    git's ':' magic) or a file or folder there. A deleted file reads as a branch, which reaches
    the whole work tree: wide, never narrow."""
    word = expand(word, names)
    return word.startswith(('.', '/', '~', ':')) or os.path.lexists(base / word)


def pathspec(spec, base, top, names):
    """Where a pathspec reaches, resolved, whether it excludes and whether it is a pattern: its
    variables read (NAMES); git's magic read (':/' and ':(top)' from the work tree's top, ':!',
    ':^' and ':(exclude)' an exclusion, ':(literal)' no pattern, ':(icase)' a pattern with no
    fixed part, since any letter of it may match its other case); a pattern cut back to the
    folder its fixed part names, all it can reach."""
    spec = expand(spec, names)
    root, exclude, literal, icase = base, False, False, False
    if spec.startswith(':('):
        magic, _, spec = spec[2:].partition(')')
        words = {word.strip().split(':')[0] for word in magic.split(',')}
        exclude, literal, icase = 'exclude' in words, 'literal' in words, 'icase' in words
        root = (top or base) if 'top' in words else base
    elif spec.startswith(':'):
        index = 1
        while index < len(spec) and spec[index] in '/!^':
            exclude = exclude or spec[index] in '!^'
            root = (top or base) if spec[index] == '/' else root
            index += 1
        spec = spec[index + 1:] if spec[index:index + 1] == ':' else spec[index:]
    cuts = [] if literal else [spec.index(char) for char in '*?[' if char in spec]
    cuts = [0] if icase else cuts
    if cuts:
        spec = spec[:min(cuts)].rpartition('/')[0]
    path = Path(spec) if spec else Path('.')
    return (path if path.is_absolute() else Path(root) / path).resolve(), exclude, bool(cuts)


def overlaps(one, other):
    """Whether two resolved paths are one, or one holds the other."""
    return one == other or one.is_relative_to(other) or other.is_relative_to(one)


def protected_paths():
    """What the guard's write rules protect, each with its advice: the ledger's folder (the edit
    rule's) and the game libraries (library_paths)."""
    return ([(methodlib.ledger_dir().resolve(), GIT_LEDGER)]
            + [(library, GAMES) for library in library_paths()])


def git_write_refusal(args, cwd, env, names):
    """A git command that stages, restores or checks out a path the guard protects, refused as a
    write to it (DECISION_67: "the guard treats a git command that stages, restores or checks out
    a guard-protected path as a write to it"): what the command reaches (git_reach, read against
    the folder it runs in, its work tree's top and a git dir's repository) against the ledger's
    folder and the libraries. A writing command whose folder, git dir or a path is not known
    before the line runs is refused (wide); an exclusion frees only a path it names literally.
    The read-only commands naming them pass."""
    base, top, repository, command, rest = git_place(args, cwd, env, names)
    if command is None:
        return None
    reach = git_reach(command, rest, lambda word: is_path(word, base, names))
    if not reach:
        return None
    places = [str(base), str(top or ''), str(repository or '')]
    unsure = [word for word in places + [expand(spec, names) for spec in reach if isinstance(spec, str)]
              if unread(word)]
    if unsure:
        return f'git {command} with {unsure[0]!r}, a folder or path not known before the line runs', GIT_UNREAD
    top = top or work_tree_top(base)
    roots, freed, excluding = [], [], False
    for spec in reach:
        if spec is WHOLE:
            roots += [top] if top else []           # outside a work tree git itself refuses
        elif spec is HERE:
            roots.append(base.resolve())
        else:
            path, exclude, pattern = pathspec(spec, base, top, names)
            if not exclude:
                roots.append(path)
            else:
                excluding = True
                if not pattern:
                    freed.append(path)              # a literal exclusion frees what it names
    if excluding and not roots:
        roots.append(top or base.resolve())          # exclusions alone: everything else
    if repository and top and repository != top:     # a git dir's index takes the paths as well
        roots += [repository / root.relative_to(top) for root in roots if root.is_relative_to(top)]
    for protected, advice in protected_paths():
        if any(overlaps(root, protected) for root in roots) and not any(
                protected == path or protected.is_relative_to(path) for path in freed):
            return f'git {command} reaching {protected}, a path the guard protects', advice
    return None


def git_writes(args, cwd, assigned, names):
    """git_write_refusal read with the command's own environment (ASSIGNED), and again with a
    GIT_WORK_TREE or GIT_DIR the line set before it: git sees one only when it is exported
    (export, declare -x, set -a), which the guard does not follow, so both readings count."""
    line = {name: names[name] for name in ('GIT_WORK_TREE', 'GIT_DIR') if name in names}
    readings = [assigned] + ([dict(line, **assigned)] if line else [])
    return next(filter(None, (git_write_refusal(args, cwd, env, names) for env in readings)), None)


def gh_refusal(args):
    named_fork = any(FORK.lower() == word.lower() for word in args)
    upstream = any(OWNER in word.lower() for word in args)
    if args[:2] == ['pr', 'create'] and not named_fork:
        return 'gh pr create without --repo ' + FORK + ' (in a fork gh may pick the upstream)', UPSTREAM
    if upstream and len(args) > 1 and args[0] in ('pr', 'issue', 'release', 'repo') and args[1] in GH_WRITES:
        return f'gh {args[0]} {args[1]} on the upstream repository', UPSTREAM
    if upstream and args[:1] == ['api'] and any(
            word in ('-f', '-F', '--field', '--raw-field', '--input') or
            (word in ('-X', '--method') and index + 1 < len(args) and args[index + 1].upper() != 'GET')
            for index, word in enumerate(args)):
        return 'a gh api write to the upstream repository', UPSTREAM
    return None


def library_paths():
    given = os.environ.get('UCDD_GAMES')
    paths = given.split(os.pathsep) if given else methodlib.CONFIG.get('games', {}).get('paths', [])
    return [Path(path).expanduser().resolve() for path in paths if path]


def in_library(word, libraries):
    word = word.split('=', 1)[1] if word.startswith('of=') else word
    if not word or word.startswith('-'):
        return False
    path = Path(word).expanduser()
    if not path.is_absolute():
        return False
    path = path.resolve()
    return any(path == library or path.is_relative_to(library) for library in libraries)


def redirects(words):
    """The files a simple command's redirections write."""
    targets = []
    for index, word in enumerate(words):
        if word in ('>', '>>', '>|', '&>') and index + 1 < len(words):
            targets.append(words[index + 1])
        elif word.startswith('>') and len(word) > 1:
            targets.append(word.lstrip('>|&'))
    return targets


def library_refusal(words, libraries):
    program, args = words[0].split('/')[-1], words[1:]
    targets = redirects(words)
    operands = [word for word in args if not word.startswith('-')]
    if program in CHANGES_ARGS:
        targets += operands
    elif program in CHANGES_LAST and operands and (program != 'xxd' or '-r' in args):
        targets.append(operands[-1])
    elif program in EDITS_IN_PLACE and any(word.startswith('-i') or word == '--in-place' for word in args):
        targets += operands
    elif program == 'dd':
        targets += [word for word in args if word.startswith('of=')]
    found = [target for target in targets if in_library(target, libraries)]
    return (f'a write into the game library ({found[0]})', GAMES) if found else None


def names_ledger(words):
    ledger = methodlib.ledger_dir()
    marks = (str(ledger), 'runs.jsonl', f'{ledger.name}/plans')
    return any(mark in word for word in words for mark in marks)


def hand_commit_runs(words):
    """ledger.py commit-runs typed by hand (the runners call it as their own child, not through
    a shell the guard sees)."""
    return any(word.endswith('ledger.py') and words[index + 1:index + 2] == ['commit-runs']
               for index, word in enumerate(words))


def token_refusal(assigned, words):
    """The runners' token set by hand: before a command or through env (ASSIGNED), through
    export, declare and the like, or in code given to a shell or an interpreter."""
    program = words[0].split('/')[-1] if words else ''
    by_hand = (RUNNER_TOKEN in assigned
               or program in ASSIGNERS and any(word.split('=', 1)[0] == RUNNER_TOKEN for word in words[1:])
               or (program in INTERPRETERS or program.startswith('python'))
               and any(RUNNER_TOKEN in word for word in words[1:]))
    return (f'{RUNNER_TOKEN} set by hand', TOKEN) if by_hand else None


def shell_code(program, args):
    """The code a shell runs with -c (its first word after the options) or eval runs (its words
    joined), or None."""
    if program == 'eval':
        return ' '.join(args)
    if program not in SHELLS:
        return None
    given, args = False, list(args)
    while args:
        word = args.pop(0)
        if word in SHELL_VALUES:
            args = args[1:]
        elif word == '--':
            return (args[0] if args else None) if given else None
        elif word.startswith(('-', '+')) and word not in ('-', '+'):
            given = given or word.startswith('-') and not word.startswith('--') and 'c' in word
        else:
            return word if given else None
    return None


def shell_code_refusal(program, args, cwd, assigned, names):
    """Code given to a shell with -c or to eval, read as a line of its own: with the line's
    variables (the outer shell expands a double-quoted one) and again with the command's own
    alone (a child shell sees only what is exported, and single quotes keep the outer shell out),
    so both readings count. Code shlex cannot read is skipped: the shell cannot read it either."""
    code = shell_code(program, args)
    if code is None:
        return None
    try:
        return bash_refusal(code, cwd, names) or bash_refusal(code, cwd, assigned)
    except ValueError:
        return None


def command_refusal(words, cwd, assigned, names):
    """One simple command's refusal or None, read from its program on: ASSIGNED its own NAME=VALUE
    words, NAMES the line's variables before it. The rules other than git's read each word as the
    shell will pass it (SEEN)."""
    program = words[0].split('/')[-1]
    found = shell_code_refusal(program, words[1:], cwd, assigned, names)
    if found:
        return found
    seen = [expand(word, names) for word in words]
    if program == 'git':
        args = [word for word in words[1:] if not word.startswith('<<')]    # here-documents: input, not operands
        found = (git_refusal(list(args), cwd, names) or git_writes(args, cwd, assigned, names)
                 or (('a git command redirected into the ledger files', LEDGER)
                     if names_ledger(redirects(seen)) else None))
    elif program == 'gh':
        found = gh_refusal(words[1:])
    elif any(word.endswith('ledger.py') for word in seen) and 'record' in seen:
        found = 'ledger.py record typed by hand', LEDGER
    elif hand_commit_runs(seen):
        found = 'ledger.py commit-runs typed by hand', TOKEN
    elif names_ledger(seen) and not any(word.endswith(('ledger.py', 'plan.py')) for word in seen):
        found = 'a shell command on the ledger files', LEDGER
    else:
        found = None
    libraries = library_paths()
    if not found and libraries:
        found = library_refusal(seen, libraries)
    return found


def bash_refusal(line, cwd, names=None):
    """A shell line's refusal or None, its simple commands read in order: the line's own variables
    (NAME=VALUE alone, export NAME=VALUE and the like) carried to the commands after them; cd,
    pushd and popd followed, PWD and OLDPWD with them (UNKNOWN where the guard cannot follow, and
    after eval or source, whose code may move the shell); a program named by a variable read as
    its value; NAMES the variables a caller's line set before it (shell_code_refusal)."""
    names = {'PWD': cwd or os.getcwd(), 'OLDPWD': UNKNOWN, **(names or {})}
    for words in commands(line):
        assigned, words, chdir = program_words(words)
        if words and '$' in words[0]:
            # the program from a variable (G=git; $G add -A): read as the shell will run it, its
            # value split into words; one still unread stays as written (not read)
            program = expand(words[0], names)
            if not unread(program):
                try:
                    words = shlex.split(program) + words[1:]
                except ValueError:
                    words = program.split() + words[1:]
        place = moved(cwd, 'cd', [chdir], names) if chdir is not None else cwd
        found = token_refusal(assigned, words)
        if words and not found:
            found = command_refusal(words, place, assigned, names)
        if found:
            return found
        if not words:                                   # NAME=VALUE alone: shell variables
            for name, value in assigned.items():
                names[name] = expand(value, names)
        elif words[0] in ASSIGNERS:                     # export NAME=VALUE and the like
            for name, given, value in (word.partition('=') for word in words[1:]):
                if given and NAME.match(name):
                    names[name] = expand(value, names)
        elif words[0] in ('cd', 'pushd', 'popd'):
            to = moved(cwd, words[0], words[1:], names)
            if to != cwd:
                names.update(OLDPWD=names.get('PWD', UNKNOWN), PWD=to)
            cwd = to
        elif words[0] in ('eval', 'source', '.'):       # code run in this shell may move it
            cwd = UNKNOWN
    return None


def refusal(call):
    tool, given = call.get('tool_name', ''), call.get('tool_input', {})
    if tool == 'Bash':
        try:
            return bash_refusal(given.get('command', ''), call.get('cwd'))
        except ValueError:
            return None
    if tool in ('Write', 'Edit', 'MultiEdit', 'NotebookEdit'):
        path = given.get('file_path') or given.get('notebook_path') or ''
        if path and Path(path).resolve().is_relative_to(methodlib.ledger_dir().resolve()):
            return f'an edit of {path}', LEDGER
        if path and in_library(path, library_paths()):
            return f'an edit in the game library ({path})', GAMES
    name = tool.split('__')[-1]
    if tool.startswith('mcp__github__') and name in ('create_or_update_file', 'push_files', 'delete_file'):
        return f'{name} through the GitHub tools', GITHUB_FILES
    if tool.startswith('mcp__github__') and not (name.startswith(READ_PREFIXES) or name.endswith('_read')):
        if OWNER in str(given.get('owner', '')).lower() or OWNER in str(given.get('repo', '')).lower():
            return f'{name} on the upstream repository', UPSTREAM
    return None


def main():
    found = refusal(json.load(sys.stdin))
    if not found:
        return 0
    what, advice = found
    print(WHY.format(what=what, advice=advice.format(fork=FORK)), file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main())
