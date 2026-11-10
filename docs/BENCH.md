# The bench: what "emulator grade" means physically

Written by Claude. As of 10 November 2026. A short description of the
machine behind every emulator-grade result in the rows, so a reader knows
what was measured and what was not.

## The emulator

86Box 6.0, built with the dynamic recompiler available but turned off for
every run that records (an entry recorded with it on is marked and never
counts as evidence; the runner defaults it off). Machine: an ASUS
P/I-P55T2P4 (Intel 430HX), the same chipset family as the real PC. CPU:
Pentium MMX 233 for the unit, driver and virtual-card tiers; an emulated
Pentium 133 for the game sweep, because an interpreting emulator at 233
cannot keep real time for a spinning game on this host and the recorder
fills the gap (measured on ten games at four speeds; 133 is the highest at
which every one stays under 2 % filled). Sound card: 86Box's Sound Blaster
16 at 220h, IRQ 5, DMA 1 and 5 for the sweep and most rows; its SB Pro v2
and SB 2.0 for the rows that test those output paths. A 3Dfx Voodoo
Graphics beside the S3 Trio64V+ for the sweep, proven not to move timing
or the recorder. CD-ROM: 86Box's drive with OAKCDROM and MSCDEX for the
control; μCDD's own mount for the driver builds.

## The second emulator

DOSBox-X (2026.10.01, its interpreting core) is the referee. It has one
job in the sweep: when a game's control fails on 86Box and a driver build
passes, the control is run on DOSBox-X with the same disk and boot lines.
If it fails there too, the failure is the game's or the boot's; if not,
the two emulators disagree and the game goes on the emulator list, not on
the driver's. A verdict the two emulators disagree on is a finding, never
a choice of the convenient one. DOSBox-X also judges a handful of
conformance cases where 86Box's own card gives no usable control. It is
not used for the sweep itself. QEMU was used early and is not part of the
campaign.

## The guest

MS-DOS 7.1, the real PC's DOS, so that what the bench finds is what the
hardware kit will reproduce (a recorded deviation from the first plan's
FreeDOS). Since 4 November the bench boots the real PC's own DOS files and
has its drives laid out as the PC's are, letter for letter: the games on
FAT32 volumes with 32 KB clusters. That last detail matters: the driver
reads a disc image through DOS, and how soon a game's first sound comes
under it moves with the cluster size (measured at 4, 16 and 32 KB). The
DOS files are the owner's own copy and are never in the repository.

Memory manager JemmEx; SHSUCDX or MSCDEX by configuration. `Logo=0` in
MSDOS.SYS, because the boot-logo timer hook holds interrupts off for up to
8 ms every two ticks and was the cause of a week of apparent dropouts. For
the sweep, the boot carries the real PC's shell settings, CuteMouse on the
emulated serial mouse, S3VBE20, SetMul and the game library's own launcher
helpers, and each record carries every boot line and the hashes of the
boot programs.

Each driver build is pinned: the fork's at one commit, the author's
release built unchanged with his own script, each with the hash of the
binaries the runs used. A run's record names the build, the bench's own
commit, the emulator, the CPU, the disk image and the boot.

Test programs wait with HLT or a port read, never a spin, unless the case
tests spinning; a test that spins measures the host's ceiling rather than
the driver.

## The recorder

86Box's audio goes to OpenAL on the host. A small library loaded beside it
logs every buffer the emulator hands over and every time a source runs dry,
on the host's clock; a sampler logs the host's busiest threads, their
cores and what they were waiting on, each second. From those two records
the harness knows, for any instant of a capture, whether what it hears is
the guest's or the recorder's: sound the recorder inserted is a harness
error, not a dropout. Only an underrun the log confirms counts as filled
time; a silence the log does not explain is the guest's.

Since 8 November the recorder also keeps each sound source's samples
beside the mix (the card's digital output, the FM synthesiser, the CD
input), so the level of a game's voices can be read apart from its music.
The mix is unchanged and is still the capture that is judged.

Each capture ends a fixed 2.5 s after the guest's closing beep. The guest's
own beeps (a PC-speaker tone at launch, another at the end) align the
capture to the guest's clock; a late closing beep is judged only when the
host record is clean and the guest's time-stamp counter shows its BIOS
count behind by the same amount.

Every sound measure reads the capture through a 6.4 Hz high-pass. The
emulated card's DAC holds its last value when a game stops playing, and
without the filter that DC level reads as loud sound.

One recording at a time: two at once multiplied the recorder's underruns
thirty-fold on this host. Nothing else runs on the machine while a plan
records; a check before every recording lists any other emulator or
display process and refuses to start. Captures are kept losslessly
compressed, each with a hash of its samples in the run's record.

## Checks on the bench itself

An instrument is trusted only after it has failed on a planted fault, and
again after every change to its rules. The recorder has plants for a host
stall, a dropped buffer and an injected tone; the level and timing judges
have theirs; the regression has two driver trees with a fault planted in
each that must fail the right rows. When a verdict surprises, the
instrument is suspected first and the screenshots are looked at.

## What the bench cannot say

It cannot say what a real card does with an odd half frame, how the
CT1345's stereo toggle behaves across transfers, which time constant gives
which rate on the real DSP, or whether a real Pentium 233 loses time under
16,000 trapped port writes a second. Those rows are held for the kit and
the real PC (Pentium MMX 233, 430HX, a Sound Blaster 16 CT2291 or an ESS
ES1868F, MS-DOS 7.1), where a person runs them and a human ear is a
hardware result. Emulator timing is never hardware truth; the emulator
produces candidates.
