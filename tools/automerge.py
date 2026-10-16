#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Marco Sumari Tellez and IngeTrazo contributors.
"""Decide whether a pull request is a NEW VERSION from a known author, the
one kind the catalog merges by itself.

A person approves an author's first entry. After that, a pull request that
only updates that same entry — sent by the GitHub account its
``author_url`` names, touching nothing but ``extensions/<id>.toml`` and the
entry's screenshot — goes in without waiting, as «Community» (the hash
changed, so the «Reviewed» badge drops until a maintainer reads it again).
Everything else waits for a person: a new extension, someone else's entry,
``reviewed.toml``, the tools, the workflows.

This script only reads the list of changed files and the entry already on
``main``; ``check`` (tools/catalog.py) then reads the new file, and
``.github/workflows/automerge.yml`` merges only if that check is clean and
its report has nothing for a reviewer to read.

Usage::

    automerge.py decide AUTHOR FILES.tsv     # FILES.tsv: "status<TAB>path"

Prints ``id=<id>`` when the pull request qualifies, or the reason it does
not on stderr. Exit code 0 either way; the output says which.
"""
from __future__ import annotations

import re
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENTRIES = ROOT / "extensions"

_ENTRY = re.compile(r"^extensions/([a-z][a-z0-9_]{1,47})\.toml$")
_SHOT = re.compile(r"^screenshots/([a-z][a-z0-9_]{1,47})\.(png|jpe?g|webp)$")


def _github_login(url) -> str | None:
    """The account an ``author_url`` names, lower-case, or None."""
    if not isinstance(url, str):
        return None
    m = re.fullmatch(r"https://github\.com/([A-Za-z0-9-]{1,39})/?", url.strip())
    return m.group(1).lower() if m else None


def decide(author: str, changes: list[tuple[str, str]],
           entries: Path | None = None) -> tuple[str | None, str]:
    """``(id, "")`` when the pull request is a new version of an entry its
    author already has, else ``(None, reason)``."""
    entries = ENTRIES if entries is None else entries
    if not changes:
        return None, "no files changed"
    ids = set()
    toml_status = None
    for status, path in changes:
        m = _ENTRY.match(path)
        if m:
            ids.add(m.group(1))
            toml_status = status
            continue
        m = _SHOT.match(path)
        if m and status in ("added", "modified"):
            ids.add(m.group(1))
            continue
        return None, f"{path} is not an entry or its screenshot"
    if len(ids) != 1:
        return None, "it touches more than one extension"
    ident = ids.pop()
    if toml_status != "modified":
        return None, ("a new extension: the first entry of each one is "
                      "approved by a person")
    current = entries / f"{ident}.toml"
    if not current.is_file():
        return None, f"{ident} is not in the catalog yet"
    try:
        entry = tomllib.loads(current.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError):
        return None, f"the entry of {ident} on main does not read"
    owner = _github_login(entry.get("author_url"))
    if owner is None:
        return None, f"{ident} names no GitHub account in author_url"
    if owner != author.strip().lower():
        return None, f"{ident} belongs to @{owner}, not @{author}"
    return ident, ""


def _read_changes(path: Path) -> list[tuple[str, str]]:
    out = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            status, _, name = line.partition("\t")
            out.append((status.strip(), name.strip()))
    return out


def main(argv=None) -> int:
    args = sys.argv[1:] if argv is None else argv
    if len(args) != 3 or args[0] != "decide":
        print(__doc__.split("Usage::")[1], file=sys.stderr)
        return 2
    ident, why = decide(args[1], _read_changes(Path(args[2])))
    if ident:
        print(f"id={ident}")
    else:
        print(f"Left for a maintainer: {why}.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
