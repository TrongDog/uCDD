#!/usr/bin/env python3
"""import_hardware.py: a hardware measurement from the PC into the bench.

    python3 METHOD/tools/import_hardware.py TCTABLE.TXT --card ct2291 --source TEXT
        [--out FILE] [--compare formula|sb16]

TCTABLE.TXT is TCTABLE.EXE's output (AKIT; the bench's T2.EXE TCTABLE case
prints the same lines): one line a time constant, "TC xxh: R.R Hz (n blocks;
the formula F Hz)", or "TC xxh: no block interrupt within 2 s". The measured
rate of every constant goes into one JSON file with its provenance (the
card, the source given, the input's sha256, the date):

    {"card": ..., "source": ..., "sha256": ..., "imported": ...,
     "rates": {"0": 3739.1, ...}, "silent": [...], "one_block": [...]}

written by default to the bench's runs/rec/hw/tctable-CARD.json. tonecheck
reads tctable-ct2291.json, when it is there, as the hardware-grade table for
every pitch on the virtual SB16 (the owner, 28 Oct 2026, question 30), in place
of the DSP 4.13 firmware's.

--compare prints, against the formula 1000000/(256-TC) or the 4.13 firmware
table (tonecheck's SB16_TIME_TABLE), the constants that differ by more than
0.2 % and the largest difference; the bench's own runs of the case (86Box's
card on C0, uCDD's on C2) are checked that way before a hardware file is
trusted. Nothing is written with --compare unless --out is given too.

    python3 METHOD/tools/import_hardware.py akit SENDOUT_FOLDER [--out FOLDER]

AKIT's results as SENDOUT brought them back (the retronet inbox's AKIT
folder: the kit's RESULTS), into the bench's results/hardware/AKIT/<date>/
(project_a.md A7 4: "import_hardware.py to ingest SENDOUT's results into
[the bench's] results/hardware/ and mark CONFIRMED_*"; the owner's ear is a hardware
result, CONTEXT.md). The folder's CASES.TXT names each case's matrix row and
the bench's verdict, ENTRIES.TXT each game entry, HEARD.TXT the owner's Y or
N; each case's own file is its program's lines. A case is read against the
kit's try in 86Box where CASES.TXT carries it (its "86Box try" column: the same
command, the program's words alone, as the PC gives them), else against the
ledger's verdict on its row (which, for a row that records, holds tonecheck's
reading of the sound too). Marks, a case: CONFIRMED_PASS or CONFIRMED_FAIL
(the PC's program reads as the bench: a part A case is the bare CT2291 against
86Box's card), HW_DIFFERS (it reads otherwise),
HW_ONLY (the bench has no verdict on the row: a held row, or none), NO_VERDICT
(no PASS or FAIL line), NOT_RUN (no file), HW_TABLE (TCTABLE's lines, kept:
the time-constant table is imported on its own, above, never from here, since
tonecheck reads it). A game entry: CONFIRMED_FAULT or NOT_CONFIRMED (a fault
entry heard or not), CONFIRMED_WORKS or HW_FAULT (a passing game's entry heard
working or not), NOT_ASKED (not by ear), NOT_PLAYED (? or no line). A case's
HEARD line (B12, D12: the tone) is kept with the case. Every input file is
copied beside hardware.json with its sha256; written through PATH.part and a
rename. tests/test_import_akit.py is its test.
decides: silent: project_a.md A7 4 (the charter's AKIT and its importer); no
reference document decides a kit's marks
lessons_read (11 Nov 2026, AKIT) = "terms: kit, retronet, publish, hardware, games, readme, import, listen; lessons: L4, L7, L20, L5, L8, L19, L17, L15, L22, L49, L12, L24, L26, L52, L23; 11 Nov 2026"
"""

from pathlib import Path
import argparse
import collections
import datetime
import hashlib
import json
import re
import sys

