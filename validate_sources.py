#!/usr/bin/env python3
"""Check high-risk wiki claims against a local jcas-ofdm checkout."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PAGES = ROOT / "pages"
DEFAULT_PROJECT_REPO = ROOT.parent / "jcas-ofdm"
DEFAULT_REPORT = ROOT / "validation" / "source-report.json"
DEFAULT_RESULTS_PDF = ROOT.parent / "Tests results.pdf"
DEFAULT_TEST_NOTES = ROOT.parent / "Test_1_2_new_folder_18aug"


def require_contains(checks: list[dict[str, str]], name: str, text: str, value: str) -> None:
    if value not in text:
        raise AssertionError(f"{name}: missing {value!r}")
    checks.append({"name": name, "status": "passed"})


def require_absent(checks: list[dict[str, str]], name: str, text: str, value: str) -> None:
    if value in text:
        raise AssertionError(f"{name}: unexpected {value!r}")
    checks.append({"name": name, "status": "passed"})


def carrier_values(grc: str, variable: str) -> list[int]:
    match = re.search(
        rf"- name: {re.escape(variable)}\n.*?\n\s+value: \(\((.*?)\),\)",
        grc,
        flags=re.DOTALL,
    )
    if not match:
        raise AssertionError(f"Could not parse carrier variable {variable}")
    return [int(value) for value in re.findall(r"-?\d+", match.group(1))]


def shell_assignments(text: str) -> dict[str, int]:
    return {
        key: int(value)
        for key, value in re.findall(
            r"^(SAMP_RATE|N|M|M_CROP|NUMBER_RANGE|CP_LEN|RESOL|RAMP_NUM)=(\d+)\s*$",
            text,
            flags=re.MULTILINE,
        )
    }


def batch_assignments(text: str) -> dict[str, int]:
    return {
        key.upper(): int(value)
        for key, value in re.findall(
            r"^set (SAMP_RATE|N|M|M_crop|NUMBER_RANGE|CP_LEN|RESOL|RAMP_NUM)=(\d+)\s*$",
            text,
            flags=re.MULTILINE | re.IGNORECASE,
        )
    }


def read_results_pdf(path: Path) -> str | None:
    """Return extracted result text when the local result report is available."""
    if not path.is_file():
        return None
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(path), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (FileNotFoundError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"Could not extract {path}: install poppler-utils") from exc
    return result.stdout


def validate(
    project_repo: Path,
    results_pdf: Path = DEFAULT_RESULTS_PDF,
    test_notes: Path = DEFAULT_TEST_NOTES,
) -> dict[str, object]:
    required_paths = (
        project_repo / "Flow_graphs" / "OFDMJCAS.grc",
        project_repo / "Flow_graphs" / "Channel_Model.grc",
        project_repo / "Flow_graphs" / "OFDMJCAStxrx.py",
        project_repo / "Simulation_starter.sh",
        project_repo / "Simulation_starter.bat",
        project_repo / "Block_definition" / "OFDM_JCAS_rx.block.yml",
        project_repo / "Block_definition" / "OFDM_JCAS_tx.block.yml",
        project_repo / "docs" / "First_tests.md",
    )
    missing = [str(path) for path in required_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError("Missing project sources:\n- " + "\n- ".join(missing))

    main_grc = required_paths[0].read_text(encoding="utf-8")
    channel_grc = required_paths[1].read_text(encoding="utf-8")
    txrx = required_paths[2].read_text(encoding="utf-8")
    linux_launcher = required_paths[3].read_text(encoding="utf-8")
    windows_launcher = required_paths[4].read_text(encoding="utf-8")
    receiver_definition = required_paths[5].read_text(encoding="utf-8")
    transmitter_definition = required_paths[6].read_text(encoding="utf-8")
    tests = required_paths[7].read_text(encoding="utf-8")
    public_sources = {
        path.name: path.read_text(encoding="utf-8") for path in sorted(PAGES.glob("*.wiki"))
    }
    project_page = public_sources["OFDM-based_Joint_Communication_and_Sensing_(JCAS).wiki"]
    checks: list[dict[str, str]] = []

    expected_launcher = {
        "SAMP_RATE": 100000,
        "N": 127,
        "M": 63,
        "M_CROP": 62,
        "NUMBER_RANGE": 256,
        "CP_LEN": 48,
        "RESOL": 4,
        "RAMP_NUM": 7,
    }
    linux_values = shell_assignments(linux_launcher)
    windows_values = batch_assignments(windows_launcher)
    if linux_values != expected_launcher:
        raise AssertionError(f"Linux launcher values changed: {linux_values}")
    checks.append({"name": "Linux reference launcher values", "status": "passed"})
    if windows_values != expected_launcher:
        raise AssertionError(f"Windows launcher values changed: {windows_values}")
    checks.append({"name": "Windows reference launcher values", "status": "passed"})

    occupied = carrier_values(main_grc, "occupied_carriers")
    pilots = carrier_values(main_grc, "pilot_carriers")
    if len(occupied) != 115 or len(pilots) != 12 or len(set(occupied + pilots)) != 127:
        raise AssertionError(
            f"Carrier map changed: occupied={len(occupied)}, pilots={len(pilots)}, "
            f"active={len(set(occupied + pilots))}"
        )
    checks.append({"name": "115 data and 12 pilot carriers", "status": "passed"})
    if pilots != list(range(-55, 56, 10)):
        raise AssertionError(f"Pilot map changed: {pilots}")
    checks.append({"name": "Pilot carrier indices", "status": "passed"})

    for value in ('header_mod: \'"QPSK"\'', 'payload_mod: \'"QPSK"\'', "scramble_bits: 'False'"):
        require_contains(checks, f"Main GRC parameter {value}", main_grc, value)
    for port in range(5555, 5559):
        require_contains(checks, f"ZMQ loopback port {port}", main_grc, f"tcp://127.0.0.1:{port}")
    for block_id in ("uhd_usrp_source", "uhd_usrp_sink", "uhd_usrp"):
        require_absent(checks, f"No {block_id} in main graph", main_grc, f"id: {block_id}")

    require_contains(
        checks,
        "Receiver two-input signature",
        txrx,
        "gr.io_signature(2, 2, [gr.sizeof_gr_complex, gr.sizeof_float])",
    )
    require_contains(
        checks,
        "Receiver three-output signature",
        txrx,
        "gr.io_signature(3, 3, [gr.sizeof_char, gr.sizeof_gr_complex, gr.sizeof_gr_complex])",
    )
    require_contains(checks, "Synchroniser threshold", txrx, "threshold = 0.996")
    require_contains(checks, "Payload equaliser alpha", txrx, "alpha=0.1")
    require_contains(checks, "Zadoff-Chu preamble", txrx, "zc_seq = numpy.exp")

    for value in ("delay: '0'", "delay: '20'", "delay: '40'", "freq: '100'", "freq: '200'", "amp: '0.001'"):
        require_contains(checks, f"Channel value {value}", channel_grc, value)
    require_contains(checks, "Channel model fixed rate", channel_grc, "value: '100000'")

    require_contains(
        checks,
        "Current Test 1 trial rates",
        tests,
        "Requested single stream trial rates | 200, 100, 66.6, 50, and 40 MS/s per active stream",
    )
    require_contains(checks, "Current Test 1 master clock", tests, "`MCR_project` | 200 MHz")
    require_contains(
        checks,
        "Current Test 1 project mapping",
        tests,
        "TX on daughterboard A with RX on daughterboard B",
    )
    require_contains(
        checks,
        "Current receiver input limit",
        tests,
        "Maximum input used in this test | -15 dBm at the USRP input",
    )
    require_contains(checks, "Current generator minimum", tests, "SMR60 minimum output | -30 dBm")
    require_contains(
        checks,
        "Current receiver display units",
        tests,
        "relative, not calibrated input power in dBFS",
    )
    require_contains(checks, "Current IIP3 procedure", tests, "#### 5. IIP3 measurement")
    require_contains(checks, "Current IIP2 procedure", tests, "#### 6. IIP2 measurement")
    require_absent(checks, "Removed unavailable receiver-status claim", tests, "Both daughterboards were tested")
    require_absent(checks, "Removed obsolete receiver ceiling", tests, "stop at -20 dBm")
    require_contains(checks, "Synchronisation test status", tests, "Status: Not performed")
    require_contains(checks, "Hardware communication execution", tests, "hardware execution of Experiment 4")

    require_contains(checks, "Legacy receiver ID", receiver_definition, "id: dns_ofdm_rx")
    require_contains(checks, "Legacy receiver class", receiver_definition, "OFDMJCAS.Radar_ofdm_rx")
    require_absent(checks, "Receiver definition omits float input", receiver_definition, "dtype: float")
    require_contains(checks, "Legacy transmitter ID", transmitter_definition, "id: dns_ofdm_tx")
    require_contains(checks, "Linux repairs receiver definition", linux_launcher, "has_float_input")
    require_contains(checks, "Linux repairs legacy class", linux_launcher, "OFDMJCAS.Ofdm_jcas_rx")

    for filename, source in public_sources.items():
        for forbidden in ("Docs/", "Docs.zip", "First tests.docx", "project_facts.txt", "/home/"):
            require_absent(checks, f"Public-source privacy: {filename}: {forbidden}", source, forbidden)
    for value in (
        "there are no UHD Source or UHD Sink blocks",
        "two inputs and three outputs",
        "100000 samples/s",
        "200 MHz USRP master clock",
        "labels the axis as velocity in m/s",
        "No CFAR or other target detector",
        "Recorded hardware results",
        "Highest reliably operated rate",
        "200 MS/s",
        "50 MS/s",
        "40 MS/s",
        "-25.68",
        "-35.79",
        "-25.13 dBm",
        "6.94 dBm",
        "-47.87",
        "-29.59",
        "-22.58 dB attenuator",
        "20 dB",
        "37.5 dB",
    ):
        require_contains(checks, f"Project-page distinction: {value}", project_page, value)

    for filename, source in public_sources.items():
        require_absent(checks, f"No obsolete navigation bar: {filename}", source, "SDR documentation")
        require_absent(checks, f"No ASCII arrow diagram: {filename}", source, "->")
        require_absent(checks, f"No Unicode arrow diagram: {filename}", source, "→")
    hub = public_sources["Software_Defined_Radio_(SDR).wiki"]
    hardware = public_sources["NI_USRP-2954R.wiki"]
    require_contains(checks, "Hub has dedicated hardware section", hub, "== Hardware ==")
    require_contains(checks, "Hub has one hardware entry", hub, "=== NI USRP-2954R ===")
    require_contains(checks, "Hub nests project under hardware", hub, "==== Project on this hardware ====")
    require_contains(checks, "Hardware hierarchy list", hardware, "== SDR hierarchy ==")
    require_contains(checks, "Hardware project section", hardware, "== Project on this hardware ==")
    require_contains(checks, "GitLab tree link", project_page, "https://git.rwth-aachen.de/ihf/sdr/jcas-ofdm/-/tree/main")
    require_contains(checks, "GitLab source-file link", project_page, "https://git.rwth-aachen.de/ihf/sdr/jcas-ofdm/-/blob/main/Flow_graphs/OFDMJCAS.grc")

    external_evidence: dict[str, object] = {}
    extracted_results = read_results_pdf(results_pdf)
    if extracted_results is None:
        external_evidence["results_pdf"] = {"status": "not-present", "path": str(results_pdf)}
    else:
        for value in (
            "Can work with 200 MS/s",
            "Only reliable if 50 MS/s",
            "offset did not exceed 50 Hz",
            "-47.87",
            "-29.59",
            "-25.13",
            "-24.44",
            "6.57",
            "6.94",
            "-22.58 dB attenuator",
        ):
            require_contains(checks, f"Recorded-results PDF: {value}", extracted_results, value)
        import hashlib

        external_evidence["results_pdf"] = {
            "status": "verified",
            "path": str(results_pdf),
            "sha256": hashlib.sha256(results_pdf.read_bytes()).hexdigest(),
            "size_bytes": results_pdf.stat().st_size,
        }

    readme_checks: dict[str, str] = {}
    for relative, expected in (
        (Path("Test1") / "README.md", "Test1_TXRX.grc"),
        (Path("Test2") / "README.md", "Test2B_IIP3.grc"),
    ):
        note_path = test_notes / relative
        if note_path.is_file():
            note_text = note_path.read_text(encoding="utf-8")
            require_contains(checks, f"Test note {relative}", note_text, expected)
            readme_checks[str(relative)] = "verified"
        else:
            readme_checks[str(relative)] = "not-present"
    external_evidence["test_notes"] = {"path": str(test_notes), "checks": readme_checks}

    revision = subprocess.run(
        ["git", "-C", str(project_repo), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    return {
        "schema_version": 2,
        "generated_at": datetime.now(UTC).isoformat(),
        "project_repository": project_repo.name,
        "project_revision": revision,
        "automatic_check_count": len(checks),
        "automatic_checks": checks,
        "external_evidence": external_evidence,
        "manual_evidence_ledger": "SOURCE_MAP.md",
        "status": "passed",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-repo", type=Path, default=DEFAULT_PROJECT_REPO)
    parser.add_argument("--results-pdf", type=Path, default=DEFAULT_RESULTS_PDF)
    parser.add_argument("--test-notes", type=Path, default=DEFAULT_TEST_NOTES)
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()

    report = validate(
        args.project_repo.resolve(),
        results_pdf=args.results_pdf.resolve(),
        test_notes=args.test_notes.resolve(),
    )
    report_path = args.report.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(
        f"Verified {report['automatic_check_count']} high-risk claims against "
        f"{report['project_revision']}."
    )
    print(f"Wrote {report_path}")


if __name__ == "__main__":
    main()
