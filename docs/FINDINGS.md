# Findings: the candidate faults, as of 10 November 2026

Written by Claude from the rows in [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md),
which are the record; this page is a readable view of them. Each row there
names its plan in the ledger, the document that decides its expected
result, and its hardware status. Every finding on this page was measured
in an emulator, and every one is UNCONFIRMED on real hardware until the
kit has been run on the real PC.

Three words used throughout. The **pin** is the fork's driver at the
pinned commit, an older base than the author's releases. **a1** and **a2**
are the author's 0.9.5-a1 and 0.9.5-a2, built unchanged with his own build
script. The **control** is the same emulated machine with no μCDD.

**On hypotheses.** A finding is what was measured. Where a row carries an
idea about the cause, it is given here under the word *Hypothesis*, and it
is untested unless the line says otherwise: the driver is not being
changed while the harness runs, so no hypothesis has yet been tried
against a fix. A hypothesis that turned out wrong stays in its row with
the date it was withdrawn.

## The count

Thirty-two candidates have a number.

| Where found | Numbers | How they sort |
|---|---|---|
| Unit tests, driver conformance, virtual card conformance | CAND-1 to CAND-21 | Ten in both the fork and the author's release, nine fixed upstream and still in the fork's line, two introduced by the fork, one undetermined. (CAND-10 was split in two and sits in two lists.) |
| The sweep of 838 games | CAND-22 to CAND-32 | Four on the pin only, six on both builds, one a class with no member yet. Sorting each affected game into one bin is the work in hand. |

The table of all of them, with the version each is open in, is
[KNOWN-ISSUES.md](KNOWN-ISSUES.md). How a finding is produced and what it
is allowed to mean is [METHOD.md](METHOD.md). The conformance tiers
("Tier 0" a unit test of one module, "Tier 1" the CD-ROM driver interface
on a synthetic disc, "Tier 2" the virtual Sound Blaster driven by a test
program) are described there.

# Part one: the conformance findings, CAND-1 to CAND-21

Three lists and one left over, kept apart because the action on each
differs. Each case ran ten times on each build. The author's 0.9.5-a2
has since been run against every row: every case gives the same result
on a2 as on a1, so what is said of a1 below holds for a2, except one
rate: CAND-11's old buffer sounds on in 2 runs of 10 on a2, 3 of 10 on a1.

<a id="present-in-both"></a>
## 1. Present in this fork and in the upstream release

These fail on the pin and on a1, so they are properties of the driver's
design rather than of the fork's changes.

<a id="cand-4"></a>
### CAND-4. After Eject, the device status never reports the door open
Tier 1. The MSCDEX device status word has a bit for "door open"; after
IOCTL Eject it stays clear and a read then fails with "not ready". On a1
the eject itself is refused while the CD audio entry is attached (the
resident-audio build always attaches it), so the door never opens at all.
Decides: the MSCDEX driver interface (device status, Eject). What a period
driver reports for a real tray is the hardware's to say.

<a id="cand-8"></a>
### CAND-8. OCW2 Set Priority is dropped; a rotating EOI loses its rotation
Tier 2. A game that sets the card's IRQ to top priority with OCW2 and ends
interrupts with the rotating EOI form expects its card's interrupt served
before a waiting timer tick. Under the pin, Set Priority is dropped. On a1,
Set Priority passes through to the physical controller, but the rotating
EOI (A0h) matches none of the forms the virtual controller handles, so no
EOI is delivered and neither pending request is served afterwards.
Decides: 8259A data sheet, OCW2 forms and priority rotation.

<a id="cand-10b"></a>
### CAND-10B. A full 64 KB 8-bit auto-init buffer is refused
Tier 2. The 8237's count register codes 65536 bytes as FFFFh and the
guide's block length is "the number of bytes to transfer less 1", so a
64 KB buffer is the largest a program can code and a real card plays it.
Both builds refuse it: no sound, no interrupt. (The 16-bit half of the
original CAND-10 is fixed upstream; see list 2.) Decides: Creative's
programming guide, block length; 8237A data sheet, word count.

<a id="cand-11"></a>
### CAND-11. A DMA channel re-programmed at a block end is not followed
Tier 2. During auto-init a game moves the channel to a new buffer exactly
at a block interrupt. A real card fetches from the new address; the virtual
card keeps sounding the old buffer. On the pin in every run; on a1 in 3 of
10. Decides: 8237A data sheet, the channel's current address.

