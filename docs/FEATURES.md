# Features and fixes

Written by Claude. What the fork added to the driver and what it fixed,
grouped by the part of the driver it touches, with how each was tested.
The record behind each line is the "Changes", "Performance" and "Fixed
after the reviews" sections of
[ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md)
and the commit messages on `count-position`. "Hardware" means tested on
the real PC (Pentium MMX 233, 430HX, ESS ES1868 or Sound Blaster 16
CT2291, MS-DOS 7.1); "emulator" means 86Box, DOSBox-X or QEMU only.

Everything on this page was done before 24 October 2026, when development
paused for the harness. The harness has since found faults in some of it:
the fork's line lacks nine fixes the author has made, lacks his doubling
of game samples while no disc plays, and carries at least two faults of
its own ([KNOWN-ISSUES.md](KNOWN-ISSUES.md)). "Emulator" on this page is
the testing of the time, before the harness's rules; where the harness
has since measured the same thing, its row is the better evidence.

## ESS AudioDrive

- Native ESS output: 44.1 kHz 16-bit stereo through the chip's extended
  mode, with an optional half-rate mode. Hardware (ES1868); the half-rate
  alignment fix on top is emulator only.
- ES1868 and ES1878 clock trimmed to an exact 44.1 kHz, and the ESS
  identified correctly so the trim runs: before the identification fix,
  every ESS ran untrimmed with every CD frame interpolated. Hardware.
- The WSS and ESS stop routine put the old IRQ handler back on the wrong
  vector; fixed. Emulator.
- A virtual ESS AudioDrive for games set to an ESS on an ESS card, rebuilt
  from the ESS data sheets in its own module: the ESS command set and
  extension registers, 16-bit data over the 8-bit channel, demand-mode
  DMA, ADPCM at 4, 2.6 and 2 bits, ESPCM accepted as silence with its
  interrupt so a game no longer waits forever, the polled DMA count one
  output period behind the mix (Descent 2's crackle), the Miles ESS
  digital driver's interrupt pattern, B1h/B2h reporting the virtual IRQ
  and DMA. Emulator.

## The virtual Sound Blaster

- SB16, SB Pro and SB 2.0 read against Creative's two programming
  documents and the DSP firmware's command tables; the virtual SB16 answers
  as a DSP 4.13, matching the real CT2291 (upstream answers 4.05, the
  version of the firmware that has been disassembled; the fork answers as
  the card in the PC does, and the two differ in a few replies and rates a
  program can see). Dozens of command-parsing,
  timing and status corrections. Emulator, with the CT2291's answers as the
  reference.
- Single-cycle playback: four fixes, including a new sound no longer
  losing its first milliseconds at large output periods, and very short
  blocks accepted (King's Quest V's driver test). Emulator.
- A block longer than the DMA buffer accepted (Descent 2's HMI ESS
  driver). Emulator.
- The DMA count and the block interrupt from one position, the card's
  fetch point; an auto-init transfer's polled count follows the output
  clock as a real counter does, never past the mix. Emulator.
- A 16-bit word OUT to the PIC handled as two bytes. Emulator.
- The physical SB16's MPU-401 interrupts on the card's own line. Emulator.
- A 512-frame output ring, so a late period interrupt no longer throws the
  clock back. Emulator.
- Interrupt counters in the release build and `UCDD -status [-reset]`:
  raised, taken, ended by the game's EOI, and the rest. Emulator.
- The "IRQ 7 wash": Doom's effects turning to noise with the physical and
  virtual card on the same IRQ; fixed. Emulator (0 washed runs of 15).

## The CD-ROM driver and images

- Discs with non-standard root directory headers mount (Hexen, Duke Nukem
  3D Atomic). Hardware.
- The CUE parser in a far buffer, 111 sheets tested, and mixed-mode images
  mounted, read and played. Emulator.
- CD audio refills keep running at a 256-frame output period. Hardware.
- A refill budget so a 386 no longer stalls a tenth of a second at a time.
  Emulator (386, 486 and Pentium templates).

## The DPMI host

- No memory corruption after exit when a game passes a protected-mode
  pointer to MSCDEX. Hardware.
- INT 1Ch/23h/24h handlers of protected-mode programs delivered; DOS-side
  termination (INT 23h and 24h, at depth 0 and from a child under a
  parent) leaves the vector table, DOS memory and VCPI pages as found.
  Emulator.
- More interrupt-flag patterns recognised, with a larger table of learned
  sites. Hardware, benefit partly confirmed.
- A data-flow pass over every entry point and join label after the IRQ 7
  stack fault. Emulator.
- The host's services read against DPMI 0.9 and 1.0, VCPI, MSCDEX 2.1 and
  the data sheets, with the fixes listed in ISSUES.md. Emulator.

## The machine

- PCI disk controller IRQs passed straight to their DOS handlers, so
  DOS/4GW games no longer freeze on a controller on IRQ 10 or 11; `UCDD
  -install` finds the controllers through the PCI BIOS; UCDDSET shows them
  in a Disk row and takes one by hand. Emulator.
- The driver steps aside while no mounted disc has CD audio and the
  physical card can be the virtual one: no output stream, no port traps,
  no DPMI host. Emulator.
- Fast DMA: the chipset's Type F timing on the output channel (Intel PIIX
  family, 82378 and EISA, ALi, OPTi, VIA and AMD-756, SiS), behind a
  UCDDSET switch, set at every output start and restored at every stop.
  Emulator.
- Two memory holes closed (3 KB conventional and one in upper memory); the
  virtual ESS's DAC ring moved to upper memory when room exists. Emulator.
- Performance pass, measured first: port traps answered in protected mode,
  the mixer chains as single loops. CD audio costs 2 to 3 % of a Pentium
  233; Doom runs 19 % slower and Quake 14 %, of which the driver's own
  work is about 6 points and the rest is the output stream's ISA DMA on
  the memory bus. Hardware.
- EMM386 dropped; JEMMEX only.

## UCDDSET

- The main screen redone: Options and Detected columns, a Disk row, tick
  boxes that grey themselves with a help line saying why, the step-aside
  and fast-DMA switches.
- A review of the setup program's own faults: the SB Pro priming timeout
  counted loop turns (now each turn reads a port); `pro_stop`.

## Beyond the driver

- A sound-engine census of the game library, so a fault seen in one game
  is tested across every game sharing its engine: "fix by family, not by
  game".
- A reference library of the data sheets and specifications the work
  follows, as text, with a key for each so that every row can name the
  document that decides it.
- UCDDPLAY, the CD player, read against its own specification with every
  citation checked, its FFT and scroller made faster with the output
  checked unchanged, and a check harness (`scripts/playcheck`) that runs it
  against an earlier build of itself. Emulator. Branch `play-harness`.
- The test harness: unit tests, driver conformance, virtual-card
  conformance, a catalogue of the 838-game library by sound engine and
  DOS extender, calibration, the library sweep on three builds, and a
  hardware kit; with its ledger, commit checks and GitHub workflow. See
  [METHOD.md](METHOD.md) and [STATUS.md](STATUS.md).

## Planned

Development is paused while the harness runs. What happens when it
resumes, in order, and the ideas for after that, are in
[PLANS.md](PLANS.md).
