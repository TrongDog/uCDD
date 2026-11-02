# Findings: the candidate faults, as of 2 November 2026

Written by Claude from the rows in [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md),
which are the record; this page is a readable view of them and says
nothing the rows do not. Each row in ISSUES.md names its ten-run plan in the
ledger, the document that decides its expected result, and its hardware
status (every one is UNCONFIRMED on real hardware until the kit has been
run). "Tier 0" below is a unit test of one module; "Tier 1" the CD-ROM
driver interface on a synthetic disc; "Tier 2" the virtual Sound Blaster
driven by a test program; the tiers are described in
[METHOD.md](METHOD.md).
Hypotheses are labelled as such in the rows and are not repeated here.

The one-page table of these, with the version each is open in, is [KNOWN-ISSUES.md](KNOWN-ISSUES.md). Three lists, kept apart because the action on each differs. "Pin" is the
fork's line at the pinned commit (an older base than the author's
releases). "a1" is the author's 0.9.5-a1 built unchanged with his own
build script. The author's 0.9.5-a2 (29 October), built the same way, has
since been run against every row, ten runs each: every case gives the
same result on a2 as on a1, so what is said of a1 below holds for a2,
except one rate: CAND-11's old buffer sounds on in 2 runs of 10 on a2,
3 of 10 on a1.

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

## Held for hardware

Rows whose judge is the real card and which the kit carries: the 8237 page
wrap on an 8-bit block (SC8PAGE2); the 8259's special mask mode
(PICSMM2), which 86Box does not emulate; the DSP's time-constant table
(TCROUND), measured in full by a self-timing program on the CT2291;
S16ODD2 and the 48 kHz 16-bit stereo case; the DAC and timer-stop cases at
8 kHz; the mixer 81h write. CAND-15's next-transfer question needs an SB
Pro 2, which the person does not have.

## Findings about the environment, not the driver

Recorded because a reader of the rows will meet them, and because they
would otherwise be mistaken for driver faults:

- **IOSYS08.** MS-DOS 7.1's boot-logo code hooks the timer and, on every
  second tick, re-enables interrupts and polls for vertical retrace with
  IRQ 0 still in service, holding faster timer interrupts off for up to
  8 ms. It stops with `Logo=0` in MSDOS.SYS. Any game that reprograms the
  timer fast loses ticks under this DOS, on real hardware as in the
  emulator.
- **DOSDATE.** MS-DOS 7.1 rewrites the BIOS tick count from the real-time
  clock on a date call, and DOS's EXEC makes one, so a tick count read
  across a child program's start or end is unreliable.
- **86FILL.** An interpreting emulator at an emulated 233 MHz cannot keep
  real time for a spinning guest on this host; the recorder fills the gap
  with silence that the length check cannot see. The sweep runs at an
  emulated Pentium 133 for that reason, with C0 and C2 on the same CPU.
- **386 Spies.** Its Phar Lap extender refuses to run under V86 mode, which
  is μCDD's documented VCPI limitation, not a fault.
