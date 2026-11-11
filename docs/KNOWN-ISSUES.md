# Known issues

A plain list of every fault the test harness has found in the driver, and
whether each is in this fork, in the upstream project, or both. Written by
Claude from the rows in [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md), which hold the
evidence. Status as of 11 November 2026.

**How to read it.** Each row is one fault, reproduced in an emulator: ten
runs out of ten for the conformance tests; for the game sweep, two takes
of three or better up to CAND-32, and from CAND-33 each row says how many
takes it rests on. None has yet been confirmed on real hardware; that is
what the hardware kit is for.

- **Fault**: what the driver does wrong, in one line.
- **In this fork**: whether the fault is present in this fork's driver at
  the commit the harness tests.
- **In upstream**: whether the same case shows the fault in the upstream
  project's most recent release the harness has run in full. That is
  0.9.5-a2. The author released 0.9.5-a3 on 7 November 2026 (two commits
  past a2: a margin in the DPMI host's free-memory answer, and the version
  number); it has been run on 40 selected games, and where a row below
  differs on a3 the row says so.
  "Fixed" means the case passes there; "Never present" means upstream
  never had it.
- **More**: a link to the fault's entry in [FINDINGS.md](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md), which says
  which test found it, what the driver should do, which document or data
  sheet says so, and what the working hypothesis is where there is one.

The first four tables are the conformance tests' findings (the driver
driven by test programs). The fifth is the game sweep's.

## In this fork and in upstream

The driver has these faults in both. They are properties of the driver's
design rather than of the fork's changes.

| Fault | In this fork | In upstream | More |
|---|---|---|---|
| After Eject, the device status never reports the door open | Present | Present; the eject itself is refused while CD audio is attached | [CAND-4](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-4) |
| OCW2 Set Priority is dropped; after a rotating EOI neither pending request is served | Present | Present; Set Priority passes, the rotating EOI is still lost | [CAND-8](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-8) |
| A full 64 KB 8-bit auto-init buffer is refused | Present | Present | [CAND-10B](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-10b) |
| A DMA channel moved at a block end is not followed; the old buffer keeps sounding | Present | Present in 2 runs of 10 | [CAND-11](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-11) |
| A 16-bit stereo auto-init block of an odd sample count is refused | Present | Present; the block plays but no interrupt follows the exit command | [CAND-12](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-12) |
| Odd-count 16-bit stereo single-cycle blocks swap channels every other block | Present | Present; the unsigned case is refused outright | [CAND-13](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-13) |
| SB Pro stereo: the first data byte after the silent byte goes left; two data sheets say right | Present | Present | [CAND-15](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-15) |
| After an 8237 master clear and re-setup, the block interrupt comes at once, not after the block's remainder | Present | Present | [CAND-17](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-17) |
| Direct DAC at 8 kHz plays 1 to 3 % slow under the port trap | Present | Present, further off; the real PC decides whether the platform shares it | [CAND-18](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-18) |
| While the DMA channel is masked, the virtual transfer runs on and the interrupt arrives early | Present | Present | [CAND-20](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-20) |

## In this fork only, fixed in upstream

The fork's driver has these; upstream has since fixed them. They are the
fork's backlog: the plan is to bring the fixes in when development resumes.

