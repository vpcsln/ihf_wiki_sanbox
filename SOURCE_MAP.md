# Source and claim ledger for the SDR wiki set

This is the internal verification record for the three public wiki drafts. It is not intended for publication. The public pages deliberately omit local working-document names and defer changing procedures and results to the project repository.

## Verified baseline

| Source set | Revision or snapshot used |
|---|---|
| `jcas-ofdm` repository | `b95f0c49f7e54ba10c93670933c3e0a7c48c805d` (`Improved Test 2B`) |
| Existing IHF SDR wiki page | revision 7595, 2026-07-14 14:28:38 UTC |
| IHF example-page corpus | 78 deduplicated latest revisions fetched 2026-08-12; hashes verified |
| NI USRP-2954R specification | NI document 375725C |
| Ettus UBX documentation | current page checked 2026-08-12 |
| UHD X300/X310 documentation | current manual checked 2026-08-12 |
| Local project documents | every PDF, DOCX, PPTX, and the duplicate documentation archive under the project workspace was inventoried and text-extracted where applicable |

Recheck current manufacturer limits and current repository code before publication if this baseline changes.

## Authority order

1. Manufacturer specifications and instrument manuals govern absolute hardware and safety limits.
2. Current source-of-truth repository files govern implemented software behaviour.
3. Current repository maintenance and test documents govern workflow and documented test status.
4. Project architecture, progress, analysis, and thesis documents provide intent, context, and planned evaluation.
5. Historical Word files, generated code, archived copies, and older descriptive text provide provenance only. They do not override current code or current documentation.

When two sources use the same term for different quantities, preserve the distinction instead of selecting a convenient value. Examples include the NI system RX gain range versus the UBX gain-stage range, the launcher simulation rate versus the hardware-test rate, and a displayed FFT level versus calibrated input power.

## Public page boundaries

| Page | Owns | Must not become |
|---|---|---|
| `Software Defined Radio (SDR)` | Short definition, signal chain, software stack, hierarchy, general RF practice | A second hardware manual or project README |
| `NI USRP-2954R` | Stable device facts, installed configuration, networking, startup checks, connector behaviour, safety, troubleshooting | A copy of the JCAS test plan |
| `OFDM-based Joint Communication and Sensing (JCAS)` | Project purpose, intended architecture, implemented graph, parameter context, repository map, status and interpretation limits | A claim that incomplete hardware or sensing work is finished |

The IHF main namespace has subpages disabled. The hierarchy is therefore expressed by page titles, a three-cell navigation table, and explicit links rather than slash-based titles.

## Claim ledger: SDR hub

| Public claim | Verification source | Result |
|---|---|---|
| SDR moves modulation, filtering, synchronisation, and demodulation into software around a configurable RF front end | GNU Radio documentation and UHD/USRP architecture documentation | Supported as a concise general description |
| Typical receive and transmit paths include RF front end, converters, FPGA, host interface, and host application | NI block diagram and UHD manuals | Supported |
| End-to-end rate and bandwidth depend on every part of the chain | NI specifications and UHD streaming documentation | Supported |
| IHF platform is a USRP-2954R with two UBX-160 daughterboards and dual 10GbE | project hardware setup, test plan, NI/Ettus device documentation | Supported |
| Current software stack uses UHD, GNU Radio, Python, and Git | project repository and hardware setup | Supported |
| General RF cautions | NI input limit, instrument manuals, current test plan | Supported; device-specific numerical limit stays on the hardware page |

## Claim ledger: NI USRP-2954R

