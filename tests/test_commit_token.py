#!/usr/bin/env python3
"""ledger.py commit-runs runs only when a runner invoked it, and the guard refuses the runners'
token set by hand (the owner's decision of 6 Nov 2026 on question 67 (7)).

    python3 METHOD/tests/test_commit_token.py

The decision: "`ledger.py commit-runs` refuses to run unless invoked by
calbatch (a token calbatch sets), so a hand invocation fails". The token is
UCDD_LEDGER_RUNNER=<the runner's script>:<its process id>, which the runner
puts in the environment of its own commit-runs call; ledger.py checks that
the process it names is its parent and runs that script (/proc). In a
temporary top folder (a git repository on main with the bench's check
installed, its own ledger through UCDD_LEDGER, a saved plan and one line
recorded since the runs file's commit):

1. commit-runs typed by hand (no token), --dry-run too, with a token naming
   this test's own process (its parent, but no runner), one naming another
   process, and one naming no runner, is refused with its message, and
   nothing is committed.
2. Through a stand-in runner (a script named calbatch.py that sets the token
   as calbatch does) it commits the runs file alone; through stand-ins named
   plan_run.py and sndreg.py it runs too (nothing new by then).
3. The guard refuses the token set by hand (before a command, through env,
   export or declare, in code given to a shell or to Python, in a
   here-document given to Python: plant AJ of NOTES.md's G4, in code given
   to a Python named by a variable: plant AM) and commit-runs
   typed by hand, and lets through a grep for the name, ledger.py show and
   commit-plan, and calbatch.py --status.
4. guard.py and ledger.py name the same token, and ledger.py the three runners.

The known-bads (lesson L4): the guard.py and ledger.py before this change (a
copy of the live method package with this file added; NOTES.md of the draft
has the commands) fail 1 and 3 and error in 4: FAILED (failures=2,
errors=1). The old ledger.py commits a hand commit-runs (1: "AssertionError:
0 != 1"), the old guard lets every form through (3: the refused list comes
back with each command and exit 0), and neither file has RUNNER_TOKEN (4:
"AttributeError: module 'guard_under_test' has no attribute
'RUNNER_TOKEN'"). 2 passes on both: the old ledger.py ignores the token;
its own known-bad is plant J of NOTES.md's G4 (the script check made to
refuse every token: the stand-in calbatch.py refused, FAILED (failures=1)).
Plants C, D and E fail 1; F, AJ and AM fail 3. Built, not run: the counts are
predictions (UNMEASURED).

decides = "the owner's decision of 6 Nov 2026 on question 67 (7): \"`ledger.py commit-runs` refuses to run unless invoked by calbatch (a token calbatch sets), so a hand invocation fails\""
searched = "terms: token, runner, invoked, hand invocation, commit; hits: 440 in 67 documents (DPMI10 20, INTEL486_1995 20, RBIL_K 20, RBIL_M 20, RBIL_Q 20, VIPM 20); 6 Nov 2026"
lessons_read = "terms: ledger, commit, token, runner, guard, hook; lessons: L38, L1, L20, L40, L33, L10, L22, L39, L32, L24, L36; 6 Nov 2026"
"""

from pathlib import Path
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
TOOL = PACKAGE / 'tools' / 'ledger.py'
GUARD = PACKAGE / 'guard' / 'guard.py'
TOKEN = 'UCDD_LEDGER_RUNNER'
RUNNERS = ('calbatch.py', 'plan_run.py', 'sndreg.py')
TAG = 'abcd1234'
RUNS = 'ledger/runs.jsonl'
# A stand-in runner: it sets the token for its child as calbatch.py's commit_runs does, <its own
# file name>:<its process id>, and runs the rest of its command line as that child.
STAND_IN = '''import os, subprocess, sys
env = dict(os.environ, UCDD_LEDGER_RUNNER=os.path.basename(__file__) + ':' + str(os.getpid()))
sys.exit(subprocess.run([sys.executable, *sys.argv[1:]], env=env).returncode)
'''


