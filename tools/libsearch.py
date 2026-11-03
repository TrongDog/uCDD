#!/usr/bin/env python3
"""Search the whole reference library before a row says "silent".

    python3 METHOD/tools/libsearch.py TERM [TERM ...] [--all] [--max N] [--searched]
    python3 METHOD/tools/libsearch.py --coverage
    python3 METHOD/tools/libsearch.py --recheck [MATRIX]

Every text file in the reference worktree ([references].worktree) and the
fork's own specifications on the row refs (docs/*.md) is searched,
case-insensitively, for lines holding any TERM (--all: every TERM on the
line). Hits print as KEY:line: text where the file has a key, else as
path:line: text. At the end, one summary line per document with its count.

What counts as a text file (r3.9): any file whose first 64 KB holds no NUL
byte and under 1 % control characters. r3.7 chose files by ending (.txt,
.md, .asm, .inc, .h, .c), which left Ralf Brown's Interrupt List unread but
for INTERRUP.C and INTERRUP.H, whose endings passed as C (question 54,
3 Nov 2026): 32 files, about 7 MB, including INT 13h and the port list.
Every "silent" searched while that held is rechecked with --recheck.

A PDF is never read; it is searched through the extraction beside it
(NAME.txt next to NAME.pdf). A PDF without one is reported by --coverage
as unsearched, and the library is not fully searched until it has one.

--coverage lists every file in the library as searched or skipped, with the
reason, and the totals; it exits 1 when a document is unsearched.

--recheck re-runs the search for every row of the matrix that carries a
searched line, with the terms that line records, and prints the rows whose
hit count rose, with the documents that now hit. It changes nothing.

--searched prints the line a row carries in place of a search nobody can
check (r3.7):

    searched = "terms: first byte, silent byte, stereo; hits: 14 in 3 documents (SBG 9, ES1868 4, SB202SPEC 1); 28 Oct 2026"

A row whose decides says "silent" must carry that line; plan.py check
refuses one without it once [matrix].searched_required is on. The point is
not the format: it is that "silent" means "searched and not found", never
"I did not need to look". PICHOLD12's D3h sat in two chipset sheets for 29
hours under a silent that was never searched (LIBAUDIT, 28 Oct 2026).
"""

from pathlib import Path
import argparse
import datetime
import re
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
import methodlib  # noqa: E402
import refcheck  # noqa: E402



def _readable(key):
    """Sort key: a name without trailing underscores first, then the shortest, then alphabetical.
    The key table may hold two names for one file (an alias kept for old citations beside a
    readable name, r3.9); hits print the readable one."""
    return (key.endswith('_'), len(key), key)


BY_FILE = {}
for _key in sorted(refcheck.KEYS, key=_readable, reverse=True):
    BY_FILE[refcheck.KEYS[_key]] = _key
ROW_REFS = list(methodlib.CONFIG.get('rows', {}).get('refs', []))
SNIFF = 65536
CONTROL = bytes(c for c in range(32) if c not in (9, 10, 12, 13, 27))
SEARCHED_FORM = re.compile(r'terms:\s*(?P<terms>.*?);\s*hits:\s*(?P<hits>\d+)\s+in\s+(?P<docs>\d+)', re.I)


def classify(path):
    """('text', '') | ('skip', reason) | ('unsearched', reason) for one library file."""
    suffix = path.suffix.lower()
    if suffix == '.pdf':
        if path.with_suffix('.txt').is_file():
            return 'skip', 'pdf; searched through its extraction'
        return 'unsearched', 'pdf without an extraction beside it'
    try:
        with open(path, 'rb') as file:
            head = file.read(SNIFF)
    except OSError as error:
        return 'unsearched', f'unreadable: {error.strerror}'
    if b'\0' in head:
        return 'skip', 'binary: NUL bytes'
    if head and sum(head.count(c) for c in CONTROL) > len(head) * 0.01:
        return 'skip', 'binary: control characters'
    return 'text', ''


def library_files(tree):
    for path in sorted(tree.rglob('*')):
        if path.is_file() and '.git' not in path.parts and classify(path)[0] == 'text':
            yield path


def coverage(tree):
    """[(state, reason, path)] for every file in the library."""
    rows = []
    for path in sorted(tree.rglob('*')):
        if path.is_file() and '.git' not in path.parts:
            state, reason = classify(path)
            rows.append((state, reason, path))
    return rows


def key_of(tree, path):
    rel = str(path.relative_to(tree)) if tree in path.parents else str(path)
    return BY_FILE.get(rel, rel)


def search_file(path, terms, need_all, limit):
    pattern = [re.compile(re.escape(t), re.I) for t in terms]
    hits = []
    try:
        with open(path, errors='replace') as file:
            for number, line in enumerate(file, 1):
                found = [bool(p.search(line)) for p in pattern]
                if (all(found) if need_all else any(found)):
                    hits.append((number, line.rstrip()[:140]))
                    if len(hits) >= limit:
                        break
    except OSError:
        pass
    return hits