| Public claim | Verification source | Result or qualification |
|---|---|---|
| 2 TX and 2 RX channels; 10 MHz to 6 GHz | NI USRP-2954 specifications | Supported |
| Maximum real-time bandwidth 160 MHz; RX 84 MHz below 500 MHz | NI USRP-2954 specifications | Supported with the low-frequency qualification retained |
| Maximum I/Q rate 200 MS/s | NI USRP-2954 specifications | Supported |
| TX gain 0–31.5 dB and RX gain 0–37.5 dB, both in 0.5 dB steps | NI USRP-2954 specifications | Supported as system specifications |
| 16-bit DAC, 14-bit ADC, 50-ohm RF impedance | NI USRP-2954 specifications | Supported |
| Maximum RX input is -15 dBm | NI USRP-2954 specifications | Supported as an absolute limit, not a target |
| UBX-160 is full duplex with independent TX and RX LOs | Ettus UBX documentation | Supported |
| TX/RX can transmit or receive; RX2 is receive-only; full duplex receives on RX2 | Ettus UBX documentation | Supported |
| System gain and UBX gain-stage figures differ | NI specification compared with Ettus UBX page | Difference retained; public text tells operators to query UHD |
| Integrated GPS-disciplined oscillator and reference/PPS facilities are available | NI USRP-2954 specifications | Supported; public text does not claim the project currently uses them |
| Ubuntu 24.04, source-built UHD, GNU Radio 3.10, XG image | local hardware setup | Supported as the recorded project-host configuration, not a universal requirement |
| Interface names `enp1s0f0np0` and `enp1s0f1np1` | local hardware setup | Supported but explicitly marked as names that may change |
| Host/USRP addresses `.30.1/.30.2` and `.40.1/.40.2`, MTU 9000, socket buffers 24912805 | local hardware setup and current test plan | Supported |
| XG provides two 10GbE interfaces | UHD X300/X310 manual | Supported |
| 200 MHz master clock and requested 100 MS/s for initial RF work | current test plan and confirmed project facts | Supported; kept separate from the simulation rate |
| Both daughterboards checked as transmitters and receivers near 5.8 GHz | current test plan | Supported as status only; public text does not invent results or assign roles |
| Project receiver ceiling -20 dBm | current receiver test plan | Supported as a conservative project ceiling below NI's -15 dBm maximum |
| No Throttle block in hardware path | GNU Radio/UHD operation and current test plan | Supported |
| Reflashing is maintenance, not routine startup | UHD X300/X310 manual and setup process | Supported |

## Claim ledger: OFDM-based JCAS

### Architecture and status

| Public claim | Verification source | Result or qualification |
|---|---|---|
| Shared OFDM waveform supports communication and channel-based sensing | project architecture, state-of-the-art analysis, thesis summary, main graph | Supported as project purpose |
| Planned primary node uses separate daughterboards for TX and sensing RX; a second USRP receives communication | system-level architecture and project updates | Supported as intended architecture; the second device's exact configuration is not asserted |
| Main graph is a software channel-model simulation with no UHD Source or Sink | `Flow_graphs/OFDMJCAS.grc` | Confirmed |
| Streaming and pure communication hardware work were performed | current `docs/First_tests.md` | Supported as project-record status; quantitative success is not inferred |
| Both TX and RX daughterboard checks were performed | current `docs/First_tests.md` | Supported; detailed RX settings/results remain unavailable |
| Inter-daughterboard synchronisation test not performed | current `docs/First_tests.md` | Confirmed |
| Static sensing and joint OTA procedures lack documented completion results | current `docs/First_tests.md` and repository result inventory | Confirmed; described as planned/unvalidated |
| No CFAR or target detector in current graph | current GRC and Python source search | Confirmed |
| TDoA was investigated but not implemented | project analysis documents and current code search | Kept out of the public overview because it is not needed to explain current behaviour |

### Implemented OFDM chain

