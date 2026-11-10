# How the harness tests μCDD

Written by Claude, directed and tested by one person; every claim below is
checkable in the ledger and the rows it refers to. As of 10 November 2026.
This page says how a result is produced and what it is allowed to mean, so
that a reader can judge a finding without taking anyone's word for it.

## The thing under test

μCDD plays CD audio by standing between a DOS game and the sound card. The
game pokes a Sound Blaster through a handful of I/O ports: reset, version,
"play this buffer at this rate", "tell me when you have finished it". μCDD
traps each poke, acts the part of the card, mixes the game's samples with
the CD audio it streams from the image, and drives the real card itself.
Protected-mode games would bypass the traps through VCPI, so μCDD hides
VCPI and serves DPMI from a host of its own, running the game at ring 3.

The harness asks two questions of every piece of that: does it do what the
documents say a real card, a real DMA controller, a real interrupt
controller, a real DPMI host does; and does a game that works on the bare
card work the same under μCDD.

## The configurations, and why there is always a control

No case and no game is judged on one run of one build. Each runs in
several configurations, and the comparison between them is what carries
meaning:

- **C0, the control**: the emulator's own sound card and CD-ROM driver, no
  μCDD. If a test cannot pass here, the test is wrong, not the driver. If
  a game fails here, nothing is said about the driver from that game.
- **C2, the pin**: the fork's full driver, audio and DPMI host, at one
  pinned commit. The thing under test.
- **The author's release**: his own source, built unchanged with his own
  build script; 0.9.5-a1 for the conformance tests, then 0.9.5-a2
  (released 29 October) for those again and for the sweep. It says
  whether a fault on the pin is the driver's or only the fork's.
- **C1, the CD-only build**: the fork's driver with no audio and no DPMI
  host. It separates a CD-ROM data-path fault from the rest. The
  calibration measured that this build plays no CD audio at all (it
  refuses the command), so a C1 failure on sound alone says nothing about
  the data path.

A game that fails the same way on the control is the game's own fault. A
game that works on the control and on C1 and fails on C2 is a candidate.

## The tiers of test

- **Tier 0, unit.** Small programs that assemble the driver's own modules
  unchanged (the CUE and MDM parsers, the resampler, the ADPCM decoders, the
  de-emphasis filter) and feed them known inputs.
- **Tier 1, driver conformance.** A DOS program that talks to the driver
  the way games do, through the MSCDEX interface, on synthetic discs the
  harness generates itself: data tracks of known content, audio tracks of
  known tones, pre-emphasis flags, pregaps, multi-disc lists, and the
  rejected shapes. Seventeen cases: reads, seeks, track and disc info, play,
  stop, resume, eject, lock, prefetch, reads under play.
- **Tier 2, virtual card conformance.** Three clients, a real-mode program,
  a raw 16-bit DPMI client, and the same tests bound under DOS/4GW and
  PMODE/W, each doing exactly one thing a game does to a Sound Blaster: the
  DSP command families at every rate and format, the mixer, the 8237's
  modes and edge cases, the 8259's EOI forms and priorities, the timer
  stopped, interrupts held off, a child program spawned, buffers above
  1 MB. About 170 rows.
- **Tier 3, the sweep.** Every game in the library, launched and left alone
  for 90 seconds, screenshots every two seconds, the sound recorded, on the
  control, the pin and the author's release. Each driver recording is
  compared with the control's of the same game: its run state, how much of
  its sound matches, at what level, and how much later it starts.
  [SWEEP.md](SWEEP.md) has the procedure and what it showed.
- **Tier 4, hardware.** A kit the person carries to a real Pentium MMX 233
  with a Sound Blaster 16 CT2291 or an ESS ES1868F. Only a human running it
  produces a confirmed result; the emulator produces candidates.

## Rules that every result obeys

**Controls first.** A test program is validated on the bare card before it
judges μCDD. A test program's own bug attributed to the driver is the worst
outcome the harness can produce, so each new check is also run against a
planted fault (a known-bad build or a known-bad recording) and must fail
there before it is trusted.

**Ten of ten.** A Tier 0 to 2 case passes only at ten runs out of ten.
Nine of ten is a failure with the count. Timing faults are the subject, so
flakiness is signal, not noise; a case that passes some runs and fails
others becomes a candidate with its rate.

**The document decides.** Every row names the key of the document that
decides its expected result: Creative's Sound Blaster programming guide,
the 8237 and 8259 data sheets, the DPMI 0.9 specification, the MSCDEX
interface, μCDD's own README for what it promises to accept. A row with no
deciding document says `silent` and carries the terms it searched the
library with and how many hits they had, so "no document says" is a
recorded search, not a memory. Firmware disassemblies of the real DSP are
read-only behaviour references, cited by command number and observed
effect, never copied.