| Fault | In this fork | In upstream | More |
|---|---|---|---|
| A CUE sheet with INDEX 02 or higher is refused | Present | Fixed | [CAND-1](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| A CUE sheet with a UTF-8 byte order mark is refused | Present | Fixed | [CAND-2](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| An audio-only CUE sheet is refused, alone or in an MDM list | Present | Fixed | [CAND-5](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| A 16-bit OUT to port 20h is dropped whole, so the 21h mask byte never lands | Present | Fixed | [CAND-7](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| An 8-bit block past the end of its 64 KB DMA page is refused | Present | Fixed | [CAND-9](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| A 16-bit auto-init buffer over 32 KB is refused | Present | Fixed | [CAND-10A](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| Mixer register 81h is ignored; 16-bit samples cannot use the 8-bit channel | Present | Fixed | [CAND-14](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| CD audio stalls for 307 ms when a real-mode game stops the timer | Present | Fixed | [CAND-16](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |
| An auto-init transfer from a buffer above 1 MB gives no sound | Present | Fixed | [CAND-21](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#fixed-upstream) |

## In this fork only, introduced by the fork

The fork's own work created these; upstream never had them. To be found and
fixed by bisecting the fork's commits when development resumes.

| Fault | In this fork | In upstream | More |
|---|---|---|---|
| CD audio drops out for up to a third of a second during disc reads under play | Present | Never present | [CAND-6](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#introduced-by-the-fork) |
| 256-byte 8-bit single-cycle blocks play 1.9 % low with sidebands while CD audio plays | Present | Never present | [CAND-19](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#introduced-by-the-fork) |

## Undetermined

| Fault | In this fork | In upstream | More |
|---|---|---|---|
| 2.6-bit ADPCM decodes differently from DOSBox-X | Present | Not testable without changing its source; the real card decides | [CAND-3](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#undetermined) |

## Found by the game sweep

Found by running 838 games on the control, this fork and upstream's
0.9.5-a2. These are measured differences from a machine with no driver,
not all of them faults: two are the driver working as designed and are
listed so that nobody is surprised by them.

| What | In this fork | In upstream | More |
|---|---|---|---|
| A launcher helper (SETMUL) stops with a protection fault under the DPMI host; 81 launchers call it | Present | Not present | [CAND-22](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-22) |
| A CD-audio game's first sound comes later than without the driver | Present, a median 1.3 s | Present, a median 0.9 s | [CAND-23, CAND-24](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-23) |
| A program sees about twice the memory under the driver; a few games fail on one side only | Present | Present | [CAND-25](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-25) |
| I Have No Mouth and I Must Scream stops with a memory message | Present | Present in a2; fixed in a3 (the game runs there, one take) | [CAND-26](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-26) |
| The disc's music is 6.0 dB quieter than through the card's own CD input (headroom, by design) | Present | Present | [CAND-27](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-27) |
| "Packed file is corrupt" under the driver only | A class with no member yet | A class with no member yet | [CAND-28](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-28) |
| Gabriel Knight 2 (a five-disc set) stops at a disc read error | Present | Present | [CAND-29](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-29) |
| Ultimate Domain plays no sound | Present | Not present | [CAND-30](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-30) |
| Gabriel Knight 1 falls silent at its menu | Present | Not present | [CAND-31](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-31) |
| Game samples are 6.0 dB quieter than on the bare card; 67 games | Present | Fixed (the author doubles them while no disc plays) | [CAND-32](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-32) |

## Filed by the sorting, 10 November 2026, and grouped into families

The sorting gave every game one verdict per build and filed a row for each candidate that had none: **CAND-33 to CAND-169**, 137 rows, in the register ([ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md)), each with its builds, its takes and its control. On 11 November every candidate was given a family by rule: the builds it shows on, its verdict and the measure that differs first, and its symptom (a level's sign and size class; which limits of the matched sound failed; a stop's state and last message). One line per family of two games or more; a candidate in no such family stands as its own row. The rule, the size classes and the split test are on the bench's families page; each family is a row of the register (FAM-n), and each member's row points to it.

| Family | Games | Fault | Builds | Rows |
|---|---|---|---|---|
| FAM-1 | 81 | LEVEL level, under the control, class 2 of 3 (-8.31 to -3.92 dB) | pin only | CAND-32, CAND-34, CAND-45, CAND-48, CAND-50, CAND-64, CAND-87, CAND-88, CAND-90, CAND-91, CAND-92, CAND-103, CAND-107, CAND-125, CAND-141, CAND-154, CAND-155, CAND-156, CAND-159 |
| FAM-2 | 21 | LEVEL level, under the control, class 3 of 3 (-3.71 to -0.57 dB) | pin only | CAND-34, CAND-46, CAND-47, CAND-49, CAND-52, CAND-54, CAND-55, CAND-57, CAND-89, CAND-93, CAND-94, CAND-108, CAND-113, CAND-115, CAND-134, CAND-149, CAND-150, CAND-151, CAND-167, CAND-168 |
| FAM-3 | 10 | HOST state, EXITED; last message: C:\> | a2 only | CAND-33, CAND-35, CAND-37, CAND-164 |
| FAM-4 | 7 | LEVEL level, under the control, class 3 of 3 (-3.71 to -0.57 dB) | a2 only | CAND-45, CAND-83, CAND-84, CAND-90, CAND-120, CAND-125, CAND-155 |
| FAM-5 | 6 | AUDIO wave, gaps | both | CAND-38, CAND-39, CAND-66, CAND-72 |
| FAM-6 | 6 | HOST state, HANG; last message: none read | pin only | CAND-31, CAND-33, CAND-35, CAND-124, CAND-131 |
| FAM-7 | 6 | HOSTLOAD time, late | pin only | CAND-23, CAND-78 |
| FAM-8 | 5 | AUDIO wave, gaps | a2 only | CAND-68, CAND-70, CAND-152, CAND-165 |
| FAM-9 | 5 | AUDIO wave, gaps | pin only | CAND-140, CAND-147 |
| FAM-10 | 5 | SFX sound, silent where the control sounds | pin only | CAND-62, CAND-110, CAND-116, CAND-142, CAND-143 |
| FAM-11 | 4 | LEVEL level, over the control, class 2 of 3 (4.70 to 9.16 dB) | a2 only | CAND-49, CAND-56, CAND-144, CAND-151 |
| FAM-12 | 4 | HOST state, HANG; last message: none read | both | CAND-76, CAND-77, CAND-133, CAND-163 |
| FAM-13 | 4 | LEVEL level, under the control, class 2 of 3 (-8.31 to -3.92 dB) | both | CAND-51, CAND-80, CAND-85, CAND-158 |
| FAM-14 | 4 | SFX state, HANG; last message: none read | pin only | CAND-60, CAND-111, CAND-117, CAND-121 |
| FAM-15 | 3 | AUDIO wave, cover | a2 only | CAND-98, CAND-100, CAND-129 |
| FAM-16 | 3 | AUDIO wave, steps back and jumps | a2 only | CAND-67, CAND-157 |
| FAM-17 | 3 | HOSTLOAD time, late | a2 only | CAND-24, CAND-79 |
| FAM-18 | 3 | LEVEL level, over the control, class 3 of 3 (11.85 to 13.87 dB) | a2 only | CAND-53, CAND-54, CAND-55 |
| FAM-19 | 3 | SFX state, EXITED; last message: C:\> | both | CAND-25, CAND-109, CAND-127 |
| FAM-20 | 2 | AUDIO state, EXITED; last message: C:\> | a2 only | CAND-40, CAND-41 |
| FAM-21 | 2 | LEVEL level, over the control, class 1 of 3 (0.08 to 2.99 dB) | a2 only | CAND-105, CAND-113 |
| FAM-22 | 2 | SFX sound, silent where the control sounds | a2 only | CAND-59, CAND-126 |
| FAM-23 | 2 | FLAKY_AUDIO wave, gaps | a2 only | CAND-42 |
| FAM-24 | 2 | FLAKY_HOSTLOAD time, late | a2 only | CAND-24, CAND-122 |
| FAM-25 | 2 | AUDIO state, HANG; last message: none read | both | CAND-148, CAND-153 |
| FAM-26 | 2 | AUDIO wave, cover | both | CAND-96, CAND-101 |
| FAM-27 | 2 | AUDIO wave, steps back and jumps | both | CAND-43, CAND-106 |
| FAM-28 | 2 | HOSTLOAD time, late | both | CAND-23, CAND-24 |
| FAM-29 | 2 | LEVEL level, under the control, class 3 of 3 (-3.71 to -0.57 dB) | both | CAND-86, CAND-136 |
| FAM-30 | 2 | AUDIO sound, silent where the control sounds | pin only | CAND-99, CAND-128 |
| FAM-31 | 2 | AUDIO wave, cover | pin only | CAND-97, CAND-146 |
| FAM-32 | 2 | AUDIO wave, gaps, steps back and jumps | pin only | CAND-68, CAND-157 |
| FAM-33 | 2 | AUDIO wave, speed fast | pin only | CAND-73, CAND-139 |
| FAM-34 | 2 | AUDIO wave, steps back and jumps | pin only | - |
| FAM-35 | 2 | LEVEL level, over the control, class 1 of 3 (0.08 to 2.99 dB) | pin only | CAND-53, CAND-81 |
| FAM-36 | 2 | SFX wave, steps back and jumps | pin only | CAND-104, CAND-160 |

## Stated limits of the driver, seen in the sweep

Not faults. The author's README says a program that supports only VCPI
needs `UCDD -install -vcpi` and loses its sound through the driver. Two
of the library's games are identified as such programs and run with
`-vcpi`: 386 Spys (its own message refuses virtual 8086 mode under
another program) and BioForge (named on the author's wiki). The other
Phar Lap and PMODE/W games that stop under upstream's a2 are not in this
list: eight run with `-vcpi` without being identified as needing only
VCPI, and two still stop with it. They are host candidates, the five
PMODE/W games one candidate for their group, since the README says
PMODE/W takes the driver's DPMI host when VCPI is hidden.

## Held for hardware

Cases whose judge is the real card and which the hardware kit carries: the
8237 page wrap on an 8-bit block; the 8259's special mask mode, which the
emulator does not have; the DSP's time-constant table, measured in full by
a self-timing program on the card; odd-count 16-bit stereo and the 48 kHz
16-bit stereo case; the DAC and timer-stop cases at 8 kHz; the mixer 81h
write. CAND-15's next-transfer question needs an SB Pro 2.

## Not driver faults

Found by the harness and recorded so that they are not mistaken for the
driver's: MS-DOS 7.1's boot-logo timer hook holding interrupts off for up
to 8 ms every two ticks (`Logo=0` stops it); MS-DOS 7.1 rewriting the BIOS
tick count on a date call; an interpreting emulator at 233 MHz unable to
keep real time for a spinning game on the test host; the emulated sound
card holding a DC level when a game stops, which reads as loud sound until
it is filtered out; 89 games that do not run on the emulated machine even
with no driver loaded. [FINDINGS.md](FINDINGS.md) has the full list.
