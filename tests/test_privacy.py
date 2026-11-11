#!/usr/bin/env python3
"""Nothing personal goes to GitHub: the checks (the owner, 10 Nov 2026; tightening r3.10, T12).

    python3 METHOD/tests/test_privacy.py

Every case runs in temporary repositories with a method.local.toml of made-up words (the real
ones are never in a pushed file, this one included): a first name, a city, an approved phrase,
an approved third-party path, and one fork-only word that is not personal. The clock is UTC
unless a case sets another.

A uCDD clone with the shared hooks (install.sh --shared):
 1. A commit whose message holds a personal word is refused; so is one that adds a line holding
    it; the refusal names the rule and never prints the word.
 2. Only added lines are read: a file that already holds the word can be edited elsewhere.
 3. The owner's approvals: a phrase in allow_phrases passes, a file under allow_paths passes; the
    same word anywhere else is refused.
 4. A session link in a message is refused (method.toml's own entry).
 5. An author identity holding a personal word is refused at the commit and at the push.
 6. The push is the last gate: commits made with the commit hooks off are refused by pre-push,
    with nothing sent; a clean branch is pushed. Known-bad: with the pre-push link removed the same
    push goes through, so it is the hook that stops it.
 7. The upstream author's commits ([fixed] upstream_refs): a rule of the fork's is not applied to
    them, a personal entry is. A merge is read for its message and identity, not its lines.
 8. The clock ([privacy] utc_dates): a commit made on another clock is refused at the commit, and
    at the push when it was made with the hooks off; a commit another committer made on his own
    clock is pushed. Known-bad: with utc_dates off the same commit goes through.
 9. The code worktrees' hook (hooks/commit-msg): an identity holding a personal word is refused;
    on a branch the change loop leaves alone ([commit] skip_branches) a personal word in the
    message is refused and the fork-only word is not; lib/checks.py names a personal entry by its
    rule and never prints the word.

A bench repository (install.sh --bench), bench scope:
10. An added personal line in a new file is refused by the pre-commit and a personal message by
    the commit-msg; the fork-only word is not refused there; a record that holds the word, moved
    unchanged, is committed; a record that already holds it is edited and committed; a file that
    did not hold it may not begin to; with no remote nothing is read.
11. The bench's push: a commit made with the hooks off that adds the word is refused; the
    bench's own main is not the upstream author's.
12. The hourly backup (bench/backup.sh) refuses a snapshot whose new lines hold a personal word
    and writes no ref; a clean snapshot is written and pushed.

13. The guard refuses `git push --no-verify` and lets `git push` and `git push -n` be.
14. privacy.py doctor: quiet on a clone whose hooks are this package's; one line for a missing
    pre-push, one for a local list with no personal word, one for a shell on another clock, one
    for a repository whose newest entry in the hourly backup's log is a refusal.
15. tools/privscan.py: a word in an old version of a file and in a message is counted (exit 1),
    the word never printed; an approved path is counted as approved; --pushed leaves out a ref
    kept aside and --own the upstream author's branch; --tree reads one commit's files and --skip
    leaves paths out; dates on another clock are counted.
16. reworded(): each entry's `replace` written, an approved phrase left as it is.
17. Without the list there is no reading: where method.local.toml names no personal word, a push
    to the fork is refused unread; the bench's push says so in a line and goes on.

decides = "silent: the owner's ruling of 10 Nov 2026 (nothing personal goes to GitHub); githooks(5) for what git gives each hook"
searched = "terms: hook, pre-push, commit-msg, personal; hits: 497 in 81 documents (DPMI09 20, INTEL94 20, INTEL96 20, PBOOK 20, RBIL_A 20, RBIL_C 20); 10 Nov 2026"
lessons_read = "terms: hook, pre-push, commit-msg, personal; lessons: L10; 10 Nov 2026"
"""

