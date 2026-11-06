#!/usr/bin/env python3
"""The results ledger: what the runners ran, on which binaries, and the verdict.

    ledger.py record PLAN RUN pass|fail --build-dir DIR [--tool FILE ...]
                     [--output FILE ...] [--note TEXT]
                     [--bench-commit HASH [--bench-changed N]]
    ledger.py show PLAN
    ledger.py spot PLAN [-n 2]
    ledger.py audit PLAN
    ledger.py commit-runs PLAN [--why TEXT] [--dry-run]     (a runner's only)
    ledger.py commit-plan PLAN [--why TEXT]
    ledger.py supersede PATH ... --why TEXT

record is for the runners (plan_run.py, which regress.sh runs through;
sndreg; calbatch.py) to call once a run is judged; the Claude Code guard
refuses it typed by hand. (Corrected 6 Nov 2026, the rule 7 form. Old text:
"the runners (regress.sh, sndreg, game_live.py, probe_test.py)"; regress.sh
records through plan_run.py, and game_live.py and probe_test.py call no
ledger.)
The plan must have been saved first (plan.py --save) and the run must be one
of its runs. --build-dir is the directory the run's UCDD.EXE came from; a run
without uCDD (mode base) has none. --tool pins the instruments by hash (the
bench is not versioned): sndreg.py, audiocmp.py, the probe program. With
UCDD_SPOT=1 in the environment the entry is a spot check, which audit
compares with the original. --bench-commit is the bench repository's commit
the plan started from, read once by the runner before anything records, and
--bench-changed N how many tracked files differed from it then; the runner
names those files once, in its plan's log, not on each entry (Michael's
decision of 6 Nov 2026: "the plan's commit hash is in the ledger"). With every
bench change a plan uses committed before the plan starts, N is 0 (results
records calbatch's rolling archive re-pointed aside: the README, "What an
entry holds") and the hash names the bench's tracked files at the plan's
start; runs/src (the
method), ignored files (the fixtures' pinned builds, kit, vms) and untracked
files are not covered. An entry made without them says null; calbatch.py,
plan_run.py and sndreg pass them, sndreg run by plan_run the plan's own, as
plan_run read it at the plan's start (Michael's decision of 6 Nov 2026 on
question 67 (7): "every runner that writes ledger rows (plan_run.py, sndreg)
records the bench's commit hash and ends with commit-runs"; runs/ledgerend.py;
built, not run). Corrected 6 Nov 2026 (the rule 7 form). Old text: "so far
only calbatch.py passes them (plan_run.py and sndreg: question 67)".

commit-runs is for the runners at a plan's end (calbatch.py's and
plan_run.py's plans at their ends, sndreg run by hand at its own end when it
wrote its entry; under plan_run sndreg commits nothing and plan_run's end
takes its lines; the same decision, built, not run; corrected 6 Nov 2026,
the rule 7 form, old text: "commit-runs is for the batch runner (calbatch.py)
at a plan's end"): the runs file committed alone on main in the repository
that holds the ledger (the top folder), the message naming the plan, why it
ended and its verdicts
(Michael's decision of 6 Nov 2026: "the ledger's runs file on the top
folder's main is committed by the tool at each plan's end (calbatch invoking
ledger), never by the agent's hand and no longer by the backup"). It refuses
when anything else is staged, when the branch is not main, and when the file
is not its last commit's lines with lines added after them (the ledger only
grows); the commit goes through the repository's own pre-commit (the bench's
check, which refuses while a plan records), and a refused commit leaves the
index as it found it. Nothing new: nothing committed, and it prints "nothing
new" (the runner reads that from its stdout). The base it names is the runs
file's own last commit (git log -1 on its path), with HEAD beside it, since
HEAD is often a later commit of the notes. --dry-run says what it would
commit and the file's size beside the bench check's limit, which skips this
file by its path (the same decision: "the bench size check excludes the
ledger's runs file by path, and from A7 the ledger rolls the file per gate";
bench/hooks/pre-commit, built, not run; changed 6 Nov 2026 with that check,
old text: "the file's size against the bench check's limit"), and commits
nothing. Exit 0 committed, nothing new or a dry run; 1 refused.

commit-runs runs only when a runner invoked it (Michael's decision of 6 Nov
2026 on question 67 (7): "`ledger.py commit-runs` refuses to run unless
invoked by calbatch (a token calbatch sets), so a hand invocation fails"; its
third change has plan_run.py and sndreg end with commit-runs too, so they are
runners here: RUNNERS). The runner puts RUNNER_TOKEN=<its script's file
name>:<its process id> in the environment of its commit-runs call, run as its
own child with no shell between. commit-runs reads the token, it does not
trust it: the process it names must be commit-runs' own parent and must run
that script (its command line in /proc); otherwise it refuses before it reads
anything, --dry-run included, and the next plan's end takes the lines. The
guard refuses the token set by hand and commit-runs typed by hand. The three
runners, and --dry-run refused by hand by the decision's "refuses to run":
the agent's choice, confirmed by Michael 6 Nov 2026 (68.1, 68.3 (a)). Built,
not run.

commit-plan is plan.py --save's: the saved plan's file committed alone on
main in the repository that holds the ledger, as commit-runs commits the runs
file (refused off main and while anything else is staged; through the
repository's own pre-commit; the index left as found when refused), since the
guard treats a git command that stages a ledger path as a write to it (the
same decision: "the guard treats a git command that stages, restores or
checks out a guard-protected path as a write to it"). A saved plan never
changes (methodlib.save_plan writes it once): a file that differs from its
committed copy is refused; one committed as it is commits nothing and says
so. Typed by hand it is allowed (the agent's choice,
confirmed by Michael 6 Nov 2026 (68.1)): it commits
a saved plan whose commit at the save was refused (while a plan records the
top folder's check refuses any commit). Its subject is "Plan <tag>:
<--why>", "saved by plan.py --save" when none is given. Exit 0 committed or
committed already; 1 refused. Built, not run.

supersede is for files set aside (Michael's decision of 6 Nov 2026 on
question 68: "The "moved aside by hand" whole-file reports are recorded as
superseded in the ledger, never deleted"). Each PATH, a file or a report
folder with every file under it, is recorded in the ledger's file of its own,
superseded.jsonl beside the runs file (SUPERSEDED), one line a file: its
path, sha256 and size, why (--why), the date and time (UTC), the PATH named,
where the file moved to, and the host. Paths are written relative to the top
of the repository that holds the ledger (the top folder), never absolute.
Each PATH is then renamed beside itself to NAME.superseded-YYYYMMDD (the UTC
date), never deleted, and the file is committed alone on main as commit-plan
commits a saved plan: refused off main and while anything else is staged,
through the repository's own pre-commit (which refuses while a plan
records), and refused when the file's committed lines changed (it only
grows, as the runs file). Before anything changes it also refuses: an empty
--why; a plan recording (the recording flag read as the bench's pre-commit
reads it, recording_line: L6, so nothing is renamed or staged beside a
recording, the hook's refusal kept behind it); a ledger folder that does not
exist or lies in no git repository; a file that ends inside a line or holds
a line that is not a record; a PATH that does not exist, or one already
recorded (the PATH or any file under it, as a file's path, a PATH named or
a place a file moved to, on any earlier line: a path is superseded once);
one outside that repository or its top itself; one in or around the ledger
folder; one in or around a game library (the guard's reading: UCDD_GAMES,
else method.toml's [games] paths; this command renames with no guard
between); one in or around this repository's own git folder (git rev-parse
--git-dir and --git-common-dir), one with a part named .git (another
repository's, or a worktree's file), and one holding a .git; a symbolic link
(the PATH or anything under it); a name in the NAME.superseded-YYYYMMDD form
(the PATH, any folder above it inside the repository, or anything under it:
set aside already); a target that exists; anything that is neither a plain
file nor a folder; a folder that cannot be read whole; a folder with no file
or with more than MAX_FILES (counted as they are found, so a mistaken PATH
such as runs/ is refused before its files are read: L21); and two PATHs one
inside the other. The renames come first and the commit last: a rename that
fails, a record that cannot be written and a refused commit each put
everything back (the file's bytes, the index, each PATH under its own name),
say so, and name any PATH that could not be put back (its own name taken
again in between). Several PATHs go in one call and one commit
(alignpairs.py --supersede-whole-file's four). Typed by hand it is allowed,
as commit-plan. Exit 0 committed; 1 refused.
Not the bench's archive of superseded captures (results/archive/captures.tsv,
the manifest with each hash; $UCDD_ARCHIVE/captures/ on the backup disk:
the bench's CLAUDE.md): that moves captures off this machine to the backup disk,
which is no work area; the decision says "in the ledger" and "never
deleted", and R5 "renamed beside", so a superseded report stays where it
was, renamed, and its record is in the ledger. Whether superseded.jsonl
should name the archive's manifest (or the manifest these records) at A7:
question 69.
The guard covers the file as part of the ledger folder: an edit of it and a
git command that stages it are refused; a shell command naming it by a
relative path is not (names_ledger: question 69).
decides (the record, "never deleted"): Michael's decision of 6 Nov 2026 on
question 68 (quoted above). decides (a file of its own and its name, its
fields, the commit alone on main as commit-plan, the rename to
NAME.superseded-YYYYMMDD, the refusals of a PATH already recorded or
missing): the agent's choice, question 69 (the main agent's ruling R5).
decides (the recording flag read before anything changes): Michael, 4 Nov
2026, L6 ("the bench's pre-commit refuses any commit while the recording
flag is set ... a commit that must wait, waits"), read here as well: the
agent's choice, question 69 (the review of 6 Nov 2026). decides (the other
refusals, several PATHs in one commit, the UTC date, MAX_FILES 200, the
renames before the commit and put back on a failure, typed by hand
allowed): the agent's choice, question 69.
decides (the mechanism as a whole): silent: no document in the library
decides it (the search below, its hits read), the agent's choice, question 69;
searched = "terms: superseded, ledger, provenance, rename, archive; hits: 204 in 35 documents (RBIL_G 20, RBIL_J 20, RBIL_L 17, DOC_BIBLIO 14, RBIL_F 11, RBIL_H 10); 6 Nov 2026"
lessons_read = "terms: supersede, ledger, rename, commit, report, hash, recording, git; lessons: L11, L6, L38, L40, L3, L20, L33, L5, L37, L15, L21, L22, L39, L32, L24, L36; 6 Nov 2026"
Built, not run (6 Nov 2026): tests/test_ledger_supersede.py, its known-bads in
its docstring.

lessons_read = "terms: ledger, commit, plan, runner, flag, backup, batch, hook; lessons: L6, L38, L2, L1, L9, L20, L40, L33, L37, L10, L22, L39, L32, L36; 6 Nov 2026"
lessons_read = "terms: ledger, commit, token, runner, plan, guard; lessons: L38, L1, L20, L40, L33, L37, L22, L39, L32, L24, L36; 6 Nov 2026"
"""

