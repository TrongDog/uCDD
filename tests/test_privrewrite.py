#!/usr/bin/env python3
"""The history rewrite and the bench's rewording (tools/privrewrite.py; tightening r3.10, T12).

    python3 METHOD/tests/test_privrewrite.py

Needs git-filter-repo (2.47 or later): importable, or its git_filter_repo.py named in the
environment as GIT_FILTER_REPO. Without it the rewrite's cases are skipped and say so; the cases
of translate, lookup and reword run either way.

A made-up fork in a temporary folder: the upstream author's branch main (one of his commits
carrying a signature, his dates on his own clock, a release tag of his, and a plain tag on an
older commit of his), and the fork's own branch on top of it: commits made on another clock whose
messages and files hold a made-up first name and city, a session line, a third-party document
that names someone else by the same first name, a binary file, a code file, an annotated tag of
the fork's own. The words are made up; the real ones are never in a pushed file.

 1. run, with the third-party document not yet approved: exit 1, the report names the document
    for the owner, nothing else is wrong.
 2. run, with the document approved by path: exit 0, all seven checks pass, and in after.git:
    his branch and his two tags have the ids they had (his signed commit among them); every
    commit of the fork's own has a new id; no message or file of the fork's own holds a word; an
    approved phrase is left; a message that lost its session line ends in one newline; the
    third-party document and the binary file are byte for byte the same; the code file at the pin
    is identical; every date of the fork's own is at +0000 and the instants are the same; the
    author named in [privacy.authors] is renamed.
 3. Known-bad (L4), the two faults the first trial met: --plant unlimited (his commits are
    rewritten too: exit 1, check 2 says how many of his changed) and --plant third-party (the
    document is altered: exit 1, check 4 names it).
 4. lookup prints a commit's new id; translate rewrites a cited old id in a checkout, to the same
    length, and leaves an id that is no commit's alone.
 5. reword (a repository whose history is not rewritten): the tracked text files outside --skip
    are reworded in place, a skipped folder is left, and the changed program line that tests for
    a string is listed to be read; --dry-run changes nothing.

decides = "silent: the owner's ruling of 10 Nov 2026 (nothing personal goes to GitHub; the fork's history cleaned once); git-filter-repo(1) for what a rewrite changes"
searched = "terms: rewrite, history, signature, filter-repo; hits: 548 in 74 documents (5597 20, DOC_MEMORY 20, INTEL486_1995 20, INTEL94 20, INTEL96 20, PBOOK 20); 10 Nov 2026"
lessons_read = "terms: rewrite, history, signature, filter-repo; lessons: L28; 10 Nov 2026"
"""

from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
TOOL = PACKAGE / 'tools' / 'privrewrite.py'
NAME, CITY = 'Zebediah', 'Quillonville'
PHRASE = f'{NAME} Springfield'
SESSION = 'Claude-' + 'Session: https://claude' + '.ai/code/session_' + 'abc123'
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

[privacy]
allow_phrases = ["{PHRASE}"]

