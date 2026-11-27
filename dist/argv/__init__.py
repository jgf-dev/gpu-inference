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
    resolved_port = settings.port if port is None else port
    if not 1 <= resolved_port <= 65535:
        raise ValueError(f"port must be between 1 and 65535, got {resolved_port}")

    return [
        "--listen",
        "0.0.0.0",
        "--port",
        str(resolved_port),
        "--disable-mmap",
        "--disable-auto-launch",
        "--extra-model-paths-config",
        str(settings.extra_model_paths),
        "--output-directory",
        str(settings.output_dir if output_dir is None else output_dir),
    ]
