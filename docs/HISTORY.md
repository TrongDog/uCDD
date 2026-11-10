# History: how the fork got here

Written by Claude. The detailed record is the "Changes", "Performance" and
"Fixed after the reviews" sections of [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md)
and the commit messages on `count-position`; this is the shape of it.

## It started with an ESS card

This is a personal project, and it began with one card. The real PC had an
ESS ES1868, an SB Pro-compatible chip with a 16-bit
mode of its own that μCDD's SB Pro path did not use. The first work was a
native ESS output path: 44.1 kHz 16-bit stereo through the chip's extended
mode, the ES1868's and ES1878's clock trimmed to an exact 44.1 kHz, and a
fix for the vector the WSS stop routine put back on the wrong interrupt.
Testing it on the PC with a large game library found other things, and
the fork grew.

## Three passes over the driver

**Reviews.** Five independent readings of the driver (the port trap and
card emulation, the mixer and CD streaming, the host's interrupt path, the
DPMI services), then the code read section by section against the
documents in the reference library: Creative's two Sound Blaster
programming documents and the DSP firmware's own command tables, the 8237
and 8259 data sheets, the ESS data sheets, DPMI 0.9 and 1.0, VCPI, MSCDEX.
The fixes from those passes are listed in ISSUES.md: DOS re-entry from the
disc hotkeys, Ctrl+Break during CD reads, DSP command parsing, the
emulated controllers, the DPMI host's handling of program exits, callbacks
and faults, the INT 1Ch/23h/24h handlers of protected-mode programs.

**Measurement.** CD audio costs 2 to 3 % of the CPU on the Pentium 233.
Doom runs 19 % slower under the driver and Quake 14 %, of which the
driver's own work is about 6 points; the rest is the output stream's ISA
DMA taking the memory bus, which any card streaming at that rate costs on
this chipset. That measurement is why the fast-DMA feature exists: the
PIIX's Type F timing on the output channel gives most of the bus back.

**Features.** PCI disk controller IRQs passed straight to their DOS
handlers so a DOS/4GW game no longer freezes on a controller on IRQ 10 or
11 (`UCDD -install` finds the controllers through the PCI BIOS; UCDDSET
shows them). The driver stepping aside, with no output stream, no port
traps and no DPMI host, while no mounted disc has CD audio and the physical
card can be the virtual one, so a game runs exactly as without the driver.
Interrupt counters and `UCDD -status`. A virtual ESS AudioDrive, built from
the ESS data sheets, for games set to an ESS on an ESS card. A sound-engine
census of the library, so a fault seen in one game is tested across every
game that shares its engine ("fix by family, not by game").

## Where it went

The ESS work turned up faults that were not the ESS's: in the virtual
card, in the DPMI host, in the CD-ROM path, in the machine around them.
Each was fixed where it lived, and by the time the review passes were
done the fork was a general one. The parts that are most its own are the
virtual ESS, the sound-engine census, the reference library, and the
harness; the rest is a long list of corrections, each with its evidence in
ISSUES.md.

## The freeze

On 24 October the fork's development stopped and the harness began. The
reason is in [METHOD.md](METHOD.md): a driver that keeps changing cannot
be measured, and the fork had no way to say, with evidence a stranger
could re-run, which of its changes worked. The pinned commit is the fork's
line at that moment.

## The harness, 24 October to now

The harness was built and run in stages, each closed only when its
acceptance lines were met with recorded runs.

**Conformance (25 to 28 October).** Unit tests of the driver's parsers and
converters, the CD-ROM driver through the MSCDEX interface on synthetic
discs, and the virtual Sound Blaster driven by test programs from real
mode and from three kinds of protected-mode client. Twenty-one candidate
faults, each with the document that decides it. Run again on the author's
release, they sorted three ways: in both, fixed upstream, and the fork's
own.

**The lessons of the first week** were mostly about the bench. A week of
apparent dropouts was MS-DOS's boot-logo timer hook. A set of "stalls"
was the recorder running dry on the host. An emulator at 233 MHz could
not keep real time, so the sweep runs at 133. Each became a rule with a
planted fault that proves the check can fail.

**Calibration (28 October to 2 November).** Eighty-four games the author
and others had already reported working, to prove the harness can confirm
a working game before it is trusted on 838. The first attempt measured
the bench (no PATH, no mouse driver, the library on the wrong drive) and
was run again on the real PC's boot.

**The sweep (2 to 7 November, closed 9 November).** Every game in the
library on the control, the pin and the author's 0.9.5-a2. Along the way
the bench's disks were rebuilt to the real PC's layout, a "30 dB quieter"
finding turned out to be the emulated card's held DC level and every
sound measure was moved to the filtered signal, and the recorder learned
to keep each sound source apart. Eleven more candidates and the families
in [SWEEP.md](SWEEP.md).

**The method.** Beside the runs, the rules themselves were tightened
again and again, each time because the work had shown a hole: a result claimed
without its artefact, a list where a rule was needed, a check that had
never been seen to fail. The method lives on its own branch with its own
tests.

## The rewrite of 10 November

The fork's own commits were rewritten once, on 10 November 2026: commit
messages, file wording and commit dates only. No code changed: the pinned
build and the feature branches are the same code under new commit ids.
The upstream author's commits on `main` were not touched. Commit ids from before that date differ.

## What comes next

The sorting of the sweep, the reports and the kit for the real PC
([STATUS.md](STATUS.md)); then development resumes, first by bringing the
fork's line up to the author's current release ([PLANS.md](PLANS.md)).
