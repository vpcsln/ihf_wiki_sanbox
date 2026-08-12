# Validation record

Validation completed on 2026-08-12 before committing the three-page wiki hierarchy.

## Baselines

- JCAS source: `b95f0c49f7e54ba10c93670933c3e0a7c48c805d` (`Improved Test 2B`).
- IHF example corpus: 78 deduplicated latest revisions in the selected categories and landing pages; all stored source and rendered-fragment hashes passed.
- Hardware facts: NI USRP-2954 document 375725C, Ettus UBX documentation, and the UHD X300/X310 manual.
- The complete local project-document inventory is recorded in `SOURCE_MAP.md`.

## Checks performed

| Check | Result |
|---|---|
| High-risk claims checked directly against current GRC, Python, launcher, block-definition, plot, and test sources | 56 passed |
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
- The receiver implementation has two inputs and three outputs; older generated/descriptive material does not consistently reflect this.
- The committed custom-block definitions retain legacy names and omit the receiver float input. The Linux launcher repairs temporary copies, while the Windows path depends on corrected installed definitions.
- The committed generated main Python graph is stale and is not treated as the source of truth.
- The reference DDM launch omits carrier frequency, so its horizontal calculation is frequency-like even though the plot label says velocity.
- Target detection, inter-daughterboard synchronisation evidence, static-target validation, and joint over-the-air validation are not presented as completed work.

The generated machine-readable details are in `source-report.json`. Repeat the checks after any relevant project or hardware-documentation change.
