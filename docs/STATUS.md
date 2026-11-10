# Status: where the work stands

Written by Claude. As of 10 November 2026. One page, updated at every
stage: what is done, what each stage proved, what is in hand and what
comes after. The evidence for every line is in the pages it links to and,
behind them, in [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md).

## In one paragraph

The fork's driver development stopped on 24 October 2026 and has not
resumed. Since then the fork has built a test harness around one pinned
build of its own driver and the author's releases built unchanged, and has
run it stage by stage, each stage closed only when its acceptance lines
were met with recorded runs. The harness does not change the driver: a
fault it finds becomes a row with evidence, never a patch. Seven stages
are closed. The eighth, sorting every game into one bin and writing a
report per fault, is in hand.

## The stages

| Stage | What it is | State | What it proved |
|---|---|---|---|
| Environment | The emulator, the guest, the recorder, the ledger, the commit checks | Closed 25 October | A run can be reproduced from its record, and a recording says whether a silence is the guest's or the recorder's. |
| Unit tests (Tier 0) | The driver's own parsers and converters, assembled unchanged and fed known inputs | Closed 25 October | CAND-1 to CAND-3. |
| Driver conformance (Tier 1) | The CD-ROM driver through the MSCDEX interface on synthetic discs | Closed 25 October | CAND-4 to CAND-6. |
| Virtual card conformance (Tier 2) | The virtual Sound Blaster, DMA controller and interrupt controller, from real mode and three kinds of protected-mode client | Closed 28 October | CAND-7 to CAND-21, and a list of cases only a real card can judge. |
| Catalogue | 838 games: launch command, disc image audit, sound engine and DOS extender of each, and the engine by extender matrix | Closed 29 October | Which games share a runtime, so a fault is counted by family and not by game. |
| Calibration | 84 known games, three runs each on the bare card and the pinned build | Closed 2 November; judged again on 5 and 6 November | The harness confirms working games and separates match from mismatch. [CALIBRATION.md](CALIBRATION.md) |
| Sweep | All 838 games, left alone for 90 seconds, on the bare card, the pinned build and the author's 0.9.5-a2 | Closed 9 November | CAND-22 to CAND-32 (the first met during the calibration) and the families in [SWEEP.md](SWEEP.md). |
| Triage, reports, hardware kit | One bin per game per build; one report per fault or per family; a kit for the real PC | In hand | |

Beside these runs a second track: the method itself (the commit checks,
the ledger, the rules a result must obey) is versioned on its own branch
and tightened whenever the work shows a hole in it. On 10 November the
fork's own history was rewritten once: commit messages, file wording and
commit dates only, no code.

## In hand

1. **Three things before the sorting**, done on 10 November, because
   each could move a whole group of games. The author's compatibility
   wiki was read again at its current state: its tables are unchanged, so
   no game's entry moved, and a new page lists one game without CD audio,
   BioForge, installed with `-vcpi`. One plan of 72 takes, all recorded:
   - the games on the Phar Lap and PMODE/W extenders, taken again with the
     driver installed with `-vcpi`, the author's documented remedy for
     programs that need VCPI. Six of the seven Phar Lap games run with it
     on both the pinned build and 0.9.5-a2, and four of the five PMODE/W
     games on 0.9.5-a2: for those, the stop without it is the driver's
     stated limit, not a fault. `ULTIMA8` and `BLASTER!` still stop.
   - the author's 0.9.5-a3 (7 November), which changes one thing, the
     DPMI host's free-memory answer, on 40 games: the protected-mode games
     whose state under 0.9.5-a2 is not the control's, the memory finding's
     four games, and a passing game from each protected-mode group that
     has one (ten groups of 26). These takes were made without `-vcpi`.
   - a new control take for the 13 of those games first swept on the
     bench's earlier setup.
2. **The sorting**, first table on 10 November. Every game has one bin
   per build, in a fixed order of questions, read against the other games
   that share its sound engine and extender. A title with CD-audio tracks
   passes only where its sound was matched piece by piece against the
   control and found the same; one that runs with sound at the control's
   level and time, but whose sound was not matched, is counted apart as
   "runs with sound", neither a pass nor a fault. On the pinned build 205
   games pass and 32 run with sound; on 0.9.5-a2, 291 and 60. 317 and 314
   are silent in the control's first 90 seconds, a game waiting for a key,
   which a run without interaction cannot judge.
3. **The reports.** One per fault, or one per group of games where the
   whole group fails the same way, largest first.
4. **The label on the fork-only faults.** A fault the pinned build has and
   the author's release does not is one of two things: a fix the author
   made after the fork's base (0.9.3b; his line is 47 commits past it at
   0.9.5-a3),
   or something the fork's 238 commits introduced. The label is placed by
   measurement where a run on the base is cheap.
5. **The kit for the real PC**: the conformance cases a real card must
   judge, and a short list of games, one passing and one failing from each
   group, ranked by how many games the group holds.

## After that

Development resumes: first the fork's line is brought up to the author's
current release, then the faults are fixed in order of how many games each
reaches. [PLANS.md](PLANS.md) has the list.

## What has not been done

- Nothing has been confirmed on real hardware. Every candidate is
  emulator-grade until the kit has been run by a person on the real PC.
- No game has been played. The sweep launches a game and leaves it alone
  for 90 seconds; a game that waits for a key is judged on whether it
  waited rather than crashed.
- The author's 0.9.5-a3 has not been run.
- A second emulator has re-run a dozen disputed games and nothing more;
  everything else rests on one emulator.
