#!/usr/bin/env python3
"""The fork's history rewritten once, so that nothing personal is left in it (tightening r3.10).

    python3 METHOD/tools/privrewrite.py run --source URL --work DIR [--keep REF ...] [--pin SHA ...]
                                            [--filter-repo FILE] [--keep-offsets] [--plant FAULT]
    python3 METHOD/tools/privrewrite.py translate --map FILE WORKTREE [--skip GLOB ...]
    python3 METHOD/tools/privrewrite.py lookup --map FILE SHA ...
    python3 METHOD/tools/privrewrite.py reword WORKTREE [--skip GLOB ...] [--dry-run]

run works on copies only and pushes nothing. In DIR (new, outside every work tree) it makes
before.git, a mirror of SOURCE as it stands (the copy to keep), and after.git, the same
rewritten with git-filter-repo (2.47 or later; --filter-repo names its git_filter_repo.py when
it is not importable). Then it checks its own work and writes DIR/commit-map.txt (old id, new
id) and DIR/report.txt. The push is a command it prints, for whoever the decision names.

What is rewritten: the fork's own commits only: every branch and tag except what is reachable
from the --keep refs (default: refs/heads/NAME for each [fixed] upstream_refs name, the upstream
author's history). A branch or a tag that points into his history (a release tag of his) is left
as it is, tag object and all. A rewrite that is not limited so strips his commits' signatures
and moves their ids (measured 10 Nov 2026: 723 of 745 commits moved, his branch with them).

What changes in those commits:
  - in every text file outside the third-party trees ([privacy] third_party) and in every commit
    and tag message, each [[banned]] entry that has a `replace` gives way to it (method.toml's and
    method.local.toml's; a phrase the owner approved in [privacy] allow_phrases is left as it is);
  - author, committer and tagger names and addresses by [privacy.authors] and [privacy.emails] of
    method.local.toml (old = new), when the owner has put any there;
  - author, committer and tagger dates keep their instant and lose their clock offset (+0000),
    unless --keep-offsets: an offset places the machine that made the commit.
Third-party documents are never altered: a personal word in one is another person's until the
owner says otherwise, and the report lists those files for him.

The checks, each a line of the report; any failure is exit 1 and nothing is to be pushed (--plant
makes the two faults the first trial met, for the checks' own test: unlimited, which check 2 must
catch, and third-party, which check 4 must catch):
  1. the keep refs, and every ref that points into their history, have the ids they had;
  2. as many commits after as before, every changed commit outside the keep refs;
  3. tools/privscan.py's reading of the rewritten refs: no personal rule broken outside the
     paths the owner approved;
  4. every third-party file at every rewritten head is byte for byte the file it was;
  5. every other file that differs at a head is exactly the old file with the replacements made;
  6. the code paths ([commit] code) at every rewritten commit are identical to the old commit's,
     so a build the ledger names is found again through the map, byte for byte; each --pin is
     named with its new id;
  7. every rewritten commit and tag carries its dates at +0000 (not with --keep-offsets).

translate rewrites, in a work tree's tracked text files outside the third-party trees and
--skip, each commit id the files cite (7 to 40 hex digits that begin exactly one old id of the
map) to the same length of its new id, and prints what it changed; the commit is the caller's.
A record the ledger holds by its hash is not translated (--skip 'results/*' on the bench), and
neither is a code file ([commit] code: a comment's citation is counted and left, so no build
moves): the map is how those old ids are read. lookup prints the new id of each old one.

reword is for a repository whose history is not rewritten (the bench: the ledger holds its
records' hashes): in WORKTREE's tracked text files, outside the third-party trees and --skip,
each [[banned]] entry that has a `replace` gives way to it, as the rewrite would write it. It
prints how many files and lines changed, by top folder, and then the lines to read before the
commit: each changed line of a program (.py, .sh) that is code and holds a test or a comparison,
because a string a program looks for must still match the older files it reads, which are not
reworded. --dry-run changes nothing. The commit is the caller's.

lessons_read = "terms: history, rewrite, force, push, mirror, backup; lessons: L38, L20, L33, L22, L45, L28, L32, L24; 10 Nov 2026"
"""

from pathlib import Path
import argparse
import bisect
import collections
import difflib
import fnmatch
import importlib.util
import os
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import methodlib  # noqa: E402
import privacy  # noqa: E402

