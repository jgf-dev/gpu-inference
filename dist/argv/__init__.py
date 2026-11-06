"""Render the exact ComfyUI command line."""

from __future__ import annotations

from pathlib import Path

from contracts.settings_contract import Settings


def build_argv(
    settings: Settings,
    *,
    port: int | None = None,
    output_dir: str | Path | None = None,
) -> list[str]:
    """Return ComfyUI argv; --disable-mmap is mandatory for FUSE model stores."""
    return [
        "--listen",
        "0.0.0.0",
        "--port",
        str(settings.port if port is None else port),
        "--disable-mmap",
        "--disable-auto-launch",
        "--extra-model-paths-config",
        str(settings.extra_model_paths),
        "--output-directory",
        str(settings.output_dir if output_dir is None else output_dir),
    ]
