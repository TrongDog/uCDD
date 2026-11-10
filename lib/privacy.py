#!/usr/bin/env python3
"""Nothing personal goes to GitHub (the owner, 10 Nov 2026; tightening r3.10, gate T12).

The rule, in the owner's words: "If it doesn't need to be on github as part of the project, then
it doesn't go to github." Never, in a file or a commit message, on any repository that has a
remote: his first name, his city, the host's name, a login of his, a LAN address, a mount name,
a Claude session link. In everything written for GitHub he is "the owner".

What is refused is the [[banned]] list: method.toml's entries, and method.local.toml's for the
words that must never be written in a pushed file (the list itself would publish them). Each is
a Python regular expression with a `why`. An entry with `personal = true` is one of the owner's
and is refused on every repository with a remote, the bench included; the others (a bench
nickname, a local path, a mention of the upstream author) are the fork's rules, as before.

    [[banned]]                       # method.local.toml: never in a pushed file
    pattern = '(?i)\\bWORD\\b'
    why = "personal: first name"     # a refusal prints this; the matched text is never printed
    personal = true
    replace = "the owner"            # what tools/privrewrite.py writes in its place

    [privacy]                        # method.local.toml
    allow_phrases = ["An Exact Phrase"]   # the owner's approvals, one by one: a phrase that holds
                                          # a refused word and is someone or something else
    allow_paths = ["Some Document/*"]     # third-party documents he approved as they stand
    repos = ["~/clone", "~/bench"]        # the repositories `doctor` reads
    backup_log = "~/top/backup.log"       # the hourly backup's log (bench/backup.sh, from cron)

    [privacy]                        # method.toml (public): whose text a rewrite never alters
    third_party = ["Ralf Brown's Interrupt List/*", ...]

Nothing is waved through: a hit in third-party text stops the commit or the push, the owner is
asked once, and his approval is a line of method.local.toml. The upstream author's commits
([fixed] upstream_refs) are read against the personal entries only: a sync of his branch is not
refused for a rule of the fork's, and nothing of the owner's rides in on it.

Without the list there is no reading: when method.local.toml is not readable where a hook runs
(UCDD_METHOD_LOCAL unset in that shell and no file beside method.toml) or names no personal
word, a push to the fork is refused, unread; the bench's hooks say so in a line and go on (its
hourly backup is not stopped for it), and `doctor` names the fault.

A refusal no one reads is a backup that has stopped: the bench's check now has one more reason to
refuse an hourly snapshot (a new line holding a word), and cron's refusals go to a log. With
[privacy] backup_log set, `doctor` and every commit-msg hook say in one line when the newest
entry for a repository there is a refusal.

The clock ([privacy] utc_dates in method.toml, the fork's rule): a date's offset from UTC places
the machine that made the commit, so a commit made here carries +0000 (TZ=UTC). "Made here" is
measured, not named: the committer is this shell's own (git var GIT_COMMITTER_IDENT); the
author's date is read when the author is the same. The upstream author's dates are his.

    privacy.py commit-msg FILE [--scope fork|bench] [--no-lines]
                                                      the message, the identity, the clock and the
                                                      added lines
    privacy.py staged [--scope fork|bench]            the identity and the lines the index adds
    privacy.py pre-push REMOTE [URL] [--scope ...]    git's pre-push lines on stdin: every commit
                                                      about to leave: message, identity, added lines
    privacy.py doctor [REPO ...]                      each worktree's hooks are this package's, the
                                                      local list names a personal word, and the
                                                      identity and the clock git would commit with
                                                      are clean

The scopes: fork reads every [[banned]] entry, with renames off (a moved file is read whole, as
lib/checks.py reads it). bench reads the personal entries only, and its older records are not
rewritten (the ledger holds their hashes), so there: renames are on (moving a record adds
nothing that was not there), and a file that already broke an entry before the commit may be
edited and still break it; a file that did not may not begin to. What a program writes into a
new file is therefore clean or refused, and old text quoted into a new file goes through
reworded() first.

lessons_read = "terms: hook, commit, push, banned, rename, backup; lessons: L38, L20, L40, L33, L10, L22, L32, L24; 10 Nov 2026"
"""