HEX = re.compile(r'(?<![0-9a-fA-F])[0-9a-f]{7,40}(?![0-9a-fA-F])')


def git(repo, *args, check=True):
    done = subprocess.run(['git', '-c', 'core.quotePath=false', '-C', str(repo), *args],
                          capture_output=True, text=True, errors='replace')
    if check and done.returncode:
        raise SystemExit(f'git {" ".join(args)} failed in {repo}: {done.stderr.strip()[-300:]}')
    return done.stdout


def git_bytes(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, check=True).stdout


def replacers():
    """(pattern, replacement) for every [[banned]] entry that names one."""
    return [(rule.pattern, rule.replace) for rule in privacy.rules('fork') if rule.replace is not None]


def rewrite_text(text, pairs=None):
    """TEXT with the replacements made, approved phrases left as they are (lib/privacy.py)."""
    return privacy.reworded(text)


def rewrite_bytes(data, pairs=None):
    return rewrite_text(data.decode('utf-8', 'surrogateescape'), pairs).encode('utf-8', 'surrogateescape')


def is_binary(data):
    return not privacy.is_text(data)


def load_filter_repo(path):
    if path:
        spec = importlib.util.spec_from_file_location('git_filter_repo', path)
        module = importlib.util.module_from_spec(spec)
        sys.modules['git_filter_repo'] = module
        spec.loader.exec_module(module)
        return module
    try:
        import git_filter_repo
        return git_filter_repo
    except ImportError:
        raise SystemExit('git-filter-repo is not importable: name its git_filter_repo.py with --filter-repo '
                         '(2.47 or later, pinned in downloads.lock)')


def refs_of(repo):
    out = {}
    for line in git(repo, 'for-each-ref', '--format=%(refname) %(objectname)', 'refs/heads', 'refs/tags').splitlines():
        name, sha = line.split()
        out[name] = sha
    return out


def tree(repo, ref):
    """path -> blob id of every file at REF."""
    out = {}
    for line in git(repo, 'ls-tree', '-r', ref).splitlines():
        meta, _, name = line.partition('\t')
        parts = meta.split()
        if len(parts) == 3 and parts[1] == 'blob':
            out[name] = parts[2]
    return out