from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
GUARD = PACKAGE / 'guard' / 'guard.py'
NAME, CITY, FORKWORD = 'Zebediah', 'Quillonville', 'benchnick'
PHRASE = f'{NAME} Springfield'
SESSION = 'https://claude' + '.ai/code/session_' + 'abc123'
ELSEWHERE = 'Etc/GMT+5'             # a clock five hours behind UTC: no one's in particular
LOCAL = f'''
[[banned]]
pattern = '(?i)\\\\b{NAME.lower()}\\\\b'
why = "personal: a made-up first name"
personal = true
replace = "the owner"

[[banned]]
pattern = '\\\\b{CITY}\\\\b'
why = "personal: a made-up city"
personal = true
replace = "local"

[[banned]]
pattern = '\\\\b{FORKWORD}\\\\b'
why = "a made-up fork-only word"

[privacy]
allow_phrases = ["{PHRASE}"]
allow_paths = ["Third Party/*"]
identities_also = ["Test <test@example.com>"]
'''.replace('\\\\', '\\')


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='privacy-')
        self.root = Path(self.tmp.name)
        self.local = self.root / 'method.local.toml'
        self.local.write_text(LOCAL)
        self.env = dict(os.environ, UCDD_METHOD_LOCAL=str(self.local), TZ='UTC',
                        UCDD_RECORDING_FLAG=str(self.root / 'no.flag'),
                        GIT_CONFIG_GLOBAL=str(self.root / 'no-gitconfig'), GIT_CONFIG_NOSYSTEM='1')
        for name in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL',
                     'GIT_AUTHOR_DATE', 'GIT_COMMITTER_DATE'):
            self.env.pop(name, None)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, repo, *args, env=None, hooks=True, input=None):
        extra = [] if hooks else ['-c', 'core.hooksPath=/dev/null']
        return subprocess.run(['git', *extra, *args], cwd=repo, capture_output=True, text=True,
                              env=env or self.env, input=input)

    def repo(self, name, install=None, remote=True, branch='work'):
        top = self.root / name
        subprocess.run(['git', 'init', '-q', '-b', branch, str(top)], check=True, env=self.env)
        for key, value in (('user.name', 'Test'), ('user.email', 'test@example.com')):
            self.git(top, 'config', key, value)
        if remote:
            bare = self.root / f'{name}-remote.git'
            subprocess.run(['git', 'init', '-q', '--bare', str(bare)], check=True, env=self.env)
            self.git(top, 'remote', 'add', 'origin', str(bare))
        if install:
            done = subprocess.run(['sh', str(PACKAGE / 'install.sh'), install, str(top)],
                                  capture_output=True, text=True, env=self.env)
            self.assertEqual(done.returncode, 0, done.stderr)
        return top

    def write(self, top, name, text):
        path = top / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.git(top, 'add', '--', name)

    def commit(self, top, message='Notes: a line', hooks=True, env=None):
        return self.git(top, 'commit', '-q', '-m', message, hooks=hooks, env=env)

    def said(self, done):
        return done.stdout + done.stderr

    def there(self, name, ref):
        return self.git(self.root / f'{name}-remote.git', 'rev-parse', '-q', '--verify', ref).stdout.strip()

    def head(self, top):
        return self.git(top, 'rev-parse', 'HEAD').stdout.strip()