**The ledger.** Every run that can produce evidence is recorded by the
runner, not by hand: the plan it belongs to, the build's hashes, the
emulator and its version, whether the dynamic recompiler was off (a run
with it on is a comparison, never evidence), the capture and its hash. A
commit that cites a run as evidence is refused by the commit hook if the
ledger does not hold it as a pass.

**Evidence grades.** Each claim carries one: data sheet, emulator,
hardware, reading, or none. The order of trust is the specification, then
the real hardware, then two emulators in agreement, then one emulator,
then reading the source. A disagreement between emulators is written up as
a dispute, never resolved by picking the convenient one.

**The instrument is suspect first.** When a result surprises, the harness
looks at its own pictures and records before it looks at the driver.
Several of the campaign's largest findings were instrument faults: MS-DOS
7.1's boot-logo hook holding interrupts off for 8 ms every 110 ms (looked
exactly like a driver dropout until bisected to a line in MSDOS.SYS); the
host recorder inserting a 20 ms buffer under load (looks exactly like a
dropout until the closing beep is seen to have moved); a 1.5 % pitch
tolerance that hid a real 1 % error until calibrated from the bare card's
own spread (0.5 %); the emulated card holding its last output value when a
game stops, which a level meter reads as loud sound and a start detector
reads as sound that never ended (it produced a "30 dB quieter" finding and
a 4.7 s "late start", both withdrawn, and every sound measure now reads
the signal with its DC level removed). Each got a rule, a planted fault
that proves the rule, and a line in the notes with the data.

**Nothing is "probably fine".** A value is measured or it is UNKNOWN.
Results are superseded, never deleted. A retake of a failed plan needs a
written reason. No thresholds are tuned inside a test to make it pass;
every threshold lives in one file with the calibration run that set it.

**By rule, not by list.** A group of games is defined by a measurement
that any game can be put to ("the pin differs from the control where the
author's build does not"), never by naming its members. Games named in
advance as members of a family have turned out not to be, once measured.

**A correction keeps the old text.** When a row or a rule is found wrong,
the old wording stays beside the new with the date, so a reader can see
what was once believed and why it changed.

## Two builds, three lists

The harness pins one commit of the fork's line and runs every case against
it; that is the pin, and it never moves inside a gate. Because the fork's
line sits on an older base than the author's releases, a failure on the
pin can be a fault the author has since fixed. So every candidate's case is
also run, ten times, on the author's current release built unchanged with
his own build script. A candidate that fails there too is open upstream. A
candidate that passes there is one of two things: the fork's line lacking
an upstream fix (the author's release note is cited), or a fault the fork's
own work introduced (no note names it; the fork bisects its own commits).
The three lists are kept apart because the action on each is different.

## Classification of a game

Each build of the driver gets its own answer for each game. In order,
stopping at the first match:

1. A harness error (missing boot marker, a recording the recorder itself
   filled, the emulator died) is taken again, never binned.
2. An image the driver's README says it does not support is expected.
3. A game whose control fails has no control: it is the game's fault only
   when the build stops the same way with the same message; otherwise it
   is listed and not judged.
4. A game that is still and silent on the control, and in the same state
   under the build, cannot be judged without pressing a key. That is the
   limit of this test, not a fault of the game or the driver.
5. A documented limitation (extenders that need VCPI, auto-init ADPCM,
   sub-Pentium CPUs) is expected, with its evidence.
6. A build whose state, sound, level and timing are the control's, within
   the limits in force, passes.
7. Anything else is a candidate, sub-typed by what differs first: the
   DPMI host, the CD-ROM path, CD audio, game sound, level, start-up time.
   A result the second emulator disagrees on is a dispute.
8. A game none of these settles, because something blocks the reading, is
   unclassified, with the blocker named.

Every game that does not pass is then read against the other games that
share its sound engine and DOS extender: a group where every game fails
the same way is one bug and one report, not twenty; a game that fails
alone in a group that passes points away from the runtime and at the
game. This sorting is the work in hand; see [STATUS.md](STATUS.md).

## What the harness does not do

It does not modify μCDD. A fault it finds is a row with evidence and a
hypothesis in a field of its own, never a patch; the fork's own development
is frozen while the harness runs, so that the thing under test stays
still. It does not press keys in games, so a game that waits for one is
judged on whether it waited rather than crashed. It does not listen: it
measures. It does not send anything to the upstream author: every finding
stays in this repository.

## What is kept out of the repository

Game files, disc images, boot disks, firmware and recordings never enter
it; the repository holds hashes, scripts, synthetic test discs the harness
generates itself, and measurements. The commit checks refuse the rest at
the commit and again at the push, and the checks are tested against
planted faults like everything else.