from pathlib import Path
import argparse
import fnmatch
import os
import re
import subprocess
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent))
import methodlib  # noqa: E402

PACKAGE = methodlib.PACKAGE
SETTINGS = methodlib.CONFIG.get('privacy', {})
SHOWN = 12          # refusals printed; the rest are counted


class Rule:
    def __init__(self, entry):
        self.pattern = re.compile(entry['pattern'])
        self.why = entry['why']
        self.personal = bool(entry.get('personal'))
        self.replace = entry.get('replace')


def rules(scope='fork', config=None):
    """The [[banned]] entries that apply: all of them on the fork, the personal ones on the bench."""
    entries = (config if config is not None else methodlib.CONFIG).get('banned', [])
    found = [Rule(entry) for entry in entries]
    return [rule for rule in found if scope == 'fork' or rule.personal]


def mask(text, settings=None):
    """TEXT with every approved phrase blanked, so a word inside one is not read."""
    for phrase in (settings if settings is not None else SETTINGS).get('allow_phrases', []):
        if phrase:
            text = text.replace(phrase, ' ' * len(phrase))
    return text


def path_allowed(name, settings=None):
    globs = (settings if settings is not None else SETTINGS).get('allow_paths', [])
    return bool(name) and any(fnmatch.fnmatchcase(name, glob) for glob in globs)


def third_party(name, settings=None):
    globs = (settings if settings is not None else SETTINGS).get('third_party', [])
    return bool(name) and any(fnmatch.fnmatchcase(name, glob) for glob in globs)


def hits(text, found, name=None):
    """The rules TEXT breaks: each rule's `why`, never the text it matched. A personal rule is
    not read in a path the owner approved."""
    text = mask(text)
    approved = path_allowed(name)
    return [rule.why for rule in found
            if not (rule.personal and approved) and rule.pattern.search(text)]


SNIFF = 65536
CONTROL = bytes(c for c in range(32) if c not in (9, 10, 12, 13, 27))


def is_text(data):
    """Text by what it holds, as tools/libsearch.py reads the library (r3.9): no NUL byte and
    under 1 % control characters in the first 64 KB. A PDF with no early NUL is not text."""
    head = data[:SNIFF]
    if b'\0' in head:
        return False
    return not head or sum(head.count(c) for c in CONTROL) <= len(head) * 0.01


def git(*args, cwd=None, input=None, check=False):
    return subprocess.run(['git', '-c', 'core.quotePath=false', *args], cwd=cwd, input=input,
                          capture_output=True, text=True, errors='replace', check=check)


def added_lines(diff, sources=None):
    """File, line number and text of every line a -U0 diff adds. SOURCES, when given, is filled
    with each file's name before the commit (another name after a rename, None for a new file)."""
    name, number, old = None, 0, None
    for line in diff.splitlines():
        if line.startswith('--- '):
            old = line[4:].strip('"')
            old = old[2:] if old.startswith('a/') else None
        elif line.startswith('+++ '):
            name = line[4:].strip('"')
            name = name[2:] if name.startswith('b/') else None
            if sources is not None and name:
                sources[name] = old
        elif line.startswith('@@'):
            found = re.search(r'\+(\d+)', line)
            number = int(found.group(1)) if found else 0
        elif line.startswith('+') and name:
            yield name, number, line[1:]
            number += 1


def diff_options(scope):
    # the fork reads a moved file whole (renames off: lib/checks.py, the decisions of 6 Nov 2026);
    # the bench's older records are not rewritten, so there a pure move adds no line
    return ['-U0', '--no-color', '--no-ext-diff', '--no-renames' if scope == 'fork' else '-M']


def held(name, before, found, cwd=None):
    """The entries the file NAME already broke at the commit BEFORE."""
    if not name or not before:
        return set()
    done = subprocess.run(['git', 'cat-file', 'blob', f'{before}:{name}'], cwd=cwd, capture_output=True)
    if done.returncode or not is_text(done.stdout):
        return set()
    return set(hits(done.stdout.decode('utf-8', 'replace'), found, name))


