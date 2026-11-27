from __future__ import annotations

import os
import stat
import subprocess
from pathlib import Path

ENTRYPOINT = Path(__file__).resolve().parents[2] / "deploy" / "entrypoint.sh"


def _make_fake_python(bin_dir: Path, name: str = "python") -> Path:
    script = bin_dir / name
    script.write_text('#!/usr/bin/env bash\nprintf "%s\\n" "$0" "$@"\n', encoding="utf-8")
    script.chmod(script.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return script


def test_entrypoint_execs_modal_python_command_unchanged(tmp_path: Path) -> None:
    fake_py = _make_fake_python(tmp_path, "python")
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ.get('PATH', '')}"}

    proc = subprocess.run(
        [
            str(ENTRYPOINT),
            "python",
            "-u",
            "-m",
            "modal._container_entrypoint",
        ],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    lines = proc.stdout.strip().splitlines()
    assert lines == [str(fake_py), "-u", "-m", "modal._container_entrypoint"]


def test_entrypoint_execs_absolute_python3_path_unchanged(tmp_path: Path) -> None:
    fake_py3 = _make_fake_python(tmp_path, "python3.13")

    proc = subprocess.run(
        [str(ENTRYPOINT), str(fake_py3), "-m", "modal._container_entrypoint"],
        capture_output=True,
        text=True,
        check=True,
    )
    lines = proc.stdout.strip().splitlines()
    assert lines == [str(fake_py3), "-m", "modal._container_entrypoint"]


def test_entrypoint_defaults_to_dist_main_with_flags(tmp_path: Path) -> None:
    fake_py = _make_fake_python(tmp_path, "python")
    env = {**os.environ, "PATH": f"{tmp_path}:{os.environ.get('PATH', '')}"}

    proc = subprocess.run(
        [str(ENTRYPOINT), "--dry-run", "--once"],
        capture_output=True,
        text=True,
        check=True,
        env=env,
    )
    lines = proc.stdout.strip().splitlines()
    assert lines == [str(fake_py), "-m", "dist.main", "--dry-run", "--once"]
