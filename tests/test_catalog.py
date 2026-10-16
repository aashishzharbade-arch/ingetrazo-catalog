# SPDX-License-Identifier: GPL-3.0-or-later
"""The checks every pull request goes through. No network: ``fetch`` is
replaced by a dict of fake files."""
from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "tools"))
import catalog  # noqa: E402

GOOD_PY = b'''"""Hello."""
def setup(app):
    pass
'''


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _entry(ident="hola", data=GOOD_PY, url=None, **over) -> str:
    url = url or f"https://example.org/v1.0/{ident}.py"
    fields = {
        "id": ident, "version": "1.0", "author": "Ana",
        "license": "MIT", "repository": "https://example.org/repo",
        "download": url, "sha256": _sha(data), "ingetrazo": "0.5.7",
        "tags": ["bim"],
    }
    fields.update(over)
    lines = []
    for k, v in fields.items():
        if v is None:
            continue
        lines.append(f"{k} = {json.dumps(v, ensure_ascii=False)}")
    lines += ['[name]', 'es = "Hola"', '[summary]', 'en = "Says hello."']
    return "\n".join(lines) + "\n"


@pytest.fixture
def repo(tmp_path, monkeypatch):
    """A catalog in tmp_path; ``files`` maps URL → bytes for fetch()."""
    (tmp_path / "extensions").mkdir()
    (tmp_path / "screenshots").mkdir()
    monkeypatch.setattr(catalog, "ENTRIES", tmp_path / "extensions")
    monkeypatch.setattr(catalog, "SHOTS", tmp_path / "screenshots")
    monkeypatch.setattr(catalog, "REVIEWED", tmp_path / "reviewed.toml")
    monkeypatch.setattr(catalog, "OUT", tmp_path / "catalog.json")
    files: dict = {}

    def fake_fetch(url):
        if url not in files:
            raise OSError("404")
        return files[url]
    monkeypatch.setattr(catalog, "fetch", fake_fetch)
    return tmp_path, files


def _add(repo, text, ident="hola", data=GOOD_PY,
         url="https://example.org/v1.0/hola.py"):
    root, files = repo
    (root / "extensions" / f"{ident}.toml").write_text(text, "utf-8")
    files[url] = data


def test_a_good_entry_passes(repo, capsys):
    _add(repo, _entry())
    assert catalog.check() == 0
    assert "All good" in capsys.readouterr().out


def test_the_hash_must_match_and_the_error_tells_the_right_one(repo, capsys):
    _add(repo, _entry(sha256="0" * 64))
    assert catalog.check() == 1
    assert _sha(GOOD_PY) in capsys.readouterr().out


def test_code_without_an_entry_point_is_refused(repo, capsys):
    data = b"x = 1\n"
    _add(repo, _entry(data=data), data=data)
    assert catalog.check() == 1
    assert "no setup(app)" in capsys.readouterr().out


def test_a_tool_subclass_counts_as_an_entry_point(repo):
    data = b"from tools.base import Tool\nclass Mine(Tool):\n    pass\n"
    _add(repo, _entry(data=data), data=data)
    assert catalog.check() == 0


@pytest.mark.parametrize("over, words", [
    ({"license": "Proprietary"}, "free licence"),
    ({"license": "GPL-2.0-only"}, "free licence"),
    ({"tags": ["games"]}, "unknown tags"),
    ({"id": "Other"}, "'id'"),
    ({"download": "http://example.org/v1.0/hola.py"}, "https://"),
    ({"download": "https://raw.githubusercontent.com/a/b/main/hola.py"},
     "branch"),
    ({"ingetrazo": "latest"}, "'ingetrazo'"),
    ({"version": None}, "missing 'version'"),
    ({"price": 5}, "unknown fields"),
])
def test_bad_fields_are_explained(repo, capsys, over, words):
    _add(repo, _entry(**over))
    assert catalog.check(offline=True) == 1
    assert words in capsys.readouterr().out


