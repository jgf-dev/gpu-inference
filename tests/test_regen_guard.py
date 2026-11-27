from __future__ import annotations

from pathlib import Path

import pytest

from scripts import regen_guard


def _seed_domain_cell(root: Path, cell: str = "alpha") -> None:
    (root / "contracts").mkdir(parents=True, exist_ok=True)
    (root / "specs").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "contracts" / f"{cell}_contract.py").write_text(
        "class Data:\n    pass\n", encoding="utf-8"
    )
    (root / "specs" / f"{cell}.spec.md").write_text(f"# SPEC: {cell}\n", encoding="utf-8")
    (root / "tests" / f"test_{cell}.py").write_text(
        "from hypothesis import given\n\n@given()\ndef test_prop():\n    pass\n",
        encoding="utf-8",
    )


def _seal_cell(root: Path, cell: str = "alpha", code: str = "VALUE = 1\n") -> int:
    assert regen_guard.cmd_prepare(cell) == 0
    (root / "dist" / cell / "__init__.py").write_text(code, encoding="utf-8")
    return regen_guard.cmd_seal(cell, "domain")


def test_ignores_pycache_and_dotfiles(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_domain_cell(tmp_path, "alpha")
    assert _seal_cell(tmp_path, "alpha") == 0

    (tmp_path / "dist" / "__pycache__").mkdir(parents=True)
    (tmp_path / "dist" / "__pycache__" / "junk.pyc").write_bytes(b"pyc")
    (tmp_path / "contracts" / "__pycache__").mkdir(parents=True)
    (tmp_path / "dist" / ".hidden").mkdir(parents=True)

    assert regen_guard.discover_all_cells() == ["alpha"]
    assert regen_guard.cmd_verify() == 0
    assert regen_guard.cmd_stale(as_json=False, names_only=False, fail_on_stale=True) == 0


def test_unsealed_cell_fails_verify_and_stale_fail_on_stale(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_domain_cell(tmp_path, "alpha")

    assert regen_guard.cmd_verify() == 1
    assert "Missing dist/alpha/.spec-lock.json" in capsys.readouterr().err

    assert regen_guard.cmd_stale(as_json=False, names_only=False, fail_on_stale=False) == 0
    assert regen_guard.cmd_stale(as_json=False, names_only=False, fail_on_stale=True) == 1
    assert regen_guard.cmd_stale(as_json=True, names_only=False, fail_on_stale=True) == 1
    assert regen_guard.cmd_stale(as_json=False, names_only=True, fail_on_stale=True) == 1


def test_corrupt_lockfile_fails_verify_cleanly(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_domain_cell(tmp_path, "alpha")
    (tmp_path / "dist" / "alpha").mkdir(parents=True)
    (tmp_path / "dist" / "alpha" / "__init__.py").write_text("X = 1\n", encoding="utf-8")
    (tmp_path / "dist" / "alpha" / ".spec-lock.json").write_text("{bad json", encoding="utf-8")

    assert regen_guard.cmd_verify() == 1
    assert "Corrupt lockfile" in capsys.readouterr().err


@pytest.mark.parametrize("bad_name", ["", "../specs", "a/b", ".hidden", ".."])
def test_rejects_invalid_cell_names(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, bad_name: str
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "specs").mkdir()
    sentinel = tmp_path / "specs" / "keep.spec.md"
    sentinel.write_text("# keep\n", encoding="utf-8")

    assert regen_guard.cmd_prepare(bad_name) == 1
    assert regen_guard.cmd_unlock(bad_name) == 1
    assert regen_guard.cmd_seal(bad_name, "domain") == 1
    assert sentinel.exists()


def test_collect_direct_upstream_avoids_substring_collisions(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_domain_cell(tmp_path, "auth")
    _seed_domain_cell(tmp_path, "oauth")

    auth_files = {p.as_posix() for p in regen_guard.collect_direct_upstream("auth")}
    assert "contracts/auth_contract.py" in auth_files
    assert "specs/auth.spec.md" in auth_files
    assert "tests/test_auth.py" in auth_files
    assert "contracts/oauth_contract.py" not in auth_files
    assert "specs/oauth.spec.md" not in auth_files
    assert "tests/test_oauth.py" not in auth_files


def test_ast_audit_ignores_docstrings_and_catches_real_violations(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_domain_cell(tmp_path, "alpha")

    # Mentions in docstrings/comments and in-memory sqlite are fine.
    clean_code = (
        '"""Never uses os.environ or from dist.beta import x."""\n'
        "import sqlite3\n"
        'CONN = sqlite3.connect(":memory:")\n'
    )
    assert _seal_cell(tmp_path, "alpha", code=clean_code) == 0

    # Relative cross-cell import must fail.
    assert _seal_cell(tmp_path, "alpha", code="from ..beta import thing\n") == 1

    # `from dist import beta` must fail.
    assert _seal_cell(tmp_path, "alpha", code="from dist import beta\n") == 1

    # `from os import getenv` must fail.
    assert _seal_cell(tmp_path, "alpha", code="from os import getenv\n") == 1

    # Hardcoded sqlite file path must fail.
    assert _seal_cell(tmp_path, "alpha", code='import sqlite3\nsqlite3.connect("a.db")\n') == 1


def test_seal_detects_newly_added_upstream_file_after_prepare(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.chdir(tmp_path)
    _seed_domain_cell(tmp_path, "alpha")
    assert regen_guard.cmd_prepare("alpha") == 0
    (tmp_path / "dist" / "alpha" / "__init__.py").write_text("X = 1\n", encoding="utf-8")

    # Add a new upstream test file mid-synthesis.
    (tmp_path / "tests" / "test_alpha_extra.py").write_text(
        "def test_x(): pass\n", encoding="utf-8"
    )

    assert regen_guard.cmd_seal("alpha", "domain") == 1
    assert "TAMPER DETECTED" in capsys.readouterr().err
