"""Beam deployment envelope. Not a synthesized cell."""

from __future__ import annotations

import os

from beam import CloudBucket, CloudBucketConfig, Image, Pod, Volume

from dist.main import build_plan

plan = build_plan(os.environ)
bucket = plan.settings.require_bucket()

image = Image.from_dockerfile("deploy/Dockerfile", context_dir=".")

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

outputs = Volume(name="comfyui-outputs", mount_path="/outputs")

comfyui = Pod(
    name="comfyui",
    image=image,
    gpu=plan.settings.beam_gpu,
    cpu=8,
    memory="32Gi",
    ports=[8188],
    keep_warm_seconds=plan.settings.idle_timeout_seconds,
    secrets=["GCS_ACCESS_KEY_ID", "GCS_SECRET_ACCESS_KEY"],
    volumes=[models, outputs],
    entrypoint=["python", "-m", "dist.main"],
)
