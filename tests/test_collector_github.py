import responses

from scripts.collectors.github import collect_github_releases

MOCK_RELEASES = [
    {
        "tag_name": "v1.90.0",
        "published_at": "2024-01-15T10:00:00Z",
        "html_url": "https://github.com/semgrep/semgrep/releases/tag/v1.90.0",
        "name": "Semgrep v1.90.0",
        "body": "## Changes\n- feat: add new rule category",
    },
    {
        "tag_name": "v1.89.0",
        "published_at": "2023-12-01T10:00:00Z",
        "html_url": "https://github.com/semgrep/semgrep/releases/tag/v1.89.0",
        "name": "Semgrep v1.89.0",
        "body": "## Bug Fixes\n- fix: false positive in taint analysis",
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
