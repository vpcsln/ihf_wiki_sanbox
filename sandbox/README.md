# Local IHF SDR Wiki sandbox

This sandbox provides a local, MediaWiki-style website for browsing, previewing, and editing the three SDR documentation pages. It has no dependency on the live IHF Wiki and contains no authentication or publishing code.

## Start

```bash
cd /home/vpc/Dokumente/RWTH_IHF/ihf_wiki_sdr_jcas
./sandbox/start.sh
```

Open <http://127.0.0.1:8765/>. Stop the server with `Ctrl-C`.

Select another port if required:

```bash
./sandbox/start.sh --port 9000
```

The server refuses non-loopback bind addresses. It cannot be exposed through `--host 0.0.0.0` without changing the source deliberately.

## Features

- The exact Vector Legacy and site styles served by the IHF Wiki, with the original IHF logo, favicon, MediaWiki badge, and referenced skin images mirrored locally.
- Browsable SDR hub, USRP hardware, and JCAS project pages.
- Read-only browsing of the gitignored IHF example-page snapshot under `/reference/`.
- Local internal links, categories, search, random page, and recent changes.
- MediaWiki source editor with local preview.
- Syntax checks for tables, code/pre blocks, and Markdown backticks.
- Atomic local saves with timestamped backups under `sandbox/backups/`.
- No third-party Python dependencies.
- No requests to the IHF Wiki and no live publishing endpoint.

Reference pages are sanitized when fetched and served with a restrictive Content Security Policy. Scripts, forms, frames, embedded objects, and remotely loaded media are not included. If no snapshot is present, the reference index shows the local fetch command instead.

The editable source remains in `pages/*.wiki`. The sandbox renders those files dynamically, so it does not need a build step after an edit.

The mirrored presentation assets are documented under `sandbox/static/vendor/ihf/README.md`. They are never loaded from the network at runtime.

## Test

```bash
python3 -m unittest discover -s sandbox/tests -v
```

For a browser smoke test, start the server and run:

```bash
curl --fail http://127.0.0.1:8765/wiki/Software_Defined_Radio_\(SDR\)
```

## Important boundary

The local renderer implements the MediaWiki syntax used by these pages; it is not the MediaWiki engine. Before publishing, paste the source into the live editor and use **Vorschau zeigen** for exact validation. Publishing remains a separate, manual action performed by an authenticated wiki user.
