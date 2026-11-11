#!/usr/bin/env python3
"""test_doccheck.py: the pages' checks (lib/docs.py, tools/doccheck.py; tightening r3.11, gate T13).

A small repository is made with a front page, an index, four pages and a register on a branch of
its own. The known-good tree passes every check. Then each fault is planted alone and its own
check, and no other, must refuse it: a check is trusted only once it has failed on a known-bad
(L4). The identity rule of lib/privacy.py is tested the same way.

Prints ok or BAD per case; exits 1 on a BAD.
"""

from datetime import datetime, timezone
from pathlib import Path
import os
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / 'lib'))
os.environ.setdefault('TZ', 'UTC')
import docs  # noqa: E402
import privacy  # noqa: E402

SETTINGS = {
    'branches': ['pages'], 'repo': 'Owner/Repo', 'owners': ['upstream'],
    'front': 'README.md', 'index': 'docs/README.md',
    'pages': ['README.md', 'docs/*.md'], 'foreign': ['BUILDING.md'], 'unstamped': ['docs/README.md'],
    'register': 'notes:ISSUES.md', 'register_page': 'docs/KNOWN-ISSUES.md', 'register_prefix': 'CAND-',
    'fluff': [r'(?i)\bseamless(ly)?\b'], 'markers': [r'\[agent:[^\]]*\]'], 'todo': r'\[TODO:[^\]]*\]',
    'conduct': [r'(?i)\bnothing\s+from\s+this\s+fork\s+has\s+been\s+sent\b'],
}
# The owner's decision of 11 Nov 2026 on the 07:00Z report, item 2: each sentence removed from the pages, as it stood,
# must be refused by method.toml's [docs] conduct; the credit line, "the author has since fixed" and METHOD.md's
# sentence on a row must pass.
CONDUCT_BAD = [
    'Nothing from this fork\nhas been sent to him.',
    '- **Decision.** No issue, pull request, comment or mention goes to the\n  upstream author.',
    '- **Enforced by.** A commit check that refuses a mention or a link to an\n  upstream issue.',
    '- **Nothing from this fork has been sent upstream**',
    'Nothing from this fork has been sent to the upstream author. Whether any\nof it is offered to him, and in what form, '
    'is for the person who runs the\nproject to decide once the findings have been confirmed on real hardware.',
    'Everything in the register was measured in an emulator unless its row\nsays otherwise, and nothing in it has been '
    'sent to the upstream author.',
    "  lives on the fork's public notes branch. Nothing is sent to the author.",
    '   against; the owner decides on them.',
    'A\ncommit that cites a run as evidence is refused by the commit hook if the\nledger does not hold it as a pass.',
    'It does not send anything to the upstream author: every finding\nstays in this repository.',
    'The commit checks refuse the rest at\nthe commit and again at the push',
    'firmware or recordings are in this repository, and the commit checks refuse\nthem.',
    'every "As of" line, every candidate row present in the table. It runs at\neach commit and on GitHub',
    '| The ledger, the decisions, the lessons | The bench machine | No. Never pushed anywhere. |',
]
CONDUCT_GOOD = [
    "All credit for the driver is the upstream author's.",
    'ten are in the fork and in the author\'s release alike, nine the author has since fixed',
    'A fault it finds is a row with evidence and a\nhypothesis in a field of its own, never a patch;',
]
TODAY = datetime(2026, 11, 10, tzinfo=timezone.utc)

