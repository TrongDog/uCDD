#!/usr/bin/env python3
"""The method's checks on GitHub: build every branch head, check new commits.

    ci.py [--branch NAME ...] [--dry-run]

Run by the workflow on fixes (ci/method.yml), on every push and every hour.
For each branch (every branch on origin, or those named) that has
scripts/build.py and is not in [ci] skip_branches:
- the head is built with every variant in [identical] variants, and its
  headroom reported against [ci] limits;
- every commit made after [ci] check_after gets lib/checks.py's checks,
  apart from the ledger, which lives on the bench.
Each result is posted as a commit status (method/build on the head,
method/commits on each commit), and one that has a status already is not
checked again. --dry-run posts nothing and checks everything. A summary goes
to $GITHUB_STEP_SUMMARY when it is set, and to the output.

A method/commits status is a verdict on the commit (the owner's decision of
10 Nov 2026 on question 82). When the checker cannot check, because a worktree
or a ref the checks read is missing (missing_inputs()), it posts nothing for
any commit: the run fails and names what is missing, and the commits are read
when it is mended. A failure already posted whose text is the checker's own
fault (CHECKER_FAULTS) is no verdict: the commit is read again and the new
status posted over it (GitHub shows the newest); a failure of any other text
stands. tests/test_ci.py is its test, with its two known-bads.
"""

from pathlib import Path
import argparse
import datetime
import fnmatch
import json
import os
import re
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
import checks  # noqa: E402

CONFIG = checks.CONFIG
SIZE = re.compile(r'^(\S+): (\d+) bytes$', re.M)
# what the checker posted when it could not check (before 10 Nov 2026): no verdict, read again
CHECKER_FAULTS = ('the reference library worktree is missing',)


class Statuses:
    """Commit statuses on GitHub, or nothing at all in a dry run."""

    def __init__(self, repo, dry):
        self.repo, self.dry = repo, dry

    def has(self, sha, context):
        if self.dry:
            return False
        out = subprocess.run(['gh', 'api', f'repos/{self.repo}/commits/{sha}/statuses',
                              '--jq', '.[].context'], capture_output=True, text=True)
        return context in out.stdout.split()

    def latest(self, sha, context):
        """CONTEXT's newest status on SHA, {'state', 'description'}, or None (GitHub lists the newest first)."""
        if self.dry:
            return None
        out = subprocess.run(['gh', 'api', f'repos/{self.repo}/commits/{sha}/statuses', '--jq',
                              f'[.[] | select(.context == "{context}")][0] | {{state, description}}'],
                             capture_output=True, text=True)
        text = out.stdout.strip()
        return json.loads(text) if text and text != 'null' else None

    def post(self, sha, context, ok, description):
        if self.dry:
            return
        subprocess.run(['gh', 'api', '-X', 'POST', f'repos/{self.repo}/statuses/{sha}',
                        '-f', f'state={"success" if ok else "failure"}', '-f', f'context={context}',
                        '-f', f'description={description[:139]}'], capture_output=True, check=True)


def branches(named):
    if named:
        return named
    refs = checks.git('for-each-ref', '--format=%(refname:short)', 'refs/remotes/origin').stdout.split()
    return [ref.removeprefix('origin/') for ref in refs if ref not in ('origin', 'origin/HEAD')]


def resolve(branch):
    for ref in (f'origin/{branch}', branch):
        if checks.ref_exists(ref):
            return checks.git('rev-parse', ref + '^{commit}').stdout.strip()
    return None


def label(options):
    """A short name for a build: p128, verify-mix p128, virtual-ess p32."""
    words = options.split()
    period = words[words.index('--audio-period-frames') + 1] if '--audio-period-frames' in words else ''
    extra = [word.removeprefix('--') for word in words
             if word.startswith('--') and word not in ('--resident-audio', '--no-refill-hint', '--audio-period-frames')]
    return ' '.join([*extra, f'p{period}' if period else '']).strip() or options


def build_head(sha):
    """Each variant's result, and the least headroom seen for each limited file, with its build."""
    results, headroom = [], {}
    with tempfile.TemporaryDirectory(prefix='method-ci-') as tmp:
        tree = Path(tmp) / 'tree'
        checks.Target(sha).export(tree)
        for options in CONFIG['identical']['variants']:
            run = subprocess.run([sys.executable, 'scripts/build.py', *options.split()],
                                 cwd=tree, capture_output=True, text=True)
            if run.returncode and 'unrecognized arguments' in run.stderr:
                results.append((options, 'skipped', 'not an option on this branch'))
                continue
            if run.returncode:
                last = (run.stderr.strip().splitlines() or ['no output'])[-1]
                results.append((options, 'failed', last))
                continue
            results.append((options, 'built', ''))
            sizes = {}
            for name, size in SIZE.findall(run.stdout):
                sizes.setdefault(name, int(size))
            for name, limit in CONFIG['ci']['limits'].items():
                if name in sizes and limit - sizes[name] < headroom.get(name, (limit + 1,))[0]:
                    headroom[name] = (limit - sizes[name], label(options))
    return results, headroom


def upstream_only(sha):
    """The commits reachable from sha that are the author's: reachable from any
    [fixed] upstream_refs ref that exists. The method does not check his commits
    (r3.6; before it, six of his commits on feature branches got refused for
    lacking trailers he never agreed to write)."""
    refs = [ref for ref in CONFIG.get('fixed', {}).get('upstream_refs', []) if checks.ref_exists(ref)]
    if not refs:
        return set()
    ours = set(checks.git('rev-list', sha, *[f'^{ref}' for ref in refs]).stdout.split())
    everything = set(checks.git('rev-list', sha).stdout.split())
    return everything - ours