def load(name, path):
    """A tool's file as a module, its main() not run."""
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommitToken(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='commit-token-')
        root = Path(self.tmp.name).resolve()
        self.top = root / 'top'
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.top)], check=True)
        for key, value in (('user.name', 'Test'), ('user.email', 'test@example.com')):
            subprocess.run(['git', 'config', key, value], cwd=self.top, check=True)
        installed = subprocess.run(['sh', str(PACKAGE / 'install.sh'), '--bench', str(self.top)],
                                   capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.ledger = self.top / 'ledger'
        (self.ledger / 'plans').mkdir(parents=True)
        runs = [{'id': f'{TAG}-00{n}', 'test': f'T-{n}', 'config': {'mode': 'base'}, 'repeat': 1,
                 'command': 'true'} for n in (1, 2)]
        (self.ledger / 'plans' / f'{TAG}.json').write_text(json.dumps({'tag': TAG, 'runs': runs}))
        (self.top / RUNS).write_text(json.dumps(
            {'plan': 'eeee0000', 'run': 'eeee0000-001', 'test': 'T-X', 'verdict': 'pass',
             'dynarec': False, 'spot': False, 'time': '2026-11-06T00:00:00+00:00'}, sort_keys=True) + '\n')
        self.runners = root / 'runners'
        self.runners.mkdir()
        for name in RUNNERS:
            (self.runners / name).write_text(STAND_IN)
        self.env = dict(os.environ, UCDD_LEDGER=str(self.ledger),
                        UCDD_RECORDING_FLAG=str(root / 'recording.flag'),
                        UCDD_METHOD_LOCAL=str(root / 'none.toml'))
        self.env.pop(TOKEN, None)
        self.git('add', '-A')
        self.assertEqual(self.git('commit', '-q', '-m', 'Notes: first').returncode, 0)
        self.first = self.head()
        recorded = self.tool('record', TAG, f'{TAG}-001', 'pass', '--dynarec', '0')
        self.assertEqual(recorded.returncode, 0, recorded.stderr)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.top, capture_output=True, text=True, env=self.env)

    def head(self):
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def tool(self, *args, token=None, runner=None):
        """ledger.py run from this test (its parent) with TOKEN set as given, or through the
        stand-in runner named RUNNER (its parent then)."""
        env = dict(self.env, **({TOKEN: token} if token is not None else {}))
        through = [str(self.runners / runner)] if runner else []
        return subprocess.run([sys.executable, *through, str(TOOL), *args], cwd=self.tmp.name,
                              capture_output=True, text=True, env=env)

    def guard(self, command):
        call = {'tool_name': 'Bash', 'tool_input': {'command': command}, 'cwd': self.tmp.name}
        return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(call),
                              capture_output=True, text=True, env=self.env).returncode

    def test_hand_commit_runs_refused(self):
        # decides: the owner's decision of 6 Nov 2026 on question 67 (7) ("`ledger.py commit-runs`
        # refuses to run unless invoked by calbatch (a token calbatch sets), so a hand invocation
        # fails"). The token bound to its process and that process's script, and --dry-run refused
        # as well: the agent's choice, confirmed by the owner 6 Nov 2026 (68.1), on "invoked by" and
        # "refuses to run" (applied, confirmed); searched = "terms: token, invoked, dry run; hits: 339 in 54 documents (INTEL486_1995 20, RBIL_K 20, RBIL_M 20, RBIL_Q 20, VIPM 20, INTEL96 19); 6 Nov 2026"
        cases = [((), None, f'{TOKEN} is not set'),
                 (('--dry-run',), None, f'{TOKEN} is not set'),
                 ((), f'calbatch.py:{os.getpid()}', 'not calbatch.py'),
                 ((), 'calbatch.py:1', 'names process 1, but this one was started by'),
                 ((), f'mytool.py:{os.getpid()}', 'is not <runner>:<process id>')]
        for extra, token, said in cases:
            done = self.tool('commit-runs', TAG, '--why', 'by hand', *extra, token=token)
            self.assertEqual(done.returncode, 1, (extra, token, done.stdout))
            self.assertIn('ledger: commit-runs refused: ', done.stderr)
            self.assertIn(said, done.stderr)
        self.assertEqual(self.head(), self.first)
        self.assertIn(f' M {RUNS}', self.git('status', '--porcelain').stdout)

    def test_runner_commit_goes_in(self):
        # decides: the owner's decision of 6 Nov 2026 on question 67 (7) for calbatch: "unless
        # invoked by calbatch (a token calbatch sets)". plan_run.py and sndreg let through as
        # well: the agent's choice, confirmed by the owner 6 Nov 2026 (68.1, 68.3 (a)), on "every
        # runner that writes ledger rows (plan_run.py, sndreg) records the bench's commit hash and
        # ends with commit-runs" beside it (applied, confirmed);
        # searched = "terms: runner, commit-runs, plan_run, sndreg; hits: 22 in 3 documents (docs/history.md 20, RBIL_N 1, docs/second-emulator/README.md 1); 6 Nov 2026"
        done = self.tool('commit-runs', TAG, '--why', 'all runs complete', runner='calbatch.py')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f'ledger: committed {RUNS} as ', done.stdout)
        self.assertEqual(self.git('rev-parse', 'HEAD^').stdout.strip(), self.first)
        self.assertEqual(self.git('show', '--name-only', '--format=', 'HEAD').stdout, f'{RUNS}\n')
        committed = self.head()
        for runner in RUNNERS[1:]:
            again = self.tool('commit-runs', TAG, '--why', 'its end', runner=runner)
            self.assertEqual(again.returncode, 0, (runner, again.stderr))
            self.assertIn('nothing new', again.stdout)
        self.assertEqual(self.head(), committed)

    def test_guard_refuses_the_token_by_hand(self):
        # decides: the agent's choice, confirmed by the owner 6 Nov 2026 (68.1), on the owner's
        # decision of 6 Nov 2026 on question 67 (7) ("`ledger.py commit-runs` refuses to run
        # unless invoked by calbatch (a token calbatch sets), so a hand invocation fails"): the
        # token set by hand and commit-runs typed by hand are refused at the guard too, and what
        # still passes (applied, confirmed);
        # searched = "terms: guard, environment variable, by hand, token; hits: 188 in 47 documents (Sound Cards/Superset references/Developer_Kit_SB_Series_Programmers_Guide.txt 20, RBIL_M 18, Sound Cards/Superset references/Developer_Kit_SB_Series_Library_Reference.txt 12, DOC_OPCODES 10, RBIL_G 10, RBIL_Q 10); 6 Nov 2026"
        refused = [f'{TOKEN}=calbatch.py:1 python3 tools/ledger.py show {TAG}',
                   f'{TOKEN}=calbatch.py:1 python3 tools/ledger.py commit-runs {TAG}',
                   f'export {TOKEN}=calbatch.py:1',
                   f'{TOKEN}=x; export {TOKEN}',
                   f'declare -x {TOKEN}=x',
                   f'env {TOKEN}=x python3 tools/ledger.py commit-runs {TAG}',
                   f'cd {self.tmp.name} && setsid nohup env {TOKEN}=x python3 x.py',
                   f'python3 -c "import os; os.environ[\'{TOKEN}\'] = \'x\'"',
                   f'bash -c "{TOKEN}=x python3 tools/ledger.py commit-runs {TAG}"',
                   f'python3 tools/ledger.py commit-runs {TAG}',
                   f'python3 tools/ledger.py commit-runs {TAG} --dry-run',
                   f'python3 ../method/tools/ledger.py commit-runs {TAG} --why x',
                   f"python3 - <<'EOF'\nimport os\nos.environ['{TOKEN}'] = 'x'\nEOF",
                   f'P=python3; $P -c "import os; os.environ[\'{TOKEN}\'] = \'x\'"']
        allowed = [f'grep -n {TOKEN} runs/calbatch.py',
                   f"grep -c '{TOKEN}=' runs/plan_run.py",
                   f'unset {TOKEN}',
                   f'python3 tools/ledger.py show {TAG}',
                   f'python3 tools/ledger.py commit-plan {TAG}',
                   'grep -n commit-runs tools/ledger.py',
                   'python3 runs/calbatch.py p.tsv --status']
        wrong = ([(command, code) for command in refused for code in [self.guard(command)] if code != 2]
                 + [(command, code) for command in allowed for code in [self.guard(command)] if code != 0])
        self.assertEqual(wrong, [])

    def test_one_token_name(self):
        # decides: the agent's choice, confirmed by the owner 6 Nov 2026 (68.1) (two files name the
        # token, so a test keeps them one name; the runners as test_runner_commit_goes_in; applied,
        # confirmed);
        # searched = "terms: token, runner, name; hits: 1648 in 123 documents (1487 20, 1533 20, 1543 20, 4031 20, 496 20, 5582 20); 6 Nov 2026"
        guard = load('guard_under_test', GUARD)
        ledger = load('ledger_under_test', TOOL)
        self.assertEqual((guard.RUNNER_TOKEN, ledger.RUNNER_TOKEN), (TOKEN, TOKEN))
        self.assertEqual(ledger.RUNNERS, RUNNERS)


if __name__ == '__main__':
    unittest.main(verbosity=1)
