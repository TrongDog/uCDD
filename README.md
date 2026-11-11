# uCDD method: the change loop, its hook, the test matrix and the ledger

Tooling for working on uCDD, kept apart from the driver. It puts the agreed
order of work into these pieces:

| Piece | What it does |
|---|---|
| `skills/change-loop/SKILL.md` | A Claude Code skill: the order of one change (spec, family, baseline, reproduce, row first, fix, prove, close), honest results, the check before `fixes` |
| `hooks/commit-msg`, `method.toml` | A git hook that refuses a code commit without its row and its evidence |
| `matrix/matrix.toml`, `matrix/plan.py` | One definition of the test matrix, and a planner that turns a diff into the runs it needs |
| `tools/ledger.py` | The results ledger: the runners record each verdict and the binaries it was for, and the bench's commit on every entry they record; the hook reads it; the runners commit its runs file at each plan's end (`commit-runs`, a runner's only: the token; calbatch.py, plan_run.py, and sndreg run by hand), and `plan.py --save` a saved plan (`commit-plan`) |
| `guard/guard.py` | A Claude Code hook: no `--no-verify`, no hand-written ledger, no git command that stages, restores or checks out a protected path, no runners' token by hand, no write into the game library, no commits through the GitHub tools, nothing to the upstream, no command but the runner's own wait while 86Box records |
| `tools/trailers.py` | Counts Issue:, Lesson: and Evidence: trailers in the history |
| `tools/game.py` | Before a game runs: its engine, driver versions and family, looked up in the library; what the notes lack |
| `tools/ci.py`, `ci/method.yml` | The checks on GitHub: every branch built with its headroom, and the hook's checks on commits made after the hook went in |
| `bench/` | The bench's backups: the bench folder in a private repository, the notes versioned on the machine only, a pre-commit check against game and heavy files, the hourly snapshot on a ref of its own (never on the working branch), and how to restore it all on a new machine (bench/README.md) |
| `install.sh`, `tests/test_method.py`, `lib/methodlib.py` | Install per worktree; self-tests (the others in `tests/`: each round's or decision's own, such as `test_moves.py` and `test_ledger_commit.py`, 6 Nov 2026, and `test_guard_git.py`, `test_commit_token.py`, `test_fork_moves.py` and `test_runs_size.py`, question 67 (7), with the runners' own `runs/test_runner_end.py` in the bench); what the pieces share |

Standard library only: Python 3.11 or later (tomllib), git, sh.

## Why a branch of its own

This branch shares no history with the driver's branches, like
`reference-library`: git refuses to merge it into `fixes` without
`--allow-unrelated-histories`, so a `.claude/` or test tooling never rides
into a fix by accident. Nothing from this fork goes to the upstream at all
(see "Nothing goes upstream" below).

## Install

From the uCDD clone:

    git fetch origin claude/brave-franklin-6h9xzo
    git worktree add ../method -b method origin/claude/brave-franklin-6h9xzo
    UCDD_REF=irq-counters python3 ../method/tests/test_method.py
    sh ../method/install.sh <worktree> [<worktree> ...]
    sh ../method/install.sh --claude <the directory Claude Code runs in>

- **Which worktrees:** all the worktrees share one hooks directory, so
  install.sh sets `core.hooksPath` per worktree (`git config --worktree`,
  after `extensions.worktreeConfig`). Worktrees you don't name never see the
  hook. `sh install.sh --remove <worktree>` takes it out again.
- **Claude Code:** `--claude` links the skill into `<dir>/.claude/skills` and
  prints the PreToolUse lines to merge into `<dir>/.claude/settings.json`
  (the guard, for Bash, Monitor, file edits and the GitHub tools). It does not edit
  the settings itself.
- **The self-tests:** they make commits in a temporary worktree of
  `UCDD_REF` and remove it afterwards, with a temporary ledger.

## What is not in git (redo it on a new machine)

- **NASM on PATH** wherever commits are made: the hook builds to prove
  `Evidence: none` and to compare a plan's binaries, and refuses when nothing
  builds.
- **`method.local.toml`**: `[games] paths` and the bench's banned words.
- **`GAMES`** in the runners' environment: the game runner's command reads
  `$GAMES/{library}`.
- **The hook**, per worktree: `sh install.sh <worktree> ...` (it is safe to
  run again).
- **The skill link and the guard** in Claude Code's settings:
  `sh install.sh --claude <dir>` prints the lines to compare.
- **The ledger** (`ledger/`, or `[ledger] path`): its results and saved plans
  exist only where the runners wrote them. Keep it in the bench's top
  folder, versioned on the machine (its runs file committed on main by
  `ledger.py commit-runs` at each plan's end, each hour's snapshot holding
  the lines since) and copied to the backup disk (bench/README.md); a lost
  ledger means plans are saved and run again before a commit can cite them.
- **The self-tests** need `UCDD_REPO` (a uCDD clone) and `UCDD_REF`, and NASM
  on PATH, or most of them skip.

There are no other environment variables: `UCDD_LEDGER`, `UCDD_GAMES` and
`UCDD_METHOD_LOCAL` only override method.toml, and `UCDD_SPOT=1` marks a
spot check. `UCDD_LEDGER_RUNNER` is the runners' token for their own
`commit-runs` call (question 67 (7)): nobody sets it by hand, and the guard
refuses a shell command that does.

## The hook

A commit that touches `src/` or `scripts/build.py` is a code commit. Any
other commit is a notes commit and needs nothing. A code commit needs these
trailers in the last paragraph of its message:

    Issue: F17
    Evidence: data sheet: SBG 6-12, a 14h block ends on its last byte
    Evidence: emulator: plan 3f2a91c4, 46 runs, all passed (ledger), D10 against D9: F17 gone

- **`Issue:`** must name a row that is already committed: in ISSUES.md or
  `docs/*.md`, at the parent commit or on `sound-engine-library` or
  `spec-first`. A row added in the same commit as the code is refused. That
  is step 5: the row before the fix.
- **`Evidence:`** starts with a grade:
  - `data sheet` (also: doc, spec)
  - `emulator` (also: 86Box, DOSBox-X, QEMU, trace)
  - `hardware` (also: hw)
  - `reading`: no check could fail on the old build
  - `none`

  Every code commit needs a `data sheet` line (rule 1). When the documents
  are silent, the line says so: `Evidence: data sheet: silent; the CT2291
  decided`.
- **A plan named in an emulator line** ("plan 3f2a91c4") is checked against
  the ledger: the plan must be saved and unedited, every one of its runs
  recorded as a pass, and the binaries each run recorded must be the ones
  this commit builds (the hook builds the staged tree to compare). See "The
  ledger".
- **`Evidence: none`** claims the binaries don't change (comments, names,
  layout). The hook proves it: it builds the parent and the staged tree with
  each variant in method.toml and compares the EXE and BIN files, which takes
  about 15 seconds. On a mismatch it builds both sides again before refusing,
  because this machine has had memory faults.
- **`Paths:`** is needed when the commit changes code under a join: a label
  whose comment names its incoming paths, as the data-flow pass wrote them
  ("Joined from", "Called from", "On both paths"; 16 such labels on
  irq-counters). The trailer names the label, after every path into it was
  checked against the comment (lesson L2). It is recall at the moment of
  the change, not proof: the hook shows the comment and asks for the name.
  An `Evidence: none` commit is exempt.
- **`Family:`** names the sound engine family the fault belongs to (rule 10),
  from `[families]` in matrix.toml, or says `none` and why it is no one
  family's. The family's page in the library (`HEAD` or the
  sound-engine-library branch) must already name the row: the knowledge goes
  back to the whole family before the fix. When the commit cites plans, one
  of them must survey the family (`plan.py --family`). An `Evidence: none`
  commit is exempt.
- **Game code, refused in every commit** (the owner, 20 Oct 2026: we never
  ship, patch or alter game code; any game as it was sold must run with uCDD
  alone): a program, driver or disc file by its suffix (`[games] suffixes`),
  a file the census knows as a game's driver under any name, three or more
  lines of a disassembly listing, two or more lines with a decompiler's own
  names (Ghidra's `FUN_0001a2b4`, `DAT_`, `undefined4`, `unaff_`, `in_AX`),
  and a game's folder name or a program name
  in a string in driver code (a special case; comments may name games). Run
  over 187 recent commits of fixes, irq-counters, sound-engine-library and
  spec-first, it finds nothing (two false alarms were fixed on the way: a web
  address, and the English word "undefined").
- **No local path, in every commit** (the owner, 20 Oct 2026): a home directory
  (`/home/<name>/`, `/Users/<name>/`, `C:\Users\<name>\`) is refused in the
  message and in every added line. The bench's own paths and account name
  live in `method.local.toml` (below), which git ignores.
- **Refused in every commit**, in the message and in every added line: the
  bench's nickname (rule 7), and an @mention of the upstream author or a
  link to one of his issues or pull requests. The patterns are in
  method.toml.
- **Not checked:** merge commits are checked for the banned patterns in their
  message only. Branches matching `archive/*` are not checked at all.

When it refuses, it says what is missing and keeps the message in
COMMIT_EDITMSG. Claude never bypasses it. A person who must can use
`git commit --no-verify` in their own shell.

All of it is in method.toml: which paths count as code, the grades, the notes
refs, the build variants, the ledger.

## The bench's own settings

`method.local.toml`, beside method.toml, is never committed (`.gitignore`).
Its tables merge into method.toml's and its `[[banned]]` entries add to the
list, so the bench can ban its own account name without publishing it:

    [games]
    paths = ["<the game library>", "<its disc images>"]

    [[banned]]
    pattern = '(?i)<the account name>'
    why = "the bench's account name"

`UCDD_METHOD_LOCAL` points at another file. The runners' commands in
matrix.toml name the library as `$GAMES`, which the bench sets in its own
environment.

## The matrix and the planner

`matrix/matrix.toml` holds:
- **The axes:** physical card, physical IRQ, virtual model, virtual IRQ,
  mode, MIDI, client and build.
- **Parked and opt-in values:** the ESS work is parked; `base`, `free` and
  the verify build are opt-in.
- **Defaults:** the owner's lines of 20 Oct, including the older models on IRQ
  7.
- **Constraints** taken from the code.
- **The environment** each value sets, and the runners' command lines.
- **Every test:** the probes, one game per family, and the findings' own
  cases.
- **The areas:** which files need which tests, varied over which axes.

From a uCDD worktree:

    python3 ../method/matrix/plan.py --base irq-counters --save   # this topic's change
    python3 ../method/matrix/plan.py --files src/audio/irq.asm
    python3 ../method/matrix/plan.py --test JILLJUNG --baseline    # with runs without uCDD (step 3)
    python3 ../method/matrix/plan.py --group pc                # add the PC's runs
    python3 ../method/matrix/plan.py --format tsv              # for a runner
    python3 ../method/matrix/plan.py check                     # after every edit to matrix.toml

**What a plan contains.** For each test it reaches, the plan covers:
- every value of a varied axis;
- every pair of values across two varied axes;
- every combination of an area's `full` axes. The interrupt area has `full`
  set on the two IRQ lines, so 5/5, 5/7, 7/5 and 7/7 always run.

Every run holds the driver on (`mode engaged`, GL_CFG_V4=1,0) unless the test
asks for `base` or `free`.

**How it is laid out:**
- Probes come first, up to seven at a time.
- Recordings come after, one at a time.
- Runs on the PC come last.

**What else it lists:**
- the estimated time;
- the coverage of each axis;
- "Blocked" tests: needed by the change, but missing a launcher ID or a
  program;
- the `Evidence:` line the commit can carry once the ledger shows every run
  passed.

**For regress.sh and sndreg:** the aim is one definition, so these should
read the matrix instead of keeping their own lists:
- **regress.sh** reads `--format tsv` (run, phase, kind, test, build, env,
  command).
- **sndreg** imports the planner:

      sys.path.insert(0, '<method>/matrix')
      import plan
      matrix = plan.load()
      matrix.group('families')                      # the test names
      config = matrix.config('JILLJUNG', {'vmodel': 'pro'})
      matrix.env('JILLJUNG', config)                # GL_IRQ=5 GL_VIRQ=7 GL_VMODEL=1 GL_CFG_V4=1,0

  Once they do, delete the lists in regress.sh (a, b, c), MODELS in
  sndreg/games.py and fixtest.SOUNDS.

## Fix by family (rule 10)

The sound engine library on `sound-engine-library` is the source; the tools
read it rather than keep their own copy.

- **Before a game runs:** `python3 ../method/tools/game.py <its folder>` finds
  its driver files by the names the census knows, hashes them as the census
  does, and looks up the game in inventory.md, each version in census.md and
  its families in matrix.toml, with the findings its family page names. It
  exits 1 and says what to add when the notes lack a game, a driver version,
  a trace or a family. Engines built into the game have no driver file: the
  inventory row is their only record. A game that runs from its disc image
  keeps its drivers there, to be scanned by hand.
- **The survey:** `plan.py --family <family>` plans one traced game per driver
  version of the family's digital drivers (`survey` in `[families]`;
  `--driver` for others), each run as its driver's card, plus every traced
  game of the family whose engine is built in. A version nobody has traced
  is listed under Blocked with the games that carry it. Survey games are
  named as the census names them; `[launchers]` maps a folder name to its
  launcher where they differ.
- **The commit:** `Family:`, the row on the family page first, and the survey
  in the cited plan (see "The hook").

## The ledger

Evidence is what a tool wrote, not what an agent says. The runners record
each verdict once a run is judged:

    python3 ../method/tools/ledger.py record <tag> <run> pass|fail \
        --build-dir <the directory the run's UCDD.EXE came from> \
        --tool runs/sndreg/sndreg.py --tool runs/rec/audiocmp.py --output <the recording>

- **What an entry holds:** the time, the plan and run, the verdict, the hash
  of every EXE and BIN in the build directory, the hash of each tool given
  (it pins the instrument exactly, whatever its folder's history says), the hash of
  each output, the host, and, on every entry calbatch.py, plan_run.py and
  sndreg record, the bench's commit the plan started from and how many
  tracked files differed from it then (`--bench-commit`, `--bench-changed
  N`; the files themselves are named once, in the plan's log; null when git
  could not read them; sndreg run by plan_run carries the plan's, as
  plan_run read it at the plan's start: the owner's decision of 6 Nov 2026 on
  question 67 (7), built, not run. Corrected 6 Nov 2026, the rule 7 form;
  old text: "and null from the other runners, plan_run.py and sndreg, which
  do not pass them yet: question 67"). the owner's decision of 6 Nov 2026: "The 'bench
  commits before a plan' rule stays, its reason now reproducibility: the
  plan's commit hash is in the ledger". So every bench change a plan will
  use is committed before the plan starts, and the hash names the bench's
  tracked files at the plan's start; runs/src (the method), ignored files
  (the fixtures' pinned builds, kit, vms) and untracked files are not
  covered. N is then 0, but for results records an earlier plan's rolling
  archive re-pointed and nobody committed yet: results/ is tracked, and
  the archive rewrites the records whose captures it moves (their
  `sound_archived` field). The plan's log names them with the rest; read
  the names first: those are the archive's, not a broken rule, and are
  committed before the next plan.
- **Where it lives:** `ledger/` beside this README (ignored by git), or
  `[ledger] path` in method.toml, or `UCDD_LEDGER`. The ledger is append
  only: `runs.jsonl`, the saved plans in `plans/`, and `superseded.jsonl`,
  the files set aside (the owner's decision of 6 Nov 2026 on question 68:
  "The "moved aside by hand" whole-file reports are recorded as superseded
  in the ledger, never deleted"). `ledger.py supersede PATH ... --why
  TEXT` records each file's path, sha256 and size with why and the date,
  renames each PATH beside itself to NAME.superseded-YYYYMMDD, and commits
  the file alone on main as commit-plan does. It is refused while a plan
  records (its own check and the hook's), and a failed rename, write or
  commit puts everything back (tests/test_ledger_supersede.py). Corrected
  6 Nov 2026 (rule 7 form); old text: "The ledger is append only:
  `runs.jsonl` and the saved plans in `plans/`."
- **Its commits** (the owner's decision of 6 Nov 2026: "the ledger's runs file
  on the top folder's main is committed by the tool at each plan's end
  (calbatch invoking ledger), never by the agent's hand and no longer by the
  backup"): calbatch.py, once a plan's last run is recorded or the plan is
  BLOCKED between batches, releases its recording flag, runs
  `ledger.py commit-runs <tag> --why <how it ended>`, and only then logs its
  closing line, `plan <tag>: ended, all runs complete|BLOCKED (...)`, the
  log's last on every end, its brackets saying what commit-runs did: `ledger
  committed <hash>`, `ledger: nothing new` (commit-runs printed so: nothing
  to commit) or `ledger refused: <its reason>`. It commits the runs
  file alone on main in the repository that holds the ledger, through that
  repository's own pre-commit, the message naming the plan, how it ended,
  its verdicts as `show` counts them, the lines added by plan since the
  runs file's own last commit (HEAD named beside it) and the bench commit
  they were recorded on. It refuses when anything else is staged,
  off main, and when the file's earlier lines differ from its last commit
  (the ledger only grows). A refused commit, a kill or a crash commits
  nothing; the next plan's end takes every line since. `--dry-run` says
  what it would commit, and the file's size beside the bench check's
  20 MB, which skips this file by its path (the owner's decision of 6 Nov 2026
  on question 67 (7): "the bench size check excludes the ledger's runs file
  by path, and from A7 the ledger rolls the file per gate"; built, not run;
  old text: "and the file's size against the bench check's 20 MB"), and
  commits nothing. commit-runs runs only when a runner invoked
  it (the owner's decision of 6 Nov 2026 on question 67 (7): "`ledger.py
  commit-runs` refuses to run unless invoked by calbatch (a token calbatch
  sets), so a hand invocation fails"): the runner (calbatch.py, plan_run.py
  or sndreg) puts `UCDD_LEDGER_RUNNER=<its script's file name>:<its process
  id>` in the environment of its commit-runs call, run as its own child with
  no shell between, and commit-runs refuses unless that process is its
  parent and runs that script; typed by hand it refuses, `--dry-run`
  included, and the guard refuses it and the token set by hand
  (tests/test_commit_token.py). Corrected 6 Nov 2026 (the rule 7 form). Old
  text: "The saved plan is the agent's to commit, with the plan." New text:
  `plan.py --save` commits the saved plan's file alone on main
  (`ledger.py commit-plan <tag> [--why TEXT]`, its subject "Plan <tag>:
  <why>"), refused off main and while anything else is staged, as
  commit-runs; a refused one (while a plan records the top folder's check
  refuses any commit) is committed later by `ledger.py commit-plan <tag>`,
  which may be typed by hand. A saved plan's file is never staged by hand:
  the guard refuses it (tests/test_guard_git.py). Built, not run. Where the
  decision's words are silent (all three runners hold the token; a hand
  `commit-runs --dry-run` refused by "refuses to run"; `commit-plan` typed
  by hand allowed; the guard's bare `git reset` and `reset --soft`, the
  commands that write the work tree from commits, and its wide reading,
  below) the agent chose, applied, and put the set to the owner: the agent's
  choice, confirmed by the owner 6 Nov 2026 (68.1).
  calbatch.py's and plan_run.py's plans commit at their ends (plan_run.py's
  closing line "plan P: ended, all runs done|stopped by boxcheck (...)"),
  and sndreg run by hand commits at its end when it wrote its entry, its
  closing line in its run's own name ("sndreg TAG: ended, check|judge
  (...)"); under plan_run, sndreg commits nothing and plan_run's end takes
  its lines; each sets the token above on its own commit-runs call
  (the owner's decision of 6 Nov 2026 on question 67 (7); built, not run:
  runs/test_runner_end.py). Corrected 6 Nov 2026 (the rule 7 form). Old
  text: "Only calbatch.py's plans commit at their ends: plan_run.py and
  sndreg do not, so their lines wait for the next calbatch plan's end
  (question 67)."
- **Who writes it:** the runners only. `record` refuses a plan that was not
  saved first (`plan.py --save`) and a run the plan does not have. The guard
  refuses `ledger.py record` typed by Claude, edits of the ledger's files, and
  shell commands other than git that name them. Corrected 6 Nov 2026 (the
  rule 7 form). Old text: "and shell commands that name them". New text: git
  commands are not checked for the ledger's files (guard.py's bash_refusal
  sends a git command to its git rules alone), so `git add`, `git commit -a`,
  `git checkout --`, `git restore` or `git reset` naming the runs file pass
  the guard: "never by the agent's hand" holds by the agent's discipline
  only. Open: question 67, for rules-bot and the owner. Answered (the owner's
  decision of 6 Nov 2026 on question 67 (7): "the guard treats a git command
  that stages, restores or checks out a guard-protected path as a write to
  it"; built, not run): the guard reads what a git command reaches, its
  paths (a pattern as the folder its fixed part names, git's `:/` and `:!`
  magic read) and the whole work tree for a whole-tree form (`add -A`, `-u`,
  `.`; `commit -a`; a branch checkout or switch; `checkout -f`; `reset` with
  no path, with a commit alone (`--soft` too) or with `--hard`; `stash`;
  `clean` the folder it runs in; `merge`,
  `rebase`, `cherry-pick`, `revert`, `pull`, `am`, `apply`), from the folder
  it runs in (the cwd, a `cd` earlier on the line, `-C`, `--work-tree`,
  `GIT_WORK_TREE`), and refuses one that reaches the ledger's folder or a
  game library. In the top folder, which holds both, no whole-tree form
  passes: its files are named (`git add FILE`, `git restore --staged FILE`,
  `git commit -m MSG -- FILE`). Read-only commands (`log`, `show`, `diff`,
  `status`, `cat-file`, `ls-files`, `blame`) and dry runs pass. It reads the
  words only, never the index or the .gitignore. The line's own variables
  (`T=DIR; git -C "$T" ...`, `export`) are read into its words (the
  program's name too: `G=git; $G add -A`), PWD and
  OLDPWD follow its `cd`; a writing command whose folder or path is not known
  before the line runs (a variable the line does not set, `$( )`, a
  backquote, `cd -`, `popd`, a `cd` after `eval` or `source`, a git dir not
  named `.git`) is refused; a pattern exclusion (`':!*.md'`) frees nothing;
  a git dir's own repository (`--git-dir`, `GIT_DIR`) is reached as well;
  code given to `sh -c` or `eval` is read as a line of its own; shell
  keywords (`if`, `do`, `{`) and env's `-u`, `-C` and `-S` are read; a
  newline is the shell's command break, a backslash-newline is joined,
  comments are taken out and a here-document's body is its command's input
  (the git rules skip it, the token and ledger rules read it). Not
  read: git and shell aliases, launchers other than env, command, builtin,
  exec, nohup, setsid and time (sudo, xargs, find -exec, timeout), the code
  of a substitution inside double quotes or a backquote (the word itself is
  unknown), `git init` or `clone` into a library, `commit --amend` over a
  runs file commit, a push from a folder the guard cannot follow (judged by
  the remote's name alone) (tests/test_guard_git.py). With this rule
  `tests/test_method.py`'s guard tests give each call a cwd, the system's
  temporary folder, in no work tree: without one, its `git commit -am "fix
  -n"` was read in the folder the test ran from and refused in the top
  folder (built, not run). the owner can record a run by hand in his own shell.
- **Reading it:** `ledger.py show <tag>` (every run's latest verdict), `spot`
  and `audit` (below).
- **Turning it on fully:** with `[ledger] require = true`, every emulator line
  must name a recorded plan. Leave it off until the runners call `record`,
  then switch it on.
- **What it does not stop:** an agent that edits a runner to record a pass it
  did not see. That is deliberate forgery, not a rounded-up summary, and the
  spot checks are there to catch it.

**The spot check before `fixes`.** A session with no stake in the fix runs
`ledger.py spot <tag>`, which picks two passed runs at random and prints
their commands. It re-runs them with `UCDD_SPOT=1` set, so the runner records
them as spot checks. Then `ledger.py audit <tag>` compares each with its
first verdict. A disagreement stops the merge: it is a finding about the fix
or about the instrument (L11).

## Game code

We never ship, patch or alter game code. Any DOS game, as it was sold, must
run with uCDD as it would on the real hardware, with no patch, extra file or
setting for that game. Decompiled or traced code only teaches what a game
expects of the hardware; the notes say it in words.

- **The hook** refuses game files, listings and games named in driver code
  (see "The hook").
- **The guard** refuses a write into the game library: an edit, an overwrite
  (`cp` onto it, `>`, `dd of=`, `xxd -r`), a move or a removal, and an in-place
  `sed`/`perl`. Reading, hex dumps, disassembling into another directory and
  copying out are allowed, and so are the runners, which set a game's own
  configuration as its setup program would. Set `[games] paths` in
  method.local.toml to the library and its disc images (or `UCDD_GAMES`).
- **While 86Box records** (the owner's decision of 11 Nov 2026 on the 09:45Z
  report, item 5) the guard refuses any command but the runner's own wait,
  `python3 runs/calbatch.py PLAN.tsv --wait [first]` (or plan_run.py's),
  alone on its line; Edit and Write of text stay open. The mark is the
  bench's runs/recording.flag, which the runners set and clear; a mark with
  no 86Box (or DOSBox-X) alive is reported as stale and holds nothing
  (tests/test_guard_recording.py). The runners refuse to start a plan saved
  without its lessons_read line, and `plan.py --save` needs
  `--lessons-read` (the bench's runs/test_plan_lessons.py).
- **The GitHub tools** cannot commit files (the guard refuses
  `create_or_update_file`, `push_files` and `delete_file`): commits are made
  with git, where the hook sees them.

## Nothing goes upstream

Nothing from this fork goes to vorvek (the owner, 20 Oct 2026). What reaches
him on GitHub, and what does not:

- **Reaches him:** a pull request or issue on his repository, a comment
  there, an @mention of him, and a link to one of his issues or pull
  requests from a commit or a note (it shows on that issue).
- **Does not reach him:** pushes to this fork, its branches and any CI it
  runs. The fork is public, though, and listed among his repository's
  forks, so anyone, him included, can read it.

The hook refuses the mention and the links. The guard refuses a push to his
repository, gh and GitHub-tool writes there, and a `gh pr create` that does
not name `--repo TrongDog/uCDD` (in a fork, gh and GitHub's own page offer
the original repository as the target).

## Nothing personal goes to GitHub

The owner's rule of 10 Nov 2026 (tightening r3.10, gate T12): "If it doesn't need to be on
github as part of the project, then it doesn't go to github." Never, in a file, a commit
message or a commit's identity, on any repository that has a remote: his first name, his city,
the host's name, a login of his, a LAN address, a mount name, a Claude session link. In
everything written for GitHub he is "the owner". The words themselves are `[[banned]]` entries
with `personal = true` in `method.local.toml`, never in a pushed file; `method.toml` carries only
the session link and the list of third-party trees. `lib/privacy.py` has the whole of it in its
first lines.

- Three gates, each reading the same list: the commit-msg hook (the message, the identity, the
  clock, the added lines), the bench's pre-commit (the lines its hourly snapshot adds too), and
  the pre-push hook, the last one: every commit about to leave, whatever made it (a rebase, a
  cherry-pick and `git am` run no commit-msg hook). The guard refuses `git push --no-verify`.
- Every worktree has them: the code worktrees and this one through their hooks path, the rest
  of a uCDD clone (the notes, the references) through `sh install.sh --shared CLONE`, a bench
  repository through `sh install.sh --bench REPO`. `python3 lib/privacy.py doctor` says which
  worktree lacks one, and whether this shell's identity and clock are clean.
- A refusal names the rule and never prints the word. A word that is someone or something else
  (a document's author with the same first name) stops the commit until the owner approves it,
  once: `[privacy] allow_phrases` or `allow_paths` in `method.local.toml`.
- The upstream author's commits are read against the personal entries only. Dates are written
  in UTC (`[privacy] utc_dates`): a clock offset places the machine that made the commit.
- The bench's older records are not rewritten (the ledger holds their hashes): there a file
  that already held a word may be edited and keep it, and a file that did not may not begin to.
- `tools/privscan.py` reads a whole history against the list (the gate's reading);
  `tools/privrewrite.py` rewrites the fork's own history once, checks its own work and pushes
  nothing; its `reword` does a work tree whose history stays.

## The pages keep up

The owner's rule of 10 Nov 2026 (tightening r3.11, gate T13). The fork's public pages (the front
page and `docs/` on the pages' branch) are a view of the rows, and a view drifts unless something
holds it to them. Found on the day the rule was made: the front page listed features the source
on its own branch does not have; the table of candidates stopped at CAND-32 while the register
held 169 rows; one page said a build had not been run that another page reported on; three
pages carried figures and no day.

What a program checks (`lib/docs.py`, `tools/doccheck.py`, `[docs]` in method.toml), at every
commit on the pages' branch that stages a page, and on GitHub at every push and every hour:

| Check | The rule |
| --- | --- |
| links | Every relative link and image resolves in the same tree, and its `#anchor` to a heading or an `<a id>`; a link into this repository on GitHub resolves in the branch it names. |
| names | A link into this repository names it as it is named now. |
| orphans | Every page is reached from the front page and is listed in the index (`docs/README.md`). |
| stamp | Every page says the day its facts were read ("As of 10 November 2026"), and not a day to come. |
| words | No word of `[docs] fluff`: a claim is a number, a constraint or a link. |
| markers | No marker left for another hand (`[agent: ...]`). `[TODO: ...]` is counted and listed, never refused: a gap that is named is not drift. |
| register | Every candidate id in the register (`notes:ISSUES.md`) is on the page that tables the candidates, by name or inside a stated range; no page names an id the register lacks. |
| conduct | No sentence of `[docs] conduct`: a working rule (what was not done or will not be sent to anyone, who decides, how a rule is enforced) stated on a page. |
| oldids | With `[docs] old_ids` set in method.local.toml: no page cites a commit id from before a rewrite. |

A check that cannot read what it needs (the register's branch not fetched) says so as a problem;
it never passes unread. `tests/test_doccheck.py` plants each fault alone and its own check, and
no other, must refuse it.

What a program cannot check, and the second reviewer holds:

1. **A page is a view of the rows.** Where they disagree the row is right and the page is
   corrected, in the same piece of work that moved the row.
2. **A number has one home.** The stage of the work is STATUS's, the candidates KNOWN-ISSUES's, a
   build's identity REFERENCE's, a limit CALIBRATION's. Another page links there, or quotes the
   number with the home page's day beside it. A commit id is written on REFERENCE and nowhere else.
3. **Each kind of page keeps to its kind** (after Diataxis): a tutorial is followed top to bottom
   and explains nothing it does not need; a how-to is one task; a reference page is tables and
   does not argue; an explanation does not give steps. The index says which is which.
4. **A hypothesis is labelled** and is never a finding; one that turned out wrong stays, dated.
5. **A decision that replaced another** is added to DECISIONS with what it replaced, and the old
   entry is marked superseded, not removed. An experiment that overturned a belief is added to
   EXPERIMENTS as hypothesis, test, result, conclusion.
6. **Nothing moves without a map.** A page that is split, merged or renamed is moved with a line
   for each of its sections saying where it went; nothing is deleted to make a page look cleaner.
7. **When a gate closes, a candidate opens or closes, or a build is pinned**, the page that is
   that fact's home moves in the same piece of work, and its "As of" line with it.
8. The pages say what was measured in an emulator and never that anything is confirmed on
   hardware before a person has run it there. No page says why the history was rewritten.
9. **A page says what the thing is, what it does and what was measured** (the owner, 11 Nov
   2026). It does not say what the project has not done toward anyone, what it will or will not
   send to anyone, who decides what, or how its rules are enforced: those are working rules and
   live off GitHub. `[docs] conduct` refuses the sentences someone has listed; the rest is the
   reader's (L54).

## On GitHub

The workflow lives on `fixes` as `.github/workflows/method.yml` (a copy of
`ci/method.yml`; the owner, 20 Oct: acceptable on fixes for now, to be
reviewed). It runs only in this fork.

- **When:** on a push to a branch that has the file (fixes, and branches
  made from it or merged with it after the file went in), every hour for
  every branch, and from the Actions tab (Run workflow).
- **What:**
  - Every branch head with scripts/build.py is built with each variant in
    `[identical] variants`, and the headroom of UCDD.EXE, the host,
    UCDDPLAY and UCDDSET is reported against build.py's limits, naming the
    build where each is tightest.
  - Every commit made after `[ci] check_after` gets the hook's checks, apart
    from the ledger, which is on the bench. A commit made with the hook off,
    or from another clone, shows up here.
- **Where the results go:** commit statuses (`method/build` on a head,
  `method/commits` on each commit; a commit that has one is not checked
  again) and the run's summary. GitHub tells the account that last changed
  the schedule in the workflow file when a scheduled run fails.
- **Turning it on:**
  - If the Actions tab says workflows are not run on this fork, enable them
    there.
  - Set `[ci] check_after` to the time the hook went in (a commit on this
    branch). Until then only the builds are checked.
  - If this branch is renamed, set the repository variable `METHOD_REF` to
    the new name.
- **What it cannot do:** run 86Box, the games or the PC; read the ledger.

Locally: `python3 tools/ci.py --dry-run [--branch NAME] [--check-after DATE]`
from a clone.

## The tally

    python3 ../method/tools/trailers.py [--since 2026-10-01] [refs]

This counts each Issue:, Lesson: and Evidence: grade across the history,
with dates. A row that keeps coming back in Issue: trailers is a fault that
was not fixed by family.

The lessons' weights are not computed here. LESSONS.md and its
`lessons.py` hold them: each hit scored by its severity (1 to 4) and doubled
when the answer was already written and not used. A `Lesson: Ln` trailer
only links a commit to the lesson it hit, so the Lesson counts here are a
cross-check: every trailer should have its hit line in the register.

## Not done yet

- **`[games] paths`** belongs in the bench's method.local.toml, or the guard
  cannot protect the library.
- **The runners do not record yet.** regress.sh, sndreg, game_live.py and
  probe_test.py each need a `ledger.py record` call after a run is judged,
  with the build directory, the tools and the outputs; then `[ledger]
  require = true`.
- **Lines marked "check" in matrix.toml** are the seed's best reading of the
  bench's report: the PROBE_RUN names, the GL_CFG_V4 fields, the runners'
  arguments, the bset suffixes, and what some probes check. The `[builds]`
  options must be the ones bset.sh uses, or the hook's binary comparison
  will refuse good runs.
- **Tests that need a launcher ID or a fact:**
  - F1: Warcraft or System Shock;
  - F4: Doom, Hexen or Raptor;
  - F15: Fade to Black;
  - XCOMUF's family and client;
  - the three games in sndreg/games.py that are not in the matrix yet.
- **Tests no area has yet:**
  - a step-aside test (mode `free`, byte-for-byte state across transitions);
  - UCDDSET's checks;
  - playcheck for UCDDPLAY.

  The plan names each as a warning when its area is hit.
- **The matrix is kept here, not with the bench folder it describes.** The
  bench folder is versioned now, in a private repository (bench/README.md),
  but the hook, the planner and GitHub's checks read the matrix from this
  branch and cannot see that repository.
- **`[ci] check_after`** is empty: GitHub builds every branch but checks no
  commits until it is set to the time the hook went in.
- **An amend** can fold a row into the code commit it should precede. The
  hook sees only the parent.

## For the session that runs the bench

> This branch is the method the owner and a cloud session agreed on 20 Oct, built
> from your status report. Please read README.md and skills/change-loop/SKILL.md,
> then:
> 1. Run the self-tests.
> 2. Install the hook in the worktrees the owner names (at least `irqcnt` and
>    `sndlib`).
> 3. Link the skill and merge the guard into the settings.
> 4. Go through every line marked "check" in matrix/matrix.toml and the "Not done
>    yet" list, and correct the matrix from what the bench actually does.
> 5. Point regress.sh and sndreg at the matrix and delete their own lists.
> 6. Make the runners call `ledger.py record` after each judged run, then set
>    `[ledger] require = true`.
> 7. Then plan the next change with `plan.py --save` before running anything.
>
> Where this disagrees with your guards or the lessons register, say so to the owner
> rather than working around either.
