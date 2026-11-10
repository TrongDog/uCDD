# The sweep: 838 games on three builds

Written by Claude from the sweep's records and tables on the bench and the
rows in [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md).
As of 10 November 2026. The sweep is finished; the sorting of every game
into one bin is not, so what follows is what the sweep measured, not yet
a verdict on each game. Everything here is emulator-grade.

## What it is

Every game in an 838-game DOS library is copied to the emulated machine,
launched by its own launcher, and left alone for 90 seconds. Nothing is
pressed. The screen is photographed every two seconds and the sound card's
output is recorded from the launch beep to the end. The same game is run
this way on three builds:

- **the control**: the emulator's own Sound Blaster 16 and CD-ROM drive,
  no μCDD;
- **the pin**: the fork's driver at the pinned commit, the full build
  with audio and the DPMI host;
- **a2**: the author's 0.9.5-a2, built unchanged with his own build
  script.

A fourth, the fork's **CD-only** build (no audio, no DPMI host), is run
on a game that does not pass, to separate the CD-ROM data path from the
rest.

The library: 838 games, 368 of them on a disc image (196 plain ISO, 145
CUE with one BIN, 26 multi-disc lists, 1 unread), 152 with CD-audio
tracks. Four games were left out by ruling, each because it cannot start
on this DOS at all (three launchers call LOADFIX, which the PC's DOS does
not carry; one game fails with DOS's own "Packed file is corrupt" on every
build). The sweep ran from 2 to 7 November in seventeen batches, one
recording at a time, and was closed on 9 November after its candidates'
re-runs were judged.

## How a game is judged

A build is never judged on its own. Each recording under the driver is
compared with the same game's recording on the control.

- **State.** From the screens: running, exited to DOS, crashed (an
  exception or DOS's "Abort, Retry, Fail?" on the screen), rebooted, or
  still and silent to the end of the run. A still, silent screen is
  usually a game waiting for a key; it counts against a build only when
  the control does something else.
- **Sound, by matching.** The driver's recording is cut into pieces and
  each piece is looked for in the control's recording. How much of it is
  found (cover), how well it matches, whether it plays at the same speed,
  and how often it steps back or jumps are each held to a limit set from
  the control's own run-to-run spread in the calibration.
- **Level.** Where the two recordings match, their levels are compared
  on the matched pieces. The expected difference depends on what the
  matched sound is: the disc's music is 6.0 dB down under the driver on
  both builds (CAND-27), so that is allowed for; game samples are expected
  level with the control.
- **Time.** How much later the first matched sound comes than on the
  control. The allowance is set per DOS extender, because the driver's
  DPMI host costs a protected-mode game time at start-up that a real-mode
  game never pays.
- **The signal.** Every measure reads the recording with its DC level
  removed. The emulator's card holds its last output value when a game
  stops playing, which a level meter reads as loud sound; one early
  finding ("30 dB quieter") was that artefact and was withdrawn.

A recording in which the recorder itself ran dry for more than a small
share of the window is thrown out and the game taken again: the
recorder's own log says when it happened, and that silence is the host's,
not the game's. A candidate is confirmed by two more takes and stands only
if two of the three agree.

## What the three builds showed

These are the sweep's families, each defined by a rule and listed in a
table on the bench; a game can be in more than one. The counts are games.

| Family | Games | What it means |
|---|---|---|
| Pin only | 107 | The pin differs from the control where a2 does not: by level in 98 rows, by sound or state in the rest. Faults in the fork's older line, each either a fix the author has made since or something the fork introduced. |
| Game sound 6 dB low on the pin | 67 | CAND-32, most of the pin-only level rows (67 games by the rule in force, the sweep's results/sweep/cand32_ac.csv; the row's first count, 54, was under the rule before 8 November). Seen across the sound engines that play samples (in 5 of 5 DMX games read, 16 of 26 Miles, 15 of 26 HMI SOS); FM, PC-speaker and MIDI music does not pass through that path and reads unchanged. |
| a2 only | 11 | a2 differs from the control where the pin does not. |
| a2 past the control | 6 | a2 runs or plays where neither the control nor the pin does. |
| Control fails | 89 | The control itself exits (66), crashes (16), sits silent where a driver build plays (6) or reboots (2). With no control there is no verdict; these are listed, not judged. |
| Late first sound | 19 pairs of 503 | A game and build whose first sound is later than its extender's allowance, with the sound still inside the window. |

**The cost of the DPMI host at start-up.** Among games that carry no CD
audio, a real-mode game's first sound comes 0.2 to 0.3 s later under
either build than on the control (the medians of 23 and 22 pairs). A
DOS/4GW game's comes 2.3 s later on the pin and 1.6 s on a2 (29 and 27
pairs). Across every DOS/4GW pair in the sweep the pin is 0.86 s slower
than a2 (medians of 2.65 s over 139 pairs and 1.79 s over 146). That gap
between the two builds is named and not yet explained.

**The CD-only build** was run on 52 candidate games, three takes each.
Twenty-nine behave there as on the control, which clears the CD-ROM data
path for them and leaves the audio side or the DPMI host. Four differ
there too (AMOK, FX Fighter, Gabriel Knight 2, SEAL Team), which points at
the data path or at something the two builds share. Eighteen are level
rows, on which a build that never touches the sound card has no verdict,
and one could not be read (no sound to align on).

**The second emulator** (DOSBox-X) is the referee for a control that
fails where a driver build passes: if the control fails there too, the
failure is the game's or the boot's; if not, it is a dispute between the
emulators and goes on the emulator list. Twelve games were put to it. In
five the control's failure appeared there as well. Seven could not be
judged: four because the memory manager finds no EMS page frame on
DOSBox-X and the game says so, three because the referee's own run did
not stand.

**Confirmation.** A candidate from the first take was taken twice more
and stands only where the takes agree. Counted per game and measure, 62
of the 67 differences put to three takes held on the pin, and 22 of 32 on
a2. The ones that did not hold are kept with their counts, not dropped.

## Two groups that fail whole under a2

Read by DOS extender, two groups stand out:

- **Phar Lap, 7 games** (386 Spys, BioForge, Crusader: No Regret,
  Crusader: No Remorse, Transport Tycoon, Transport Tycoon Deluxe, Ultima
  VIII). None runs under either driver build. Under a2 all seven are back
  at the DOS prompt. Under the pin four stop at a memory manager exception
  06, two sit still and one exits. The control runs five of them with
  sound.
- **PMODE/W, 5 games** (Blaster!, Death Rally, Rayman, Rayman Forever,
  S.T.O.R.M.). All five are back at the DOS prompt under a2. Two of them
  run under the pin.

The author's README says that some extenders choose VCPI when it is
there, that the driver hides VCPI while it provides DPMI, and that a
program which supports only VCPI needs the driver installed with `-vcpi`,
at the cost of its sound bypassing the driver. On 7 November his wiki
added BioForge as such a game. So the working reading is that these
twelve are the driver's stated limit rather than twelve faults. That is a
reading, not a result: each game is being taken again with `-vcpi`, and
the answer goes here.

## What the sweep cannot say

- Whether any of it is so on a real card. Emulator timing is not hardware
  timing; a real Pentium with a real Sound Blaster decides.
- What happens after the first 90 seconds, or after a key is pressed.
- Anything about a game whose control fails on this bench.
- Why. The sweep finds that a build differs and by how much; the cause is
  a hypothesis in the fault's row until the driver is read or changed,
  and the driver is not being changed while the harness runs.
