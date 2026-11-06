from pathlib import Path

from contracts.settings_contract import Settings
from dist.argv import build_argv


def test_exact_arguments():
    settings = Settings(
        port=8188,
        output_dir=Path("/outputs"),
        extra_model_paths=Path("/opt/ComfyUI/extra_model_paths.yaml"),
    )
    assert build_argv(settings) == [
        "--listen",
        "0.0.0.0",
        "--port",
        "8188",
        "--disable-mmap",
        "--disable-auto-launch",
        "--extra-model-paths-config",
        "/opt/ComfyUI/extra_model_paths.yaml",
        "--output-directory",
        "/outputs",
    ]


def test_port_and_output_overrides():
    args = build_argv(Settings(), port=9000, output_dir="/tmp/out")
    assert args[args.index("--port") + 1] == "9000"
    assert args[args.index("--output-directory") + 1] == "/tmp/out"


def test_disable_mmap_always_present():
    assert "--disable-mmap" in build_argv(Settings())