def run(args):
    work = Path(args.work).resolve()
    if work.exists() and any(work.iterdir()):
        raise SystemExit(f'{work} is not empty: the rewrite works in a folder of its own')
    work.mkdir(parents=True, exist_ok=True)
    inside = subprocess.run(['git', '-C', str(work), 'rev-parse', '--is-inside-work-tree'],
                            capture_output=True, text=True)
    if inside.returncode == 0 and inside.stdout.strip() == 'true':
        raise SystemExit(f'{work} lies inside a work tree: name a folder outside every repository')
    pairs = replacers()
    if not any(rule.personal and rule.replace is not None and rule.why != 'personal: a Claude session link'
               for rule in privacy.rules('fork')):
        raise SystemExit('no personal [[banned]] entry with a `replace` in method.local.toml: nothing of the '
                         "owner's would be rewritten")
    fr = load_filter_repo(args.filter_repo)
    before, after = work / 'before.git', work / 'after.git'
    subprocess.run(['git', 'clone', '-q', '--mirror', args.source, str(before)], check=True)
    subprocess.run(['git', 'clone', '-q', '--mirror', str(before), str(after)], check=True)
    git(after, 'remote', 'remove', 'origin')            # after.git pushes nowhere by itself
    old_refs = refs_of(before)
    keep = args.keep or [f'refs/heads/{name.split("/")[-1]}'
                         for name in methodlib.CONFIG.get('fixed', {}).get('upstream_refs', [])]
    keep = sorted({ref for ref in keep if ref in old_refs})
    if not keep:
        raise SystemExit("no --keep ref exists in the source: the upstream author's history must be named, "
                         'or his commits would be rewritten')
    kept_commits = set(git(before, 'rev-list', *keep).split())
    # a ref that points into the upstream author's history (a release tag of his) is his too
    inside = sorted(ref for ref in old_refs if ref not in keep
                    and git(before, 'rev-parse', '-q', '--verify', f'{ref}^{{commit}}', check=False).strip()
                    in kept_commits)
    rewritten = [ref for ref in old_refs if ref not in keep and ref not in inside]
    commits_before = len(git(before, 'rev-list', '--all').split())

    authors = privacy.SETTINGS.get('authors', {})
    emails = privacy.SETTINGS.get('emails', {})
    cache = {}

    def file_info(filename, mode, blob_id, value):
        if mode not in (b'100644', b'100755') or blob_id in cache:
            return filename, mode, cache.get(blob_id, blob_id)
        name = filename.decode('utf-8', 'surrogateescape')
        new = blob_id
        if args.plant == 'third-party' or not privacy.third_party(name):
            data = value.get_contents_by_identifier(blob_id)
            if data is not None and not is_binary(data):
                changed = rewrite_bytes(data, pairs)
                if changed != data:
                    new = value.insert_file_with_contents(changed)
        cache[blob_id] = new
        return filename, mode, new

    def message(text):
        changed = rewrite_bytes(text, pairs)
        return changed.rstrip(b'\n') + b'\n' if changed != text else text

    def utc(date):
        return date if args.keep_offsets else date.split()[0] + b' +0000'

    def mapped(value, table):
        return table.get(value.decode('utf-8', 'surrogateescape'), None)

    def person(obj, prefix):
        for field, table in (('name', authors), ('email', emails)):
            attr = f'{prefix}_{field}'
            new = mapped(getattr(obj, attr), table)
            if new is not None:
                setattr(obj, attr, new.encode())
        setattr(obj, f'{prefix}_date', utc(getattr(obj, f'{prefix}_date')))

    def commit(obj, _metadata):
        person(obj, 'author')
        person(obj, 'committer')

    def tag(obj, _metadata):
        if getattr(obj, 'tagger_name', None) is not None:
            person(obj, 'tagger')

    here = os.getcwd()
    os.chdir(after)
    try:
        options = fr.FilteringOptions.parse_args(
            ['--force', '--quiet', '--replace-refs', 'delete-no-add', '--prune-empty', 'never',
             '--prune-degenerate', 'never', '--refs', *rewritten,
             *([] if args.plant == 'unlimited' else [f'^{ref}' for ref in keep])],
            error_on_empty=False)
        fr.RepoFilter(options, file_info_callback=file_info, message_callback=message,
                      commit_callback=commit, tag_callback=tag).run()
    finally:
        os.chdir(here)

    # ---- the checks ----
    lines, bad = [], []

    def check(ok, text):
        lines.append(('ok   ' if ok else 'BAD  ') + text)
        if not ok:
            bad.append(text)

    new_refs = refs_of(after)
    moved_keep = [ref for ref in keep + inside if new_refs.get(ref) != old_refs[ref]]
    check(not moved_keep, f'1. the keep refs keep their ids ({", ".join(keep)}'
          + (f'; and {len(inside)} refs that point into their history' if inside else '') + ')'
          + (f': moved {", ".join(moved_keep)}' if moved_keep else ''))

    pairs_map = [line.split() for line in (after / 'filter-repo' / 'commit-map').read_text().splitlines()[1:]]
    changed = {old: new for old, new in pairs_map if old != new}
    commits_after = len(git(after, 'rev-list', *new_refs.values()).split())
    astray = [old for old in changed if old in kept_commits]
    check(commits_after == commits_before and not astray,
          f'2. {commits_after} commits after, {commits_before} before; {len(changed)} of the fork\'s own '
          f'{len(pairs_map)} have a new id; {len(astray)} of the keep refs\' commits changed')

    scan = subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'privscan.py'), str(after),
                           '--list', '--refs', *[ref for ref in new_refs if ref not in keep],
                           *[f'^{ref}' for ref in keep]], capture_output=True, text=True)
    check(scan.returncode == 0, '3. privscan on the rewritten refs: '
          + ('no personal rule broken outside the approved paths' if scan.returncode == 0
             else 'a personal rule is broken (below)'))

    third_changed, other_wrong, differing = [], [], collections.Counter()
    third_hits = set()
    personal = [rule for rule in privacy.rules('fork') if rule.personal]
    for ref in rewritten:
        if not ref.startswith('refs/heads/'):
            continue
        old_tree, new_tree = tree(before, old_refs[ref]), tree(after, new_refs[ref])
        if set(old_tree) != set(new_tree):
            other_wrong.append(f'{ref}: the file list changed')
        for name, blob in new_tree.items():
            was = old_tree.get(name)
            if privacy.third_party(name):
                if was != blob:
                    third_changed.append(f'{ref}:{name}')
                continue
            if was is None or was == blob:
                continue
            differing[ref] += 1
            old_data = git_bytes(before, 'cat-file', 'blob', was)
            if rewrite_bytes(old_data, pairs) != git_bytes(after, 'cat-file', 'blob', blob):
                other_wrong.append(f'{ref}:{name}')
        for name, blob in new_tree.items():
            if privacy.third_party(name) and name not in third_hits:
                data = git_bytes(after, 'cat-file', 'blob', blob)
                if not is_binary(data) and any(rule.pattern.search(privacy.mask(data.decode('utf-8', 'replace')))
                                               for rule in personal):
                    third_hits.add(name)
    check(not third_changed, f'4. third-party files at the rewritten heads are byte for byte as they were'
          + (f': {len(third_changed)} changed, first {third_changed[0]}' if third_changed else ''))
    check(not other_wrong, f'5. {sum(differing.values())} other files differ at {len(differing)} heads, each '
          'exactly the old file with the replacements made'
          + (f': {len(other_wrong)} not so, first {other_wrong[0]}' if other_wrong else ''))

    code = methodlib.CONFIG['commit']['code']

    def code_of(repo, commit):
        return {name: blob for name, blob in tree(repo, commit).items()
                if any(fnmatch.fnmatchcase(name, glob) for glob in code)}

    # the code at every rewritten commit is the code at the commit it was (a ledger entry's build
    # is found again through the map, byte for byte)
    differ = [old for old, new in changed.items() if code_of(before, old) != code_of(after, new)]
    check(not differ, f'6. the code paths ({", ".join(code)}) at each of the {len(changed)} rewritten commits are '
          'identical to the old commit\'s' + (f': {len(differ)} differ, first {differ[0][:12]}' if differ else ''))
    for pin in args.pin:
        full = git(before, 'rev-parse', '--verify', f'{pin}^{{commit}}').strip()
        new = changed.get(full, full)
        check(full not in differ, f'6. pin {full[:9]} is now {new[:9]}: its {len(code_of(after, new))} code files '
              + ('are identical' if full not in differ else 'DIFFER'))

    if not args.keep_offsets:
        own = [new_refs[ref] for ref in rewritten if ref in new_refs]
        zones = collections.Counter(git(after, 'log', '--date=format:%z', '--format=%ad%n%cd', *own,
                                        *[f'^{old_refs[ref]}' for ref in keep]).split() if own else [])
        tags = [ref for ref in rewritten if ref.startswith('refs/tags/')]
        tagged = git(after, 'for-each-ref', '--format=%(objecttype) %(taggerdate:format:%z)',
                     *tags).splitlines() if tags else []
        zones.update(line.split()[1] for line in tagged if line.startswith('tag ') and len(line.split()) == 2)
        away = sum(n for zone, n in zones.items() if zone not in ('+0000', '-0000'))
        check(not away, '7. every rewritten commit and tag carries its dates at +0000'
              + (f': {away} dates do not' if away else ''))

    first = [old for old, new in changed.items()
             if not any(parent in changed for parent in git(before, 'rev-list', '--parents', '-n', '1', old).split()[1:])]
    by_author = collections.Counter(git(before, 'log', '--no-walk', '--format=%an', *changed).splitlines()
                                    if changed else [])
    # commit ids cited in messages: filter-repo writes the new id where it already knows it; a
    # citation of a commit that comes later in the history keeps the old id, and is listed
    olds = sorted(changed)
    stale = []
    own = [new_refs[ref] for ref in rewritten if ref in new_refs]
    log = git(after, 'log', '--format=%H%x1f%B%x1e', *own, *[f'^{old_refs[ref]}' for ref in keep]) if own else ''
    for record in log.split('\x1e'):
        sha, _, body = record.strip('\n').partition('\x1f')
        for token in set(HEX.findall(body)):
            at = bisect.bisect_left(olds, token)
            found = [old for old in olds[at:at + 2] if old.startswith(token)]
            if len(found) == 1:
                stale.append(f'{sha[:12]} cites {token}, now {changed[found[0]][:len(token)]}')
    (work / 'commit-map.txt').write_text(''.join(f'{old} {new}\n' for old, new in pairs_map))
    report = [f'source: {args.source}', f'refs rewritten: {len(rewritten)}; kept: {", ".join(keep)}',
              *lines, '',
              'changed commits by author (before): ' + ', '.join(f'{n} {a}' for a, n in by_author.most_common()),
              f'first changed commits ({len(first)}): ' + ' '.join(sorted(sha[:12] for sha in first)[:40]),
              f'messages that still cite an old id, by their new commit ({len(stale)}):',
              *[f'    {line}' for line in sorted(stale)],
              f'third-party files holding a personal word, left as they are, for the owner ({len(third_hits)}):',
              *[f'    {name}' for name in sorted(third_hits)], '', 'privscan --list on the rewritten refs:',
              *['    ' + line for line in (scan.stdout + scan.stderr).splitlines()], '',
              'the push, once the decision names who makes it (after.git has no remote of its own):',
              f"    git -C {after} push --force {args.source} 'refs/heads/*:refs/heads/*' 'refs/tags/*:refs/tags/*'",
              f'the copy to keep: {before}; the map: {work / "commit-map.txt"}']
    (work / 'report.txt').write_text('\n'.join(report) + '\n')
    print('\n'.join(report[:2 + len(lines)]))
    print(f'{work / "report.txt"}: {"nothing to push: " + str(len(bad)) + " checks failed" if bad else "all checks passed"}')
    return 1 if bad else 0


