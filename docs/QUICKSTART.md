# Quickstart: build the driver and hear a CD game

Written by Claude. As of 11 November 2026. A tutorial: follow it top to
bottom once. Its install and mount lines are the pinned build's own, read
from the harness's runs; the steps were not run as one sequence. It takes about fifteen minutes plus the time to copy files to
the DOS machine.

At the end you will have built this fork's driver, installed it under DOS,
mounted a copy of a game CD from the hard disk, and heard the disc's music
through the sound card.

> [!WARNING]
> This fork is a test bed. Its driver has known faults
> ([KNOWN-ISSUES.md](KNOWN-ISSUES.md)), and none of the harness's results
> has been confirmed on real hardware. To play games, the
> [author's release](https://github.com/vorvek/uCDD) is the maintained
> driver, and its README is the manual.

## What you need

| | |
|---|---|
| A computer to build on | Python 3 and [NASM](https://www.nasm.us) (the bench uses NASM 2.16.03). Nothing is downloaded during the build. |
| A DOS machine, real or emulated | A 386 or later (a Pentium for smooth CD audio), DOS 5 or later. |
| A memory manager | [JemmEx](https://github.com/Baron-von-Riedesel/Jemm) 5.86 or 5.87. HIMEM alone is not enough: the driver needs XMS, VCPI and a way to trap I/O ports. |
| A CD redirector | [SHSUCDX](http://adoxa.altervista.org/shsucdx/) or MSCDEX. It gives the drive its letter. |
| A sound card | A Sound Blaster (1.5/2.0, Pro or 16), a Windows Sound System codec, or an ESS AudioDrive. **Set the card up first**, with its jumpers or its own setup program. The driver does not configure it. |
| A disc image | An `.ISO`, or a `.CUE` with one `.BIN`, with a DOS 8.3 file name, on a local hard disk, smaller than 2 GB. |

## 1. Build

```console
git clone https://github.com/TrongDog/uCDD.git
cd uCDD
git checkout count-position
python scripts/build.py --resident-audio --audio-period-frames 32 --no-refill-hint
```

The build prints the size of each program. You now have, in `build/`:

| File | What it is |
|---|---|
| `UCDD.EXE` | The driver. It carries the DPMI host (`UCDDHOST.BIN`) inside it. |
| `UCDDSET.EXE` | The setup program. |
| `UCDDPLAY.EXE` | A CD player for the mounted disc. Not needed here. |

`count-position` is the line the harness tests. The exact commit and the
other builds are in [REFERENCE.md](REFERENCE.md#builds); every option of
the build is in [../BUILDING.md](../BUILDING.md).

## 2. Copy to the DOS machine

Copy `UCDD.EXE` and `UCDDSET.EXE` into one directory, for example
`C:\UCDD`. Copy your disc image to the hard disk, for example
`C:\IMAGES\GAME.CUE` and `C:\IMAGES\GAME.BIN`.

## 3. Load the memory manager

In `CONFIG.SYS`:

```dos
DOS=HIGH,UMB
DEVICE=C:\JEMMEX\JEMMEX.EXE
```

## 4. Set up the cards

Boot, and before the driver is installed run:

```dos
C:\UCDD\UCDDSET
```

Set **Physical** to the card in the machine (Detect reads it from the
hardware) and **Virtual** to the card the game should see. Save. The
settings go to `UCDD.CFG` beside the programs.

## 5. Install the driver, then the redirector

In `AUTOEXEC.BAT`, after the mouse driver if you load one:

```dos
LH C:\UCDD\UCDD.EXE -install
C:\DOS\SHSUCDX.COM /D:UCDD0001 /L:F
```

Reboot. You should see:

```text
The uCDD driver is installed.
```

The driver is installed once per boot, before the redirector. `F` is the
letter the CD drive will have.

## 6. Mount the image

```dos
C:\UCDD\UCDD -mount C:\IMAGES\GAME.CUE
```

You should see:

```text
The image is mounted.
Drive F:
```

`DIR F:` now lists the disc's files.

## 7. Play

Start the game as you would with the disc in a drive. Set the game's
sound to the card you chose as **Virtual** in step 4. When the game asks
for a CD track, the disc's music plays through the sound card together
with the game's own sound.

To check the driver's side of it, run this after a minute of play:

```dos
C:\UCDD\UCDD -status
```

It prints the sound interrupt counts and, under them, what healthy counts
look like. [TODO: Confirm the lines `UCDD -status` prints from a run of
the pinned build; the sentence above is read from the source.]

## If it did not work

[TROUBLESHOOTING.md](TROUBLESHOOTING.md) lists the common stops: a game
that exits at once, no sound, quiet music, a setup menu that opens at
every boot.

## Where next

- One task at a time: [HOWTO.md](HOWTO.md).
- Every command and option: [REFERENCE.md](REFERENCE.md).
- How the driver does it: [ARCHITECTURE.md](ARCHITECTURE.md).
