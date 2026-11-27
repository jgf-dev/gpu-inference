"""Beam deployment envelope. Not a synthesized cell."""

from __future__ import annotations

import os
from pathlib import Path

from beam import CloudBucket, CloudBucketConfig, Image, Pod, Volume

from dist.main import build_plan

ROOT = Path(__file__).resolve().parents[1]
plan = build_plan(os.environ)
bucket = plan.settings.require_bucket()

image = Image.from_dockerfile(
    str(ROOT / "deploy" / "Dockerfile"),
    context_dir=str(ROOT),
)

models = CloudBucket(
    name=bucket,
    mount_path=str(plan.settings.models_mount),
    config=CloudBucketConfig(
        access_key="GCS_ACCESS_KEY_ID",
        secret_key="GCS_SECRET_ACCESS_KEY",
        endpoint="https://storage.googleapis.com",
        region="us-east-1",
        read_only=True,
    ),
)

outputs = Volume(name="comfyui-outputs", mount_path=str(plan.settings.output_dir))

runtime_env = {
    "GCS_BUCKET": bucket,
    "COMFYUI_PORT": str(plan.port),
    "COMFYUI_OUTPUT_DIR": str(plan.settings.output_dir),
    "COMFYUI_HOME": str(plan.settings.comfyui_home),
    "MODELS_MOUNT": str(plan.settings.models_mount),
    "EXTRA_MODEL_PATHS_CONFIG": str(plan.settings.extra_model_paths),
}

comfyui = Pod(
    name="comfyui",
    image=image,
    gpu=plan.settings.beam_gpu,
    cpu=8,
    memory="32Gi",
    ports=[plan.port],
    env=runtime_env,
    keep_warm_seconds=plan.settings.idle_timeout_seconds,
    secrets=["GCS_ACCESS_KEY_ID", "GCS_SECRET_ACCESS_KEY"],
    volumes=[models, outputs],
    entrypoint=["python", "-m", "dist.main"],
)
