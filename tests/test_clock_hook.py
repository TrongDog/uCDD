#!/usr/bin/env python3
"""The bench's pre-commit runs the repository's own clock check on the top folder's notes
(the owner's decision of 6 Nov 2026, lesson L40: "every time heading in HANDOFF and STATE is written
by a tool from the clock, and the commit check refuses a time line the tool did not write").

    python3 METHOD/tests/test_clock_hook.py [HOOK]

HOOK (default: bench/hooks/pre-commit of this package) is run as if it were that file in its own
place (its methodlib, its bench.toml), so a planted copy elsewhere reads this package's settings
(the known-bads, lesson L4; tests/test_runs_size.py's loader). Each case uses one temporary git
repository laid out as the top folder (context/HANDOFF.md, context/STATE.md, no remote), its
first commit made before the hook is put in; the hook is then its pre-commit through a two-line
shell file that execs it (git stays its parent, as for any hook). context/clockhead.py there is a
stand-in written by this test: it notes its arguments in a log and, by STANDIN_MODE, refuses
(printing "STAND-IN refused: ARGS", exit 1), passes (exit 0) or crashes (a traceback's words on
stderr, nothing on stdout, exit 2). This test reads only the wiring; the tool's own rules are the
top folder's context/test_clockhead.py. UCDD_RECORDING_FLAG names a flag that does not exist, the
user's global and system git files are off.

  1 a clocked file, refused  context/HANDOFF.md changed, committed: exit 1; "pre-commit: refused: a
                             time line the clock tool did not write" and "  - STAND-IN refused:
                             check context/HANDOFF.md" in git's output
  2 a clocked file, passed   the same, the stand-in passing: exit 0, the stand-in run once with
                             "check context/HANDOFF.md"
  3 another file             docs/x.txt alone: exit 0; the stand-in not run
  4 both notes               both changed: the stand-in run once with "check context/HANDOFF.md
                             context/STATE.md"
  5 STATE alone              "check context/STATE.md"
  6 no tool                  context/clockhead.py gone, HANDOFF changed: exit 1;
                             "context/HANDOFF.md: its time headings are checked by
                             context/clockhead.py, which this repository does not hold"
  7 the backup's snapshot    HANDOFF changed in an index of its own outside .git, the hook run as
                             bench/backup.sh runs it (by a script, not git): exit 0; not run
  8 run by hand, own index   HANDOFF staged in the repository's own index, the hook run by a
                             script (not git): run, exit 1
  9 a commit on another index GIT_INDEX_FILE naming an index outside .git, git commit: run, exit 1
                             (a commit never reaches the backup's skip)
 10 the tool crashes         exit 1; "context/clockhead.py check: exit 2: Traceback (most recent
                             call last): | boom"

The known-bads (lesson L4; the draft's NOTES.md has the commands): the hook as it stands before
this change (no clock check): cases 1, 2, 4, 5, 6, 8, 9 and 10 BAD, "8 bad" (case 2 by the
stand-in never run); the backup's skip taken
out ("if not staged:"): case 7 BAD, "1 bad"; the skip on the index alone ("if not staged or not
own_index():"): case 9 BAD, "1 bad"; the skip on the parent alone ("if not staged or not
run_by_git():"): case 8 BAD, "1 bad"; the missing tool's refusal made "if False:": case 6 BAD, "1
bad" (the refusal then comes from Python's own error, not the words); CLOCKED holding HANDOFF
alone: cases 4 and 5 BAD, "2 bad"; the stderr fallback made "return []" (a crashing tool passing
the commit): case 10 BAD, "1 bad". Prints ok or BAD per case and "N bad" last; exits 1 on a BAD.
Built, not run (6 Nov 2026): every count here is a prediction (UNMEASURED).

What decides each expected value: a commit refused on what the tool says (cases 1, 4, 5, 8, 9),
the owner's decision of 6 Nov 2026 (L40): "the commit check refuses a time line the tool did not
write"; the check run on the two notes only (cases 3 to 5), a missing tool refused (6), the
backup's snapshot skipped (7) and only it (8, 9), a crash refused (10): the agent's choice,
confirmed by the owner 7 Nov 2026 (69.2); git running a hook as the hook's parent, and an as-is
commit's hook given its index as GIT_INDEX_FILE, silent: githooks(5), git-commit(1), asserted by
cases 8 and 9 on the installed git.

decides = "the owner's decision of 6 Nov 2026 (L40): \"every time heading in HANDOFF and STATE is written by a tool from the clock, and the commit check refuses a time line the tool did not write\"; the two notes only, a missing tool refused, the backup's skip and a crash refused: the agent's choice, confirmed by the owner 7 Nov 2026 (69.2); git's hook environment silent: githooks(5), asserted here"
searched = "terms: pre-commit, hook, index, parent; hits: 1543 in 124 documents (1487 20, 1523 20, 1533 20, 1543 20, 206 20, 4031 20); 6 Nov 2026"
lessons_read = "terms: clock, heading, time, hook, commit, backup; lessons: L38, L40, L20, L33, L10, L18, L22, L16, L32, L43; 6 Nov 2026"
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

PACKAGE = Path(__file__).resolve().parent.parent
LIVE = PACKAGE / 'bench' / 'hooks' / 'pre-commit'
LOADER = ('import sys\n'
          'live, code = sys.argv[1], sys.argv[2]\n'
          'sys.argv = [live]\n'
          'scope = {"__name__": "__main__", "__file__": live}\n'
          'exec(compile(open(code).read(), code, "exec"), scope)\n')
STANDIN = ('import os, sys\n'
           'with open(os.environ["STANDIN_LOG"], "a") as log:\n'
           '    log.write(" ".join(sys.argv[1:]) + "\\n")\n'
           'mode = os.environ.get("STANDIN_MODE", "refuse")\n'
           'if mode == "pass":\n'
           '    sys.exit(0)\n'
           'if mode == "crash":\n'
           '    sys.stderr.write("Traceback (most recent call last):\\nboom\\n")\n'
           '    sys.exit(2)\n'
           'print("STAND-IN refused: " + " ".join(sys.argv[1:]))\n'
           'sys.exit(1)\n')
HEADER = 'pre-commit: refused: a time line the clock tool did not write'


def main():
    hook = Path(sys.argv[1] if len(sys.argv) > 1 else LIVE).resolve()
    bad = 0
    tmp = Path(tempfile.mkdtemp(prefix='clock-hook-'))
    repo, loader, log = tmp / 'top', tmp / 'loader.py', tmp / 'standin.log'
    tool = repo / 'context' / 'clockhead.py'

    def report(ok, label, seen):
        nonlocal bad
        bad += not ok
        print('%s %-26s %s' % ('ok  ' if ok else 'BAD ', label, ' | '.join(
            line.strip() for line in str(seen).splitlines() if line.strip())[-400:] or 'nothing said'), flush=True)

    env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
    env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1', STANDIN_LOG=str(log),
               UCDD_RECORDING_FLAG=str(tmp / 'no.flag'), UCDD_LEDGER=str(tmp / 'ledger-outside'))

    def git(*words, index=None, mode='refuse'):
        run_env = dict(env, STANDIN_MODE=mode, **({'GIT_INDEX_FILE': str(index)} if index else {}))
        return subprocess.run(['git', '-c', 'user.name=Test', '-c', 'user.email=test@example.com', *words],
                              cwd=repo, env=run_env, capture_output=True, text=True)

    def runs():
        """The stand-in's runs since the last case, by their arguments; the log emptied."""
        said = log.read_text().splitlines() if log.exists() else []
        log.write_text('')
        return said

    def change(*names):
        for name in names:
            with open(repo / name, 'a') as f:
                f.write('one more line\n')

    def commit(*names, mode='refuse', index=None):
        """NAMES changed, staged and committed through the hook: (exit, git's output, the
        stand-in's runs); a refused commit's files put back as HEAD has them."""
        runs()
        change(*names)
        git('add', '--', *names, index=index)
        done = git('commit', '-q', '-m', 'Notes: a test', index=index, mode=mode)
        if done.returncode:
            git('checkout', '-q', 'HEAD', '--', *names)
        return done.returncode, done.stdout + done.stderr, runs()

    def by_script(index=None):
        """HANDOFF changed and staged (in INDEX, or the repository's own), the hook run by this
        script, not git: (exit, its stderr, the stand-in's runs); the file put back."""
        runs()
        change('context/HANDOFF.md')
        if index:
            git('read-tree', 'HEAD', index=index)
        git('add', '--', 'context/HANDOFF.md', index=index)
        run_env = dict(env, STANDIN_MODE='refuse', **({'GIT_INDEX_FILE': str(index)} if index else {}))
        done = subprocess.run([sys.executable, str(loader), str(LIVE), str(hook)], cwd=repo, env=run_env,
                              capture_output=True, text=True)
        git('reset', '-q', '--', 'context/HANDOFF.md')
        git('checkout', '-q', 'HEAD', '--', 'context/HANDOFF.md')
        return done.returncode, done.stderr, runs()

    try:
        (repo / 'context').mkdir(parents=True)
        (repo / 'docs').mkdir()
        for name in ('context/HANDOFF.md', 'context/STATE.md', 'docs/x.txt'):
            (repo / name).write_text('# %s\n' % name)
        tool.write_text(STANDIN)
        loader.write_text(LOADER)
        git('init', '-q')
        git('add', '--', 'context/HANDOFF.md', 'context/STATE.md', 'docs/x.txt')
        git('commit', '-q', '-m', 'Notes: first')
        wrapper = repo / '.git' / 'hooks' / 'pre-commit'
        wrapper.parent.mkdir(parents=True, exist_ok=True)
        wrapper.write_text('#!/bin/sh\nexec "%s" "%s" "%s" "%s"\n' % (sys.executable, loader, LIVE, hook))
        wrapper.chmod(0o755)

        code, said, ran = commit('context/HANDOFF.md')
        report(code == 1 and HEADER in said and '  - STAND-IN refused: check context/HANDOFF.md' in said,
               '1 a clocked file, refused', 'exit %s; %s' % (code, said))
        code, said, ran = commit('context/HANDOFF.md', mode='pass')
        report(code == 0 and ran == ['check context/HANDOFF.md'], '2 a clocked file, passed',
               'exit %s; runs %r; %s' % (code, ran, said))
        code, said, ran = commit('docs/x.txt')
        report(code == 0 and ran == [], '3 another file', 'exit %s; runs %r' % (code, ran))
        code, said, ran = commit('context/HANDOFF.md', 'context/STATE.md')
        report(ran == ['check context/HANDOFF.md context/STATE.md'], '4 both notes', 'exit %s; runs %r' % (code, ran))
        code, said, ran = commit('context/STATE.md')
        report(code == 1 and ran == ['check context/STATE.md'], '5 STATE alone', 'exit %s; runs %r' % (code, ran))

        tool.rename(tmp / 'clockhead.away')
        code, said, ran = commit('context/HANDOFF.md')
        (tmp / 'clockhead.away').rename(tool)
        report(code == 1 and 'context/HANDOFF.md: its time headings are checked by context/clockhead.py, which '
               'this repository does not hold' in said, '6 no tool', 'exit %s; %s' % (code, said))

        code, said, ran = by_script(index=tmp / 'snapshot.index')
        report(code == 0 and ran == [] and HEADER not in said, "7 the backup's snapshot",
               'exit %s; runs %r; %s' % (code, ran, said))
        code, said, ran = by_script()
        report(code == 1 and ran == ['check context/HANDOFF.md'], '8 run by hand, own index',
               'exit %s; runs %r; %s' % (code, ran, said))

        alt = tmp / 'alt.index'
        git('read-tree', 'HEAD', index=alt)
        code, said, ran = commit('context/HANDOFF.md', index=alt)
        report(code == 1 and ran == ['check context/HANDOFF.md'], '9 a commit on another index',
               'exit %s; runs %r; %s' % (code, ran, said))

        code, said, ran = commit('context/HANDOFF.md', mode='crash')
        report(code == 1 and 'context/clockhead.py check: exit 2: Traceback (most recent call last): | boom' in said,
               '10 the tool crashes', 'exit %s; %s' % (code, said))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print('%d bad' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
