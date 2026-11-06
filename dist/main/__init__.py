"""Composition root: the only cell that reads the process environment."""

from __future__ import annotations

import argparse
import json
import os
from collections.abc import Mapping, Sequence

from contracts.argv_contract import LaunchPlan
from contracts.main_contract import CliOptions, MainResult
from dist.argv import build_argv
from dist.launcher import launch
from dist.settings import parse_settings


def build_plan(env: Mapping[str, str]) -> LaunchPlan:
    settings = parse_settings(env)
    return LaunchPlan(
        settings=settings,
        argv=build_argv(settings),
        cwd=settings.comfyui_home,
        port=settings.port,
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="comfyui")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--once", action="store_true")
    namespace = parser.parse_args(argv)
    options = CliOptions(dry_run=namespace.dry_run, once=namespace.once)

    plan = build_plan(os.environ)
    if options.dry_run:
        print(MainResult(plan=plan, executed=False).model_dump_json(indent=2))
        return 0
    if options.once:
        print(json.dumps({"status": "ok", "port": plan.port}))
        return 0

    launch(plan)
    return 0
