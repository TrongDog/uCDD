# Plans: what happens next, and the ideas after that

Written by Claude. As of 11 November 2026. Three lists, in the order
they will happen. The first is work in hand. The second is decided in
outline and waits for the first. The third is ideas: nothing in it is a
commitment, and each item says what would have to be measured before it
became one.

No change to the driver is being made while the harness runs. That is
why every fault on the other pages has a hypothesis and none has a fix.

## 1. Now: finish the harness's last stage

1. Three runs that can each move a whole group of games: the Phar Lap and
   PMODE/W games with the driver installed with `-vcpi`; the author's
   0.9.5-a3 on the protected-mode games that do not pass; the author's
   compatibility wiki read again as it stands now.
2. Every game sorted into one bin per build, then read against the games
   that share its sound engine and DOS extender.
3. One report per fault, or per group that fails the same way, largest
   group first, each with the document that decides the expected
   behaviour and the smallest case that shows the difference.
4. Each fault that only the fork has labelled as one of two things: a fix
   the author made after the fork's base, or something the fork
   introduced.
5. The kit for the real PC, and then the real PC: the conformance cases
   only a real card can judge, and a short list of games chosen to cover
   every group with the least listening. Until a person has run it,
   nothing on these pages is confirmed.

[STATUS.md](STATUS.md) tracks this list.

## 2. When development resumes

In this order, because each step changes what the next one would find.

1. **Bring the fork's line up to the author's current release.** The
   fork's base is 0.9.3b. The author's line is 47 commits past it at
   0.9.5-a3 and the fork has 238 commits of its own. This one step is
   expected to clear the nine conformance faults the author has fixed,
   the game sound that is 6 dB low on the fork's build (CAND-32, which is
   a change of his the fork lacks), and possibly the launcher helper's
   fault (CAND-22). Three of the fork's features (disk controller IRQs,
   stepping aside, fast DMA) now exist upstream in the author's own form,
   so the fork's versions of those are compared with his and the
   duplicate dropped. Then the whole harness is run again on the result:
   that is what it was built for.
2. **Bisect what the fork introduced.** CD audio dropping out during disc
   reads (CAND-6), short single-cycle blocks playing flat (CAND-19), and
   whichever of the sweep's fork-only faults (CAND-30, CAND-31, and the
   forty games that differ on the fork alone for other reasons) survive
   step 1.
3. **The faults that are in every version**, ranked by how many games
   each reaches in the sweep, not by how interesting they are. The ten
   conformance faults present in both ([KNOWN-ISSUES.md](KNOWN-ISSUES.md))
   and the sweep's both-build candidates. Each fix is proposed with its
   test case, and the test has to fail before the fix and pass after.
4. The virtual ESS's compatibility-mode stereo channel order, per the
   ES1868 data sheet.
5. The virtual SB16's time-constant table replaced by one measured on the
   real CT2291.
6. A DPMI host that absorbs a client's HLT instead of faulting it, if the
   sorting finds a game that idles that way.
7. The ESS half-rate mode, which needs a mixer change first.

## 3. Ideas, not commitments

Each came out of something the sweep measured. None is designed. Each
names what would have to be found out first.

- **Changing discs without a hotkey.** Thirty-three games in the library
  come on more than one disc, and one of them (Gabriel Knight 2, five
  discs) fails at a disc read. *First:* a survey of how each multi-disc
  game asks for the next disc, to see whether the driver could tell.
- **A loader helper for "Packed file is corrupt".** Three of the
  library's launchers call LOADFIX, which the real PC's DOS does not
  carry. *First:* a member for the class (CAND-28 has none yet) and the
  load address measured.
- **A limiter in place of the fixed 6 dB of headroom.** Disc music and
  game sound are each halved so that their sum cannot clip (CAND-27).
  A limiter would keep full level when only one is playing. *First:* a
  listening comparison on the real card, since the author's doubling of
  game samples while no disc plays already answers half of it.
- **More in `UCDD -status`.** The sweep's hardest cases to read are the
  ones where a game simply exits. A last-error line for the DPMI host and
  the CD-ROM driver would turn a screenshot into a diagnosis. *First:*
  the list of exits from the sorting, to see what would have helped.
- **The DPMI host's start-up cost.** A DOS/4GW game's first sound comes
  about 2 s later under the driver than without it, and the fork's build
  is 0.86 s slower than the author's. *First:* find where the time goes;
  it may be the extender's own probing, not the host.
- **Reading ahead on the disc image.** A CD-audio game's first sound
  comes about a second later under the driver, and it moves with the
  disk's cluster size (CAND-23). *First:* the same measurement on the
  real PC's real disk.

Not planned: a mode that keeps the driver's sound for programs that need
VCPI (the author's design excludes it, for a reason); compressed audio
tracks; any tuning of the card's interrupt timing before the real card
has been measured.
