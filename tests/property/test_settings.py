from hypothesis import given, strategies as st

from contracts.settings_contract import Settings


@given(st.integers(min_value=1, max_value=65535))
def test_port_roundtrip(port):
    assert Settings(port=port).port == port


@given(st.text(min_size=1).filter(lambda s: not s.strip().startswith("gs://")))
def test_bucket_is_always_stripped(bucket):
    assert Settings(gcs_bucket=bucket).gcs_bucket == bucket.strip()


@given(st.integers(min_value=1, max_value=65535))
def test_parse_settings_port_roundtrip(port):
    from dist.settings import parse_settings

    assert parse_settings({"COMFYUI_PORT": str(port)}).port == port


@given(st.text(min_size=1).filter(lambda s: not s.strip().startswith("gs://")))
def test_parse_settings_bucket_roundtrip(bucket):
    from dist.settings import parse_settings

    assert parse_settings({"GCS_BUCKET": bucket}).gcs_bucket == bucket.strip()
