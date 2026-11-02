# History: what the fork did before the harness, and where it went

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
line at that moment. Development resumes when the harness has finished:
first by bringing the fork's line up to date, then by bisecting the two
faults the fork introduced, then with whatever the sweep says is worth
doing.
