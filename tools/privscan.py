#!/usr/bin/env python3
"""Does a repository hold anything personal, anywhere in its history? (tightening r3.10)

    python3 METHOD/tools/privscan.py REPO [--refs REF ... | --pushed [REMOTE]] [--own] [--tree REV]
                                          [--skip GLOB ...] [--scope fork|bench] [--list] [--all-rules]

Reads everything reachable from REPO's refs (all of them, or the ones named): every version of
every text file, every file name, every commit and tag message, every author and committer
identity, against the [[banned]] list (lib/privacy.py; method.toml and method.local.toml). It
prints counts, by the rule's `why`; the matched text is never printed. --list adds the paths,
and for each the branch heads that hold that version now. Exit 1 when a personal rule is broken
outside what the owner approved ([privacy] allow_paths, allow_phrases), or any rule with
--all-rules; exit 0 otherwise.

    personal: first name: messages 0, identities 0, file names 0, file versions 0 in 0 files
    approved by the owner (allow_paths): 5 files

It is the gate's reading (run at each gate, and before and after a history rewrite), not the
hook's: the hooks read what a commit or a push adds; this reads what is already there. A binary
file (lib/privacy.py is_text: a NUL byte, or over 1 % control characters, in its first 64 KB) is
not read: a PDF is read through the extraction beside it.

--refs takes ref names, and ^NAME to leave a ref's history out, so `--refs refs/heads/notes
^refs/heads/main` reads a branch's own commits. Without it: every ref, the backup's and the tags
included. --pushed reads what is, or would be, on the remote: the branches, the tags and the
remote's own refs as this clone has them, and no other ref (not the old history a rewrite left
under refs/old). --own leaves the upstream author's history out ([fixed] upstream_refs). --tree REV reads
the files of that one commit and nothing else (what a checkout holds now, not what its history
held); --skip leaves paths out of the file reading (shell globs, * also matches a /), as
`--scope bench --tree HEAD --skip 'results/*'` reads the bench's programs and instructions and
leaves its older records, which are not rewritten.

The clock (scope fork): the dates of the repository's own commits and tags (those the upstream
refs do not reach) that carry an offset from UTC, counted for this shell's committer (git var
GIT_COMMITTER_IDENT in REPO), which is the hooks' rule, and beside it for every other committer,
which is for reading: a commit of the upstream author's that his refs here do not reach yet is
his. With [privacy] utc_dates the first count is a fault.

lessons_read = "terms: scan, history, hook, banned; lessons: L10; 10 Nov 2026"
"""

from pathlib import Path
import argparse
import collections
import fnmatch
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
import privacy  # noqa: E402

MAX_BYTES = 64 * 1024 * 1024


def git(repo, *args, input=None, text=True):
    done = subprocess.run(['git', '-c', 'core.quotePath=false', '-C', str(repo), *args], input=input,
                          capture_output=True, text=text, errors='replace' if text else None)
    return done.stdout


def objects(repo, refs):
    """Every blob reachable from REFS with the first path it was seen under."""
    paths = {}
    for line in git(repo, 'rev-list', '--objects', *refs).splitlines():
        sha, _, name = line.partition(' ')
        if name:
            paths.setdefault(sha, name)
    kinds = git(repo, 'cat-file', '--batch-check', input='\n'.join(paths) + '\n').splitlines()
    blobs = []
    for line in kinds:
        parts = line.split()
        if len(parts) == 3 and parts[1] == 'blob' and int(parts[2]) <= MAX_BYTES:
            blobs.append(parts[0])
    return paths, blobs


def head_holders(repo):
    """blob id -> the branch heads whose tree holds it now."""
    holders = collections.defaultdict(set)
    heads = [line for line in git(repo, 'for-each-ref', '--format=%(refname)', 'refs/heads',
                                  'refs/remotes').splitlines() if not line.endswith('/HEAD')]
    for head in heads:
        short = head.split('/', 2)[2] if head.count('/') >= 2 else head
        for line in git(repo, 'ls-tree', '-r', head).splitlines():
            meta, _, _ = line.partition('\t')
            parts = meta.split()
            if len(parts) == 3:
                holders[parts[2]].add(short)
    return holders


