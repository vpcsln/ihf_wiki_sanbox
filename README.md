# IHF SDR and JCAS wiki drafts

This folder contains MediaWiki source for three linked IHF wiki pages:

| File | Wiki page title |
|---|---|
| `pages/Software_Defined_Radio_(SDR).wiki` | `Software Defined Radio (SDR)` |
| `pages/NI_USRP-2954R.wiki` | `NI USRP-2954R` |
| `pages/OFDM-based_Joint_Communication_and_Sensing_(JCAS).wiki` | `OFDM-based Joint Communication and Sensing (JCAS)` |

The IHF MediaWiki does not enable subpages in its main namespace. The drafts therefore use standalone titles with explicit links. The SDR hub has one dedicated Hardware entry for the NI USRP-2954R, and the JCAS project is listed below that hardware entry.

Together, these three pages form one SDR documentation set. The SDR page is the hub, while the linked hardware and project pages contain the detailed material. Maintain and review all three together.

## Directory structure

```text
ihf_wiki_sdr_jcas/
├── README.md
├── SOURCE_MAP.md # Evidence and update rules for technical claims
├── assets/       # Images or diagrams to upload later
├── pages/        # Editable MediaWiki source
├── previews/     # Generated HTML and screenshot previews
├── reference/    # Local-only IHF Wiki example corpus tooling
├── render_previews.py
├── sandbox/      # Local browsable wiki and editor
├── validate_sources.py
└── validation/   # Generated project-source verification report
```

## Browse and edit in the local sandbox

```bash
cd /home/vpc/Dokumente/RWTH_IHF/ihf_wiki_sdr_jcas
./sandbox/start.sh
```

Open <http://127.0.0.1:8765/>. The sandbox reads and writes only the local files under this directory and automatically backs up local edits. See `sandbox/README.md` for details.

## Preview in MediaWiki

No additional package or network access is required. Python 3 renders all three drafts locally:

```bash
cd /home/vpc/Dokumente/RWTH_IHF/ihf_wiki_sdr_jcas
python3 render_previews.py
```

Open the generated HTML files under `previews/` in a browser. The script also writes `previews/validation.json` with the categories and internal links found in each source file.

The local renderer covers the syntax used by these drafts but is not a complete MediaWiki implementation. Always use **Vorschau zeigen** in the wiki editor for the final exact rendering before publishing.

The HTML files under `previews/` are generated previews and should not be edited directly.

## Verify project-specific claims

With the `jcas-ofdm` checkout beside this directory, compare the high-risk implementation claims with its current source files:

```bash
python3 validate_sources.py
```

This checks launcher values, carrier maps, stream signatures, channel parameters, ZMQ ports, current Test 1/Test 2B wording, recorded hardware-result values when `Tests results.pdf` is present, hierarchy structure, GitLab source links, legacy block-definition handling, and the public/private documentation boundary. It writes `validation/source-report.json`. Manufacturer specifications and prose-level judgements remain recorded in `SOURCE_MAP.md` and require human review.

## Local IHF Wiki examples

The read-only reference downloader collects current pages from the IHF Wiki's Hardware, Software, Messtechnik, and Forschungsthemen categories. Page bodies are stored only in the gitignored local snapshot; they are never pushed to GitHub.

```bash
python3 reference/ihf_wiki_examples/sync.py fetch
python3 reference/ihf_wiki_examples/sync.py verify
```

When present, the snapshot is available from the sandbox under `/reference/`.

## Private GitHub repository

This folder is maintained in the private GitHub repository `ihf_wiki_sanbox`. Keep the repository private: the drafts contain internal network configuration and IHF-specific project information. Do not add passwords, wiki session cookies, access tokens, or other credentials even to the private repository.

## Publish manually

1. Sign in to the IHF Wiki.
2. Open the target page with `?action=edit`.
3. Paste the corresponding `.wiki` file into the source editor.
4. Select **Vorschau zeigen** and check the table of contents, links, tables, commands, and categories.
5. Use a specific edit summary, for example `Add SDR overview and links to USRP and JCAS documentation`.
6. Publish the two new pages before replacing the SDR hub so that its links are blue immediately.

Publishing is intentionally manual. The scripts in this folder never authenticate to MediaWiki and never call its edit API.

Suggested edit URLs:

- `http://intern.ihf.rwth-aachen.de/wiki/index.php?title=NI_USRP-2954R&action=edit`
- `http://intern.ihf.rwth-aachen.de/wiki/index.php?title=OFDM-based_Joint_Communication_and_Sensing_(JCAS)&action=edit`
- `http://intern.ihf.rwth-aachen.de/wiki/index.php?title=Software_Defined_Radio_(SDR)&action=edit`

## Maintenance rule

- Keep general SDR concepts and navigation on the SDR page.
- Keep reusable device setup, network configuration, connector behavior, and RF safety on the USRP page.
- Keep architecture, repository entry points, execution, outputs, and project verification on the JCAS page.
- Keep exact code, volatile parameters, detailed procedures, results, and issue history in the Git repository.
- Update the `.wiki` source here before or together with edits to the live wiki.
- Review all three pages and `SOURCE_MAP.md` together when hardware, software, or project architecture changes.