from pathlib import Path
import argparse
import collections
import datetime
import json
import os
import platform
import random
import re
import subprocess
import sys
import tomllib

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'lib'))
import methodlib  # noqa: E402

BRANCH = 'main'      # the top folder's working branch (bench/README.md; the decision's "on the top folder's main")
DECISION = "Michael's decision of 6 Nov 2026"
DECISION_67 = "Michael's decision of 6 Nov 2026 on question 67"
COMMIT_HASH = re.compile(r'^[0-9a-f]{40}([0-9a-f]{24})?$')     # SHA-1, or SHA-256 repositories
# The runners' token (DECISION_67 (7)): guard/guard.py's RUNNER_TOKEN, the same name
# (tests/test_commit_token.py checks that the two agree); and the runners that set it, by their
# scripts' file names: calbatch.py, and plan_run.py and sndreg, which the decision's third change
# has end with commit-runs too.
RUNNER_TOKEN = 'UCDD_LEDGER_RUNNER'
RUNNERS = ('calbatch.py', 'plan_run.py', 'sndreg.py')
# supersede (DECISION_68): the decision's words; the ledger's file of its own, beside the runs file;
# the form a superseded PATH is renamed to; the most files one PATH may hold (a report folder holds
# a handful: audiocmp writes report.txt and four pictures, its docstring; UNMEASURED, the folders
# not listed, L21), counted as they are found
DECISION_68 = "Michael's decision of 6 Nov 2026 on question 68"
NEVER_DELETED = ('The "moved aside by hand" whole-file reports are recorded as superseded in the '
                 'ledger, never deleted')
