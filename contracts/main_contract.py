"""CLI and result schemas for the composition root."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from contracts.argv_contract import LaunchPlan


class CliOptions(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    dry_run: bool = False
    once: bool = False


class MainResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    plan: LaunchPlan
    executed: bool
