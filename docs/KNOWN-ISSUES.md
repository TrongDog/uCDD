# Known issues

A plain list of every fault the test harness has found in the driver, and
whether each is in this fork, in the upstream project, or both. Written by
Claude from the rows in [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md), which hold the
evidence. Status as of 2 November 2026.

**How to read it.** Each row is one fault, reproduced ten runs out of ten
in an emulator. None has yet been confirmed on real hardware; that is what
the hardware kit is for.

- **Fault**: what the driver does wrong, in one line.
- **In this fork**: whether the fault is present in this fork's driver at
  the commit the harness tests.
- **In upstream**: whether the same case shows the fault in the upstream
  project's most recent release the harness has run (0.9.5-a1 at the
  moment; the version is stated here once and updated when a newer
  release has been through the same runs). "Fixed" means the case passes
  there; "Never present" means upstream never had it.
- **More**: a link to the fault's entry in [FINDINGS.md](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md), which says
  which test found it, what the driver should do, which document or data
  sheet says so, and where in ISSUES.md the recorded runs, the citation
  and the hypothesis live.

## In this fork and in upstream

The driver has these faults in both. They are properties of the driver's
design rather than of the fork's changes.

| Fault | In this fork | In upstream | More |
|---|---|---|---|
| After Eject, the device status never reports the door open | Present | Present; the eject itself is refused while CD audio is attached | [CAND-4](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-4) |
| OCW2 Set Priority is dropped; after a rotating EOI neither pending request is served | Present | Present; Set Priority passes, the rotating EOI is still lost | [CAND-8](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-8) |
| A full 64 KB 8-bit auto-init buffer is refused | Present | Present | [CAND-10B](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-10b) |
| A DMA channel moved at a block end is not followed; the old buffer keeps sounding | Present | Present in 3 runs of 10 | [CAND-11](https://github.com/TrongDog/uCDD/blob/fixes/docs/FINDINGS.md#cand-11) |
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
keep real time for a spinning game on the test host; a Phar Lap extender
refusing V86 mode, which is the driver's documented VCPI limitation.
