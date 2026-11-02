# Calibration: can the harness tell a working game from a broken one?

Written by Claude from the calibration report and ledger of 28 October to
2 November 2026. The numbers here are the bench's (86Box 6.0, dynamic
recompiler off, emulated Pentium 133, MS-DOS 7.1 booted as the real PC
boots); none were taken on real hardware.

## Why a calibration

Before the harness is let loose on 838 games, it has to prove it can
confirm the games already known to work. The author's wiki lists games he
and others have tested; if the harness cannot show those producing the
same sound under μCDD as on the bare card, the harness is wrong, not the
games. The charter put it bluntly: a harness that cannot confirm Quake is
a broken harness, and the sweep does not start.

## The selection

84 games: every game the wiki marks as working that is in the library (54
with measurable sound within the 90-second window, 48 silent without a
keypress), one game standing for each populated cell of the sound-engine
by extender matrix (so the thresholds are set across every runtime
combination, not one engine's timing), the games the bench already held
sound references for, and Quake. Each ran three times on the bare card
(C0) and three under μCDD (C2); the games not passing on C2 ran three more
on the CD-only build (C1). 504 recordings in the main plan, 160 in the C1
plan, every one in the ledger with the boot it ran on and the hashes of the
four boot programs.

## What had to be fixed first

The first calibration measured the bench, not the driver. Quake died on
the first line of its launcher under both C0 and C2, and most of the
"failures" were identical on both sides: no PATH, no PROMPT, no mouse
driver, no VESA driver, none of the helper programs the library's
launchers call, and the library on the wrong drive letter. The sweep now
boots as the real PC boots, with the same shell settings, CuteMouse,
S3VBE20, SetMul and the launcher helpers, and each record carries every
boot line. Then Quake played on both sides.

Three things the recordings also found, each now a rule with a planted
fault proving it: the emulated 233 MHz CPU could not keep real time for a
spinning game on this host (the sweep runs at an emulated Pentium 133,
where the worst game's filled silence is 0.5 % of the window against 17.6 %
at 233); the screen watchdog misread three ways a game stops (a message
without a newline before the prompt, the cursor's two blink phases, DOS's
"Abort, Retry, Fail?"); and the CD-only build turned out to play no CD
audio at all (it refuses the command), so a C1 failure on sound alone says
nothing about the CD-ROM data path. Twenty-three games that had been
binned as CD-ROM faults on that evidence were re-sorted.

## How a game is judged

The C2 recording of a game is compared with its own C0 recording from the
launch beep onward: is sound present, when does it start, how many gaps,
does it match the reference and how much of it is covered, is it playing
at the same speed, how often does it step back or jump. The limits are not
chosen; they sit just outside the bare card's own run-to-run spread over
the 54 known-good games:

| Measure | Limit | Where it came from |
|---|---|---|
| match | at least 0.95 | the bare card's own floor across 108 pairs was 0.96 |
| cover | at least 0.85 | floor 0.86 |
| speed | within 2 % | the bare card was exactly 1.00 in every pair |
| gaps, steps back, jumps | the game's own C0 maximum plus 1, 15, 25 | the 95th percentile of C0 run-to-run differences |
| first audio | within 3 s of C0's median | C0 spread 0.8 s; μCDD mounts the disc about 1.7 s after the beep |
| runs to pass | 2 of 3 | |

A game passes if two of its three C2 runs pass. The screen watchdog adds
run state: running, hung (screen and sound unchanged 20 s), crashed (an
exception on screen), exited to DOS. A recording with more than 2 % of its
window filled by the recorder, or outside 2 % of its expected length, is a
harness error and is retaken.

## The result

Of the 54 wiki-confirmed games with sound: 15 match the bare card under
the pinned build; 38 differ (32 on the CD-audio side, 4 in the
protected-mode host, 2 in game sound); 1 has no working control on this
bench (Johnny Bazookatone: the emulated CD-ROM refuses a data read while a
CD track plays). Of the 84: 17 pass, 51 differ in a way that points at μCDD, and the rest
are the games' own faults, games that stay silent until a key is pressed,
or a handful with a written reason.

Quake: boots, launches, plays its demo and records sound on every run. On
the bare card it repeats itself (match 0.96, speed 1.00). Under μCDD's
audio build it plays about 5 % slow on all three runs; under the CD-only
build it matches the bare card exactly. The slowness is on the audio side,
and Quake is the only game of the 54 whose speed is off by more than 2 %.

These are calibration bins. They show the instrument can separate match
from mismatch on known-good games, which is what the gate existed to
prove. The sweep classifies every game again, with three runs, the author's
current release as a second build, and the context of the other games in
its matrix cell, before anything is ranked for a report.

## What it cost

The first calibration ran on the bench's own boot and measured the bench,
not the driver; it was kept as a baseline and the calibration was run
again on the PC's boot. That is the price of finding out the bench was
wrong before the sweep rather than after it.