SUPERSEDED = 'superseded.jsonl'
SUPERSEDED_AS = re.compile(r'\.superseded-\d{8}$')
MAX_FILES = 200          # the agent's choice, question 69
GIT_NAME = '.git'        # a repository's own folder, or a worktree's file naming it: never moved


def plan_or_exit(tag):
    plan = methodlib.saved_plan(tag)
    if not plan:
        raise SystemExit(f'ledger: plan {tag} is not saved in {methodlib.ledger_dir()}: '
                         'run plan.py with --save before running it')
    return plan


def dynarec_of(args):
    """False (off, evidence), True (on, comparison) or None (unknown, comparison)."""
    if args.config:
        text = Path(args.config).read_text(errors='replace')
        match = re.search(r'^\s*cpu_use_dynarec\s*=\s*(\d+)', text, re.M)
        if not match:
            raise SystemExit(f'ledger: {args.config} has no cpu_use_dynarec line')
        return match.group(1) != '0'
    if args.dynarec is not None:
        return args.dynarec != '0'
    value = os.environ.get('RIG_DYNAREC')
    return None if value is None else value != '0'


def record(args):
    plan = plan_or_exit(args.plan)
    runs = {run['id']: run for run in plan['runs']}
    if args.run not in runs:
        raise SystemExit(f'ledger: plan {args.plan} has no run {args.run}')
    run = runs[args.run]
    if run['config']['mode'] != 'base' and not args.build_dir:
        raise SystemExit('ledger: a run with uCDD needs --build-dir, the binaries it ran')
    if args.bench_commit is not None and not COMMIT_HASH.match(args.bench_commit):
        raise SystemExit(f'ledger: --bench-commit {args.bench_commit!r} is not a full commit hash')
    if args.bench_changed is not None and args.bench_commit is None:
        raise SystemExit('ledger: --bench-changed needs --bench-commit, the commit they differ from')
    if args.bench_changed is not None and args.bench_changed < 0:
        raise SystemExit(f'ledger: --bench-changed {args.bench_changed} is not a count of files')
    entry = {
        'time': datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds'),
        'plan': args.plan, 'run': args.run, 'test': run['test'], 'verdict': args.verdict,
        'binaries': methodlib.binaries(args.build_dir) if args.build_dir else {},
        'tools': {name: methodlib.sha256(name) for name in args.tool},
        'outputs': {name: methodlib.sha256(name) for name in args.output},
        'note': args.note, 'spot': os.environ.get('UCDD_SPOT') == '1', 'host': platform.node(),
        'dynarec': dynarec_of(args),
        # the bench's commit (Michael's decision of 6 Nov 2026); null: the runner did not say
        'bench_commit': args.bench_commit,
        'bench_changed': args.bench_changed,         # a count; the runner's log names the files
    }
    if args.build_dir and not entry['binaries']:
        raise SystemExit(f'ledger: no built files in {args.build_dir}')
    methodlib.append(entry)
    print(f'ledger: {args.run} {args.verdict}' + (' (spot check)' if entry['spot'] else '')
          + ('' if methodlib.is_evidence(entry) else
             ' (comparison: the recompiler was on or not recorded; not evidence)'))


def show(args):
    plan = plan_or_exit(args.plan)
    evidence = methodlib.latest(args.plan, evidence_only=True)
    anything = methodlib.latest(args.plan)
    counts = {}
    for run in plan['runs']:
        entry = evidence.get(run['id'])
        other = anything.get(run['id'])
        if entry:
            verdict, when, dyn = entry['verdict'], entry['time'], 'dynarec off'
        elif other:
            verdict, when, dyn = other['verdict'] + '*', other['time'], 'dynarec ON' if other.get('dynarec') else 'dynarec ?'
        else:
            verdict, when, dyn = 'not run', '', ''
        counts[verdict] = counts.get(verdict, 0) + 1
        extra = ''
        # The two listings are separate loads of the file, so identity never matches; a later
        # comparison is one that is itself not evidence (r3.4: the agent found this on A0).
        if entry and other and not methodlib.is_evidence(other):
            extra = f'  (a later comparison: {other["verdict"]}, {other["time"]}, dynarec {"ON" if other.get("dynarec") else "?"})'
        print(f'{run["id"]}  {run["test"]:14} {verdict:9} {when}  {dyn}{extra}')
    print('; '.join(f'{verdict}: {count}' for verdict, count in sorted(counts.items())))
    if any(v.endswith('*') for v in counts):
        print('* comparison only: the recompiler was on or not recorded; not evidence (record with --config)')
    return 0 if counts.get('pass', 0) == len(plan['runs']) else 1


def spot(args):
    plan = plan_or_exit(args.plan)
    newest = methodlib.latest(args.plan)
    passed = [run for run in plan['runs'] if newest.get(run['id'], {}).get('verdict') == 'pass']
    if not passed:
        raise SystemExit(f'ledger: no run of {args.plan} has passed yet')
    for run in random.SystemRandom().sample(passed, min(args.n, len(passed))):
        print(f'{run["id"]}  UCDD_SPOT=1 {run["command"]}')


