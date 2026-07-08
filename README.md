# Chrome AI Region Patch

Patch Chrome's local region eligibility fields for built-in AI surfaces such as Gemini in Chrome, AI-powered history search, and DevTools AI.

This is a small, macOS-first Python script. It edits Chrome's local `Local State` JSON file, creates a timestamped backup before writing, and does not install extensions, send telemetry, or depend on third-party packages.

> Status: this is an unofficial local workaround. Chrome and Google server-side eligibility rules can change, so a successful patch may still take time to surface in the browser.

## Quick Start

```bash
git clone https://github.com/JingxuanKang/chrome-ai-region-patch.git
cd chrome-ai-region-patch
python3 chrome_ai_region_patch.py --force-kill
```

Use `--force-kill` only if Chrome does not quit cleanly. The script normally asks macOS to quit Chrome first, then reopens it after patching.

Dry run:

```bash
python3 chrome_ai_region_patch.py --dry-run
```

Patch a custom Chrome user data directory:

```bash
python3 chrome_ai_region_patch.py --profile-dir "~/Library/Application Support/Google/Chrome"
```

## What It Changes

In Chrome's user data directory, the script opens `Local State` and:

- sets every `is_glic_eligible` value to `true`;
- sets `variations_country` to `us` by default;
- sets `variations_permanent_consistency_country` to `[<Chrome app version>, "us"]`;
- writes a timestamped backup before saving changes.

On macOS, Chrome's user data directory is normally:

```text
~/Library/Application Support/Google/Chrome
```

The script also checks Chrome Beta, Dev, and Canary if those profiles exist.

## Why Ask Gemini Disappears After Updates

Chrome updates and restarts can rewrite `Local State`. In practice, region fields may revert to the machine's real region, for example `gb`, even if `is_glic_eligible` remains `true`.

When that happens, rerun:

```bash
python3 chrome_ai_region_patch.py --force-kill
```

If Chrome has just updated, this script reads the installed Chrome app version from the app bundle first, rather than trusting a stale profile `Last Version` file.

## Similar Projects

This repository exists because the underlying workaround is useful, but day-to-day use benefits from a smaller, auditable macOS script that can be rerun after Chrome updates.

- [`lcandy2/enable-chrome-ai`](https://github.com/lcandy2/enable-chrome-ai): the main upstream Python implementation. It supports multiple platforms and Chrome channels, but depends on `psutil` and uses the profile `Last Version` file.
- [`appsail/Gemini-in-Chrome`](https://github.com/appsail/Gemini-in-Chrome): one-command shell and PowerShell scripts for macOS, Linux, and Windows.
- [`tianlanyb/Gemini-in-Chrome`](https://github.com/tianlanyb/Gemini-in-Chrome): another one-click script collection for non-US users.
- [`gemini-unlock`](https://lib.rs/crates/gemini-unlock): a Rust utility in the same problem space.
- Manual guides and forum posts commonly describe editing `Local State` by hand.

This project is intentionally narrower: no third-party Python packages, timestamped backups, dry-run output, app-bundle version detection on macOS, and no hard-coded personal paths.

## Options

```text
--country CODE       Country code to write; default: us
--channels ...       macOS channels to patch: stable beta dev canary
--profile-dir PATH   Patch one explicit user data directory
--dry-run            Show planned changes without editing files
--no-restart         Do not reopen Chrome after patching
--force-kill         Force-kill Chrome if normal quit does not finish
```

## Privacy

The script only reads and writes local Chrome configuration files. It does not upload data or read browsing history, cookies, saved passwords, bookmarks, or extension data.

The repository intentionally avoids machine-specific paths, usernames, tokens, hostnames, and personal profile content.

## Chinese

中文说明见 [README.zh.md](README.zh.md)。

## Credits

This project is based on the local-state patching approach from [`lcandy2/enable-chrome-ai`](https://github.com/lcandy2/enable-chrome-ai), released under the MIT License. See [NOTICE.md](NOTICE.md).

## License

MIT. See [LICENSE](LICENSE).
