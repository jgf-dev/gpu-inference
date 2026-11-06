import json

from dist.main import build_plan, main


def test_build_plan_from_mapping():
    plan = build_plan({"GCS_BUCKET": "my-bucket", "COMFYUI_PORT": "9000"})
    assert plan.port == 9000
    assert plan.settings.gcs_bucket == "my-bucket"
    assert "--disable-mmap" in plan.argv
    assert plan.cwd.as_posix() == "/opt/ComfyUI"


def test_dry_run_prints_json(monkeypatch, capsys):
    monkeypatch.setenv("GCS_BUCKET", "my-bucket")
    assert main(["--dry-run", "--once"]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["executed"] is False
    assert payload["plan"]["port"] == 8188
    assert payload["plan"]["settings"]["gcs_bucket"] == "my-bucket"


def test_once_prints_status(monkeypatch, capsys):
    monkeypatch.setenv("GCS_BUCKET", "my-bucket")
    assert main(["--once"]) == 0
    assert json.loads(capsys.readouterr().out) == {"status": "ok", "port": 8188}