class Fork(Base):
    def setUp(self):
        super().setUp()
        self.top = self.repo('fork', '--shared')
        self.write(self.top, 'a.md', 'first\n')
        done = self.commit(self.top)
        self.assertEqual(done.returncode, 0, self.said(done))

    def test_01_message_and_line_refused_word_never_printed(self):
        self.write(self.top, 'b.md', 'clean\n')
        done = self.commit(self.top, f'Notes: as {NAME} ruled')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('personal: a made-up first name', self.said(done))
        self.assertNotIn(NAME, self.said(done))
        self.assertEqual(self.commit(self.top, 'Notes: as the owner ruled').returncode, 0)
        self.write(self.top, 'c.md', f'one\nlives in {CITY}\n')
        done = self.commit(self.top)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('c.md:2: personal: a made-up city', self.said(done))
        self.assertNotIn(CITY, self.said(done))

    def test_02_only_added_lines(self):
        self.write(self.top, 'old.md', f'{NAME} said so\nsecond\n')
        self.assertEqual(self.commit(self.top, hooks=False).returncode, 0)
        self.write(self.top, 'old.md', f'{NAME} said so\nsecond, edited\n')
        self.assertEqual(self.commit(self.top).returncode, 0, 'an old line was read')
        # the fork keeps no word a file already held: a new line that holds it is refused there too
        self.write(self.top, 'old.md', f'{NAME} said so\nsecond, edited\n{NAME} again\n')
        self.assertNotEqual(self.commit(self.top).returncode, 0)

    def test_03_the_owners_approvals(self):
        self.write(self.top, 'd.md', f'by {PHRASE}, 1994\n')
        self.assertEqual(self.commit(self.top).returncode, 0, 'an approved phrase was refused')
        self.write(self.top, 'Third Party/doc.txt', f'{NAME} Other wrote this\n')
        self.assertEqual(self.commit(self.top).returncode, 0, 'an approved path was refused')
        self.write(self.top, 'e.md', f'{NAME} Other wrote this\n')
        self.assertNotEqual(self.commit(self.top).returncode, 0)

    def test_04_session_link(self):
        self.write(self.top, 'f.md', 'clean\n')
        done = self.commit(self.top, f'Notes: a line\n\n{SESSION}')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('personal: a Claude session link', self.said(done))

    def test_05_identity(self):
        self.write(self.top, 'g.md', 'clean\n')
        env = dict(self.env, GIT_AUTHOR_NAME=f'{NAME} Q', GIT_AUTHOR_EMAIL='q@example.com')
        done = self.commit(self.top, env=env)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('identity: personal: a made-up first name', self.said(done))
        self.assertEqual(self.commit(self.top, hooks=False, env=env).returncode, 0)
        pushed = self.git(self.top, 'push', '-q', 'origin', 'work')
        self.assertNotEqual(pushed.returncode, 0)
        self.assertIn('identity', self.said(pushed))

    def test_06_push_is_the_last_gate(self):
        self.assertEqual(self.git(self.top, 'push', '-q', 'origin', 'work').returncode, 0)
        self.write(self.top, 'h.md', f'{CITY}\n')
        self.assertEqual(self.commit(self.top, f'Notes: {NAME}', hooks=False).returncode, 0)
        done = self.git(self.top, 'push', '-q', 'origin', 'work')
        self.assertNotEqual(done.returncode, 0)
        self.assertNotIn(NAME, self.said(done))
        self.assertNotEqual(self.there('fork', 'refs/heads/work'), self.head(self.top), 'it was sent')
        # known-bad (L4): without the hook the same push goes through
        hooks = Path(self.git(self.top, 'rev-parse', '--git-path', 'hooks').stdout.strip())
        (self.top / hooks / 'pre-push').unlink()
        self.assertEqual(self.git(self.top, 'push', '-q', 'origin', 'work').returncode, 0)

    def test_07_upstream_and_merges(self):
        # his branch, with a word only the fork's own rules refuse: his commits are not ours to check
        self.git(self.top, 'checkout', '-q', '-b', 'main')
        self.write(self.top, 'his.md', f'a {FORKWORD} of his own\n')
        self.assertEqual(self.commit(self.top, f'His {FORKWORD}', hooks=False).returncode, 0)
        self.git(self.top, 'checkout', '-q', 'work')
        merged = self.git(self.top, 'merge', '-q', '--no-ff', '-m', 'Merge his branch', 'main')
        self.assertEqual(merged.returncode, 0, self.said(merged))
        done = self.git(self.top, 'push', '-q', 'origin', 'work', 'main')
        self.assertEqual(done.returncode, 0, self.said(done))
        # the same word in a commit of ours is refused: it is the upstream refs that made the difference
        self.write(self.top, 'ours.md', f'a {FORKWORD}\n')
        self.assertEqual(self.commit(self.top, hooks=False).returncode, 0)
        self.assertNotEqual(self.git(self.top, 'push', '-q', 'origin', 'work').returncode, 0)
        self.git(self.top, 'reset', '-q', '--hard', 'HEAD~1')
        # a personal entry is read in his commits too: nothing of the owner's rides in on a sync
        self.git(self.top, 'checkout', '-q', 'main')
        self.write(self.top, 'his2.md', f'thanks to {NAME}\n')
        self.assertEqual(self.commit(self.top, 'A credit', hooks=False).returncode, 0)
        done = self.git(self.top, 'push', '-q', 'origin', 'main')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('his2.md:1: personal: a made-up first name', self.said(done))
        # a merge's own message is read
        self.git(self.top, 'checkout', '-q', 'work')
        self.git(self.top, 'checkout', '-q', '-b', 'side', 'work~1')
        self.write(self.top, 'side.md', 'clean\n')
        self.assertEqual(self.commit(self.top).returncode, 0)
        self.git(self.top, 'checkout', '-q', 'work')
        self.assertNotEqual(self.git(self.top, 'merge', '-q', '--no-ff', '-m', f'Merge for {NAME}', 'side').returncode, 0)

    def test_08_the_clock(self):
        away = dict(self.env, TZ=ELSEWHERE)
        self.write(self.top, 'i.md', 'clean\n')
        done = self.commit(self.top, env=away)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('clock offset', self.said(done))
        self.assertNotIn('0500', self.said(done))
        self.assertEqual(self.commit(self.top, hooks=False, env=away).returncode, 0)
        done = self.git(self.top, 'push', '-q', 'origin', 'work')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('clock offset', self.said(done))
        # known-bad (L4): with the rule off the same commit goes through
        off = self.root / 'off.toml'
        off.write_text(LOCAL + 'utc_dates = false\n')
        done = self.git(self.top, 'push', '-q', 'origin', 'work', env=dict(self.env, UCDD_METHOD_LOCAL=str(off)))
        self.assertEqual(done.returncode, 0, self.said(done))
        # another committer's commit, on his own clock, is his
        his = dict(away, GIT_AUTHOR_NAME='Someone Else', GIT_AUTHOR_EMAIL='else@example.com',
                   GIT_COMMITTER_NAME='Someone Else', GIT_COMMITTER_EMAIL='else@example.com')
        self.write(self.top, 'j.md', 'clean\n')
        self.assertEqual(self.commit(self.top, hooks=False, env=his).returncode, 0)
        done = self.git(self.top, 'push', '-q', 'origin', 'work')
        self.assertEqual(done.returncode, 0, self.said(done))

    def test_09_code_worktree_hook(self):
        code = self.repo('code')
        self.git(code, 'config', 'core.hooksPath', str(PACKAGE / 'hooks'))
        self.write(code, 'docs/a.md', 'first\n')
        done = self.commit(code)
        self.assertEqual(done.returncode, 0, self.said(done))
        self.write(code, 'docs/b.md', 'clean\n')
        env = dict(self.env, GIT_AUTHOR_NAME=f'{NAME} Q', GIT_AUTHOR_EMAIL='q@example.com')
        done = self.commit(code, env=env)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('identity: personal: a made-up first name', self.said(done))
        # lib/checks.py: a personal entry by its rule, the word never printed
        done = self.commit(code, f'Notes: {NAME} and a {FORKWORD}')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('the message: personal: a made-up first name', self.said(done))
        self.assertIn(f'the message has "{FORKWORD}"', self.said(done))
        self.assertNotIn(NAME, self.said(done))
        self.assertEqual(self.commit(code).returncode, 0)
        # a branch the change loop leaves alone: the personal entries still stand, the fork's own do not
        self.git(code, 'checkout', '-q', '-b', 'archive/old')
        self.write(code, 'docs/c.md', f'a {FORKWORD}\n')
        done = self.commit(code, f'Notes: {NAME}')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('personal: a made-up first name', self.said(done))
        done = self.commit(code, f'Notes: a {FORKWORD}')
        self.assertEqual(done.returncode, 0, self.said(done))


