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
