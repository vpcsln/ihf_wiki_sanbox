# Source map for the SDR wiki documentation set

Use this file to verify technical edits before copying them to the IHF Wiki. It is a maintenance aid and is not intended for publication.

## Authority order

1. Current manufacturer specifications for safety limits and device behavior.
2. Confirmed project facts and current hardware configuration.
3. Current repository code and maintenance documentation for implemented behavior.
4. Architecture and literature documents for context and planned evaluation.
5. Historical files and backups only for provenance; they do not override current facts.

## SDR hub

| Topic | Source |
|---|---|
| General UHD role and USRP data path | [UHD and USRP manual](https://files.ettus.com/manual/) |
| GNU Radio concepts and blocks | [GNU Radio Wiki](https://wiki.gnuradio.org/) |
| Hardware and project navigation | The two linked local `.wiki` pages |

Keep this page general. Do not copy project-specific parameters, results, or long setup instructions into it.

## NI USRP-2954R and UBX-160

| Topic | Source |
|---|---|
| Channel count, frequency range, gain, bandwidth, sample rate, and -15 dBm input limit | [NI USRP-2954 specifications](https://download.ni.com/support/manuals/375725c.pdf) |
| `TX/RX`, `RX2`, full-duplex behavior, LO-lock sensor, and UBX details | [Ettus UBX documentation](https://kb.ettus.com/UBX) |
| XG image and X300 networking | [UHD X300/X310 documentation](https://files.ettus.com/manual/page_usrp_x3x0.html) |
| Ubuntu, UHD/GNU Radio installation, IP addresses, MTU, and socket buffers | `Docs/Hardware_setup.md` |
| 200 MHz master clock and 100 MS/s hardware-test rate | `project_facts.txt` and `jcas-ofdm/docs/First_tests.md` |
| Measurement logging and conservative -20 dBm receiver-test ceiling | `jcas-ofdm/docs/First_tests.md` |

Never replace a manufacturer limit with a measured or convenient operating value. State conservative project ceilings separately.

## OFDM-based JCAS project

| Topic | Source |
|---|---|
| Repository entry points and maintenance rules | `jcas-ofdm/MAINTENANCE.md` |
| Current simulation topology and defaults | `jcas-ofdm/Flow_graphs/OFDMJCAS.grc`, launchers, and repository `README.md` |
| OFDM transmitter, receiver, synchronization, and equalization | `jcas-ofdm/Flow_graphs/OFDMJCAStxrx.py` |
| CFR, CIR, and DDM visualization | `jcas-ofdm/Plots/` and embedded blocks in the primary GRC file |
| Hardware and RF verification sequence | `jcas-ofdm/docs/First_tests.md` |
| Quasi-bistatic automotive architecture and second receive node | `Docs/System-level architecture.docx` |
| Communication and sensing evaluation quantities | `Docs/SoA analysis.docx` and `Docs/Second biweekly update.docx` |

Important distinctions:

- The main repository flowgraph is a channel-model simulation and does not contain a UHD hardware source or sink.
- The default simulation rate is 100 kS/s; the initial hardware RF tests use 100 MS/s with a 200 MHz master clock.
- BER, CFR, CIR, and DDM are current outputs. Other figures of merit are evaluation quantities and must not be described as implemented until the code and results support that claim.
- Detailed procedures and test status belong in the repository; the wiki page should remain a stable overview.

## Pre-publication review

- Confirm every number against the source above.
- Compare the wiki description with the current `main` branch, not a generated or backup file.
- Regenerate local previews and inspect navigation, tables, commands, and categories.
- Use **Vorschau zeigen** on the live wiki for the exact MediaWiki rendering.
- Publish manually with an explicit edit summary only after review.