| Public claim | Verification source | Result or qualification |
|---|---|---|
| Reference payload is seven ramps of bytes 0–255, 1792 bytes total | launchers and `OFDMJCAS.grc` vector/tagged-stream settings | Confirmed |
| FFT length 128, active-carrier parameter 127 | `N_FFT=N+1`, launcher `N=127`, carrier maps | Confirmed |
| 115 data carriers plus 12 pilots; Nyquist bin omitted | exact occupied and pilot tuples in main GRC | Confirmed by counting the tuples |
| Pilot bins are -55 through 55 in steps of 10; pilot values all 1 | exact main GRC tuples | Confirmed; older README text implying a step of 5 is not used |
| Header and payload are QPSK; scrambling disabled | custom block parameters in main GRC | Confirmed |
| First preamble is Zadoff–Chu on alternating active carriers, producing repeated halves | `_make_sync_word1` in `OFDMJCAStxrx.py` | Confirmed without relying on ambiguous odd/even naming |
| Second preamble is fixed-seed BPSK | `_make_sync_word2` and seed 42 in `OFDMJCAStxrx.py` | Confirmed |
| Channel model direct path, delayed paths, source amplitudes/frequencies, and Gaussian noise values | exact blocks and connections in `Channel_Model.grc` | Confirmed; public wording states the literal block sequence rather than collapsing effective gains |
| Channel hierarchy has its own fixed 100 kS/s parameter | `Channel_Model.grc` | Confirmed and called out as a coupling risk |
| Receiver has two inputs and three outputs | Python `gr.io_signature`, main GRC connections, and Linux launcher's temporary definition repair | Confirmed; committed block definition omits the float input and older README states four outputs |
| Synchroniser falling-edge threshold 0.996 | receiver constructor in `OFDMJCAStxrx.py` | Confirmed |
| Fine-frequency correction input is constant zero in the main graph | main GRC connection from Analog Constant Source | Confirmed |
| DFE adaptation factor is 0.1 | header/payload equaliser construction | Confirmed for payload equalisation paths |
| BER matches PDU packets by `packet_num` and reports a cumulative compared-bit ratio | embedded BER block in main GRC | Confirmed; public limitation about missing/unmatched packets added |
| CFR is computed as scaled unequalised active symbols divided by softly equalised active symbols | receiver ports and main GRC multiply/vector/divide connections | Confirmed; expression uses `(Y/N)/X_est` |
| CIR is an orthonormal IFFT along subcarriers | embedded CFR-to-CIR block | Confirmed |
| DDM applies windowing, zero-padding, subcarrier IFFT, symbol FFT, and magnitude squared | embedded matrix block and downstream connection | Confirmed |
| Resolution factor is zero-padding/display sampling, not new physical resolution | implementation and standard Fourier interpretation | Supported |
| CFR and CIR visualisers receive only real parts | complex-to-real blocks and ZMQ connections | Confirmed |
| DDM dB and linear publishers both receive magnitude squared; dB conversion occurs in the subscriber | main GRC and plot scripts | Confirmed |
| ZMQ ports 5555/5556/5557/5558 map to DDM dB input/DDM linear/CFR/CIR | GRC and plot-script constants | Confirmed |
| All ZMQ interfaces use loopback | addresses in GRC and plot scripts | Confirmed |
| Launcher omits `f_c`; plot then calculates frequency spacing but labels the axis velocity | launcher arguments and both DDM scripts | Confirmed as an implementation limitation, not silently presented as velocity |

### Parameters and execution

| Public claim | Verification source | Result or qualification |
|---|---|---|
| Both launchers use 100000, N=127, M=63, M_crop=62, range=256, CP=48, resolution=4, ramps=7 | `Simulation_starter.sh` and `.bat` | Confirmed |
| Raw GRC defaults differ (10000, M=5, M_crop=4, CP=4) | parameter fields in `OFDMJCAS.grc` | Confirmed; public page identifies launchers as reference configuration |
| Reference GNU Radio version is 3.10.12.0 | `MAINTENANCE.md`, GRC metadata, README | Confirmed as project reference, not latest general release |
| Required Python packages include NumPy, SciPy, pyzmq, PyQt5, pyqtgraph, SIP | Linux preflight and maintenance guide | Confirmed |
| Linux launcher supports `--check` and `--no-diagnostics` | `Simulation_starter.sh` | Confirmed |
| Committed custom-block definitions retain legacy IDs/classes and omit the receiver float input | block-definition files and Linux temporary rewrite function | Confirmed; public page documents the Linux repair and Windows dependency |
| Committed generated main Python graph is stale and still connects a fourth receiver output | generated `OFDM_JCAS.py` compared with current GRC and receiver signature | Confirmed; treated as derived output, not current source |
| Runtime captures are generated diagnostics and should not be committed | maintenance guide, launchers, plot scripts, ignore rules | Confirmed |

