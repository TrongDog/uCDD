#!/usr/bin/env python3
"""import_hardware.py akit: AKIT's results into the bench, each case and game entry marked (project_a.md A7 4).

    python3 METHOD/tests/test_import_akit.py
    UCDD_IMPORT_UNDER_TEST=OLD/tools/import_hardware.py python3 METHOD/tests/test_import_akit.py   the known-bad

A made-up RESULTS folder as SENDOUT brings it back, DOS line ends: CASES.TXT with seven cases (a C0 case the bench
passed, a pin case the 86Box try failed and the ledger passed, a held row with no ledger entry, TCTABLE, a case with no
file, a case whose file holds no PASS or FAIL line, a case the ledger failed on its sound and the try passed), their
files (the pin case passing on the PC: it differs from the try; the last passing: it agrees with the try), ENTRIES.TXT with six entries
(two faults, two passing games, one not by ear, one unplayed) and HEARD.TXT (Y, N, the tone line B02, a ? line).
1. Each case's mark: CONFIRMED_PASS, HW_DIFFERS (read against the try, not the ledger), HW_ONLY, HW_TABLE, NOT_RUN,
   NO_VERDICT, CONFIRMED_PASS (the try governs); B02's tone kept with it.
2. Each entry's mark: CONFIRMED_FAULT, NOT_CONFIRMED, CONFIRMED_WORKS, HW_FAULT, NOT_ASKED, NOT_PLAYED.
3. Every input file copied beside hardware.json with its sha256; no .part file left.
The known-bad (L4): import_hardware.py before this change (its HEAD copy beside the live lib): it has no akit form and
refuses the call (argparse: --card is required), so 1 to 3 fail.

decides = "silent: project_a.md A7 4 (\"import_hardware.py to ingest SENDOUT's results into [the bench's] results/hardware/ and mark CONFIRMED_*\"); no reference document decides a kit's marks"
lessons_read = "terms: kit, retronet, publish, hardware, games, readme, import, listen; lessons: L4, L7, L20, L5, L8, L19, L17, L15, L22, L49, L12, L24, L26, L52, L23; 11 Nov 2026"
"""

from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
TOOL = Path(os.environ.get('UCDD_IMPORT_UNDER_TEST') or PACKAGE / 'tools' / 'import_hardware.py')
CASES = ('case\tpart\trow\tcommand\tthe bench\t86Box try\n'
         'A01\tA\tT2C0-S16ODD2\tT2.EXE S16ODD2 C0\tplan 11111111: pass 10\tnot tried\n'
         'B01\tB\tT2X-S16ODD2\tT2.EXE S16ODD2\tplan 22222222: pass 10\tFAIL: S16ODD2 the channels swap\n'
         'B02\tB\tT2X-SC8PAGE2\tT2.EXE SC8PAGE2\tno ledger entry (a held row: the CT2291 judges it)\tnot tried\n'
         'A10\tA\tTCTABLE (T2X-TCROUND\'s judge)\tTCTABLE.EXE\tno ledger entry\ttable (2 lines)\n'
         'B03\tB\tT2X-DMAMCR\tT2.EXE DMAMCR\tplan 33333333: fail 12\tFAIL: DMAMCR\n'
         'B04\tB\tT2X-DAC\tT2.EXE DAC 8000\tplan 44444444: fail 20, pass 20\tPASS: DAC\n'
         'B05\tB\tT2X-S16ON8\tT2.EXE S16ON8\tplan 55555555: fail 12\tPASS: S16ON8 (the sound failed tonecheck)\n')
FILES = {'A01.TXT': 'PASS S16ODD2 C0: the second block starts on its own channel\n',
         'B01.TXT': 'PASS S16ODD2: the second block starts on its own channel\n',
         'B02.TXT': 'FAIL SC8PAGE2: the block went on past the page\n',
         'A10.TXT': 'TC 00h: 3906.2 Hz (4 blocks; the formula 3906.3 Hz)\nTC 01h: 3921.6 Hz (4 blocks; the formula '
                    '3921.6 Hz)\n',
         'B04.TXT': 'T2: no card found\n',
         'B05.TXT': 'TICK BEEP 1\nPASS S16ON8 each format\n'}
