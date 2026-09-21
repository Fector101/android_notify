"""Read published versions from per-artifact changelogs (Keep a Changelog)."""

from __future__ import annotations

import argparse
import re
from pathlib import Path

_VERSION_HEADING = re.compile(r"^## \[([^\]]+)\]")
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent

PACKAGES = ("android-notify-music-bridge",)

_CHANGELOG_PATHS = {
    "android-notify-music-bridge": _REPO_ROOT / "bridges" / "android" / "CHANGELOG.md",
}


def get_version(package: str = "android-notify-music-bridge") -> str:
    """Return the first release version in the artifact's ``CHANGELOG.md``."""
    if package not in PACKAGES:
        raise ValueError(f"Unknown package {package!r} (expected one of {PACKAGES})")

    changelog = _CHANGELOG_PATHS[package]
    if not changelog.is_file():
        raise FileNotFoundError(f"Missing changelog: {changelog}")

    for line in changelog.read_text(encoding="utf-8").splitlines():
        match = _VERSION_HEADING.match(line.strip())
        if not match:
            continue
        version = match.group(1).strip()
        if version.lower() == "unreleased":
            continue
        return version

    raise RuntimeError(
        f"{changelog} has no release section (expected ## [X.Y.Z] below Unreleased)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "package",
        nargs="?",
        default="android-notify-music-bridge",
        choices=PACKAGES,
        help="Artifact changelog to read (default: android-notify-music-bridge)",
    )
    args = parser.parse_args()
    print(get_version(args.package))


if __name__ == "__main__":
    main()