## Source inventory reviewed

### Current repository sources

- `README.md`, `MAINTENANCE.md`, launchers, ignore rules, and repository history.
- Every GRC file under `Flow_graphs/`, the hand-written TX/RX Python module, generated graph code where needed for cross-checking, custom block definitions, and every plotter under `Plots/`.
- `docs/First_tests.md`, including all seven test stages and the current Test 2B receiver section.

### Local project and architecture documents

- `Hardware_setup.pdf`.
- `Biweekly update 19_06_26.docx` and `Second biweekly update.docx`.
- `Implementation problems.docx`, `Protocol initial meeting RWTH-UMA.docx`, `SoA analysis.docx`, `System-level architecture.docx`, `Thesis Matías López Lovera.docx`, `Trials.pptx`, and `Figures.pptx`.
- Historical `First tests.docx` copies and `Docs.zip`, checked for provenance and overlap but not treated as current.

### Literature corpus

The local survey, architecture, SDR implementation, delay-Doppler, vehicular sensing, passive radar, distributed processing, and OFDM radar PDFs were inventoried and text-extracted. They were used to check terminology and project intent. They do not override the code when describing what this repository currently implements.

### Wiki examples

The local read-only corpus contains the latest readable pages from Hardware, Software, Messtechnik, and Forschungsthemen plus the selected landing pages. The drafts follow the useful local conventions—short introductions, explicit sectioning, wikitables, related-page links, and categories—while avoiding copied obsolete setup instructions and inconsistent page-specific habits.

## Conflicts and traps resolved

| Potential error | Resolution in the drafts |
|---|---|
| Treating raw GRC defaults as the normal launch configuration | Launcher values are tabulated; raw defaults are explicitly identified as different |
| Confusing 100 kS/s simulation with 100 MS/s hardware RF work | Both are labelled with their context wherever they appear |
| Describing four receiver outputs | Corrected to two inputs and three outputs from the actual signature |
| Presenting committed block definitions or generated Python as current | Public page records the Linux temporary repair and tells maintainers to regenerate and align derived files |
| Claiming the main graph controls the USRP | Explicitly states that the graph has no UHD Source or Sink |
| Assigning final TX/RX roles from incomplete measurements | States that comparable recorded results are required before assignment |
| Reporting Test 5 or Test 6 as completed | Kept as planned with no completed result set documented |
| Calling displayed Frequency Sink values calibrated dBm or receiver SNR | Detailed caution remains in the repository test procedure; public page avoids the claim |
| Calling DDM bins detected targets or calibrated RCS | Explicitly prohibited in interpretation limits |
| Calling the reference DDM horizontal axis physical velocity | Public page records the missing `f_c` and current label/calculation mismatch |
| Claiming zero-padding improves physical resolution | Public page distinguishes display sampling from waveform resolution |
| Copying local working-document names into a public page | Automated test rejects local research paths and names |
| Using slash titles as MediaWiki subpages | Three standalone titles are linked explicitly |

## Pre-publication verification

1. Confirm the `jcas-ofdm` revision and inspect changes to the GRC sources, `OFDMJCAStxrx.py`, launchers, plotters, maintenance guide, and current test document.
2. Recheck all manufacturer limits against the current official NI and Ettus pages.
3. Run the sandbox source tests and reference-corpus verification.
4. Regenerate standalone previews and inspect their validation report.
5. Run the Linux project preflight in the intended GNU Radio environment. A local preview-machine check is not evidence that the laboratory host or USRP works.
6. Browse all three local pages at desktop and narrow widths. Check hierarchy links, table layout, commands, external URLs, categories, and the absence of local-only document references.
7. Read every page once as public prose: remove repetition, unsupported conclusions, internal shorthand, and wording that assumes access to a private working file.
8. On the live wiki, use **Vorschau zeigen** to validate exact MediaWiki rendering. Do not publish until the page title, links, and edit summary have been reviewed and explicit approval has been given.
