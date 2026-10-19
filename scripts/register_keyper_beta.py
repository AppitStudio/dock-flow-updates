#!/usr/bin/env python3
"""Register the published, mutable DockFlow beta with Keyper.

On a `release: published` event the release comes from the event payload.
On a manual `workflow_dispatch` run (no release event) the current `beta`
release is fetched from the GitHub API, so an already-published beta can be
registered. Both paths go through the same validation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime


DEFAULT_ENDPOINT = "https://keyper.appitstudio.com/api/releases"
DEFAULT_GITHUB_API = "https://api.github.com"
REPOSITORY = "AppitStudio/dock-flow-updates"
BETA_TAG = "beta"
DMG_ASSET = "DockFlow.dmg"
VERSION_RE = re.compile(r"B(1\.\d+)")
USER_AGENT = "appit-updates-release-sync/1"


def beta_payload(event: dict) -> dict[str, object]:
    release = event["release"]
    if event["repository"]["full_name"] != REPOSITORY:
        raise ValueError("Unexpected release repository")
    if release["tag_name"] != BETA_TAG or release["prerelease"] is not True:
        raise ValueError("Expected the published DockFlow beta release")
    name = release["name"]
    match = VERSION_RE.fullmatch(name) if isinstance(name, str) else None
    if match is None:
        raise ValueError("Beta release title must be B followed by a DockFlow version")
    if not any(asset.get("name") == DMG_ASSET for asset in release["assets"]):
        raise ValueError(f"Published beta release has no {DMG_ASSET} asset")
    published_at = release["published_at"]
    if not isinstance(published_at, str) or datetime.fromisoformat(
        published_at.replace("Z", "+00:00")
    ).tzinfo is None:
        raise ValueError("Published beta release has no timestamp with timezone")

    # The beta tag is replaced on every upload. Keep its mutable download URL
    # out of the immutable Keyper history while allowing version checks.
    return {
        "version": match.group(1),
        "released_at": published_at,
        "is_prerelease": True,
    }


def fetch_beta_release(api_url: str, repository: str, token: str) -> dict:
    """Return the current `beta` release from the GitHub REST API."""
    if repository != REPOSITORY:
        raise ValueError("Unexpected release repository")
    if not api_url.startswith("https://"):
        raise ValueError("GITHUB_API_URL must use HTTPS")
    url = (
        f"{api_url.rstrip('/')}/repos/{repository}/releases/tags/"
        f"{urllib.parse.quote(BETA_TAG)}"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            release = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        raise RuntimeError(
            f"GitHub returned HTTP {error.code} for the {BETA_TAG} release"
        ) from error
    if not isinstance(release, dict):
        raise ValueError("GitHub returned an unexpected release payload")
    return release


def load_event(environ: dict[str, str]) -> dict:
    """Build the release event: the real one, or one from the API on dispatch."""
    if environ.get("GITHUB_EVENT_NAME") == "release":
        return json.loads(Path(environ["GITHUB_EVENT_PATH"]).read_text())
    repository = environ.get("GITHUB_REPOSITORY", "").strip()
    api_url = environ.get("GITHUB_API_URL", "").strip() or DEFAULT_GITHUB_API
    token = environ.get("GITHUB_TOKEN", "").strip()
    release = fetch_beta_release(api_url, repository, token)
    return {"repository": {"full_name": repository}, "release": release}


def register(endpoint: str, token: str, payload: dict[str, object]) -> int:
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload).encode("utf-8"),
        method="POST",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.status
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")[:500]
        raise RuntimeError(f"Keyper rejected beta with HTTP {error.code}: {body}") from error


def main() -> int:
    try:
        event = load_event(dict(os.environ))
        payload = beta_payload(event)
        token = os.environ.get("KEYPER_RELEASE_TOKEN", "").strip()
        if not token:
            raise ValueError("KEYPER_RELEASE_TOKEN is required")
        endpoint = os.environ.get("KEYPER_RELEASE_ENDPOINT", "").strip() or DEFAULT_ENDPOINT
        if not endpoint.startswith("https://"):
            raise ValueError("KEYPER_RELEASE_ENDPOINT must use HTTPS")
        status = register(endpoint, token, payload)
        print(f"Registered DockFlow beta {payload['version']} (HTTP {status})")
    except (KeyError, TypeError, OSError, ValueError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
