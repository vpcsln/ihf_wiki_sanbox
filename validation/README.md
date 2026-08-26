# Validation record

Validation was refreshed on 2026-08-26 after the project documentation advanced to the `084933d` revision and the public hierarchy was reorganised.

## Baselines

- JCAS source: `084933d` (`Fixed inaccuracies`, current `main`).
- Recorded hardware results: local `Tests results.pdf`, SHA-256 `421cc17430ed1c3da1e9e3c67f2ab6a36defef78a1eaf1391985845198d3e638`.
- IHF example corpus: 78 deduplicated latest revisions in the selected categories and landing pages; all stored source and rendered-fragment hashes passed.
- Hardware facts: NI USRP-2954 document 375725C, Ettus UBX documentation, and the UHD X300/X310 manual.
- The complete local project-document inventory is recorded in `SOURCE_MAP.md`.

## Checks performed

| Check | Result |
|---|---|
| High-risk claims checked directly against current GRC, Python, launcher, block-definition, plot, and test sources | Reported by `source-report.json` |
| Recorded result values checked from the PDF text extraction | Test 1 matrix, Test 2A values, Test 2B LO/image, compression observations, IIP3, and IIP2 |
| Sandbox and renderer unit tests | 17 passed |
| IHF example-corpus hash verification | 78 pages passed |
| GNU Radio Linux preflight on an isolated copy | Passed with GNU Radio 3.10.12.0; channel and main flowgraphs compiled |
| Standalone preview generation | 3 pages generated without syntax errors |
| Browser review | SDR, USRP, and JCAS pages checked at 1440 px; JCAS also checked at 800 px |
| Reference browser review | Index and an individual sanitized page returned HTTP 200 and rendered in the local IHF skin |
| Public-source boundary | No local paths, Word filenames, archive names, or private working-document references in the three `.wiki` files |
| Live IHF Wiki writes | None |

The isolated GNU Radio check copied the repository to `/tmp`, ran `Simulation_starter.sh --check`, and removed the copy after the result was recorded. It did not modify the project checkout or connect to a USRP.

## Findings preserved in the public documentation

- The main graph is a channel-model simulation and contains no UHD source or sink.
- The reference launchers use 100 kS/s, while initial hardware RF work requests 100 MS/s with a 200 MHz master clock.
- The latest Test 1 procedure requests 200, 100, 66.6, 50, and 40 MS/s; the recorded reliable matrix is limited by Ethernet throughput and TX underflows.
- The receiver implementation has two inputs and three outputs; older generated/descriptive material does not consistently reflect this.
- Test 2B uses a -15 dBm maximum input, a -30 dBm SMR60 minimum output, dBFS display levels, and IIP3/IIP2 measurements; the page includes the recorded values without presenting dBFS as calibrated dBm.
- The committed custom-block definitions retain legacy names and omit the receiver float input. The Linux launcher repairs temporary copies, while the Windows path depends on corrected installed definitions.
- The committed generated main Python graph is stale and is not treated as the source of truth.
- The reference DDM launch omits carrier frequency, so its horizontal calculation is frequency-like even though the plot label says velocity.
- Target detection, inter-daughterboard synchronisation evidence, static-target validation, and joint over-the-air validation are not presented as completed work.
- The old three-cell “SDR documentation” navigation bar was removed. The hub now has one dedicated Hardware entry, with the JCAS project nested below the NI USRP-2954R entry; the detail pages expose the same hierarchy through explicit links.
- JCAS source paths in the repository table use direct GitLab `main` branch tree/blob links.

The generated machine-readable details are in `source-report.json`. Repeat the checks after any relevant project or hardware-documentation change.
