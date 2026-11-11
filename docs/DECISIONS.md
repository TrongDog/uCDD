# Decisions, and what was tried and dropped

Written by Claude. As of 10 November 2026. Each entry is a short decision
record: the situation, what was decided, what was rejected and why, and
what it cost. They are here so that nobody repeats a dead end. Newest
decisions are at the bottom of each group.

A decision that was later replaced stays, marked *Superseded*, with the
entry that replaced it.

Where the reason for a decision is not in a public row, the entry says
`[TODO: ...]` and does not guess.

## The shape of the work

### D-01. Stop changing the driver while the harness runs

- **When.** 24 October 2026.
- **Situation.** Three passes over the driver had changed about a
  hundred things. Each was tested by listening, on the real PC or in an
  emulator, with nothing to compare against. Nobody could say which
  changes worked.
- **Decision.** Development stops. One commit of the fork's line is
  pinned and tested until the harness has finished.
- **Rejected.** Fixing faults as the harness finds them: the thing under
  test would move, and a result on Tuesday's build would say nothing
  about Wednesday's.
- **Cost.** Every fault on these pages has a hypothesis and none has a
  fix.

### D-02. Nothing is judged without a control

- **Decision.** Every test and every game also runs on the same machine
  with no driver. A test that cannot pass there is a broken test. A game
  that fails there says nothing about the driver.
- **Rejected.** Judging a driver run on its own ("it made sound, so it
  works"). The first calibration showed why: most "failures" were the
  same with and without the driver.
- **Cost.** At least twice the recordings.

### D-03. The author's release is tested beside the fork's

- **When.** 0.9.5-a1 from 27 October, 0.9.5-a2 from 2 November.
- **Decision.** The author's source, built unchanged with his own script,
  runs every case and every game the fork's build runs.
- **Why.** It tells a fault of the driver from a fault of the fork, and
  it is what makes a finding of use to anyone else.
- **Rejected.** Testing only the fork: a fault could not be placed.
- **Later.** 0.9.5-a3 is run on selected games only; the sweep's builds
  stay as they were so its three columns stay comparable. The author's
  0.9.3b was added on 10 November to say which line moved
  ([EXPERIMENTS.md](EXPERIMENTS.md#e-15-which-line-moved-the-forks-or-the-authors)).

### D-04. Findings stay in this repository

- **Decision.** No issue, pull request, comment or mention goes to the
  upstream author. A finding is a row with evidence and, where there is
  one, a labelled hypothesis. Never a patch.
- **Why.** The project owner's rule of 20 October 2026, with no exception
  since.
- **Enforced by.** A commit check that refuses a mention or a link to an
  upstream issue.

## The bench

### D-05. 86Box as the emulator, the real PC's chipset

- **Situation.** The first plan named DOSBox-X as the main emulator, with
  Bochs as referee and QEMU as an optional third.
- **Decision.** 86Box, on the same chipset family as the real PC (Intel
  430HX), is the main emulator. DOSBox-X is the referee for a control
  that fails. QEMU is not used.
- **Why.** On 12 October 86Box was the only one of the three that
  reproduced a fault seen on the real PC: UCDDSET's Test froze on IRQ 7,
  which QEMU and DOSBox-X missed.
- **Rejected.** Bochs as referee. It was the fallback: the second emulator
  was to be DOSBox-X if a Linux build of it ran on the bench machine, and
  Bochs built from source otherwise. DOSBox-X ran, so Bochs was never
  built.
- **Cost.** 86Box's Sound Blaster 16 is not the real card (port timing,
  FIFO, version), so timing faults are held for the real PC.

### D-06. The interpreter only, for anything that counts

- **When.** 24 October 2026.
- **Decision.** The emulator's dynamic recompiler is off for every run
  that is recorded as evidence.
- **Why.** What the driver's correctness rests on (changes of privilege
  ring, virtual 8086 mode, single-stepping, the virtual interrupt flag)
  is what a recompiler approximates.
- **Rejected.** The recompiler for speed, with the interpreter for
  disputes only: a run with it on is named a comparison and is never
  evidence.
- **Cost.** Speed, and with it D-08.

### D-07. The real PC's own DOS, not FreeDOS

- **Situation.** The first plan named FreeDOS for the emulated machine
  and MS-DOS only on the real one.
- **Decision.** The bench boots MS-DOS 7.1, the real PC's DOS; since 4
  November its own DOS files, with the drives laid out as the PC's are.
- **Why.** What the bench finds should be what the kit reproduces on the
  PC. Two findings came straight from this: the boot-logo timer hook, and
  the effect of the disk's cluster size.
- **Rejected.** FreeDOS on the bench: a difference between the two DOS
  kernels would sit between every bench result and its hardware check.
- **Cost.** The DOS files are licensed and are never in the repository.

### D-08. An emulated Pentium 133 for the sweep

- **When.** 29 October 2026.
- **Decision.** The sweep's CPU is the highest of MMX 200, MMX 166 and
  Pentium 133 at which ten test games all stay under 2 % filled silence:
  the 133. Every build runs on the same CPU.
- **Rejected.** The real PC's 233 (the emulator falls behind real time,
  17.6 % of the worst game's window filled). A speed chosen per game (a
  result would then depend on the choice).