<a id="cand-12"></a>
### CAND-12. A 16-bit stereo auto-init block of an odd sample count is refused
Tier 2. The author's 0.9.4 note says odd counts are accepted; on the pin
the block is refused outright (no sound, no interrupt). On a1 the block
plays, but after the exit command D9h no interrupt comes, which is a
different failure with the same trigger. Decides: Creative's programming
guide, the 16-bit block length; the author's 0.9.4 note.

<a id="cand-13"></a>
### CAND-13. Odd-count 16-bit stereo single-cycle blocks swap channels every other block
Tier 2. Each block of an odd number of samples ends half a frame in; a real
card carries the odd word so the next block's first word lands on the
channel it should. The virtual card starts every other block on the right,
so the channels alternate block by block. Signed: the same on both builds.
Unsigned: a1 refuses the block where the pin plays it. The real CT2291
decides how the half frame is handled; it is in the kit.
Decides: Creative's programming guide, the stereo data order.

<a id="cand-15"></a>
### CAND-15. SB Pro stereo: the first data byte after the silent byte goes left
Tier 2. Creative's procedure for SB Pro stereo output sends one silent byte
before the data. The guide says the first byte after the stereo switch
goes to the left channel; the ES1868 data sheet, for its SB Pro-compatible
mode, says the first byte of a transfer is the right channel. Read
together: the silent byte takes the left slot and the data's first byte is
right, which both emulators also do. The virtual SB Pro sends the data's
first byte left, so the channels are swapped. The mechanism on the next
transfer (toggle persists, or resets per transfer) differs between the
CT1345 and the ESS and between the two emulators; that question needs a
real SB Pro 2 and is held. Decides: Creative's programming guide, CT1345
stereo switch; ES1868 data sheet, stereo DAC transfers in compatibility
mode.

<a id="cand-17"></a>
### CAND-17. After an 8237 master clear and re-setup, the block interrupt comes at once
Tier 2. A master clear halts the controller and the DSP keeps its own count
of bytes into the current block. When the channel is set up again the
first interrupt should come after the remainder of the interrupted block
(about 92 ms in the case); both builds raise it within a millisecond.
Decides: 8237A data sheet, master clear; Creative's guide, the block
interrupt after the programmed count.

<a id="cand-18"></a>
### CAND-18. Direct DAC output at 8 kHz plays slow under the trap
Tier 2. A game writing samples one at a time with DSP command 10h from an
8 kHz timer interrupt, 16,000 trapped port writes a second, loses about
1 % of its time on the pin (17 ms in a 2 s phase, measured by the
program's own time-stamp counter) and more while CD audio plays; a1 loses
more. The symptom is pitch; the cause is the trap's cost per write
against the interrupt period. Whether a real Pentium 233 loses the same
time without μCDD decides whether this is the driver's or the platform's;
it is in the kit as a measured case. Decides: Creative's guide, direct
mode; the expected result is the bare card's own timing.

<a id="cand-20"></a>
### CAND-20. While the channel is masked, the virtual transfer runs on
Tier 2. Masking a DMA channel disables its requests: nothing transfers, the
count stands, the DSP waits. Both builds keep advancing the stream's frame
while the channel is masked (summing silence), so the count moves across
the mask and the next block interrupt arrives within a millisecond of the
unmask instead of after the block's remainder. Seen from real mode, from
DOS/4GW, from PMODE/W and from the raw DPMI client, one result. Decides:
8237A data sheet, the mask register and DREQ.

<a id="fixed-upstream"></a>
## 2. Fixed upstream, still in the fork's line

These fail on the pin and pass on a1; the author's release note that fixed
each is cited in the row. They are the fork's backlog, not findings about
the author's code.

| ID | What | Author's note |
|---|---|---|
| CAND-1 | CUE sheet with INDEX 02 or higher refused | 0.9.4-a1 |
| CAND-2 | CUE sheet with a UTF-8 byte order mark refused | 0.9.4-a1 |
| CAND-5 | Audio-only CUE sheet refused, alone or in an MDM list | 0.9.4-a3 |
| CAND-7 | A 16-bit OUT to port 20h dropped whole, so the 21h mask byte never lands | 0.9.4-a3 |
| CAND-9 | An 8-bit block running past the end of its 64 KB DMA page refused | 0.9.4-a6 |
| CAND-10A | A 16-bit auto-init buffer over 32 KB refused | 0.9.4-a3 |
| CAND-14 | Mixer 81h ignored; 16-bit samples cannot use the 8-bit channel | 0.9.3d |
| CAND-16 | CD audio stalls 307 ms when a real-mode game stops the timer | 0.9.4-a3, 0.9.5-a1 |
| CAND-21 | An auto-init transfer from a buffer above 1 MB gives no sound | 0.9.4-a2 |

<a id="introduced-by-the-fork"></a>
## 3. Introduced by the fork

These fail on the pin and pass on a1, and no release note of the author's
names them: a1 never had the fault. The fork bisects its own commits when
its development resumes.

- **CAND-6.** CD audio drops out for up to a third of a second while data
  is read from the disc during play (the background-read scheduler under
  load).
- **CAND-19.** 256-byte 8-bit single-cycle blocks at 22050 Hz play 1.9 %
  low with sidebands near ±40 Hz while CD audio plays; 1.2 % low without.
  The shape of a periodic phase step in the resampler.

<a id="undetermined"></a>
## 4. Undetermined

- **CAND-3.** The virtual Sound Blaster's 2.6-bit ADPCM decoder differs
  from DOSBox-X's in 1475 of 1920 samples of a reference stream; the 4-bit
  and 2-bit decoders match. a1's decoder cannot be unit-tested without
  patching its source, which the harness does not do, so its a1 line is a
  reading only. No public document defines the 2.6-bit table; the kit
  carries the case for the real CT2291.

# Part two: the sweep's candidates, CAND-22 to CAND-32

Found by launching every game in the library and leaving it alone for 90
seconds on the control, the pin and a2 ([SWEEP.md](SWEEP.md)). Every one
is open. The sweep says that a build differs from the control and by how
much; it does not say why.

<a id="cand-22"></a>
### CAND-22. A launcher helper faults under the pin's DPMI host
Eighty-one of the library's launchers call a small helper, SETMUL.EXE (a
utility that slows the CPU for old games; it is a protected-mode program
that carries its own DPMI host for when none is present), before the game
starts. Under the pin it stops with "General Protection Fault at
eip=e0003843". It fails 10 runs of 10 on the pin and passes 10 of 10 on
the control and on a2. The fault is counted here, once, and not against
each of the 81 games: the screen names the helper as the program that
stopped. **Pin only.**
*Hypothesis:* the helper's CPU detection raises a processor exception
that the pin's host does not hand back to the program the way the
helper's own host and a2's host do. Whether the fork lacks a fix of the
author's or introduced the fault is not placed; it has not been run on a1,
and a run on a1 or a bisect places it.

