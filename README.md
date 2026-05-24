# sast-tools-feed
A repository that aggregates release information from static code analysis tools, generates per-tool summary pages and comparison pages as HTML, and publishes them as feeds.

## Tool Category

This repository covers **SAST (Static Application Security Testing) tools** — also known as static code analysis security tools.

These tools analyze source code, bytecode, or AST (Abstract Syntax Tree) patterns to detect potential security vulnerabilities, bugs, and code quality issues without executing the program.

The following categories are **out of scope**:

- **SCA (Software Composition Analysis)**: Tools that detect vulnerabilities in dependencies/packages (e.g., Trivy, Grype)
- **DAST (Dynamic Application Security Testing)**: Tools that detect vulnerabilities by sending requests to a running system (e.g., OWASP ZAP)

## Published Site

https://tmyymmt.github.io/sast-tools-feed/ is published as GitHub Pages. You can browse feed listings, per-tool summary pages, and the comparison page. All HTML pages support dark mode via `prefers-color-scheme`.

## How It Works

- Update feed files and render HTML pages (from Markdown sources) using one of the following methods:
  - Run weekly via GitHub Actions (every Friday at UTC 22:00)
  - Create an Issue, have Copilot create a PR, complete review, and merge to main

## File Structure

### Spec Template
- GitHub Spec Kit style feature spec template: `.specify/templates/spec-template.md`

### Full Specification
- docs/full-specs/spec.md
- The full specification always reflects the latest spec

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
- **GitHub Pages**: In repository Settings → Pages, set Source to `GitHub Actions`.

## License

MIT License