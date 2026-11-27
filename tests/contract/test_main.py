import json

import pytest

from contracts.argv_contract import LaunchPlan
from dist.main import build_plan, main

_COMFY_ENV_KEYS = (
    "GCS_BUCKET",
    "GCS_SECRET_NAME",
    "COMFYUI_HOME",
    "MODELS_MOUNT",
    "COMFYUI_OUTPUT_DIR",
    "COMFYUI_PORT",
    "IDLE_TIMEOUT_SECONDS",
    "MODAL_GPU",
    "BEAM_GPU",
    "EXTRA_MODEL_PATHS_CONFIG",
)


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in _COMFY_ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_build_plan_from_mapping() -> None:
    plan = build_plan({"GCS_BUCKET": "my-bucket", "COMFYUI_PORT": "9000"})
    assert plan.port == 9000
    assert plan.settings.gcs_bucket == "my-bucket"
    assert "--disable-mmap" in plan.argv
    assert plan.cwd.as_posix() == "/opt/ComfyUI"


def test_dry_run_prints_json(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("GCS_BUCKET", "my-bucket")
    assert main(["--dry-run", "--once"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["executed"] is False
    assert payload["plan"]["port"] == 8188
    assert payload["plan"]["settings"]["gcs_bucket"] == "my-bucket"


def test_once_prints_status(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setenv("GCS_BUCKET", "my-bucket")
    assert main(["--once"]) == 0
    assert json.loads(capsys.readouterr().out) == {"status": "ok", "port": 8188}


def test_default_mode_invokes_launcher_once(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GCS_BUCKET", "my-bucket")
    launched: list[LaunchPlan] = []

    def fake_launch(plan: LaunchPlan) -> None:
        launched.append(plan)

    monkeypatch.setattr("dist.main.launch", fake_launch)
    assert main([]) == 0
    assert len(launched) == 1
    assert launched[0].port == 8188


def test_unknown_flag_exits_2() -> None:
    with pytest.raises(SystemExit) as exc_info:
        main(["--does-not-exist"])
    assert exc_info.value.code == 2


def test_bad_port_raises_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMFYUI_PORT", "not-a-port")
    with pytest.raises(ValueError, match="COMFYUI_PORT must be an integer"):
        main(["--once"])
