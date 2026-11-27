from hypothesis import given
from hypothesis import strategies as st

from contracts.settings_contract import Settings


def _valid_bucket_text(value: str) -> bool:
    stripped = value.strip()
    return not stripped.lower().startswith("gs://") and "/" not in stripped


@given(st.integers(min_value=1, max_value=65535))
def test_port_roundtrip(port: int) -> None:
    assert Settings(port=port).port == port


@given(st.text(min_size=1).filter(_valid_bucket_text))
def test_bucket_is_always_stripped(bucket: str) -> None:
    assert Settings(gcs_bucket=bucket).gcs_bucket == bucket.strip()


@given(st.integers(min_value=1, max_value=65535))
def test_parse_settings_port_roundtrip(port: int) -> None:
    from dist.settings import parse_settings

    assert parse_settings({"COMFYUI_PORT": str(port)}).port == port


@given(st.text(min_size=1).filter(_valid_bucket_text))
def test_parse_settings_bucket_roundtrip(bucket: str) -> None:
    from dist.settings import parse_settings

    assert parse_settings({"GCS_BUCKET": bucket}).gcs_bucket == bucket.strip()
