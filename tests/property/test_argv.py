from hypothesis import given, strategies as st

from contracts.settings_contract import Settings
from dist.argv import build_argv


@given(st.integers(min_value=1, max_value=65535))
def test_port_is_rendered_as_decimal(port):
    args = build_argv(Settings(port=port))
    assert args[args.index("--port") + 1] == str(port)


@given(st.text(min_size=1, max_size=40).filter(lambda s: "\x00" not in s))
def test_disable_mmap_survives_any_output_dir(output_dir):
    assert "--disable-mmap" in build_argv(Settings(), output_dir=output_dir)
