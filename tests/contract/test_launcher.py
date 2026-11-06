from pathlib import Path
from typing import NoReturn

import pytest

from contracts.argv_contract import LaunchPlan
from contracts.settings_contract import Settings
from dist.launcher import launch


def test_chdir_happens_before_exec():
    plan = LaunchPlan(
        settings=Settings(),
        argv=["--listen", "0.0.0.0", "--port", "8188"],
        cwd=Path("/opt/ComfyUI"),
        port=8188,
    )
    seen_chdir: list[str] = []
    seen_exec: list[tuple[str, list[str]]] = []

    def fake_chdir(path: str) -> None:
        seen_chdir.append(path)

    def fake_exec(file: str, args: list[str]) -> NoReturn:
        seen_exec.append((file, args))
        raise SystemExit(0)

    with pytest.raises(SystemExit):
        launch(plan, exec_fn=fake_exec, chdir_fn=fake_chdir)

    assert seen_chdir == ["/opt/ComfyUI"]
    assert seen_exec[0][1][1:] == [
        "main.py",
        "--listen",
        "0.0.0.0",
        "--port",
        "8188",
    ]


def test_argv_is_forwarded_without_rewriting():
    argv = ["--listen", "0.0.0.0", "--disable-mmap"]
    plan = LaunchPlan(
        settings=Settings(),
        argv=argv,
        cwd=Path("/opt/ComfyUI"),
        port=8188,
    )
    seen_exec: list[list[str]] = []

    def fake_exec(file: str, args: list[str]) -> NoReturn:
        seen_exec.append(args)
        raise SystemExit(0)

    with pytest.raises(SystemExit):
        launch(plan, exec_fn=fake_exec, chdir_fn=lambda path: None)

    assert seen_exec[0][2:] == argv
