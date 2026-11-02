#!/usr/bin/env python3
"""Read the lessons register before the work it governs (r3.8).

    python3 METHOD/tools/lessons_recall.py TERM [TERM ...] [--register FILE] [--line]
    python3 METHOD/tools/lessons_recall.py check [--register FILE] [--state FILE]

The register is context/LESSONS.md in the top folder (the agent's own
lessons.py reads and rewrites it; this tool only reads it, with the same
line forms, so the two never disagree about what a lesson is).

TERMS: prints every lesson whose Short, Tags, Recall or Rule line holds a
term (case-insensitive), heaviest first, with its guard, then the line a
STATE gate row or a new tool's header carries:

    lessons_read = "terms: record, batch, 86Box; lessons: L6, L9, L39; 2 Nov 2026"

That line is what "the lessons were read first" means. Without it, "read
first" is a claim from memory, the same failure L35 closed for the library.

check: reads STATE.md for gate rows (lines starting "| A" or "| T" in the
Project A and Tightening tables) whose status is IN_PROGRESS and that carry
no lessons_read line in the same row or the row after; and reads the
register's hit lines for the "read:" field (r3.8): a relearned hit marked
"read: no" is a reading failure, "read: yes" a guard failure, unmarked is
unknown. It prints the counts and exits 1 if any IN_PROGRESS gate lacks its
line. The hit line form stays as lessons.py parses it; the field is a
suffix the old parser folds into the hit's text:

    - 2 Nov | 2 | relearned | plan_run ran with the recompiler on | read: no
"""

from pathlib import Path
import argparse
import datetime
import re
import sys

TOP = Path(__file__).resolve()
DEFAULT_REGISTER = None
for parent in TOP.parents:
    candidate = parent / 'context' / 'LESSONS.md'
    if candidate.exists():
        DEFAULT_REGISTER = candidate
        break

HIT = re.compile(r'^  - (.+?) \| (\d) \| (\w+) \| (.*)$')
READ = re.compile(r'\|\s*read:\s*(yes|no)\s*$', re.I)
FACTORS = {'first': 1, 'applied': 1, 'relearned': 2}


def read_register(path):
    lessons, cur = [], None
    for line in Path(path).read_text().splitlines():
        m = re.match(r'### (L\d+)\. (.*)', line)
        if m:
            cur = dict(id=m.group(1), title=m.group(2), short='', tags=[], recall='', guard='none',
                       rule='', hits=[])
            lessons.append(cur)
            continue
        if cur is None:
            continue
        m = re.match(r'- (Short|Tags|Recall|Guard|Rule|Work): (.*)', line)
        if m:
            key, val = m.group(1).lower(), m.group(2).strip()
            cur[key] = [t.strip() for t in val.split(',')] if key == 'tags' else val
            continue
        m = HIT.match(line)
        if m:
            date, sev, kind, text = m.group(1), int(m.group(2)), m.group(3), m.group(4)
            r = READ.search(text)
            cur['hits'].append(dict(date=date, sev=sev, kind=kind, text=text,
                                    read=(r.group(1).lower() if r else None)))
    for l in lessons:
        l['weight'] = sum(h['sev'] * FACTORS.get(h['kind'], 1) for h in l['hits'])
        l['level'] = l['guard'].split(':')[0].strip().split()[0] if l['guard'] else 'none'
    lessons.sort(key=lambda l: (-l['weight'], int(l['id'][1:])))
    return lessons


def matching(lessons, terms):
    pats = [re.compile(re.escape(t), re.I) for t in terms]
    out = []
    for l in lessons:
        hay = ' '.join([l['short'], l['title'], ' '.join(l['tags']), l['recall'], l['rule']])
        if any(p.search(hay) for p in pats):
            out.append(l)
    return out


def read_line(terms, found):
    today = datetime.date.today().strftime('%-d %b %Y')
    ids = ', '.join(l['id'] for l in found) or 'none'
    return f'lessons_read = "terms: {", ".join(terms)}; lessons: {ids}; {today}"'


def check_state(state_path, lessons):
    text = Path(state_path).read_text().splitlines() if state_path and Path(state_path).exists() else []
    missing = []
    for i, line in enumerate(text):
        cells = line.split('|')
        # the status cell only: a row keeps its history inline ("PASS (...). Before: IN_PROGRESS")
        if re.match(r'^\|\s*[AT]\d', line) and len(cells) > 2 and cells[2].strip().startswith('IN_PROGRESS'):
            window = line + ' ' + (text[i + 1] if i + 1 < len(text) else '')
            if 'lessons_read' not in window:
                missing.append(line.split('|')[1].strip())
    reading, guard, unknown = 0, 0, 0
    for l in lessons:
        for h in l['hits']:
            if h['kind'] != 'relearned':
                continue
            if h['read'] == 'no':
                reading += 1
            elif h['read'] == 'yes':
                guard += 1
            else:
                unknown += 1
    return missing, reading, guard, unknown


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('terms', nargs='*')
    parser.add_argument('--register', default=str(DEFAULT_REGISTER) if DEFAULT_REGISTER else None)
    parser.add_argument('--state')
    parser.add_argument('--line', action='store_true', help='print the lessons_read line only')
    args = parser.parse_args()
    if not args.register or not Path(args.register).exists():
        sys.exit('lessons_recall: no register (give --register context/LESSONS.md)')
    lessons = read_register(args.register)
    if args.terms and args.terms[0] == 'check':
        state = args.state or str(Path(args.register).parent / 'STATE.md')
        missing, reading, guard, unknown = check_state(state, lessons)
        print(f'relearned hits: {reading} reading failures (read: no), {guard} guard failures (read: yes), '
              f'{unknown} unmarked')
        if missing:
            print('IN_PROGRESS gates without a lessons_read line: ' + ', '.join(missing))
            return 1
        print('every IN_PROGRESS gate carries its lessons_read line')
        return 0
    if not args.terms:
        parser.error('give terms, or "check"')
    found = matching(lessons, args.terms)
    if not args.line:
        for l in found:
            print(f'{l["id"]:<4} W{l["weight"]:>3}  guard {l["level"]:<8} {l["short"]}')
            if l['recall']:
                print(f'           recall: {l["recall"]}')
        print()
    print(read_line(args.terms, found))
    return 0


if __name__ == '__main__':
    sys.exit(main())
