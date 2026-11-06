import pytest
from pydantic import ValidationError

from contracts.settings_contract import Settings


def test_defaults():
    settings = Settings()
    assert settings.port == 8188
    assert settings.idle_timeout_seconds == 1200
    assert settings.comfyui_home.as_posix() == "/opt/ComfyUI"
    assert settings.models_mount.as_posix() == "/models"
    assert settings.output_dir.as_posix() == "/outputs"


def test_rejects_gs_scheme():
    with pytest.raises(ValidationError, match="without gs://"):
        Settings(gcs_bucket="gs://my-bucket")


def test_requires_bucket():
    with pytest.raises(ValueError, match="GCS_BUCKET is required"):
        Settings().require_bucket()


def test_port_bounds():
    with pytest.raises(ValidationError):
        Settings(port=0)
    with pytest.raises(ValidationError):
        Settings(port=65536)


def test_parse_settings_defaults():
    from dist.settings import parse_settings

    assert parse_settings({}) == Settings()


def test_parse_settings_overrides():
    from dist.settings import parse_settings

    settings = parse_settings(
        {
            "GCS_BUCKET": "my-bucket",
            "GCS_SECRET_NAME": "other-secret",
            "COMFYUI_PORT": "9000",
            "IDLE_TIMEOUT_SECONDS": "600",
            "MODAL_GPU": "A10G",
            "BEAM_GPU": "RTX4090",
            "COMFYUI_HOME": "/srv/ComfyUI",
        }
    )
    assert settings.gcs_bucket == "my-bucket"
    assert settings.gcs_secret_name == "other-secret"
    assert settings.port == 9000
    assert settings.idle_timeout_seconds == 600
    assert settings.modal_gpu == "A10G"
    assert settings.comfyui_home.as_posix() == "/srv/ComfyUI"


def test_parse_settings_rejects_bad_port():
    from dist.settings import parse_settings

    with pytest.raises(ValueError, match="COMFYUI_PORT must be an integer"):
        parse_settings({"COMFYUI_PORT": "not-a-number"})
