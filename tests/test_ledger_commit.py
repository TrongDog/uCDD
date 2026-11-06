#!/usr/bin/env python3
"""The ledger's runs file committed by the tool at a plan's end (the owner's decision of 6 Nov 2026).

    python3 METHOD/tests/test_ledger_commit.py

The decision: "the ledger's runs file on the top folder's main is committed
by the tool at each plan's end (calbatch invoking ledger), never by the
agent's hand and no longer by the backup. The 'bench commits before a plan'
rule stays, its reason now reproducibility: the plan's commit hash is in the
ledger." In a temporary top folder (a git repository on main, no remote, the
bench's check installed as the real one has it) with its own ledger
(UCDD_LEDGER) and a saved plan of three runs, two recorded:

1. commit-runs refuses while another file is staged and leaves it staged;
   then another file is committed, so HEAD is no longer the runs file's last
   commit; --dry-run commits nothing; with nothing else staged it commits
   the runs file alone (the modified and untracked files around it stay as
   they were), its message naming the plan, why it ended, its verdicts, the
   lines added by plan since the runs file's own last commit (not HEAD,
   which is named beside it) and the bench commit they were recorded on; run
   again, it finds nothing new and says so, naming its own commit.
2. It goes through the repository's own check: while a plan records the
   check refuses, and the index is left as found; once the recorder is gone
   the commit goes in. It refuses off main, and refuses a runs file whose
   earlier lines were changed (the ledger only grows).
3. record keeps --bench-commit and the count --bench-changed N on the
   entry, null when not given; it refuses a hash that is not a full one, a
   count without a commit and a count below 0, and writes nothing then.

The known-bads (lesson L4): a copy of the method package with commit-runs'
refusal of other staged files taken out ("    if besides:" made "    if
False:") fails 1; with its only-grows refusal taken out ("    if not
text.startswith(before):" made "    if False:") fails 2; with the base
taken from HEAD again ("    last = git('log', ..." made "    last =
head[:7]": HEAD named as the base) fails 1; the ledger.py
before the change fails all three in setUp (FAILED (failures=3),
"unrecognized arguments: --bench-commit": absence only). NOTES.md of the
draft has the commands. Built, not run: the counts are predictions
(UNMEASURED).

Since the owner's decision of 6 Nov 2026 on question 67 (7) ("`ledger.py
commit-runs` refuses to run unless invoked by calbatch (a token calbatch
sets), so a hand invocation fails"), commit-runs is called here through a
stand-in runner, a script named calbatch.py that sets the token as calbatch
does (STAND_IN); test_commit_token.py proves the refusal. The plants above
are unchanged by it. The same decision has the bench size check skip the
runs file by its path ("the bench size check excludes the ledger's runs file
by path"; bench/hooks/pre-commit, tests/test_runs_size.py), so --dry-run's
size line now says so; its known-bad is the ledger.py before this change
(the line read "the bench check refuses over 20 MB"): FAILED (failures=1)
in 1, the draft's G2. Built, not run.

decides = "silent: the owner's ruling of 6 Nov 2026 (the decision on the 15:50Z, 21:11Z and 23:31Z reports)"
searched = "terms: ledger, commit, reproducibility; hits: 107 in 32 documents (DPMI10 20, docs/history.md 12, PBOOK 8, INTEL486_1995 7, RBIL_H 7, RBIL_N 6); 6 Nov 2026"
lessons_read = "terms: ledger, commit, plan, runner, flag, backup, batch, hook; lessons: L6, L38, L2, L1, L9, L20, L40, L33, L37, L10, L22, L39, L32, L36; 6 Nov 2026"
"""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
TOOL = PACKAGE / 'tools' / 'ledger.py'
TAG = 'abcd1234'
BENCH = '0123456789abcdef0123456789abcdef01234567'
RUNS = 'ledger/runs.jsonl'
# A stand-in runner (question 67 (7)): it sets the token for its child as calbatch.py's commit_runs
# does, <its own file name>:<its process id>, and runs the rest of its command line as that child.
STAND_IN = '''import os, subprocess, sys
env = dict(os.environ, UCDD_LEDGER_RUNNER=os.path.basename(__file__) + ':' + str(os.getpid()))
sys.exit(subprocess.run([sys.executable, *sys.argv[1:]], env=env).returncode)
'''


def line(plan, run, verdict):
    return json.dumps({'plan': plan, 'run': run, 'test': 'T-X', 'verdict': verdict, 'dynarec': False,
                       'spot': False, 'time': '2026-11-06T00:00:00+00:00'}, sort_keys=True) + '\n'


