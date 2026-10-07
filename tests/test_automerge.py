# SPDX-License-Identifier: GPL-3.0-or-later
"""Which pull requests the catalog merges by itself: only a new version of
an entry, from the GitHub account that entry names. Everything else waits
for a person."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import automerge  # noqa: E402


@pytest.fixture
def entries(tmp_path):
    d = tmp_path / "extensions"
    d.mkdir()
    (d / "escalera.toml").write_text(
        'id = "escalera"\nauthor_url = "https://github.com/Ana-Lima"\n',
        encoding="utf-8")
    (d / "sin_cuenta.toml").write_text('id = "sin_cuenta"\n', encoding="utf-8")
    return d


def _decide(author, changes, entries):
    return automerge.decide(author, changes, entries)


def test_a_new_version_from_its_author_goes_in(entries):
    ident, why = _decide("ana-lima", [("modified", "extensions/escalera.toml")],
                         entries)
    assert ident == "escalera" and why == ""


def test_with_a_new_screenshot_too(entries):
    ident, _ = _decide("Ana-Lima", [
        ("modified", "extensions/escalera.toml"),
        ("added", "screenshots/escalera.png")], entries)
    assert ident == "escalera"


@pytest.mark.parametrize("author, changes", [
    # someone else's entry
    ("otro", [("modified", "extensions/escalera.toml")]),
    # a new extension, even from a known author
    ("ana-lima", [("added", "extensions/nueva.toml")]),
    # the maintainers' files
    ("ana-lima", [("modified", "extensions/escalera.toml"),
                  ("modified", "reviewed.toml")]),
    ("ana-lima", [("modified", "extensions/escalera.toml"),
                  ("modified", "tools/catalog.py")]),
    ("ana-lima", [("modified", ".github/workflows/automerge.yml")]),
    # deleting an entry
    ("ana-lima", [("removed", "extensions/escalera.toml")]),
    # another extension's screenshot
    ("ana-lima", [("modified", "extensions/escalera.toml"),
                  ("added", "screenshots/otra.png")]),
    # only a screenshot
    ("ana-lima", [("added", "screenshots/escalera.png")]),
    # an entry that names no account
    ("ana-lima", [("modified", "extensions/sin_cuenta.toml")]),
    ("ana-lima", []),
])
def test_everything_else_waits_for_a_person(entries, author, changes):
    ident, why = _decide(author, changes, entries)
    assert ident is None and why


def test_the_command_line_says_which(entries, tmp_path, capsys, monkeypatch):
    monkeypatch.setattr(automerge, "ENTRIES", entries)
    files = tmp_path / "files.tsv"
    files.write_text("modified\textensions/escalera.toml\n", encoding="utf-8")
    assert automerge.main(["decide", "Ana-Lima", str(files)]) == 0
    assert capsys.readouterr().out.strip() == "id=escalera"
    assert automerge.main(["decide", "otro", str(files)]) == 0
    out = capsys.readouterr()
    assert out.out == "" and "maintainer" in out.err
