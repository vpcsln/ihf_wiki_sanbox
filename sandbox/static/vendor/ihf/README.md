# Mirrored IHF Wiki skin assets

These files reproduce the presentation layer of the internal IHF Wiki in the local sandbox. They were fetched read-only on 2026-08-12 from the anonymous `Software Defined Radio (SDR)` page and the static resources referenced by that page.

Included material:

- the IHF Wiki's `skins.vector.styles.legacy` ResourceLoader stylesheet;
- the IHF Wiki's `site.styles` ResourceLoader stylesheet;
- the original `Logo_IHF.png` and `favicon.ico` files;
- all images referenced by those stylesheets; and
- the three MediaWiki “Powered by” badge resolutions used by the live footer.

The two stylesheet files differ from the downloaded bytes only in their asset URLs: live `/wiki/...` and Wikimedia URLs were rewritten to `/static/vendor/ihf/...` so the sandbox is fully local. The unmodified downloaded stylesheet SHA-256 values were:

| Resource | SHA-256 before local URL rewriting |
|---|---|
| `skins.vector.styles.legacy` | `3ac91a3448afe585be5c3122efc197f84fbc98eb2f13f8b2354043f8ea7f6000` |
| `site.styles` | `f924e4c626d65070a646ef4a9a5cc0118882c4ff08a9f288b52fa248a36792e4` |
| `Logo_IHF.png` | `428e22aebbe8412260cdd311b2e85215bb7eb9a76f45f097b11938daffe1516f` |
| `favicon.ico` | `ebbc99a9af93ae8c243355b2ae48b32e699d7ce2fd0a370c0e58e611fa6e0f31` |

Source endpoints:

- `http://intern.ihf.rwth-aachen.de/wiki/load.php?lang=de&modules=skins.vector.styles.legacy&only=styles&skin=vector`
- `http://intern.ihf.rwth-aachen.de/wiki/load.php?lang=de&modules=site.styles&only=styles&skin=vector`
- static assets below `/wiki/images/`, `/wiki/resources/`, and `/wiki/skins/Vector/`
- the two Monobook bullet images referenced by `site.styles`, mirrored from Wikimedia Commons

The IHF logo remains IHF branding and is included for this private internal documentation sandbox. The MediaWiki skin and its bundled assets retain their upstream licences. Do not assume that this repository's own licence grants permission to reuse the IHF logo externally.