def commits_after(sha, cutoff):
    if not cutoff:
        return []
    since = datetime.datetime.fromisoformat(cutoff)
    if since.tzinfo is None:
        since = since.replace(tzinfo=datetime.timezone.utc)
    skip = upstream_only(sha)
    found = []
    for line in checks.git('log', '--format=%H %cI', sha).stdout.splitlines():
        commit, date = line.split()
        if commit in skip:
            continue
        if datetime.datetime.fromisoformat(date) >= since:
            found.append(commit)
    return list(reversed(found))


def missing_inputs():
    """What the commit checks read and this run cannot find: the reference library worktree (when keys are
    set), a row ref of which neither the local nor the origin/ form exists. Empty when everything is there."""
    import refcheck
    out = []
    if refcheck.KEYS:
        tree = refcheck.worktree()
        if tree is None or not tree.is_dir():
            out.append(f'the reference library worktree ({refcheck.WORKTREE or "[references].worktree unset"})')
    names = {ref.removeprefix('origin/') for ref in CONFIG['rows']['refs'] if ref != 'HEAD'}
    for name in sorted(names):
        if not (checks.ref_exists(name) or checks.ref_exists(f'origin/{name}')):
            out.append(f'the row ref {name}')
    return out


def unread(status, plant=None):
    """True when a commit with this newest method/commits STATUS is to be checked: none yet, or a failure whose
    text is the checker's own fault. PLANT 'skip_faults' (test_ci.py's): any status counts as read, the form
    before."""
    if status is None:
        return True
    if plant == 'skip_faults':
        return False
    return status.get('state') == 'failure' and (status.get('description') or '').startswith(CHECKER_FAULTS)


def check_commits(sha, cutoff, statuses, missing, line, plant=None):
    """Check and post each commit after CUTOFF on SHA that unread() admits; none when MISSING names an input the
    checks cannot find (PLANT 'post_unchecked', test_ci.py's: they are checked anyway, the form before).
    Returns how many had problems."""
    if missing and plant != 'post_unchecked':
        return 0
    checked = bad_commits = 0
    for commit in commits_after(sha, cutoff):
        if not unread(statuses.latest(commit, 'method/commits'), plant):
            continue
        message = checks.git('log', '-1', '--format=%B', commit).stdout
        problems, _ = checks.check(message, checks.Target(commit), ledger=False)
        checked += 1
        bad_commits += bool(problems)
        line['problems'] += [f'{commit[:7]}: {problem}' for problem in problems]
        statuses.post(commit, 'method/commits', not problems,
                      problems[0] if problems else 'the method\'s checks pass (the ledger is not on GitHub)')
    if checked:
        line['commits'] = f'{checked} checked, {bad_commits} with problems'
    return bad_commits


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('--branch', action='append', default=[])
    parser.add_argument('--dry-run', action='store_true')
    parser.add_argument('--repo', default=os.environ.get('GITHUB_REPOSITORY', ''))
    parser.add_argument('--check-after', help='instead of [ci] check_after')
    args = parser.parse_args()
    statuses = Statuses(args.repo, args.dry_run or not args.repo)
    cutoff = args.check_after if args.check_after is not None else CONFIG['ci'].get('check_after', '')
    report, failed = [], False
    missing = missing_inputs() if cutoff else []
    failed |= bool(missing)
    for branch in branches(args.branch):
        sha = resolve(branch)
        if (not sha or any(fnmatch.fnmatchcase(branch, pattern) for pattern in CONFIG['ci']['skip_branches'])
                or checks.git('cat-file', '-e', f'{sha}:scripts/build.py', check=False).returncode):
            continue
        line = {'branch': branch, 'head': sha[:7], 'build': 'checked before', 'headroom': '',
                'commits': 'off' if not cutoff else 'not checked: an input is missing' if missing else 'none new',
                'problems': []}
        if not statuses.has(sha, 'method/build'):
            results, headroom = build_head(sha)
            bad = [f'{options}: {why}' for options, state, why in results if state == 'failed']
            built = sum(state == 'built' for _, state, _ in results)
            free = ', '.join(f'{name} {room} free ({build})' for name, (room, build) in headroom.items())
            line['build'] = f'{built} built' + (f', {len(bad)} failed' if bad else '') + (
                f', {len(results) - built - len(bad)} skipped' if len(results) - built - len(bad) else '')
            line['headroom'] = free
            line['problems'] += bad
            statuses.post(sha, 'method/build', not bad, (bad[0] if bad else f'{built} builds; {free}'))
            failed |= bool(bad)
        failed |= bool(check_commits(sha, cutoff, statuses, missing, line))
        report.append(line)
    summary = ['| Branch | Head | Builds | Headroom | Commits |', '|---|---|---|---|---|']
    summary += [f'| {line["branch"]} | {line["head"]} | {line["build"]} | {line["headroom"]} | '
                f'{line["commits"]} |' for line in report]
    if missing:
        summary += ['', '**No commit was checked and no status posted: the checks cannot find '
                    + '; '.join(missing) + '.**']
    for line in report:
        if line['problems']:
            summary += ['', f'**{line["branch"]}**', ''] + [f'- {problem}' for problem in line['problems']]
    text = '\n'.join(summary) + '\n'
    print(text)
    if os.environ.get('GITHUB_STEP_SUMMARY'):
        with open(os.environ['GITHUB_STEP_SUMMARY'], 'a') as file:
            file.write(text)
    if args.dry_run:
        print(json.dumps({'branches': len(report), 'failed': failed}))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