def test_the_code_is_reported_never_run(repo, capsys, tmp_path):
    marker = tmp_path / "ran"
    data = (b"import subprocess\nopen(%r, 'w').write('x')\n"
            b"def setup(app):\n    subprocess.run(['ls'])\n"
            % str(marker).encode())
    _add(repo, _entry(data=data), data=data)
    assert catalog.check() == 0
    out = capsys.readouterr().out
    assert "imports subprocess" in out
    assert not marker.exists()


def test_qt_exec_is_not_reported_but_builtin_exec_is(repo, capsys):
    data = b"def setup(app):\n    dlg.exec()\n    exec('1')\n"
    _add(repo, _entry(data=data), data=data)
    catalog.check()
    out = capsys.readouterr().out
    assert out.count("runs text as code") == 1


def _zip(members: dict) -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        for name, text in members.items():
            zf.writestr(name, text)
    return buf.getvalue()


def test_a_package_zip_is_accepted(repo):
    data = _zip({"hola/__init__.py": GOOD_PY, "hola/util.py": b"x = 1\n"})
    url = "https://example.org/v1.0/hola.zip"
    _add(repo, _entry(data=data, url=url), data=data, url=url)
    assert catalog.check() == 0


@pytest.mark.parametrize("members", [
    {"../evil/__init__.py": GOOD_PY},
    {"a/__init__.py": GOOD_PY, "b/__init__.py": GOOD_PY},
    {"loose.py": GOOD_PY},
])
def test_bad_zips_are_refused(repo, members):
    data = _zip(members)
    url = "https://example.org/v1.0/hola.zip"
    _add(repo, _entry(data=data, url=url), data=data, url=url)
    assert catalog.check() == 1


def test_reviewed_badge_follows_the_hash(repo):
    root, _ = repo
    _add(repo, _entry())
    (root / "reviewed.toml").write_text(
        f'[hola]\nsha256 = "{_sha(GOOD_PY)}"\n', "utf-8")
    assert catalog.build()["extensions"][0]["reviewed"] is True
    new = GOOD_PY + b"# v2\n"
    _add(repo, _entry(data=new), data=new)
    assert catalog.build()["extensions"][0]["reviewed"] is False


def test_the_real_catalog_is_valid_offline():
    """The entries in this repository, without downloading."""
    assert catalog.check(offline=True) == 0


def _commit(root, message, when):
    import subprocess
    env = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when,
           "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@example.org",
           "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@example.org",
           "PATH": "/usr/bin:/bin", "HOME": str(root)}
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
    subprocess.run(["git", "commit", "-qm", message], cwd=root, check=True,
                   env=env)


def test_dates_come_from_git_history_and_follow_a_rename(repo):
    """«Most recent» (#656): added = first merge, updated = when the
    current version was merged; a metadata-only edit or a rename does not
    count as an update."""
    import subprocess
    root, _ = repo
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    _add(repo, _entry())
    _commit(root, "add", "2026-10-01T10:00:00+00:00")
    _add(repo, _entry(version="1.1"))
    _commit(root, "1.1", "2026-10-05T12:30:00-05:00")
    _add(repo, _entry(version="1.1", tags=["bim", "terrain"]))
    _commit(root, "tags only", "2026-10-07T09:00:00+00:00")
    old = root / "extensions" / "hola.toml"
    old.rename(root / "extensions" / "hola_lite.toml")
    _commit(root, "rename", "2026-10-09T09:00:00+00:00")
    dates = catalog.entry_dates(root / "extensions" / "hola_lite.toml")
    assert dates == {"added_at": "2026-10-01T10:00Z",
                     "updated_at": "2026-10-05T17:30Z"}


def test_an_entry_git_does_not_know_gets_no_dates(repo):
    root, _ = repo
    _add(repo, _entry())
    assert catalog.entry_dates(root / "extensions" / "hola.toml") == {}
    assert "added_at" not in catalog.build()["extensions"][0]
