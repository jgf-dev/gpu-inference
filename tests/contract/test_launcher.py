import sys
from pathlib import Path
from typing import NoReturn

import pytest

from contracts.argv_contract import LaunchPlan
from contracts.launcher_contract import Launcher
from contracts.settings_contract import Settings
from dist.launcher import launch


def test_launch_conforms_to_launcher_protocol() -> None:
    launcher_fn: Launcher = launch
    assert callable(launcher_fn)


def test_chdir_happens_before_exec() -> None:
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
    assert seen_exec[0][0] == sys.executable
    assert seen_exec[0][1][0] == sys.executable
    assert seen_exec[0][1][1:] == [
        "main.py",
        "--listen",
        "0.0.0.0",
        "--port",
        "8188",
    ]


def test_chdir_failure_aborts_before_exec() -> None:
    plan = LaunchPlan(
        settings=Settings(),
        argv=["--listen", "0.0.0.0", "--port", "8188"],
        cwd=Path("/does/not/exist"),
        port=8188,
    )
    exec_called = False

    def failing_chdir(path: str) -> None:
        raise FileNotFoundError(path)

    def fake_exec(file: str, args: list[str]) -> NoReturn:
        nonlocal exec_called
        exec_called = True
        raise SystemExit(0)

    with pytest.raises(FileNotFoundError):
        launch(plan, exec_fn=fake_exec, chdir_fn=failing_chdir)

    assert exec_called is False


def test_argv_is_forwarded_without_rewriting() -> None:
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