GOOD = {
    'README.md': '# Front\n\nAs of 10 November 2026.\n\nRead [the index](docs/README.md) and '
                 '[status](docs/STATUS.md#in-hand).\n\n```\n[a link in code](nowhere.md)\n```\n',
    'docs/README.md': '# Index\n\n- [Status](STATUS.md)\n- [Known issues](KNOWN-ISSUES.md)\n'
                      '- [Method](METHOD.md)\n- [Build](../BUILDING.md)\n',
    'docs/STATUS.md': '# Status\n\nAs of 10 November 2026.\n\n## In hand\n\nSee [the method](METHOD.md#how-a-row-is-read) '
                      'and [the register](https://github.com/Owner/Repo/blob/notes/ISSUES.md).\n\n'
                      '<a id="pinned"></a>\nThe pin. [TODO: Insert the date]\n',
    'docs/KNOWN-ISSUES.md': '# Known issues\n\nAs of 10 November 2026.\n\nCAND-1, CAND-2 and CAND-10 (split). '
                            'CAND-33 to CAND-40 are single games. CAND-50A and CAND-50B are one row split.\n',
    'docs/METHOD.md': '# Method\n\nWritten on the bench. As of 9 November\n2026.\n\n## How a row is read\n\n'
                      'Text, with `[agent: x]` and `[TODO: an example]` in code.\n',
    'BUILDING.md': '# Build\n\nSee [the front page](README.md). Robust and seamless, in another author\'s words.\n',
}
REGISTER = '# Rows\n\n### CAND-1 one\n\n### CAND-2 two\n\n### CAND-10A a\n\n### CAND-10B b\n\n### CAND-50 split\n\n' + \
           ''.join(f'### CAND-{n} x\n\n' for n in range(33, 41))


def run(*args, cwd):
    return subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=True).stdout


def repository(files, register=REGISTER):
    root = Path(tempfile.mkdtemp(prefix='doccheck-'))
    env = dict(os.environ, GIT_AUTHOR_NAME='T', GIT_AUTHOR_EMAIL='t@example.invalid',
               GIT_COMMITTER_NAME='T', GIT_COMMITTER_EMAIL='t@example.invalid')

    def git(*args):
        return subprocess.run(['git', *args], cwd=root, env=env, capture_output=True, text=True, check=True).stdout

    git('init', '-q', '-b', 'notes')
    (root / 'ISSUES.md').write_text(register)
    git('add', '-A')
    git('commit', '-q', '-m', 'rows')
    git('checkout', '-q', '--orphan', 'pages')
    git('rm', '-q', '-rf', '.')
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
    git('add', '-A')
    git('commit', '-q', '-m', 'pages')
    return root, git


BAD = 0


def case(name, good):
    global BAD
    print(('ok  ' if good else 'BAD ') + name)
    BAD += 0 if good else 1


def problems_of(files, only=None, register=REGISTER, old_ids=None, staged=False):
    root, _ = repository(files, register)
    tree = docs.Tree(staged=True, cwd=root) if staged else docs.Tree(ref='pages', cwd=root)
    found, notes, counts = docs.check(tree, only=only, settings=SETTINGS, cwd=root, old_ids=old_ids, today=TODAY)
    return found, notes, counts


def planted(name, change, check, phrase):
    """CHANGE alone must make CHECK refuse with PHRASE, and every other check stay silent."""
    files = dict(GOOD)
    register = REGISTER
    extra = change(files)
    if isinstance(extra, str):
        register = extra
    found, _, _ = problems_of(files, register=register)
    mine, _, _ = problems_of(files, only=[check], register=register)
    others = [p for p in found if p not in mine]
    case(f'{name}: {check} refuses it', any(phrase in p for p in mine))
    case(f'{name}: no other check speaks', not others)