- **Cost.** The sweep says nothing about a real Pentium 233 under load.

### D-09. One recording at a time

- **When.** 29 October 2026.
- **Decision.** One emulator records at a time, with nothing else running
  on the machine.
- **Rejected.** Four at once, as first planned: two at once multiplied
  the recorder's underruns thirty-fold.
- **Cost.** The sweep took five days.

### D-10. The real PC's disk layout on the bench

- **When.** 4 November 2026.
- **Decision.** The bench's drives match the real PC's, letter for
  letter, with the same 32 KB clusters.
- **Rejected.** The first layout, a generic disk with small clusters: the
  driver's start-up time moved with the cluster size.
- **Cost.** The first five batches of the sweep ran on the old layout;
  anything from them that matters is taken again.

## The measurements

### D-11. A limit is measured from the control, never chosen

- **When.** 27 October 2026, after a chosen pitch tolerance of 1.5 % had
  passed a real 1 % error.
- **Decision.** Every pass limit is set from the control's own spread,
  with the data that set it recorded beside it.
- **Rejected.** Limits by judgment, and tolerances widened inside a test
  until it passes.

### D-12. Compare with the control's recording of the same game

- **Situation.** The first plan was to match a recording against the
  disc's own audio tracks.
- **Decision.** A driver recording is compared with the control's
  recording of the same game: cut into pieces, each piece looked for in
  the control's.
- **Why.** It works for every game, with or without CD audio, and for
  the game's own sound as well as the disc's; and it measures the level
  against what the bare card actually gives. [TODO: Confirm this reason
  against the calibration stage's notes.]
- **Rejected.** Matching against the disc's tracks: it says nothing about
  the 686 games with no CD audio, or about a game's samples.

### D-13. Every sound measure reads the filtered signal

- **When.** 5 November 2026.
- **Decision.** Level, first sound and matching all read the capture
  through a 6.4 Hz high-pass.
- **Rejected.** The raw capture: the emulated card holds a DC level when
  a game stops, which produced a "30 dB quieter" finding and a "4.7 s
  late" one, both withdrawn.
- **Cost.** The calibration and the sweep were judged again.

### D-14. A group is defined by a measurement, not by a list of names

- **Decision.** "The games that differ on the fork's build only" is a
  rule any game can be put to. No family is made by listing its members.
- **Rejected.** Lists. Games named in advance as members of a family
  turned out not to be, once measured.

### D-15. "It runs with sound" is not a pass for a CD-audio game

- **When.** 10 November 2026.
- **Decision.** A game with CD-audio tracks passes only where its sound
  was compared with the control's and is the same. One that runs with
  sound and was not compared is counted apart.
- **Rejected.** *Superseded:* the sweep's first reading, which took
  sound at the right level and time as a pass. Quake read as fine that
  way while its sound was 5 % off speed.

### D-16. `-vcpi` running a game does not make its stop a stated limit

- **When.** 10 November 2026.
- **Decision.** A stop counts as the driver's documented VCPI limit only
  when the program is shown to support nothing but VCPI: by its own
  message, the author's page, or its extender's documentation.
- **Rejected.** *Superseded:* "it runs with `-vcpi`, so it is the stated
  limit". That had filed a game on the author's own list of working
  games as expected to fail.

## The record

### D-17. A correction keeps the old text

- **Decision.** A row or a rule found wrong keeps its old wording beside
  the new, dated. A result is superseded, never deleted. A failed plan is
  taken again only with a written reason.
- **Why.** A reader can see what was believed and when it changed, and a
  second run cannot quietly replace an inconvenient first one.

### D-18. An instrument is trusted only after it has failed on purpose

- **Decision.** Every check, judge and reader is run once against a
  planted fault it must catch, and again after any change to its rules.
- **Rejected.** Trusting a check because it passes.

### D-19. A 32-frame output period for every test build

- **When.** 22 October 2026.
- **Decision.** The harness builds every driver at a 32-frame output
  period; 128 and 256 only as named comparisons.
- **Why.** The lowest added latency the driver allows; the virtual card's
  DMA count closest to the real card's (one sound engine keeps its margin
  at 32 frames and loses most of it at 128); the upstream author's own
  design; and builds at 32 frames had already run on the real PC, with the
  ESS card on 15 October and the Sound Blaster 16 on 16 October. Other
  periods stay open as a measured comparison, possibly by CPU class.

### D-20. The pages: sorted by kind, in one flat folder

- **When.** 10 November 2026.
- **Situation.** The pages had grown one at a time. A visitor met the
  fork's change list before learning what the driver is; there was no
  tutorial, no reference, no map of the parts, and the front page listed
  features the source on its own branch does not have.
- **Decision.** The pages are sorted by what a reader is doing (learn,
  do, look up, understand, plus a lab notebook), listed by kind in
  [README.md](README.md), in one folder. A number is stated on one page.
  A program checks the links, the index, the dates and the candidate
  table at every commit.
- **Rejected.** A folder per kind: the rows and other branches link to
  these pages by path, and every move would have broken them. One long
  page: unreadable on a phone.

## Before the harness

What the fork tried on the driver itself between 5 and 23 October, what
worked and what was reverted, is in [HISTORY.md](HISTORY.md) and, as it
was written at the time, in [../ISSUES.md](../ISSUES.md).