def row_ref_docs(terms, need_all, limit):
    """docs/*.md on the row refs (the fork's own specifications), via git show."""
    out = {}
    seen = set()
    for ref in ROW_REFS:
        listed = subprocess.run(['git', 'ls-tree', '--name-only', '-r', ref, '--', 'docs'],
                                capture_output=True, text=True)
        for name in listed.stdout.split():
            if not name.endswith('.md') or name in seen:
                continue
            seen.add(name)
            shown = subprocess.run(['git', 'show', f'{ref}:{name}'], capture_output=True, text=True,
                                   errors='replace')
            if shown.returncode:
                continue
            pattern = [re.compile(re.escape(t), re.I) for t in terms]
            hits = []
            for number, line in enumerate(shown.stdout.splitlines(), 1):
                found = [bool(p.search(line)) for p in pattern]
                if (all(found) if need_all else any(found)):
                    hits.append((number, line.rstrip()[:140]))
                    if len(hits) >= limit:
                        break
            if hits:
                out[BY_FILE.get(name, name)] = hits
    return out


def search(terms, need_all=False, limit=20):
    tree = refcheck.worktree()
    results = {}
    if tree and tree.is_dir():
        for path in library_files(tree):
            hits = search_file(path, terms, need_all, limit)
            if hits:
                results[key_of(tree, path)] = hits
    results.update(row_ref_docs(terms, need_all, limit))
    return results


def searched_line(terms, results):
    total = sum(len(h) for h in results.values())
    top = sorted(results.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:6]
    docs = ', '.join(f'{key} {len(hits)}' for key, hits in top)
    today = datetime.date.today().strftime('%-d %b %Y')
    return (f'searched = "terms: {", ".join(terms)}; hits: {total} in {len(results)} documents'
            f'{" (" + docs + ")" if docs else ""}; {today}"')


def parse_searched(text):
    """(terms, hits, documents) from a row's searched line, or None."""
    found = SEARCHED_FORM.search(str(text))
    if not found:
        return None
    terms = [t.strip() for t in found.group('terms').split(',') if t.strip()]
    return terms, int(found.group('hits')), int(found.group('docs'))


def recheck(matrix_path, limit=20):
    """Rows whose searched line records fewer hits than the library now gives."""
    import tomllib
    matrix = tomllib.loads(Path(matrix_path).read_text())
    rows = []
    for entry in matrix.get('test', []):
        parsed = parse_searched(entry.get('searched', ''))
        if not parsed:
            continue
        terms, old_hits, old_docs = parsed
        results = search(terms, False, limit)
        new_hits = sum(len(h) for h in results.values())
        rows.append((entry.get('name', '?'), terms, old_hits, old_docs, new_hits, results))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('terms', nargs='*')
    parser.add_argument('--all', action='store_true', help='every term on the line, not any')
    parser.add_argument('--max', type=int, default=20, help='hits per document to print')
    parser.add_argument('--searched', action='store_true', help='print the row line only')
    parser.add_argument('--coverage', action='store_true', help='list every library file as searched or skipped')
    parser.add_argument('--recheck', nargs='?', const='', metavar='MATRIX',
                        help='re-run every searched line of the matrix (default METHOD/matrix/matrix.toml)')
    args = parser.parse_args()

    if args.coverage:
        tree = refcheck.worktree()
        if not tree or not tree.is_dir():
            print('no reference worktree ([references].worktree)')
            return 1
        rows = coverage(tree)
        counts = {'text': 0, 'skip': 0, 'unsearched': 0}
        sizes = {'text': 0, 'skip': 0, 'unsearched': 0}
        for state, reason, path in rows:
            counts[state] += 1
            sizes[state] += path.stat().st_size
            if state != 'text':
                print(f'{state:10} {path.relative_to(tree)}  ({reason})')
        print(f'searched {counts["text"]} files, {sizes["text"] // 1024} KB; '
              f'skipped {counts["skip"]}, {sizes["skip"] // 1024} KB; '
              f'unsearched {counts["unsearched"]}, {sizes["unsearched"] // 1024} KB')
        return 1 if counts['unsearched'] else 0

    if args.recheck is not None:
        matrix_path = args.recheck or str(Path(__file__).resolve().parent.parent / 'matrix' / 'matrix.toml')
        rows = recheck(matrix_path, args.max)
        rose = 0
        for name, terms, old_hits, old_docs, new_hits, results in rows:
            if new_hits > old_hits:
                rose += 1
                docs = '; '.join(f'{key} {len(hits)}' for key, hits in
                                 sorted(results.items(), key=lambda kv: (-len(kv[1]), kv[0])))
                print(f'{name}: hits {old_hits} -> {new_hits}  terms: {", ".join(terms)}  now in: {docs}')
        print(f'{len(rows)} searched lines rechecked; {rose} rose')
        return 0

    if not args.terms:
        parser.error('TERM needed (or --coverage / --recheck)')
    results = search(args.terms, args.all, args.max)
    if args.searched:
        print(searched_line(args.terms, results))
        return 0
    for key, hits in sorted(results.items(), key=lambda kv: (-len(kv[1]), kv[0])):
        for number, text in hits:
            print(f'{key}:{number}: {text}')
    print()
    if not results:
        print(f'no hits for: {", ".join(args.terms)}')
    else:
        print('; '.join(f'{key} {len(hits)}' for key, hits in sorted(results.items(), key=lambda kv: -len(kv[1]))))
    print(searched_line(args.terms, results))
    return 0


if __name__ == '__main__':
    sys.exit(main())
