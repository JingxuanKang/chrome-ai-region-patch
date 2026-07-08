# Chrome AI Region Patch

Small macOS-first Python CLI that patches Chrome's local `Local State` region eligibility fields for built-in AI surfaces.

Key architecture:
- `chrome_ai_region_patch.py` is the single implementation file and has no third-party dependencies.
- It patches only Chrome user data `Local State` JSON files and creates timestamped backups before writes.
- It reads the installed Chrome app bundle version first on macOS to avoid stale profile `Last Version` values after browser updates.

Guardrails:
- Do not add user-specific absolute paths, hostnames, tokens, Chrome profile data, cookies, browsing history, or screenshots.
- Keep documentation English-first, with Chinese content in `README.zh.md` or clearly secondary sections.
- Preserve upstream attribution to `lcandy2/enable-chrome-ai` in public-facing docs.
- Avoid adding dependencies unless they remove a real maintenance burden.
