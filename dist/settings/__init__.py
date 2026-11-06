"""Pure settings parsing for ComfyUI deployments."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from contracts.settings_contract import Settings


def _int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = env.get(key, "")
    if raw == "":
        return default
    try:
        return int(raw)
    except ValueError as exc:
        raise ValueError(f"{key} must be an integer, got {raw!r}") from exc


def parse_settings(env: Mapping[str, str]) -> Settings:
    return Settings(
        gcs_bucket=env.get("GCS_BUCKET", ""),
        gcs_secret_name=env.get("GCS_SECRET_NAME", "gcs-hmac"),
        comfyui_home=Path(env.get("COMFYUI_HOME", "/opt/ComfyUI")),
        models_mount=Path(env.get("MODELS_MOUNT", "/models")),
        output_dir=Path(env.get("COMFYUI_OUTPUT_DIR", "/outputs")),
        port=_int(env, "COMFYUI_PORT", 8188),
        idle_timeout_seconds=_int(env, "IDLE_TIMEOUT_SECONDS", 1200),
        modal_gpu=env.get("MODAL_GPU", "L40S"),
        beam_gpu=env.get("BEAM_GPU", "RTX4090"),
        extra_model_paths=Path(
            env.get("EXTRA_MODEL_PATHS_CONFIG", "/opt/ComfyUI/extra_model_paths.yaml")
        ),
    )