def read_map(path):
    pairs = [line.split() for line in Path(path).read_text().splitlines() if len(line.split()) == 2]
    return {old: new for old, new in pairs if re.fullmatch(r'[0-9a-f]{40}', old)}


def translate(args):
    table = read_map(args.map)
    olds = sorted(table)
    worktree = Path(args.worktree)
    counts, files = collections.Counter(), 0
    code, left = methodlib.CONFIG['commit']['code'], collections.Counter()

    def new_for(token):
        at = bisect.bisect_left(olds, token)
        found = [old for old in olds[at:at + 2] if old.startswith(token)]
        if len(found) != 1 or table[found[0]] == found[0]:
            return None                         # no old id, more than one, or an id that did not change
        return table[found[0]][:len(token)]

    for name in git(worktree, 'ls-files').splitlines():
        path = worktree / name
        if (privacy.third_party(name) or any(fnmatch.fnmatchcase(name, glob) for glob in args.skip)
                or not path.is_file() or path.is_symlink()):
            continue
        data = path.read_bytes()
        if is_binary(data):
            continue
        text = data.decode('utf-8', 'surrogateescape')
        here = collections.Counter()

        def swap(found):
            new = new_for(found.group(0))
            if new is None:
                return found.group(0)
            here[f'{found.group(0)} -> {new}'] += 1
            return new

        changed = HEX.sub(swap, text)
        if changed != text and any(fnmatch.fnmatchcase(name, glob) for glob in code):
            left[name] = sum(here.values())         # a code file is not touched: no build moves
            continue
        if changed != text:
            tmp = path.with_name(path.name + '.translate.tmp')
            tmp.write_bytes(changed.encode('utf-8', 'surrogateescape'))
            os.chmod(tmp, path.stat().st_mode)
            os.replace(tmp, path)               # a tracked file is written through a rename (L4)
            files += 1
            counts.update(here)
    for swap_line, n in sorted(counts.items()):
        print(f'{n:4}  {swap_line}')
    print(f'{sum(counts.values())} citations of {len(counts)} commits translated in {files} files of {worktree}')
    if left:
        print(f'left in code files, where the map reads them ({sum(left.values())} citations): '
              + ', '.join(sorted(left)))
    return 0