<a id="cand-23"></a>
### CAND-23 and CAND-24. A CD-audio game's first sound comes later under the driver
On the pin a CD-audio game's first sound comes a median 1.3 s later than
on the control (15 games; 1.22 s as first filed, before the measure read
the signal with its DC level removed). On a2 the median is 0.9 s (14
games; 1.27 s as first filed). The largest are several seconds. **Both
builds.** Recorded as a finding for the real PC, where the disk is a
real disk.
*Hypothesis, in two parts not yet separated:* the launcher mounts the
disc image after the launch beep, where the control's drive is ready
before it; and the driver reads the image through DOS, so the first read
depends on the file system. The second part has a measurement behind it:
on the bench, the pin's first sound comes earlier as the disk's clusters
grow (one game 6.92, 6.05 and 5.95 s at 4, 16 and 32 KB clusters; the
control unmoved). The bench now uses the real PC's 32 KB.

A related measurement, not a numbered candidate: games with no CD audio
also start later under the driver, by an amount that depends on the DOS
extender (0.2 to 0.3 s in real mode; 2.3 s on the pin and 1.6 s on a2
under DOS/4GW). That is the DPMI host's start-up cost, and the allowance
for "late" is set per extender because of it. A game and build beyond its
allowance, with its sound still inside the window, is a **late first
sound** candidate: 19 pairs of the 503 measured. The pin is a median
0.86 s slower than a2 across DOS/4GW games; that gap is named and not
explained.

