import responses

from scripts.collectors.github import collect_github_releases

MOCK_RELEASES = [
    {
        "tag_name": "v1.90.0",
        "published_at": "2024-01-15T10:00:00Z",
        "html_url": "https://github.com/semgrep/semgrep/releases/tag/v1.90.0",
        "name": "Semgrep v1.90.0",
        "body": "## Changes\n- feat: add new rule category",
        "draft": False,
    },
    {
        "tag_name": "v1.89.0",
        "published_at": "2023-12-01T10:00:00Z",
        "html_url": "https://github.com/semgrep/semgrep/releases/tag/v1.89.0",
        "name": "Semgrep v1.89.0",
        "body": "## Bug Fixes\n- fix: false positive in taint analysis",
        "draft": False,
    },
]


@responses.activate
def test_collect_github_releases_returns_entries():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        json=MOCK_RELEASES,
        status=200,
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert len(entries) == 2
    assert entries[0].version == "v1.90.0"
    assert entries[0].tool_id == "semgrep"
    assert entries[0].tool_name == "Semgrep"
    assert entries[0].url == "https://github.com/semgrep/semgrep/releases/tag/v1.90.0"
    assert entries[0].category in ("feature", "bugfix", "security", "other", "announcement", "pricing")


@responses.activate
def test_collect_github_releases_returns_empty_on_404():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/unknown/notfound/releases",
        json={"message": "Not Found"},
        status=404,
    )
    entries = collect_github_releases(
        tool_id="notfound",
        tool_name="NotFound",
        repo="unknown/notfound",
        github_token=None,
    )
    assert entries == []


@responses.activate
def test_collect_github_releases_returns_empty_on_rate_limit():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        status=429,
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert entries == []


@responses.activate
def test_collect_github_releases_returns_empty_on_403_rate_limit():
    """HTTP 403 with X-RateLimit-Remaining: 0 should be treated as rate-limited."""
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        status=403,
        headers={"X-RateLimit-Remaining": "0"},
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert entries == []


@responses.activate
def test_collect_github_releases_403_non_rate_limit_is_unexpected():
    """HTTP 403 without rate-limit header should fall through to 'unexpected status'."""
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        status=403,
        headers={"X-RateLimit-Remaining": "100"},
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert entries == []


@responses.activate
def test_collect_github_releases_skips_drafts():
    """Draft releases should be excluded from the results."""
    releases = [
        {
            "tag_name": "v2.0.0-draft",
            "published_at": None,
            "html_url": "https://github.com/semgrep/semgrep/releases/tag/v2.0.0-draft",
            "name": "Draft release",
            "body": "",
            "draft": True,
        },
        *MOCK_RELEASES,
    ]
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        json=releases,
        status=200,
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert len(entries) == 2
    assert all(e.version != "v2.0.0-draft" for e in entries)


@responses.activate
def test_collect_github_releases_falls_back_to_created_at_when_published_at_null():
    """When published_at is null, created_at should be used instead."""
    releases = [
        {
            "tag_name": "v1.91.0",
            "published_at": None,
            "created_at": "2024-02-01T00:00:00Z",
            "html_url": "https://github.com/semgrep/semgrep/releases/tag/v1.91.0",
            "name": "Pre-release",
            "body": "",
            "draft": False,
        }
    ]
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        json=releases,
        status=200,
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert len(entries) == 1
    assert entries[0].published_at == "2024-02-01T00:00:00Z"


@responses.activate
def test_collect_github_releases_skips_entries_with_missing_required_fields():
    """Entries without tag_name or html_url should be skipped."""
    releases = [
        {
            "tag_name": None,
            "published_at": "2024-01-01T00:00:00Z",
            "html_url": "https://github.com/semgrep/semgrep/releases/tag/v1.92.0",
            "name": "Missing tag",
            "body": "",
            "draft": False,
        },
        *MOCK_RELEASES,
    ]
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        json=releases,
        status=200,
    )
    entries = collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token=None,
    )
    assert len(entries) == 2


@responses.activate
def test_collect_github_releases_uses_token_in_header():
    responses.add(
        responses.GET,
        "https://api.github.com/repos/semgrep/semgrep/releases",
        json=MOCK_RELEASES,
        status=200,
    )
    collect_github_releases(
        tool_id="semgrep",
        tool_name="Semgrep",
        repo="semgrep/semgrep",
        github_token="test-token",
    )
    assert responses.calls[0].request.headers.get("Authorization") == "Bearer test-token"
