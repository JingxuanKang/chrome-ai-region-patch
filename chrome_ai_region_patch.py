#!/usr/bin/env python3
"""Patch Chrome's local region eligibility fields for built-in AI features.

This script edits Chrome's local "Local State" JSON file. It does not contact
Google, install extensions, or collect profile data.
"""

from __future__ import annotations

import argparse
import json
import os
import plistlib
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


DEFAULT_COUNTRY = "us"
APP_NAME = "Google Chrome"

MAC_CHANNELS = {
    "stable": {
        "app": "/Applications/Google Chrome.app",
        "profile": "~/Library/Application Support/Google/Chrome",
    },
    "canary": {
        "app": "/Applications/Google Chrome Canary.app",
        "profile": "~/Library/Application Support/Google/Chrome Canary",
    },
    "dev": {
        "app": "/Applications/Google Chrome Dev.app",
        "profile": "~/Library/Application Support/Google/Chrome Dev",
    },
    "beta": {
        "app": "/Applications/Google Chrome Beta.app",
        "profile": "~/Library/Application Support/Google/Chrome Beta",
    },
}


def expand(path: str) -> Path:
    return Path(os.path.expanduser(path)).resolve()


def read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, data: Any) -> None:
    tmp = path.with_name(path.name + ".tmp")
    with tmp.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, separators=(",", ":"))
    tmp.replace(path)


def app_version(app_bundle: Path) -> str | None:
    info_plist = app_bundle / "Contents" / "Info.plist"
    if not info_plist.exists():
        return None
    with info_plist.open("rb") as handle:
        info = plistlib.load(handle)
    version = info.get("CFBundleShortVersionString")
    return str(version).strip() if version else None


def profile_last_version(profile_dir: Path) -> str | None:
    path = profile_dir / "Last Version"
    if not path.exists():
        return None
    version = path.read_text(encoding="utf-8").strip()
    return version or None


def set_glic_eligible(value: Any) -> int:
    changed = 0
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "is_glic_eligible" and item is not True:
                value[key] = True
                changed += 1
            elif isinstance(item, (dict, list)):
                changed += set_glic_eligible(item)
    elif isinstance(value, list):
        for item in value:
            changed += set_glic_eligible(item)
    return changed


def summarize_state(local_state: dict[str, Any]) -> dict[str, Any]:
    glic_values: list[Any] = []

    def walk(value: Any) -> None:
        if isinstance(value, dict):
            for key, item in value.items():
                if key == "is_glic_eligible":
                    glic_values.append(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    walk(local_state)
    return {
        "variations_country": local_state.get("variations_country"),
        "variations_permanent_consistency_country": local_state.get(
            "variations_permanent_consistency_country"
        ),
        "is_glic_eligible_count": len(glic_values),
        "is_glic_eligible_all_true": bool(glic_values)
        and all(item is True for item in glic_values),
    }


def patch_local_state(
    local_state_path: Path,
    chrome_version: str | None,
    country: str,
    dry_run: bool,
) -> bool:
    local_state = read_json(local_state_path)
    before = summarize_state(local_state)

    changed = False
    glic_changes = set_glic_eligible(local_state)
    if glic_changes:
        changed = True

    if local_state.get("variations_country") != country:
        local_state["variations_country"] = country
        changed = True

    target_version = chrome_version
    existing = local_state.get("variations_permanent_consistency_country")
    if isinstance(existing, list) and len(existing) >= 2:
        target_version = target_version or str(existing[0])
        if existing[0] != target_version or existing[1] != country:
            existing[0] = target_version
            existing[1] = country
            changed = True
    else:
        local_state["variations_permanent_consistency_country"] = [
            target_version or "",
            country,
        ]
        changed = True

    after = summarize_state(local_state)
    print(f"  Before: {before}")
    print(f"  After:  {after}")

    if dry_run:
        print("  Dry run: no files changed")
        return changed

    if not changed:
        print("  Already patched")
        return False

    backup = local_state_path.with_name(
        local_state_path.name + ".bak." + time.strftime("%Y%m%d-%H%M%S")
    )
    shutil.copy2(local_state_path, backup)
    write_json(local_state_path, local_state)
    print(f"  Patched; backup: {backup.name}")
    return True


def chrome_running() -> bool:
    if sys.platform != "darwin":
        return False
    result = subprocess.run(["pgrep", "-x", APP_NAME], capture_output=True)
    return result.returncode == 0


def close_chrome(force: bool) -> bool:
    if sys.platform != "darwin" or not chrome_running():
        return False

    subprocess.run(
        ["osascript", "-e", f'quit app "{APP_NAME}"'],
        capture_output=True,
        text=True,
    )
    for _ in range(20):
        if not chrome_running():
            return True
        time.sleep(0.3)

    if force:
        subprocess.run(["pkill", "-9", "-x", APP_NAME], capture_output=True)
        time.sleep(1.0)
    return True


def reopen_chrome() -> None:
    if sys.platform == "darwin":
        subprocess.run(["open", "-a", APP_NAME], capture_output=True)


def channel_targets(channels: list[str]) -> list[tuple[str, Path, Path | None]]:
    if sys.platform != "darwin":
        raise SystemExit("Automatic channel detection currently supports macOS only.")

    targets: list[tuple[str, Path, Path | None]] = []
    for channel in channels:
        config = MAC_CHANNELS[channel]
        profile_dir = expand(config["profile"])
        app_bundle = Path(config["app"])
        if (profile_dir / "Local State").exists():
            targets.append((channel, profile_dir, app_bundle))
    return targets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Patch Chrome's local AI eligibility region fields."
    )
    parser.add_argument(
        "--country",
        default=DEFAULT_COUNTRY,
        help='Country code to write into Chrome Local State (default: "us").',
    )
    parser.add_argument(
        "--channels",
        nargs="+",
        choices=sorted(MAC_CHANNELS),
        default=["stable", "beta", "dev", "canary"],
        help="Chrome channels to patch on macOS.",
    )
    parser.add_argument(
        "--profile-dir",
        help="Patch a specific Chrome user data directory instead of auto-detecting.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the planned changes without editing files.",
    )
    parser.add_argument(
        "--no-restart",
        action="store_true",
        help="Do not reopen Chrome after patching.",
    )
    parser.add_argument(
        "--force-kill",
        action="store_true",
        help="Force-kill Chrome if normal quit does not finish.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    country = args.country.lower()

    was_running = close_chrome(force=args.force_kill)
    targets: list[tuple[str, Path, Path | None]]
    if args.profile_dir:
        targets = [("custom", expand(args.profile_dir), None)]
    else:
        targets = channel_targets(args.channels)

    if not targets:
        print("No Chrome profile with Local State was found.", file=sys.stderr)
        return 1

    any_changed = False
    for channel, profile_dir, app_bundle in targets:
        local_state_path = profile_dir / "Local State"
        chrome_version = (
            app_version(app_bundle) if app_bundle is not None else None
        ) or profile_last_version(profile_dir)
        print(f"Chrome [{channel}]")
        print(f"  Profile: {profile_dir}")
        print(f"  Version: {chrome_version or 'unknown'}")
        any_changed = (
            patch_local_state(local_state_path, chrome_version, country, args.dry_run)
            or any_changed
        )

    if was_running and not args.no_restart and not args.dry_run:
        reopen_chrome()

    return 0 if any_changed or args.dry_run else 0


if __name__ == "__main__":
    raise SystemExit(main())
