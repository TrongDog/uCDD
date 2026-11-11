# Troubleshooting

Written by Claude. As of 10 November 2026. Two parts. The first is for
someone using the driver: a symptom, its cause, what to do. The second is
for someone building a test bench like this one: things that looked like
driver faults and were not.

Each entry says how it is known. "Measured" means the harness saw it in
the emulator; "documented" means the upstream README says so; "untested"
means the remedy is a hypothesis. Nothing here has been confirmed on real
hardware by the harness.

## Part 1. Using the driver

| Symptom | Go to |
|---|---|
| The setup menu opens at every boot | [1](#1-the-setup-menu-opens-at-every-boot) |
| A game prints a banner and drops back to the prompt | [2](#2-a-game-prints-its-extenders-banner-and-returns-to-the-prompt) |
| "EMS driver is not VCPI compliant." | [3](#3-ems-driver-is-not-vcpi-compliant) |
| A game stops with a message about memory | [4](#4-a-game-stops-with-a-message-about-memory) |
| The disc's music is quieter than the game's sound used to be | [5](#5-the-discs-music-is-quiet) |
| Voices and effects are quiet, music is fine | [6](#6-voices-and-effects-are-quiet-on-this-forks-build) |
| The first sound comes a second or two late | [7](#7-the-first-sound-comes-late) |
| Short dropouts under MS-DOS 7.1 | [8](#8-short-dropouts-under-ms-dos-71) |
| No sound at all, or the card is not found | [9](#9-no-sound-or-the-card-is-not-found) |
| A DOS/4GW game freezes at its banner | [10](#10-a-dos4gw-game-freezes-at-its-banner) |
| "Packed file is corrupt" | [11](#11-packed-file-is-corrupt) |
| A multi-disc game stops at a read error | [12](#12-a-multi-disc-game-stops-at-a-disc-read-error) |

### 1. The setup menu opens at every boot

**Cause.** `UCDD.CFG` is missing beside `UCDD.EXE`, or was written by an
older version. `UCDD -install` runs `UCDDSET`, which opens its menu when
the file needs attention.
**Do.** Run `UCDDSET` once, check the cards, save.
**Known by.** Documented.

### 2. A game prints its extender's banner and returns to the prompt

**Cause.** With the audio driver installed, VCPI is hidden and a
protected-mode game runs on the driver's own DPMI host. Some programs
cannot run that way, and for some the host itself fails.
**Do.** Install with `-vcpi` ([HOWTO.md](HOWTO.md#run-a-program-that-will-not-start-with-the-driver-loaded)).

> [!IMPORTANT]
> With `-vcpi` the program's sound bypasses the driver. The program runs;
> its sound and the disc's music may stop or conflict.

**Known by.** Measured on the author's 0.9.5-a2: ten of the library's
twelve Phar Lap and PMODE/W games run with `-vcpi` and not without it. Two
still stop with it (Ultima VIII, Blaster!). Rows: CAND-33 and the rows it
names.

### 3. "EMS driver is not VCPI compliant."

**Cause.** The same hidden VCPI, seen by a game that checks for it.
Wing Commander Armada prints this and stops under both this fork's build
and the author's 0.9.5-a2; it runs with no driver.
**Do.** Try `-vcpi`. Untested for this game.
**Known by.** Measured (the stop); the remedy is untested.
Row: [CAND-25](FINDINGS.md#cand-25).

### 4. A game stops with a message about memory

**Cause.** Under the driver a protected-mode program is given its memory
by the driver's DPMI host, and sees about twice what it sees without the
driver. A game that sizes its caches from that answer can then fail to
allocate the rest. I Have No Mouth and I Must Scream stops this way on
this fork's build ("Can't allocate enough memory for scene cache.") and
on the author's 0.9.5-a2.
**Do.** Use the author's 0.9.5-a3 or later: its release note names the
game, and the game runs on it.
**Known by.** Measured (one take on a3).
Row: [CAND-26](FINDINGS.md#cand-26).

### 5. The disc's music is quiet

**Cause.** Read from the code: the mixer's unity gain halves each sample,
and its own comment says that is so a sum needs no clipping. The row
holds that as the cause in a labelled hypothesis. Disc music is 6.0 dB
under what the card's own CD input gives, with every mixer level at its
top, on every build.
**Do.** Turn the amplifier up. There is no setting that removes it.
**Known by.** Measured, the same in six games.
Row: [CAND-27](FINDINGS.md#cand-27).

### 6. Voices and effects are quiet on this fork's build

**Cause.** This fork's build plays a game's own samples 6 dB low all the
time. The author's releases since 24 October double them again while no
disc is playing; the fork's line is older than that change.
**Do.** Use the author's release. On this fork there is no setting.
**Known by.** Measured in 67 games, and read in both source trees.
Row: [CAND-32](FINDINGS.md#cand-32).

### 7. The first sound comes late

**Cause.** Two things add up. A protected-mode game starts later under
the driver's DPMI host: about 2 s for a DOS/4GW game, 0.2 to 0.3 s for a
real-mode one. And a CD-audio game's music starts about a second later,
because the image is read through DOS.
**Do.** Nothing; it is a start-up cost, not a stall. On a disk with small
clusters it is longer.
**Known by.** Measured. Rows: [CAND-23](FINDINGS.md#cand-23), and the
start-up cost in [SWEEP.md](SWEEP.md).

### 8. Short dropouts under MS-DOS 7.1

**Cause.** Not the driver. MS-DOS 7.1 (the DOS that comes with Windows
98) keeps a boot-logo routine on the timer that holds faster timer interrupts
off for up to 8 ms every other tick. Any game that speeds the timer up
loses ticks.
**Do.** In `MSDOS.SYS`, under `[Options]`, set `Logo=0`.
**Known by.** Measured in the emulator, with and without the driver; not
yet seen or measured on the real PC, which runs the same DOS. Row: IOSYS08.

### 9. No sound, or the card is not found

**Cause.** The driver does not configure the physical card.
**Do.** Set the card up first, with its jumpers or its own program (a
Plug and Play card, and an ESS card, need theirs run at every boot).
Then run `UCDDSET` with the audio driver **not** installed: Detect and
Test both need the bare card.
**Known by.** Documented.

### 10. A DOS/4GW game freezes at its banner

**Cause.** A PCI disk controller on IRQ 10 or 11 holds its request until
its real-mode handler runs; a protected-mode game waiting on that disk
freezes.
**Do.** This fork's driver passes the controller's IRQ straight to DOS.
`UCDD -install` finds PCI controllers itself; for one it does not find,
set the IRQ by hand in the Disk row of `UCDDSET`
([../BUILDING.md](../BUILDING.md), "Disk controller IRQs").
**Known by.** The fork's own testing before the harness
([FEATURES.md](FEATURES.md)).

### 11. "Packed file is corrupt"

**Cause.** DOS's message for a packed program whose unpacker fails.
*Hypothesis:* the program was loaded below 64 KB with DOS loaded high.
**Do.** Start the program through `LOADFIX`. Untested here: the one game
that prints the message in this library prints it with no driver too.
**Known by.** Untested. Row: [CAND-28](FINDINGS.md#cand-28).

### 12. A multi-disc game stops at a disc read error

**Cause.** Not known. Gabriel Knight 2, a five-disc set mounted as a
list, stops with DOS's "General failure reading drive" 1.4 s after
launch on both builds, and on the CD-only build too.
**Do.** No workaround is known.
**Known by.** Measured. Row: [CAND-29](FINDINGS.md#cand-29).

## Part 2. Building a bench: faults that were not the driver's

Each of these was taken for a driver fault at first, some for days.

> [!WARNING]
> When a result surprises, suspect the instrument first and look at the
> screenshots. Every item below was found that way.

| What it looked like | What it was | What settled it |
|---|---|---|
| Dropouts in every tone test | The DOS boot logo holding the timer (entry 8 above) | The same dropouts with no driver |
| Disc music 30 dB too quiet; a first sound 4.7 s late | The emulated card's DAC holds its last value when a game stops, and a meter reads that as sound | A 6.4 Hz high-pass on every measure |
| Stalls in the middle of a capture | The recorder running dry on the host | A log of every buffer and underrun on the host's clock; only a confirmed underrun counts as the recorder's |
| Games stuttering at the real PC's speed | The emulator, with its recompiler off, cannot keep real time at 233 MHz | The sweep at an emulated Pentium 133 |
| Underruns everywhere | Two emulators recording at once | One recording at a time |
| Almost every known-good game "failing" | The bench's boot: no PATH, no mouse driver, the library on the wrong drive | The real PC's boot, line for line |
| A CD-audio game's music starting later on some runs | The disk's cluster size | The real PC's disk layout on the bench |
| "CD-ROM faults" in 23 games | The CD-only build refuses the play command: it plays no CD audio at all | A failure on sound alone on that build is not read |
| Games "crashing" that had exited cleanly | The screen watchdog misreading a message with no line break, the cursor's blink, and "Abort, Retry, Fail?" | Three fixes, each with a planted case |
| 81 games failing the same way on the fork's build | One launcher helper faulting before the game starts | Counted once, as its own row ([CAND-22](FINDINGS.md#cand-22)) |
| A control that fails where the driver passes | Sometimes the emulator: its own CD-ROM drive misreads a CUE sheet with 2048-byte sectors | A second emulator as referee |
| Four games unjudged on the second emulator | It has no EMS page frame under this memory manager | Recorded; those four stay unjudged |
| Tick counts wrong after a program starts | MS-DOS 7.1 resets the BIOS tick count on a date call | Tests no longer time across a program start |

The rows for each are in the register under the names IOSYS08, ACSIG,
86FILL, TIER3CPU, PARALLEL, SWEEPWD, 86CUE2048, DBXCTRL and DOSDATE. The
experiments behind several are in [EXPERIMENTS.md](EXPERIMENTS.md).
