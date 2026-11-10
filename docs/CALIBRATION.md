# Calibration: can the harness tell a working game from a broken one?

Written by Claude from the calibration report and ledger of 28 October to
2 November 2026 and the re-judging of 5 and 6 November. As of 10 November
2026. The numbers here are the bench's (86Box 6.0, dynamic recompiler off,
emulated Pentium 133, MS-DOS 7.1 booted as the real PC boots); none were
taken on real hardware.

## Why a calibration

Before the harness is let loose on 838 games, it has to prove it can
confirm the games already known to work. The author's wiki lists games he
and others have tested; if the harness cannot show those producing the
same sound under μCDD as on the bare card, the harness is wrong, not the
games. The charter put it bluntly: a harness that cannot confirm Quake is
a broken harness, and the sweep does not start.

## The selection

84 games. First, the known-good set: the games the wiki marks as working
that are in the library and make measurable sound within the 90-second
window without a keypress, 54 of them (48 more wiki games stay silent
until a key is pressed and cannot be judged this way). Second, one game
standing for each populated cell of the sound-engine by extender matrix,
so the limits are set across every runtime combination and not on one
engine's timing. And Quake. The lists overlap, which is why they come to
84. Each game ran three times on the bare card (C0) and three under the
fork's pinned build (C2); the games not passing on C2 ran three more on
the CD-only build (C1). 504 recordings in the main plan, 160 in the C1
plan, every one in the ledger with the boot it ran on and the hashes of
the boot programs.

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

| Measure | Limit as set on 1 November | In force now | Where it came from |
|---|---|---|---|
| match | at least 0.95 | the same | the bare card's own floor across 108 pairs was 0.96 |
| cover | at least 0.85 | the same | floor 0.86 |
| speed | within 2 % | the same | the bare card was exactly 1.00 in every pair |
| gaps | the game's own C0 maximum plus 1 | plus 2 | the 95th percentile of C0 run-to-run differences, read again on the filtered signal |
| steps back, jumps | C0 maximum plus 15, plus 25 | the same | the 95th percentile of C0 run-to-run differences |
| first audio | within 3 s of C0's median | within 2.5 s, on top of an allowance per DOS extender | C0 spread 0.8 s; then the sweep measured what the driver's start-up costs each extender |
| level | not judged | within 0.5 dB of the expected offset | added during the sweep: 6.0 dB down for disc music, level for game samples |
| runs to pass | 2 of 3 | the same | |

A game passes if two of its three C2 runs pass. The screen watchdog adds
run state: running, hung (screen and sound unchanged 20 s), crashed (an
exception on screen), exited to DOS. A recording with more than 2 % of its
window filled by the recorder, or outside 2 % of its expected length, is a
harness error and is retaken.

**What changed after the calibration, and why.** On 5 November every
sound measure was moved to the capture with its DC level filtered out,
because the emulated card holds its last output value when a game stops
and that had been read as sound. The calibration's recordings were judged
again on that signal, with the limits re-derived the same way from the
same games. Both readings are kept below. No recording was taken again
for it: the captures are the same, the instrument reading them changed.

## The result

**As first judged (2 November, the raw signal).** Of the 54 known-good
games: 15 match the bare card under the pinned build; 38 differ (32 on
the CD-audio side, 4 in the protected-mode host, 2 in game sound); 1 has
no working control on this bench (Johnny Bazookatone: the emulated CD-ROM
refuses a data read while a CD track plays). Of all 84: 17 pass.

**As judged again (5 and 6 November, the filtered signal).** Of the 84:
19 pass, 47 differ in a way that points at μCDD, 10 are silent on both
sides (games that wait for a key), and 8 have no passing control (the
games' own faults, or a handful with a written reason). Sorted into bins
with the CD-only build's result:

| Bin | Games |
|---|---|
| Pass | 19 |
| Differs, CD-audio side | 24 |
| Differs, DPMI host | 9 |
| Differs, game sound | 5 |
| The game's own fault (fails the same way on the bare card) | 6 |
| No sound in the window on the bare card | 6 |
| Not classified, each with a written blocker | 13 |
| A gap in the bench's setup | 1 |
| The driver's documented VCPI limit | 1 |

**How to read "47 differ".** It does not mean 47 broken games. The
calibration had one driver build, the fork's older line, and no level
rule. Of the 47, 37 are CD-audio games and 4 are members of CAND-32 in
the sweep (game samples 6 dB low on the fork's build alone). The sweep,
with the author's release beside it, showed two things that move many
CD-audio games on both builds: disc music 6 dB down (CAND-27) and a first
sound about a second later (CAND-23). How many of the 47 differ for those
reasons alone has not been counted. A game that differs for one of them
plays; it plays at another level or a moment later. The gate the calibration had to
pass was narrower and it passed it: the instrument repeats itself on the
bare card, and it tells a match from a mismatch.

**Quake.** It boots, launches, plays its demo and records sound on every
run. On the bare card it repeats itself (match 0.96, speed 1.00). Under
the fork's audio build it reads 5 % slow with a match of 0.82 on all three
runs; under the CD-only build it matches the bare card exactly. So the
difference is on the audio side. Quake is the only known-good game whose
speed is off by more than 2 %. *Hypothesis:* none recorded; the game has
ten CD-audio tracks and mixes its own sound, and which of the two is slow
has not been separated. In the sweep (90 seconds, no keys) Quake runs with
sound on the bare card, the pin and a2 alike, and no family holds it.

These are calibration bins. The sweep classifies every game again, with
three builds, and the context of the other games that share its sound
engine and extender, before anything is ranked for a report. See
[SWEEP.md](SWEEP.md).

## What it cost

The first calibration ran on the bench's own boot and measured the bench,
not the driver; it was kept as a baseline and the calibration was run
again on the PC's boot. That is the price of finding out the bench was
wrong before the sweep rather than after it.
