# How to: one task at a time

Written by Claude. As of 10 November 2026. Each recipe stands alone. All of
them assume the driver is built and installed as in
[QUICKSTART.md](QUICKSTART.md), from the `count-position` line. The
commands are tabled in [REFERENCE.md](REFERENCE.md#commands).

Where a recipe says "measured", the harness measured it in the emulator;
none of it has been confirmed on real hardware yet.

## Mount and unmount an image

```dos
UCDD -mount C:\IMAGES\GAME.CUE
UCDD -mount C:\IMAGES\DATA.ISO -drive G
UCDD -unmount
UCDD -unmount -drive G
```

Without `-drive`, mount uses the first empty μCDD letter and unmount the
first mounted one. Close files on a drive before changing its image. The
driver itself stays loaded until the next boot.

## Have more than one drive letter

Install with a unit count, 1 to 4:

```dos
LH C:\UCDD\UCDD.EXE -install -units 2
```

The count is fixed until the next boot.

## Play a game that comes on several discs

1. Write a text file with the extension `.MDM`, one image path per line
   (up to ten), paths absolute or relative to the file:

   ```text
   DISC1.ISO
   DISC2.CUE
   DISC3.BIN
   ```

2. Mount the list. The first disc is in the drive.

   ```dos
   UCDD -mount C:\IMAGES\GAME.MDM
   ```

3. When the game asks for another disc, press the disc's hotkey
   (Ctrl+Alt+2 for disc 2, or Ctrl+Alt+PgDn for the next one). The keys
   are tabled in [REFERENCE.md](REFERENCE.md#hotkeys).

Every listed image is opened before the mount happens; if one is missing,
the disc already mounted stays. Lists need XMS.

> [!WARNING]
> One five-disc game in the library, Gabriel Knight 2, stops at a disc
> read error under both this fork's build and the author's 0.9.5-a2
> (measured; [CAND-29](FINDINGS.md#cand-29)). The cause is not known.

## Run a program that will not start with the driver loaded

Some programs start, print their DOS extender's banner and return to the
prompt. First try the driver with VCPI left visible:

```dos
LH C:\UCDD\UCDD.EXE -install -vcpi
```

By default the driver hides VCPI so that a protected-mode game uses the
driver's own DPMI host, which keeps the sound traps in place. `-vcpi`
turns that off.

> [!IMPORTANT]
> With `-vcpi`, the sound of a program that uses VCPI goes straight to the
> card and bypasses the driver: the game's sound and the disc's music may
> stop or conflict. It is a way to run the program, not to fix its sound.

Measured on the author's 0.9.5-a2: with `-vcpi`, ten of the twelve Phar
Lap and PMODE/W games in the library run where they did not without it.
On the `count-position` build two of the five PMODE/W games stop, and
both run with `-vcpi`
([EXPERIMENTS.md](EXPERIMENTS.md#e-12-do-the-phar-lap-and-pmodew-games-need-vcpi)).
Only two of them are programs that support nothing but VCPI. For the
rest, the stop without `-vcpi` is a candidate fault of the DPMI host, and
`-vcpi` is a workaround.

## Use an ESS AudioDrive card

1. Run the card's own setup program first, so the card is initialised.
2. Run `UCDDSET` with the driver not installed, and use **Detect**.
3. Choose the physical card it found. The fork's build drives the ESS chip
   in its own extended mode at 44.1 kHz, 16-bit stereo
   ([FEATURES.md](FEATURES.md#ess-audiodrive)).

The ESS path was the reason this fork began, and it was tested on a real
ES1868 before the harness existed. The harness's game sweep ran on the
Sound Blaster 16 only. [TODO: Name the card models the conformance plans
ran (the test matrix offers SB16, SB Pro, SB 2.0 and an ESS model), from
the ledger.]

## Read the driver's interrupt counters

```dos
UCDD -status
UCDD -status -reset
```

`-status` prints the sound interrupt counts since the driver started;
`-reset` starts them from zero. Reset, play for a minute, then read. The
last lines of the output say what healthy counts look like: the game's
handler takes about as many interrupts as the virtual card raises, the
counts under them stay near zero, and few output periods are refilled
late.

## Keep the driver out of a game's way

When no mounted disc has CD audio, and the physical card can be the
virtual one at the same port, IRQ and DMA channels, the driver steps
aside: the game talks to the real card directly. Unmount the image, or
mount a data-only one, and the game runs as without the driver
([FEATURES.md](FEATURES.md)).

## Find out what is known about a game

1. Look for the game's short name in
   [KNOWN-ISSUES.md](KNOWN-ISSUES.md) and
   [FINDINGS.md](FINDINGS.md).
2. For the full record, search
   [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md)
   for the name. A row names the builds it was seen on, the takes that
   show it and how many agreed, the control's result, and its hypothesis
   if it has one.
3. A game with no row either passed, or could not be judged without a
   key press. [REFERENCE.md](REFERENCE.md#bins) explains each verdict.

## Check a claim made on these pages

Every number on a page comes from a row, and every row names the recorded
runs behind it. Follow the page's link to the row in the register. The
recordings and the run ledger are on the bench, which is private (it
holds game files); the row quotes what a reader needs from them. Nothing
on any page is a hardware result unless it says "hardware".