PROGRAMS = ('.py', '.sh')
TESTED = re.compile(r'\b(if|elif|assert|while|case)\b|==|!=|\bin\b|\bre\.\w+\(|startswith|endswith|\.find\(|'
                    r'\.count\(|\.index\(|\bgrep\b|\[ ')
TRIPLE = ('"' * 3, "'" * 3)


def code_lines(lines):
    """The 1-based numbers of the lines that are code: not a comment line, not inside a docstring."""
    out, inside = set(), False
    for number, line in enumerate(lines, 1):
        text = line.strip()
        quotes = sum(text.count(mark) for mark in TRIPLE)
        was = inside
        if quotes % 2:
            inside = not inside
        if not was and not quotes and text and not text.startswith('#'):
            out.add(number)
    return out


def reword(args):
    worktree = Path(args.worktree)
    files, lines_changed, to_read = collections.Counter(), 0, []
    for name in git(worktree, 'ls-files').splitlines():
        path = worktree / name
        if (privacy.third_party(name) or any(fnmatch.fnmatchcase(name, glob) for glob in args.skip)
                or not path.is_file() or path.is_symlink()):
            continue
        data = path.read_bytes()
        if is_binary(data):
            continue
        new = rewrite_bytes(data)
        if new == data:
            continue
        old_lines = data.decode('utf-8', 'surrogateescape').split('\n')
        new_lines = new.decode('utf-8', 'surrogateescape').split('\n')
        if len(old_lines) == len(new_lines):
            moved = [n for n, (a, b) in enumerate(zip(old_lines, new_lines), 1) if a != b]
            count = len(moved)
        else:                                   # a whole line went (a session line)
            moved, count = [], 0
            for kind, a, b, start, end in difflib.SequenceMatcher(None, old_lines, new_lines,
                                                                  autojunk=False).get_opcodes():
                if kind != 'equal':
                    count += max(b - a, end - start)
                    moved += range(start + 1, end + 1)
        files[name.split('/')[0] if '/' in name else '.'] += 1
        lines_changed += count
        if name.endswith(PROGRAMS):
            code = code_lines(new_lines)
            to_read += [f'{name}:{n}' for n in moved
                        if n in code and TESTED.search(new_lines[n - 1].split('#')[0])]
        if not args.dry_run:
            tmp = path.with_name(path.name + '.reword.tmp')
            tmp.write_bytes(new)
            os.chmod(tmp, path.stat().st_mode)
            os.replace(tmp, path)               # a tracked file is written through a rename
    for folder, n in sorted(files.items(), key=lambda kv: (-kv[1], kv[0])):
        print(f'{n:6}  {folder}')
    print(f'{sum(files.values())} files, {lines_changed} lines '
          + ('would be reworded' if args.dry_run else 'reworded') + f' in {worktree}'
          + (f' (without {", ".join(args.skip)})' if args.skip else ''))
    if to_read:
        print(f'to read before the commit ({len(to_read)}): program lines that test or compare; what a '
              'program looks for must still match the older files it reads')
        for line in to_read:
            print(f'    {line}')
    return 0


