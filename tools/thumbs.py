#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Marco Sumari Tellez and IngeTrazo contributors.
"""Write ``thumbs/<name>.webp``: each screenshot scaled for a card.

The extension manager shows every screenshot at 256 × 160. Downloading the
full picture (up to 600 KB) for that made the cards fill in slowly; the
thumbnail is ~10–20 KB, at twice the card size for high-DPI screens. The
picture is scaled to *cover* 512 × 320 (never cropped here): the card crops
it the same way it cropped the full screenshot.

Only missing or out-of-date thumbnails are written — ``thumbs/index.json``
remembers the SHA-256 each was made from (file dates mean nothing after a
CI checkout) — so an unchanged screenshot never produces a new file and the
publish job has nothing to commit. Needs Pillow (CI installs it; ``catalog.py`` stays stdlib-only).

    thumbs.py           write what is missing, delete orphans
"""
from __future__ import annotations

import hashlib
import json
import sys
import tomllib
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SHOTS = ROOT / "screenshots"
THUMBS = ROOT / "thumbs"
SIZE = (512, 320)
QUALITY = 80


def thumb_name(shot: str) -> str:
    return Path(shot).stem + ".webp"


def make(source: Path, target: Path) -> None:
    with Image.open(source) as im:
        im = im.convert("RGBA" if "A" in im.getbands() else "RGB")
        scale = max(SIZE[0] / im.width, SIZE[1] / im.height)
        if scale < 1:
            im = im.resize((max(1, round(im.width * scale)),
                            max(1, round(im.height * scale))),
                           Image.Resampling.LANCZOS)
        tmp = target.with_suffix(".part")
        im.save(tmp, "WEBP", quality=QUALITY, method=6)
        tmp.replace(target)


def main() -> int:
    THUMBS.mkdir(exist_ok=True)
    index_path = THUMBS / "index.json"
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        index = {}
    fresh = {}
    wanted = {index_path.name}
    written = 0
    # Only the screenshots an entry names: an old picture left in
    # screenshots/ (loop_cut.webp beside loop_cut.png) gets no thumbnail and
    # cannot overwrite the one in use.
    shots = set()
    for entry in sorted((ROOT / "extensions").glob("*.toml")):
        shot = tomllib.loads(entry.read_text(encoding="utf-8")).get("screenshot")
        if isinstance(shot, str) and (SHOTS / shot).is_file():
            shots.add(shot)
    for source in (SHOTS / shot for shot in sorted(shots)):
        target = THUMBS / thumb_name(source.name)
        wanted.add(target.name)
        sha = hashlib.sha256(source.read_bytes()).hexdigest()
        fresh[target.name] = sha
        if target.is_file() and index.get(target.name) == sha:
            continue
        make(source, target)
        written += 1
    removed = 0
    for old in THUMBS.iterdir():
        if old.name not in wanted:
            old.unlink()
            removed += 1
    text = json.dumps(fresh, indent=1, sort_keys=True) + "\n"
    if not index_path.is_file() or index_path.read_text(encoding="utf-8") != text:
        index_path.write_text(text, encoding="utf-8")
    print(f"thumbs: {written} written, {removed} removed, {len(fresh)} total")
    return 0


if __name__ == "__main__":
    sys.exit(main())
