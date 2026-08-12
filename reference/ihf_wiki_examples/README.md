# Local IHF Wiki example corpus

This directory supports a local, read-only snapshot of representative IHF Wiki pages. It is used to compare structure, terminology, tables, categories, and navigation patterns while maintaining the SDR, USRP, and JCAS documentation.

The selection contains the current members of these main-namespace categories:

- `Hardware`
- `Software`
- `Messtechnik`
- `Forschungsthemen`

It also contains the main page, the tutorial, and the four category landing pages. The downloader stores only the latest readable revision. It does not download histories, user or talk pages, authentication data, or uploaded binaries.

## Fetch and verify

```bash
python3 reference/ihf_wiki_examples/sync.py fetch
python3 reference/ihf_wiki_examples/sync.py verify
```

The generated `snapshot/` directory contains MediaWiki source, sanitized rendered fragments, per-page metadata, a manifest, and a local index. The complete directory is ignored by Git. `validation-summary.json` contains only aggregate counts and may be committed.

The HTML sanitizer removes scripts, forms, embedded objects, and remotely loaded media. Referenced media titles remain in metadata, but the files themselves are not mirrored.

The downloader uses anonymous MediaWiki API reads. It contains no login, cookie, token, or editing support.
