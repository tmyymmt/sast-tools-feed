import logging
from typing import List, Optional

import requests

from scripts.categorize import classify_release
from scripts.models import ReleaseEntry

logger = logging.getLogger(__name__)


def collect_github_releases(
    tool_id: str,
    tool_name: str,
    repo: str,
    github_token: Optional[str] = None,
) -> List[ReleaseEntry]:
    """GitHub Releases APIからリリース情報を収集する。

    エラー時は空リストを返す（部分失敗を許容）。
    """
    url = f"https://api.github.com/repos/{repo}/releases"
    headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
    if github_token:
        headers["Authorization"] = f"Bearer {github_token}"

    releases = []
    next_url = url
    params = {"per_page": 100}

    while next_url:
        try:
            resp = requests.get(next_url, headers=headers, params=params, timeout=30)
        except requests.RequestException as e:
            logger.warning("Failed to fetch %s: %s", next_url, e)
            return []

        if resp.status_code == 429 or (
            resp.status_code == 403
            and int(resp.headers.get("X-RateLimit-Remaining", "1")) == 0
        ):
            logger.warning("Rate limited for %s, skipping this run", repo)
            return []

        if resp.status_code == 404:
            logger.warning("Repository not found: %s", repo)
            return []

        if not resp.ok:
            logger.warning("Unexpected status %d for %s", resp.status_code, repo)
            return []

        releases.extend(resp.json())
        next_url = resp.links.get("next", {}).get("url")
        params = None

    entries = []
    for r in releases:
        if r.get("draft"):
            continue
        tag_name = r.get("tag_name")
        html_url = r.get("html_url")
        if not tag_name or not html_url:
            continue
        published_at = r.get("published_at") or r.get("created_at")
        if not published_at:
            continue
        title = r.get("name") or tag_name
        body = r.get("body") or ""
        entry = ReleaseEntry(
            tool_id=tool_id,
            tool_name=tool_name,
            version=tag_name,
            published_at=published_at,
            url=html_url,
            summary=title,
            body=body,
            category=classify_release(title, body, "github"),
        )
        entries.append(entry)
    return entries
