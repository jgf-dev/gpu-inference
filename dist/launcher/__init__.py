"""Process-launch adapter. No policy, no environment reads."""

from __future__ import annotations

import os
import sys

from contracts.argv_contract import LaunchPlan
from contracts.launcher_contract import ChdirFn, ExecFn


def launch(
    plan: LaunchPlan,
    *,
    exec_fn: ExecFn = os.execvp,
    chdir_fn: ChdirFn = os.chdir,
) -> None:
    chdir_fn(str(plan.cwd))
    exec_fn(sys.executable, [sys.executable, "main.py", *plan.argv])
