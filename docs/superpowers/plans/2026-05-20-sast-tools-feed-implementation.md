# sast-tools-feed Implementation Plan

**Date**: 2026-05-20  
**Status**: Completed

## Overview

This document records the implementation plan for creating the sast-tools-feed repository as a SAST (Static Application Security Testing) version of the sca-tools-feed repository.

## Background

The sca-tools-feed repository aggregates release information from SCA tools and publishes them as RSS/Atom/JSON feeds with comparison pages. This project adapts the same architecture for SAST tools.

## Target SAST Tools

| Tool | Repo | Type | Languages |
|------|------|------|-----------|
| Semgrep | semgrep/semgrep | OSS/SaaS | 30+ |
| CodeQL | github/codeql-action | OSS/SaaS | 10+ |
| SonarQube | SonarSource/sonarqube | OSS/SaaS | 30+ |
| Bandit | PyCQA/bandit | OSS | Python |
| Brakeman | presidentbeef/brakeman | OSS | Ruby/Rails |
| gosec | securego/gosec | OSS | Go |
| PMD | pmd/pmd | OSS | Java+ |
| SpotBugs | spotbugs/spotbugs | OSS | Java |

## Feature Flags (SAST-specific)

The following 12 feature flags are defined for SAST tools (replacing SCA-specific flags):

| Flag | Description |
|------|-------------|
| `multi_language` | Supports multiple programming languages |
| `dataflow_taint` | Taint / dataflow analysis |
| `ide_plugin` | IDE plugin available |
| `ci_cd_plugin` | CI/CD plugin/integration |
| `custom_rules` | Custom rules/queries support |
| `saas` | Available as SaaS/Cloud version |
| `api_server` | API server support |
| `dashboard` | Dashboard UI |
| `centralized_management` | Centralized management of findings |
| `sarif_output` | SARIF output support |
| `auto_fix` | Auto-fix / code fix suggestions |
| `iac` | IaC (Infrastructure as Code) scanning |

## Architecture (same as sca-tools-feed)

```
tools/tools.yml          ← SAST tool configuration
scripts/
  main.py               ← Entry point (adapted for SAST)
  models.py             ← ReleaseEntry dataclass
  storage.py            ← JSON persistence
  categorize.py         ← Release type classification
  feed_generator.py     ← RSS/Atom/JSON Feed generation
  markdown_generator.py ← HTML page generation (SAST features)
  collectors/
    github.py           ← GitHub Releases API collector
data/                   ← Persisted JSON data (gitkeep)
public/                 ← Generated output (gitignored)
```

## Key Differences from sca-tools-feed

1. **tools/tools.yml**: 8 SAST tools instead of SCA tools
2. **Feature flags**: SAST-specific (multi_language, dataflow_taint, ide_plugin, etc.)
3. **scripts/main.py**: FEED_TITLE = "SAST Tools Feed", no SaaS scraper imports
4. **scripts/markdown_generator.py**: SAST feature labels in EN/JA
5. **No SaaS scrapers**: No futurevuls.py / yamory.py (all tools use GitHub Releases API)
6. **Comparison page**: SAST-adapted column headers

## Checklist

- [x] Create .gitignore
- [x] Create requirements.txt / requirements-dev.txt
- [x] Create scripts/ modules (main, models, storage, categorize, feed_generator, markdown_generator)
- [x] Create scripts/collectors/github.py
- [x] Create tools/tools.yml with 8 SAST tools
- [x] Create data/.gitkeep
- [x] Create tests/ (test_categorize, test_collector_github, test_feed_generator, test_markdown_generator, test_storage)
- [x] Create .github/copilot-instructions.md
- [x] Create .github/workflows/update-feeds.yml
- [x] Create .specify/templates/
- [x] Create .vscode/settings.json
- [x] Create docs/full-specs/ (spec.md, spec_ja.md, spec-nonfunctional.md, spec-nonfunctional_ja.md)
- [x] Update README.md
- [x] Create README_ja.md