class CommitRuns(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ledger-commit-')
        self.top = Path(self.tmp.name) / 'top'
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.top)], check=True)
        for key, value in (('user.name', 'Test'), ('user.email', 'test@example.com')):
            subprocess.run(['git', 'config', key, value], cwd=self.top, check=True)
        installed = subprocess.run(['sh', str(PACKAGE / 'install.sh'), '--bench', str(self.top)],
                                   capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.ledger = self.top / 'ledger'
        (self.ledger / 'plans').mkdir(parents=True)
        runs = [{'id': f'{TAG}-00{n}', 'test': f'T-{n}', 'config': {'mode': 'base'}, 'repeat': 1,
                 'command': 'true'} for n in (1, 2, 3)]
        (self.ledger / 'plans' / f'{TAG}.json').write_text(json.dumps({'tag': TAG, 'runs': runs}))
        (self.top / RUNS).write_text(line('eeee0000', 'eeee0000-001', 'pass'))
        (self.top / 'notes.md').write_text('notes\n')
        self.flag = Path(self.tmp.name) / 'recording.flag'
        self.env = dict(os.environ, UCDD_LEDGER=str(self.ledger), UCDD_RECORDING_FLAG=str(self.flag))
        self.env.pop('UCDD_LEDGER_RUNNER', None)
        self.runner = Path(self.tmp.name) / 'runner' / 'calbatch.py'
        self.runner.parent.mkdir()
        self.runner.write_text(STAND_IN)
        self.git('add', '-A')
        self.assertEqual(self.git('commit', '-q', '-m', 'Notes: first').returncode, 0)
        self.first = self.head()
        # the plan: run 1 passed, run 2 failed, run 3 not run; another plan's line between them
        self.record(f'{TAG}-001', 'pass', '--bench-commit', BENCH, '--bench-changed', '0')
        with open(self.top / RUNS, 'a') as file:
            file.write(line('ffff0000', 'ffff0000-001', 'pass'))
        self.record(f'{TAG}-002', 'fail', '--bench-commit', BENCH, '--bench-changed', '0')

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.top, capture_output=True, text=True, env=self.env)

    def head(self):
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def tool(self, *args):
        # commit-runs runs only from a runner (question 67 (7)): through the stand-in calbatch.py
        runner = [str(self.runner)] if args[:1] == ('commit-runs',) else []
        return subprocess.run([sys.executable, *runner, str(TOOL), *args], cwd=self.tmp.name,
                              capture_output=True, text=True, env=self.env)

    def record(self, run, verdict, *extra):
        done = self.tool('record', TAG, run, verdict, '--dynarec', '0', *extra)
        self.assertEqual(done.returncode, 0, done.stderr)

    def last_entry(self):
        return json.loads((self.top / RUNS).read_text().splitlines()[-1])

    def test_commits_the_runs_file_alone(self):
        # decides: the owner's decision of 6 Nov 2026 ("committed by the tool at each plan's end");
        # refused while anything else is staged: the agent's reading of "alone" and "never by the
        # agent's hand" (question 67); the base the message names, the runs file's own last commit
        # and not HEAD: the second review of 6 Nov 2026 (HEAD is often a later commit of the notes),
        # with git-log(1) (a path after -- keeps only the commits that changed it), asserted on the
        # installed git
        (self.top / 'notes.md').write_text('changed\n')
        self.git('add', 'notes.md')
        refused = self.tool('commit-runs', TAG, '--why', 'all runs complete')
        self.assertEqual(refused.returncode, 1, refused.stdout)
        self.assertIn('other files are staged', refused.stderr)
        self.assertIn('notes.md', refused.stderr)
        self.assertEqual(self.head(), self.first)
        self.assertEqual(self.git('diff', '--cached', '--name-only').stdout, 'notes.md\n')
        self.git('reset', '-q')
        # a commit of another file after the runs file's: HEAD is no longer the runs file's last commit
        (self.top / 'other.md').write_text('other\n')
        self.git('add', 'other.md')
        self.assertEqual(self.git('commit', '-q', '-m', 'Notes: other').returncode, 0)
        notes = self.head()
        self.assertNotEqual(notes, self.first)
        (self.top / 'scratch.txt').write_text('scratch\n')
        dry = self.tool('commit-runs', TAG, '--why', 'all runs complete', '--dry-run')
        self.assertEqual(dry.returncode, 0, dry.stderr)
        # the size beside the bench check's limit, which skips this file: the owner's decision of
        # 6 Nov 2026 on question 67 (7) ("the bench size check excludes the ledger's runs file by
        # path"); 20 MB: bench.toml's max_mb
        self.assertIn('MB (the bench check skips this file by its path, its 20 MB limit kept for '
                      'every other file)', dry.stdout)
        # %h is at least 7 digits (core.abbrev may make it longer), HEAD's always 7: each half apart
        self.assertIn(f'since its last commit {self.first[:7]}', dry.stdout)
        self.assertIn(f' (HEAD {notes[:7]}): {TAG} 2, ffff0000 1.', dry.stdout)
        self.assertEqual(self.head(), notes)
        done = self.tool('commit-runs', TAG, '--why', 'all runs complete')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f'ledger: committed {RUNS}', done.stdout)
        self.assertEqual(self.git('rev-parse', 'HEAD^').stdout.strip(), notes)
        self.assertEqual(self.git('show', '--name-only', '--format=', 'HEAD').stdout, f'{RUNS}\n')
        self.assertEqual(self.git('log', '-1', '--format=%s').stdout.strip(),
                         f'Ledger: plan {TAG}, all runs complete: 3 runs, fail 1, not run 1, pass 1')
        body = self.git('log', '-1', '--format=%b').stdout
        self.assertIn("the owner's decision of 6 Nov 2026", body)
        self.assertIn(f'3 lines added since its last commit {self.first[:7]}', body)
        self.assertIn(f' (HEAD {notes[:7]}): {TAG} 2, ffff0000 1.', body)
        self.assertIn(f'recorded on the bench at {BENCH[:7]} (2).', body)
        status = self.git('status', '--porcelain').stdout
        self.assertIn(' M notes.md', status)
        self.assertIn('?? scratch.txt', status)
        self.assertNotIn('runs.jsonl', status)
        committed = self.head()
        again = self.tool('commit-runs', TAG, '--why', 'all runs complete')
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn(f'nothing new in {RUNS} since its last commit {committed[:7]}', again.stdout)
        self.assertIn(f' (HEAD {committed[:7]}); nothing committed', again.stdout)
        self.assertEqual(self.head(), committed)

    def test_refusals(self):
        # decides: the owner, 4 Nov 2026 (L6): the bench's pre-commit refuses any commit while the
        # recording flag is set; off main: the decision's "on the top folder's main"; the ledger
        # only grows: bench/README.md ("Never check out, reset or revert the ledger: it only grows")
        recorder = subprocess.Popen(['sleep', '60'])
        try:
            self.flag.write_text(f'{recorder.pid} calbatch {TAG}_sweep.tsv\n')
            held = self.tool('commit-runs', TAG, '--why', 'all runs complete')
            self.assertEqual(held.returncode, 1, held.stdout)
            self.assertIn('a plan is recording', held.stderr)
            self.assertEqual(self.head(), self.first)
            self.assertEqual(self.git('diff', '--cached', '--name-only').stdout, '')
        finally:
            recorder.kill()
            recorder.wait()
        done = self.tool('commit-runs', TAG, '--why', 'all runs complete')
        self.assertEqual(done.returncode, 0, done.stderr)
        committed = self.head()
        self.git('checkout', '-q', '-b', 'other')
        self.record(f'{TAG}-003', 'pass')
        off = self.tool('commit-runs', TAG, '--why', 'all runs complete')
        self.assertEqual(off.returncode, 1, off.stdout)
        self.assertIn('not main', off.stderr)
        self.git('checkout', '-q', 'main')
        text = (self.top / RUNS).read_text()
        (self.top / RUNS).write_text(text.replace('"verdict": "pass"', '"verdict": "fail"', 1))
        grown = self.tool('commit-runs', TAG, '--why', 'all runs complete')
        self.assertEqual(grown.returncode, 1, grown.stdout)
        self.assertIn('the ledger only grows', grown.stderr)
        self.assertEqual(self.head(), committed)

    def test_record_keeps_the_bench_commit(self):
        # decides: the owner's decision of 6 Nov 2026 ("the plan's commit hash is in the ledger");
        # the count in place of the list: the review of 6 Nov 2026 (the list once per plan, in its log);
        # a short hash refused: the agent's choice (a full hash cannot become ambiguous later); a count
        # refused without a commit or below 0: that review and the agent's choice
        self.record(f'{TAG}-003', 'pass', '--bench-commit', BENCH, '--bench-changed', '2')
        entry = self.last_entry()
        self.assertEqual((entry['bench_commit'], entry['bench_changed']), (BENCH, 2))
        self.record(f'{TAG}-003', 'pass', '--bench-commit', BENCH)
        entry = self.last_entry()
        self.assertEqual((entry['bench_commit'], entry['bench_changed']), (BENCH, None))
        self.record(f'{TAG}-003', 'pass')
        entry = self.last_entry()
        self.assertEqual((entry['bench_commit'], entry['bench_changed']), (None, None))
        lines = (self.top / RUNS).read_text()
        for extra, said in ((('--bench-commit', BENCH[:7]), 'not a full commit hash'),
                            (('--bench-changed', '2'), 'needs --bench-commit'),
                            (('--bench-commit', BENCH, '--bench-changed', '-1'), 'not a count of files')):
            refused = self.tool('record', TAG, f'{TAG}-003', 'pass', '--dynarec', '0', *extra)
            self.assertNotEqual(refused.returncode, 0, extra)
            self.assertIn(said, refused.stderr)
        self.assertEqual((self.top / RUNS).read_text(), lines)


if __name__ == '__main__':
    unittest.main(verbosity=1)