def lookup(args):
    table = read_map(args.map)
    status = 0
    for sha in args.sha:
        found = [old for old in table if old.startswith(sha)]
        if len(found) == 1:
            print(f'{sha} {table[found[0]]}')
        else:
            print(f'{sha} {"not in the map" if not found else "more than one"}')
            status = 1
    return status


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    sub = parser.add_subparsers(dest='command', required=True)
    one = sub.add_parser('run')
    one.add_argument('--source', required=True, help='the repository as it stands: its URL')
    one.add_argument('--work', required=True, help='a new folder outside every work tree')
    one.add_argument('--keep', nargs='+', default=[], help="refs whose history is the upstream author's")
    one.add_argument('--pin', nargs='+', default=[], help='commits whose code paths must come out identical')
    one.add_argument('--filter-repo', help='git_filter_repo.py, when it is not importable')
    one.add_argument('--keep-offsets', action='store_true', help='leave the dates\' clock offsets as they are')
    one.add_argument('--plant', choices=['unlimited', 'third-party'],
                     help='a planted fault for the checks (L4): the limit to the fork\'s own commits off '
                          '(check 2 must fail), or the third-party trees read as ordinary files (check 4 must fail)')
    two = sub.add_parser('translate')
    two.add_argument('--map', required=True)
    two.add_argument('--skip', nargs='+', default=[], help='paths left as they are (shell globs)')
    two.add_argument('worktree')
    three = sub.add_parser('lookup')
    three.add_argument('--map', required=True)
    three.add_argument('sha', nargs='+')
    four = sub.add_parser('reword')
    four.add_argument('worktree')
    four.add_argument('--skip', nargs='+', default=[], help='paths left as they are (shell globs)')
    four.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    return {'run': run, 'translate': translate, 'lookup': lookup, 'reword': reword}[args.command](args)


if __name__ == '__main__':
    sys.exit(main())
