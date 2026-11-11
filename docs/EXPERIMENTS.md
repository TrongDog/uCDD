# Experiments: the lab notebook

Written by Claude. As of 11 November 2026. Every experiment the harness
has run that changed what is believed, oldest first. Each entry has the
same four parts: the question or the hypothesis going in, the test, the
result in numbers, and the conclusion. Long tables are folded; the long
write-ups are their own pages.

All of it was measured in an emulator ([BENCH.md](BENCH.md)). The row
named at the end of an entry, in
[ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md),
holds the recorded runs.

| | Experiment | Outcome in a line |
|---|---|---|
| E-01 | [Can the harness tell a working game from a broken one?](#e-01-can-the-harness-tell-a-working-game-from-a-broken-one) | Yes, once it was booted like the real PC. |
| E-02 | [Are the dropouts the driver's?](#e-02-are-the-dropouts-the-drivers) | No: the DOS boot logo held the timer. |
| E-03 | [How fast can the emulated PC be?](#e-03-how-fast-can-the-emulated-pc-be) | A Pentium 133, not a 233. |
| E-04 | [How many recordings at once?](#e-04-how-many-recordings-at-once) | One. |
| E-05 | [Is the pitch tolerance tight enough?](#e-05-is-the-pitch-tolerance-tight-enough) | No: 1.5 % hid a 1 % error. Now 0.5 %. |
| E-06 | [Does a 3D card on the emulated PC move the timing?](#e-06-does-a-3d-card-on-the-emulated-pc-move-the-timing) | No. |
| E-07 | [Is the disc's music 30 dB quieter under the driver?](#e-07-is-the-discs-music-30-db-quieter-under-the-driver) | No: 6 dB. The 30 was the bench. |
| E-08 | [Does the disk's cluster size move the first sound?](#e-08-does-the-disks-cluster-size-move-the-first-sound) | Yes, under the driver only. |
| E-09 | [The sweep: 838 games on three builds](#e-09-the-sweep-838-games-on-three-builds) | Eleven candidates and the families. |
| E-10 | [Game sound 6 dB low on the fork: a fault, or a fix it lacks?](#e-10-game-sound-6-db-low-on-the-fork-a-fault-or-a-fix-it-lacks) | A fix it lacks, by reading the source. |
| E-11 | [Does a game that sounds also sound right?](#e-11-does-a-game-that-sounds-also-sound-right) | Not always: the sweep had not checked. |
| E-12 | [Do the Phar Lap and PMODE/W games need VCPI?](#e-12-do-the-phar-lap-and-pmodew-games-need-vcpi) | Two do. Ten are host candidates. |
| E-13 | [Does the author's 0.9.5-a3 fix the memory stop?](#e-13-does-the-authors-095-a3-fix-the-memory-stop) | Yes, on one take. |
| E-14 | [Do faults seen once hold on three takes?](#e-14-do-faults-seen-once-hold-on-three-takes) | 44 of 44 held. |
| E-15 | [Which line moved: the fork's or the author's?](#e-15-which-line-moved-the-forks-or-the-authors) | In hand. |

---

### E-01. Can the harness tell a working game from a broken one?

**Hypothesis.** A game the author and others report as working will be
read as working by the harness. If not, the harness is broken, not the
game.

**Test.** 84 games: 54 known-good ones that sound within 90 seconds, one
game for each group of sound engine and DOS extender, and Quake. Three
takes on the control and three on the pin; the games not passing got
three more on the CD-only build. 504 recordings, then 160.

**Result.** The first attempt measured the bench. Quake died on the
first line of its launcher on the control and the pin alike, and most
"failures" were the same on both sides: no PATH, no mouse driver, no
VESA driver, none of the helper programs the library's launchers call,
and the library on the wrong drive letter. Run again on the real PC's
boot, the control repeated itself: match at least
0.96, cover at least 0.86, speed exactly 1.00 in every pair of 54 games.
As judged again on 5 and 6 November: 19 pass, 47 differ, 10 are silent
on both, 8 have no passing control.

**Conclusion.** The instrument repeats itself on the bare card and tells
a match from a mismatch. The first attempt had measured the bench. The
limits were set from the control's own spread. Long write-up:
[CALIBRATION.md](CALIBRATION.md). Row: CALTHRESH.

### E-02. Are the dropouts the driver's?

**Hypothesis.** Short dropouts in tone tests under the driver are the
driver losing interrupts.

**Test.** The same tests on the control, with no driver, and a read of
what holds the timer interrupt.

**Result.** The dropouts were there with no driver loaded. MS-DOS 7.1's
boot-logo code hooks the timer and, on every second tick, polls the
display with IRQ 0 still in service, holding faster timer interrupts off
for up to 8 ms.

**Conclusion.** Not the driver's. `Logo=0` in MSDOS.SYS stops it on the
bench; the real PC runs the same DOS, where it has not been measured. It
had cost a week. Row: IOSYS08.

### E-03. How fast can the emulated PC be?

**Hypothesis.** The emulated machine can be the real PC's speed, a
Pentium MMX 233.

**Test.** A test program with a spinning main loop on the control at 233,
then ten games one at a time at MMX 200, MMX 166 and Pentium 133, reading
how much of each 90-second capture the recorder had to fill.

**Result.** At 233, with the recompiler off, the emulator falls behind
real time whenever the guest spins, and the recorder fills the capture
with repeated buffers: the worst game had 17.6 % of its window filled.
The Pentium 133 was the highest of the three at which all ten games
stayed under 2 % filled; the worst game there is at 0.5 %.

**Conclusion.** The sweep runs at an emulated Pentium 133, every build on
the same CPU. The unit, driver and card tests stay at 233, because their
programs wait with HLT or a port read and never spin. Rows: 86FILL,
TIER3CPU.

<details>
<summary>Filled time per game at each speed (the TIER3CPU row, 29 October 2026)</summary>

Share of the capture the recorder filled, and the take's state; C2 the
pin, C0 the control (taken for three games).

| Game | 233 C2 | 200 C2 | 166 C2 | 133 C2 | 233 C0 | 200 C0 | 166 C0 | 133 C0 |
|---|---|---|---|---|---|---|---|---|
| LOLLYPOP | 5.54 % running | 2.41 % running | 0.02 % running | 0.00 % running | 6.50 % running | 3.01 % running | 0.12 % running | 0.00 % running |
| REDRAMRA | 0.16 % running | 0.09 % running | 0.00 % running | 0.01 % running | | | | |
| BATTLEAR | 17.63 % hang | 9.58 % hang | 3.09 % hang | 0.00 % hang | 15.15 % hang | 10.29 % hang | 2.91 % hang | 0.01 % hang |
| TRACKATT | 0.13 % exited | 0.00 % exited | 0.01 % exited | 0.50 % hang | | | | |
| DEDERBY | 0.78 % running | 0.19 % running | 0.09 % running | 0.00 % running | | | | |
| STARGENE | 0.09 % running | 0.00 % exited | 0.16 % exited | 0.00 % exited | | | | |
| FXFIGHTE | 0.01 % running | 0.00 % running | 0.01 % running | 0.04 % running | | | | |
| GOB3 | 0.15 % running | 0.10 % running | 0.11 % running | 0.01 % running | | | | |
| XCOMUF | 2.63 % running | 0.00 % running | 0.01 % running | 0.04 % running | 2.07 % running | 0.08 % running | 0.18 % running | 0.00 % running |
| ADOM | 0.20 % hang | 0.10 % hang | 0.03 % hang | 0.00 % hang | | | | |
| worst | 17.63 % | 9.58 % | 3.09 % | 0.50 % | 15.15 % | 10.29 % | 2.91 % | 0.01 % |

</details>

### E-04. How many recordings at once?

**Hypothesis.** Four emulators can record side by side, as first planned.

**Test.** Ten games recorded one at a time, then two at a time, then
four, each with its own display, files and capture, comparing the
recorder's underruns per capture.

**Result.** Two at once multiplied the recorder's underruns thirty-fold.

**Conclusion.** One recording at a time, and nothing else on the machine
while it records. Row: PARALLEL.

### E-05. Is the pitch tolerance tight enough?

**Hypothesis.** A captured tone within 1.5 % of its expected pitch is
right. The figure had been chosen, not measured.

**Test.** Every tone the bare card had played to date: 1990 tone and band
checks in 36 plans, each peak measured against its expected frequency.

**Result.** The bare card's largest deviation was 0.161 %. With the
tolerance set from that, two cases that had passed now failed: one
0.9 % low and one 1.1 % low under the driver.

**Conclusion.** The tolerance is the larger of 0.5 % and three times the
control's largest deviation: 0.5 %. Every limit since has been set from
the control's own spread and not chosen. Row: PITCHCAL.

### E-06. Does a 3D card on the emulated PC move the timing?

**Hypothesis.** Adding the real PC's Voodoo card to the emulated one will
not change what the recorder or the watchdog reads.

**Test.** The five watchdog test cases, one Glide game, and one known-good
game whose control and pin takes must match its takes without the card.

**Result.** The five cases read as before, with no underruns and under
0.03 % filled. Shadow Warrior's Glide build reached its 3D menu with
sound on the control and the pin (pin against control: match 1.00, cover
0.93, speed 1.00) where without the card it stopped at its Glide check.
The known-good game's takes passed the same limits as before.

**Conclusion.** The card is on for the sweep. Row: VOODOO.

### E-07. Is the disc's music 30 dB quieter under the driver?

**Hypothesis (from a first reading on 3 November).** Disc music is about
30 dB quieter under the driver than through the card's own CD input.

**Test.** The level again, game by game, and a look at the waveform when
a game stops playing.

**Result.** The emulated card's DAC holds its last value when a game
stops. A level meter reads that held value as loud sound, and a start
detector reads it as sound that never ended. With the signal passed
through a 6.4 Hz high-pass, the difference is 6.0 dB: 9.6 dB under the
disc's own level on the control, 15.6 dB under it with either driver
build, the same in six games.

**Conclusion.** The 30 dB finding was withdrawn the next day, and a
"4.7 second late start" with it. Every sound measure now reads the
filtered signal. The 6.0 dB is real; the mixer's own comment calls its
halving headroom, which the row holds as a labelled hypothesis
([CAND-27](FINDINGS.md#cand-27)). Row: ACSIG.

### E-08. Does the disk's cluster size move the first sound?

**Hypothesis.** The driver reads the disc image through DOS, so the file
system's cluster size changes how soon a CD-audio game's first sound
comes.

**Test.** One game on the pin and on the control, with the games disk
formatted at 4, 16 and 32 KB clusters.

**Result.** The pin's first sound at 6.92, 6.05 and 5.95 s. The control
did not move.

**Conclusion.** The hypothesis held. The bench's disks were rebuilt to
the real PC's layout (32 KB clusters) on 4 November, and the takes made
before that on the older layout are marked. Row:
[CAND-23](FINDINGS.md#cand-23).

### E-09. The sweep: 838 games on three builds

**Question.** For every game in the library: does it behave under the
driver as it does without it?

**Test.** Each game launched and left alone for 90 seconds on the
control, the pin and the author's 0.9.5-a2, in seventeen batches from 2
to 7 November. The CD-only build on 52 candidates; a second emulator on
twelve control failures.

**Result.**

<details>
<summary>The families, by games</summary>

| Family | Games |
|---|---|
| Differs on the pin only | 107 |
| of which game sound 6 dB low | 67 |
| Differs on a2 only | 11 |
| a2 runs where neither the control nor the pin does | 6 |
| The control itself fails | 89 |
| First sound later than its allowance | 19 game-and-build pairs of 503 |

Start-up cost of the driver's DPMI host, to first sound: 0.2 to 0.3 s for
real-mode games; 2.3 s on the pin and 1.6 s on a2 for DOS/4GW games.

</details>

**Conclusion.** Eleven numbered candidates (CAND-22 to CAND-32), and the
discovery that most games that differ on the pin differ for one reason
(E-10). The sweep says that a build differs and by how much, never why.
Long write-up: [SWEEP.md](SWEEP.md).

### E-10. Game sound 6 dB low on the fork: a fault, or a fix it lacks?

**Hypothesis.** The fork's build plays a game's own samples at half
level because of a fault the fork introduced.

**Test.** The level on three builds, per sound source; the CD-only build;
and a read of both source trees.

**Result.** 6.0 dB low on the pin and level on a2, in 67 games (5 of 5
DMX games read, 16 of 26 Miles, 15 of 26 HMI SOS). FM, speaker and MIDI
music unchanged. On the CD-only build, which does not carry the game's
sound, the level matches the control. Both source trees take game samples
at half level; a2 then doubles them while no disc is playing, a change
the author made on 24 October, after the fork's base.

**Conclusion.** The hypothesis was wrong: it is a fix the fork lacks.
Measured on the base release (E-15): two of the three games that stand
for the group read on 0.9.3b as on the pin, 6.01 and 6.02 dB low against
the pin's 6.01; the third, Doom, stops in its own start-up on 0.9.3b, so
its level could not be read there. The group's label stays UNKNOWN by the
rule that the three must agree; the two that could be read say the fix is
the author's, made after 0.9.3b. Row: [CAND-32](FINDINGS.md#cand-32).

### E-11. Does a game that sounds also sound right?

**Hypothesis.** A game that runs, makes sound at the control's level and
starts on time is playing the same sound as the control.

**Test.** Quake first: the calibration had compared its sound piece by
piece; the sweep had not. Then the 109 game-and-build pairs of CD-audio
games that ran with sound but had never been compared, matched from the
captures already stored.

**Result.** Quake on the pin: a match of 0.82 and 5 % off speed, three
takes of three, while the sweep's measures read it as running with sound.
After the matching, passes rose from 205 to 222 on the pin and from 291
to 318 on a2, and sound differences from 21 to 28 and from 6 to 31.
Twenty CD-audio games differ on both builds, mostly the same games in the
same way: short gaps in the music in seven, missing stretches in five
games of one sound engine.

**Conclusion.** The hypothesis was wrong. A game with CD-audio tracks now
passes only where its sound was compared and is the same; otherwise it is
counted apart as "runs with sound". A difference only counts where the
game's own control repeats itself: every game whose difference had no
control pair was given a second control take (31 games); 30 repeated, and
one (Carmageddon, match 0.79) did not, so its sound is not read on either
build. Each difference that rested on one comparison was then taken twice
more (42 rows, 84 takes): 38 held on three takes of three, 2 on two of
three, and 2 did not repeat and are marked flaky.

### E-12. Do the Phar Lap and PMODE/W games need VCPI?

**Hypothesis (a working reading, 10 November).** None of the seven Phar
Lap games and none of the five PMODE/W games runs under a2. The author's
README says a program that supports only VCPI needs `-vcpi`. So these
twelve are the driver's stated limit, not twelve faults.

**Test.** Each game again with the driver installed with `-vcpi`, on a2
and on the pin; then the author's a3 and a1 on the PMODE/W five.

**Result.** With `-vcpi`, ten of the twelve run. But only two are shown
to support nothing but VCPI: 386 Spys, by its own message, and BioForge,
which the author's wiki names. The README also says PMODE/W uses the
driver's DPMI host when VCPI is hidden, so those games are meant to run
without `-vcpi`. All five PMODE/W games stop on a1, a2 and a3. The pin
runs two of them, Rayman and Rayman Forever; Rayman is on the author's
list of working games.

**Conclusion.** The hypothesis was wrong for ten of the twelve. Two are
the stated limit. Ten are candidates against the DPMI host, with `-vcpi`
as a workaround for eight of them. Whether the author's line changed
after 0.9.3b or the fork's did is E-15. Row: CAND-33.

### E-13. Does the author's 0.9.5-a3 fix the memory stop?

**Hypothesis.** a3's release note names I Have No Mouth and I Must Scream
and says the DPMI host now reports less free memory. So a3 runs the game
that a2 stops.

**Test.** a3, built unchanged, on 40 games: the protected-mode games not
running under a2, the memory finding's games, and a passing game from
each protected-mode group.

**Result.** I Have No Mouth runs on a3 (one take) where the pin and a2
stop with memory messages. Three games that pass on a2 read "runs with
sound" on a3 only because their a3 sound has not been compared.

**Conclusion.** The hypothesis held, on one take. Row:
[CAND-26](FINDINGS.md#cand-26).

### E-14. Do faults seen once hold on three takes?

**Hypothesis.** A fault of state or sound seen on one take is repeatable.

**Test.** Two more takes for each of the 44 rows that rested on one.

**Result.** 44 of 44 held, three takes of three.

**Conclusion.** The single takes were sound. Two sound differences
elsewhere did not repeat and are kept as intermittent.

### E-15. Which line moved: the fork's or the author's?

**Question.** For a fault only one driver has, did the fork introduce or
fix something, or did the author?

**Test.** The author's 0.9.3b, the release the fork started from, built
unchanged and run on the same games. If it behaves as the fork's build,
the author's line moved; if it behaves as the author's current build,
the fork's did.

**Result.** 0.9.3b's own settings file was first proven byte for byte
against its own setup program's save, and every take of it showed the
driver installed. One take on each of the 107 games that differ on the
pin only (CAND-32's group by three of them): 28 read as the pin
(LACKS-FIX), none as the control and a2 (FORK-REGRESSION), 79 neither or
unreadable (UNKNOWN; 64 of them CAND-32's group). Three conformance cases,
ten runs each on 0.9.3b: CAND-6 passes as a2 does (FORK-REGRESSION),
CAND-22 fails as the pin does (LACKS-FIX), and CAND-19 fails another way
(UNKNOWN). On 11 November the 17 games that differ on a2 only or run past the
control on a2 alone, and two more of the five PMODE/W games, one take
each: of the 11 that differ on a2 only, 7 read as the pin on 0.9.3b (the
author's line moved since: UPSTREAM-REGRESSION; Rayman and S.T.O.R.M.
among them), 1 as a2 (the fork's line moved: FORK-FIX), 3 neither; of the
6 that run past the control on a2 alone, 4 read as a2 (the fork's line
moved) and 2 as the pin (the author's).

**Conclusion.** Most of what the fork's build alone gets wrong is a fix
the author made after the fork's base; one conformance fault, CAND-6, is
the fork's own. Most of what the author's build alone gets wrong came in
on his line after 0.9.3b. Each row says its label.
[REFERENCE.md](REFERENCE.md#labels-which-line-moved) has the labels.