def line_problems(diff, found, where='', before=None, cwd=None):
    """The entries the added lines break. BEFORE (the bench's scope) names the commit the lines
    are added to: an entry the file already broke there is not refused again."""
    problems, sources, already = [], {}, {}
    for name, number, text in added_lines(diff, sources):
        whys = hits(text, found, name)
        if whys and before:
            if name not in already:
                already[name] = held(sources.get(name), before, found, cwd)
            whys = [why for why in whys if why not in already[name]]
        for why in whys:
            problems.append(f'{where}{name}:{number}: {why}')
    return problems


def before_commit(scope, rev):
    return rev if scope == 'bench' else None


def reworded(text):
    """TEXT with every [[banned]] entry that names a `replace` giving way to it, approved phrases
    left as they are: what tools/privrewrite.py writes, and what a program calls on old text it
    quotes into a new file."""
    pairs = [(rule.pattern, rule.replace) for rule in rules('fork') if rule.replace is not None]
    phrases = [phrase for phrase in SETTINGS.get('allow_phrases', []) if phrase]
    if phrases:
        keep = re.compile('|'.join(re.escape(p) for p in sorted(phrases, key=len, reverse=True)))
        parts, last = [], 0
        for found in keep.finditer(text):
            parts += [(text[last:found.start()], False), (found.group(0), True)]
            last = found.end()
        parts.append((text[last:], False))
    else:
        parts = [(text, False)]
    out = []
    for part, kept in parts:
        if not kept:
            for pattern, replacement in pairs:
                part = pattern.sub(lambda _found, r=replacement: r, part)
        out.append(part)
    return ''.join(out)


def identity_problems(found, where='', cwd=None, idents=None):
    """The author's and committer's names and addresses against the personal rules: a commit made
    in a shell whose git identity is the owner's own would carry it to GitHub."""
    if idents is None:
        idents = [git('var', name, cwd=cwd).stdout.strip()
                  for name in ('GIT_AUTHOR_IDENT', 'GIT_COMMITTER_IDENT')]
    problems = []
    for ident in idents:
        ident = re.sub(r'\s+\d+\s+[+-]\d{4}$', '', ident)       # git var's date
        for why in hits(ident, [rule for rule in found if rule.personal]):
            problem = f'{where}the commit\'s author or committer identity: {why}'
            if problem not in problems:
                problems.append(problem)
    return problems


DATED = re.compile(r'^(.*?)\s+\d+\s+([+-]\d{4})$')
CLOCK = ('a date of the commit carries a clock offset, not +0000 ([privacy] utc_dates): '
         'commit with TZ=UTC set')


def split_ident(ident):
    """'Name <address> 1700000000 +0000' -> ('Name <address>', '+0000'); without a date, no offset."""
    found = DATED.match(ident.strip())
    return (found.group(1), found.group(2)) if found else (ident.strip(), None)


def utc_dates(scope):
    return scope == 'fork' and bool(SETTINGS.get('utc_dates'))


def own_ident(cwd=None):
    return split_ident(git('var', 'GIT_COMMITTER_IDENT', cwd=cwd).stdout)[0]


def clock_problems(scope, where='', cwd=None, author=None, committer=None, mine=None):
    """The clock offsets of a commit made here. Without AUTHOR and COMMITTER: the commit git is
    about to make (git var), whose committer is this shell by definition."""
    if not utc_dates(scope):
        return []
    if committer is None:
        author = git('var', 'GIT_AUTHOR_IDENT', cwd=cwd).stdout
        committer = git('var', 'GIT_COMMITTER_IDENT', cwd=cwd).stdout
        mine = split_ident(committer)[0]
    dated = [split_ident(ident) for ident in (author or '', committer)]
    bad = any(who == mine and offset not in (None, '+0000', '-0000') for who, offset in dated)
    return [where + CLOCK] if bad and mine else []