METHOD = Path(__file__).resolve().parent.parent
BENCH = METHOD.parent.parent.parent          # the bench: runs/src/method -> the bench
LINE = re.compile(r'TC ([0-9A-F]{2})h: (?:([0-9]+\.[0-9]) Hz|(no block interrupt)|(one block only))')


def parse(text):
    rates, silent, one = {}, [], []
    for m in LINE.finditer(text):
        tc = int(m.group(1), 16)
        if m.group(2):
            rates[tc] = float(m.group(2))
        elif m.group(3):
            silent.append(tc)
        else:
            one.append(tc)
    return rates, silent, one


def sb16_table():
    sys.path.insert(0, str(BENCH / 'runs' / 'rec'))
    import tonecheck
    return lambda tc: tonecheck.SB16_TIME_TABLE[min(tc, 0xeb)] * 4096 / 23


def compare(rates, against):
    model = (lambda tc: 1000000 / (256 - tc)) if against == 'formula' else sb16_table()
    worst, off = 0.0, []
    for tc, rate in sorted(rates.items()):
        due = model(tc)
        dev = abs(rate - due) / due * 100
        worst = max(worst, dev)
        if dev > 0.2:
            off.append('%02Xh %.1f against %.1f (%.2f %%)' % (tc, rate, due, dev))
    print('%d constants measured; against the %s: %d differ by more than 0.2 %%, the largest %.3f %%'
          % (len(rates), against, len(off), worst))
    for line in off:
        print('  ' + line)
    return not off


def tab_rows(path):
    """The rows of a tab-separated file with a header line (DOS line ends allowed)."""
    lines = [l.rstrip('\r') for l in path.read_text(errors='replace').split('\n') if l.strip()]
    head = lines[0].split('\t')
    return [dict(zip(head, l.split('\t'))) for l in lines[1:]]


def bench_word(text):
    """The bench's verdict from CASES.TXT's words: 'pass', 'fail', 'split' or None (no verdict)."""
    words = set(re.findall(r'\b(pass|fail) \d+', text))
    return None if not words else words.pop() if len(words) == 1 else 'split'


def case_mark(text, bench):
    """(the PC's word, the mark) of a case's own lines against the bench's verdict."""
    lines = [l.strip() for l in text.split('\n')]
    if any(LINE.match(l) for l in lines):
        return 'table', 'HW_TABLE'
    pc = ('fail' if any(l.startswith('FAIL ') for l in lines) else
          'pass' if any(l.startswith('PASS ') for l in lines) else None)
    if pc is None:
        return None, 'NO_VERDICT'
    if bench not in ('pass', 'fail'):
        return pc, 'HW_ONLY'
    return pc, 'CONFIRMED_%s' % pc.upper() if pc == bench else 'HW_DIFFERS'


ENTRY_MARKS = {('fault', 'Y'): 'CONFIRMED_FAULT', ('fault', 'N'): 'NOT_CONFIRMED',
               ('pass', 'Y'): 'CONFIRMED_WORKS', ('pass', 'N'): 'HW_FAULT'}


