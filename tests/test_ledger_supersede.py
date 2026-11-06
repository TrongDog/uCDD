#!/usr/bin/env python3
"""ledger.py supersede: files set aside, recorded in the ledger and renamed beside, never deleted.

    python3 METHOD/tests/test_ledger_supersede.py      (as the bench's account, not root: two cases
                                                       lock a folder by its mode)

The decision (Michael's decision of 6 Nov 2026 on question 68): "The "moved
aside by hand" whole-file reports are recorded as superseded in the ledger,
never deleted." In a temporary top folder (a git repository on main, no
remote, the bench's check installed as the real one has it, /bench/ ignored
as the real top folder ignores the bench, its own repository) with its own
ledger (UCDD_LEDGER), its own recording flag (UCDD_RECORDING_FLAG, set before
the first commit) and a bench-like tree of three report folders in the form
runs/calpairs/PLAN/GAME_CFG-1/ac_levels/ (a report.txt and a picture each;
the names are 9068b37f's, the contents made here):

1. test_records_and_renames: two folders and one file in one call: exit 0;
   the superseded file committed alone (HEAD's only file, over the commit
   before it), its subject; one line a file with its path, sha256 (read here
   from the file's own bytes), size, why, date, the PATH named and where it
   moved; no absolute path in a record; each PATH gone from its place and
   its bytes whole at NAME.superseded-YYYYMMDD (never deleted); the modified
   and untracked files around it as they were; a second call appends its
   lines over the first commit, the earlier lines unchanged (it only grows).
2. test_refused_while_recording: the flag naming a live process: exit 1,
   "nothing is set aside while it records", refused before anything changes
   (HEAD, the index, the superseded file and every file of the tree as they
   were), with no line yet and again once one is committed; the flag's
   process gone: the flag is stale and the call goes through.
3. test_refused_commit_puts_back: a stand-in hook (the link install.sh made
   removed, never written through; it refuses while a mark file exists,
   else runs the real check) refuses the commit: exit 1, its words, "every
   PATH back under its own name", everything as it was; the same once a
   line is committed (the file's bytes as they were).
4. test_put_back_blocked: the stand-in hook makes the PATH's own name again
   (an empty folder) and refuses: exit 1, "NOT put back", "exists again";
   the new folder left as it is, the set-aside one whole beside it, HEAD and
   the index as found, no superseded file.
5. test_rename_fails_half_way: two PATHs, the second in a folder its mode
   locks: exit 1, "could not rename", "the 1 renamed before it put back",
   everything as it was.
6. test_write_fails_puts_back: the ledger folder's mode locked: exit 1,
   "could not write ledger/superseded.jsonl", "every PATH back under its own
   name", everything as it was.
7. test_refusals: each PATH refused with its reason before anything changes
   (the same snapshot), in this order: missing; recorded already (the folder
   made again at its old place, and its new file at a recorded file's
   path); a file inside a set-aside folder (by its parts); a folder holding
   a set-aside folder (found under it); outside the top folder; in the
   ledger folder; in a game library (UCDD_GAMES); in this repository's git
   folder (.git/info); in a .git of another repository (by its parts); a
   folder holding a .git (found under it); a symbolic link; a folder
   holding a link to a file, and one holding a link to a folder; a named
   pipe; a folder holding a socket; a folder holding one that cannot be
   read; a name already .superseded-YYYYMMDD; a target that exists; a folder
   with no file; one with 201 files (MAX_FILES 200); the same PATH twice,
   and a file inside a folder given.
8. test_ledger_refusals: an empty --why; the ledger folder missing; one in
   no git repository; the superseded file ending inside a line, holding a
   line that is not JSON, and one that is not a record; another file staged
   (left staged); off main; the committed line changed (it only grows).

The known-bads (lesson L4), each a fresh copy of the method package with one
line of tools/ledger.py planted, then this file run in that copy (the
draft's NOTES.md has every command and its pass lines). Each must FAIL as
written: the test or tests that fail, then FAILED (failures=N).
 K1  "        if again:" made "        if False:": 7 (one, made again, is
     refused as "exists already"); failures=1.
 K2  undo's "        left = put_back()" made "        left = []": 3, 4 and
     6; failures=3.
 K3  "    if not held.startswith(kept):" made "    if False:": 8 (the changed
     line is committed over); failures=1.
 K4  "methodlib.sha256(file)" made "methodlib.sha256(__file__)": 1;
     failures=1.
 K5  the ledger.py before this change (no supersede: argparse's "invalid
     choice", exit 2): all eight; failures=8 (absence only).
 K6  "    if busy:" made "    if False:": 2 (the bench check refuses
     instead, in its own words); failures=1.
 K7  "    if not why:" made "    if False:": 8; failures=1.
 K8  "    if on != BRANCH:" made "    if False:": 8; failures=1.
 K9  "    if beside:" made "    if False:": 8; failures=1.
 K10 "    if held and not held.endswith(b'\\n'):" made "    if False:": 8
     (refused as "not a record" instead); failures=1.
 K11 "    if old is None or not all(isinstance(entry, dict) for entry in
     old):" made "    if False:": 8 (a traceback); failures=1.
 K12 "    if not ledger.is_dir():" made "    if False:": 8 (a traceback);
     failures=1.
 K13 "    if toplevel.returncode:" made "    if False:": 8 (refused as off
     main instead); failures=1.
 K14 "        if not os.path.lexists(place):" made "        if False:": 7;
     failures=1.
 K15 "        if place.is_symlink():" made "        if False:": 7 (the link's
     target set aside); failures=1.
 K16 "        if real == top or not real.is_relative_to(top):" made
     "        if False:": 7 (a traceback); failures=1.
 K17 "        if real.is_relative_to(ledger) or ledger.is_relative_to(real):"
     made "        if False:": 7; failures=1.
 K18 "    libs = libraries()" made "    libs = []": 7 (the game's folder set
     aside); failures=1.
 K19 "        if any(real.is_relative_to(own) or own.is_relative_to(real) for
     own in gits):" made "        if False:": 7 (refused by its parts
     instead, in other words); failures=1.
 K20 "        if GIT_NAME in parts:" made "        if False:": 7; failures=1.
 K21 "        if any(SUPERSEDED_AS.search(part) for part in parts):" made
     "        if False:": 7 (refused as recorded already, by its moved_to:
     the second layer); failures=1.
 K22 "        seen.append(real)" taken out: 7 (refused at the second rename,
     "exists now", instead); failures=1.
 K23 "        if os.path.lexists(target):" made "        if False:": 7
     (refused at the rename, "exists now", instead); failures=1.
 K24 "                if path.is_symlink():" made "                if False:":
     7; failures=1.
 K25 "                if name == GIT_NAME:" made "                if False:":
     7; failures=1.
 K26 "                if SUPERSEDED_AS.search(name):" made
     "                if False:": 7 (refused as recorded already instead);
     failures=1.
 K27 "    if not place.is_dir():" made "    if False:": 7 (refused as not
     readable instead); failures=1.
 K28 "                if not path.is_file():" made "                if False:":
     7 (a traceback reading the socket); failures=1.
 K29 "os.walk(place, onerror=fail)" made "os.walk(place)": 7; failures=1.
 K30 "    if not found:" made "    if False:": 7; failures=1.
 K31 "MAX_FILES = 200 " made "MAX_FILES = 10 ** 9 ": 7; failures=1.
 K32 the rename loop's "            left = put_back()" made
     "            left = []": 5; failures=1.
 K33 "        return undo(f'could not write {name} ({error})')" made
     "        raise": 6; failures=1.
 K34 put_back's "                if os.path.lexists(real):" made
     "                if False:": 4 (the PATH renamed back over the empty
     folder); failures=1.
Not planted: the rename loop's own "if os.path.lexists(target):" (a target
made between the check and the rename needs a second process; K22 and K23
show the line refusing, "exists now"), and the git add refusal (no way to
make git add fail on one file here).
Built, not run (6 Nov 2026): every count above is a prediction (UNMEASURED).
A test that runs across midnight UTC can read two dates (the folders it
names by the first call's date): rerun it.

decides (the record and "never deleted"): Michael's decision of 6 Nov 2026
on question 68 (quoted above); decides (the file of its own, its fields, the
commit alone on main, the rename's form, a PATH missing or recorded already
refused): the agent's choice, question 69 (the main agent's ruling R5);
decides (off main, another file staged, it only grows): as commit-plan and
commit-runs (Michael's decision of 6 Nov 2026; bench/README.md: "it only
grows"); decides (the recording flag): Michael, 4 Nov 2026, L6 ("a commit
that must wait, waits"), read by supersede itself before anything changes:
the agent's choice, question 69; decides (the other refusals, several PATHs
in one commit, the way back): the agent's choice, question 69.
searched = "terms: superseded, ledger, provenance, rename, archive; hits: 204 in 35 documents (RBIL_G 20, RBIL_J 20, RBIL_L 17, DOC_BIBLIO 14, RBIL_F 11, RBIL_H 10); 6 Nov 2026"
lessons_read = "terms: supersede, ledger, rename, commit, report, hash, test, plant, recording; lessons: L11, L6, L4, L38, L30, L7, L1, L40, L3, L20, L33, L5, L17, L37, L41, L15, L21, L22, L39, L32, L42, L26, L36; 6 Nov 2026"
"""

