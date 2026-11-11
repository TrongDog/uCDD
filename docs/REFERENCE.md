# Reference

Written by Claude. As of 10 November 2026. Tables to look things up in.
Nothing here explains; for the why, see
[ARCHITECTURE.md](ARCHITECTURE.md) and [METHOD.md](METHOD.md).

Unless a row says otherwise, the driver facts are those of the
`count-position` line, read from its source and its README.

## Commands

From the driver's own help text (`UCDD /?`).

| Command | What it does |
|---|---|
| `UCDD -install [-units n] [-ems] [-vcpi]` | Install the driver. Once per boot, before the CD redirector. |
| `UCDD -mount image [-drive d]` | Put an image in a μCDD drive: the first empty one, or drive `d`. |
| `UCDD -unmount [image] [-drive d]` | Take the image out: of the first mounted drive, or drive `d`. |
| `UCDD -status [-reset]` | Print the sound interrupt counts; `-reset` starts them from 0. |
| `UCDD /?` | Print the help. |
| `UCDDSET` | Open the setup menu. `UCDDSET /?` prints its help. |

| Option | Meaning |
|---|---|
| `-units n` | Number of drives, 1 to 4. |
| `-ems` | Keep the CD audio queue in EMS, not in XMS. |
| `-vcpi` | Keep VCPI visible. The sound of VCPI programs then bypasses the driver. |
| `-drive d` | A μCDD drive letter. |
| `image` | An ISO, CUE, BIN or MDM file. An MDM file lists up to 10 discs. |

`-status`, `-ems` and `-vcpi` exist only in a build made with
`--resident-audio`. `-status` is not in the source on the `fixes` branch.

Messages: `The uCDD driver is installed.`, `The uCDD driver is already
installed.`, `The image is mounted.`, `No uCDD drive is available.`,
`All uCDD drives are in use.`, `No image is mounted on the selected
drive.`

## Build options

`python scripts/build.py [options]`. The full text, with the size limits,
is [../BUILDING.md](../BUILDING.md).

| Option | Effect |
|---|---|
| (none) | A CD-ROM driver only: no audio, no DPMI host. |
| `--resident-audio` | The full driver: CD audio, virtual sound card, DPMI host. |
| `--audio-period-frames N` | Output period of 32, 64, 128 or 256 frames. Default 32. Larger costs less CPU and adds delay. |
| `--no-refill-hint` | Test build: ignore the display retrace hint for deferred CD refills. |
| `--virtual-ess` | Include the virtual ESS AudioDrive (virtual model 4). Left out by default: the Sound Blasters take its room in the segment. The harness's pinned build leaves it out. |
| `--verify-mix` | Test build: check every fast mixer path against the general loop. |
| `--profile-host`, `--profile-driver` | Test builds: cycle and event counters, written to `build/profile`. Need a Pentium. |
| `--no-flat-sink`, `--no-inject-register`, `--no-split-word-io` | Build without one of three fixes, for comparison with 0.9.3. |
| `--disk-irq-direct` | No effect: the disk IRQ handling is always built. Kept so that older build commands still work. |

The build stops when `UCDD.EXE` reaches 65536 bytes or `UCDDHOST.BIN`
65535.

<a id="builds"></a>
## Builds

The builds the harness runs. A commit id is stated here and nowhere else
on these pages.

| Name on the pages | What | Source | Build line |
|---|---|---|---|
| The control (C0) | No μCDD: the emulated Sound Blaster 16 and CD-ROM drive, OAKCDROM and MSCDEX | none | none |
| The pin (C2) | This fork's full driver | `count-position` at `546b389` | `--resident-audio --audio-period-frames 32 --no-refill-hint` |
| The CD-only build (C1) | This fork's driver with no audio and no DPMI host | the same commit | no options |
| a1 | The author's 0.9.5-a1, unchanged | `main` at `c5531c8` | `--resident-audio --audio-period-frames 32` |
| a2 | The author's 0.9.5-a2, unchanged | `main` at `245759c` | the same |
| a3 | The author's 0.9.5-a3, unchanged | `main` at `6c2f3e3` | the same |
| The base | The author's 0.9.3b, the release this fork started from | `main` at `90ad361` | the same |

Each build is made twice and must give the same files; the hashes of the
files a run used are in the run's record. Builds compare byte for byte
only when made with the same NASM.

The pin is 238 commits past 0.9.3b. The author's line is 47 commits past
it at 0.9.5-a3.

## Settings

`UCDDSET` writes `UCDD.CFG` beside the programs (38 bytes at the pin, file
version 4) and sets `BLASTER` for the virtual card at install, keeping
other `BLASTER` fields such as `P330`. If the file is missing or from an
older version, the menu opens at install.

| Setting | Values at the pin |
|---|---|
| Virtual Sound Blaster port | 220h, 240h, 260h, 280h |
| Virtual Sound Blaster IRQ | 5, 7 |
| Low DMA channel | 1, 3 |
| High DMA channel | 5, 6, 7 |
| Virtual WSS codec port | 530h, 604h, E80h, F40h |
| Virtual WSS codec IRQ | 7, 9, 10, 11 |
| Mixer levels (CD, game, master) | 0 to 100 |

The harness's standard is a virtual SB16 at `A220 I5 D1 H5`, the real PC's
own setting.

