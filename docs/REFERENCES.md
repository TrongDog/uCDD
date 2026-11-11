# References, credit and lineage

Written by Claude. As of 10 November 2026. What the work rests on, who is
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
- **Nothing from this fork has been sent upstream**
  ([DECISIONS.md](DECISIONS.md#d-04-findings-stay-in-this-repository)).

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

Each key names a file on the [`reference-library`](https://github.com/TrongDog/uCDD/tree/reference-library) branch; the file name carries the title and, where it has one, the edition or year.

| Key | Document |
|---|---|
| 1487 | Chipsets/486/M1487_M1489_486_PCI_Chip_Set_199707.txt |
| 1523 | Chipsets/Pentium/M1523B_PCI_to_ISA_Bridge_199701.txt |
| 1533 | Chipsets/Pentium/M1533_PCI_to_ISA_Bus_Bridge_v1.56_199811.txt |
| 1535 | Chipsets/P6/M1535_South_Bridge_Product_Brief.txt |
| 1535D | Chipsets/P6/M1535D+_South_Bridge_Product_Brief.txt |
| 1543 | Chipsets/Pentium/M1543C_Desktop_Southbridge.txt |
| 206 | Reference parts and specs/82C206_Integrated_Peripheral_Controller_199608.txt |
| 4031 | Chipsets/486/CS4031_Chipset_F84031_F84035_199305.txt |
| 460 | Chipsets/486/SiS_85C460.txt |
| 471 | Chipsets/486/85C471_V6.0_199408.txt |
| 496 | Chipsets/486/SiS_85C496-497_199507.txt |
| 496G | Chipsets/486/VT82C496G_VT82C406MV_199504.txt |
| 5582 | Chipsets/Pentium/SiS-5582_199704.txt |
| 5595 | Chipsets/Pentium/SiS-5595_PCI_System_IO_199811.txt |
| 5597 | Chipsets/Pentium/SiS-5597-5598_199704.txt |
| 586A | Chipsets/Pentium/VT82C586A_PCI_Integrated_Periph_Ctlr_199610.txt |
| 586B | Chipsets/Pentium/VT82C586B_PCI_Integrated_Periph_Ctlr_199705.txt |
| 596B | Chipsets/Pentium/VT82C596B_South_Bridge_199906.txt |
| 630 | Chipsets/P6/SiS-630_199910.txt |
| 686A | Chipsets/P6/VT82C686A_Super_South_Bridge_V1.1_199904.txt |
| 686B | Chipsets/P6/VT82C686B.txt |
| 756 | Chipsets/Athlon/AMD-756_Peripheral_Bus_Controller_22548B_199908.txt |
| 766 | Chipsets/Athlon/AMD-766_Peripheral_Bus_Controller_23167B_200103.txt |
| 768 | Chipsets/Athlon/AMD-768_Peripheral_Bus_Controller_24467B_200110.txt |
| 8231 | Chipsets/P6/VT8231_PC99_South_Bridge_199910.txt |
| 8237 | Reference parts and specs/8237A.txt |
| 8259 | Reference parts and specs/8259A.txt |
| 82C206 | Reference parts and specs/82C206_Integrated_Peripheral_Controller_199608.txt |
| AWE | Sound Cards/AWE32 and AWE64/adip301.txt |
| CS4231A | Sound Cards/Windows Sound System/CS4231A_datasheet.txt |
| CS4232 | Sound Cards/Windows Sound System/CS4232_datasheet.txt |
| CT2290 | docs/sound-engines/ct2291.md |
| CT2291 | docs/sound-engines/ct2291.md |
| DOC_240843_001_82344_199010 | Chipsets/386/240843-001_82344_199010.txt |
| DOC_241731_002_INTEL486_MICROPROCESSORS_AND_ | Chipsets/486/241731-002_Intel486_Microprocessors_and_Related_Products_1995.txt |
| DOC_29055102 | Chipsets/Pentium/29055102.txt |
| DOC_82C283_386SX_SYSTEM_CONTROLLER_199409 | Chipsets/386/82C283_386SX_System_Controller_199409.txt |
| DOC_82C291_SXWB_PC_AT_CHIPSET_199410 | Chipsets/386/82C291_SXWB_PC_AT_Chipset_199410.txt |
| DOC_82C491_82C392_OPTI_486WB_PC_AT_CHIPSET_1 | Chipsets/486/82C491_82C392_OPTi-486WB_PC_AT_Chipset_199104.txt |
| DOC_82C493_392_206_OPTI_486SXWB_CHIPSET_1991 | Chipsets/486/82C493_392_206_OPTi-486SXWB_Chipset_199108.txt |
| DOC_82C495XLC_82C206_PC_AT_CHIP_SET_199410 | Chipsets/486/82C495XLC_82C206_PC_AT_Chip_Set_199410.txt |
| DOC_82C546_82C547_PYTHON_CHIPSET_MAY94 | Chipsets/Pentium/82C546_82C547_Python_Chipset_May94.txt |
| DOC_82C681_EBC_682_MCC_686_ISP_687_DBC_OPTI_ | Chipsets/486/82C681_EBC_682_MCC_686_ISP_687_DBC_OPTi-368_486_EISA_Chipset.txt |
| DOC_86BUGS | Ralf Brown's Interrupt List/86BUGS.LST |
| DOC_AMD_750_CHIPSET_OVERVIEW_23016A_199908 | Chipsets/Athlon/AMD-750_Chipset_Overview_23016A_199908.txt |
| DOC_AMD_756_REVISION_GUIDE_22591C_200005 | Chipsets/Athlon/AMD-756_Revision_Guide_22591C_200005.txt |
| DOC_BIBLIO | Ralf Brown's Interrupt List/BIBLIO.LST |
| DOC_CMOS | Ralf Brown's Interrupt List/CMOS.LST |
| DOC_CS8221_NEAT_DATA_BOOK_198710 | Chipsets/386/CS8221_NEAT_Data_Book_198710.txt |
| DOC_CS8230_CS8231_386AT_CHIPSETS_1989 | Chipsets/386/CS8230_CS8231_386AT_Chipsets_1989.txt |
| DOC_FARCALL | Ralf Brown's Interrupt List/FARCALL.LST |
| DOC_GLOSSARY | Ralf Brown's Interrupt List/GLOSSARY.LST |
| DOC_I2C | Ralf Brown's Interrupt List/I2C.LST |
| DOC_INTERRUP | Ralf Brown's Interrupt List/INTERRUP.A |
| DOC_INTERRUP_ | Ralf Brown's Interrupt List/INTERRUP.B |
| DOC_INTERRUP__ | Ralf Brown's Interrupt List/INTERRUP.C |
| DOC_INTERRUP___ | Ralf Brown's Interrupt List/INTERRUP.D |
| DOC_INTERRUP____ | Ralf Brown's Interrupt List/INTERRUP.E |
| DOC_INTERRUP_____ | Ralf Brown's Interrupt List/INTERRUP.F |
| DOC_INTERRUP______ | Ralf Brown's Interrupt List/INTERRUP.G |
| DOC_INTERRUP_______ | Ralf Brown's Interrupt List/INTERRUP.H |
| DOC_INTERRUP________ | Ralf Brown's Interrupt List/INTERRUP.I |
| DOC_INTERRUP_________ | Ralf Brown's Interrupt List/INTERRUP.J |
| DOC_INTERRUP__________ | Ralf Brown's Interrupt List/INTERRUP.K |
| DOC_INTERRUP___________ | Ralf Brown's Interrupt List/INTERRUP.L |
| DOC_INTERRUP____________ | Ralf Brown's Interrupt List/INTERRUP.M |
| DOC_INTERRUP_____________ | Ralf Brown's Interrupt List/INTERRUP.N |
| DOC_INTERRUP______________ | Ralf Brown's Interrupt List/INTERRUP.O |
| DOC_INTERRUP_______________ | Ralf Brown's Interrupt List/INTERRUP.P |
| DOC_INTERRUP________________ | Ralf Brown's Interrupt List/INTERRUP.PRI |
| DOC_INTERRUP_________________ | Ralf Brown's Interrupt List/INTERRUP.Q |
| DOC_INTERRUP__________________ | Ralf Brown's Interrupt List/INTERRUP.R |
| DOC_MEMORY | Ralf Brown's Interrupt List/MEMORY.LST |
| DOC_MSR | Ralf Brown's Interrupt List/MSR.LST |
| DOC_OPCODES | Ralf Brown's Interrupt List/OPCODES.LST |
| DOC_OVERVIEW | Ralf Brown's Interrupt List/OVERVIEW.LST |
| DOC_PORTS | Ralf Brown's Interrupt List/PORTS.B |
| DOC_PORTS_ | Ralf Brown's Interrupt List/PORTS.C |
| DOC_SMM | Ralf Brown's Interrupt List/SMM.LST |
| DOC_TABLES | Ralf Brown's Interrupt List/TABLES.LST |
| DPMI09 | Memory managers and DOS extenders/1990_04_23-DPMI_Spec_v09.txt |
| DPMI10 | Memory managers and DOS extenders/1991_03_12-DPMI_Spec_v10.txt |
| ECMA119 | CD-ROM/ECMA-119_2nd_edition_december_1987.txt |
| EISA | Reference parts and specs/eisabook.txt |
| EMS | Memory managers and DOS extenders/LIM 4.0 Specs (EMS) · OpenRakis_Spice86 Wiki.txt |
| EMU8K | Sound Cards/AWE32 and AWE64/emu8kpgm.txt |
| EMUSRC | Sound Cards/Emulator and driver source/Emulator and driver source.txt |
| ES1868 | Sound Cards/ESS AudioDrive/ESS_ES1868_Data_Sheet_1996.txt |
| ES1869 | Sound Cards/ESS AudioDrive/DS1869.txt |
| ES1869B | Sound Cards/ESS AudioDrive/DS1869_other_revision.txt |
| ES1878 | Sound Cards/ESS AudioDrive/DS1878A.txt |
| ES1887 | Sound Cards/ESS AudioDrive/ES1887_Data_Sheet_part_1_of_2.txt |
| ES1887B | Sound Cards/ESS AudioDrive/ES1887_Data_Sheet_part_2_of_2.txt |
| ES1888 | Sound Cards/ESS AudioDrive/ES1888_Design_Guide_1995-10_rev_C.txt |
| ESC | Chipsets/Pentium/82374EB.txt |
| FIRE | Chipsets/Pentium/82C700_Firestar_Single-Chip_Notebook_Solution_199702.txt |
| HOSTCD | docs/host-cdrom-spec.md |
| I386 | Reference parts and specs/i386.txt |
| INTEL486_1995 | Chipsets/486/241731-002_Intel486_Microprocessors_and_Related_Products_1995.txt |
| INTEL94 | Reference parts and specs/1994_Intel_Peripheral_Components.txt |
| INTEL96 | Reference parts and specs/1996_Intel_Peripheral_Components.txt |
| JEMM | Memory managers and DOS extenders/Jemm Readme.txt |
| JR | Memory managers and DOS extenders/Jemm Readme.txt |
| MISA | Chipsets/P6/290563-001_82380AB_199702.txt |
| MSCDEX | CD-ROM/MSCDEX21.txt |
| OPTI368 | Chipsets/486/82C681_EBC_682_MCC_686_ISP_687_DBC_OPTi-368_486_EISA_Chipset.txt |
| PBOOK | Chipsets/Pentium/241732-003_Pentium_and_Pentium_Pro_Processors_and_Related_Products_1996.txt |
| PCIBIOS | Reference parts and specs/PCI_BIOS_Specification_Revision_2.1_199408.txt |
| PDMA | docs/platform-dma.md |
| PEAK | Chipsets/386/82C351_355_356_PEAK_DM_prelim_199102.txt |
| PIIX | Chipsets/Pentium/82371FB_82371SB_PIIX_PIIX3_datasheet_final.txt |
| PIIX3 | Chipsets/Pentium/290550-001_82371FB_82371SB_PCI_ISA_IDE_Xcelerator_199605.txt |
| PIIX4 | Chipsets/Pentium/290562_82371AB_PCI-TO-ISA_IDE_XCELERATOR_PIIX4_199704.txt |
| PIIXp | Chipsets/Pentium/290550-001_82371FB_82371SB_PCI_ISA_IDE_Xcelerator_199605.txt |
| PORTS | Ralf Brown's Interrupt List/PORTS.A |
| PORTS_A | Ralf Brown's Interrupt List/PORTS.A |
| PORTS_B | Ralf Brown's Interrupt List/PORTS.B |
| PORTS_C | Ralf Brown's Interrupt List/PORTS.C |
| QPI | Memory managers and DOS extenders/Jemm QPI (QPIEMU.txt, public domain).txt |
| RBIL | Ralf Brown's Interrupt List/INTERRUP.1ST |
| RBIL_A | Ralf Brown's Interrupt List/INTERRUP.A |
| RBIL_B | Ralf Brown's Interrupt List/INTERRUP.B |
| RBIL_C | Ralf Brown's Interrupt List/INTERRUP.C |
| RBIL_D | Ralf Brown's Interrupt List/INTERRUP.D |
| RBIL_E | Ralf Brown's Interrupt List/INTERRUP.E |
| RBIL_F | Ralf Brown's Interrupt List/INTERRUP.F |
| RBIL_G | Ralf Brown's Interrupt List/INTERRUP.G |
| RBIL_H | Ralf Brown's Interrupt List/INTERRUP.H |
| RBIL_I | Ralf Brown's Interrupt List/INTERRUP.I |
| RBIL_J | Ralf Brown's Interrupt List/INTERRUP.J |
| RBIL_K | Ralf Brown's Interrupt List/INTERRUP.K |
| RBIL_L | Ralf Brown's Interrupt List/INTERRUP.L |
| RBIL_M | Ralf Brown's Interrupt List/INTERRUP.M |
| RBIL_N | Ralf Brown's Interrupt List/INTERRUP.N |
| RBIL_O | Ralf Brown's Interrupt List/INTERRUP.O |
| RBIL_P | Ralf Brown's Interrupt List/INTERRUP.P |
| RBIL_PRI | Ralf Brown's Interrupt List/INTERRUP.PRI |
| RBIL_Q | Ralf Brown's Interrupt List/INTERRUP.Q |
| RBIL_R | Ralf Brown's Interrupt List/INTERRUP.R |
| README | README.md |
| SB202SPEC | Sound Cards/Superset references/Sb202Spec.md |
| SBDK | Sound Cards/Superset references/Developer_Kit_SB_Series_Hardware_Programming_Reference.txt |
| SBG | Sound Cards/Superset references/Sound_Blaster_Series_Hardware_Programming_Guide.txt |
| SHSUCDX | CD-ROM/shsucdx.txt |
| SIO | Chipsets/486/1993_Intel_82378_PCI-ISA_System_IO.txt |
| SIO93 | Chipsets/486/1993_Intel_82378_PCI-ISA_System_IO.txt |
| SIOZB | Chipsets/Pentium/290571-001_82378ZB_82379ZB_System_IO_and_System_IO_APIC_199603.txt |
| SNDLIB | docs/sound-engines/findings.md |
| SPECFIRST | docs/spec-first.md |
| UM82C206 | Reference parts and specs/UM82C206.txt |
| UMC | Chipsets/486/UM8881_UM8886_HB4_Reverse_Engineered_20260216.txt |
| VCPI | Memory managers and DOS extenders/Virtual Control Program Interface specification v1 - EDM2.txt |
| VESS | docs/vess-spec.md |
| VIPER | Chipsets/Pentium/Viper_Express+_BIOS_Programming_Guide_199701.txt |
| VIPM | Chipsets/Pentium/82C556M_82C557M_82C558M_Viper-M_Preliminary_Data_Book_199504.txt |
| VP | Chipsets/Pentium/VT82C580VP_Apollo_VP_199602.txt |
| VSB | docs/vsb-spec.md |
| vsb-spec | docs/vsb-spec.md |
| XMS | Memory managers and DOS extenders/XMS35.txt |
| XMS30 | Memory managers and DOS extenders/XMS30.txt |
| YM3812 | Sound Cards/FM synthesis/Yamaha YM3812 Application Manual_text.txt |
| YMF262 | Sound Cards/FM synthesis/YMF262_199411.txt |

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