from pathlib import Path
import hashlib
import json
import os
import shlex
import subprocess
import sys
import tempfile
import unittest

PACKAGE = Path(__file__).resolve().parent.parent
TOOL = PACKAGE / 'tools' / 'ledger.py'
HOOK = PACKAGE / 'bench' / 'hooks' / 'pre-commit'
NAME = 'ledger/superseded.jsonl'
CALPAIRS = 'bench/runs/calpairs/9068b37f'
FOLDERS = ('DOS_THNK_SQ6_C2-1', 'DOS_THNK_SQ6_A2-1', 'DOS_THNK_LSL7DOS_C2-1')
WHY = 'a whole-file AC report in ac_levels/: decision 66 (3) set its counts aside'
TIMEOUT_S = 300          # a planted known-bad that blocks ends as an error, never a hang


class Supersede(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='ledger-supersede-')
        self.addCleanup(self.tmp.cleanup)        # last: the cleanups below run before it
        self.top = Path(self.tmp.name) / 'top'
        self.ledger = self.top / 'ledger'
        self.flag = Path(self.tmp.name) / 'recording.flag'
        self.mark = Path(self.tmp.name) / 'refuse'
        # before the first commit: the hook reads its flag from the environment git hands it
        self.env = dict(os.environ, UCDD_LEDGER=str(self.ledger), UCDD_RECORDING_FLAG=str(self.flag))
        self.env.pop('UCDD_GAMES', None)
        subprocess.run(['git', 'init', '-q', '-b', 'main', str(self.top)], check=True, env=self.env)
        for key, value in (('user.name', 'Test'), ('user.email', 'test@example.com')):
            subprocess.run(['git', 'config', key, value], cwd=self.top, check=True, env=self.env)
        installed = subprocess.run(['sh', str(PACKAGE / 'install.sh'), '--bench', str(self.top)],
                                   capture_output=True, text=True, env=self.env)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.ledger.mkdir()
        # as the real top folder: the bench is its own repository, never in the top folder's
        (self.top / '.gitignore').write_text('/bench/\n')
        (self.top / 'notes.md').write_text('notes\n')
        self.reports = []
        for folder in FOLDERS:
            place = self.top / CALPAIRS / folder / 'ac_levels'
            place.mkdir(parents=True)
            (place / 'report.txt').write_text('SIGNAL ac\nWHOLE X present 1 first 1.00 gaps 0 match '
                                              f'1.00 cover 0.90\n{folder}\n')
            (place / 'mix.png').write_bytes(b'\x89PNG\r\n\x1a\n' + folder.encode())
            self.reports.append(place)
        self.git('add', '.gitignore', 'notes.md')
        self.assertEqual(self.git('commit', '-q', '-m', 'Notes: first').returncode, 0)
        self.first = self.head()

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.top, capture_output=True, text=True, env=self.env)

    def head(self):
        return self.git('rev-parse', 'HEAD').stdout.strip()

    def tool(self, *args, env=None):
        return subprocess.run([sys.executable, str(TOOL), *args], cwd=self.tmp.name, capture_output=True,
                              text=True, env=env or self.env, timeout=TIMEOUT_S)

    def lines(self):
        path = self.top / NAME
        return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []

    def snapshot(self):
        """What a refusal leaves as it was: HEAD, the index, the superseded file's bytes (None while
        there is none), and every plain file of the bench-like tree by its path, with its bytes (walked
        without following a link, a folder that cannot be read passed over; a pipe or socket is no plain
        file and is never opened)."""
        record = self.top / NAME
        files = {}
        for folder, _, names in os.walk(self.top / 'bench'):
            for name in names:
                path = Path(folder) / name
                if path.is_file() and not path.is_symlink():
                    files[path.relative_to(self.top).as_posix()] = path.read_bytes()
        return (self.head(), self.git('diff', '--cached', '--name-only').stdout,
                record.read_bytes() if record.exists() else None, files)

    def stand_in_hook(self, script):
        """The repository's pre-commit replaced by a stand-in: the link install.sh made is removed (never
        written through: it points at the method's own check), and the stand-in runs SCRIPT, then the
        real check."""
        hook = self.top / '.git' / 'hooks' / 'pre-commit'
        self.assertTrue(hook.is_symlink(), 'install.sh links the check; the test expects that link')
        hook.unlink()
        hook.write_text(f'#!/bin/sh\n{script}\nexec {shlex.quote(str(HOOK))}\n')
        hook.chmod(0o755)

    @staticmethod
    def unlock(path):
        try:
            path.chmod(0o755)
        except OSError:                          # renamed by a planted known-bad: tempfile resets it
            pass

    def test_records_and_renames(self):
        # decides: Michael's decision of 6 Nov 2026 on question 68 ("recorded as superseded in the
        # ledger, never deleted"); the file of its own, its fields, the commit alone on main, the
        # rename's form and several PATHs in one commit: the agent's choice, question 69 (R5)
        one, two, three = self.reports
        loose = three.parent / 'report.txt'        # a file as a PATH: a stand-in windowed report
        loose.write_text('VERDICT X pieces 10\n')
        want = {path.relative_to(self.top).as_posix():
                (hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_size, path.read_bytes())
                for path in (one / 'report.txt', one / 'mix.png', two / 'report.txt', two / 'mix.png', loose)}
        (self.top / 'notes.md').write_text('changed\n')
        (self.top / 'scratch.txt').write_text('scratch\n')
        done = self.tool('supersede', str(one), str(two), str(loose), '--why', WHY)
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f'ledger: committed {NAME} as ', done.stdout)
        self.assertIn('never deleted', done.stdout)
        self.assertEqual(self.git('rev-parse', 'HEAD^').stdout.strip(), self.first)
        self.assertEqual(self.git('show', '--name-only', '--format=', 'HEAD').stdout, f'{NAME}\n')
        self.assertEqual(self.git('log', '-1', '--format=%s').stdout.strip(),
                         'Ledger: superseded 3 paths, 5 files (ledger.py supersede)')
        body = self.git('log', '-1', '--format=%b').stdout
        self.assertIn("Michael's decision of 6 Nov 2026 on question 68", body)
        self.assertIn('never deleted', body)
        self.assertIn(f'Why: {WHY}', body)
        lines = self.lines()
        self.assertEqual(sorted(entry['path'] for entry in lines), sorted(want))
        dates = {entry['date'] for entry in lines}
        self.assertEqual(len(dates), 1)
        stamp = dates.pop().replace('-', '')
        self.assertRegex(stamp, r'^\d{8}$')
        for entry in lines:
            sha, size, data = want[entry['path']]
            self.assertEqual((entry['sha256'], entry['size'], entry['why']), (sha, size, WHY), entry['path'])
            self.assertTrue(entry['time'].startswith(entry['date'] + 'T'))
            self.assertFalse(entry['path'].startswith('/') or entry['moved_to'].startswith('/'))
            self.assertFalse((self.top / entry['path']).exists(), entry['path'])        # moved...
            self.assertEqual((self.top / entry['moved_to']).read_bytes(), data)         # ...never deleted
        by = {entry['path']: entry for entry in lines}
        report = by[f'{CALPAIRS}/{FOLDERS[0]}/ac_levels/report.txt']
        self.assertEqual(report['named'], f'{CALPAIRS}/{FOLDERS[0]}/ac_levels')
        self.assertEqual(report['moved_to'], f'{CALPAIRS}/{FOLDERS[0]}/ac_levels.superseded-{stamp}/report.txt')
        single = by[f'{CALPAIRS}/{FOLDERS[2]}/report.txt']
        self.assertEqual((single['named'], single['moved_to']),
                         (single['path'], f'{CALPAIRS}/{FOLDERS[2]}/report.txt.superseded-{stamp}'))
        status = self.git('status', '--porcelain').stdout
        self.assertIn(' M notes.md', status)
        self.assertIn('?? scratch.txt', status)
        self.assertNotIn('superseded', status)
        # a second call appends over the first commit; the earlier lines unchanged (it only grows)
        earlier = (self.top / NAME).read_bytes()
        committed = self.head()
        more = self.tool('supersede', str(three), '--why', WHY)
        self.assertEqual(more.returncode, 0, more.stderr)
        self.assertTrue((self.top / NAME).read_bytes().startswith(earlier))
        self.assertEqual(len(self.lines()), 7)
        self.assertEqual(self.git('rev-parse', 'HEAD^').stdout.strip(), committed)
        self.assertFalse(three.exists())
        self.assertTrue(three.with_name(f'ac_levels.superseded-{stamp}').is_dir())

    def test_refused_while_recording(self):
        # decides: Michael, 4 Nov 2026 (L6): the bench's pre-commit refuses any commit while the
        # recording flag is set ("a commit that must wait, waits"); read by supersede itself before
        # anything changes, the hook behind it: the agent's choice, question 69
        recorder = subprocess.Popen(['sleep', '60'])
        try:
            self.flag.write_text(f'{recorder.pid} calbatch test_sweep.tsv\n')
            found = self.snapshot()
            held = self.tool('supersede', str(self.reports[0]), str(self.reports[1]), '--why', WHY)
            self.assertEqual(held.returncode, 1, held.stdout)
            self.assertIn('nothing is set aside while it records', held.stderr)
            self.assertIn(f'{recorder.pid} calbatch', held.stderr)
            self.assertEqual(self.snapshot(), found)
            self.assertIsNone(found[2])
            # once a line is committed: the same, the file's bytes as they were
            self.flag.unlink()
            first = self.tool('supersede', str(self.reports[2]), '--why', WHY)
            self.assertEqual(first.returncode, 0, first.stderr)
            self.flag.write_text(f'{recorder.pid} calbatch test_sweep.tsv\n')
            found = self.snapshot()
            held = self.tool('supersede', str(self.reports[0]), '--why', WHY)
            self.assertEqual(held.returncode, 1, held.stdout)
            self.assertIn('nothing is set aside while it records', held.stderr)
            self.assertEqual(self.snapshot(), found)
            # the recorder gone: its flag is stale and ignored, here as in the hook
            recorder.kill()
            recorder.wait()
            stale = self.tool('supersede', str(self.reports[0]), '--why', WHY)
            self.assertEqual(stale.returncode, 0, stale.stderr)
        finally:
            recorder.kill()
            recorder.wait()

    def test_refused_commit_puts_back(self):
        # decides: the way back on a refused commit: the agent's choice, question 69
        self.stand_in_hook(f'if [ -e {shlex.quote(str(self.mark))} ]; then '
                           'echo "stand-in hook: refused" >&2; exit 1; fi')
        self.mark.write_text('refuse\n')
        found = self.snapshot()
        held = self.tool('supersede', str(self.reports[0]), str(self.reports[1]), '--why', WHY)
        self.assertEqual(held.returncode, 1, held.stdout)
        self.assertIn('stand-in hook: refused', held.stderr)
        self.assertIn('every PATH back under its own name', held.stderr)
        self.assertEqual(self.snapshot(), found)
        self.assertIsNone(found[2])
        # once a line is committed, a refused commit leaves the file's bytes as they were
        self.mark.unlink()
        first = self.tool('supersede', str(self.reports[2]), '--why', WHY)
        self.assertEqual(first.returncode, 0, first.stderr)
        self.mark.write_text('refuse\n')
        found = self.snapshot()
        held = self.tool('supersede', str(self.reports[0]), '--why', WHY)
        self.assertEqual(held.returncode, 1, held.stdout)
        self.assertIn('every PATH back under its own name', held.stderr)
        self.assertEqual(self.snapshot(), found)

    def test_put_back_blocked(self):
        # decides: a PATH's own name taken again in between is never renamed over, and named: the
        # agent's choice, question 69
        one = self.reports[0]
        self.stand_in_hook(f'mkdir {shlex.quote(str(one))}; echo "stand-in hook: refused" >&2; exit 1')
        head, index = self.head(), self.git('diff', '--cached', '--name-only').stdout
        data = {path.name: path.read_bytes() for path in one.iterdir()}
        held = self.tool('supersede', str(one), '--why', WHY)
        self.assertEqual(held.returncode, 1, held.stdout)
        self.assertIn('NOT put back', held.stderr)
        self.assertIn('exists again', held.stderr)
        self.assertEqual((self.head(), self.git('diff', '--cached', '--name-only').stdout), (head, index))
        self.assertFalse((self.top / NAME).exists())
        self.assertEqual(list(one.iterdir()), [])                  # the new folder, left as it is
        aside = [path for path in one.parent.iterdir() if path.name.startswith('ac_levels.superseded-')]
        self.assertEqual(len(aside), 1)
        self.assertEqual({path.name: path.read_bytes() for path in aside[0].iterdir()}, data)  # whole

    def test_rename_fails_half_way(self):
        # decides: a rename that fails puts back the ones made before it: the agent's choice, question 69
        locked = self.top / CALPAIRS / 'locked'
        inner = locked / 'ac_levels'
        inner.mkdir(parents=True)
        (inner / 'report.txt').write_text('x\n')
        locked.chmod(0o555)                          # its entries cannot be renamed
        self.addCleanup(self.unlock, locked)
        found = self.snapshot()
        held = self.tool('supersede', str(self.reports[0]), str(inner), '--why', WHY)
        self.assertEqual(held.returncode, 1, held.stdout)
        self.assertIn('could not rename', held.stderr)
        self.assertIn('the 1 renamed before it put back', held.stderr)
        self.assertEqual(self.snapshot(), found)

    def test_write_fails_puts_back(self):
        # decides: a record that cannot be written puts every PATH back: the agent's choice, question 69
        self.ledger.chmod(0o555)                     # no new file in it
        self.addCleanup(self.unlock, self.ledger)
        found = self.snapshot()
        held = self.tool('supersede', str(self.reports[0]), '--why', WHY)
        self.assertEqual(held.returncode, 1, held.stdout)
        self.assertIn(f'could not write {NAME}', held.stderr)
        self.assertIn('every PATH back under its own name', held.stderr)
        self.assertEqual(self.snapshot(), found)

    def test_refusals(self):
        # decides: a PATH missing or recorded already: the agent's choice, question 69 (R5); every other
        # refusal: the agent's choice, question 69
        one, two, three = self.reports
        done = self.tool('supersede', str(one), '--why', WHY)
        self.assertEqual(done.returncode, 0, done.stderr)
        stamp = self.lines()[0]['date'].replace('-', '')
        aside = one.with_name(f'ac_levels.superseded-{stamp}')
        one.mkdir()                                  # made again at its old place, as a new fast path
        (one / 'report.txt').write_text('LEVELS from x (sha256 0123456789ab)\n')
        outside = Path(self.tmp.name) / 'outside'
        outside.mkdir()
        (outside / 'report.txt').write_text('x\n')
        library = self.top / 'games'
        (library / 'GAME').mkdir(parents=True)
        (library / 'GAME' / 'GAME.CFG').write_text('x\n')
        (self.ledger / 'note.txt').write_text('x\n')
        info = self.top / '.git' / 'info'
        info.mkdir(exist_ok=True)
        (info / 'note').write_text('x\n')
        base = self.top / CALPAIRS
        nested = base / 'nested'                     # another repository's .git, by its name
        (nested / '.git').mkdir(parents=True)
        (nested / '.git' / 'config').write_text('x\n')
        (nested / 'report.txt').write_text('x\n')
        (base / 'link').symlink_to(two)
        (base / 'innerlink').mkdir()
        (base / 'innerlink' / 'report.txt').symlink_to(two / 'report.txt')
        (base / 'innerdir').mkdir()
        (base / 'innerdir' / 'report.txt').write_text('x\n')
        (base / 'innerdir' / 'sub').symlink_to(two)
        os.mkfifo(base / 'pipe')
        piped = base / 'piped'
        piped.mkdir()
        (piped / 'report.txt').write_text('x\n')
        # a socket file, bound by a short relative name (a socket's path has a length limit)
        subprocess.run([sys.executable, '-c', 'import socket; socket.socket(socket.AF_UNIX).bind("sock")'],
                       cwd=piped, check=True)
        shut = base / 'unreadable' / 'shut'
        shut.mkdir(parents=True)
        (base / 'unreadable' / 'report.txt').write_text('x\n')
        (shut / 'report.txt').write_text('x\n')
        shut.chmod(0)
        self.addCleanup(self.unlock, shut)
        (base / f'old.superseded-{stamp}').mkdir()
        (base / f'old.superseded-{stamp}' / 'report.txt').write_text('x\n')
        (base / 'taken').mkdir()
        (base / 'taken' / 'report.txt').write_text('x\n')
        (base / f'taken.superseded-{stamp}').mkdir()
        (base / 'empty').mkdir()
        (base / 'crowded').mkdir()
        for number in range(201):
            (base / 'crowded' / f'{number}.png').write_bytes(b'x')
        cases = [
            ((base / 'nothing',), 'does not exist'),
            ((one,), 'is recorded in ledger/superseded.jsonl already'),
            ((one / 'report.txt',), 'is recorded in ledger/superseded.jsonl already'),
            ((aside / 'report.txt',), 'is set aside already'),
            ((one.parent,), 'is set aside already'),
            ((outside,), 'is not inside'),
            ((self.ledger / 'note.txt',), 'is in the ledger folder'),
            ((library / 'GAME',), 'is in a game library'),
            ((info,), "this repository's git folder"),
            ((nested / '.git',), 'lies in a .git folder'),
            ((nested,), "a repository's own (.git)"),
            ((base / 'link',), 'is a symbolic link'),
            ((base / 'innerlink',), 'is a symbolic link'),
            ((base / 'innerdir',), 'is a symbolic link'),
            ((base / 'pipe',), 'neither a plain file nor a folder'),
            ((piped,), 'is not a plain file'),
            ((base / 'unreadable',), 'not readable'),
            ((base / f'old.superseded-{stamp}',), 'is set aside already'),
            ((base / 'taken',), 'exists already'),
            ((base / 'empty',), 'no file in it'),
            ((base / 'crowded',), 'more than 200 files'),
            ((two, two), 'named twice'),
            ((two, two / 'report.txt'), 'named twice'),
        ]
        env = dict(self.env, UCDD_GAMES=str(library))
        for paths, said in cases:
            found = self.snapshot()
            refused = self.tool('supersede', *map(str, paths), '--why', WHY, env=env)
            self.assertEqual(refused.returncode, 1, (said, paths, refused.stdout, refused.stderr))
            self.assertIn(said, refused.stderr, (said, paths))
            self.assertEqual(self.snapshot(), found, (said, paths))
        self.assertTrue((info / 'note').is_file() and (library / 'GAME' / 'GAME.CFG').is_file())

    def test_ledger_refusals(self):
        # decides: off main, another file staged, it only grows: as commit-plan and commit-runs
        # (Michael's decision of 6 Nov 2026; bench/README.md); the rest: the agent's choice, question 69
        one, two, three = self.reports
        done = self.tool('supersede', str(one), '--why', WHY)
        self.assertEqual(done.returncode, 0, done.stderr)
        path = self.top / NAME
        committed = path.read_bytes()
        found = self.snapshot()
        blank = self.tool('supersede', str(two), '--why', '  ')
        self.assertEqual(blank.returncode, 1, blank.stdout)
        self.assertIn('--why is empty', blank.stderr)
        self.assertEqual(self.snapshot(), found)
        # the ledger folder missing, and one in no git repository (git stopped from looking above)
        loose = Path(self.tmp.name) / 'loose'
        loose.mkdir()
        for env, said in ((dict(self.env, UCDD_LEDGER=str(Path(self.tmp.name) / 'gone')), 'the ledger folder'),
                          (dict(self.env, UCDD_LEDGER=str(loose), GIT_CEILING_DIRECTORIES=self.tmp.name),
                           'is in no git repository')):
            refused = self.tool('supersede', str(two), '--why', WHY, env=env)
            self.assertEqual(refused.returncode, 1, (said, refused.stdout, refused.stderr))
            self.assertIn(said, refused.stderr, said)
            self.assertEqual(self.snapshot(), found, said)
        # the file ending inside a line, holding a line that is not JSON, and one that is not a record;
        # its committed bytes put back after each
        for tail, said in ((b'{"path": "x"', 'ends inside a line'), (b'not json\n', 'is not a record'),
                           (b'[1]\n', 'is not a record')):
            path.write_bytes(committed + tail)
            found = self.snapshot()
            refused = self.tool('supersede', str(two), '--why', WHY)
            self.assertEqual(refused.returncode, 1, (said, tail, refused.stdout, refused.stderr))
            self.assertIn(said, refused.stderr, (said, tail))
            self.assertEqual(self.snapshot(), found, (said, tail))
        path.write_bytes(committed)
        # another file staged: refused, and left staged
        (self.top / 'notes.md').write_text('changed\n')
        self.git('add', 'notes.md')
        staged = self.tool('supersede', str(two), '--why', WHY)
        self.assertEqual(staged.returncode, 1, staged.stdout)
        self.assertIn('other files are staged', staged.stderr)
        self.assertEqual(self.git('diff', '--cached', '--name-only').stdout, 'notes.md\n')
        self.assertTrue(two.is_dir())
        self.git('restore', '--staged', 'notes.md')
        # off main
        self.git('checkout', '-q', '-b', 'other')
        off = self.tool('supersede', str(two), '--why', WHY)
        self.assertEqual(off.returncode, 1, off.stdout)
        self.assertIn('not main', off.stderr)
        self.assertTrue(two.is_dir())
        self.git('checkout', '-q', 'main')
        # the committed line changed: it only grows
        path.write_text(path.read_text().replace(WHY, 'another reason', 1))
        found = self.snapshot()
        grown = self.tool('supersede', str(two), '--why', WHY)
        self.assertEqual(grown.returncode, 1, grown.stdout)
        self.assertIn('it only grows', grown.stderr)
        self.assertEqual(self.snapshot(), found)


if __name__ == '__main__':
    unittest.main(verbosity=1)