def tree_objects(repo, rev):
    """Every blob of the one commit REV, by its path there."""
    paths, blobs = {}, []
    for line in git(repo, 'ls-tree', '-r', '-l', rev).splitlines():
        meta, _, name = line.partition('\t')
        parts = meta.split()
        if len(parts) == 4 and parts[1] == 'blob' and parts[3].isdigit() and int(parts[3]) <= MAX_BYTES:
            paths.setdefault(parts[2], name)
    blobs = list(paths)
    return paths, blobs


def clocks(repo, refs, scope):
    """(dates of this shell's committer off UTC, its commits and tags read, other committers' off
    UTC) among the repository's own commits and annotated tags."""
    his = privacy.upstream_refs(repo) if scope == 'fork' else []
    mine = privacy.own_ident(repo)
    off = ('+0000', '-0000')
    ours = read = others = 0
    log = git(repo, 'log', '--date=raw', '--format=%an <%ae>%x1f%ad%x1f%cn <%ce>%x1f%cd', *refs,
              *[f'^{ref}' for ref in his])
    for line in log.splitlines():
        parts = line.split('\x1f')
        if len(parts) != 4:
            continue
        author, adate, committer, cdate = parts
        bad = cdate.split()[-1] not in off or (author == committer and adate.split()[-1] not in off)
        if committer == mine:
            read += 1
            ours += bad
        else:
            others += bad
    tags = git(repo, 'for-each-ref', '--format=%(objecttype)%1f%(taggername) %(taggeremail)%1f%(taggerdate:raw)',
               'refs/tags')
    for line in tags.splitlines():
        parts = line.split('\x1f')
        if len(parts) != 3 or parts[0] != 'tag' or not parts[2].split():
            continue
        bad = parts[2].split()[-1] not in off
        if parts[1] == mine:
            read += 1
            ours += bad
        else:
            others += bad
    return ours, read, others


