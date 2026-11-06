#!/usr/bin/env python3
"""The fork's commit-msg check lists a moved file's paths (the owner's decision of 6 Nov 2026 on
question 67 (7): "the fork's commit-msg check lists files with renames off").

    python3 METHOD/tests/test_fork_moves.py [CHECKS]

CHECKS (default: lib/checks.py of this package) is loaded as if it were lib/checks.py, so a
planted copy elsewhere imports this package's methodlib and reads its method.toml (the
known-bads, lesson L4). Each case makes a temporary git repository of its own, one commit of a
harmless file, then moves it with git mv, with rename detection on for every git command,
whatever the user's own configuration says (GIT_CONFIG_COUNT: diff.renames=true; the global and
system files off, so no hook of the user's runs in it), and runs the checks on the staged tree as
the commit-msg hook does (checks.check(message, checks.Target()), the ledger off). The two lists
the decision names are the check's lists of files: Target.files (which says whether a commit
changes code) and the game-code check's list of added files (game_code_problems).

  1 git's own listing        docs/notes.txt moved, unchanged, to docs/SETUP.EXE is one R100 entry
                             in git diff --cached --name-status; the game-code listing as it was
                             (--name-only --diff-filter=AM) names nothing; with --no-renames it
                             names docs/SETUP.EXE (the reason for the change, asserted on the
                             installed git)
  2 a program file moved in  the same move: refused, "docs/SETUP.EXE: a program, driver or disc
                             file; we never ship game code" (the game-code list)
  3 a code file moved out    src/notes.txt (a code path: method.toml [commit] code "src/*") moved
                             to attic/notes.txt: Target.files lists both paths, attic/notes.txt
                             and src/notes.txt; check() names src/notes.txt as the code it changes
                             and asks for its row ("no Issue: trailer naming the row this change
                             answers"), as a deletion of it would (Target.files)
  4 a clean move             docs/c.txt, forty plain lines, moved to docs/d.txt: no problem and no
                             code (a move is listed, not refused)

  A named comparison, printed as "info", not counted: a listing moved. docs/a.txt, three lines of a
  made-up disassembly listing (built here from numbers, so this file holds none) then forty plain
  lines, moved unchanged to docs/b.txt. The line readings (added_lines) keep git's default, so an
  unchanged move adds no lines and the listing is not read: "not refused" is expected on this
  change and before it. It shows what the decision's "lists files" leaves (question 68, part
  U2-1), and it is not this change's test.

The known-bads (lesson L4; the draft's NOTES.md has the commands): lib/checks.py before the
change: cases 2 and 3 BAD, "2 bad"; this change without --no-renames in Target.files (the game-code
list alone): case 3 BAD, "1 bad"; this change without it in the game-code list (Target.files
alone): case 2 BAD, "1 bad"; this change with the game-code check refusing every staged move (each
R entry git lists with renames on): case 4 BAD, "1 bad". Case 1 is a control with no known-bad: it
reads git's own listing, not checks.py, so no copy of checks.py can fail it; it fails only when
the installed git lists a move otherwise. Prints ok or BAD per case, the info line, and "N bad"
last; exits 1 on a BAD. Built, not run (6 Nov 2026): every count here is a prediction
(UNMEASURED).

What decides each expected value: the rule, the owner's decision of 6 Nov 2026 on question 67 (7)
("the fork's commit-msg check lists files with renames off"): case 2, the game-code list, which
question 67 (7) named (lib/checks.py:430); case 3, Target.files, the other list the check makes,
by the reading of "lists files" as the check's two lists of files, the line checks left as they
are (the agent's choice, question 68); the refusals themselves, method.toml's [games] (the
suffixes: the owner's hard rule of 20 Oct 2026, we never ship game code) and [commit] code (a code
commit names its row); git's listing of a move (R100; --diff-filter=AM keeping none of it;
--no-renames splitting it into D and A), silent: git-diff(1), asserted on the installed git as
tests/test_moves.py does for the bench's check. The comparison's "not refused" decides nothing:
it is information.

decides = "the owner's decision of 6 Nov 2026 on question 67 (7): \"the fork's commit-msg check lists files with renames off\" (case 2, the game-code list it named); case 3, Target.files: the agent's choice, question 68 (the check's two lists of files, the line checks unchanged); git's listing silent: git-diff(1), asserted here"
searched = ""terms: rename, staged, commit-msg, diff-filter; hits: 109 in 22 documents (RBIL_J 20, RBIL_G 19, RBIL_F 10, RBIL_H 9, RBIL_M 7, MSCDEX 5); 6 Nov 2026""
lessons_read = "terms: rename, commit-msg, hook, check, staged, game; lessons: L11, L4, L38, L2, L30, L7, L35, L1, L20, L40, L33, L5, L8, L13, L19, L37, L41, L10, L15, L21, L22, L12, L14, L25, L31, L32, L42, L43, L26, L36, L23; 6 Nov 2026"
"""

from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile
import types

