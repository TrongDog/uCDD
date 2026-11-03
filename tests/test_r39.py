#!/usr/bin/env python3
"""Tightening r3.9: the library search reads every text file, whatever its ending.

    python3 METHOD/tests/test_r39.py

1. A file is searched by what it holds, not by its ending: INTERRUP.A,
   PORTS.B, TABLES.LST and even a text file named INTERRUP.O are text; a
   file with NUL bytes is not; a PDF is searched through the extraction
   beside it and reported unsearched without one (question 54, 3 Nov 2026).
2. --recheck re-runs a row's searched line and reports a rise when the
   library now holds the term.
3. When the key table names one file twice, hits print the readable name,
   not the one that ends in underscores.
4. In the installed method.toml, no file keyed only by an underscore-ended
   name is left without a readable key (RBIL_A .. RBIL_R, RBIL_PRI,
   PORTS_A .. PORTS_C).
"""

from pathlib import Path
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
sys.path.insert(0, str(PACKAGE / 'lib'))
sys.path.insert(0, str(PACKAGE / 'tools'))

import libsearch  # noqa: E402
import refcheck  # noqa: E402


def plant(tree):
    rbil = tree / "Ralf Brown's Interrupt List"
    rbil.mkdir()
    (rbil / 'INTERRUP.A').write_bytes(b'Interrupt List\r\n\x0c--------D-1300-------------------------------\r\nINT 13 - DISK - RESET DISK SYSTEM\r\n')
    (rbil / 'INTERRUP.O').write_bytes(b'INT 7A - plain text in a file named like an object file\r\n')
    (rbil / 'PORTS.B').write_bytes(b'PORT 0220-022F - SOUND BLASTER\r\n')
    (rbil / 'TABLES.LST').write_bytes(b'Table 00001\r\n')
    (tree / 'Chips').mkdir()
    (tree / 'Chips' / 'sheet.pdf').write_bytes(b'%PDF-1.4\n\x00\x00binary\n')
    (tree / 'Chips' / 'sheet.txt').write_text('extracted: the PIIX3 DMA page registers\n')
    (tree / 'Chips' / 'lonely.pdf').write_bytes(b'%PDF-1.4\n\x00\x00binary\n')
    (tree / 'Chips' / 'firmware.bin').write_bytes(bytes(range(256)) * 4)


class Sniff(unittest.TestCase):
    def test_text_by_content_not_ending(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp)
            plant(tree)
            names = sorted(p.name for p in libsearch.library_files(tree))
            self.assertEqual(names, ['INTERRUP.A', 'INTERRUP.O', 'PORTS.B', 'TABLES.LST', 'sheet.txt'])
            states = {p.name: s for s, _, p in libsearch.coverage(tree)}
            self.assertEqual(states['sheet.pdf'], 'skip')
            self.assertEqual(states['lonely.pdf'], 'unsearched')
            self.assertEqual(states['firmware.bin'], 'skip')
            hits = libsearch.search_file(tree / "Ralf Brown's Interrupt List" / 'INTERRUP.A', ['reset disk'], False, 5)
            self.assertEqual(hits[0][0], 3)


class Recheck(unittest.TestCase):
    def test_rise_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / 'refs'
            tree.mkdir()
            plant(tree)
            matrix = Path(tmp) / 'm.toml'
            matrix.write_text('[[test]]\nname = "T-A"\ndecides = "silent: the bench decides"\n'
                              'searched = "terms: sound blaster, reset disk; hits: 0 in 0 documents; 28 Oct 2026"\n'
                              '[[test]]\nname = "T-B"\ndecides = "silent: the bench decides"\n'
                              'searched = "terms: nothing here; hits: 0 in 0 documents; 28 Oct 2026"\n')
            old_tree, old_refs = refcheck.worktree, libsearch.ROW_REFS
            refcheck.worktree = lambda: tree
            libsearch.ROW_REFS = []
            try:
                rows = libsearch.recheck(matrix)
            finally:
                refcheck.worktree, libsearch.ROW_REFS = old_tree, old_refs
            by_name = {r[0]: r for r in rows}
            self.assertEqual(by_name['T-A'][4], 2)
            self.assertEqual(by_name['T-B'][4], 0)
            self.assertEqual(libsearch.parse_searched('terms: a, b; hits: 14 in 3 documents (X 9); 28 Oct 2026'),
                             (['a', 'b'], 14, 3))


class ReadableKeys(unittest.TestCase):
    def test_readable_name_wins(self):
        self.assertEqual(sorted(['DOC_INTERRUP___', 'RBIL_D'], key=libsearch._readable), ['RBIL_D', 'DOC_INTERRUP___'])

    def test_installed_table_has_readable_twins(self):
        by_file = {}
        for key, name in refcheck.KEYS.items():
            by_file.setdefault(name, []).append(key)
        missing = [name for name, keys in by_file.items()
                   if all(k.endswith('_') for k in keys)]
        self.assertEqual(missing, [], f'files keyed only by an underscore-ended name: {missing}')


if __name__ == '__main__':
    unittest.main(verbosity=1)