class Bench(Base):
    def setUp(self):
        super().setUp()
        self.top = self.repo('bench', '--bench', branch='main')
        self.write(self.top, 'runs/old.txt', f'as {NAME} decided\n' + 'line\n' * 30)
        self.write(self.top, 'runs/clean.txt', 'line\n' * 5)
        self.assertEqual(self.commit(self.top, 'Bench: first', hooks=False).returncode, 0)
        # the records as they stand are on the remote already: the bench's history is not rewritten
        pushed = self.git(self.top, 'push', '-q', 'origin', 'main', hooks=False)
        self.assertEqual(pushed.returncode, 0, self.said(pushed))

    def test_10_bench_scope(self):
        self.write(self.top, 'results/new.txt', f'as {NAME} decided\n')
        done = self.commit(self.top, 'Bench: a record')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('results/new.txt:1: personal: a made-up first name', self.said(done))
        self.assertNotIn(NAME, self.said(done))
        self.git(self.top, 'reset', '-q')
        (self.top / 'results/new.txt').unlink()
        # the fork-only word is the fork's rule, not the bench's
        self.write(self.top, 'runs/tool.py', f'# {FORKWORD}\n')
        self.assertEqual(self.commit(self.top, 'Bench: a tool').returncode, 0)
        # the message
        self.write(self.top, 'runs/x.txt', 'clean\n')
        self.assertNotEqual(self.commit(self.top, f'Bench: for {NAME}').returncode, 0)
        self.assertEqual(self.commit(self.top, 'Bench: for the owner').returncode, 0)
        # a record that already holds the word is edited, the new line holding it too: committed
        self.write(self.top, 'runs/old.txt', f'as {NAME} decided\n' + 'line\n' * 30 + f'archived, {NAME}\n')
        done = self.commit(self.top, 'Bench: a record re-pointed')
        self.assertEqual(done.returncode, 0, self.said(done))
        # the same record moved unchanged: nothing is added
        self.assertEqual(self.git(self.top, 'mv', 'runs/old.txt', 'runs/old.txt.superseded').returncode, 0)
        moved = self.commit(self.top, 'Bench: superseded')
        self.assertEqual(moved.returncode, 0, self.said(moved))
        # a file that did not hold it may not begin to
        self.write(self.top, 'runs/clean.txt', 'line\n' * 5 + f'as {NAME} decided\n')
        done = self.commit(self.top, 'Bench: an edit')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('runs/clean.txt:6: personal: a made-up first name', self.said(done))
        # a repository with no remote (the top folder) is not read
        alone = self.repo('top', '--bench', remote=False, branch='main')
        self.write(alone, 'notes.md', f'{NAME} in {CITY}\n')
        self.assertEqual(self.commit(alone, f'Notes: {NAME}').returncode, 0)

    def test_11_bench_push(self):
        self.write(self.top, 'runs/new.txt', f'{CITY}\n')
        self.assertEqual(self.commit(self.top, 'Bench: a line', hooks=False).returncode, 0)
        done = self.git(self.top, 'push', '-q', 'origin', 'main')
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('runs/new.txt:1: personal: a made-up city', self.said(done))
        self.assertNotEqual(self.there('bench', 'refs/heads/main'), self.head(self.top), 'it was sent')

    def test_12_hourly_backup(self):
        backup = ['sh', str(PACKAGE / 'bench' / 'backup.sh'), str(self.top)]
        (self.top / 'results').mkdir()
        (self.top / 'results' / 'work.txt').write_text(f'{CITY}\n')
        done = subprocess.run(backup, capture_output=True, text=True, env=self.env)
        self.assertNotEqual(done.returncode, 0, self.said(done))
        self.assertIn('not backed up', self.said(done))
        self.assertNotIn(CITY, self.said(done))
        self.assertNotEqual(self.git(self.top, 'rev-parse', '-q', '--verify', 'refs/backup/hourly').returncode, 0)
        (self.top / 'results' / 'work.txt').write_text('clean\n')
        # an old record edited in the working tree, still holding its word, does not stop the backup
        (self.top / 'runs' / 'old.txt').write_text(f'as {NAME} decided\n' + 'line\n' * 30 + f'archived, {NAME}\n')
        done = subprocess.run(backup, capture_output=True, text=True, env=self.env)
        self.assertEqual(done.returncode, 0, self.said(done))
        snap = self.git(self.top, 'rev-parse', '-q', '--verify', 'refs/backup/hourly').stdout.strip()
        self.assertTrue(snap)
        self.assertEqual(self.there('bench', 'refs/backup/hourly'), snap, 'the snapshot was not pushed')


