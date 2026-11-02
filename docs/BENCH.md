# The bench: what "emulator grade" means physically

Written by Claude. A short description of the machine behind every
emulator-grade result in the rows, so a reader knows what was measured
and what was not.

## The emulator

86Box 6.0, built with the dynamic recompiler available but turned off for
every run that records (an entry recorded with it on is marked and never
counts as evidence; the runner now defaults it off). Machine: an ASUS
P/I-P55T2P4 (Intel 430HX), the same chipset family as the real PC. CPU:
Pentium MMX 233 for the unit, driver and virtual-card tiers; an emulated
Pentium 133 for the game sweep, because an interpreting emulator at 233
cannot keep real time for a spinning game on this host and the recorder
fills the gap with silence (measured on ten games at four speeds; 133 is
the highest at which every one stays under 2 % filled). Sound card: 86Box's
Sound Blaster 16 at 220h, IRQ 5, DMA 1 and 5 for the sweep and most rows;
its SB Pro v2 and SB 2.0 for the rows that test those output paths. A 3Dfx
Voodoo Graphics beside the S3 Trio64V+ for the sweep, proven not to move
timing or the recorder. CD-ROM: 86Box's drive with OAKCDROM and MSCDEX
for the control configuration; μCDD's own mount for the driver
configurations.

DOSBox-X is installed as the second emulator for disputes and for one
held row, and is not yet an instrument: its runner has to pass a known
case and a planted fault before anything it records is evidence. QEMU was
used early and is not part of the campaign.

## The guest

MS-DOS 7.1 (the real PC's DOS, a recorded deviation from the charter's
FreeDOS so that the hardware kit reproduces the bench), JemmEx, SHSUCDX or
MSCDEX by configuration. `Logo=0` in MSDOS.SYS, because the boot-logo
timer hook holds interrupts off for up to 8 ms every two ticks and was the
cause of a week of apparent dropouts. For the sweep, the boot carries the
real PC's shell settings, CuteMouse on the emulated serial mouse,
S3VBE20, SetMul and the game library's own launcher helpers, and each
record carries every boot line and the hashes of the four boot programs.

Test programs wait with HLT or a port read, never a spin, unless the case
tests spinning; a test that spins measures the host's ceiling rather than
the driver.

## The recorder

86Box's audio goes to OpenAL on the host. A small library loaded beside it
logs every buffer the emulator hands over and every time a source runs dry,
on the host's clock; a sampler logs the host's busiest threads, their
cores and what they were waiting on, each second. From those two records
the harness knows, for any instant of a capture, whether what it hears is
the guest's or the recorder's: silence the recorder inserted is a harness
error, not a dropout. Each capture ends a fixed 2.5 s after the guest's
closing beep. The guest's own beeps (a PC-speaker tone at launch, another
at the end) align the capture to the guest's clock; a late closing beep is
judged only when the host record is clean and the guest's time-stamp
counter shows its BIOS count behind by the same amount.

One recording at a time: two at once multiplied the recorder's underruns
thirty-fold on this host. Nothing else runs on the machine while a plan
records; a check before every recording lists any other emulator or
display process and refuses to start.

## What the bench cannot say

It cannot say what a real card does with an odd half frame, how the
CT1345's stereo toggle behaves across transfers, which time constant gives
which rate on the real DSP, or whether a real Pentium 233 loses time under
16,000 trapped port writes a second. Those rows are held for the kit and
the real PC (Pentium MMX 233, 430HX, a Sound Blaster 16 CT2291 or an ESS ES1868F,
MS-DOS 7.1), where a person runs them and a human ear is a hardware
result. Emulator timing is never hardware truth; the emulator produces
candidates.
