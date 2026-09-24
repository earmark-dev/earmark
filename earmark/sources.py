"""The library's reading list, ``<library>/sources.yml``.

``earmark publish`` with no SOURCE makes the feed match this file: an entry
with no episode is published, and an episode whose entry was deleted is
removed. That is what lets a library live in a GitHub repo and publish itself
from an Action -- editing one file in the web editor is the whole interface.

An entry is identified by its ``source`` string exactly as written. That string
is recorded on the episode as ``listed``, which is the only link back: an
episode published by hand has no ``listed`` and sync never touches it.

Like :mod:`earmark.config`, loading never raises. Problems are collected into
``warnings`` (a key that was ignored) and ``errors`` (an entry that cannot be
used), so the caller decides when to stop.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from earmark.source import is_url

FILENAME = "sources.yml"

# Per-entry overrides. Each is the dest of a `publish` flag, so an entry can
# say anything the command line can say about one document, and no more.
OVERRIDES = ("title", "author", "date", "voice", "speed", "lang", "profile")

TEMPLATE = """\
# earmark reading list
#
# `earmark publish` with no SOURCE makes the feed match this list: a new entry
# is narrated and published, and deleting an entry deletes its episode.
#
# An entry is a URL, a file path relative to this folder, or a mapping with
# `source:` plus any of: title, author, date, voice, speed, lang, profile.
#
# - https://example.com/some-article
# - files/a-paper.pdf
# - source: https://example.com/long-read
#   title: A better title
#   voice: bf_emma
#   profile: paper
"""


@dataclass
class Entry:
    source: str
    overrides: dict[str, Any] = field(default_factory=dict)

    def path(self, root: Path) -> str:
        """What to hand the pipeline: a URL as is, a file relative to the library."""
        return self.source if is_url(self.source) else str(root / self.source)


@dataclass
class Sources:
    entries: list[Entry] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    path: Path | None = None

    @property
    def exists(self) -> bool:
        return self.path is not None and self.path.is_file()


def load(root: Path) -> Sources:
    """Read ``sources.yml`` from a library root. A missing file is an empty list."""
    path = Path(root) / FILENAME
    if not path.is_file():
        return Sources(path=path)
    try:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return Sources(path=path, errors=[f"{FILENAME} is not valid YAML: {exc}"])

    # A file of nothing but comments -- the template -- parses to None.
    if raw is None:
        return Sources(path=path)
    if not isinstance(raw, list):
        return Sources(path=path, errors=[f"{FILENAME} must be a list of entries, one per `- ` line"])

    out = Sources(path=path)
    seen: set[str] = set()
    for number, item in enumerate(raw, 1):
        entry = _entry(item, number, out)
        if entry is None:
            continue
        if entry.source in seen:
            out.errors.append(f"entry {number}: {entry.source} is listed twice")
            continue
        seen.add(entry.source)
        if not is_url(entry.source) and not (Path(root) / entry.source).is_file():
            out.errors.append(f"entry {number}: no such file {entry.source}")
            continue
        out.entries.append(entry)
    return out


def _entry(item: Any, number: int, out: Sources) -> Entry | None:
    if isinstance(item, str):
        source, extra = item, {}
    elif isinstance(item, dict):
        extra = dict(item)
        source = extra.pop("source", None)
        if not isinstance(source, str):
            out.errors.append(f"entry {number} has no `source:`")
            return None
    else:
        out.errors.append(f"entry {number} is neither a URL, a path nor a mapping")
        return None

    source = source.strip()
    if not source:
        out.errors.append(f"entry {number} is empty")
        return None

    overrides = {}
    for key, value in extra.items():
        if key not in OVERRIDES:
            out.warnings.append(f"entry {number}: unknown key {key!r} ignored")
            continue
        # YAML reads `date: 2026-01-01` as a date, not a string.
        overrides[key] = value if key == "speed" else str(value)
    return Entry(source=source, overrides=overrides)
