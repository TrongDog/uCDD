"""The pages keep up with the work (tightening r3.11, gate T13; the owner, 10 Nov 2026).

The fork's public pages (the front page and docs/) are a view of the rows. A view drifts: a link
breaks when a page moves, a page is written and never linked, a count is copied to three pages
and corrected on one, a candidate row is filed and the table of candidates never hears of it.
These are the checks that can be made by a program. What a program cannot check (whether a
sentence is true) stays with the second review; README.md, "The pages", has those rules.

Checks, each by a rule and none by a list of pages:

  links     every relative link and image in a page resolves to a file of the same tree, and its
            #anchor to a heading or an <a id> of that file; a link into this repository on GitHub
            (blob or tree, any branch) resolves in that branch as this clone holds it
  names     a link into this repository names it as it is named now ([docs] repo, with the
            upstream's): a link under any other owner is a name the repository no longer has
  orphans   every page is reached from the front page by links, and is listed in the index
  stamp     every page says the day its facts were read ("As of 10 November 2026"), and the day is
            not in the future
  words     no word of [docs] fluff: a claim is a number, a constraint or a link, not an adjective
  conduct   no sentence of [docs] conduct: a page says what the thing is, what it does and what was measured,
            not what the project has not done toward anyone, what it will or will not send to anyone, who decides
            what, or how its rules are enforced (the owner, 11 Nov 2026); the patterns find only what was listed
  markers   no marker left for another hand ([docs] markers); [TODO: ...] markers are counted and
            listed, never refused: a gap that is named is not drift
  register  every candidate id of the register ([docs] register, a file on another branch) is on
            the page that tables them ([docs] register_page), by name or inside a stated range
            ("CAND-33 to CAND-169"); and no page names an id the register does not hold
  oldids    with a file of commit ids given (--old-ids), no page cites one of them

What is read: the pages ([docs] pages, shell globs) for every check; the files of [docs] foreign
(another author's text, or a page kept as it was on a stated day) for links and names only.

A tree is a commit (--ref), the index (--staged) or a directory (--dir). The register is read
from git. A check that cannot read what it needs says so as a problem: it never passes unread.
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
import fnmatch
import os
import posixpath
import re
import subprocess

import methodlib

SETTINGS = methodlib.CONFIG.get('docs', {})
CHECKS = ('links', 'names', 'orphans', 'stamp', 'words', 'conduct', 'markers', 'register', 'oldids')
SHOWN = 12

FENCE = re.compile(r'(?ms)^(```|~~~).*?^\1[^\n]*$')
INLINE = re.compile(r'`[^`\n]*`')
LINK = re.compile(r'!?\[(?:[^\]\[]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+"[^"]*")?\s*\)')
HTML = re.compile(r'(?i)\b(?:href|src)\s*=\s*"([^"]+)"')
HEADING = re.compile(r'(?m)^#{1,6}[ \t]+(.+?)[ \t]*#*[ \t]*$')
ANCHOR = re.compile(r'(?i)<a\s+(?:id|name)\s*=\s*"([^"]+)"')
MONTHS = ('january february march april may june july august september october november '
          'december').split()


def git(*args, cwd=None):
    return subprocess.run(['git', *args], cwd=cwd, capture_output=True, text=True, errors='replace')


class Tree:
    """The files a check reads: a commit, the index or a plain directory."""

    def __init__(self, ref=None, staged=False, directory=None, cwd=None):
        self.ref, self.staged, self.directory, self.cwd = ref, staged, directory, cwd
        self._names = None
        self._text = {}

    def label(self):
        return self.directory or ('the index' if self.staged else self.ref)

    def names(self):
        if self._names is None:
            if self.directory:
                root = Path(self.directory)
                found = [str(p.relative_to(root)).replace(os.sep, '/')
                         for p in root.rglob('*') if p.is_file() and '.git' not in p.parts]
            elif self.staged:
                found = git('ls-files', '-z', cwd=self.cwd).stdout.split('\0')
            else:
                found = git('ls-tree', '-r', '-z', '--name-only', self.ref, cwd=self.cwd).stdout.split('\0')
            self._names = {name for name in found if name}
        return self._names

    def exists(self, name):
        name = name.rstrip('/')
        return name in ('', '.') or name in self.names() or any(n.startswith(name + '/') for n in self.names())

    def text(self, name):
        if name not in self._text:
            if self.directory:
                self._text[name] = (Path(self.directory) / name).read_text(errors='replace')
            else:
                spec = f':{name}' if self.staged else f'{self.ref}:{name}'
                self._text[name] = git('show', spec, cwd=self.cwd).stdout
        return self._text[name]


def matching(names, globs):
    return sorted(name for name in names if any(fnmatch.fnmatchcase(name, glob) for glob in globs))


def pages(tree, settings=None):
    settings = SETTINGS if settings is None else settings
    foreign = set(matching(tree.names(), settings.get('foreign', [])))
    return [name for name in matching(tree.names(), settings.get('pages', [])) if name not in foreign]


def foreign(tree, settings=None):
    settings = SETTINGS if settings is None else settings
    return matching(tree.names(), settings.get('foreign', []))


def prose(text):
    """The text with code taken out: a link inside a code block is an example, not a link."""
    text = FENCE.sub(lambda found: '\n' * found.group(0).count('\n'), text)
    return INLINE.sub(lambda found: ' ' * len(found.group(0)), text)


def slug(heading):
    heading = re.sub(r'!?\[([^\]]*)\]\([^)]*\)', r'\1', heading)        # a link in a heading: its text
    heading = re.sub(r'<[^>]+>', '', heading)
    return re.sub(r'[^\w\- ]', '', heading.strip().lower()).replace(' ', '-')


def anchors(text):
    found, seen = set(ANCHOR.findall(text)), {}
    for heading in HEADING.findall(FENCE.sub('', text)):
        name = slug(heading)
        count = seen.get(name, 0)
        seen[name] = count + 1
        found.add(name if not count else f'{name}-{count}')
    return found


def line_of(text, position):
    return text.count('\n', 0, position) + 1


def targets(text):
    body = prose(text)
    for pattern in (LINK, HTML):
        for found in pattern.finditer(body):
            yield found.group(1), line_of(body, found.start())


def repo_link(target, settings):
    """('owner', 'repo', 'blob|tree'|None, 'rest') for a link to a GitHub repository, else None."""
    found = re.match(r'https?://github\.com/([^/\s#?]+)/([^/\s#?]+)(?:/(blob|tree)/([^#?\s]+))?', target)
    return found.groups() if found else None


def branch_split(rest, cwd):
    """'claude/x-1/tools/ci.py' -> ('origin/claude/x-1', 'tools/ci.py'): the longest ref this clone
    holds that the path starts with, as a remote branch, a local branch or a tag."""
    parts = rest.split('/')
    for cut in range(len(parts), 0, -1):
        name = '/'.join(parts[:cut])
        for ref in (f'refs/remotes/origin/{name}', f'refs/heads/{name}', f'refs/tags/{name}'):
            if git('rev-parse', '-q', '--verify', f'{ref}^{{commit}}', cwd=cwd).returncode == 0:
                return ref, '/'.join(parts[cut:])
    if re.fullmatch(r'[0-9a-f]{7,40}', parts[0]) and \
            git('rev-parse', '-q', '--verify', f'{parts[0]}^{{commit}}', cwd=cwd).returncode == 0:
        return parts[0], '/'.join(parts[1:])
    return None, rest


def link_problems(tree, names, settings=None, cwd=None):
    settings = SETTINGS if settings is None else settings
    repo = settings.get('repo', '')
    problems, count = [], 0
    for name in names:
        text = tree.text(name)
        own = None
        for target, line in targets(text):
            count += 1
            where = f'{name}:{line}'
            if target.startswith(('mailto:', 'tel:')):
                continue
            if target.startswith('#'):
                own = anchors(text) if own is None else own
                if target[1:] and target[1:] not in own:
                    problems.append(f'{where}: no heading or anchor "{target}" on this page')
                continue
            if re.match(r'[a-z][a-z0-9+.-]*:', target, re.I):
                found = repo_link(target, settings)
                if not found or f'{found[0]}/{found[1]}'.lower() != repo.lower() or not found[2]:
                    continue                                    # another site, or the repository's root
                if tree.directory and not cwd:
                    continue
                ref, path = branch_split(found[3], cwd)
                path, _, anchor = path.partition('#')
                anchor = anchor or target.partition('#')[2]
                if ref is None:
                    problems.append(f'{where}: "{target}" names a branch this clone does not hold: '
                                    'fetch it, or the link is dead')
                    continue
                kind = git('cat-file', '-t', f'{ref}:{path}' if path else ref, cwd=cwd).stdout.strip()
                if not kind:
                    problems.append(f'{where}: "{target}": no such file on that branch')
                elif anchor and kind == 'blob' and path.endswith('.md'):
                    if anchor not in anchors(git('show', f'{ref}:{path}', cwd=cwd).stdout):
                        problems.append(f'{where}: "{target}": no heading or anchor "#{anchor}" there')
                continue
            path, _, anchor = target.partition('#')
            path = path.partition('?')[0]
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), path))
            if resolved.startswith('..'):
                problems.append(f'{where}: "{target}" leaves the repository')
            elif not tree.exists(resolved):
                problems.append(f'{where}: "{target}": no such file ({resolved})')
            elif anchor and resolved.endswith('.md') and resolved in tree.names():
                if anchor not in anchors(tree.text(resolved)):
                    problems.append(f'{where}: "{target}": no heading or anchor "#{anchor}" in {resolved}')
    return problems, count


def name_problems(tree, names, settings=None):
    """A link into this repository under an owner it does not have: a name it no longer has."""
    settings = SETTINGS if settings is None else settings
    repo = settings.get('repo', '')
    if '/' not in repo:
        return ['[docs] repo is not set: the names check cannot read']
    owner, short = repo.split('/', 1)
    owners = {owner.lower(), *(name.lower() for name in settings.get('owners', []))}
    problems = []
    for name in names:
        for target, line in targets(tree.text(name)):
            found = repo_link(target, settings)
            if found and found[1].lower() == short.lower() and found[0].lower() not in owners:
                problems.append(f'{name}:{line}: a link to this repository under a name it does not '
                                f'have now ([docs] repo is {repo})')
    return problems


def local_links(tree, name):
    out = set()
    for target, _ in targets(tree.text(name)):
        if re.match(r'[a-z][a-z0-9+.-]*:', target, re.I) or target.startswith('#'):
            continue
        path = target.partition('#')[0].partition('?')[0]
        out.add(posixpath.normpath(posixpath.join(posixpath.dirname(name), path)))
    return out


def orphan_problems(tree, names, settings=None):
    settings = SETTINGS if settings is None else settings
    front, index = settings.get('front', 'README.md'), settings.get('index', '')
    if front not in tree.names():
        return [f'the front page {front} is not in {tree.label()}']
    reached, queue = {front}, [front]
    while queue:
        for target in local_links(tree, queue.pop()):
            if target in names and target not in reached:
                reached.add(target)
                queue.append(target)
    problems = [f'{name}: no chain of links leads here from {front}' for name in names if name not in reached]
    if index:
        if index not in tree.names():
            problems.append(f'the index {index} is not in {tree.label()}')
        else:
            listed = local_links(tree, index) | {index, front}
            problems += [f'{name}: not listed in the index {index}' for name in names if name not in listed]
    return problems


def stamp_day(text, settings=None):
    settings = SETTINGS if settings is None else settings
    found = re.search(settings.get('stamp', r'(?i:\bas\s+of)\s+(\d{1,2})\s+([A-Z][a-z]+)\s+(\d{4})\b'), text)
    if not found:
        return None
    try:
        return datetime(int(found.group(3)), MONTHS.index(found.group(2).lower()) + 1, int(found.group(1)),
                        tzinfo=timezone.utc)
    except ValueError:
        return False


def stamp_problems(tree, names, settings=None, today=None):
    settings = SETTINGS if settings is None else settings
    today = today or datetime.now(timezone.utc)
    spared = set(matching(names, settings.get('unstamped', [])))
    problems = []
    for name in names:
        if name in spared:
            continue
        day = stamp_day(tree.text(name), settings)
        if day is None:
            problems.append(f'{name}: no "As of <day month year>" line: a page says when its facts were read')
        elif day is False:
            problems.append(f'{name}: its "As of" line is not a date')
        elif day > today + timedelta(days=1):
            problems.append(f'{name}: its "As of" day is in the future')
    return problems


def pattern_problems(tree, names, patterns, why):
    problems = []
    for name in names:
        body = prose(tree.text(name))
        for pattern in patterns:
            for found in re.finditer(pattern, body):
                said = ' '.join(found.group(0).split())[:40]          # a phrase across a line break, on one line
                problems.append(f'{name}:{line_of(body, found.start())}: "{said}": {why}')
    return problems


def todo_notes(tree, names, settings=None):
    settings = SETTINGS if settings is None else settings
    pattern = settings.get('todo', r'\[TODO:[^\]]*\]')
    notes = []
    for name in names:
        body = prose(tree.text(name))                 # a marker quoted in code is an example
        notes += [f'{name}:{line_of(body, found.start())}: {" ".join(found.group(0).split())[:110]}'
                  for found in re.finditer(pattern, body)]
    return notes


def register_ids(settings=None, cwd=None, register=None):
    """(ids, problem): the candidate ids of the register, read from git."""
    settings = SETTINGS if settings is None else settings
    spec = register or settings.get('register', '')
    if ':' not in spec:
        return None, '[docs] register is not set (branch:path)'
    branch, path = spec.split(':', 1)
    for ref in (branch, f'origin/{branch}'):
        shown = git('show', f'{ref}:{path}', cwd=cwd)
        if shown.returncode == 0:
            pattern = settings.get('register_id', r'(?m)^### (CAND-\d+[A-Z]?)\b')
            return set(re.findall(pattern, shown.stdout)), None
    return None, f'the register {spec} is not in this clone: fetch that branch; the check did not read'


def number(ident):
    found = re.search(r'\d+', ident)
    return int(found.group(0)) if found else None


def register_problems(tree, names, settings=None, cwd=None, register=None):
    settings = SETTINGS if settings is None else settings
    ids, problem = register_ids(settings, cwd, register)
    if problem:
        return [problem]
    page = settings.get('register_page', '')
    if page not in tree.names():
        return [f'the page that tables the candidates, {page}, is not in {tree.label()}']
    prefix = settings.get('register_prefix', 'CAND-')
    word = re.compile(re.escape(prefix) + r'\d+[A-Z]?\b')
    text = tree.text(page)
    named = set(word.findall(text))
    ranges = [(int(a), int(b)) for a, b in
              re.findall(re.escape(prefix) + r'(\d+)\s+to\s+' + re.escape(prefix) + r'(\d+)', text)]

    def covered(ident):
        # CAND-10 is on the page when the page names it, its parts (CAND-10A) or the whole of a part
        if ident in named or re.sub(r'[A-Z]$', '', ident) in named or \
                any(re.fullmatch(re.escape(ident) + r'[A-Z]', other) for other in named):
            return True
        return any(low <= number(ident) <= high for low, high in ranges)

    missing = sorted((ident for ident in ids if not covered(ident)), key=number)
    problems = []
    if missing:
        shown = ', '.join(missing[:8]) + (f' and {len(missing) - 8} more' if len(missing) > 8 else '')
        problems.append(f'{page}: {len(missing)} candidate row(s) of the register are not on the page, '
                        f'by name or inside a stated range: {shown}')
    known = {re.sub(r'[A-Z]$', '', ident) for ident in ids} | ids
    for name in names:
        strangers = sorted({ident for ident in word.findall(tree.text(name))
                            if ident not in known and re.sub(r'[A-Z]$', '', ident) not in known
                            and not any(re.fullmatch(re.escape(ident) + r'[A-Z]', other) for other in ids)},
                           key=number)
        if strangers:
            problems.append(f'{name}: names {", ".join(strangers[:6])}, which the register does not hold')
    return problems


def oldid_problems(tree, names, path):
    try:
        old = {line.split()[0].lower() for line in Path(path).read_text().splitlines() if line.strip()}
    except OSError as error:
        return [f'the file of old commit ids could not be read ({error.strerror}): the check did not read']
    short = {}
    for ident in old:
        short.setdefault(ident[:7], []).append(ident)
    problems = []
    for name in names:
        text = tree.text(name)
        for found in re.finditer(r'\b[0-9a-f]{7,40}\b', text):
            token = found.group(0)
            # either may be the short form: a full id cited where the file holds the short one too
            if any(ident.startswith(token) or token.startswith(ident) for ident in short.get(token[:7], [])):
                problems.append(f'{name}:{line_of(text, found.start())}: cites a commit id from before '
                                'the rewrite; give the id the pushed history holds')
    return problems


def check(tree, only=None, settings=None, cwd=None, register=None, old_ids=None, today=None):
    """(problems, notes, counts) for a tree."""
    settings = SETTINGS if settings is None else settings
    wanted = [name for name in CHECKS if not only or name in only]
    own = pages(tree, settings)
    every = own + foreign(tree, settings)
    problems, notes, links = [], [], 0
    if not own:
        return [f'no page of [docs] pages is in {tree.label()}: nothing was read'], [], {'pages': 0, 'links': 0}
    if 'links' in wanted:
        found, links = link_problems(tree, every, settings, cwd)
        problems += found
    if 'names' in wanted:
        problems += name_problems(tree, every, settings)
    if 'orphans' in wanted:
        problems += orphan_problems(tree, own, settings)
    if 'stamp' in wanted:
        problems += stamp_problems(tree, own, settings, today)
    if 'words' in wanted:
        problems += pattern_problems(tree, own, settings.get('fluff', []),
                                     'an adjective where a number, a constraint or a link belongs ([docs] fluff)')
    if 'conduct' in wanted:
        problems += pattern_problems(tree, own, settings.get('conduct', []),
                                     'a working rule stated on a public page ([docs] conduct): it lives off GitHub')
    if 'markers' in wanted:
        problems += pattern_problems(tree, own, settings.get('markers', []),
                                     'a marker left for another hand ([docs] markers)')
        notes = todo_notes(tree, own, settings)
    if 'register' in wanted:
        problems += register_problems(tree, own, settings, cwd, register)
    if 'oldids' in wanted and old_ids:
        problems += oldid_problems(tree, every, old_ids)
    return problems, notes, {'pages': len(own), 'foreign': len(every) - len(own), 'links': links}


def staged_problems(cwd=None, settings=None):
    """For the commit hook: the checks on the index, when the commit is on the pages' branch and
    stages a page. Nothing otherwise."""
    settings = SETTINGS if settings is None else settings
    if not settings.get('pages'):
        return []
    branch = git('symbolic-ref', '-q', '--short', 'HEAD', cwd=cwd).stdout.strip()
    if not any(fnmatch.fnmatchcase(branch, glob) for glob in settings.get('branches', [])):
        return []
    staged = [name for name in git('diff', '--cached', '--name-only', '-z', cwd=cwd).stdout.split('\0') if name]
    globs = settings.get('pages', []) + settings.get('foreign', [])
    if not any(fnmatch.fnmatchcase(name, glob) for name in staged for glob in globs):
        return []
    problems, _, _ = check(Tree(staged=True, cwd=cwd), settings=settings, cwd=cwd,
                           old_ids=settings.get('old_ids') or None)
    return [f'the pages: {problem}' for problem in problems]
