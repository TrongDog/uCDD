# The pages, by kind

Written by Claude. This is the index of every page in the fork's
documentation. The front page is [../README.md](../README.md); the page that
moves with the work is [STATUS.md](STATUS.md).

The pages are sorted by what a reader is trying to do, after the
[Diátaxis](https://diataxis.fr/) scheme: learning, doing, looking up,
understanding. A fifth group, the lab notebook, holds the experiments.

## Learn: start here and follow along

| Page | What you will have done at the end |
|---|---|
| [QUICKSTART.md](QUICKSTART.md) | Built the driver, installed it on a DOS machine, mounted a disc image and heard its music. |

## Do: one task at a time

| Page | For |
|---|---|
| [HOWTO.md](HOWTO.md) | Short recipes: several discs, a program that needs VCPI, an ESS card, reading the driver's counters, reading a row. |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | A symptom, its cause and what to do, for the driver and for anyone building a test bench like this one. |

## Look up: facts, tables, lists

| Page | Holds |
|---|---|
| [REFERENCE.md](REFERENCE.md) | The command line, build options, the settings file, hotkeys, image rules, the builds the harness tests, the bins and labels, a glossary. |
| [KNOWN-ISSUES.md](KNOWN-ISSUES.md) | The table of every candidate fault and which version of the driver has it. |
| [REFERENCES.md](REFERENCES.md) | Every document, data sheet and tool the work rests on, and the upstream lineage. |
| [../BUILDING.md](../BUILDING.md) | The upstream build page with the fork's additions: size limits and build options in full. |
| [../RELEASE-NOTES.md](../RELEASE-NOTES.md) | The upstream release notes, with the fork's changes to 20 October 2026. |

## Understand: why it is the way it is

| Page | Explains |
|---|---|
| [ARCHITECTURE.md](ARCHITECTURE.md) | The driver's parts, the harness's parts, the repository's branches, with diagrams and links into the source. |
| [METHOD.md](METHOD.md) | How a result is produced and what it is allowed to mean. |
| [BENCH.md](BENCH.md) | The emulated machine every number comes from, and what it cannot say. |
| [DECISIONS.md](DECISIONS.md) | The decisions that shaped the work, each with what was tried and dropped. |
| [FEATURES.md](FEATURES.md) | What the fork added to the driver and fixed in it before the harness, and how each was tested. |
| [HISTORY.md](HISTORY.md) | How the fork got here, in order. |
| [PLANS.md](PLANS.md) | What happens next, and the ideas after that. |

## The lab notebook: experiments and their results

| Page | Holds |
|---|---|
| [EXPERIMENTS.md](EXPERIMENTS.md) | Every experiment as question, test, result and conclusion, newest last, with links to the long write-ups. |
| [CALIBRATION.md](CALIBRATION.md) | The long write-up of the calibration on 84 known games. |
| [SWEEP.md](SWEEP.md) | The long write-up of the 838-game sweep. |
| [FINDINGS.md](FINDINGS.md) | Each candidate fault in a paragraph, with its hypothesis where there is one. |

## The state of the work

| Page | Holds |
|---|---|
| [STATUS.md](STATUS.md) | Where the work stands, stage by stage. Updated at every step. |
| [../ISSUES.md](../ISSUES.md) | The fork's state as written on 20 October 2026, before the harness. Kept as it was. |

## Rules these pages keep

1. A page is a view of the rows in
   [ISSUES.md on `notes`](https://github.com/TrongDog/uCDD/blob/notes/ISSUES.md).
   Where a page and a row disagree, the row is right and the page is
   corrected.
2. A number is stated on one page, the one that owns it, and other pages
   link there. The stage of the work belongs to STATUS, the candidates to
   KNOWN-ISSUES, a build's identity to REFERENCE.
3. Every page says the day its facts were read ("As of ...").
4. A hypothesis is written under the word *Hypothesis* and never as a
   finding. A hypothesis that turned out wrong stays, dated.
5. A gap is written as `[TODO: what is missing]`, never papered over.
6. Nothing is confirmed on real hardware until a person has run it there,
   and no page says otherwise.

