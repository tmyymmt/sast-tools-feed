# Full Specification

This directory contains the full specification of this project.

## Writing Guidelines

- The specification should be navigable starting from this file
- Manage specifications hierarchically to prevent individual files from becoming too large and hard to read
- When there is a large amount of specification content, start with a high-level, concise description and create child files for the details
- When creating child files
  - Include links to prerequisite information files

---

## 1. Target Tools

### In Scope

| Tool | Type | Source | Collection Method |
|---|---|---|---|
| Semgrep | OSS | https://github.com/semgrep/semgrep | GitHub Releases API |
| CodeQL | OSS / GitHub Advanced Security | https://github.com/github/codeql-action | GitHub Releases API |
| SonarQube | OSS / SaaS (SonarCloud) | https://github.com/SonarSource/sonarqube | GitHub Releases API |
| Bandit | OSS | https://github.com/PyCQA/bandit | GitHub Releases API |
| Brakeman | OSS | https://github.com/presidentbeef/brakeman | GitHub Releases API |
| gosec | OSS | https://github.com/securego/gosec | GitHub Releases API |
| PMD | OSS | https://github.com/pmd/pmd | GitHub Releases API |
| SpotBugs | OSS | https://github.com/spotbugs/spotbugs | GitHub Releases API |

### Out of Scope (reference only)

The following categories of tools are out of scope:

- **SCA (Software Composition Analysis)**: Tools that detect vulnerabilities in dependencies/packages (e.g., Trivy, Grype)
- **DAST (Dynamic Application Security Testing)**: Tools that detect vulnerabilities by sending requests to a running system (e.g., OWASP ZAP)

---

## 2. Feed Specification

### Formats

All three formats are supported:

- RSS 2.0
- Atom 1.0
- JSON Feed 1.1

### Feed Fields

- Version (tag name)
- Date/time (published date)
- URL (link to release page)
- Summary (title and overview)
- Change details (CHANGELOG / release notes body)
- Release type category (see below)

### Release Type Categories

Feeds are categorized by release type, also used for filtering:

- `feature`: Feature additions and changes
- `pricing`: Pricing changes
- `security`: Security fixes and hotfixes
  - Classification requires CVE identifiers, hotfix/critical keywords, the word "security" with context (fix/patch/vulnerability/advisory/update/alert/bug), or "脆弱性"/"セキュリティ" with equivalent context — standalone "セキュリティ" (e.g., event names) is not classified as security
- `bugfix`: Bug fixes
- `announcement`: Announcements, conference appearances, awards, etc.
- `other`: Other

### Update Frequency

- Weekly execution via GitHub Actions (every Saturday at JST 07:00 / UTC Friday 22:00)
- Or: create an Issue → Copilot creates a PR → review → merge to main

### Publication Endpoint

- Published via GitHub Pages
- If GitHub Pages is not enabled yet, the update workflow enables it automatically before deployment

---

## 3. Data Collection

### Collection Methods

| Target Type | Method |
|---|---|
| GitHub OSS (Semgrep, CodeQL, etc.) | GitHub Actions + GitHub Releases API (structured data) |

### GitHub Releases API

- Endpoint: `https://api.github.com/repos/{owner}/{repo}/releases`
- Available fields: `tag_name` (version), `published_at` (date), `body` (CHANGELOG), `html_url`
- Pagination: requests `per_page=100` and follows `Link: rel="next"` until exhausted
- Rate limits: 60 req/hour unauthenticated, 5000 req/hour with token; HTTP 429 and HTTP 403 with `X-RateLimit-Remaining: 0` are both treated as rate-limit signals (skip run, keep existing data)
- Draft releases (`draft: true`) are skipped; entries missing `tag_name` or `html_url` are also skipped
- If `published_at` is null (pre-releases), `created_at` is used as fallback; entries with neither field are skipped
- **Prefer API over scraping** (scraping breaks when HTML structure changes)

### Execution Model

- Polling (weekly scheduled execution) is the primary model
- Event-driven (GitHub webhooks, etc.) is not adopted as it adds complexity without significant benefit

---

## 4. Data Storage

- Collected data is stored as files within the repository (JSON intermediate format)
- All sources are normalized to a unified JSON intermediate format, from which RSS/Atom/JSON Feed files are generated
  - Minimizes impact when upstream sources change