[privacy.authors]
"Old Handle" = "Claude"
'''.replace('\\\\', '\\')
APPROVED = LOCAL.replace('allow_phrases', 'allow_paths = ["Chipsets/*"]\nallow_phrases')
BINARY = b'\x00\x01' + NAME.encode() + b'\x00\x02'


def filter_repo():
    named = os.environ.get('GIT_FILTER_REPO')
    if named and Path(named).is_file():
        return named
    return '' if importlib.util.find_spec('git_filter_repo') else None


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='privrewrite-')
        self.root = Path(self.tmp.name)
        self.env = dict(os.environ, TZ='UTC', GIT_CONFIG_GLOBAL=str(self.root / 'no-gitconfig'),
                        GIT_CONFIG_NOSYSTEM='1', UCDD_RECORDING_FLAG=str(self.root / 'no.flag'))
        for name in ('GIT_AUTHOR_NAME', 'GIT_AUTHOR_EMAIL', 'GIT_COMMITTER_NAME', 'GIT_COMMITTER_EMAIL',
                     'GIT_AUTHOR_DATE', 'GIT_COMMITTER_DATE'):
            self.env.pop(name, None)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, repo, *args, env=None, input=None, text=True):
        done = subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=text,
                              env=env or self.env, input=input)
        self.assertEqual(done.returncode, 0, (args, done.stderr))
        return done.stdout.strip() if text else done.stdout

    def who(self, name, zone='UTC'):
        mail = name.lower().replace(' ', '.') + '@example.com'
        return dict(self.env, TZ=zone, GIT_AUTHOR_NAME=name, GIT_AUTHOR_EMAIL=mail,
                    GIT_COMMITTER_NAME=name, GIT_COMMITTER_EMAIL=mail)

    def write(self, repo, name, data):
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data if isinstance(data, bytes) else data.encode())
        self.git(repo, 'add', '--', name)

    def local(self, text, name='method.local.toml'):
        path = self.root / name
        path.write_text(text)
        return dict(self.env, UCDD_METHOD_LOCAL=str(path))

    def tool(self, *args, env):
        return subprocess.run([sys.executable, str(TOOL), *args], capture_output=True, text=True, env=env)

    def fork(self):
        """The made-up fork; returns its folder and the ids the cases ask about."""
        top = self.root / 'fork'
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(top)], check=True, env=self.env)
        his, ours = self.who('Upstream Author', 'Etc/GMT-2'), self.who('Claude', 'Etc/GMT+5')
        ids = {}
        self.write(top, 'src/driver.asm', 'mov ax, 1\n')
        self.write(top, 'README.md', 'his readme\n')
        self.git(top, 'commit', '-q', '-m', 'His first commit', env=his)
        ids['his_first'] = self.git(top, 'rev-parse', 'HEAD')
        self.git(top, 'tag', 'old-point', env=his)
        self.write(top, 'README.md', 'his readme, second\n')
        self.git(top, 'commit', '-q', '-m', 'His second commit', env=his)
        # his second commit again, carrying a signature: a rewrite that reaches it strips the signature
        body = self.git(top, 'cat-file', 'commit', 'HEAD')
        head, _, message = body.partition('\n\n')
        signed = (head + '\ngpgsig -----BEGIN PGP SIGNATURE-----\n \n made up, for the test\n'
                  ' -----END PGP SIGNATURE-----\n\n' + message + '\n')
        ids['his_signed'] = self.git(top, 'hash-object', '-t', 'commit', '-w', '--stdin', input=signed)
        self.git(top, 'update-ref', 'refs/heads/main', ids['his_signed'])
        self.git(top, 'reset', '-q', '--hard', 'main')
        self.git(top, 'tag', '-a', '-m', 'His release', 'v1', env=his)
        ids['his_tag'] = self.git(top, 'rev-parse', 'refs/tags/v1')
        # the fork's own
        self.git(top, 'checkout', '-q', '-b', 'work')
        self.write(top, 'notes.md', f'{NAME} decided in {CITY}\nby {PHRASE}, 1994\n')
        self.write(top, 'Chipsets/doc.txt', f'written by {NAME} Other\n')
        self.write(top, 'blob.bin', BINARY)
        self.git(top, 'commit', '-q', '-m', f'Notes: as {NAME} ruled\n\n{SESSION}', env=ours)
        ids['ours_first'] = self.git(top, 'rev-parse', 'HEAD')
        self.write(top, 'src/driver.asm', 'mov ax, 2\n')
        self.git(top, 'commit', '-q', '-m', 'Driver: a change', env=self.who('Old Handle', 'Etc/GMT+5'))
        ids['pin'] = self.git(top, 'rev-parse', 'HEAD')
        self.write(top, 'cites.md', f'the pin is {ids["pin"][:9]}; not a commit: 1234567\n')
        self.git(top, 'commit', '-q', '-m', 'Notes: the pin cited', env=ours)
        self.git(top, 'tag', '-a', '-m', f'Archived for {NAME}', 'archive/one', env=ours)
        ids['instants'] = self.git(top, 'log', '--format=%at %ct', 'work', '^main')
        return top, ids


@unittest.skipIf(filter_repo() is None, 'git-filter-repo is not importable and GIT_FILTER_REPO names no file: '
                                         'the rewrite is not tested here')
class Rewrite(Base):
    def run_tool(self, top, work, env, *more):
        named = filter_repo()
        extra = ['--filter-repo', named] if named else []
        return self.tool('run', '--source', str(top), '--work', str(self.root / work), *extra, *more, env=env)

    def test_1_unapproved_third_party_stops_it(self):
        top, ids = self.fork()
        done = self.run_tool(top, 'w1', self.local(LOCAL), '--pin', ids['pin'])
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        report = (self.root / 'w1' / 'report.txt').read_text()
        self.assertIn('BAD  3.', report)
        self.assertEqual(report.count('BAD  '), 1, report)
        self.assertIn('    Chipsets/doc.txt', report)
        self.assertNotIn(NAME, report)

    def test_2_the_rewrite(self):
        top, ids = self.fork()
        done = self.run_tool(top, 'w2', self.local(APPROVED), '--pin', ids['pin'])
        self.assertEqual(done.returncode, 0, done.stdout + done.stderr)
        work = self.root / 'w2'
        report = (work / 'report.txt').read_text()
        self.assertEqual(report.count('ok   '), 8, report)        # the seven checks, and the pin's line
        self.assertIn('messages that still cite an old id, by their new commit (0):', report)
        self.assertNotIn('BAD', report)
        before, after = work / 'before.git', work / 'after.git'
        # his history, his tags
        self.assertEqual(self.git(after, 'rev-parse', 'refs/heads/main'), ids['his_signed'])
        self.assertEqual(self.git(after, 'rev-parse', 'refs/tags/v1'), ids['his_tag'])
        self.assertEqual(self.git(after, 'rev-parse', 'refs/tags/old-point'), ids['his_first'])
        self.assertIn('gpgsig', self.git(after, 'cat-file', 'commit', 'refs/heads/main'))
        # the fork's own
        table = dict(line.split() for line in (work / 'commit-map.txt').read_text().splitlines())
        old = self.git(before, 'rev-list', 'work', '^main').split()
        self.assertEqual(len(old), 3)
        self.assertTrue(all(table[sha] != sha for sha in old), 'a commit of the fork\'s own kept its id')
        self.assertEqual(self.git(after, 'merge-base', 'work', 'main'), ids['his_signed'])
        log = self.git(after, 'log', '--format=%an|%B', 'work', '^main')
        self.assertNotIn(NAME, log)
        self.assertNotIn('session_', log)
        self.assertNotIn('Old Handle', log)
        first = self.git(after, 'cat-file', 'commit', table[ids['ours_first']], text=False)
        self.assertTrue(first.endswith(b'Notes: as the owner ruled\n'), first[-60:])
        self.assertEqual(self.git(after, 'show', 'work:notes.md'), f'the owner decided in local\nby {PHRASE}, 1994')
        self.assertNotIn(NAME, self.git(after, 'cat-file', 'tag', 'refs/tags/archive/one'))
        for name in ('Chipsets/doc.txt', 'blob.bin'):
            self.assertEqual(self.git(after, 'rev-parse', f'work:{name}'), self.git(before, 'rev-parse', f'work:{name}'))
        self.assertEqual(self.git(after, 'rev-parse', table[ids['pin']] + ':src/driver.asm'),
                         self.git(before, 'rev-parse', ids['pin'] + ':src/driver.asm'))
        zones = set(self.git(after, 'log', '--date=format:%z', '--format=%ad %cd', 'work', '^main').split())
        self.assertEqual(zones, {'+0000'})
        self.assertEqual(self.git(after, 'log', '--format=%at %ct', 'work', '^main'), ids['instants'])
        self.assertIn('+0200', self.git(after, 'log', '-1', '--date=format:%z', '--format=%ad', 'main'))

    def test_3_known_bad(self):
        top, ids = self.fork()
        env = self.local(APPROVED)
        done = self.run_tool(top, 'w3', env, '--plant', 'unlimited')
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        report = (self.root / 'w3' / 'report.txt').read_text()
        self.assertIn('BAD  2.', report)
        self.assertNotIn("0 of the keep refs' commits changed", report)
        done = self.run_tool(top, 'w4', env, '--plant', 'third-party')
        self.assertEqual(done.returncode, 1, done.stdout + done.stderr)
        report = (self.root / 'w4' / 'report.txt').read_text()
        self.assertIn('BAD  4.', report)
        self.assertIn('Chipsets/doc.txt', report)


class Words(Base):
    def test_4_lookup_and_translate(self):
        top, ids = self.fork()
        new = 'f' * 40
        table = self.root / 'map.txt'
        table.write_text(f'old                                      new\n{ids["pin"]} {new}\n'
                         f'{ids["ours_first"]} {ids["ours_first"]}\n')
        env = self.local(LOCAL)
        done = self.tool('lookup', '--map', str(table), ids['pin'][:10], 'abcdef0', env=env)
        self.assertEqual(done.returncode, 1)
        self.assertIn(f'{ids["pin"][:10]} {new}', done.stdout)
        self.assertIn('abcdef0 not in the map', done.stdout)
        skipped = self.tool('translate', '--map', str(table), str(top), '--skip', '*.md', env=env)
        self.assertIn('0 citations of 0 commits translated in 0 files', skipped.stdout)
        done = self.tool('translate', '--map', str(table), str(top), env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual((top / 'cites.md').read_text(), 'the pin is fffffffff; not a commit: 1234567\n')
        self.assertIn('1 citations of 1 commits translated in 1 files', done.stdout)

    def test_5_reword(self):
        top = self.root / 'bench'
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(top)], check=True, env=self.env)
        self.write(top, 'runs/tool.py', f'"""A tool ({NAME}, a date)."""\n# as {NAME} decided\n'
                                        f'NOTE = "for {NAME}"\nif "held for {NAME}" in verdict:\n    pass\n')
        self.write(top, 'results/r1.json', f'{{"why": "{NAME} ruled"}}\n')
        self.write(top, 'docs/a.md', f'{NAME} lives in {CITY}\n{SESSION}\nlast\n')
        self.git(top, 'commit', '-q', '-m', 'first', env=self.who('Test'))
        env = self.local(LOCAL)
        dry = self.tool('reword', str(top), '--skip', 'results/*', '--dry-run', env=env)
        self.assertEqual(dry.returncode, 0, dry.stderr)
        self.assertIn('2 files, 6 lines would be reworded', dry.stdout)
        self.assertEqual(self.git(top, 'status', '--porcelain'), '')
        done = self.tool('reword', str(top), '--skip', 'results/*', env=env)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn('2 files, 6 lines reworded', done.stdout)
        self.assertIn('to read before the commit (1)', done.stdout)
        self.assertIn('    runs/tool.py:4', done.stdout)
        self.assertNotIn(NAME, done.stdout)
        self.assertEqual((top / 'docs/a.md').read_text(), 'the owner lives in local\nlast\n')
        self.assertIn('if "held for the owner" in verdict', (top / 'runs/tool.py').read_text())
        self.assertEqual((top / 'results/r1.json').read_text(), f'{{"why": "{NAME} ruled"}}\n')
        self.assertEqual(self.git(top, 'status', '--porcelain').split(), ['M', 'docs/a.md', 'M', 'runs/tool.py'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
