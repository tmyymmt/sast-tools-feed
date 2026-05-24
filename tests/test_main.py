from scripts import main as main_module


def test_write_feeds_generates_per_tool_files_even_without_entries(tmp_path, monkeypatch):
    monkeypatch.setattr(main_module, "FEEDS_DIR", tmp_path / "feeds")
    monkeypatch.setattr(main_module, "FEED_BASE_URL", "https://example.com/feeds")

    tools = [{"id": "semgrep", "name": "Semgrep"}]
    main_module.write_feeds([], tools=tools)

    for ext in ("rss", "atom", "json"):
        assert (tmp_path / "feeds" / f"all.{ext}").exists()
        assert (tmp_path / "feeds" / f"semgrep.{ext}").exists()