def audit(args):
    plan_or_exit(args.plan)
    original = methodlib.latest(args.plan, evidence_only=True)
    again = methodlib.latest(args.plan, spot=True, evidence_only=True)
    if not again:
        print(f'ledger: plan {args.plan} has no spot check')
        return 1
    disagree = 0
    for run, entry in sorted(again.items()):
        first = original.get(run, {}).get('verdict', 'not run')
        same = first == entry['verdict']
        disagree += not same
        print(f'{run}  {entry["test"]:14} first {first:8} again {entry["verdict"]:8} '
              + ('agrees' if same else 'DISAGREES: the fix or the instrument (L11)'))
    return 1 if disagree else 0


def tally(plan):
    """A plan's verdicts as show counts them: each run's newest evidence entry, else its newest
    comparison (marked *), else not run. {verdict: runs}."""
    evidence = methodlib.latest(plan['tag'], evidence_only=True)
    anything = methodlib.latest(plan['tag'])
    counts = collections.Counter()
    for run in plan['runs']:
        if run['id'] in evidence:
            counts[evidence[run['id']]['verdict']] += 1
        elif run['id'] in anything:
            counts[anything[run['id']]['verdict'] + '*'] += 1
        else:
            counts['not run'] += 1
    return counts


def refuse(why, command='commit-runs'):
    print(f'ledger: {command} refused: {why}', file=sys.stderr)
    return 1


def runner_script(pid):
    """The file name of the first .py word on a process's command line (Linux's /proc), the
    script a Python runner runs; None when there is none or it cannot be read."""
    try:
        words = Path(f'/proc/{pid}/cmdline').read_bytes().split(b'\0')
    except OSError:
        return None
    scripts = [word.decode('utf-8', 'replace') for word in words if word.endswith(b'.py')]
    return os.path.basename(scripts[0]) if scripts else None


def runner_refusal():
    """Why commit-runs may not run here, or None when a runner invoked it (DECISION_67 (7):
    "`ledger.py commit-runs` refuses to run unless invoked by calbatch (a token calbatch sets),
    so a hand invocation fails"). The token is RUNNER_TOKEN=<runner>:<process id>, set by the
    runner for its own commit-runs call; it is read, not trusted: the process it names must be
    this one's parent and must run that runner's script."""
    token = os.environ.get(RUNNER_TOKEN, '')
    if not token:
        return (f'{RUNNER_TOKEN} is not set: commit-runs runs only from a runner at a plan\'s end '
                f'({", ".join(RUNNERS)}), never by hand ({DECISION_67} (7): "a hand invocation '
                'fails"); nothing committed, the next plan\'s end takes these lines')
    name, _, pid = token.rpartition(':')
    if name not in RUNNERS or not pid.isdigit():
        return (f'{RUNNER_TOKEN}={token!r} is not <runner>:<process id> (the runner one of '
                f'{", ".join(RUNNERS)}); nothing committed')
    if int(pid) != os.getppid():
        return (f'{RUNNER_TOKEN} names process {pid}, but this one was started by process '
                f'{os.getppid()}: a token copied from another process; nothing committed')
    script = runner_script(pid)
    if script != name:
        return (f'{RUNNER_TOKEN} names {name}, but process {pid} runs {script or "no Python script"}, '
                f'not {name}; nothing committed')
    return None


