# μCDD: a fork with fixes, an ESS AudioDrive path, and a test harness that measures it

**Everything in this fork was written by an AI (Claude), directed and tested
by one person.**

This is a fork of [vorvek's μCDD](https://github.com/vorvek/uCDD), a DOS
driver that mounts CD images from a hard disk and plays their CD audio by
becoming a virtual Sound Blaster. All credit for the driver is his. For
what μCDD is and how to use it, read his README and releases; this page is
about what the fork did to it and what it found.

This fork began as an attempt to give μCDD a native ESS AudioDrive path,
and grew into a review of the driver and a test harness as the ESS work
kept turning up things that needed measuring. The pages linked below are
written for a reader with no background in the driver; the detail behind
every claim is one link further in.

## Features

- **Native ESS AudioDrive output**: 44.1 kHz 16-bit stereo through the
  chip's extended mode, the ES1868 and ES1878 clock trimmed to an exact
  44.1 kHz, and the chip correctly identified so the trim runs.
- **A virtual ESS AudioDrive** for games set to an ESS, built from the
  ESS data sheets: the ESS command set, 16-bit data on the 8-bit channel,
  demand-mode DMA, ESS ADPCM and ESPCM.
- **PCI disk controller IRQs passed straight to DOS**, so DOS/4GW games no
  longer freeze on a controller on IRQ 10 or 11; the installer finds the
  controllers through the PCI BIOS and UCDDSET shows them.
- **The driver steps aside** while no mounted disc has CD audio and the
  physical card can be the virtual one, so a game runs exactly as without
  it.
- **Fast DMA**: the chipset's Type F timing on the output channel (PIIX,
  82378, ALi, OPTi, VIA, AMD-756, SiS), which gives back most of the memory
  bus the CD stream takes.
- **Interrupt counters** and `UCDD -status`, so a sound fault can be
  described in numbers.
- **UCDDSET redone**: a Disk row, Options and Detected columns, switches
  that explain themselves when greyed.

The full list, with what each one was tested on, is in
[docs/FEATURES.md](docs/FEATURES.md).

## Fixes

- The virtual Sound Blaster (SB16, SB Pro, SB 2.0) read against Creative's
  programming documents and the real card, with dozens of command, timing
  and status corrections; the virtual SB16 now answers as a DSP 4.13.
- Single-cycle playback no longer loses its first milliseconds; very short
  blocks and over-long blocks are accepted.
- The DMA count and the block interrupt come from one position, the card's
  fetch point, and the polled count follows the output clock as a real
  counter does.
- A 512-frame output ring, so a late period interrupt no longer throws the
  clock back.
- The DPMI host: no memory corruption after exit with a protected-mode
  pointer to MSCDEX; INT 1Ch/23h/24h handlers of protected-mode programs
  delivered; clean termination at any nesting depth.
- Discs with non-standard root directory headers mount; the CUE parser in
  a far buffer; mixed-mode images.
- Two memory holes closed; CD audio at 2 to 3 % of a Pentium 233 after the
  performance pass.

Every fix has its row, its evidence and its hardware status in
[ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md),
and the readable summary is in [docs/FEATURES.md](docs/FEATURES.md).

## What the harness found

Since late October the fork has been running a test harness against a
pinned build: unit tests of the parsers and converters, driver conformance
on synthetic discs, virtual Sound Blaster conformance against Creative's
guide and the 8237 and 8259 data sheets, a calibration against games known
to work, and a zero-interaction sweep of an 838-game library. It has found
twenty-one candidate faults so far, each with the line of the
specification it departs from and the recorded run that shows it.

- [docs/KNOWN-ISSUES.md](docs/KNOWN-ISSUES.md): the table of every
  candidate fault, and which version of the driver has it.
- [docs/FINDINGS.md](docs/FINDINGS.md): each fault in a paragraph, with the
  document that decides it.
- [docs/CALIBRATION.md](docs/CALIBRATION.md): how a working game is told
  from a broken one, and the result on 84 known games.
- [docs/METHOD.md](docs/METHOD.md): how a result is produced and what it is
  allowed to mean.
- [docs/BENCH.md](docs/BENCH.md): the machine the numbers come from.

## Plans

Development of the driver is paused while the harness runs, so that the
thing under test stays still. When it resumes:

- Fix the faults the harness found, ranked by how many games each one
  reaches.
- Bisect and fix the two faults the fork's own work introduced (CD-audio
  dropouts during disc reads; 256-byte single-cycle blocks playing flat).
- The virtual ESS's compatibility-mode stereo channel order, per the ES1868
  data sheet.
- The virtual SB16's time-constant table measured from a real card.
- A DPMI host that absorbs a client's HLT instead of faulting it, if the
  sweep finds a game that needs it.
- The ESS half-rate mode, which needs a mixer change first.
- A hardware kit for a real Pentium MMX 233 with a Sound Blaster 16 CT2291 or
  an ESS ES1868F, so every candidate can be confirmed by a human ear.

The history of how it got here is in [docs/HISTORY.md](docs/HISTORY.md).

## Branches

| Branch | Holds |
|---|---|
| `main` | The upstream releases, unchanged. |
| `fixes` | This page and the fork's combined line to 20 October 2026, kept for its history. |
| `count-position` | The fork's line, the build the harness pins. |
| `merge-a6` | The fork's line with upstream 0.9.4-a6 merged in; built, not run. |
| `feature/disk-irq`, `feature/step-aside`, `feature/fast-dma`, `feature/ess` | The feature branches, each one change on upstream 0.9.4-a6. |
| `play-harness` | UCDDPLAY, the CD player: a reference pass against its own specification, a faster FFT and scroller, and `scripts/playcheck`, which runs the player against an earlier build of itself and compares the output. |
| `notes` | The harness's rows: ISSUES.md, the candidate reports, the lessons. |
| `claude/brave-franklin-6h9xzo` | The method package: the commit checks, the ledger, the test matrix, the GitHub workflow. |
| `sound-engine-library`, `reference-library`, `spec-first` | The game-engine census, text copies of the data sheets and specifications, and the design notes. |

Earlier working branches live on as `archive/<name>` tags.

## Licence

GPL-3.0-only, as upstream. The harness's own scripts are under the same
licence. No game files, disc images, boot disks, firmware or recordings
are in this repository, and the commit checks refuse them.
