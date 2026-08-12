# IHF SDR and JCAS wiki drafts

This folder contains MediaWiki source for three linked IHF wiki pages:

| File | Wiki page title |
|---|---|
| `pages/Software_Defined_Radio_(SDR).wiki` | `Software Defined Radio (SDR)` |
| `pages/NI_USRP-2954R_and_UBX-160.wiki` | `NI USRP-2954R and UBX-160` |
| `pages/OFDM-based_Joint_Communication_and_Sensing_(JCAS).wiki` | `OFDM-based Joint Communication and Sensing (JCAS)` |

The IHF MediaWiki does not enable subpages in its main namespace. The drafts therefore use standalone titles with explicit navigation links instead of slash-based titles.

Together, these three pages form one SDR documentation set. The SDR page is the hub, while the linked hardware and project pages contain the detailed material. Maintain and review all three together.

## Directory structure

```text
ihf_wiki_sdr_jcas/
├── README.md
├── SOURCE_MAP.md # Evidence and update rules for technical claims
├── assets/       # Images or diagrams to upload later
├── pages/        # Editable MediaWiki source
├── previews/     # Generated HTML and screenshot previews
├── render_previews.py
└── sandbox/      # Local browsable wiki and editor
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

- `http://intern.ihf.rwth-aachen.de/wiki/index.php?title=NI_USRP-2954R_and_UBX-160&action=edit`
- `http://intern.ihf.rwth-aachen.de/wiki/index.php?title=OFDM-based_Joint_Communication_and_Sensing_(JCAS)&action=edit`
- `http://intern.ihf.rwth-aachen.de/wiki/index.php?title=Software_Defined_Radio_(SDR)&action=edit`

## Maintenance rule

- Keep general SDR concepts and navigation on the SDR page.
- Keep reusable device setup, network configuration, connector behavior, and RF safety on the USRP page.
- Keep architecture, repository entry points, execution, outputs, and project verification on the JCAS page.
- Keep exact code, volatile parameters, detailed procedures, results, and issue history in the Git repository.
- Update the `.wiki` source here before or together with edits to the live wiki.
- Review all three pages and `SOURCE_MAP.md` together when hardware, software, or project architecture changes.
