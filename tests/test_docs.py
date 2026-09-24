"""The docs reference must not drift from the code it documents.

A new flag or config key is easy to add and easy to forget to document, and a
reference that is quietly incomplete is worse than no reference at all. These
tests are the same trick ``test_config.py`` plays on ``TEMPLATE``: assert the
prose against the source of truth rather than trusting a habit.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from earmark import cli, config, sources

REFERENCE = Path(__file__).resolve().parent.parent / "reference"
# The guide sections, each ordered by an NN- prefix on its page names.
GUIDES = [Path(__file__).resolve().parent.parent / d for d in ("github", "local")]


def read(name: str) -> str:
    return (REFERENCE / name).read_text(encoding="utf-8")


def test_every_command_has_a_reference_page():
    for command in cli.HANDLERS:
        assert (REFERENCE / f"{command}.qmd").is_file(), (
            f"no reference/{command}.qmd for `earmark {command}`"
        )


def test_reference_index_links_every_command():
    index = read("index.qmd")
    for command in cli.HANDLERS:
        assert f"]({command}.qmd)" in index, f"reference/index.qmd does not link {command}.qmd"


@pytest.mark.parametrize("key", sorted(config.DEFAULTS))
def test_every_config_key_is_documented(key):
    assert f"`{key}`" in read("configuration.qmd"), (
        f"{key} is in config.DEFAULTS but not in reference/configuration.qmd"
    )


@pytest.mark.parametrize("key", sorted(config.FEED_KEYS))
def test_every_feed_key_is_documented(key):
    assert f"`{key}`" in read("configuration.qmd"), (
        f"feed.{key} is in config.FEED_KEYS but not in reference/configuration.qmd"
    )


@pytest.mark.parametrize(
    "name,allowed",
    [("profile", config.PROFILES), ("model", config.MODELS), ("engine", config.ENGINES)],
)
def test_every_allowed_value_is_documented(name, allowed):
    text = read("configuration.qmd")
    for value in allowed:
        assert f"`{value}`" in text, f"{name} accepts {value!r}, undocumented"


def _flags(parser) -> set[str]:
    """Every long option a parser accepts, minus the ones on every command."""
    found = set()
    for action in parser._actions:
        found.update(o for o in action.option_strings if o.startswith("--"))
    return found - {"--help", "--library"}


def test_every_flag_is_documented():
    parser = cli.build_parser()
    subparsers = next(
        a for a in parser._actions if isinstance(a, __import__("argparse")._SubParsersAction)
    )
    missing = []
    for command, sub in subparsers.choices.items():
        page = read(f"{command}.qmd")
        for flag in sorted(_flags(sub)):
            # `publish` lists the flags it shares with `audio` as prose rather
            # than repeating five tables; a bare mention still counts.
            if flag not in page:
                missing.append(f"{command}: {flag}")
    assert not missing, "undocumented flags: " + ", ".join(missing)


@pytest.mark.parametrize("guide", GUIDES, ids=lambda d: d.name)
def test_guide_pages_are_numbered_uniquely(guide):
    prefixes = [p.name[:2] for p in guide.glob("*.qmd")]
    assert prefixes, f"no guide pages in {guide.name}/"
    assert len(prefixes) == len(set(prefixes)), "two guide pages share an order prefix"
    for path in guide.glob("*.qmd"):
        assert re.match(r"^\d\d-", path.name), f"{path.name} has no NN- order prefix"


@pytest.mark.parametrize("key", sources.OVERRIDES)
def test_every_sources_override_is_on_the_settings_page(key):
    # The settings page is where a user looks for what a sources.yml entry
    # accepts; a new override that is missing there is invisible.
    page = (REFERENCE.parent / "settings" / "index.qmd").read_text(encoding="utf-8")
    assert f"`{key}: " in page, f"sources.yml key {key!r} is not on settings/index.qmd"


def test_guide_media_exist():
    # Screenshots and voice samples are committed files; a renamed or missing
    # one renders as a broken image or a silent player, with no build error.
    root = Path(__file__).resolve().parent.parent
    for guide in [*GUIDES, root / "settings"]:
        for page in guide.glob("*.qmd"):
            text = page.read_text(encoding="utf-8")
            srcs = re.findall(r"!\[[^\]]*\]\(([^)\s]+)", text) + re.findall(r'src="([^"]+)"', text)
            for src in srcs:
                if "://" not in src:
                    path = (guide / src).resolve()
                    assert path.is_file(), f"{page.relative_to(root)} uses missing file {src}"
