"""Immutable runtime settings shared by every cell."""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    gcs_bucket: str = ""
    gcs_secret_name: str = "gcs-hmac"
    comfyui_home: Path = Path("/opt/ComfyUI")
    models_mount: Path = Path("/models")
    output_dir: Path = Path("/outputs")
    port: int = Field(default=8188, ge=1, le=65535)
    idle_timeout_seconds: int = Field(default=1200, ge=1, le=1200)
    modal_gpu: str = "L40S"
    beam_gpu: str = "RTX4090"
    extra_model_paths: Path = Path("/opt/ComfyUI/extra_model_paths.yaml")

    @field_validator("gcs_bucket")
    @classmethod
    def _normalize_bucket(cls, value: str) -> str:
        value = value.strip()
        if value.startswith("gs://"):
            raise ValueError("gcs_bucket must be the bucket name without gs://")
        return value

    def require_bucket(self) -> str:
        if not self.gcs_bucket:
            raise ValueError("GCS_BUCKET is required")
        return self.gcs_bucket
