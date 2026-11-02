#!/usr/bin/env python3
"""Tightening r3.8: the lessons register is read before the work it governs.

    python3 METHOD/tests/test_r38.py

1. lessons_recall finds lessons by term across Short, Tags, Recall and Rule,
   heaviest first, and prints the lessons_read line.
2. The "read: yes|no" suffix on a hit line is parsed, and the agent's own
   lessons.py regex still accepts the line (the suffix folds into the text).
3. check reports an IN_PROGRESS gate row without a lessons_read line and
   exits 1; with the line it exits 0; and it counts reading failures.
"""

from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
TOOL = PACKAGE / 'tools' / 'lessons_recall.py'
sys.path.insert(0, str(PACKAGE / 'tools'))

REGISTER = """# Lessons register

### L6. Nothing else on the host
- Short: Nothing else on the host while 86Box records or a regression runs.
- Tags: run
- Recall: before starting any recording or batch.
- Guard: partial: boxcheck.py
- Hits:
  - 24 Oct | 2 | first | a stray DOSBox-X beside two days of recordings
  - 30 Oct | 2 | relearned | the batch runner did not hold the recording flag | read: no

### L9. Never pgrep -f yourself
- Short: Never wait on or kill by pgrep -f with a pattern in the same command.
- Tags: shell
- Recall: any wait or kill.
- Guard: none
- Hits:
  - 20 Oct | 1 | first | matched its own shell
  - 2 Nov | 1 | relearned | the wait watched setsid's own process | read: yes

### L39. Recompiler off
- Short: The recompiler is off for every recording that records.
- Tags: run, probe
- Recall: before any plan runs.
- Guard: full since 2 Nov: plan_run defaults it off
- Hits:
  - 2 Nov | 2 | relearned | the C1 Play plan ran with it on | read: no
"""

STATE_BAD = """## Project A
| Gate | Status | Notes |
| A6 | IN_PROGRESS | the sweep |
| A5 | PASS | done |
"""

STATE_GOOD = """## Project A
| Gate | Status | Notes |
| A6 | IN_PROGRESS | the sweep; lessons_read = "terms: record, batch; lessons: L6, L39; 2 Nov 2026" |
| A5 | PASS | done |
"""

OLD_HIT = re.compile(r'  - (.+?) \| (\d) \| (\w+) \| (.*)')


class Recall(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.reg = Path(self.tmp.name) / 'LESSONS.md'
        self.reg.write_text(REGISTER)

    def tearDown(self):
        self.tmp.cleanup()

    def run_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *args, '--register', str(self.reg)],
                              capture_output=True, text=True)

    def test_terms_find_by_tag_recall_and_short(self):
        import lessons_recall
        lessons = lessons_recall.read_register(self.reg)
        found = lessons_recall.matching(lessons, ['record'])
        self.assertEqual([l['id'] for l in found], ['L6', 'L39'])  # L6 weight 6 > L39 weight 4
        found = lessons_recall.matching(lessons, ['kill'])
        self.assertEqual([l['id'] for l in found], ['L9'])

    def test_line_form(self):
        done = self.run_tool('record', 'batch', '--line')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertRegex(done.stdout.strip(), r'^lessons_read = "terms: record, batch; lessons: L6, L39; \d+ \w{3} \d{4}"$')

    def test_read_field_parsed_and_old_regex_still_matches(self):
        import lessons_recall
        lessons = {l['id']: l for l in lessons_recall.read_register(self.reg)}
        self.assertEqual(lessons['L6']['hits'][1]['read'], 'no')
        self.assertEqual(lessons['L9']['hits'][1]['read'], 'yes')
        self.assertIsNone(lessons['L6']['hits'][0]['read'])
        for line in REGISTER.splitlines():
            if line.startswith('  - '):
                m = OLD_HIT.match(line)
                self.assertIsNotNone(m, line)
                self.assertIn(m.group(3), ('first', 'applied', 'relearned'))

    def test_check_missing_and_present(self):
        state = Path(self.tmp.name) / 'STATE.md'
        state.write_text(STATE_BAD)
        done = self.run_tool('check', '--state', str(state))
        self.assertEqual(done.returncode, 1, done.stdout)
        self.assertIn('A6', done.stdout)
        self.assertIn('2 reading failures', done.stdout)
        self.assertIn('1 guard failures', done.stdout)
        state.write_text(STATE_GOOD)
        done = self.run_tool('check', '--state', str(state))
        self.assertEqual(done.returncode, 0, done.stdout)

    def test_status_cell_only(self):
        # 2 Nov 2026, at install: STATE's gate rows keep their history inline ("PASS (...). Before:
        # IN_PROGRESS (...)"); only the status cell decides that a gate is IN_PROGRESS
        state = Path(self.tmp.name) / 'STATE.md'
        state.write_text("""## Project A
| Gate | Status | Notes |
| A4 | PASS (the owner, 29 Oct). Before: IN_PROGRESS (28 Oct) | done |
| A6 | NOT_STARTED | the sweep |
""")
        done = self.run_tool('check', '--state', str(state))
        self.assertEqual(done.returncode, 0, done.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=1)
