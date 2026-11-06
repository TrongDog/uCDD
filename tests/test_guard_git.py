#!/usr/bin/env python3
"""The guard treats a git command that stages, restores or checks out a protected path as a write
to it, and plan.py --save commits its own saved plan (the owner's decision of 6 Nov 2026 on
question 67 (7)).

    python3 METHOD/tests/test_guard_git.py

The decision: "the guard treats a git command that stages, restores or
checks out a guard-protected path as a write to it". In a temporary top
folder (a git repository on main with the bench's check installed, holding
its own ledger through UCDD_LEDGER and a game library through UCDD_GAMES, as
the real top folder holds both) and a second repository beside it that holds
neither (a stand-in for the bench or a uCDD worktree):

1. Every git form that stages, restores or checks out the ledger's files or
   the library is refused (exit 2): by name, by a folder or pattern that
   holds them, through git's magic (':(icase)' too), through a whole-tree
   form (a pattern exclusion beside it frees nothing), from the top folder,
   through -C, after a cd on the same line, with GIT_WORK_TREE or
   --work-tree, through a git dir's own repository, behind env (its -u and
   -C), nohup or a shell keyword, with a variable the line sets (the
   program's name too: G=git; $G ...), in code
   given to sh -c or eval, on the line after a newline, a comment, a
   here-document (an apostrophe in its body), a here-string or a
   backslash-newline; so is a writing command whose folder or path is not
   known before the line runs (a substitution, a variable the line does not
   set, cd -, popd, a cd after eval, OLDPWD, a git dir not named .git), the
   commands that write the work tree from commits there, and a git command
   redirected into the runs file.
2. The read-only commands naming them pass (log, show, diff, status,
   cat-file, ls-files, blame), and so do the writes that name only other
   files in the top folder, the dry runs, a new branch from HEAD, a commit
   whose message is a substitution or a here-document (a $ in it), read-only
   code given to sh -c or eval,
   a push from a folder the guard cannot follow, a here-document whose body
   only holds a git write (text, not a command), and every whole-tree form
   in the repository that holds no protected path, there by a variable the
   line sets too.
3. plan.py --save commits its saved plan's file alone on main (the
   consequence of 1: no hand staging of a ledger path), a changed file
   beside it left as it was; saved again, it commits nothing and says so.
4. ledger.py commit-plan refuses while another file is staged (leaving it
   staged) and off main, commits with its --why as the subject, and refuses
   a committed plan whose file changed (a saved plan never changes).
5. The guard's ledger and library rules read a word with the line's own
   variables: a removal through one is refused, one elsewhere passes.

The known-bads (lesson L4; NOTES.md of the draft has the commands):
- the guard.py, plan.py and ledger.py before this change (a copy of the
  live method package with this file added) fail 1, 3, 4 and 5: FAILED
  (failures=4). The old guard lets every git form through (1: the refused
  list comes back with each command and exit 0) and reads no variable (5),
  the old plan.py saves without committing (3: the "ledger: committed" line
  missing from its stderr), the old ledger.py has no commit-plan (4:
  "AssertionError: 2 != 1", argparse's exit);
- the guard as first drafted and reviewed (knownbad/guard_draft1.py in the
  draft's folder, in a copy of the new package) fails 1 and 5: FAILED
  (failures=2), 1's list opening with ("git add . ':!*.md'", 0, '');
- each one-line plant of NOTES.md's G4 fails the method that guards it.
2 passes on both known-bads: it guards the new rules' edges, not their
reach (plants I, L, W, AD, AG and AK fail it). Built, not run: the counts are
predictions (UNMEASURED).

decides = "the owner's decision of 6 Nov 2026 on question 67 (7): \"the guard treats a git command that stages, restores or checks out a guard-protected path as a write to it\""
searched = "terms: git, stage, restore, checkout, guard, write; hits: 2321 in 132 documents (1487 20, 1523 20, 1533 20, 1543 20, 206 20, 4031 20); 6 Nov 2026"
lessons_read = "terms: guard, git, ledger, plan, commit, hook, shell, variable; lessons: L38, L9, L20, L40, L33, L37, L10, L21, L22, L39, L31, L32, L24, L36, L23; 6 Nov 2026"
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
TOOL = PACKAGE / 'tools' / 'ledger.py'
PLAN = PACKAGE / 'matrix' / 'plan.py'
TAG = 'abcd1234'
RUNS = 'ledger/runs.jsonl'
SAVED = f'ledger/plans/{TAG}.json'
# The variable names the commands below set or read: none comes from the test's own environment.
LINE_NAMES = ('T', 'L', 'D', 'G', 'X', 'GIT_WORK_TREE', 'GIT_DIR', 'UCDD_LEDGER_RUNNER')


class GitWrites(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='guard-git-')
        self.root = Path(self.tmp.name).resolve()
        self.top, self.other = self.root / 'top', self.root / 'bench'
        for repo in (self.top, self.other):
            subprocess.run(['git', 'init', '-q', '-b', 'main', str(repo)], check=True)
            for key, value in (('user.name', 'Test'), ('user.email', 'test@example.com')):
                subprocess.run(['git', 'config', key, value], cwd=repo, check=True)
        installed = subprocess.run(['sh', str(PACKAGE / 'install.sh'), '--bench', str(self.top)],
                                   capture_output=True, text=True)
        self.assertEqual(installed.returncode, 0, installed.stderr)
        self.ledger = self.top / 'ledger'
        (self.ledger / 'plans').mkdir(parents=True)
        (self.top / SAVED).write_text(json.dumps({'tag': TAG, 'runs': []}) + '\n')
        (self.top / RUNS).write_text('{}\n')
        self.library = self.top / 'LIB'
        (self.library / 'GAME').mkdir(parents=True)
        (self.library / 'GAME' / 'GAME.EXE').write_bytes(b'MZ')
        (self.top / '.gitignore').write_text('/LIB/\n')           # as the top folder ignores its libraries
        (self.top / 'notes.md').write_text('notes\n')
        (self.other / 'file.txt').write_text('x\n')
        self.env = dict(os.environ, UCDD_LEDGER=str(self.ledger), UCDD_GAMES=str(self.library),
                        UCDD_METHOD_LOCAL=str(self.root / 'none.toml'),
                        UCDD_RECORDING_FLAG=str(self.root / 'recording.flag'))
        for name in LINE_NAMES:
            self.env.pop(name, None)
        # the guard's own PWD and OLDPWD name a folder in no work tree: a guard that read them in
        # place of the line's (plant AC) reaches nothing through them
        self.env.update(PWD=str(self.root), OLDPWD=str(self.root))
        for repo in (self.top, self.other):
            self.git(repo, 'add', '-A')
            self.assertEqual(self.git(repo, 'commit', '-q', '-m', 'first').returncode, 0)

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, repo, *args):
        return subprocess.run(['git', *args], cwd=repo, capture_output=True, text=True, env=self.env)

    def head(self):
        return self.git(self.top, 'rev-parse', 'HEAD').stdout.strip()

    def wrong(self, commands, expected, cwd):
        """The commands whose guard exit is not EXPECTED, each with its exit and what it said."""
        found = []
        for command in commands:
            call = {'tool_name': 'Bash', 'tool_input': {'command': command}, 'cwd': str(cwd)}
            done = subprocess.run([sys.executable, str(GUARD)], input=json.dumps(call),
                                  capture_output=True, text=True, env=self.env)
            if done.returncode != expected:
                found.append((command, done.returncode, done.stderr.strip()[:200]))
        return found

    def plan_save(self):
        return subprocess.run([sys.executable, str(PLAN), '--test', 'SBT16', '--save', '--format', 'json'],
                              cwd=self.root, capture_output=True, text=True, env=self.env)

    def ledger_tool(self, *args):
        return subprocess.run([sys.executable, str(TOOL), *args], cwd=self.root,
                              capture_output=True, text=True, env=self.env)

    def test_writes_refused(self):
        # decides: the owner's decision of 6 Nov 2026 on question 67 (7): "the guard treats a git
        # command that stages, restores or checks out a guard-protected path as a write to it".
        # How the guard reads what a command reaches (a whole-tree form in the top folder, a bare
        # reset and reset --soft, the commands that write the work tree from commits, a pattern
        # read as its folder and ':(icase)' as its root, a pattern exclusion freeing nothing, the
        # line's variables, a folder or path not known before the line runs read wide, code given
        # to sh -c or eval, a git dir's own repository, a newline as the shell's command break, a
        # comment and a here-document body taken out): the agent's choice, question 68 (applied, for
        # the owner to confirm: a bare reset and reset --soft stay refused in the top folder, so do
        # merge, rebase, cherry-pick, revert, pull, am and apply, and the wide reading as drafted;
        # bench/README.md beside it: "Never check out, reset or revert the ledger");
        # searched = "terms: git, reset, revert, merge, pathspec, variable, substitution; hits: 2132 in 128 documents (1487 20, 1523 20, 1533 20, 1543 20, 206 20, 4031 20); 6 Nov 2026"
        top, other, root = self.top, self.other, self.root
        named = [f'git add {RUNS}', f'git add -- {SAVED}', 'git stage ledger',
                 'git add -f LIB/GAME/GAME.EXE', "git add 'ledger/*.json'", f'git add {top}/ledger',
                 'git add :/ledger', "git add ':(top)ledger'",
                 f'git commit -m x {RUNS}', f'git commit -m x -- {SAVED}',
                 f'git restore {RUNS}', f'git restore --staged {RUNS}', 'git restore -s HEAD~1 -- ledger',
                 f'git checkout -- {RUNS}', 'git checkout HEAD -- ledger',
                 f'git reset -q -- {RUNS}', f'git reset HEAD~1 {RUNS}',
                 f'git rm --cached {RUNS}', 'git rm -r -q ledger', f'git mv {SAVED} old.json',
                 f'git stash push -- {RUNS}', 'git clean -fd LIB',
                 f'git update-index --add {RUNS}', f'git checkout-index -f -- {RUNS}',
                 f'git show HEAD:{RUNS} > {RUNS}']
        whole = ['git add -A', 'git add --all', 'git add .', 'git add -u', 'git add :/', 'git add "*"',
                 "git add -A -- . ':!ledger'", "git add . ':!*.md'", "git add -A ':!*.png'",
                 'git commit -am x', 'git commit --all -m x',
                 'git restore .', 'git checkout .', 'git checkout main', 'git checkout -f',
                 'git checkout -b x main', 'git switch main',
                 'git reset', 'git reset -q', 'git reset --hard', 'git reset --soft HEAD~1', 'git reset HEAD~1',
                 'git stash', 'git stash -m x', 'git stash pop', 'git stash apply', 'git clean -fdx',
                 'git merge x', 'git rebase main', 'git cherry-pick x', 'git revert HEAD', 'git pull',
                 'git am x.mbox', 'git apply x.patch', 'git checkout-index -a -f']
        hidden = ['git add "$(echo ledger)/runs.jsonl"', 'git add $(git ls-files ledger)',
                  'bash -c "git add -A"', "sh -c 'git stash'", 'eval git checkout -- .',
                  f"T={other}; bash -c 'git -C \"$T\" add -A'",
                  'if true; then git add -A; fi', '{ git add -A; }', "git add ':(icase)LEDGER'",
                  "git status # it's fine\ngit add -A", "cat > x.txt <<'EOF'\nMichael's note\nEOF\ngit add -A",
                  'git add \\\n  -A', 'cat <<< "x"\ngit add -A']
        elsewhere = [f'git -C {top} add {RUNS}', f'git -C {top} add -A', f'cd {top} && git add -A',
                     f'cd {top}; git commit -am x', f'GIT_WORK_TREE={top} git add -A',
                     f'git --work-tree={top} --git-dir={top}/.git add -A', f'env git -C {top} add -A',
                     f'nohup git -C {top} stash', f'git add {top}/{RUNS}',
                     f'T={top}; git -C "$T" add -A', f'T={top}; git -C "$T" add {RUNS}',
                     f'L={top}/ledger; git add "$L/runs.jsonl"',
                     f'git -C $(echo {top}) add -A', f'D=$(echo {top}); git -C "$D" add -A',
                     f'cd {top}; cd {other}; cd -; git add -A',
                     f'pushd {top}; pushd {other}; popd; git add -A',
                     f'eval cd {top}; git add -A',
                     f'env -u X git -C {top} add -A', f'env -C {top} git add -A',
                     f'export GIT_WORK_TREE={top}; git add -A',
                     f'git --git-dir={top}/.git add -A', f'GIT_DIR={top}/.git git add {RUNS}',
                     f'git --git-dir={root}/bare.git add -A',
                     f'cd {top}; git -C "$PWD" add -A', 'git -C "$OLDPWD" add -A',
                     f'cd {top}\ngit add -A',
                     f'G=git; $G -C {top} add -A', f'G="git -C {top}"; $G add -A']
        self.assertEqual(self.wrong(named + whole + hidden, 2, top) + self.wrong(elsewhere, 2, other), [])

    def test_reads_and_other_writes_allowed(self):
        # decides: the owner's decision of 6 Nov 2026 on question 67 (7): only a git command that
        # "stages, restores or checks out a guard-protected path" is a write to it, so the
        # read-only commands naming the ledger and the writes naming only other files pass. The
        # dry runs, a new branch from HEAD, a variable the line sets to another folder, a
        # substitution or a here-document in a commit's message, a here-document's body (input,
        # not commands), read-only code given to sh -c or eval, a push from a folder the guard
        # cannot follow: the agent's choice, question 68 (they stage, restore and check out no
        # protected path; the wide reading as drafted, applied, for the owner to confirm);
        # searched = "terms: git, dry run, read-only, variable; hits: 1253 in 113 documents (1543 20, 630 20, AWE 20, CS4231A 20, CS4232 20, DOC_BIBLIO 20); 6 Nov 2026"
        top, other = self.top, self.other
        message = "git commit -m \"$(cat <<'EOF'\nMichael's fix (7): 1) the guard\nEOF\n)\" -- notes.md"
        at_top = [f'git log -- {RUNS}', 'git log -p -1 -- ledger', f'git show HEAD:{RUNS}',
                  f'git show HEAD:{RUNS} > {self.root}/copy.txt', f'git diff {RUNS}',
                  'git diff --cached --name-only', 'git status', f'git status --porcelain -- {RUNS}',
                  f'git cat-file -p HEAD:{RUNS}', 'git ls-files ledger', f'git blame {RUNS}',
                  'git merge-base main HEAD',
                  'git add notes.md', 'git commit -m x', 'git commit -m "x" -- notes.md',
                  'git commit -m x notes.md', 'git restore --staged notes.md', 'git restore notes.md',
                  'git checkout -- notes.md', 'git checkout notes.md', 'git rm --cached notes.md',
                  'git reset -q -- notes.md', 'git reset notes.md',
                  'git checkout -b newbranch', 'git switch -c newbranch', 'git stash list', 'git stash show',
                  'git clean -n', 'git clean -nd', 'git add -n -A', 'git add --dry-run .',
                  'git commit --dry-run -a', 'git apply --check x.patch', 'git apply --stat x.patch',
                  message, 'echo $(git rev-parse HEAD)', 'for f in a b; do git add notes.md; done',
                  'bash -c "git status"', 'eval git log -1', 'cd -; git push origin x',
                  "cat > x.sh <<'EOF'\ngit add -A\nEOF", "git commit -F - <<'EOF'\nfix: costs $5\nEOF",
                  'G=git; $G status']
        in_other = ['git add -A', 'git add .', 'git commit -am x', 'git stash', 'git stash pop',
                    'git reset --hard', 'git reset', 'git checkout main', 'git checkout -- .',
                    'git restore .', 'git clean -fdx', 'git merge x', 'git revert HEAD',
                    f'git -C {top} add notes.md', f'cd {top} && git status', f'git -C {top} log -- {RUNS}',
                    f'T={other}; git -C "$T" add -A', f'export T={other}; git -C "$T" add -A',
                    f'env -u X git -C {top} log -1', f'T={top}; git -C "$T" status', 'G=git; $G add -A']
        self.assertEqual(self.wrong(at_top, 0, top) + self.wrong(in_other, 0, other), [])

    def test_line_variables_other_rules(self):
        # decides: the agent's choice, question 68 (the guard's ledger and library rules read a word
        # as the shell will pass it, with the line's own variables; the rules themselves are the
        # guard's before this change; the wide reading as drafted, applied, for the owner to confirm);
        # searched = "terms: guard, variable, ledger, library; hits: 570 in 83 documents (AWE 20, I386 20, INTEL486_1995 20, PBOOK 20, RBIL_K 20, RBIL_M 20); 6 Nov 2026"
        top, other = self.top, self.other
        refused = [f'L={top}/ledger; rm "$L/plans/{TAG}.json"', f'G={top}/LIB; rm -rf "$G/GAME"']
        allowed = [f'G={other}; rm -f "$G/file.txt"']
        self.assertEqual(self.wrong(refused, 2, other) + self.wrong(allowed, 0, other), [])

    def test_plan_save_commits_its_file(self):
        # decides: the agent's choice, question 68, on the owner's decision of 6 Nov 2026 on question
        # 67 (7) ("the guard treats a git command that stages, restores or checks out a
        # guard-protected path as a write to it"): with no hand staging of a saved plan, plan.py
        # --save commits its own file alone on main (applied, for the owner to confirm);
        # searched = "terms: plan, save, commit, saved plan; hits: 1057 in 96 documents (5597 20, 586B 20, 596B 20, 630 20, 686A 20, 686B 20); 6 Nov 2026"
        (self.top / 'notes.md').write_text('changed\n')
        before = self.head()
        done = self.plan_save()
        self.assertEqual(done.returncode, 0, done.stderr)
        tag = json.loads(done.stdout)['tag']
        name = f'ledger/plans/{tag}.json'
        self.assertIn(f'ledger: committed {name} as ', done.stderr)
        self.assertEqual(self.git(self.top, 'rev-parse', 'HEAD^').stdout.strip(), before)
        self.assertEqual(self.git(self.top, 'show', '--name-only', '--format=', 'HEAD').stdout, f'{name}\n')
        self.assertEqual(self.git(self.top, 'log', '-1', '--format=%s').stdout.strip(),
                         f'Plan {tag}: saved by plan.py --save')
        self.assertIn("the owner's decision of 6 Nov 2026 on question 67 (7)",
                      self.git(self.top, 'log', '-1', '--format=%b').stdout)
        self.assertIn(' M notes.md', self.git(self.top, 'status', '--porcelain').stdout)
        committed = self.head()
        again = self.plan_save()
        self.assertEqual(again.returncode, 0, again.stderr)
        self.assertIn(f'ledger: commit-plan: {name} is committed as it is', again.stderr)
        self.assertEqual(self.head(), committed)

    def test_commit_plan_refusals(self):
        # decides: the agent's choice, question 68 (applied, for the owner to confirm; commit-plan may
        # be typed by hand): commit-plan refused while another file is staged and off main, the
        # index left as found, as commit-runs is (tests/test_ledger_commit.py); a saved plan
        # never changes (methodlib.save_plan writes a
        # plan once and never over it, and lib/checks.py refuses a plan that no longer matches its
        # tag); searched = "terms: saved plan, tag, commit; hits: 1453 in 116 documents (1487 20, 4031 20, 460 20, 471 20, 496 20, 496G 20); 6 Nov 2026"
        tag = 'eeee0000'
        saved = self.ledger / 'plans' / f'{tag}.json'
        saved.write_text(json.dumps({'tag': tag, 'runs': [
            {'id': f'{tag}-001', 'test': 'T-1', 'config': {'mode': 'base'}, 'repeat': 1,
             'command': 'true'}]}) + '\n')
        (self.top / 'notes.md').write_text('changed\n')
        self.git(self.top, 'add', 'notes.md')
        start = self.head()
        staged = self.ledger_tool('commit-plan', tag)
        self.assertEqual(staged.returncode, 1, staged.stdout)
        self.assertIn('ledger: commit-plan refused: other files are staged', staged.stderr)
        self.assertEqual(self.git(self.top, 'diff', '--cached', '--name-only').stdout, 'notes.md\n')
        self.git(self.top, 'reset', '-q')
        self.git(self.top, 'checkout', '-q', '-b', 'other')
        off = self.ledger_tool('commit-plan', tag)
        self.assertEqual(off.returncode, 1, off.stdout)
        self.assertIn('not main', off.stderr)
        self.git(self.top, 'checkout', '-q', 'main')
        self.assertEqual(self.head(), start)
        done = self.ledger_tool('commit-plan', tag, '--why', 'a test plan')
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(self.git(self.top, 'log', '-1', '--format=%s').stdout.strip(),
                         f'Plan {tag}: a test plan')
        self.assertEqual(self.git(self.top, 'show', '--name-only', '--format=', 'HEAD').stdout,
                         f'ledger/plans/{tag}.json\n')
        committed = self.head()
        saved.write_text(saved.read_text().replace('T-1', 'T-2'))
        changed = self.ledger_tool('commit-plan', tag)
        self.assertEqual(changed.returncode, 1, changed.stdout)
        self.assertIn('a saved plan never changes', changed.stderr)
        self.assertEqual(self.head(), committed)


if __name__ == '__main__':
    unittest.main(verbosity=1)