def message_text(path):
    # what git will store: comment lines and everything after the scissors go (hooks/commit-msg)
    lines = []
    for line in Path(path).read_text(errors='replace').splitlines():
        if line.startswith('# ') and '>8' in line:
            break
        if not line.startswith('#'):
            lines.append(line)
    return '\n'.join(lines).strip() + '\n'


def message_problems(text, found, where=''):
    return [f'{where}the message: {why}' for why in hits(text, found)]


def has_remote(cwd=None):
    return bool(git('remote', cwd=cwd).stdout.strip())


def staged_problems(scope, cwd=None):
    """The identity and the lines the index adds over HEAD (the bench's pre-commit, and the hourly
    backup's snapshot through it)."""
    found = rules(scope)
    diff = git('diff', '--cached', *diff_options(scope), cwd=cwd).stdout
    return (identity_problems(found, cwd=cwd) + clock_problems(scope, cwd=cwd)
            + line_problems(diff, found, before=before_commit(scope, 'HEAD'), cwd=cwd))


def merging(cwd=None):
    return git('rev-parse', '-q', '--verify', 'MERGE_HEAD', cwd=cwd).returncode == 0


def commit_msg_problems(path, scope, cwd=None, lines=True):
    found = rules(scope)
    problems = message_problems(message_text(path), found) + identity_problems(found, cwd=cwd)
    problems += clock_problems(scope, cwd=cwd)
    if lines and not merging(cwd):
        problems += line_problems(git('diff', '--cached', *diff_options(scope), cwd=cwd).stdout, found,
                                  before=before_commit(scope, 'HEAD'), cwd=cwd)
    return problems


def zero(oid):
    return set(oid) == {'0'}


def upstream_refs(cwd=None):
    """The refs whose commits are the upstream author's ([fixed] upstream_refs, as tools/ci.py
    reads them): his commits are not ours to check, and a sync of his branch is not refused for
    what he wrote."""
    refs = methodlib.CONFIG.get('fixed', {}).get('upstream_refs', [])
    return [ref for ref in refs
            if git('rev-parse', '-q', '--verify', f'{ref}^{{commit}}', cwd=cwd).returncode == 0]


def commit_problems(sha, found, scope, cwd=None, mine=None):
    """One commit about to be pushed. MINE is this shell's identity for the clock rule; None for
    a commit of the upstream author's, whose dates are his."""
    short = sha[:9]
    where = f'{short} '
    shown = git('show', '-s', '--date=raw', '--format=%an <%ae> %ad%x00%cn <%ce> %cd%x00%B', sha, cwd=cwd).stdout
    author, committer, message = (shown.split('\0', 2) + ['', '', ''])[:3]
    problems = message_problems(message, found, where)
    problems += identity_problems(found, where, idents=[author, committer])
    if mine:
        problems += clock_problems(scope, where, author=author, committer=committer, mine=mine)
    parents = git('rev-list', '--parents', '-n', '1', sha, cwd=cwd).stdout.split()[1:]
    if len(parents) > 1:
        # a merge: its message and identity only, as lib/checks.py reads a merge (what it brings
        # in was read where it was committed; the bench's hourly snapshot, a two-parent commit, has
        # its lines read by the bench's pre-commit before its ref is written)
        return problems
    diff = git('show', '--format=', *diff_options(scope), sha, cwd=cwd).stdout
    return problems + line_problems(diff, found, where, before_commit(scope, f'{sha}^'), cwd)


def pushed_commits(lines, remote, cwd=None, scope='fork'):
    """The commits a push would add to REMOTE, from git's pre-push lines (local ref, local id,
    remote ref, remote id): ours, the upstream author's (reachable from [fixed] upstream_refs),
    and the annotated tags among the pushed refs."""
    commits, theirs, tags = [], [], []
    for line in lines:
        parts = line.split()
        if len(parts) != 4:
            continue
        _, local, _, there = parts
        if zero(local):
            continue                                    # a deletion sends nothing
        kind = git('cat-file', '-t', local, cwd=cwd).stdout.strip()
        if kind == 'tag':
            tags.append(local)
        args = ['rev-list', local]
        if not zero(there) and git('cat-file', '-e', f'{there}^{{commit}}', cwd=cwd).returncode == 0:
            args.append(f'^{there}')
        sent = ['--not', f'--remotes={remote}'] if remote else []
        his = upstream_refs(cwd) if scope == 'fork' else []      # the bench's main is its own
        ours = git(*args, *[f'^{ref}' for ref in his], *sent, cwd=cwd).stdout.split()
        for sha in ours:
            if sha not in commits:
                commits.append(sha)
        for sha in git(*args, *sent, cwd=cwd).stdout.split():
            if sha not in ours and sha not in theirs:
                theirs.append(sha)
    return commits, [sha for sha in theirs if sha not in commits], tags


