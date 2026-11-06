"""Launch plan shared by the argv and launcher cells."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from contracts.settings_contract import Settings


class LaunchPlan(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    settings: Settings
    argv: list[str] = Field(min_length=1)
    cwd: Path
    port: int = Field(ge=1, le=65535)
