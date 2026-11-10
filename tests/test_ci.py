#!/usr/bin/env python3
"""test_ci.py: tools/ci.py's rule of 10 Nov 2026 (the owner's decision on question 82: "A method/commits
status is a verdict on the commit"), on stubs: nothing is posted to GitHub and no git history is read.

    python3 tests/test_ci.py                         the cases below, each ok
    TEST_CI_PLANT=post_unchecked python3 tests/test_ci.py    known-bad 1: case 1 fails
    TEST_CI_PLANT=skip_faults python3 tests/test_ci.py       known-bad 2: case 2 fails

1 The reference library absent: no commit is checked and no status posted (today's ci.py, before the rule,
  posted the failure "the reference library worktree is missing").
2 A stored failure whose text is the checker's own fault: the commit is read again and the new status posted
  over it (before the rule the commit was skipped as checked).
3 A stored failure of any other text stands: the commit is not read again.
4 missing_inputs() names the library worktree when it is absent and a row ref of which neither form exists.
Each known-bad was run once at install (10 Nov 2026), one line each.
decides: silent: the owner's decision of 10 Nov 2026 on question 82 (a method rule; no document decides)
searched = "terms: commit status, verdict, checker; hits: 31 in 9 documents (PBOOK 20, RBIL_L 3, PEAK 2, INTEL486_1995 1, PORTS 1, RBIL_K 1); 10 Nov 2026"
lessons_read = "terms: check, status, ci, verdict, known-bad; lessons: L4, L11; 10 Nov 2026"
"""

from pathlib import Path
import os
import sys
import unittest
from unittest import mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'tools'))
sys.path.insert(0, str(HERE.parent / 'lib'))
import ci  # noqa: E402

PLANT = os.environ.get('TEST_CI_PLANT') or None
FAULT = ('the reference library worktree is missing (../refs): add it (git worktree add) before a code commit '
         'cites a data sheet')
KEY_RULE = '"data sheet: PCI BIOS 2.1 ...": "PCI" is not a reference key (method.toml [references].keys: ...)'


class Statuses:
    """ci.Statuses' two calls, on a dict: {sha: {'state', 'description'}}; posts kept in order."""

    def __init__(self, stored=None):
        self.stored, self.posts = dict(stored or {}), []

    def latest(self, sha, context):
        return self.stored.get(sha)

    def post(self, sha, context, ok, description):
        self.posts.append((sha, context, 'success' if ok else 'failure', description))


class Rule(unittest.TestCase):
    def run_commits(self, statuses, missing, problems):
        line = {'commits': 'none new', 'problems': []}
        with mock.patch.object(ci, 'commits_after', return_value=['c1']), \
                mock.patch.object(ci.checks, 'git', return_value=mock.Mock(stdout='a message')), \
                mock.patch.object(ci.checks, 'check', return_value=(problems, None)), \
                mock.patch.object(ci.checks, 'Target', return_value=None):
            bad = ci.check_commits('h', '2026-10-20T00:00:00+00:00', statuses, missing, line, plant=PLANT)
        return bad, line

    def test_1_library_absent_posts_nothing(self):
        statuses = Statuses()
        bad, line = self.run_commits(statuses, ['the reference library worktree (../refs)'], [FAULT])
        self.assertEqual(statuses.posts, [], 'a status was posted for a commit the checker could not check')
        self.assertEqual(bad, 0)

    def test_2_checker_fault_read_again(self):
        statuses = Statuses({'c1': {'state': 'failure', 'description': FAULT}})
        self.run_commits(statuses, [], [])
        self.assertEqual(statuses.posts, [('c1', 'method/commits', 'success',
                                           'the method\'s checks pass (the ledger is not on GitHub)')],
                         'a checker-fault failure was not read again')

    def test_3_other_failure_stands(self):
        statuses = Statuses({'c1': {'state': 'failure', 'description': KEY_RULE}})
        self.run_commits(statuses, [], [])
        self.assertEqual(statuses.posts, [], 'a verdict was read again')

    def test_4_missing_inputs(self):
        with mock.patch.object(ci, 'CONFIG', {'rows': {'refs': ['HEAD', 'notes', 'origin/notes', 'gone']}}), \
                mock.patch('refcheck.KEYS', {'X': 'x'}), mock.patch('refcheck.WORKTREE', '../refs'), \
                mock.patch('refcheck.worktree', return_value=Path('/nonexistent/refs')), \
                mock.patch.object(ci.checks, 'ref_exists', side_effect=lambda ref: ref == 'origin/notes'):
            self.assertEqual(ci.missing_inputs(), ['the reference library worktree (../refs)', 'the row ref gone'])


if __name__ == '__main__':
    unittest.main(verbosity=1)