ENTRIES = ('entry\tkind\tpart\treport\tgame\tbuild\tbench bin\tbench measure\n'
           '1\tfault\tB\tFAM-6\tDOS_THNK/TRANSPOR\tpin\tCANDIDATE_UCDD_HOST\tstate\n'
           '2\tfault\tD\tFAM-3\tDOS_THNK/TRANSPOR\ta2\tCANDIDATE_UCDD_HOST\tstate\n'
           '3\tpass\tB\tcell x\tDOS_ACT/GREATESC\tpin\tPASS\t\n'
           '4\tpass\tB\tcell y\tDOS_ACT/OTHER\tpin\tPASS\t\n'
           '5\tnotbyear\tB\tFAM-1\tDOS_ACT/BLUBROJA\tpin\tCANDIDATE_UCDD_LEVEL\tlevel\n'
           '6\tfault\tB\tFAM-10\tDOS_ACT/DESERT\tpin\tCANDIDATE_UCDD_SFX\tsound\n')
HEARD = ('AKIT: Y or N after each number you played (then any words); ? if not played.\n'
         'B02 Y it broke up twice\n1 Y it hung at the menu\n2 n ran fine\n3 y\n4 N silent all through\n6 ?\n')


class AkitImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='import-akit-')
        self.root = Path(self.tmp.name)
        self.src = self.root / 'AKIT'
        self.src.mkdir()
        for name, text in [('CASES.TXT', CASES), ('ENTRIES.TXT', ENTRIES), ('HEARD.TXT', HEARD)] + list(FILES.items()):
            (self.src / name).write_bytes(text.replace('\n', '\r\n').encode())
        self.out = self.root / 'out'
        self.done = subprocess.run([sys.executable, str(TOOL), 'akit', str(self.src), '--out', str(self.out)],
                                   capture_output=True, text=True)
        path = self.out / 'hardware.json'
        self.record = json.loads(path.read_text()) if path.exists() else {'cases': [], 'entries': [], 'inputs': {}}

    def tearDown(self):
        self.tmp.cleanup()

    def test_1_cases(self):
        marks = {c['case']: c['mark'] for c in self.record['cases']}
        self.assertEqual(marks, {'A01': 'CONFIRMED_PASS', 'B01': 'HW_DIFFERS', 'B02': 'HW_ONLY', 'A10': 'HW_TABLE',
                                 'B03': 'NOT_RUN', 'B04': 'NO_VERDICT', 'B05': 'CONFIRMED_PASS'}, self.done.stderr[-300:])
        b02 = next((c for c in self.record['cases'] if c['case'] == 'B02'), {})
        self.assertEqual(b02.get('heard'), ['Y', 'it broke up twice'])

    def test_2_entries(self):
        marks = {e['entry']: e['mark'] for e in self.record['entries']}
        self.assertEqual(marks, {'1': 'CONFIRMED_FAULT', '2': 'NOT_CONFIRMED', '3': 'CONFIRMED_WORKS',
                                 '4': 'HW_FAULT', '5': 'NOT_ASKED', '6': 'NOT_PLAYED'}, self.done.stderr[-300:])

    def test_3_inputs(self):
        names = sorted(p.name for p in self.src.iterdir())
        self.assertEqual(sorted(self.record['inputs']), names)
        for n in names:
            self.assertEqual(self.record['inputs'][n], hashlib.sha256((self.out / n).read_bytes()).hexdigest())
        self.assertEqual([p.name for p in self.out.iterdir() if p.name.endswith('.part')], [])


if __name__ == '__main__':
    unittest.main(verbosity=1)
