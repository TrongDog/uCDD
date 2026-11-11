#!/usr/bin/env python3
"""While 86Box records, the guard refuses any command but the runner's own wait (the owner's decision of
11 Nov 2026 on the 09:45Z report, item 5).

    python3 METHOD/tests/test_guard_recording.py
    UCDD_GUARD_UNDER_TEST=OLD/guard/guard.py python3 METHOD/tests/test_guard_recording.py   the known-bad

The mark is a flag of the test's own (UCDD_RECORDING_FLAG), naming this test's PID as a runner's names its
own; 86Box is a copy of bash named 86Box waiting on its builtin read, so its /proc/PID/exe ends in /86Box
as the real one's does (the guard reads the executable, never a pattern: L9). Each call goes to the guard
as Claude Code sends it (its JSON on stdin):
1. recording (the mark set, 86Box alive), the plant: `echo hi`, a Python parse check (the two commands of
   the L6 hit of 11 Nov 2026), the runner's --status, the wait with a second command after it or its
   output redirected, the wait behind a variable, and a Monitor's command are refused (exit 2, "while
   86Box records"); the wait alone passes (calbatch.py and plan_run.py, 'first' and the end, --log, after a
   cd, through the bench's Python); an Edit and a Write of a text file pass.
2. stale (the mark set, no 86Box alive; its holder alive, then gone): `echo hi` passes (exit 0) and the
   guard's output says the mark is stale, as JSON with a systemMessage.
3. no mark: `echo hi` passes, nothing said.
The known-bad (lesson L4): the guard before this change (its HEAD copy beside the live lib) fails 1 (the
plant: a command issued during a recording passes) and 2 (no notice); 3 passes on it.

decides = "the owner's decision of 11 Nov 2026 on the 09:45Z report, item 5: \"While 86Box records, the session's command guard refuses any command but the runner's own wait; Edit and Write of text stay open. The runner sets the mark and clears it. A mark with no 86Box alive is reported as stale and does not hold the session. Its plant: a command issued during a recording is refused.\""
lessons_read = "terms: guard, recording, flag, runner, plan, wait, lessons, hook; lessons: L6, L11, L2, L9, L38, L1, L3, L21, L33, L36, L5, L37, L10, L39, L45, L46, L48, L25, L31, L24, L44; 11 Nov 2026"
"""

from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
GUARD = Path(os.environ.get('UCDD_GUARD_UNDER_TEST') or PACKAGE / 'guard' / 'guard.py')
WAIT = 'python3 /bench/runs/calbatch.py /bench/runs/abcd1234_a7x.tsv --wait'
REFUSED = ['echo hi',
           'python3 -c "import ast; ast.parse(open(\'x.py\').read())"',
           'python3 runs/calbatch.py runs/abcd1234_a7x.tsv --status',
           WAIT + '; echo done',
           WAIT + ' && git status',
           WAIT + ' > /tmp/out.txt',
           'P=runs/calbatch.py; python3 $P runs/abcd1234_a7x.tsv --wait',
           'python3 runs/calbatch.py runs/abcd1234_a7x.tsv --wait first $(date)']
PASSED = [WAIT,
          WAIT + ' first',
          'cd /bench && python3 runs/calbatch.py runs/abcd1234_a7x.tsv --wait first',
          'python3 runs/plan_run.py runs/abcd1234_t.tsv --wait --log runs/plan_run_abcd1234.log',
          '../tools/py-venv/bin/python runs/plan_run.py runs/abcd1234_t.tsv --wait end']


class Recording(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='guard-rec-')
        self.root = Path(self.tmp.name)
        self.flag = self.root / 'recording.flag'
        self.env = dict(os.environ, UCDD_RECORDING_FLAG=str(self.flag),
                        UCDD_METHOD_LOCAL=str(self.root / 'none.toml'))
        self.box = None

    def tearDown(self):
        self.stop_box()
        self.tmp.cleanup()

    def start_box(self):
        # a copy of bash waiting on its own builtin read: one process, no child (the host's sleep is a
        # multi-call binary that reads its own name and stops under any other)
        fake = self.root / '86Box'
        shutil.copy(os.path.realpath(shutil.which('bash')), fake)
        fake.chmod(0o755)
        self.box = subprocess.Popen([str(fake), '-c', 'read -t 120'], stdin=subprocess.PIPE)

    def stop_box(self):
        if self.box:
            self.box.kill()
            self.box.wait()
            self.box.stdin.close()
            self.box = None

    def guard(self, tool, given):
        call = {'tool_name': tool, 'tool_input': given, 'cwd': str(self.root)}
        done = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(call), capture_output=True,
                              text=True, env=self.env)
        return done.returncode, done.stdout, done.stderr

    def test_1_recording(self):
        self.flag.write_text(f'{os.getpid()} abcd1234_a7x.tsv\n')
        self.start_box()
        wrong = []
        for line in REFUSED:
            code, _, err = self.guard('Bash', {'command': line})
            if code != 2 or 'while 86Box records' not in err:
                wrong.append(('refused?', line, code, err[:120]))
        code, _, err = self.guard('Monitor', {'command': 'tail -f runs/x.log', 'description': 'x',
                                              'timeout_ms': 1000})
        if code != 2:
            wrong.append(('refused?', 'Monitor', code, err[:120]))
        for line in PASSED:
            code, _, err = self.guard('Bash', {'command': line})
            if code != 0:
                wrong.append(('passed?', line, code, err[:120]))
        text = self.root / 'notes.md'
        for tool, given in (('Edit', {'file_path': str(text), 'old_string': 'a', 'new_string': 'b'}),
                            ('Write', {'file_path': str(text), 'content': 'text'})):
            code, _, err = self.guard(tool, given)
            if code != 0:
                wrong.append(('passed?', tool, code, err[:120]))
        self.assertEqual(wrong, [])

    def test_2_stale(self):
        dead = subprocess.Popen(['true'])
        dead.wait()
        said = []
        for holder in (os.getpid(), dead.pid):
            self.flag.write_text(f'{holder} abcd1234_a7x.tsv\n')
            code, out, err = self.guard('Bash', {'command': 'echo hi'})
            notice = json.loads(out).get('systemMessage', '') if out.strip().startswith('{') else ''
            said.append((code, 'stale' in notice, ('alive' if holder == os.getpid() else 'gone') in notice))
        self.assertEqual(said, [(0, True, True), (0, True, True)])

    def test_3_no_mark(self):
        code, out, err = self.guard('Bash', {'command': 'echo hi'})
        self.assertEqual((code, out.strip()), (0, ''))


if __name__ == '__main__':
    unittest.main(verbosity=1)
