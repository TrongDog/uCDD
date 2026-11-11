#!/usr/bin/env python3
"""doccheck.py [--ref REF | --staged | --dir DIR] [--register BRANCH:PATH] [--old-ids FILE]
               [--only links,names,...] [--todo]

The pages' checks (lib/docs.py; tightening r3.11, gate T13): links, names, orphans, stamp, words,
markers, register, oldids. Prints each problem and exits 1 when there is one. --todo lists the
[TODO: ...] markers the pages carry; they are counted in every run and never refused.

  doccheck.py                      the pages' branch as this clone holds it (origin/<branch>)
  doccheck.py --staged             the index: what the commit hook reads
  doccheck.py --dir DIR            a directory laid out as the repository (a draft before it is
                                   committed); links to other branches are read when --git names
                                   the clone to read them from
  doccheck.py --old-ids FILE       also: no page cites a commit id listed in FILE (one a line)

It reads; it changes nothing.
"""

from pathlib import Path
import argparse
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
import docs  # noqa: E402


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--ref')
    parser.add_argument('--staged', action='store_true')
    parser.add_argument('--dir')
    parser.add_argument('--git', help='with --dir: the clone whose branches the links are read against')
    parser.add_argument('--register')
    parser.add_argument('--old-ids')
    parser.add_argument('--only')
    parser.add_argument('--todo', action='store_true')
    args = parser.parse_args(argv)
    settings = docs.SETTINGS
    if not settings.get('pages'):
        print('doccheck: [docs] pages is not set in method.toml: nothing was read', file=sys.stderr)
        return 1
    cwd = args.git
    if args.dir:
        tree = docs.Tree(directory=args.dir)
    elif args.staged:
        tree = docs.Tree(staged=True)
    else:
        ref = args.ref
        if not ref:
            branches = [name for name in settings.get('branches', []) if '*' not in name]
            ref = f'origin/{branches[0]}' if branches else 'HEAD'
        if docs.git('rev-parse', '-q', '--verify', f'{ref}^{{commit}}').returncode != 0:
            print(f'doccheck: {ref} is not in this clone: nothing was read', file=sys.stderr)
            return 1
        tree = docs.Tree(ref=ref)
    only = [name.strip() for name in args.only.split(',')] if args.only else None
    unknown = [name for name in (only or []) if name not in docs.CHECKS]
    if unknown:
        print(f'doccheck: no such check: {", ".join(unknown)} (the checks: {", ".join(docs.CHECKS)})',
              file=sys.stderr)
        return 1
    problems, notes, counts = docs.check(tree, only=only, cwd=cwd, register=args.register,
                                         old_ids=args.old_ids or settings.get('old_ids') or None)
    print(f'doccheck: {tree.label()}: {counts["pages"]} pages, {counts.get("foreign", 0)} other files, '
          f'{counts["links"]} links read; {len(notes)} TODO marker(s); {len(problems)} problem(s)')
    for problem in problems:
        print(f'  - {problem}')
    if args.todo:
        for note in notes:
            print(f'  todo: {note}')
    return 1 if problems else 0


if __name__ == '__main__':
    sys.exit(main())