def push_problems(lines, remote, scope, cwd=None):
    found = rules(scope)
    personal = [rule for rule in found if rule.personal]
    commits, theirs, tags = pushed_commits(lines, remote, cwd, scope)
    mine = own_ident(cwd)
    problems = []
    for tag in tags:
        text = git('cat-file', 'tag', tag, cwd=cwd).stdout       # its tagger line and its message
        problems += [f'tag {tag[:9]} {problem}' for problem in message_problems(text, found)]
        tagger = re.search(r'^tagger (.+)$', text.split('\n\n', 1)[0], re.M)
        if tagger:
            problems += clock_problems(scope, f'tag {tag[:9]} ', author='', committer=tagger.group(1), mine=mine)
    for sha in commits:
        problems += commit_problems(sha, found, scope, cwd, mine)
    for sha in theirs:
        problems += commit_problems(sha, personal, scope, cwd)
    return problems, len(commits) + len(theirs)


def hooks_dir(worktree):
    path = git('rev-parse', '--git-path', 'hooks', cwd=worktree).stdout.strip()
    return (Path(worktree) / path).resolve() if path else None


def local_personal():
    """How many personal entries method.local.toml itself holds (the public list has only the
    session link: a block whose local list is empty refuses nothing of the owner's)."""
    try:
        entries = tomllib.loads(methodlib.LOCAL.read_text()).get('banned', [])
    except (OSError, tomllib.TOMLDecodeError):
        return 0
    return sum(1 for entry in entries if entry.get('personal'))


REFUSED = ('not backed up', 'not pushed to')


def backup_faults():
    """One line for each repository whose newest entry in the hourly backup's log is a refusal
    (bench/backup.sh: "TIME REPO not backed up: ..." or "... kept here, not pushed to ...")."""
    named = SETTINGS.get('backup_log')
    if not named:
        return []
    try:
        with open(Path(named).expanduser(), 'rb') as log:
            log.seek(0, os.SEEK_END)
            log.seek(max(0, log.tell() - 65536))
            lines = log.read().decode('utf-8', 'replace').splitlines()
    except OSError:
        return [f'the hourly backup\'s log is not readable ([privacy] backup_log)']
    newest = {}
    for line in lines:
        found = re.match(r'(\d{4}-\d\d-\d\dT\d\d:\d\dZ) (\S+?):? ', line)
        if found and ('backed up' in line or any(mark in line for mark in REFUSED)):
            newest[found.group(2)] = (found.group(1), line)
    return [f'the hourly backup of {Path(repo).name} was refused at {when}: its log has why ([privacy] backup_log)'
            for repo, (when, line) in sorted(newest.items()) if any(mark in line for mark in REFUSED)]


