# μCDD: a fork with fixes, an ESS AudioDrive path, and a test harness that measures it

**Everything in this fork was written by an AI (Claude), directed and tested
by one person.**

This is a fork of [vorvek's μCDD](https://github.com/vorvek/uCDD), a DOS
driver that mounts CD images from a hard disk and plays their CD audio by
becoming a virtual Sound Blaster. All credit for the driver is his. For
what μCDD is and how to use it, read his README and releases; this page is
about what the fork did to it and what it found.

It is a personal project. It began as an attempt to give μCDD a native ESS
AudioDrive path, and grew into a review of the driver and a test harness as
the ESS work kept turning up things that needed measuring. Nothing here has
been submitted upstream. The pages linked below are written for a reader
with no background in the driver; the detail behind every claim is one link
further in.

## Where it stands (10 November 2026)

Development of the driver has been paused since 24 October so that the
thing under test stays still. The harness has since run its unit,
driver and virtual-card tests, calibrated itself on 84 known games, and
swept an 838-game library on three builds: the bare card, the fork's
pinned build, and the author's 0.9.5-a2. It has 32 candidate faults on
record. The sorting of every game into one bin, the candidate reports and
the kit for the real PC are the work in hand. The one-page view is
[docs/STATUS.md](docs/STATUS.md).

## Read next

| Page | What it answers |
|---|---|
| [docs/STATUS.md](docs/STATUS.md) | Where the work is, stage by stage, and what comes next. |
| [docs/KNOWN-ISSUES.md](docs/KNOWN-ISSUES.md) | The table of every candidate fault, and which version of the driver has it. |
| [docs/FINDINGS.md](docs/FINDINGS.md) | Each fault in a paragraph: what the driver does, what it should do, which document says so, and the working hypothesis. |
| [docs/SWEEP.md](docs/SWEEP.md) | The 838-game sweep: how a game is judged and what the three builds showed. |
| [docs/CALIBRATION.md](docs/CALIBRATION.md) | How the harness proved it can tell a working game from a broken one. |
| [docs/METHOD.md](docs/METHOD.md) | How a result is produced and what it is allowed to mean. |
| [docs/BENCH.md](docs/BENCH.md) | The machine the numbers come from, and what it cannot say. |
| [docs/FEATURES.md](docs/FEATURES.md) | What the fork added and fixed in the driver, with how each was tested. |
| [docs/PLANS.md](docs/PLANS.md) | What happens when development resumes, and the ideas after that. |
| [docs/HISTORY.md](docs/HISTORY.md) | How the fork got here. |

The working record behind all of them is
[ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md):
long, in the order it was written, every row a claim with its evidence.

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

The full list of both, with what each was tested on, is
[docs/FEATURES.md](docs/FEATURES.md).

## What the harness found, in one paragraph

Thirty-two candidate faults, each with the document that decides it and the
recorded runs that show it, none yet confirmed on real hardware. Twenty-one
came from the conformance tests: ten are in the fork and in the author's
release alike, nine the author has since fixed and the fork's older line
still has, two the fork introduced, and one is undetermined (one candidate
is split across two of those lists). Eleven came from the game sweep: a
helper program that faults under the fork's DPMI host, a later first
sound, memory that a game sees differently under the driver, a game that
stops for want of memory, CD music and game sound each 6 dB low, a disc
read that fails, and games silent on the fork's build alone. Two whole
groups of games, those built on the Phar Lap and PMODE/W extenders, do not
run under the author's 0.9.5-a2 in the sweep; whether that is the driver's
documented VCPI limit is the next thing measured.

## Branches

| Branch | Holds |
|---|---|
| `main` | The upstream releases, unchanged. |
| `fixes` | This page and the fork's combined line to 20 October 2026, kept for its history. `ISSUES.md`, `BUILDING.md` and `RELEASE-NOTES.md` here describe that line as it was then. |
| `count-position` | The fork's line, the build the harness pins. |
| `merge-a6` | The fork's line with upstream 0.9.4-a6 merged in; built, not run. |
| `feature/disk-irq`, `feature/step-aside`, `feature/fast-dma`, `feature/ess` | The feature branches, each one change on upstream 0.9.4-a6. Disk-irq, step-aside and fast-dma now exist upstream in 0.9.5-a2, in the author's own form; upstream has also dropped Microsoft EMM386, as the fork had. |
| `play-harness` | UCDDPLAY, the CD player: a reference pass against its own specification, a faster FFT and scroller, and `scripts/playcheck`, which runs the player against an earlier build of itself and compares the output. |
| `notes` | The harness's rows: ISSUES.md, the index of fixes, the specifications the fork wrote for itself. |
| `claude/brave-franklin-6h9xzo` | The method package: the commit checks, the ledger, the test matrix, the GitHub workflow. |
| `sound-engine-library`, `reference-library`, `spec-first` | The game-engine census, text copies of the data sheets and specifications, and the design notes. |

Earlier working branches live on as `archive/<name>` tags.

The fork's own history was rewritten on 10 November 2026: commit messages,
file wording and commit dates only, no code. Commit ids from before that
date differ; the upstream releases on `main` keep theirs.

## Licence

GPL-3.0-only, as upstream. The harness's own scripts are under the same
licence. No game files, disc images, boot disks, firmware or recordings
are in this repository, and the commit checks refuse them.
