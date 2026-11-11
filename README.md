# μCDD fork: the notes branch

Written by Claude. This branch holds the working record of the fork's test
harness. It is not the place to start reading.

- **Start here instead:** the fork's front page and its `docs/` folder on
  the default branch,
  [`fixes`](https://github.com/TrongDog/uCDD/tree/fixes). The one-page
  state of the work is
  [docs/STATUS.md](https://github.com/TrongDog/uCDD/blob/fixes/docs/STATUS.md).
- **[ISSUES.md](ISSUES.md)** is the register: every candidate fault, every
  emulator difference and every bench setting as a row, in the order it
  was written, each with the document that decides it, the recorded runs
  that show it, and its hypothesis in a field of its own. A correction
  keeps the old text beside the new with its date. It is long.
- **[FIXED.md](FIXED.md)** is the index of fixes: which commit closed which
  row.
- **`docs/`** holds the specifications the fork wrote for itself before
  building (the virtual ESS, the DPMI host's CD-ROM calls, the platform
  DMA work).

Everything in the register was measured in an emulator unless its row
says otherwise.
