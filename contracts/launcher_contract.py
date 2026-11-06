"""Injected process-execution ports for the launcher adapter."""

from __future__ import annotations

from typing import NoReturn, Protocol

from contracts.argv_contract import LaunchPlan


class ExecFn(Protocol):
    def __call__(self, file: str, args: list[str]) -> NoReturn: ...


class ChdirFn(Protocol):
    def __call__(self, path: str) -> None: ...


class Launcher(Protocol):
    def __call__(
        self,
        plan: LaunchPlan,
        *,
        exec_fn: ExecFn,
        chdir_fn: ChdirFn,
    ) -> NoReturn: ...
