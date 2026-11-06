#!/usr/bin/env python3
"""The bench's check reads a moved file (the owner's decision of 6 Nov 2026).

    python3 METHOD/tests/test_moves.py

The decision: "the bench pre-commit lists staged files with renames off
(--no-renames) so a moved file is read". In a temporary bench repository
with the check installed (install.sh --bench) and a remote, so the home-path
check is on, every commit made with rename detection on, git's default:

1. git's own behaviour, the reason for the change: a file moved with git mv
   and edited is one R entry in `git diff --cached --name-status` (old path,
   new path); `--name-only` alone names the new path; the check's listing
   before the change (`--name-only --diff-filter=AM`) names nothing at all,
   since the filter drops R; with --no-renames it is a D of the old path and
   an A of the new one, and the listing names the new path.
2. A file moved and given an absolute home path is refused, by its new name.
3. A file moved, unchanged (R100), to a name the check refuses (kit/UCDD.EXE)
   is refused.
4. A clean file moved is committed: renames are read, not refused.

The known-bad (lesson L4) is the check before the change: on it 2 and 3
commit (exit 0) and fail here; 1 and 4 pass on both.

decides = "silent: the owner's ruling of 6 Nov 2026 (the decision on the 15:50Z, 21:11Z and 23:31Z reports)"
searched = "terms: rename, staged, pre-commit, diff-filter; hits: 108 in 21 documents (RBIL_J 20, RBIL_G 19, RBIL_F 10, RBIL_H 9, RBIL_M 7, MSCDEX 5); 6 Nov 2026"
lessons_read = "terms: rename, hook, commit, check, staged, backup; lessons: L11, L4, L38, L2, L30, L7, L35, L20, L40, L33, L13, L19, L37, L41, L10, L15, L22, L12, L25, L31, L32, L42, L43, L21, L26, L36, L23; 6 Nov 2026"
"""

from pathlib import Path
import os
import subprocess
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
BODY = ''.join(f'line {n}\n' for n in range(40))


class MovedFile(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='bench-moves-')
        self.top = Path(self.tmp.name) / 'top'
        remote = Path(self.tmp.name) / 'remote.git'
        subprocess.run(['git', 'init', '-q', '--bare', str(remote)], check=True)
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.top)], check=True)
        for key, value in (('user.name', 'Test'), ('user.email', 'test@example.com')):
            subprocess.run(['git', 'config', key, value], cwd=self.top, check=True)
        installed = subprocess.run(['sh', str(PACKAGE / 'install.sh'), '--bench', str(self.top)],
                                   capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.git('remote', 'add', 'origin', str(remote))
        # no flag: the bench's own runs/recording.flag must not decide these commits
        self.env = dict(os.environ, UCDD_RECORDING_FLAG=str(Path(self.tmp.name) / 'no.flag'))

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args):
        # rename detection on whatever the user's own git config says: `git -c` reaches the hook's
        # own git calls through the environment (GIT_CONFIG_PARAMETERS)
        return subprocess.run(['git', '-c', 'diff.renames=true', *args], cwd=self.top,
                              capture_output=True, text=True, env=getattr(self, 'env', None))

    def commit_new(self, name, text):
        path = self.top / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.git('add', '--', name)
        done = self.git('commit', '-q', '-m', f'Bench: {name}')
        self.assertEqual(done.returncode, 0, done.stderr)

    def test_git_hides_a_rename_from_the_old_listing(self):
        # decides: silent: git-diff(1) (renames detected by default, one R entry with both paths;
        # --diff-filter=AM keeps neither; --no-renames splits it into D and A), asserted on the
        # installed git, under the searched line above
        self.commit_new('runs/a.py', BODY)
        self.assertEqual(self.git('mv', 'runs/a.py', 'runs/b.py').returncode, 0)
        with open(self.top / 'runs/b.py', 'a') as file:
            file.write('where = "/home/someone/bench/x"\n')
        self.git('add', '--', 'runs/b.py')
        status = self.git('diff', '--cached', '--name-status').stdout.split('\n')[0].split('\t')
        self.assertTrue(status[0].startswith('R'), status)
        self.assertEqual(status[1:], ['runs/a.py', 'runs/b.py'])
        self.assertEqual(self.git('diff', '--cached', '--name-only').stdout, 'runs/b.py\n')
        old = self.git('diff', '--cached', '--name-only', '--diff-filter=AM', '-z').stdout
        self.assertEqual(old, '', 'the old listing names nothing for a rename')
        new = self.git('diff', '--cached', '--no-renames', '--name-only', '--diff-filter=AM', '-z').stdout
        self.assertEqual(new, 'runs/b.py\0')
        self.assertEqual(self.git('diff', '--cached', '--no-renames', '--name-status').stdout,
                         'D\truns/a.py\nA\truns/b.py\n')

    def test_moved_and_edited_is_read(self):
        # decides: the owner's decision of 6 Nov 2026 (the rule); the refusal itself: the owner's
        # ruling of 2 Nov 2026, the home-path check (method.toml's [[banned]] local path)
        self.commit_new('runs/a.py', BODY)
        self.git('mv', 'runs/a.py', 'runs/b.py')
        with open(self.top / 'runs/b.py', 'a') as file:
            file.write('where = "/home/someone/bench/x"\n')
        self.git('add', '--', 'runs/b.py')
        done = self.git('commit', '-q', '-m', 'Bench: moved')
        self.assertEqual(done.returncode, 1, 'a moved file with a home path went in unread')
        self.assertIn('runs/b.py:41: a local path', done.stderr)

    def test_moved_to_a_refused_name_is_read(self):
        # decides: the owner's decision of 6 Nov 2026 (the rule); the refusal itself: bench.toml's
        # refuse list and method.toml's [games] suffixes; the R100 listing, silent: git-diff(1)
        # (an unchanged move scores 100), asserted on the installed git
        self.commit_new('kit/notes.txt', BODY)
        self.git('mv', 'kit/notes.txt', 'kit/UCDD.EXE')
        self.assertTrue(self.git('diff', '--cached', '--name-status').stdout.startswith('R100\t'))
        done = self.git('commit', '-q', '-m', 'Bench: moved')
        self.assertEqual(done.returncode, 1, 'a file moved to a refused name went in unread')
        self.assertIn('kit/UCDD.EXE: a game, program, disc', done.stderr)

    def test_clean_move_goes_in(self):
        # decides: the owner's decision of 6 Nov 2026 (a moved file is read, not refused: the rule
        # reads it); the listing it reads, silent: git-diff(1), asserted on the installed git,
        # under the searched line above
        self.commit_new('runs/c.py', BODY)
        self.git('mv', 'runs/c.py', 'runs/d.py')
        done = self.git('commit', '-q', '-m', 'Bench: moved')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.git('ls-files').stdout, 'runs/d.py\n')


if __name__ == '__main__':
    unittest.main(verbosity=1)