<a id="cand-25"></a>
### CAND-25. A program sees twice the memory under the driver, and some games fail on one side only
On the same 64 MB machine and the same memory manager line, a DOS
extender's program reports about 31 MB without μCDD and about 62 MB under
either build (Zork Nemesis prints 32,276,480 bytes on the control and
about 62.5 million under the pin and a2). It cuts both ways: Pirates!
Gold stops on the control alone with an insufficient-memory page fault
and runs with sound under both builds; Wing Commander Armada runs on the
control and stops under both builds at "EMS driver is not VCPI
compliant." **Both builds.** Kept as a finding, not a fault: the driver
hides VCPI and serves DPMI from its own host by design, and a different
memory picture follows from that.
*Hypothesis:* without μCDD the extender meets the memory manager's EMS
limit (the 31 MB figure sits just under EMS's 2048 pages of 16 KB); under
μCDD the DPMI host answers instead. Which call the extender makes has not
been read.

<a id="cand-26"></a>
### CAND-26. I Have No Mouth and I Must Scream stops with a memory message
It runs with sound on the control and stops under both builds: on the pin
at "Can't allocate enough memory for scene cache.", on a2 at "Unable to
initialize temp image memory pool." **Both builds.** The author's
0.9.5-a3 release note (7 November) names this game and a2's message and
says the DPMI host now reports less free memory so that a program which
takes the largest block can still allocate more. a3 has not been run on
the bench yet; it is one of the next three runs.
*Hypothesis (ours, before a3):* the game sizes its caches from the DPMI
host's answer and then cannot allocate the rest. The author's fix is
consistent with that.

<a id="cand-27"></a>
### CAND-27. The disc's music is 6.0 dB quieter than through the card's own CD input
With every mixer level at its top, a disc's audio track is recorded
9.6 dB under the disc's own level on the control and 15.6 dB under it
with the pin and with a2: 6.0 dB lower under the driver, the same in six
games read firmly. **Both builds.** First filed as "30 dB quieter", which
was the emulated card's held DC level and was withdrawn the next day.
*Hypothesis:* deliberate headroom, so that the disc and the game's own
sound can be added in 16 bits without clipping. The pinned build's source says
as much in a comment the fork added (a gain that halves each sample "keeps
every sample inside 16 bits, so nothing needs clipping"). Whether 6 dB down is
the right trade on a real card is a design question, not a defect; it is
listed so a listener is not surprised.

<a id="cand-28"></a>
### CAND-28. A class: "Packed file is corrupt" under the driver only
This is DOS's own message for a packed program whose unpacker fails. The
class is for a game that shows it under μCDD and runs on the control.
**No member yet**: the one game that prints it in this library printed
it on the control as well as under the pin in the calibration, and is the
game's own fault on this DOS; the sweep leaves it out.
*Hypothesis:* the unpacking fails when the program is loaded below 64 KB
with DOS loaded high; LOADFIX is the remedy. The load address has not
been measured.

<a id="cand-29"></a>
### CAND-29. Gabriel Knight 2 stops at a disc read error
Under the pin, DOS's "General failure reading drive G" 1.4 s after the
launch; under a2 the same failure with a garbled device name. On the
control it runs with sound. The game is a five-disc set mounted through
the driver's disc list. It fails on the fork's CD-only build as well,
which points at the CD-ROM side rather than the audio side. **Both builds.**
*Hypothesis:* none written. Which request the driver failed has not been
read.

<a id="cand-30"></a>
### CAND-30. Ultimate Domain plays no sound on the pin
The pictures are the same on all three and the game runs to the end of
the window. First sound comes at 12.9 s on the control and 13.1 s on a2;
on the pin, none. A real-mode game with its own Sound Blaster code.
**Pin only.**

<a id="cand-31"></a>
### CAND-31. Gabriel Knight 1 falls silent at its menu on the pin
The Sierra logo plays on all three builds. On the control and on a2 the
music then plays on to the end of the window; on the pin the menu is
still and silent from 21 s to the end, four takes of four. The disc has
no audio track: the music is the game's own, through the virtual card.
**Pin only.**

<a id="cand-32"></a>
### CAND-32. Game sound is 6.0 dB quieter on the pin
A game's own samples (voices, effects, sampled music) come out 6.0 dB
under the control on the pin, and level with it on a2. Sixty-seven games
show it, across the three big sample-playing sound engines (5 of 5 DMX
games read, 16 of 26 Miles, 15 of 26 HMI SOS; a game of those engines
that reads somewhere between is one that mixes FM or speaker sound into
the same passage). FM, PC-speaker and MIDI music does not pass through
that path and reads unchanged on both builds. Confirmed
three takes of three on one game per engine. On the fork's CD-only
build, which does not carry the game's sound, the level matches the
control. **Pin only.**
*Cause, by reading the source (not a hypothesis, but not a test either):*
both builds decode game samples at half level. The author's a2 then
doubles them again while no disc is playing; that change came in one of
his commits of 24 October, which the pin's older line does not have. So
this is a fix the fork lacks, and with a disc playing a2 halves game
sound as well, for the headroom in CAND-27.

A game whose level gap on the pin is some other size is not this
candidate; each keeps a row of its own until it is read. In two (Tyrian
and Tyrian 2000) the gap is more than 20 dB.

## Groups the sweep found that are not one fault

**Two extenders that do not run under a2.** None of the seven Phar Lap
games and none of the five PMODE/W games runs under a2; all twelve are
back at the DOS prompt. The author's README says that a program which
supports only VCPI needs the driver installed with `-vcpi`, at the cost
of its sound bypassing the driver, and on 7 November his wiki named
BioForge as such a game. *Working reading, being tested now:* these are
the driver's stated limit, not twelve faults. Each is being taken again
with `-vcpi`. The pin differs (two of the PMODE/W games run on it, and
four of the Phar Lap games stop at a memory manager exception where a2
exits cleanly), which is a second question behind the first.
[SWEEP.md](SWEEP.md) lists the games.

**Runs under the driver, not on the control.** A short list kept by
name: Pirates! Gold (the control's page fault, above), Bruce Lee (the
control restarts the machine a few seconds after the title, on every
boot), M.C. Kids (the control stays black and silent) and Street Fighter
II (the control stops at a memory manager exception). Each runs under
both driver builds. Cause unread in each; they are listed with no
verdict, because a game whose control fails has no control. By rule
rather than by name, the sweep's table holds six more games where a2 runs
or plays and neither the control nor the pin does (Heart of China among
them, whose card test is in the environment list below).

**Control fails.** Eighty-nine games do not run on the control on this
bench at all. Nothing is said about the driver from them. Twelve of
those that a driver build passes were put to the second emulator; in
five the failure appeared there too, so it is the game's or the boot's.

## Held for hardware

Rows whose judge is the real card and which the kit carries: the 8237 page
wrap on an 8-bit block (SC8PAGE2); the 8259's special mask mode
(PICSMM2), which 86Box does not emulate; the DSP's time-constant table
(TCROUND), measured in full by a self-timing program on the CT2291;
S16ODD2 and the 48 kHz 16-bit stereo case; the DAC and timer-stop cases at
8 kHz; the mixer 81h write. CAND-15's next-transfer question needs an SB
Pro 2, which the person does not have.

## Findings about the environment, not the driver

Recorded because a reader of the rows will meet them, and because each
would otherwise be mistaken for a driver fault. Several were, for a time.

- **The boot logo holds the timer (IOSYS08).** MS-DOS 7.1's boot-logo
  code hooks the timer and, on every second tick, re-enables interrupts
  and polls for vertical retrace with IRQ 0 still in service, holding
  faster timer interrupts off for up to 8 ms. It stops with `Logo=0` in
  MSDOS.SYS. Any game that reprograms the timer fast loses ticks under
  this DOS, on real hardware as in the emulator.
- **A date call resets the tick count (DOSDATE).** MS-DOS 7.1 rewrites
  the BIOS tick count from the real-time clock on a date call, and DOS's
  EXEC makes one, so a tick count read across a child program's start or
  end is unreliable.
- **The emulator falls behind at 233 MHz (86FILL).** An interpreting
  emulator at an emulated 233 MHz cannot keep real time for a spinning
  guest on this host; the recorder fills the gap. The sweep runs at an
  emulated Pentium 133 for that reason, every build on the same CPU.
- **The emulated card holds DC when a game stops (ACSIG).** A stopped
  DAC on the emulated Sound Blaster 16 keeps its last value. A level
  meter reads that as loud sound and a start detector reads it as sound
  that never ended. Every sound measure now reads the signal through a
  6.4 Hz high-pass. This one produced two false findings before it was
  found.
- **Cluster size moves the driver's start-up time.** The driver reads a
  disc image through DOS, so the size of the disk's clusters changes how
  soon the first sound comes (CAND-23). The bench's disks were rebuilt to
  the real PC's layout, letter for letter, on 4 November.
- **Where the emulators disagree with each other or with the data
  sheets.** The emulator's own CD-ROM drive misreads a CUE sheet whose
  data track has 2048-byte sectors; its interrupt controller has no
  special mask mode; its 8-bit DMA crosses a 64 KB page where the second
  emulator wraps; its Sound Blaster gives no interrupt for a 16-bit
  stereo single-cycle block of an odd sample count; its mixer keeps 0 dB
  after a reset where the data sheet's defaults are lower; and both
  emulators read two mixer registers unlike the real card. Each has a row,
  and each case it touches is held for the real card.
- **The second emulator has no EMS page frame under this memory
  manager.** Four of the twelve control disputes could not be judged on
  it for that reason.
- **One game's card test (Heart of China)** waits a fixed number of loop
  passes for the interrupt of a one-byte block. Whether it passes is a
  question of how fast the machine is, and the real PC decides.
- **A fidelity note on a2.** The author's virtual mixer reads two status
  registers with their reserved bits clear where the real card (and the
  pin) reads them set. No game is known to care; it is recorded.
- **386 Spys.** Its Phar Lap extender refuses to run in virtual 8086 mode
  under another program's control, which is the driver's documented VCPI
  limitation, not a fault. It is one of the seven Phar Lap games above.