- History is retained permanently and accumulates indefinitely (never deleted)
- Target tools are managed in a configuration file (YAML, etc.) so new tools can be added without code changes
- `merge_entries` deduplicates by URL across both existing and new entries (including pre-existing duplicates and duplicates within the new batch)

---

## 5. Publication and Distribution

- Target users: general public
- Subscription methods: RSS readers, or direct access to repository files
- Filtering: available by release type category

### Published URL

https://tmyymmt.github.io/sast-tools-feed/

### Output File Structure (public/)

`public/` is not committed to the repository (gitignored). It is generated at runtime by GitHub Actions and deployed to GitHub Pages.

| Path | Content |
|---|---|
| `feeds/all.{rss,atom,json}` | Combined feed for all tools |
| `feeds/{tool_id}.{rss,atom,json}` | Per-tool feeds (always generated for every configured tool, including empty feeds when no entries are available) |
| `{tool_id}.html` / `{tool_id}_ja.html` | Per-tool summary pages (English/Japanese) |
| `comparison.html` / `comparison_ja.html` | All-tools comparison pages (Summary table + Detailed Comparison table) |
| `index.html` | Top page (feed list and links to comparison pages) |
| `.nojekyll` | Disables Jekyll processing on GitHub Pages |

HTML pages automatically apply dark mode by detecting browser/OS settings via the `prefers-color-scheme` media query.

The tool list in `index.html` uses the same sort order as the comparison tables: feature checkmark count descending, then supported language count descending, then alphabetically by tool name.

### Per-Tool Page Structure

Each per-tool page (`{tool_id}.html` / `{tool_id}_ja.html`) contains:

- Tool overview (title, description, type, license, homepage link)
  - **Type** is derived from an optional top-level `distribution` field in tools.yml (`oss` → "OSS", `saas` → "SaaS", `hybrid` → "OSS / SaaS"); if absent, falls back to the `saas` feature flag
- **Features table**: all 12 feature flags with ✅/❌ status:
  - Multi-Language Support, Dataflow/Taint Analysis, IDE Plugin, CI/CD Plugin, Custom Rules, SaaS/Cloud Version, API Server, Dashboard, Centralized Management, SARIF Output, Auto-Fix, IaC Scanning
- Feature reference link to official documentation (`features_url` in tools.yml, fallback to `homepage`)
- Release History (list of releases with version, date, and description)
- Source URL link below the Release History heading, pointing to the upstream release page

### Comparison Page Structure

The comparison pages (`comparison.html` / `comparison_ja.html`) contain two tables:

- **Summary table**: Tool name (with link to per-tool page and feature reference link), latest version, last updated, type, license, pricing, supported programming languages, and basic feature flags (Multi-Lang, Dataflow, Custom Rules, SARIF Output).
- **Detailed Comparison table**: Tool name (with link to per-tool page and feature reference link), supported programming languages, all feature flags plus a Unique Features column. Feature flags covered:
  - Multi-Lang, Dataflow, IDE Plugin, CI/CD Plugin, Custom Rules, SaaS, API Server, Dashboard, Centralized Mgmt, SARIF, Auto-Fix, IaC

When a tool's pricing text includes `Paid` and `pricing_url` is configured in `tools/tools.yml`, the pricing text is rendered as a link to the official pricing page.

If `pricing_free_url` and `pricing_paid_url` are both configured and the pricing text contains ` / `, the pricing cell is rendered as two links: Free-part text links to `pricing_free_url`, and Paid-part text links to `pricing_paid_url`.

Both tables use the same sort order: feature checkmark count descending, then supported language count descending, then alphabetical.

---

## 6. Non-Functional Requirements

See [spec-nonfunctional.md](spec-nonfunctional.md) for details.

- Prefer GitHub API over scraping; scraping is a last resort
- Tolerate partial failures; keep updating other tools' feeds on failure
- Use atomic writes to prevent publishing partially written files
- HTML output escapes tool names, IDs, and page titles via `html.escape` to prevent invalid markup
- Rendered Markdown HTML is sanitized before page output to strip potentially dangerous tags/attributes from raw HTML input
- The `feed-failure` GitHub label is created automatically if it does not exist before an alert issue is opened