def commit_runs(args):
    """The runs file alone on main at a plan's end (Michael's decision of 6 Nov 2026), and only
    when a runner invoked it (runner_refusal, DECISION_67 (7))."""
    refused = runner_refusal()
    if refused:
        return refuse(refused)
    plan = plan_or_exit(args.plan)
    runs_file = (methodlib.ledger_dir() / 'runs.jsonl').resolve()
    if not runs_file.exists():
        return refuse(f'{runs_file} does not exist: nothing was ever recorded')
    # a caller's git settings never steer the commit (as bench/backup.sh)
    env = {key: value for key, value in os.environ.items()
           if key not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY')}

    def git(*words, binary=False):
        return subprocess.run(['git', *words], cwd=top, env=env, capture_output=True, text=not binary)

    top = runs_file.parent
    found = git('rev-parse', '--show-toplevel')
    if found.returncode:
        return refuse(f'{runs_file.parent} is in no git repository')
    top = Path(found.stdout.strip()).resolve()
    name = runs_file.relative_to(top).as_posix()
    branch = git('symbolic-ref', '-q', '--short', 'HEAD').stdout.strip()
    if branch != BRANCH:
        return refuse(f'{top} is on {branch or "a detached HEAD"}, not {BRANCH}: the runs file is '
                      f'committed on {BRANCH} only')
    staged = git('diff', '--cached', '--no-renames', '--name-only', '-z').stdout
    besides = sorted(path for path in staged.split('\0') if path and path != name)
    if besides:
        return refuse(f'other files are staged in {top} ({", ".join(besides)}); the runs file is '
                      'committed alone: commit or unstage them first (the agent\'s own commit)')
    head = git('rev-parse', '-q', '--verify', 'HEAD^{commit}').stdout.strip()
    tracked = bool(head) and git('cat-file', '-e', f'HEAD:{name}').returncode == 0
    before = git('cat-file', 'blob', f'HEAD:{name}', binary=True).stdout if tracked else b''
    # the base the message names: the runs file's own last commit, by its path, never HEAD (often a
    # later commit of the notes); HEAD beside it, the commit this one goes on
    last = git('log', '-1', '--format=%h', '--', name).stdout.strip() if tracked else ''
    since = (f'its last commit {last or "not read"} (HEAD {head[:7]})' if tracked else
             'it was made (its first commit)')
    text = runs_file.read_bytes()
    if not text.startswith(before):
        return refuse(f'{name} is not its last commit\'s lines with lines added after them: the '
                      'ledger only grows (bench/README.md); nothing committed, say so to Michael')
    if text and not text.endswith(b'\n'):
        return refuse(f'{name} ends inside a line (a record being written?); nothing committed: '
                      'the next plan\'s end takes it')
    added = text[len(before):].decode('utf-8', 'replace').splitlines()
    if not added:
        print(f'ledger: commit-runs: nothing new in {name} since {since}; nothing committed')
        return 0
    by_plan, unread, benches = collections.Counter(), 0, collections.Counter()
    for line in added:
        try:
            entry = json.loads(line)
        except ValueError:
            unread += 1
            continue
        by_plan[entry.get('plan', '?')] += 1
        if entry.get('plan') == plan['tag']:
            commit = entry.get('bench_commit')
            benches[commit[:7] if commit else 'a commit not recorded'] += 1
    counts = tally(plan)
    verdicts = ', '.join(f'{verdict} {count}' for verdict, count in sorted(counts.items()))
    subject = f'Ledger: plan {plan["tag"]}, {args.why}: {len(plan["runs"])} runs, {verdicts}'
    body = [f'The runs file alone, committed by ledger.py commit-runs at the plan\'s end ({DECISION}: '
            'by the tool at each plan\'s end, never by the agent\'s hand, no longer by the backup).',
            f'{len(added)} lines added since {since}: '
            + ', '.join(f'{tag} {count}' for tag, count in sorted(by_plan.items()))
            + (f', {unread} unreadable' if unread else '') + '.']
    if benches:
        body.append(f'Plan {plan["tag"]}\'s added entries were recorded on the bench at '
                    + ', '.join(f'{commit} ({count})' for commit, count in sorted(benches.items())) + '.')
    body.append('The verdicts are each run\'s newest evidence entry (the recompiler off), as '
                '`ledger.py show` counts them; * a comparison only.')
    saved = methodlib.ledger_dir().resolve() / 'plans' / f'{plan["tag"]}.json'
    plan_name = saved.relative_to(top).as_posix() if saved.is_relative_to(top) else None
    if plan_name and git('cat-file', '-e', f'HEAD:{plan_name}').returncode:
        print(f'ledger: commit-runs: note: the plan\'s saved file {plan_name} is not in HEAD; '
              f'`ledger.py commit-plan {plan["tag"]}` commits it (plan.py --save does at the save), '
              f'never a hand git add ({DECISION_67} (7)); not this commit')
    if args.dry_run:
        limit = tomllib.loads((methodlib.PACKAGE / 'bench' / 'bench.toml').read_text())['max_mb']
        # the bench check skips this file by its path and keeps its limit for every other file
        # (DECISION_67 (7): "the bench size check excludes the ledger's runs file by path")
        print(f'ledger: commit-runs --dry-run: {name}, {len(text) / 2 ** 20:.2f} MB (the bench check '
              f'skips this file by its path, its {limit} MB limit kept for every other file); '
              f'would commit on {BRANCH} over {head[:7] or "no commit"}:')
        print('\n'.join(['  ' + subject, ''] + ['  ' + line for line in body]))
        return 0
    if not tracked:
        git('add', '--', name)
    # --only: the commit holds the runs file as it is on the disk and nothing else, whatever is
    # staged by the time git runs; the hook runs on that commit's own index
    done = git('commit', '-q', '--only', '-m', subject, '-m', '\n\n'.join(body), '--', name)
    if done.returncode:
        if not tracked:
            git('rm', '-q', '--cached', '--', name)     # the index as it was found
        hook = (done.stderr or done.stdout).strip()
        return refuse(f'git commit said: {hook or "exit %d" % done.returncode}; nothing committed, '
                      'the next plan\'s end takes these lines')
    print(f'ledger: committed {name} as {git("rev-parse", "--short", "HEAD").stdout.strip()} on '
          f'{BRANCH}: {subject}')
    return 0


def commit_plan(args):
    """A saved plan's file committed alone on main in the repository that holds the ledger, at
    its save by plan.py --save (DECISION_67 (7): "the guard treats a git command that stages,
    restores or checks out a guard-protected path as a write to it", so no hand git add of a
    saved plan). The same steps as commit_runs: commit_runs keeps its own copy, since its
    known-bad plants (tests/test_ledger_commit.py) are written against its lines; the two can
    share one helper at A7's method review."""
    plan = plan_or_exit(args.plan)
    saved = (methodlib.ledger_dir() / 'plans' / f'{plan["tag"]}.json').resolve()
    env = {key: value for key, value in os.environ.items()
           if key not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY')}

    def git(*words, binary=False):
        return subprocess.run(['git', *words], cwd=top, env=env, capture_output=True, text=not binary)

    top = saved.parent
    found = git('rev-parse', '--show-toplevel')
    if found.returncode:
        return refuse(f'{saved.parent} is in no git repository', 'commit-plan')
    top = Path(found.stdout.strip()).resolve()
    name = saved.relative_to(top).as_posix()
    branch = git('symbolic-ref', '-q', '--short', 'HEAD').stdout.strip()
    if branch != BRANCH:
        return refuse(f'{top} is on {branch or "a detached HEAD"}, not {BRANCH}: a saved plan is '
                      f'committed on {BRANCH} only', 'commit-plan')
    # its own names, not commit_runs' (besides, last): test_ledger_commit.py's plants match those
    staged = git('diff', '--cached', '--no-renames', '--name-only', '-z').stdout
    others = sorted(path for path in staged.split('\0') if path and path != name)
    if others:
        return refuse(f'other files are staged in {top} ({", ".join(others)}); the saved plan is '
                      'committed alone: commit or unstage them first, then `ledger.py commit-plan '
                      f'{plan["tag"]}`', 'commit-plan')
    text = saved.read_bytes()
    head = git('rev-parse', '-q', '--verify', 'HEAD^{commit}').stdout.strip()
    if head and git('cat-file', '-e', f'HEAD:{name}').returncode == 0:
        if git('cat-file', 'blob', f'HEAD:{name}', binary=True).stdout != text:
            return refuse(f'{name} differs from its committed copy: a saved plan never changes '
                          '(plan.py writes it once); nothing committed, say so to Michael', 'commit-plan')
        holder = git('log', '-1', '--format=%h', '--', name).stdout.strip()
        print(f'ledger: commit-plan: {name} is committed as it is (in {holder or "HEAD"}); nothing '
              'committed')
        return 0
    tests = sorted({run['test'] for run in plan['runs']})
    subject = f'Plan {plan["tag"]}: {args.why}'
    body = [f'The saved plan alone, committed by ledger.py commit-plan at its save ({DECISION_67} '
            '(7): "the guard treats a git command that stages, restores or checks out a '
            'guard-protected path as a write to it"; plan.py --save commits its own file, so no '
            'ledger path is staged by hand).',
            f'{len(plan["runs"])} runs of {len(tests)} tests'
            + (f': {", ".join(tests)}.' if len(tests) <= 8 else '.')]
    added = git('add', '--', name)
    if added.returncode:
        return refuse(f'git add said: {(added.stderr or added.stdout).strip()}; nothing committed',
                      'commit-plan')
    # --only: the commit holds the plan's file and nothing else; the hook runs on its own index
    done = git('commit', '-q', '--only', '-m', subject, '-m', '\n\n'.join(body), '--', name)
    if done.returncode:
        git('rm', '-q', '--cached', '--', name)          # the index as it was found
        hook = (done.stderr or done.stdout).strip()
        return refuse(f'git commit said: {hook or "exit %d" % done.returncode}; nothing committed: '
                      f'`ledger.py commit-plan {plan["tag"]}` once that is cleared', 'commit-plan')
    print(f'ledger: committed {name} as {git("rev-parse", "--short", "HEAD").stdout.strip()} on '
          f'{BRANCH}: {subject}')
    return 0


def libraries():
    """The game libraries as guard/guard.py's library_paths reads them (UCDD_GAMES, else
    method.toml's [games] paths), resolved. supersede renames with no guard between, so it refuses
    them itself: we never alter game files (Michael, 20 Oct 2026)."""
    given = os.environ.get('UCDD_GAMES')
    paths = given.split(os.pathsep) if given else methodlib.CONFIG.get('games', {}).get('paths', [])
    return [Path(path).expanduser().resolve() for path in paths if path]


def recording_line():
    """'FLAG: its first line' while the PID that line names is alive, else None: the recording flag read
    as the bench's pre-commit reads it (bench/hooks/pre-commit's recording(); Michael, 4 Nov 2026, L6):
    the flag UCDD_RECORDING_FLAG names (the tests), else the bench's runs/recording.flag, found from this
    package's own place (<bench>/runs/src/method) as the hook finds it from its own. A flag whose PID is
    gone is stale and ignored, as runs/quiet.sh reads it for the backups."""
    flag = Path(os.environ.get('UCDD_RECORDING_FLAG') or methodlib.PACKAGE.parents[1] / 'recording.flag')
    try:
        line = flag.read_text().splitlines()[0]
        pid = int(line.split()[0])
    except (OSError, IndexError, ValueError):
        return None
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return None
    except PermissionError:                      # alive, another account's
        pass
    return f'{flag}: {line}'


def files_of(place):
    """(the files PLACE holds, sorted; '') or (None, why): PLACE itself when it is a file, else every
    file under it, read without following a link. Each name under it is looked at as it is found, the
    folders' with the files': refused are a symbolic link, a .git (a repository's own folder, or a
    worktree's file naming one), a name in the NAME.superseded-YYYYMMDD form (set aside already), anything
    that is neither a plain file nor a folder, a folder that cannot be read (its files would be left out
    of the record), no file at all, and more than MAX_FILES (counted as they are found, so a mistaken PATH
    is never read whole: L21)."""
    if place.is_file():
        return [place], ''
    if not place.is_dir():
        return None, 'neither a plain file nor a folder'
    found = []

    def fail(error):
        raise error

    try:
        for folder, folders, names in os.walk(place, onerror=fail):
            for name in sorted(folders) + sorted(names):
                path = Path(folder) / name
                if path.is_symlink():
                    return None, f'{path.relative_to(place)} is a symbolic link'
                if name == GIT_NAME:
                    return None, (f'it holds {path.relative_to(place)}, a repository\'s own (.git): '
                                  'nothing of git\'s is moved')
                if SUPERSEDED_AS.search(name):
                    return None, (f'{path.relative_to(place)} is set aside already (its name ends '
                                  '.superseded-YYYYMMDD): a path is superseded once')
            for name in sorted(names):
                path = Path(folder) / name
                if not path.is_file():
                    return None, f'{path.relative_to(place)} is not a plain file'
                found.append(path)
                if len(found) > MAX_FILES:
                    return None, (f'more than {MAX_FILES} files: a report folder holds a handful; is it '
                                  'the right PATH?')
    except OSError as error:
        return None, f'not readable ({error})'
    if not found:
        return None, 'no file in it'
    return sorted(found), ''


def supersede(args):
    """Each PATH recorded in the ledger's file of its own and renamed beside itself, never deleted
    (DECISION_68: NEVER_DELETED); the file committed alone on main as commit_plan commits a saved
    plan, with its own copy of the steps (commit_plan's docstring: one helper at A7's method
    review). Every refusal comes before anything changes; the renames come before the commit, and a
    refused commit puts each one back with the file's bytes and the index. Every refusal has its
    known-bad plant in tests/test_ledger_supersede.py's docstring; the names here (busy, toplevel, on,
    beside, kept, held, stuck) are its own, not commit_runs' or commit_plan's, so each plant's line is
    unique in this file."""
    command = 'supersede'
    why = ' '.join(args.why.split())
    if not why:
        return refuse('--why is empty: say why these are set aside (it goes on every record); nothing '
                      'changed', command)
    # nothing renamed or staged beside a recording (L6): read before anything changes; the bench's
    # pre-commit refuses the commit as well, behind this
    busy = recording_line()
    if busy:
        return refuse(f'a plan is recording ({busy}): nothing is set aside while it records (L6; the bench '
                      'check would refuse the commit too); nothing changed: run it at a gap', command)
    ledger = methodlib.ledger_dir().resolve()
    if not ledger.is_dir():
        return refuse(f'the ledger folder {ledger} does not exist; nothing changed', command)
    record_file = ledger / SUPERSEDED
    # a caller's git settings never steer the commit (as commit_runs and bench/backup.sh)
    env = {key: value for key, value in os.environ.items()
           if key not in ('GIT_DIR', 'GIT_WORK_TREE', 'GIT_INDEX_FILE', 'GIT_OBJECT_DIRECTORY')}

    def git(*words, binary=False):
        return subprocess.run(['git', *words], cwd=top, env=env, capture_output=True, text=not binary)

    top = ledger
    toplevel = git('rev-parse', '--show-toplevel')
    if toplevel.returncode:
        return refuse(f'{ledger} is in no git repository; nothing changed', command)
    top = Path(toplevel.stdout.strip()).resolve()
    # git's own folders for this repository, whatever their names (its git dir and common dir, as git
    # prints them, resolved against the top): nothing in or around them is moved
    gits = sorted({(top / line.strip()).resolve() for line in
                   git('rev-parse', '--git-dir', '--git-common-dir').stdout.splitlines() if line.strip()})
    name = record_file.relative_to(top).as_posix()
    on = git('symbolic-ref', '-q', '--short', 'HEAD').stdout.strip()
    if on != BRANCH:
        return refuse(f'{top} is on {on or "a detached HEAD"}, not {BRANCH}: the superseded file '
                      f'is committed on {BRANCH} only; nothing changed', command)
    staged = git('diff', '--cached', '--no-renames', '--name-only', '-z').stdout
    beside = sorted(path for path in staged.split('\0') if path and path != name)
    if beside:
        return refuse(f'other files are staged in {top} ({", ".join(beside)}); the superseded file is '
                      'committed alone: commit or unstage them first; nothing changed', command)
    head = git('rev-parse', '-q', '--verify', 'HEAD^{commit}').stdout.strip()
    tracked = bool(head) and git('cat-file', '-e', f'HEAD:{name}').returncode == 0
    kept = git('cat-file', 'blob', f'HEAD:{name}', binary=True).stdout if tracked else b''
    existed = record_file.exists()
    held = record_file.read_bytes() if existed else b''
    if not held.startswith(kept):
        return refuse(f'{name} is not its last commit\'s lines with lines added after them: it only '
                      'grows, as the runs file; nothing changed, say so to Michael', command)
    if held and not held.endswith(b'\n'):
        return refuse(f'{name} ends inside a line; nothing changed, say so to Michael', command)
    try:
        old = [json.loads(line) for line in held.decode('utf-8').splitlines() if line.strip()]
    except ValueError:                           # UnicodeDecodeError is one too
        old = None
    if old is None or not all(isinstance(entry, dict) for entry in old):
        return refuse(f'{name} holds a line that is not a record; nothing changed, say so to Michael',
                      command)
    # a path is superseded once: each record's file where it was, the PATH named and where the file went
    # (every moved_to holds a .superseded-YYYYMMDD part, so the parts check below meets those first)
    recorded = {entry.get(key) for entry in old for key in ('path', 'named', 'moved_to')}
    now = datetime.datetime.now(datetime.timezone.utc)
    stamp = now.strftime('%Y%m%d')               # the UTC date, as every time in the ledger
    libs = libraries()
    moves, entries, seen = [], [], []
    for given in args.paths:
        place = Path(given).expanduser().absolute()       # not resolved yet: a link is seen as one
        if not os.path.lexists(place):
            return refuse(f'{given} does not exist; nothing changed', command)
        if place.is_symlink():
            return refuse(f'{given} is a symbolic link: name what it points to; nothing changed', command)
        real = place.resolve()
        if real == top or not real.is_relative_to(top):
            return refuse(f'{given} is not inside {top}, the repository that holds the ledger (its path '
                          'is recorded relative to it); nothing changed', command)
        parts = real.relative_to(top).parts
        if real.is_relative_to(ledger) or ledger.is_relative_to(real):
            return refuse(f'{given} is in the ledger folder or holds it; nothing changed', command)
        if any(real.is_relative_to(library) or library.is_relative_to(real) for library in libs):
            return refuse(f'{given} is in a game library or holds one: nothing there is moved (we never '
                          'alter game files); nothing changed', command)
        if any(real.is_relative_to(own) or own.is_relative_to(real) for own in gits):
            return refuse(f'{given} is in this repository\'s git folder or holds it '
                          f'({", ".join(str(own) for own in gits)}): nothing of git\'s is moved; nothing '
                          'changed', command)
        if GIT_NAME in parts:
            return refuse(f'{given} lies in a .git folder (a repository\'s own, or a worktree\'s file): '
                          'nothing of git\'s is moved; nothing changed', command)
        if any(SUPERSEDED_AS.search(part) for part in parts):
            return refuse(f'{given} is set aside already (it, or a folder above it, ends '
                          '.superseded-YYYYMMDD): a path is superseded once; nothing changed', command)
        if any(real.is_relative_to(other) or other.is_relative_to(real) for other in seen):
            return refuse(f'{given} is named twice, or lies inside another PATH given or holds one; '
                          'nothing changed', command)
        seen.append(real)
        named = real.relative_to(top).as_posix()
        files, why_not = files_of(real)
        if files is None:
            return refuse(f'{given}: {why_not}; nothing changed', command)
        again = [path for path in [named] + [file.relative_to(top).as_posix() for file in files]
                 if path in recorded]
        if again:
            return refuse(f'{again[0]} is recorded in {name} already: a path is superseded once; nothing '
                          'changed', command)
        target = real.with_name(f'{real.name}.superseded-{stamp}')
        moved = target.relative_to(top).as_posix()
        if os.path.lexists(target):
            return refuse(f'{moved} exists already: nothing is overwritten; nothing changed', command)
        size = 0
        for file in files:
            bytes_ = file.stat().st_size
            size += bytes_
            # where the file will be: the PATH's new name, or its place inside the renamed folder
            lands = target if file == real else target / file.relative_to(real)
            entries.append({
                'time': now.isoformat(timespec='seconds'), 'date': now.date().isoformat(),
                'path': file.relative_to(top).as_posix(), 'moved_to': lands.relative_to(top).as_posix(),
                'named': named, 'sha256': methodlib.sha256(file), 'size': bytes_, 'why': why,
                'host': platform.node()})
        moves.append((real, target, named, moved, len(files), size))
    done = []

    def put_back():
        """Each PATH renamed so far back under its own name, the last first; what could not be (its
        own name taken again in between: never renamed over, since a rename over an empty folder
        succeeds and would hide it)."""
        stuck = []
        for real, target, named, moved, _, _ in reversed(done):
            try:
                if os.path.lexists(real):
                    raise OSError(f'{named} exists again')
                os.rename(target, real)
            except OSError as error:
                stuck.append(f'{moved} ({error})')
        return stuck

    def undo(reason):
        """The way back once every PATH is renamed (a record that cannot be written, a refused git add
        or commit): the index, the file's bytes, then each PATH."""
        if not tracked:
            git('rm', '-q', '--cached', '--ignore-unmatch', '--', name)
        try:
            if existed:
                with open(record_file, 'r+b') as file:
                    file.truncate(len(held))
            else:
                record_file.unlink(missing_ok=True)
        except OSError as error:
            reason += f'; {name} NOT restored ({error}): say so to Michael'
        left = put_back()
        return refuse(f'{reason}; nothing recorded, ' + (
            f'but NOT put back: {", ".join(left)} (rename each back by hand)' if left
            else 'every PATH back under its own name'), command)

    for move in moves:
        real, target, named, moved = move[:4]
        try:
            if os.path.lexists(target):          # made since it was checked: never overwritten
                raise OSError(f'{moved} exists now')
            os.rename(real, target)
        except OSError as error:
            had = len(done)
            left = put_back()
            return refuse(f'could not rename {named} to {moved} ({error}); nothing recorded, '
                          + (f'NOT put back: {", ".join(left)} (rename each back by hand)' if left
                             else f'the {had} renamed before it put back' if had else 'nothing moved'),
                          command)
        done.append(move)
    try:
        with open(record_file, 'ab') as file:
            file.write(''.join(json.dumps(entry, sort_keys=True) + '\n' for entry in entries).encode())
    except OSError as error:
        return undo(f'could not write {name} ({error})')
    if not tracked:
        added = git('add', '--', name)
        if added.returncode:
            return undo(f'git add said: {(added.stderr or added.stdout).strip()}')
    plural = lambda count, word: f'{count} {word}' + ('' if count == 1 else 's')
    subject = (f'Ledger: superseded {plural(len(moves), "path")}, {plural(len(entries), "file")} '
               '(ledger.py supersede)')
    body = [f'The superseded file alone, by ledger.py supersede ({DECISION_68}: "{NEVER_DELETED}"): '
            'each file\'s path, sha256 and size, why and the date; nothing deleted, each PATH renamed '
            f'beside itself to NAME.superseded-{stamp}.',
            f'Why: {why}',
            '\n'.join(f'{named} -> {moved}: {plural(count, "file")}, {size} bytes'
                      for _, _, named, moved, count, size in moves)]
    # --only: the commit holds the superseded file and nothing else; the hook runs on its own index
    committed = git('commit', '-q', '--only', '-m', subject, '-m', '\n\n'.join(body), '--', name)
    if committed.returncode:
        hook = (committed.stderr or committed.stdout).strip()
        return undo(f'git commit said: {hook or "exit %d" % committed.returncode}')
    print(f'ledger: committed {name} as {git("rev-parse", "--short", "HEAD").stdout.strip()} on '
          f'{BRANCH}: {subject}')
    for _, _, named, moved, count, size in moves:
        print(f'  {named} -> {moved} ({plural(count, "file")}, {size} bytes; never deleted)')
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    commands = parser.add_subparsers(dest='command', required=True)
    one = commands.add_parser('record')
    one.add_argument('plan')
    one.add_argument('run')
    one.add_argument('verdict', choices=('pass', 'fail'))
    one.add_argument('--build-dir')
    one.add_argument('--tool', action='append', default=[])
    one.add_argument('--output', action='append', default=[])
    one.add_argument('--note', default='')
    one.add_argument('--config', help="the run's 86box.cfg: cpu_use_dynarec decides evidence or comparison")
    one.add_argument('--dynarec', choices=('0', '1'), help='when no 86box.cfg is at hand')
    one.add_argument('--bench-commit', help="the bench repository's commit the plan started from")
    one.add_argument('--bench-changed', type=int, metavar='N',
                     help='how many tracked bench files differed from that commit at the start '
                          "(the runner's log names them)")
    for name in ('show', 'spot', 'audit'):
        command = commands.add_parser(name)
        command.add_argument('plan')
        if name == 'spot':
            command.add_argument('-n', type=int, default=2)
    end = commands.add_parser('commit-runs')
    end.add_argument('plan')
    end.add_argument('--why', default='its end', help='why the plan ended, for the message')
    end.add_argument('--dry-run', action='store_true', help='say what would be committed; commit nothing')
    saved = commands.add_parser('commit-plan')
    saved.add_argument('plan')
    saved.add_argument('--why', default='saved by plan.py --save',
                       help="what the plan is for: its commit's subject after \"Plan <tag>: \"")
    aside = commands.add_parser('supersede', help='record files set aside and rename them beside, '
                                                  'never deleted (question 68)')
    aside.add_argument('paths', nargs='+', metavar='PATH', help='a file, or a report folder and all in it')
    aside.add_argument('--why', required=True, help='why they are set aside: on every record and in the commit')
    args = parser.parse_args()
    return {'record': record, 'show': show, 'spot': spot, 'audit': audit,
            'commit-runs': commit_runs, 'commit-plan': commit_plan,
            'supersede': supersede}[args.command](args) or 0


if __name__ == '__main__':
    sys.exit(main())