<a id="hotkeys"></a>
## Hotkeys

Defaults, from the README on `count-position`. The keys still reach the
game.

| Action | Keys |
|---|---|
| Select disc 1 to 10 | Ctrl+Alt+1 to Ctrl+Alt+0 (or F1 to F10) |
| Next, previous disc | Ctrl+Alt+PgDn, Ctrl+Alt+PgUp |
| Eject | Ctrl+Alt+E |
| CD audio volume up, down | Ctrl+Alt+Keypad +, Ctrl+Alt+Keypad - |

## Images

From the README on `count-position`.

| Format | Accepted |
|---|---|
| `.ISO` | 2048-byte data sectors. |
| `.CUE` with `.BIN` | One BINARY file, tracks in order, INDEX 01 on each track. INDEX 00 and PREGAP accepted. Data track MODE1/2048, MODE1/2352, or MODE2/2352 with Form 1 sectors. |
| `.BIN` alone | MODE1/2352 data, no audio. |
| `.MDM` | A list of up to ten images, one path a line. |

Names are DOS 8.3, on a local hard disk, under 2 GiB. `FLAGS PRE` applies
CD de-emphasis; `DCP`, `4CH` and `SCMS` are accepted. Not supported: other
MODE2 forms, compressed audio, a CUE sheet with more than one file.

<a id="bins"></a>
## Bins: the verdict a game gets on each build

One bin per game per build, the first that applies.
[METHOD.md](METHOD.md) has the order and the reasons.

| Bin | Meaning |
|---|---|
| `PASS` | The build behaves as the control does. For a game with CD-audio tracks: its sound was also compared with the control's, piece by piece, and is the same. |
| `RUNS_WITH_SOUND` | A game with CD-audio tracks that runs with sound at the control's level and time, but whose sound could not be read: not compared, or no control pair to read it against. Neither a pass nor a fault. |
| `NO_AUDIO_IN_WINDOW` | Silent on the control for the 90 seconds, and in the same state under the build. Cannot be judged without pressing a key. |
| `NO_CONTROL` | The control itself does not run. Nothing is said about the driver. |
| `GAME_FAULT` | The control and the build stop the same way with the same message. |
| `EXPECTED_VCPI` | The program supports only VCPI, shown by its own message, the author's page or its extender's documentation, and it runs with `-vcpi`. The driver's documented limit. |
| `EXPECTED_IMAGE` | The disc image is of a kind the driver says it does not support. |
| `CANDIDATE_UCDD_HOST` | Runs on the control; stops, hangs or crashes under the build. A protected-mode game. |
| `CANDIDATE_UCDD_CDROM` | A disc game that also fails on the CD-only build. |
| `CANDIDATE_UCDD_AUDIO` | Runs; the disc's music is missing or differs from the control's. |
| `CANDIDATE_UCDD_SFX` | Runs; the game's own sound is missing or differs. |
| `CANDIDATE_UCDD_LEVEL` | Runs; the sound is the same sound at a different level than expected. |
| `CANDIDATE_UCDD_HOSTLOAD` | Runs; its first sound comes later than the allowance for its DOS extender. |
| `FLAKY_...` | The same, seen on fewer than two takes of three. Kept with its counts. |
| `HARNESS_ERROR` | The take failed on the bench's side. Never final: it is taken again. |
| `UNCLASSIFIED` | Not enough evidence, with a written blocker. |

## Labels: which line moved

For a fault only one of the two drivers has. Set by running the base
(0.9.3b) on the same game.

| Label | Meaning |
|---|---|
| `LACKS-FIX` | Only the pin fails, and the base fails the same way: the author fixed it after 0.9.3b. |
| `FORK-REGRESSION` | Only the pin fails, and the base passes: the fork introduced it. |
| `UPSTREAM-REGRESSION` | Only the author's build fails, and the base passes: his line changed after 0.9.3b. |
| `FORK-FIX` | Only the author's build fails, and the base fails the same way: a change of the fork's made the pin pass. |
| `UNKNOWN` | The base reads as neither, or has not been run. |

## Glossary

| Term | Meaning |
|---|---|
| The bench | The emulated PC and its tools, on a private machine. [BENCH.md](BENCH.md). |
| Take | One recorded run of one game on one build: 90 seconds from launch, a screenshot every two seconds, the sound captured. |
| Plan | A saved list of takes, run as one. Its id (eight hex digits) is quoted in the rows. |
| Ledger | The append-only record of every take, with the hashes of what it used and produced. |
| Row | One entry in the register, [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md): a claim with its evidence. |
| Candidate | A fault found in an emulator, not yet confirmed on real hardware. Numbered `CAND-n`. |
| Cell | The games that share a sound engine and a DOS extender. |
| Family | Candidates that share builds, bin and symptom, across cells. |
| Grade | How well a row is supported: one take, or three that agree. |
| Wave | The reading of whether a build's sound is the control's sound: same, differs, or not read. A difference counts only where the game's own control, taken twice, repeats itself. |
| DOS extender | The layer a protected-mode DOS game runs on (DOS/4GW, PMODE/W, Phar Lap and others). |
| VCPI, DPMI | Two interfaces a DOS extender can use to reach protected mode. The driver hides the first and serves the second itself. |
| CD audio (Red Book) | The disc's own audio tracks, as a CD player plays them. |
