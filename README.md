# μCDD: a fork with fixes, an ESS AudioDrive path, and a test harness that measures it

**Everything in this fork was written by an AI (Claude), directed and tested
by one person.** 

This is a fork of [vorvek's μCDD](https://github.com/vorvek/uCDD), a DOS
driver that mounts CD images from a hard disk and plays their CD audio by
becoming a virtual Sound Blaster. All credit for the driver is his. For
what μCDD is and how to use it, read his README and releases; this page is
about what the fork did to it and what it found.

This fork began as an attempt to give μCDD a native ESS AudioDrive path, and grew into a review of the driver and a test
harness as the ESS work kept turning up things that needed measuring. 

## What is here, in three parts

**1. Fixes and features** The fork began as an
attempt to give μCDD a native ESS AudioDrive output path and grew into a
review of the whole driver against the hardware documents. Fixes that were found neccessary while testing on a real-hardware system include: disk controller IRQs passed straight to DOS, the
driver stepping aside when it has nothing to add, and the chipset's fast
DMA timing. The fork's own line, with its history, stays on
[`count-position`](https://github.com/TrongDog/uCDD/tree/count-position)
and [`merge-a6`](https://github.com/TrongDog/uCDD/tree/merge-a6); the
feature branches stay as the record of the work. See
[docs/HISTORY.md](docs/HISTORY.md).

**2. A test harness.** Since late October the fork has been running a
harness against a pinned build of its own line and against the author's
releases: unit tests of the parsers and converters, driver conformance
against the MSCDEX interface on synthetic discs, virtual Sound Blaster
conformance against Creative's programming guide and the 8237 and 8259
data sheets, a calibration against the games the author's wiki says work,
and a zero-interaction sweep of an 838-game library. How it works and why
its numbers can be trusted is in [docs/METHOD.md](docs/METHOD.md); the
machine it runs on is in [docs/BENCH.md](docs/BENCH.md).

**3. Findings.** Twenty-one candidate faults so far, each with the line of
the specification it departs from and the run that shows it, sorted into
three lists: present in the author's current code as well, fixed upstream
but still in the fork's line, and introduced by the fork itself. The full table is in
[docs/FINDINGS.md](docs/FINDINGS.md); the calibration result, including
how a known-good game is told from a broken one, is in
[docs/CALIBRATION.md](docs/CALIBRATION.md).

## The findings in one table

Status as of 2 November 2026. "Pin" is the fork's line at the pinned
commit; "a1" is the author's 0.9.5-a1 built unchanged. Every row has a
ten-run plan behind it in the ledger; the IDs link to the row in
[ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md).

| ID | Tier | What the driver does | Pin | a1 | List |
|---|---|---|---|---|---|
| CAND-4 | 1 | After Eject, the device status never reports the door open | fails | fails (refuses the eject while audio is attached) | open upstream |
| CAND-8 | 2 | OCW2 Set Priority is dropped; after a rotating EOI neither pending request is served | fails | fails (narrower) | open upstream |
| CAND-10B | 2 | A full 64 KB 8-bit auto-init buffer is refused | fails | fails | open upstream |
| CAND-11 | 2 | The DMA channel moved at a block end is not followed; the old buffer keeps sounding | fails | fails 3/10 | open upstream |
| CAND-12 | 2 | A 16-bit stereo auto-init block of an odd sample count is refused | fails | fails (block plays, no interrupt after D9h) | open upstream |
| CAND-13 | 2 | Odd-count 16-bit stereo single-cycle blocks swap channels every other block | fails | fails (unsigned refused) | open upstream |
| CAND-15 | 2 | SB Pro stereo: the first data byte after the silent byte goes left; two data sheets say right | fails | fails | open upstream |
| CAND-17 | 2 | After an 8237 master clear and re-setup, the block interrupt comes at once, not after the block's remainder | fails | fails | open upstream |
| CAND-18 | 2 | Direct DAC at 8 kHz plays 1 to 3 % slow under the trap; time is lost in the interrupt handler | fails | further off | open upstream (hardware pending) |
| CAND-20 | 2 | While the channel is masked, the virtual transfer runs on; the count moves and the interrupt arrives early | fails | fails | open upstream |
| CAND-1, -2, -5 | 0, 1 | CUE sheets with INDEX 02, a byte order mark, or only audio tracks are refused | fails | passes | fork lacks the upstream fix |
| CAND-7, -9, -10A, -14, -16, -21 | 2 | Word OUT to the PIC dropped; 8-bit block past a 64 KB page refused; 16-bit buffers over 32 KB refused; 16-bit on the 8-bit channel refused; CD audio stalls with the timer stopped; buffers above 1 MB silent | fails | passes | fork lacks the upstream fix |
| CAND-6 | 1 | CD audio drops out for up to a third of a second during data reads | fails | passes (never had it) | fork regression |
| CAND-19 | 2 | 256-byte single-cycle blocks play 1.9 % low with sidebands while CD audio plays | fails | passes (never had it) | fork regression |
| CAND-3 | 0 | 2.6-bit ADPCM decodes differently from DOSBox-X | fails | undetermined | undetermined |

The calibration (84 games, including every game the author's wiki marks
working that is in the library) found 15 of 54 wiki-confirmed games
matching the bare card under the pinned build and 38 differing, most on
the CD-audio side; Quake plays about 5 % slow. Those are calibration bins,
not final ones: the sweep re-classifies every game with three runs and the
context of the other games that share its sound engine and extender.

## Branches

| Branch | Holds |
|---|---|
| `main` | The author's releases, unchanged (now 0.9.5-a2). |
| `fixes` | This page and the fork's combined line to 20 October 2026, kept for its history. |
| `count-position` | The fork's line, the build the harness pins. |
| `merge-a6` | The fork's line with the author's 0.9.4-a6 merged in; built, not run. |
| `feature/disk-irq`, `feature/step-aside`, `feature/fast-dma`, `feature/ess` | The feature branches, each one change on the author's 0.9.4-a6; the first three now exist upstream in 0.9.5-a2 in the author's own form. |
| `notes` | The harness's rows: ISSUES.md, the candidate reports, the lessons. |
| `claude/brave-franklin-6h9xzo` | The method package: the commit checks, the ledger, the test matrix, the GitHub workflow. |
| `sound-engine-library`, `reference-library`, `spec-first` | The game-engine census, text copies of the data sheets and specifications, and the design notes. |

Earlier working branches live on as `archive/<name>` tags.

## Licence

GPL-3.0-only, as upstream. The harness's own scripts are under the same
licence. No game files, disc images, boot disks, firmware or recordings
are in this repository, and the commit checks refuse them.