def akit(folder, out=None):
    """AKIT's results (the docstring) into OUT, by default the bench's results/hardware/AKIT/<date>/."""
    folder = Path(folder)
    for need in ('CASES.TXT', 'ENTRIES.TXT', 'HEARD.TXT'):
        if not (folder / need).exists():
            sys.exit('import_hardware akit: %s has no %s: not AKIT\'s RESULTS' % (folder, need))
    heard = {}
    for l in (folder / 'HEARD.TXT').read_text(errors='replace').split('\n')[1:]:
        m = re.match(r'\s*(\w+)\s+([YyNn?])(?=\s|$)\s*(.*)', l)
        if m:
            heard[m.group(1).upper()] = (m.group(2).upper(), m.group(3).strip())
    cases = []
    for c in tab_rows(folder / 'CASES.TXT'):
        f = folder / ('%s.TXT' % c['case'])
        tried = re.match(r'(PASS|FAIL): ', c.get('86Box try', ''))     # the kit's try in 86Box: the same command
        bench = tried.group(1).lower() if tried else bench_word(c.get('the bench', ''))
        if not f.exists():
            pc, mark = None, 'NOT_RUN'
        else:
            pc, mark = case_mark(f.read_text(errors='replace').replace('\r', ''), bench)
        cases.append({'case': c['case'], 'part': c['part'], 'row': c['row'], 'command': c['command'],
                      'bench': c.get('the bench', ''), 'tried': c.get('86Box try', ''),
                      'against': 'the 86Box try' if tried else 'the ledger', 'pc': pc, 'mark': mark,
                      'heard': heard.get(c['case'].upper())})
    entries = []
    for e in tab_rows(folder / 'ENTRIES.TXT'):
        h = heard.get(e['entry'])
        if e['kind'] == 'notbyear':
            mark = 'NOT_ASKED'
        elif not h or h[0] == '?':
            mark = 'NOT_PLAYED'
        else:
            mark = ENTRY_MARKS[(e['kind'], h[0])]
        entries.append(dict(e, heard=h, mark=mark))
    day = datetime.datetime.now(datetime.timezone.utc)
    out = Path(out) if out else BENCH / 'results' / 'hardware' / 'AKIT' / day.strftime('%Y%m%d')
    out.mkdir(parents=True, exist_ok=True)
    inputs = {}
    for f in sorted(folder.iterdir()):
        if f.is_file():
            raw = f.read_bytes()
            inputs[f.name] = hashlib.sha256(raw).hexdigest()
            (out / (f.name + '.part')).write_bytes(raw)
            (out / (f.name + '.part')).replace(out / f.name)
    counts = {'cases': dict(sorted(collections.Counter(c['mark'] for c in cases).items())),
              'entries': dict(sorted(collections.Counter(e['mark'] for e in entries).items()))}
    record = {'kit': 'AKIT', 'imported': day.isoformat(timespec='seconds'), 'from': folder.name, 'inputs': inputs,
              'counts': counts, 'cases': cases, 'entries': entries}
    part = out / 'hardware.json.part'
    part.write_text(json.dumps(record, indent=1) + '\n')
    part.replace(out / 'hardware.json')
    print('import_hardware akit: %d cases %s; %d entries %s; written: %s' % (
        len(cases), counts['cases'], len(entries), counts['entries'], out / 'hardware.json'))
    return 0


def main():
    if sys.argv[1:2] == ['akit']:
        ap = argparse.ArgumentParser(description='AKIT\'s results into the bench (the docstring)')
        ap.add_argument('akit')
        ap.add_argument('folder')
        ap.add_argument('--out')
        a = ap.parse_args()
        return akit(a.folder, a.out)
    ap = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    ap.add_argument('file')
    ap.add_argument('--card', required=True, help='the card measured, e.g. ct2291, es1868')
    ap.add_argument('--source', help='where the file came from (kit, run, date)')
    ap.add_argument('--out')
    ap.add_argument('--compare', choices=('formula', 'sb16'))
    a = ap.parse_args()
    raw = Path(a.file).read_bytes()
    rates, silent, one = parse(raw.decode('ascii', 'replace'))
    print('%s: %d rates, %d silent, %d one block only' % (a.file, len(rates), len(silent), len(one)))
    ok = True
    if a.compare:
        ok = compare(rates, a.compare)
    if a.out or not a.compare:
        if not a.source:
            sys.exit('import_hardware: --source is required to write a hardware table (its provenance)')
        out = Path(a.out) if a.out else BENCH / 'runs' / 'rec' / 'hw' / ('tctable-%s.json' % a.card)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps({
            'card': a.card, 'source': a.source, 'sha256': hashlib.sha256(raw).hexdigest(),
            'imported': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
            'rates': {str(tc): rate for tc, rate in sorted(rates.items())},
            'silent': silent, 'one_block': one}, indent=1) + '\n')
        print('written: %s' % out)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
