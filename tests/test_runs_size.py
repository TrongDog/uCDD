#!/usr/bin/env python3
"""The bench's size check lets the ledger's runs file in by its path, and nothing else over the
limit (Michael's decision of 6 Nov 2026 on question 67 (7): "the bench size check excludes the
ledger's runs file by path").

    python3 METHOD/tests/test_runs_size.py [HOOK]

HOOK (default: bench/hooks/pre-commit of this package) is run as if it were that file in its own
place (its methodlib, its bench.toml), so a planted copy elsewhere reads this package's settings
(the known-bads, lesson L4). Each case makes a temporary git repository of its own with no
remote (the top folder's kind: the home-path check off), stages its files and runs the hook as
git would, in the repository, with UCDD_LEDGER naming the ledger folder (methodlib.ledger_dir),
UCDD_RECORDING_FLAG a flag that does not exist (the bench's own must not decide) and the user's
global and system git files off. Each big file is 21 MiB, over bench.toml's 20 MB:

  1 the runs file              ledger/runs.jsonl, the ledger at ledger/: exit 0, nothing said
  2 another file beside it     ledger/runs.jsonl and ledger/other.jsonl, the ledger at ledger/:
                               exit 1, "  - ledger/other.jsonl: 21 MB, over 20 MB"; the runs file
                               not named
  3 the same name elsewhere    elsewhere/runs.jsonl, the ledger at ledger/: exit 1,
                               "  - elsewhere/runs.jsonl: 21 MB, over 20 MB" (by path, not by name)
  4 the ledger outside         ledger/runs.jsonl staged, the ledger folder outside the repository
                               (the bench repository's case): exit 1, "  - ledger/runs.jsonl: 21
                               MB, over 20 MB" (nothing skipped)

The known-bads (lesson L4; the draft's NOTES.md has the commands): the hook before the change:
cases 1 and 2 BAD, "2 bad" (the runs file refused, and named in case 2's refusal); the exclusion
made a name pattern (the staged name ending in the runs file's
name): case 3 BAD, "1 bad"; the exclusion made the ledger's folder (any staged name under it):
case 2 BAD, "1 bad"; the exclusion made one fixed relative name, the same in every repository
(not the path methodlib resolves inside the one being committed): case 4 BAD, "1 bad". Prints ok
or BAD per case and "N bad" last; exits 1 on a BAD. Built, not run
(6 Nov 2026): every count here is a prediction (UNMEASURED). Each case writes up to 42 MiB in a
temporary folder, removed at its end.

What decides each expected value: the exclusion and that it is by path, Michael's decision of 6
Nov 2026 on question 67 (7) ("the bench size check excludes the ledger's runs file by path");
by that exact path only, in whichever repository holds it, with no further condition (no test
of whether the repository has a remote), the agent's choice, confirmed by Michael 6 Nov 2026 (68.3); every other file over
the limit refused, bench.toml's max_mb (20) and its refusal's own words (the hook); the ledger's
path, methodlib.ledger_dir with UCDD_LEDGER, as ledger.py commit-runs reads it.

decides = "Michael's decision of 6 Nov 2026 on question 67 (7): \"the bench size check excludes the ledger's runs file by path\"; by the exact path only: the agent's choice, confirmed by Michael 6 Nov 2026 (68.3); the limit, bench.toml max_mb"
searched = ""terms: ledger, size, limit, pre-commit; hits: 2007 in 131 documents (1487 20, 1533 20, 1543 20, 4031 20, 460 20, 471 20); 6 Nov 2026""
lessons_read = "terms: ledger, size, hook, commit; lessons: L38, L20, L40, L33, L41, L10, L22, L39, L32; 6 Nov 2026"
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent.parent
LIVE = PACKAGE / 'bench' / 'hooks' / 'pre-commit'
RUNS_NAME = 'runs.jsonl'              # the name methodlib.append and ledger.py commit-runs write
BIG = 21 * 2 ** 20                    # 21 MiB: over bench.toml's 20 MB, read back as "21 MB"
# the hook's code from the file given, run as if it were the package's own pre-commit
LOADER = ('import sys\n'
          'live, code = sys.argv[1], sys.argv[2]\n'
          'sys.argv = [live]\n'
          'scope = {"__name__": "__main__", "__file__": live}\n'
          'exec(compile(open(code).read(), code, "exec"), scope)\n')


def case(tmp, hook, label, big, ledger_in_repo=True):
    """A repository at TMP/LABEL with BIG (paths) staged at 21 MiB each, the ledger folder at its
    ledger/ or outside it: the hook's (exit code, stderr)."""
    top = tmp / label
    top.mkdir()
    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
               UCDD_LEDGER=str(top / 'ledger' if ledger_in_repo else tmp / (label + '-outside')),
               UCDD_RECORDING_FLAG=str(tmp / 'no.flag'))
    subprocess.run(['git', 'init', '-q'], cwd=top, env=env, check=True)
    for name in big:
        path = top / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            f.write(b'0' * (BIG - 1) + b'\n')
        subprocess.run(['git', 'add', '--', name], cwd=top, env=env, check=True)
    done = subprocess.run([sys.executable, '-c', LOADER, str(LIVE), hook], cwd=top, env=env,
                          capture_output=True, text=True)
    shutil.rmtree(top, ignore_errors=True)
    return done.returncode, done.stderr


def main():
    hook = sys.argv[1] if len(sys.argv) > 1 else str(LIVE)
    bad = 0
    tmp = Path(tempfile.mkdtemp(prefix='runs-size-'))

    def report(ok, label, code, said):
        nonlocal bad
        bad += not ok
        shown = ' | '.join(line.strip() for line in said.splitlines() if line.strip()) or 'nothing said'
        print('%s %-26s exit %s; %s' % ('ok  ' if ok else 'BAD ', label, code, shown[-300:]), flush=True)

    runs = 'ledger/' + RUNS_NAME
    try:
        code, said = case(tmp, hook, 'one', [runs])
        report(code == 0 and not said.strip(), 'the runs file', code, said)

        code, said = case(tmp, hook, 'two', [runs, 'ledger/other.jsonl'])
        report(code == 1 and '  - ledger/other.jsonl: 21 MB, over 20 MB' in said.splitlines()
               and runs not in said, 'another file beside it', code, said)

        code, said = case(tmp, hook, 'three', ['elsewhere/' + RUNS_NAME])
        report(code == 1 and '  - elsewhere/%s: 21 MB, over 20 MB' % RUNS_NAME in said.splitlines(),
               'the same name elsewhere', code, said)

        code, said = case(tmp, hook, 'four', [runs], ledger_in_repo=False)
        report(code == 1 and '  - %s: 21 MB, over 20 MB' % runs in said.splitlines(),
               'the ledger outside', code, said)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('%d bad' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