def scan(repo, refs, scope='fork', tree=None, skip=()):
    found = privacy.rules(scope)
    counts = {rule.why: collections.Counter() for rule in found}
    files = {rule.why: {} for rule in found}                 # why -> {path: [versions, a blob id]}
    approved = collections.Counter()                          # path -> versions with an approved hit

    def note(why, kind, n=1):
        counts[why][kind] += n

    # messages and identities (not for --tree: one commit's files only)
    idents = set()
    if tree is None:
        log = git(repo, 'log', '--format=%an <%ae>%x1f%cn <%ce>%x1f%B%x1e', *refs)
        for record in log.split('\x1e'):
            parts = record.strip('\n').split('\x1f')
            if len(parts) != 3:
                continue
            idents.update(parts[:2])
            for why in privacy.hits(parts[2], found):
                note(why, 'messages')
        tags = git(repo, 'for-each-ref', '--format=%(taggername) %(taggeremail)%1f%(contents)%1e', 'refs/tags')
        for record in tags.split('\x1e'):
            tagger, _, text = record.strip('\n').partition('\x1f')
            if tagger.strip():
                idents.add(tagger.strip())
            for why in privacy.hits(text, found):
                note(why, 'messages')
    for ident in idents:
        for why in privacy.hits(ident, [rule for rule in found if rule.personal]):
            note(why, 'identities')

    # file names and file versions
    paths, blobs = objects(repo, refs) if tree is None else tree_objects(repo, tree)
    if skip:
        blobs = [sha for sha in blobs if not any(fnmatch.fnmatchcase(paths[sha], glob) for glob in skip)]
        paths = {sha: paths[sha] for sha in blobs}
    for name in sorted(set(paths.values())):
        for why in privacy.hits(name, [rule for rule in found if rule.personal]):
            note(why, 'file names')
    reader = subprocess.Popen(['git', '-C', str(repo), 'cat-file', '--batch'],
                              stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    for sha in blobs:
        reader.stdin.write((sha + '\n').encode())
        reader.stdin.flush()
        header = reader.stdout.readline().split()
        size = int(header[2])
        data = reader.stdout.read(size)
        reader.stdout.read(1)
        if not privacy.is_text(data):
            continue
        text = privacy.mask(data.decode('utf-8', 'replace'))
        name = paths[sha]
        allowed = privacy.path_allowed(name)
        for rule in found:
            if not rule.pattern.search(text):
                continue
            if rule.personal and allowed:
                approved[name] += 1
                continue
            note(rule.why, 'file versions')
            entry = files[rule.why].setdefault(name, [0, sha])
            entry[0] += 1
    reader.stdin.close()
    reader.wait()
    return found, counts, files, approved


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('repo')
    parser.add_argument('--refs', nargs='+', default=None)
    parser.add_argument('--pushed', nargs='?', const='', metavar='REMOTE',
                        help='the branches, the tags and the refs of REMOTE (of every remote without a name)')
    parser.add_argument('--own', action='store_true', help="leave out the upstream author's history")
    parser.add_argument('--tree', help='the files of this one commit only')
    parser.add_argument('--skip', nargs='+', default=[], help='paths left out of the file reading (shell globs)')
    parser.add_argument('--scope', choices=['fork', 'bench'], default='fork')
    parser.add_argument('--list', action='store_true', help='the paths, and the heads that hold each now')
    parser.add_argument('--all-rules', action='store_true', help='exit 1 on any rule, not only a personal one')
    args = parser.parse_args()
    if args.refs and args.pushed is not None:
        parser.error('--refs or --pushed, not both')
    if args.pushed is not None:
        args.refs = ['--branches', '--tags', f'--remotes={args.pushed}' if args.pushed else '--remotes']
    args.refs = args.refs or ['--all']
    if args.own:
        args.refs += [f'^{ref}' for ref in privacy.upstream_refs(args.repo)]

    found, counts, files, approved = scan(args.repo, args.refs, args.scope, args.tree, args.skip)
    holders = head_holders(args.repo) if args.list else {}
    bad = 0
    if args.tree:
        print(f'the files of {args.tree} only' + (f', without {", ".join(args.skip)}' if args.skip else ''))
    said = set()
    for rule in found:
        if rule.why in said:
            continue                    # entries that share a `why` are counted together
        said.add(rule.why)
        count = counts[rule.why]
        total = sum(count.values())
        print(f'{rule.why}: messages {count["messages"]}, identities {count["identities"]}, '
              f'file names {count["file names"]}, file versions {count["file versions"]} '
              f'in {len(files[rule.why])} files')
        if total and (any(r.personal for r in found if r.why == rule.why) or args.all_rules):
            bad += total
        if args.list:
            for name, (versions, sha) in sorted(files[rule.why].items(), key=lambda kv: (-kv[1][0], kv[0])):
                held = ', '.join(sorted(holders.get(sha, []))[:6]) or 'history only'
                third = ' (third-party tree)' if privacy.third_party(name) else ''
                print(f'    {versions:4} versions  {name}{third}  [{held}]')
    if approved:
        print(f'approved by the owner (allow_paths): {len(approved)} files, {sum(approved.values())} versions')
        if args.list:
            for name in sorted(approved):
                print(f'    {approved[name]:4} versions  {name}')
    if args.tree is None and args.scope == 'fork':
        ours, read, others = clocks(args.repo, args.refs, args.scope)
        print(f'dates on a clock other than UTC: {ours} of {read} commits and tags by this shell\'s committer; '
              f'{others} by other committers')
        if ours and privacy.utc_dates(args.scope):
            bad += ours
    if not any(rule.personal for rule in found):
        print('no personal rule in the list: nothing of the owner\'s was looked for')
        return 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