def main():
    found, notes, counts = problems_of(GOOD)
    case('the known-good tree passes every check', not found)
    case('its counts: 5 pages, 1 other file, links read', counts['pages'] == 5 and counts['foreign'] == 1 and counts['links'] >= 9)
    case('the TODO marker is counted, not refused', len(notes) == 1 and 'docs/STATUS.md' in notes[0])
    case('a link inside a code block is not read', not any('nowhere.md' in p for p in found))
    found, _, _ = problems_of(GOOD, staged=True)
    case('the index reads as the commit does', not found)

    def broken(files):
        files['docs/STATUS.md'] = files['docs/STATUS.md'].replace('(METHOD.md#how', '(METHODS.md#how')
    planted('a link to a page that is not there', broken, 'links', 'no such file')

    def anchor(files):
        files['README.md'] = files['README.md'].replace('#in-hand', '#in-hands')
    planted('a link to a heading that is not there', anchor, 'links', 'no heading or anchor')

    def branch(files):
        files['docs/STATUS.md'] = files['docs/STATUS.md'].replace('blob/notes/ISSUES.md', 'blob/notes/ROWS.md')
    planted('a link to a file another branch does not hold', branch, 'links', 'no such file on that branch')

    def gone(files):
        files['docs/STATUS.md'] = files['docs/STATUS.md'].replace('blob/notes/', 'blob/nowhere/')
    planted('a link to a branch the clone does not hold', gone, 'links', 'does not hold')

    def renamed(files):
        files['docs/STATUS.md'] = files['docs/STATUS.md'].replace('github.com/Owner/Repo/blob/notes/ISSUES.md',
                                                                'github.com/OldName/Repo')
    planted('a link under a name the repository no longer has', renamed, 'names', 'a name it does not')

    def orphan(files):
        files['docs/LOST.md'] = '# Lost\n\nAs of 10 November 2026.\n'
    planted('a page nothing links to', orphan, 'orphans', 'docs/LOST.md')

    def unlisted(files):
        files['docs/EXTRA.md'] = '# Extra\n\nAs of 10 November 2026.\n'
        files['docs/STATUS.md'] += '\n[extra](EXTRA.md)\n'
    planted('a page linked but not in the index', unlisted, 'orphans', 'not listed in the index')

    def unstamped(files):
        files['docs/METHOD.md'] = files['docs/METHOD.md'].replace('As of 9 November\n2026.', 'Undated.')
    planted('a page with no "As of" line', unstamped, 'stamp', 'no "As of')

    def future(files):
        files['docs/METHOD.md'] = files['docs/METHOD.md'].replace('9 November\n2026', '30 November\n2026')
    planted('an "As of" day in the future', future, 'stamp', 'in the future')

    def fluff(files):
        files['docs/METHOD.md'] += '\nIt is seamless.\n'
    planted('a word that claims without showing', fluff, 'words', 'seamless')

    def conduct(files):
        files['docs/METHOD.md'] += '\nNothing from this fork has been sent to him.\n'
    planted('a working rule stated on a page', conduct, 'conduct', 'working rule')

    import re
    pats = docs.SETTINGS.get('conduct', [])
    missed = [x for x in CONDUCT_BAD if not any(re.search(p, docs.prose(x)) for p in pats)]
    case('conduct: the %d sentences removed on 11 Nov are each refused by method.toml\'s patterns%s' % (
        len(CONDUCT_BAD), (': missed ' + ' | '.join(m[:40] for m in missed)) if missed else ''), bool(pats) and not missed)
    hit = [x for x in CONDUCT_GOOD if any(re.search(p, docs.prose(x)) for p in pats)]
    case('conduct: the credit line, "the author has since fixed" and the row sentence pass%s' % (
        (': refused ' + ' | '.join(h[:40] for h in hit)) if hit else ''), not hit)

    def marker(files):
        files['docs/METHOD.md'] += '\nClosed [agent: date].\n'
    planted('a marker left for another hand', marker, 'markers', 'another hand')

    def unlisted_row(files):
        return REGISTER + '### CAND-41 new\n\n'
    planted('a candidate row the page does not table', unlisted_row, 'register', 'CAND-41')

    def stranger(files):
        files['docs/STATUS.md'] += '\nSee CAND-99.\n'
    planted('a candidate id the register does not hold', stranger, 'register', 'CAND-99')

    root, git = repository(GOOD)
    tree = docs.Tree(ref='pages', cwd=root)
    settings = dict(SETTINGS, register='rows:ISSUES.md')
    found, _, _ = docs.check(tree, only=['register'], settings=settings, cwd=root, today=TODAY)
    case('a register that cannot be read is a problem, never a pass', any('did not read' in p for p in found))

    old = Path(tempfile.mkdtemp(prefix='doccheck-ids-')) / 'old-ids.txt'
    old.write_text('0123456789abcdef0123456789abcdef01234567 refs/heads/x\n')
    files = dict(GOOD)
    files['docs/METHOD.md'] += '\nBuilt at 0123456789ab, and 8f91e1a is an address.\n'
    found, _, _ = problems_of(files, only=['oldids'], old_ids=str(old))
    case('a commit id from before the rewrite is refused', len(found) == 1 and 'before the rewrite' in found[0])
    found, _, _ = problems_of(GOOD, only=['oldids'], old_ids=str(old))
    case('the known-good tree cites none', not found)
    found, _, _ = problems_of(GOOD, only=['oldids'], old_ids=str(old) + '.missing')
    case('a file of ids that cannot be read is a problem', any('did not read' in p for p in found))
    shortfile = old.with_name('old-short.txt')                  # the file may hold the short form (INSTALL.md 3)
    shortfile.write_text('0123456\n')
    files = dict(GOOD)
    files['docs/METHOD.md'] += '\nBuilt at 0123456789abcdef.\n'
    found, _, _ = problems_of(files, only=['oldids'], old_ids=str(shortfile))
    case('an old id held short is refused when a page cites it longer', len(found) == 1)

    # the commit hook's entry: only on the pages' branch, only when a page is staged
    root, git = repository(GOOD)
    case('the hook: nothing staged, nothing read', docs.staged_problems(cwd=root, settings=SETTINGS) == [])
    (root / 'docs' / 'STATUS.md').write_text(GOOD['docs/STATUS.md'].replace('(METHOD.md#how', '(METHODS.md#how'))
    git('add', '-A')
    found = docs.staged_problems(cwd=root, settings=SETTINGS)
    case('the hook: a staged page with a dead link is refused', any('no such file' in p for p in found))
    git('checkout', '-q', '-b', 'elsewhere')
    case('the hook: another branch is not read', docs.staged_problems(cwd=root, settings=SETTINGS) == [])

    # the hooks themselves, with the package's own [docs] (the pages' branch is its first entry)
    branch = [name for name in docs.SETTINGS.get('branches', []) if '*' not in name][0]
    for hooks in ('hooks', 'hooks/shared'):
        root, git = repository(GOOD)
        git('branch', '-m', branch)
        env = dict(os.environ, TZ='UTC', UCDD_METHOD_LOCAL=str(root / 'none.toml'),
                   GIT_AUTHOR_NAME='T', GIT_AUTHOR_EMAIL='t@example.invalid',
                   GIT_COMMITTER_NAME='T', GIT_COMMITTER_EMAIL='t@example.invalid')

        def commit(message):
            return subprocess.run(['git', '-c', f'core.hooksPath={HERE.parent / hooks}', 'commit', '-q', '-m', message],
                                  cwd=root, env=env, capture_output=True, text=True)

        (root / 'docs' / 'METHOD.md').write_text(GOOD['docs/METHOD.md'] + '\nA line more.\n')
        git('add', '-A')
        done = commit('Docs: a line more\n\nEvidence: none: a page')
        case(f'{hooks}/commit-msg: a good page is committed', done.returncode == 0)
        (root / 'docs' / 'STATUS.md').write_text(GOOD['docs/STATUS.md'].replace('(METHOD.md#how', '(METHODS.md#how'))
        git('add', '-A')
        done = commit('Docs: a dead link\n\nEvidence: none: a page')
        case(f'{hooks}/commit-msg: a page with a dead link is refused',
             done.returncode != 0 and 'no such file' in done.stderr)

    # tools/privscan.py: an own commit by an identity the method does not name is counted
    sys.path.insert(0, str(HERE.parent / 'tools'))
    import privscan
    root, git = repository(GOOD)
    saved = dict(privacy.SETTINGS)
    try:
        privacy.SETTINGS['identities'] = ['Claude <noreply@anthropic.com>']
        privacy.SETTINGS.pop('identities_also', None)
        count, distinct, commits = privscan.unnamed(str(root), ['--all'])
        case('the identity rule: commits by an identity the method does not name are counted',
             count == 2 and distinct == 1 and len(commits) == 2)
        privacy.SETTINGS['identities_also'] = ['T <t@example.invalid>']
        case('the identity rule: one the owner accepts in the local file passes',
             privscan.unnamed(str(root), ['--all'])[0] == 0)
        privacy.SETTINGS['identities'] = []
        privacy.SETTINGS['identities_also'] = []
        case('the identity rule: no list, no reading', privscan.unnamed(str(root), ['--all']) is None)
    finally:
        privacy.SETTINGS.clear()
        privacy.SETTINGS.update(saved)

    return 1 if BAD else 0


if __name__ == '__main__':
    sys.exit(main())