def doctor(repos):
    """One line per fault: a worktree of a repository with a remote whose commit-msg or pre-push
    hook is missing or not this package's, a local list with no personal word, an identity that
    breaks a personal rule."""
    problems, worktrees = backup_faults(), 0
    if not local_personal():
        problems.append(f'{methodlib.LOCAL.name} names no personal word ([[banned]] with personal = true): '
                        'only the session link is refused')
    personal = [rule for rule in rules('fork') if rule.personal]
    for repo in repos:
        repo = Path(repo).expanduser()
        if git('rev-parse', '--git-dir', cwd=repo).returncode:
            problems.append(f'{repo}: not a git repository')
            continue
        if not has_remote(repo):
            continue
        listed = git('worktree', 'list', '--porcelain', cwd=repo).stdout
        for worktree in re.findall(r'^worktree (.+)$', listed, re.M):
            if not Path(worktree).is_dir():
                continue
            worktrees += 1
            hooks = hooks_dir(worktree)
            scope = 'fork'
            for hook in ('commit-msg', 'pre-push'):
                path = hooks / hook if hooks else None
                if path is None or not path.is_file() or not os.access(path, os.X_OK):
                    problems.append(f'{worktree}: no {hook} hook ({path})')
                elif PACKAGE.resolve() not in path.resolve().parents:
                    problems.append(f'{worktree}: its {hook} hook is not this package\'s ({path.resolve()})')
                elif (PACKAGE / 'bench' / 'hooks').resolve() in path.resolve().parents:
                    scope = 'bench'                 # the bench's hooks: the personal entries, no clock rule
            problems += identity_problems(personal, f'{worktree}: ', cwd=worktree)
            problems += clock_problems(scope, f'{worktree}: ', cwd=worktree)
    return problems, worktrees


def report(name, problems, extra=''):
    print(f'{name}: refused by the [[banned]] list (lib/privacy.py: nothing personal goes to GitHub){extra}',
          file=sys.stderr)
    for problem in problems[:SHOWN]:
        print(f'  - {problem}', file=sys.stderr)
    if len(problems) > SHOWN:
        print(f'  - and {len(problems) - SHOWN} more', file=sys.stderr)
    print('A word that is someone or something else is the owner\'s to approve, once, in '
          f'{methodlib.LOCAL.name} ([privacy] allow_phrases or allow_paths).', file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('command', choices=['commit-msg', 'staged', 'pre-push', 'doctor'])
    parser.add_argument('rest', nargs='*')
    parser.add_argument('--scope', choices=['fork', 'bench'], default='fork')
    parser.add_argument('--no-lines', action='store_true',
                        help='commit-msg: the message and the identity only (a pre-commit reads the lines)')
    args = parser.parse_args(argv)

    if args.command == 'doctor':
        repos = args.rest or SETTINGS.get('repos', [])
        if not repos:
            print('privacy: no repository named ([privacy] repos in method.local.toml, or as arguments)')
            return 1
        problems, worktrees = doctor(repos)
        for problem in problems:
            print(f'privacy: {problem}')
        if not problems:
            print(f'privacy: hooks in place in {worktrees} worktrees of {len(repos)} repositories; '
                  f'{local_personal()} personal words in the local list')
        return 1 if problems else 0

    if not has_remote():
        return 0                    # a repository with no remote (the top folder) sends nothing
    if not local_personal():
        unread = (f'the owner\'s own words are not readable here: {methodlib.LOCAL} has no [[banned]] entry '
                  'with personal = true (set UCDD_METHOD_LOCAL to the file, or link it beside method.toml)')
        if args.command == 'pre-push' and args.scope == 'fork':
            print(f'pre-push: refused: {unread}; nothing is pushed to the fork unread', file=sys.stderr)
            return 1
        print(f'privacy: {unread}; only the session link is read', file=sys.stderr)
    if args.command == 'commit-msg':
        for fault in backup_faults():
            print(f'privacy: {fault}', file=sys.stderr)         # said at every commit until it is mended
        if not args.rest:
            parser.error('commit-msg needs the message file')
        problems = commit_msg_problems(args.rest[0], args.scope, lines=not args.no_lines)
        if problems:
            report('commit-msg', problems)
            kept = git('rev-parse', '--git-path', 'COMMIT_EDITMSG').stdout.strip()
            print(f'The message is kept in {kept}.', file=sys.stderr)
        return 1 if problems else 0
    if args.command == 'staged':
        problems = staged_problems(args.scope)
        if problems:
            report('pre-commit', problems)
        return 1 if problems else 0
    remote = args.rest[0] if args.rest else ''
    problems, count = push_problems(sys.stdin.read().splitlines(), remote, args.scope)
    if problems:
        report('pre-push', problems, f'; {count} commits read, nothing pushed')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
