"""Modal deployment envelope. Not a synthesized cell."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import modal

from dist.main import build_plan

ROOT = Path(__file__).resolve().parents[1]
plan = build_plan(os.environ)
bucket = plan.settings.require_bucket()

app = modal.App("comfyui")

image = modal.Image.from_dockerfile(
    str(ROOT / "deploy" / "Dockerfile"),
    context_dir=str(ROOT),
)

gcs_mount = modal.CloudBucketMount(
    bucket_name=bucket,
    bucket_endpoint_url="https://storage.googleapis.com",
    secret=modal.Secret.from_name(plan.settings.gcs_secret_name),
    read_only=True,
)

outputs = modal.Volume.from_name("comfyui-outputs", create_if_missing=True)


@app.function(
    image=image,
    gpu=plan.settings.modal_gpu,
    volumes={
        str(plan.settings.models_mount): gcs_mount,
        "/outputs": outputs,
    },
    min_containers=0,
    max_containers=1,
    scaledown_window=plan.settings.idle_timeout_seconds,
    timeout=86_400,
)
@modal.concurrent(max_inputs=100)
@modal.web_server(8188, startup_timeout=600, requires_proxy_auth=False)
def ui() -> None:
    subprocess.Popen(
        [sys.executable, "-m", "dist.main"],
        cwd="/app",
        stdout=sys.stdout,
        stderr=sys.stderr,
    )
