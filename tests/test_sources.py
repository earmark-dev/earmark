"""sources.yml: the list a GitHub library publishes from.

Every problem is collected rather than raised, as in config.py, because a
half-read list is worse than a stopped one: sync removes the episode of any
entry it cannot see.
"""

from __future__ import annotations

import datetime

from earmark import sources


def write(root, text):
    (root / sources.FILENAME).write_text(text, encoding="utf-8")


def test_the_template_is_an_empty_list_not_an_error(tmp_path):
    """The template is all comments, which YAML reads as None. Treating that as
    an error would break every freshly initialized library."""
    write(tmp_path, sources.TEMPLATE)
    listed = sources.load(tmp_path)
    assert listed.entries == [] and listed.errors == [] and listed.exists


def test_a_missing_file_is_distinguishable_from_an_empty_one(tmp_path):
    """Sync must refuse to run without the file rather than read "no entries"
    and delete every listed episode."""
    assert not sources.load(tmp_path).exists


def test_bare_strings_and_mappings_mix(tmp_path):
    (tmp_path / "files").mkdir()
    (tmp_path / "files" / "a.pdf").write_bytes(b"%PDF")
    write(tmp_path, "- https://example.com/a\n"
                    "- files/a.pdf\n"
                    "- source: https://example.com/b\n  voice: bf_emma\n  speed: 1.2\n")
    listed = sources.load(tmp_path)
    assert listed.errors == []
    assert [e.source for e in listed.entries] == [
        "https://example.com/a", "files/a.pdf", "https://example.com/b"]
    assert listed.entries[2].overrides == {"voice": "bf_emma", "speed": 1.2}


def test_a_file_entry_resolves_against_the_library_not_the_cwd(tmp_path, monkeypatch):
    """The Action and a local run start in different folders."""
    (tmp_path / "a.pdf").write_bytes(b"%PDF")
    write(tmp_path, "- a.pdf\n")
    monkeypatch.chdir("/")
    entry = sources.load(tmp_path).entries[0]
    assert entry.path(tmp_path) == str(tmp_path / "a.pdf")
    assert entry.path(tmp_path) != entry.source


def test_a_yaml_date_becomes_a_string(tmp_path):
    """YAML turns `date: 2026-01-01` into a datetime.date, which the feed's
    date handling does not expect."""
    write(tmp_path, "- source: https://example.com/a\n  date: 2026-01-01\n")
    date = sources.load(tmp_path).entries[0].overrides["date"]
    assert date == "2026-01-01" and not isinstance(date, datetime.date)


def test_an_unknown_key_warns_and_is_dropped(tmp_path):
    write(tmp_path, "- source: https://example.com/a\n  vioce: bf_emma\n")
    listed = sources.load(tmp_path)
    assert any("vioce" in w for w in listed.warnings)
    assert listed.entries[0].overrides == {}


def test_problems_are_errors_naming_the_entry(tmp_path):
    write(tmp_path, "- https://example.com/a\n"
                    "- https://example.com/a\n"
                    "- files/missing.pdf\n"
                    "- title: no source here\n"
                    "- 42\n")
    errors = sources.load(tmp_path).errors
    assert any("entry 2" in e and "twice" in e for e in errors)
    assert any("entry 3" in e and "missing.pdf" in e for e in errors)
    assert any("entry 4" in e and "source" in e for e in errors)
    assert any("entry 5" in e for e in errors)


def test_a_mapping_at_the_top_is_an_error(tmp_path):
    write(tmp_path, "sources:\n  - https://example.com/a\n")
    assert sources.load(tmp_path).errors


def test_broken_yaml_is_an_error_not_a_crash(tmp_path):
    write(tmp_path, "- [unclosed\n")
    listed = sources.load(tmp_path)
    assert listed.errors and "YAML" in listed.errors[0]
