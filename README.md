# SAST Tools Feed
A repository that aggregates release information from static code analysis tools, generates per-tool summary pages and comparison pages as HTML, and publishes them as feeds.

🌐 **Live site**: https://tmyymmt.github.io/sast-tools-feed/

## Covered Tool Categories

This repository covers **SAST (Static Application Security Testing) tools** — also known as static code analysis security tools.

These tools analyze source code, bytecode, or AST (Abstract Syntax Tree) patterns to detect potential security vulnerabilities, bugs, and code quality issues without executing the program.

The following categories are **out of scope**:

- **SCA (Software Composition Analysis)**: Tools that detect vulnerabilities in dependencies/packages (e.g., Trivy, Grype)
  - https://github.com/tmyymmt/sca-tools-feed/
- **DAST (Dynamic Application Security Testing)**: Tools that detect vulnerabilities by sending requests to a running system (e.g., OWASP ZAP)
  - https://github.com/tmyymmt/dast-tools-feed/

## How It Works

- Update feed files and render HTML pages (from Markdown sources) using one of the following methods:
  - Run weekly via GitHub Actions (every Friday at UTC 22:00)
  - Create an Issue, have Copilot create a PR, complete review, and merge to main

## Covered Tools

| Tool | Type | License |
|------|------|---------|
| [SonarQube](https://www.sonarsource.com/products/sonarqube/) | OSS / SaaS | LGPL-3.0 |
| [Semgrep](https://semgrep.dev) | OSS / SaaS | LGPL-2.1 |
| [CodeQL](https://codeql.github.com) | OSS / GitHub Advanced Security | MIT |
| [PMD](https://pmd.github.io) | OSS | BSD-style |
| [Bandit](https://bandit.readthedocs.io) | OSS | Apache-2.0 |
| [Brakeman](https://brakemanscanner.org) | OSS | MIT |
| [gosec](https://github.com/securego/gosec) | OSS | Apache-2.0 |
| [SpotBugs](https://spotbugs.github.io) | OSS | LGPL-3.0 |

## Feed URLs

### All Tools (Combined)

| Format | URL |
|--------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/all.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/all.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sast-tools-feed/feeds/all.json` |

### Per-Tool Feeds

Replace `{tool_id}` with: `semgrep`, `codeql`, `sonarqube`, `bandit`, `brakeman`, `gosec`, `pmd`, `spotbugs`

| Format | URL |
|--------|-----|
| RSS 2.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/{tool_id}.rss` |
| Atom 1.0 | `https://tmyymmt.github.io/sast-tools-feed/feeds/{tool_id}.atom` |
| JSON Feed 1.1 | `https://tmyymmt.github.io/sast-tools-feed/feeds/{tool_id}.json` |

## Pages

- **Comparison**: [English](https://tmyymmt.github.io/sast-tools-feed/comparison.html) / [Japanese](https://tmyymmt.github.io/sast-tools-feed/comparison_ja.html)
- **Per-tool summaries**: `https://tmyymmt.github.io/sast-tools-feed/{tool_id}.html`

## Release Categories

Releases are categorized for easy filtering:

| Category | Description |
|----------|-------------|
| `feature` | Feature additions and changes |
| `bugfix` | Bug fixes |
| `security` | Security fixes and hotfixes |
| `pricing` | Pricing changes |
| `announcement` | Announcements, events, awards |
| `other` | Other |

## Repository Structure

```
.
├── scripts/            # Python scripts
│   ├── main.py         # Entry point
│   ├── models.py       # Data models
│   ├── categorize.py   # Release categorization
│   ├── storage.py      # JSON storage
│   ├── feed_generator.py   # RSS/Atom/JSON Feed generation
│   ├── markdown_generator.py  # HTML page generation
│   └── collectors/     # Data collectors per tool type
│       └── github.py   # GitHub Releases API collector
├── tools/
│   └── tools.yml       # Tool configuration
├── data/               # Persisted release data (JSON)
├── public/             # Generated output (gitignored, deployed to GitHub Pages)
├── tests/              # Test suite
└── docs/               # Specifications
```

## Rules

- Create documentation in both Japanese and English
  - English: `*.md`, Japanese: `*_ja.md`
- Update the full specification when making functional changes
- AI-specific rules are defined in `.github/copilot-instructions.md`

## Setup

### Prerequisites

- Python 3.11 or higher

### Installation

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Install development dependencies (for running tests only)
pip install -r requirements-dev.txt
```

## Local Execution

### Environment Variables

A `GITHUB_TOKEN` is required for the GitHub API.

```bash
export GITHUB_TOKEN=your_github_token
```

### Run

```bash
python -m scripts.main
```

This updates HTML files under `public/` and feed files under `public/feeds/`.

## GitHub Actions

### Automated (Weekly)

`.github/workflows/update-feeds.yml` runs automatically every Friday at UTC 22:00 (JST Saturday 07:00).

### Manual Trigger

Go to the **Actions** tab in the GitHub repository → **Update Feeds** → **Run workflow**.

### Required Configuration

- **Secrets**: `GITHUB_TOKEN` is provided automatically by GitHub Actions — no additional setup needed.
- **Permissions**: `contents: write` (for data commits) and `pages: write` (for GitHub Pages deployment) are preconfigured.
- **GitHub Pages**: If GitHub Pages is not enabled yet, the workflow enables it automatically before the first deployment.

## License

MIT License