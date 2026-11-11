# References, credit and lineage

Written by Claude. As of 11 November 2026. What the work rests on, who is
owed credit, and how this fork relates to the project it came from.

## Upstream and lineage

**μCDD is vorvek's.** The driver, its design and nearly all of its code
are the work of the upstream author:
[github.com/vorvek/uCDD](https://github.com/vorvek/uCDD), GPL-3.0-only.
Every source file carries his copyright line. This fork is a derivative
under the same licence.

| Point | What |
|---|---|
| 0.9.3b, 29 September 2026 | The upstream release this fork started from. |
| 5 to 23 October 2026 | The fork's changes: 238 commits on its `count-position` line ([FEATURES.md](FEATURES.md), [HISTORY.md](HISTORY.md)). |
| 0.9.4-a6, 23 October | The upstream release the fork's feature branches are cut against. |
| 0.9.5-a1, 26 October | Tested by the harness's conformance tiers beside the fork's build. |
| 0.9.5-a2, 29 October | Tested by the conformance tiers again and by the sweep. |
| 0.9.5-a3, 7 November | Run on selected games. 47 commits past 0.9.3b. |

How the fork diverges:

- **What the fork has that upstream took in its own form.** Disk
  controller IRQs passed to DOS, stepping aside, and fast DMA exist
  upstream since 0.9.5-a2, written by the author. Upstream has also
  dropped Microsoft EMM386, as the fork had.
- **What the fork has that upstream does not.** The native ESS AudioDrive
  output path and the virtual ESS AudioDrive; `UCDD -status` and the
  interrupt counters; the fork's readings of the virtual Sound Blaster
  against Creative's documents ([FEATURES.md](FEATURES.md)).
- **What upstream has that the fork lacks.** Everything after 0.9.3b,
  among it nine fixes the harness has measured and the doubling of game
  samples while no disc plays ([KNOWN-ISSUES.md](KNOWN-ISSUES.md)).

The upstream author's compatibility list (his wiki) is the source of the
"known to work" games the calibration used.

## Documents

Rows cite documents by short keys (SBG, CT2290, VSB and others). The keys
are defined in the method package's
[`method.toml`](https://github.com/TrongDog/uCDD/blob/claude/brave-franklin-6h9xzo/method.toml),
under `[references.keys]`. Text copies of the documents themselves are on
the [`reference-library`](https://github.com/TrongDog/uCDD/tree/reference-library)
branch, in these groups:

| Group | Documents |
|---|---|
| Sound cards | The Sound Blaster family (Creative's hardware programming guide and card documents), the ESS AudioDrive data sheets (ES1868, ES1869, ES1878, ES1887, ES1888), the Windows Sound System codecs (CS4231A, CS4232), the FM chips. |
| Parts and specifications | The Intel 8237A DMA controller, 8259A interrupt controller and 82C54 timer; the 82C206; Intel's peripheral data books; the i386 reference. |
| Chipsets | The south bridges that hold the ISA bus and its DMA timing, from the 386 to the Pentium III (the PIIX family among them). |
| Memory managers and DOS extenders | DPMI 0.9 and 1.0, VCPI, XMS, EMS (LIM 4.0), Jemm. |
| CD-ROM | ISO 9660 (ECMA-119), the MSCDEX device driver interface, SHSUCDX. |
| Ralf Brown's Interrupt List | Release 61: interrupts, ports, CMOS, memory. |

For CD audio itself: the Red Book's 50/15 µs pre-emphasis curve, for the
de-emphasis test.

The fork's own specifications, written from those documents before the
code: on the `count-position` branch under
[`docs/`](https://github.com/TrongDog/uCDD/tree/count-position/docs)
(the virtual Sound Blasters, the virtual ESS, the DPMI host's CD-ROM
calls, platform DMA).

<details>
<summary>The 162 keys and their documents (method.toml <code>[references.keys]</code> on the method branch)</summary>

Each key names a file; the last column says on which branch of this repository it is, read on GitHub's branches on 11 November 2026. Most are on [`reference-library`](https://github.com/TrongDog/uCDD/tree/reference-library); the fork's own documents are on `notes` or `sound-engine-library`; a key whose file is on no branch here says so.

| Key | Document | Where |
|---|---|---|
| 1487 | Chipsets/486/M1487_M1489_486_PCI_Chip_Set_199707.txt | `reference-library` |
| 1523 | Chipsets/Pentium/M1523B_PCI_to_ISA_Bridge_199701.txt | `reference-library` |
| 1533 | Chipsets/Pentium/M1533_PCI_to_ISA_Bus_Bridge_v1.56_199811.txt | `reference-library` |
| 1535 | Chipsets/P6/M1535_South_Bridge_Product_Brief.txt | `reference-library` |
| 1535D | Chipsets/P6/M1535D+_South_Bridge_Product_Brief.txt | `reference-library` |
| 1543 | Chipsets/Pentium/M1543C_Desktop_Southbridge.txt | `reference-library` |
| 206 | Reference parts and specs/82C206_Integrated_Peripheral_Controller_199608.txt | `reference-library` |
| 4031 | Chipsets/486/CS4031_Chipset_F84031_F84035_199305.txt | `reference-library` |
| 460 | Chipsets/486/SiS_85C460.txt | `reference-library` |
| 471 | Chipsets/486/85C471_V6.0_199408.txt | `reference-library` |
| 496 | Chipsets/486/SiS_85C496-497_199507.txt | `reference-library` |
| 496G | Chipsets/486/VT82C496G_VT82C406MV_199504.txt | `reference-library` |
| 5582 | Chipsets/Pentium/SiS-5582_199704.txt | `reference-library` |
| 5595 | Chipsets/Pentium/SiS-5595_PCI_System_IO_199811.txt | `reference-library` |
| 5597 | Chipsets/Pentium/SiS-5597-5598_199704.txt | `reference-library` |
| 586A | Chipsets/Pentium/VT82C586A_PCI_Integrated_Periph_Ctlr_199610.txt | `reference-library` |
| 586B | Chipsets/Pentium/VT82C586B_PCI_Integrated_Periph_Ctlr_199705.txt | `reference-library` |
| 596B | Chipsets/Pentium/VT82C596B_South_Bridge_199906.txt | `reference-library` |
| 630 | Chipsets/P6/SiS-630_199910.txt | `reference-library` |
| 686A | Chipsets/P6/VT82C686A_Super_South_Bridge_V1.1_199904.txt | `reference-library` |
| 686B | Chipsets/P6/VT82C686B.txt | `reference-library` |
| 756 | Chipsets/Athlon/AMD-756_Peripheral_Bus_Controller_22548B_199908.txt | `reference-library` |
| 766 | Chipsets/Athlon/AMD-766_Peripheral_Bus_Controller_23167B_200103.txt | `reference-library` |
| 768 | Chipsets/Athlon/AMD-768_Peripheral_Bus_Controller_24467B_200110.txt | `reference-library` |
| 8231 | Chipsets/P6/VT8231_PC99_South_Bridge_199910.txt | `reference-library` |
| 8237 | Reference parts and specs/8237A.txt | `reference-library` |
| 8259 | Reference parts and specs/8259A.txt | `reference-library` |
| 82C206 | Reference parts and specs/82C206_Integrated_Peripheral_Controller_199608.txt | `reference-library` |
| AWE | Sound Cards/AWE32 and AWE64/adip301.txt | `reference-library` |
| CS4231A | Sound Cards/Windows Sound System/CS4231A_datasheet.txt | `reference-library` |
| CS4232 | Sound Cards/Windows Sound System/CS4232_datasheet.txt | `reference-library` |
| CT2290 | docs/sound-engines/ct2291.md | `sound-engine-library` |
| CT2291 | docs/sound-engines/ct2291.md | `sound-engine-library` |
| DOC_240843_001_82344_199010 | Chipsets/386/240843-001_82344_199010.txt | `reference-library` |
| DOC_241731_002_INTEL486_MICROPROCESSORS_AND_ | Chipsets/486/241731-002_Intel486_Microprocessors_and_Related_Products_1995.txt | `reference-library` |
| DOC_29055102 | Chipsets/Pentium/29055102.txt | `reference-library` |
| DOC_82C283_386SX_SYSTEM_CONTROLLER_199409 | Chipsets/386/82C283_386SX_System_Controller_199409.txt | `reference-library` |
| DOC_82C291_SXWB_PC_AT_CHIPSET_199410 | Chipsets/386/82C291_SXWB_PC_AT_Chipset_199410.txt | `reference-library` |
| DOC_82C491_82C392_OPTI_486WB_PC_AT_CHIPSET_1 | Chipsets/486/82C491_82C392_OPTi-486WB_PC_AT_Chipset_199104.txt | `reference-library` |
| DOC_82C493_392_206_OPTI_486SXWB_CHIPSET_1991 | Chipsets/486/82C493_392_206_OPTi-486SXWB_Chipset_199108.txt | `reference-library` |
| DOC_82C495XLC_82C206_PC_AT_CHIP_SET_199410 | Chipsets/486/82C495XLC_82C206_PC_AT_Chip_Set_199410.txt | `reference-library` |
| DOC_82C546_82C547_PYTHON_CHIPSET_MAY94 | Chipsets/Pentium/82C546_82C547_Python_Chipset_May94.txt | `reference-library` |
| DOC_82C681_EBC_682_MCC_686_ISP_687_DBC_OPTI_ | Chipsets/486/82C681_EBC_682_MCC_686_ISP_687_DBC_OPTi-368_486_EISA_Chipset.txt | `reference-library` |
| DOC_86BUGS | Ralf Brown's Interrupt List/86BUGS.LST | `reference-library` |
| DOC_AMD_750_CHIPSET_OVERVIEW_23016A_199908 | Chipsets/Athlon/AMD-750_Chipset_Overview_23016A_199908.txt | `reference-library` |
| DOC_AMD_756_REVISION_GUIDE_22591C_200005 | Chipsets/Athlon/AMD-756_Revision_Guide_22591C_200005.txt | `reference-library` |
| DOC_BIBLIO | Ralf Brown's Interrupt List/BIBLIO.LST | `reference-library` |
| DOC_CMOS | Ralf Brown's Interrupt List/CMOS.LST | `reference-library` |
| DOC_CS8221_NEAT_DATA_BOOK_198710 | Chipsets/386/CS8221_NEAT_Data_Book_198710.txt | `reference-library` |
| DOC_CS8230_CS8231_386AT_CHIPSETS_1989 | Chipsets/386/CS8230_CS8231_386AT_Chipsets_1989.txt | `reference-library` |
| DOC_FARCALL | Ralf Brown's Interrupt List/FARCALL.LST | `reference-library` |
| DOC_GLOSSARY | Ralf Brown's Interrupt List/GLOSSARY.LST | `reference-library` |
| DOC_I2C | Ralf Brown's Interrupt List/I2C.LST | `reference-library` |
| DOC_INTERRUP | Ralf Brown's Interrupt List/INTERRUP.A | `reference-library` |
| DOC_INTERRUP_ | Ralf Brown's Interrupt List/INTERRUP.B | `reference-library` |
| DOC_INTERRUP__ | Ralf Brown's Interrupt List/INTERRUP.C | `reference-library` |
| DOC_INTERRUP___ | Ralf Brown's Interrupt List/INTERRUP.D | `reference-library` |
| DOC_INTERRUP____ | Ralf Brown's Interrupt List/INTERRUP.E | `reference-library` |
| DOC_INTERRUP_____ | Ralf Brown's Interrupt List/INTERRUP.F | `reference-library` |
| DOC_INTERRUP______ | Ralf Brown's Interrupt List/INTERRUP.G | `reference-library` |
| DOC_INTERRUP_______ | Ralf Brown's Interrupt List/INTERRUP.H | `reference-library` |
| DOC_INTERRUP________ | Ralf Brown's Interrupt List/INTERRUP.I | `reference-library` |
| DOC_INTERRUP_________ | Ralf Brown's Interrupt List/INTERRUP.J | `reference-library` |
| DOC_INTERRUP__________ | Ralf Brown's Interrupt List/INTERRUP.K | `reference-library` |
| DOC_INTERRUP___________ | Ralf Brown's Interrupt List/INTERRUP.L | `reference-library` |
| DOC_INTERRUP____________ | Ralf Brown's Interrupt List/INTERRUP.M | `reference-library` |
| DOC_INTERRUP_____________ | Ralf Brown's Interrupt List/INTERRUP.N | `reference-library` |
| DOC_INTERRUP______________ | Ralf Brown's Interrupt List/INTERRUP.O | `reference-library` |
| DOC_INTERRUP_______________ | Ralf Brown's Interrupt List/INTERRUP.P | `reference-library` |
| DOC_INTERRUP________________ | Ralf Brown's Interrupt List/INTERRUP.PRI | `reference-library` |
| DOC_INTERRUP_________________ | Ralf Brown's Interrupt List/INTERRUP.Q | `reference-library` |
| DOC_INTERRUP__________________ | Ralf Brown's Interrupt List/INTERRUP.R | `reference-library` |
| DOC_MEMORY | Ralf Brown's Interrupt List/MEMORY.LST | `reference-library` |
| DOC_MSR | Ralf Brown's Interrupt List/MSR.LST | `reference-library` |
| DOC_OPCODES | Ralf Brown's Interrupt List/OPCODES.LST | `reference-library` |
| DOC_OVERVIEW | Ralf Brown's Interrupt List/OVERVIEW.LST | `reference-library` |
| DOC_PORTS | Ralf Brown's Interrupt List/PORTS.B | `reference-library` |
| DOC_PORTS_ | Ralf Brown's Interrupt List/PORTS.C | `reference-library` |
| DOC_SMM | Ralf Brown's Interrupt List/SMM.LST | `reference-library` |
| DOC_TABLES | Ralf Brown's Interrupt List/TABLES.LST | `reference-library` |
| DPMI09 | Memory managers and DOS extenders/1990_04_23-DPMI_Spec_v09.txt | `reference-library` |
| DPMI10 | Memory managers and DOS extenders/1991_03_12-DPMI_Spec_v10.txt | `reference-library` |
| ECMA119 | CD-ROM/ECMA-119_2nd_edition_december_1987.txt | `reference-library` |
| EISA | Reference parts and specs/eisabook.txt | `reference-library` |
| EMS | Memory managers and DOS extenders/LIM 4.0 Specs (EMS) · OpenRakis_Spice86 Wiki.txt | `reference-library` |
| EMU8K | Sound Cards/AWE32 and AWE64/emu8kpgm.txt | `reference-library` |
| EMUSRC | Sound Cards/Emulator and driver source/Emulator and driver source.txt | `reference-library` |
| ES1868 | Sound Cards/ESS AudioDrive/ESS_ES1868_Data_Sheet_1996.txt | `reference-library` |
| ES1869 | Sound Cards/ESS AudioDrive/DS1869.txt | `reference-library` |
| ES1869B | Sound Cards/ESS AudioDrive/DS1869_other_revision.txt | `reference-library` |
| ES1878 | Sound Cards/ESS AudioDrive/DS1878A.txt | `reference-library` |
| ES1887 | Sound Cards/ESS AudioDrive/ES1887_Data_Sheet_part_1_of_2.txt | `reference-library` |
| ES1887B | Sound Cards/ESS AudioDrive/ES1887_Data_Sheet_part_2_of_2.txt | `reference-library` |
| ES1888 | Sound Cards/ESS AudioDrive/ES1888_Design_Guide_1995-10_rev_C.txt | `reference-library` |
| ESC | Chipsets/Pentium/82374EB.txt | `reference-library` |
| FIRE | Chipsets/Pentium/82C700_Firestar_Single-Chip_Notebook_Solution_199702.txt | `reference-library` |
| HOSTCD | docs/host-cdrom-spec.md | `notes` |
| I386 | Reference parts and specs/i386.txt | `reference-library` |
| INTEL486_1995 | Chipsets/486/241731-002_Intel486_Microprocessors_and_Related_Products_1995.txt | `reference-library` |
| INTEL94 | Reference parts and specs/1994_Intel_Peripheral_Components.txt | `reference-library` |
| INTEL96 | Reference parts and specs/1996_Intel_Peripheral_Components.txt | `reference-library` |
| JEMM | Memory managers and DOS extenders/Jemm Readme.txt | `reference-library` |
| JR | Memory managers and DOS extenders/Jemm Readme.txt | `reference-library` |
| MISA | Chipsets/P6/290563-001_82380AB_199702.txt | `reference-library` |
| MSCDEX | CD-ROM/MSCDEX21.txt | `reference-library` |
| OPTI368 | Chipsets/486/82C681_EBC_682_MCC_686_ISP_687_DBC_OPTi-368_486_EISA_Chipset.txt | `reference-library` |
| PBOOK | Chipsets/Pentium/241732-003_Pentium_and_Pentium_Pro_Processors_and_Related_Products_1996.txt | `reference-library` |
| PCIBIOS | Reference parts and specs/PCI_BIOS_Specification_Revision_2.1_199408.txt | not on GitHub |
| PDMA | docs/platform-dma.md | `notes` |
| PEAK | Chipsets/386/82C351_355_356_PEAK_DM_prelim_199102.txt | `reference-library` |
| PIIX | Chipsets/Pentium/82371FB_82371SB_PIIX_PIIX3_datasheet_final.txt | `reference-library` |
| PIIX3 | Chipsets/Pentium/290550-001_82371FB_82371SB_PCI_ISA_IDE_Xcelerator_199605.txt | `reference-library` |
| PIIX4 | Chipsets/Pentium/290562_82371AB_PCI-TO-ISA_IDE_XCELERATOR_PIIX4_199704.txt | `reference-library` |
| PIIXp | Chipsets/Pentium/290550-001_82371FB_82371SB_PCI_ISA_IDE_Xcelerator_199605.txt | `reference-library` |
| PORTS | Ralf Brown's Interrupt List/PORTS.A | `reference-library` |
| PORTS_A | Ralf Brown's Interrupt List/PORTS.A | `reference-library` |
| PORTS_B | Ralf Brown's Interrupt List/PORTS.B | `reference-library` |
| PORTS_C | Ralf Brown's Interrupt List/PORTS.C | `reference-library` |
| QPI | Memory managers and DOS extenders/Jemm QPI (QPIEMU.txt, public domain).txt | `reference-library` |
| RBIL | Ralf Brown's Interrupt List/INTERRUP.1ST | `reference-library` |
| RBIL_A | Ralf Brown's Interrupt List/INTERRUP.A | `reference-library` |
| RBIL_B | Ralf Brown's Interrupt List/INTERRUP.B | `reference-library` |
| RBIL_C | Ralf Brown's Interrupt List/INTERRUP.C | `reference-library` |
| RBIL_D | Ralf Brown's Interrupt List/INTERRUP.D | `reference-library` |
| RBIL_E | Ralf Brown's Interrupt List/INTERRUP.E | `reference-library` |
| RBIL_F | Ralf Brown's Interrupt List/INTERRUP.F | `reference-library` |
| RBIL_G | Ralf Brown's Interrupt List/INTERRUP.G | `reference-library` |
| RBIL_H | Ralf Brown's Interrupt List/INTERRUP.H | `reference-library` |
| RBIL_I | Ralf Brown's Interrupt List/INTERRUP.I | `reference-library` |
| RBIL_J | Ralf Brown's Interrupt List/INTERRUP.J | `reference-library` |
| RBIL_K | Ralf Brown's Interrupt List/INTERRUP.K | `reference-library` |
| RBIL_L | Ralf Brown's Interrupt List/INTERRUP.L | `reference-library` |
| RBIL_M | Ralf Brown's Interrupt List/INTERRUP.M | `reference-library` |
| RBIL_N | Ralf Brown's Interrupt List/INTERRUP.N | `reference-library` |
| RBIL_O | Ralf Brown's Interrupt List/INTERRUP.O | `reference-library` |
| RBIL_P | Ralf Brown's Interrupt List/INTERRUP.P | `reference-library` |
| RBIL_PRI | Ralf Brown's Interrupt List/INTERRUP.PRI | `reference-library` |
| RBIL_Q | Ralf Brown's Interrupt List/INTERRUP.Q | `reference-library` |
| RBIL_R | Ralf Brown's Interrupt List/INTERRUP.R | `reference-library` |
| README | README.md | `reference-library` |
| SB202SPEC | Sound Cards/Superset references/Sb202Spec.md | not on GitHub |
| SBDK | Sound Cards/Superset references/Developer_Kit_SB_Series_Hardware_Programming_Reference.txt | `reference-library` |
| SBG | Sound Cards/Superset references/Sound_Blaster_Series_Hardware_Programming_Guide.txt | `reference-library` |
| SHSUCDX | CD-ROM/shsucdx.txt | `reference-library` |
| SIO | Chipsets/486/1993_Intel_82378_PCI-ISA_System_IO.txt | `reference-library` |
| SIO93 | Chipsets/486/1993_Intel_82378_PCI-ISA_System_IO.txt | `reference-library` |
| SIOZB | Chipsets/Pentium/290571-001_82378ZB_82379ZB_System_IO_and_System_IO_APIC_199603.txt | `reference-library` |
| SNDLIB | docs/sound-engines/findings.md | `sound-engine-library` |
| SPECFIRST | docs/spec-first.md | `notes` |
| UM82C206 | Reference parts and specs/UM82C206.txt | `reference-library` |
| UMC | Chipsets/486/UM8881_UM8886_HB4_Reverse_Engineered_20260216.txt | `reference-library` |
| VCPI | Memory managers and DOS extenders/Virtual Control Program Interface specification v1 - EDM2.txt | `reference-library` |
| VESS | docs/vess-spec.md | `notes` |
| VIPER | Chipsets/Pentium/Viper_Express+_BIOS_Programming_Guide_199701.txt | `reference-library` |
| VIPM | Chipsets/Pentium/82C556M_82C557M_82C558M_Viper-M_Preliminary_Data_Book_199504.txt | `reference-library` |
| VP | Chipsets/Pentium/VT82C580VP_Apollo_VP_199602.txt | `reference-library` |
| VSB | docs/vsb-spec.md | `notes` |
| vsb-spec | docs/vsb-spec.md | `notes` |
| XMS | Memory managers and DOS extenders/XMS35.txt | `reference-library` |
| XMS30 | Memory managers and DOS extenders/XMS30.txt | not on GitHub |
| YM3812 | Sound Cards/FM synthesis/Yamaha YM3812 Application Manual_text.txt | `reference-library` |
| YMF262 | Sound Cards/FM synthesis/YMF262_199411.txt | `reference-library` |

</details>

## Tools the work depends on

| Tool | Used for |
|---|---|
| [JemmEx](https://github.com/Baron-von-Riedesel/Jemm) | The memory manager the driver is designed for: XMS, VCPI, port traps. The pinned line's README asks for 5.86 or 5.87; the bench runs 5.86. |
| [SHSUCDX](http://adoxa.altervista.org/shsucdx/) | The CD redirector that gives the driver's device a drive letter. |
| [NASM](https://www.nasm.us) | The assembler. The bench uses 2.16.03. |
| [86Box](https://86box.net) | The emulator every result comes from. Version 6.0. |
| [DOSBox-X](https://dosbox-x.com) | The second emulator, as referee. Version 2025.02.01, the Linux distribution's package. |
| OpenAL | The sound path the bench's recorder sits on. |
| CuteMouse, S3VBE20, SetMul | DOS helpers the library's launchers expect, loaded as on the real PC. |
| Python 3 | The build script and every harness tool. |

## How these pages are organised

The split into learning, doing, looking up and understanding follows
[Diátaxis](https://diataxis.fr/). The decision records in
[DECISIONS.md](DECISIONS.md) follow the lightweight
[ADR](https://adr.github.io/) form.

## Authorship

Nearly all of this fork's changes were written by an AI (Claude); one
person directed and tested them, and made a few edits by hand in GitHub's
editor. The harness's method (its rules, its checks, the
rule that an instrument must first fail on purpose) is in the method
package and in [METHOD.md](METHOD.md).
