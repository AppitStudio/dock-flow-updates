#!/usr/bin/env python3
"""Validate the retained Sparkle history and register it with Keyper."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import datetime
from email.utils import parsedate_to_datetime
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET


SPARKLE_NAMESPACE = "http://www.andymatuschak.org/xml-namespaces/sparkle"
DEFAULT_ENDPOINT = "https://keyper.appitstudio.com/api/releases"


@dataclass(frozen=True)
class Release:
    version: str
    build: str
    released_at: datetime


def required_text(item: ET.Element, path: str, label: str) -> str:
    value = item.findtext(path)
    if value is None or not value.strip():
        raise ValueError(f"Appcast item is missing {label}")
    return value.strip()


def load_releases(appcast_path: Path) -> list[Release]:
    root = ET.parse(appcast_path).getroot()
    items = root.findall("./channel/item")
    if not items:
        raise ValueError("Appcast must retain at least one release item")

    releases: list[Release] = []
    versions: set[str] = set()
    builds: set[str] = set()
    previous_date: datetime | None = None

    for item in items:
        version = required_text(
            item,
            f"{{{SPARKLE_NAMESPACE}}}shortVersionString",
            "sparkle:shortVersionString",
        )
        build = required_text(
            item,
            f"{{{SPARKLE_NAMESPACE}}}version",
            "sparkle:version",
        )
        published_text = required_text(item, "pubDate", "pubDate")
        try:
            released_at = parsedate_to_datetime(published_text)
        except (TypeError, ValueError) as error:
            raise ValueError(f"{version} has an invalid RFC 2822 pubDate") from error
        if released_at.tzinfo is None:
            raise ValueError(f"{version} pubDate must include a timezone")
        stated_weekday = published_text.split(",", maxsplit=1)[0]
        if stated_weekday != released_at.strftime("%a"):
            raise ValueError(f"{version} pubDate weekday does not match its calendar date")
        if previous_date is not None and released_at >= previous_date:
            raise ValueError("Appcast items must be ordered newest to oldest by pubDate")
        previous_date = released_at

        if version in versions:
            raise ValueError(f"Duplicate release version: {version}")
        if build in builds:
            raise ValueError(f"Duplicate Sparkle build: {build}")
        versions.add(version)
        builds.add(build)

        enclosure = item.find("enclosure")
        if enclosure is None:
            raise ValueError(f"{version} is missing its enclosure")
        if not enclosure.get("url", "").startswith("https://"):
            raise ValueError(f"{version} enclosure must use HTTPS")
        if not enclosure.get(f"{{{SPARKLE_NAMESPACE}}}edSignature", "").strip():
            raise ValueError(f"{version} is missing its EdDSA signature")

        releases.append(Release(version=version, build=build, released_at=released_at))

    return releases


def register_release(endpoint: str, token: str, release: Release) -> int:
    body = json.dumps(
        {
            "version": release.version,
            "released_at": release.released_at.isoformat(),
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        method="POST",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "appit-updates-release-sync/1",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as error:
        response_body = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(
            f"Keyper rejected {release.version} with HTTP {error.code}: {response_body}"
        ) from error


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--appcast", type=Path, default=Path("appcast.xml"))
    parser.add_argument("--validate-only", action="store_true")
    args = parser.parse_args()

    try:
        releases = load_releases(args.appcast)
        print(f"Validated {len(releases)} retained releases")
        if args.validate_only:
            return 0

        token = os.environ.get("KEYPER_RELEASE_TOKEN", "").strip()
        if not token:
            raise ValueError("KEYPER_RELEASE_TOKEN is required for release registration")
        endpoint = os.environ.get("KEYPER_RELEASE_ENDPOINT", "").strip() or DEFAULT_ENDPOINT
        if not endpoint.startswith("https://"):
            raise ValueError("KEYPER_RELEASE_ENDPOINT must use HTTPS")

        for release in reversed(releases):
            status = register_release(endpoint, token, release)
            print(f"Registered {release.version} (HTTP {status})")
    except (OSError, ET.ParseError, ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