PACKAGE = Path(__file__).resolve().parent.parent
BODY = ''.join(f'line {n}\n' for n in range(40))
# a made-up listing (address, bytes, mnemonic), built from numbers so no line of this file is one
LISTING = ''.join('%04X:%04X  %02X %02X  mov ah, %d\n' % (0x1000, 0x100 + 2 * n, 0xB4, n, n) for n in range(3))
MESSAGE = 'Notes: a file moved\n'
NO_ROW = 'no Issue: trailer naming the row this change answers'
# rename detection on for every git command here, the checks' own included (they inherit this
# environment); the user's global and system files off; the author for the scratch commits
GIT_ENV = {'GIT_CONFIG_GLOBAL': os.devnull, 'GIT_CONFIG_NOSYSTEM': '1', 'GIT_CONFIG_COUNT': '3',
           'GIT_CONFIG_KEY_0': 'diff.renames', 'GIT_CONFIG_VALUE_0': 'true',
           'GIT_CONFIG_KEY_1': 'user.name', 'GIT_CONFIG_VALUE_1': 'Test',
           'GIT_CONFIG_KEY_2': 'user.email', 'GIT_CONFIG_VALUE_2': 'test@example.com'}


def load(path):
    """checks from PATH, run as if it were this package's lib/checks.py."""
    sys.path.insert(0, str(PACKAGE / 'lib'))
    module = types.ModuleType('checks')
    module.__file__ = str(PACKAGE / 'lib' / 'checks.py')
    with open(path) as f:
        code = compile(f.read(), path, 'exec')
    sys.modules['checks'] = module
    exec(code, module.__dict__)
    return module


def git(*words):
    return subprocess.run(['git', *words], capture_output=True, text=True)


def moved(top, old, new, text):
    """A repository at TOP with OLD committed, then moved to NEW with git mv: git mv's answer."""
    top.mkdir()
    os.chdir(top)
    git('init', '-q')
    (top / old).parent.mkdir(parents=True, exist_ok=True)
    (top / old).write_text(text)
    git('add', '--', old)
    git('commit', '-q', '-m', 'Notes: first')
    (top / new).parent.mkdir(parents=True, exist_ok=True)
    return git('mv', old, new)


def main():
    checks = load(sys.argv[1] if len(sys.argv) > 1 else PACKAGE / 'lib' / 'checks.py')
    for key in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY'):
        os.environ.pop(key, None)
    os.environ.update(GIT_ENV)
    bad, here = 0, os.getcwd()
    tmp = Path(tempfile.mkdtemp(prefix='fork-moves-'))

    def report(ok, label, text):
        nonlocal bad
        bad += not ok
        print('%s %-26s %s' % ('ok  ' if ok else 'BAD ', label, text), flush=True)

    def checked():
        """check()'s (problems, code) on the staged tree; an exception as the one problem."""
        try:
            return checks.check(MESSAGE, checks.Target(), ledger=False)
        except BaseException as e:                 # a SystemExit from a failed git call included
            return ['%s: %s' % (type(e).__name__, e)], None

    def listed():
        try:
            return checks.Target().files()
        except BaseException as e:
            return '%s: %s' % (type(e).__name__, e)

    try:
        # 1. git's own listing of an unchanged move, the reason for the change
        mv = moved(tmp / 'one', 'docs/notes.txt', 'docs/SETUP.EXE', BODY)
        status = git('diff', '--cached', '--name-status').stdout
        old = git('diff', '--cached', '--name-only', '--diff-filter=AM', '-z').stdout
        new = git('diff', '--cached', '--no-renames', '--name-only', '--diff-filter=AM', '-z').stdout
        report(mv.returncode == 0 and status == 'R100\tdocs/notes.txt\tdocs/SETUP.EXE\n' and old == ''
               and new == 'docs/SETUP.EXE\0', 'git\'s own listing', 'status %r; as it was %r; renames off %r' % (
                   status, old, new))

        # 2. a program file moved in: refused by its new name (the game-code list)
        found, code = checked()
        want = 'docs/SETUP.EXE: a program, driver or disc file; we never ship game code'
        report(want in found, 'a program file moved in', ' | '.join(found) or 'NO PROBLEM FOUND')

        # 3. a code file moved out of the code paths: both paths listed, the old one read as code
        moved(tmp / 'three', 'src/notes.txt', 'attic/notes.txt', BODY)
        files = listed()
        found, code = checked()
        report(files == ['attic/notes.txt', 'src/notes.txt'] and code == ['src/notes.txt'] and NO_ROW in found,
               'a code file moved out', 'files %r; code %r; problems %s' % (files, code, ' | '.join(found) or 'none'))

        # 4. a clean move goes through
        moved(tmp / 'four', 'docs/c.txt', 'docs/d.txt', BODY)
        found, code = checked()
        report(not found and code == [], 'a clean move', '%s; code %r' % (' | '.join(found) or 'no problem', code))

        # the named comparison, not counted: an unchanged moved listing (the line readings)
        moved(tmp / 'listing', 'docs/a.txt', 'docs/b.txt', LISTING + BODY)
        found, code = checked()
        hit = [p for p in found if p.startswith('docs/b.txt:3: a disassembly listing;')]
        print('info %-26s %s' % ('a listing moved', 'refused: %s' % hit[0] if hit else
                                  'not refused (an unchanged move adds no lines: question 68, part U2-1)'),
              flush=True)
    finally:
        os.chdir(here)
        shutil.rmtree(tmp, ignore_errors=True)
    print('%d bad' % bad)
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main())