class GuardDoctorScan(Base):
    def guard(self, command):
        call = {'tool_name': 'Bash', 'tool_input': {'command': command}, 'cwd': str(self.root)}
        return subprocess.run([sys.executable, str(GUARD)], input=json.dumps(call),
                              capture_output=True, text=True, env=self.env).returncode

    def test_13_guard(self):
        self.assertEqual(self.guard('git push --no-verify origin notes'), 2)
        self.assertEqual(self.guard('git push origin notes'), 0)
        self.assertEqual(self.guard('git push -n origin notes'), 0)

    def doctor(self, *repos, env=None):
        return subprocess.run([sys.executable, str(PACKAGE / 'lib' / 'privacy.py'), 'doctor', *map(str, repos)],
                              capture_output=True, text=True, env=env or self.env)

    def test_14_doctor(self):
        top = self.repo('fork', '--shared')
        self.write(top, 'a.md', 'first\n')
        self.commit(top)
        done = self.doctor(top)
        self.assertEqual(done.returncode, 0, self.said(done))
        self.assertIn('hooks in place in 1 worktrees', done.stdout)
        away = self.doctor(top, env=dict(self.env, TZ=ELSEWHERE))
        self.assertEqual(away.returncode, 1)
        self.assertIn('clock offset', away.stdout)
        hooks = Path(self.git(top, 'rev-parse', '--git-path', 'hooks').stdout.strip())
        (top / hooks / 'pre-push').unlink()
        done = self.doctor(top)
        self.assertEqual(done.returncode, 1)
        self.assertIn('no pre-push hook', done.stdout)
        empty = self.root / 'empty.toml'
        empty.write_text('')
        done = self.doctor(top, env=dict(self.env, UCDD_METHOD_LOCAL=str(empty)))
        self.assertIn('names no personal word', done.stdout)
        # the hourly backup's log: a repository whose newest entry is a refusal is named, once mended it is not
        log = self.root / 'backup.log'
        logged = self.root / 'logged.toml'
        logged.write_text(LOCAL + f'backup_log = "{log}"\n')
        seen = dict(self.env, UCDD_METHOD_LOCAL=str(logged))
        log.write_text('2026-11-10T01:17Z /somewhere/bench backed up 1234567 on refs/backup/hourly (2 paths beyond main at 89abcde)\n'
                       '2026-11-10T02:17Z /somewhere/bench not backed up: the bench\'s check refused the snapshot (above); no ref written\n'
                       '2026-11-10T02:19Z /somewhere/top backed up 7654321 on refs/backup/hourly (1 paths beyond main at fedcba9)\n')
        (top / hooks).mkdir(exist_ok=True)
        done = self.doctor(top, env=seen)
        self.assertIn('the hourly backup of bench was refused at 2026-11-10T02:17Z', done.stdout)
        self.assertNotIn('backup of top', done.stdout)
        with open(log, 'a') as file:
            file.write('2026-11-10T03:17Z /somewhere/bench backed up 2345678 on refs/backup/hourly (2 paths beyond main at 89abcde)\n')
        self.assertNotIn('hourly backup', self.doctor(top, env=seen).stdout)
        # a bench's shell on another clock is no fault: the clock is the fork's rule
        bench = self.repo('bench', '--bench', branch='main')
        self.write(bench, 'a.txt', 'first\n')
        self.commit(bench, 'Bench: first')
        done = self.doctor(bench, env=dict(self.env, TZ=ELSEWHERE))
        self.assertEqual(done.returncode, 0, self.said(done))

    def scan(self, repo, *args):
        return subprocess.run([sys.executable, str(PACKAGE / 'tools' / 'privscan.py'), str(repo), *args],
                              capture_output=True, text=True, env=self.env)

    def test_15_privscan(self):
        top = self.repo('fork', remote=False)
        self.write(top, 'a.md', f'{NAME} said\n')
        self.commit(top, f'Notes: {CITY}', env=dict(self.env, TZ=ELSEWHERE))
        self.write(top, 'a.md', 'the owner said\n')
        self.write(top, 'results/r.txt', f'{NAME}\n')
        self.commit(top, 'Notes: reworded')
        done = self.scan(top, '--list')
        self.assertEqual(done.returncode, 1, self.said(done))
        self.assertIn('personal: a made-up first name: messages 0, identities 0, file names 0, '
                      'file versions 2 in 2 files', done.stdout)
        self.assertIn('personal: a made-up city: messages 1', done.stdout)
        self.assertIn('history only', done.stdout)
        self.assertIn('dates on a clock other than UTC: 1 of 2', done.stdout)
        self.assertNotIn(NAME, done.stdout)
        self.assertNotIn(CITY, done.stdout)
        # --pushed reads the branches, the tags and the remotes' refs, not a ref kept aside (the old
        # history a rewrite leaves under refs/old); --own leaves the upstream author's branch out
        kept = self.repo('kept', remote=False, branch='main')
        self.write(kept, 'his.md', f'a credit to {NAME}\n')
        self.commit(kept, 'His commit')
        self.git(kept, 'checkout', '-q', '-b', 'work')
        self.write(kept, 'old.md', f'{CITY}\n')
        self.commit(kept, 'Notes: an old line')
        self.git(kept, 'update-ref', 'refs/old/heads/work', 'HEAD')
        self.git(kept, 'reset', '-q', '--hard', 'main')
        self.write(kept, 'new.md', 'clean\n')
        self.commit(kept, 'Notes: a clean line')
        self.assertIn('personal: a made-up city: messages 0, identities 0, file names 0, file versions 1',
                      self.scan(kept).stdout)
        pushed = self.scan(kept, '--pushed')
        self.assertEqual(pushed.returncode, 1, self.said(pushed))
        self.assertIn('personal: a made-up city: messages 0, identities 0, file names 0, file versions 0',
                      pushed.stdout)
        self.assertEqual(self.scan(kept, '--pushed', '--own').returncode, 0)
        # one commit's files: the old version of a.md is not among them; results/ left out by --skip
        done = self.scan(top, '--tree', 'HEAD')
        self.assertEqual(done.returncode, 1, self.said(done))
        self.assertIn('file versions 1 in 1 files', done.stdout)
        done = self.scan(top, '--tree', 'HEAD', '--skip', 'results/*')
        self.assertEqual(done.returncode, 0, self.said(done))
        clean = self.repo('clean', remote=False)
        self.write(clean, 'Third Party/doc.txt', f'{NAME} Other\n')
        self.write(clean, 'b.md', f'by {PHRASE}\n')
        self.commit(clean, 'Notes: a document')
        done = self.scan(clean)
        self.assertEqual(done.returncode, 0, self.said(done))
        self.assertIn('approved by the owner (allow_paths): 1 files', done.stdout)

    def test_17_without_the_list(self):
        empty = self.root / 'empty.toml'
        empty.write_text('')
        bare = dict(self.env, UCDD_METHOD_LOCAL=str(empty))
        top = self.repo('fork', '--shared')
        self.write(top, 'a.md', 'first\n')
        self.assertEqual(self.commit(top).returncode, 0)
        done = self.git(top, 'push', '-q', 'origin', 'work', env=bare)
        self.assertNotEqual(done.returncode, 0)
        self.assertIn('nothing is pushed to the fork unread', self.said(done))
        self.assertEqual(self.git(top, 'push', '-q', 'origin', 'work').returncode, 0)
        bench = self.repo('bench', '--bench', branch='main')
        self.write(bench, 'a.txt', 'first\n')
        self.assertEqual(self.commit(bench, 'Bench: first').returncode, 0)
        done = self.git(bench, 'push', '-q', 'origin', 'main', env=bare)
        self.assertEqual(done.returncode, 0, self.said(done))
        self.assertIn('not readable here', self.said(done))

    def test_16_reworded(self):
        code = ('import sys; sys.path.insert(0, sys.argv[1]); import privacy; '
                'sys.stdout.write(privacy.reworded(sys.stdin.read()))')
        text = f'{NAME} of {CITY}; by {PHRASE}; {NAME.lower()}\n'
        done = subprocess.run([sys.executable, '-c', code, str(PACKAGE / 'lib')], input=text,
                              capture_output=True, text=True, env=self.env)
        self.assertEqual(done.stdout, f'the owner of local; by {PHRASE}; the owner\n', done.stderr)


if __name__ == '__main__':
    unittest.main(verbosity=1)
