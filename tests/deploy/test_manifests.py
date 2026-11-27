import ast
from pathlib import Path

from tests.ast_utils import calls, keyword, parse

EXPECTED_RUNTIME_ENV_KEYS = {
    "GCS_BUCKET",
    "COMFYUI_PORT",
    "COMFYUI_OUTPUT_DIR",
    "COMFYUI_HOME",
    "MODELS_MOUNT",
    "EXTRA_MODEL_PATHS_CONFIG",
}


def _assigned_dict_keys(tree: ast.Module, name: str) -> set[str]:
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            assert isinstance(node.value, ast.Dict)
            return {
                k.value
                for k in node.value.keys
                if isinstance(k, ast.Constant) and isinstance(k.value, str)
            }
    raise AssertionError(f"Expected module-level dict assignment `{name}`")


def test_modal_mounts_gcs_read_only_and_scales_to_zero():
    tree = parse("deploy/modal_app.py")
    mounts = calls(tree, "CloudBucketMount")
    assert len(mounts) == 1
    endpoint = keyword(mounts[0], "bucket_endpoint_url")
    assert isinstance(endpoint, ast.Constant)
    assert endpoint.value == "https://storage.googleapis.com"
    read_only = keyword(mounts[0], "read_only")
    assert isinstance(read_only, ast.Constant)
    assert read_only.value is True

    assert _assigned_dict_keys(tree, "runtime_env") >= EXPECTED_RUNTIME_ENV_KEYS

    functions = calls(tree, "function")
    assert len(functions) == 1
    env = keyword(functions[0], "env")
    assert isinstance(env, ast.Name)
    assert env.id == "runtime_env"
    volumes = keyword(functions[0], "volumes")
    assert isinstance(volumes, ast.Dict)
    assert all(not isinstance(k, ast.Constant) for k in volumes.keys)
    min_containers = keyword(functions[0], "min_containers")
    assert isinstance(min_containers, ast.Constant)
    assert min_containers.value == 0
    max_containers = keyword(functions[0], "max_containers")
    assert isinstance(max_containers, ast.Constant)
    assert max_containers.value == 1
    assert keyword(functions[0], "scaledown_window") is not None

    servers = calls(tree, "web_server")
    assert len(servers) == 1
    assert ast.unparse(servers[0].args[0]) == "plan.port"


def test_beam_mounts_gcs_as_s3_compatible_and_forwards_plan():
    tree = parse("deploy/beam_app.py")
    buckets = calls(tree, "CloudBucket")
    assert len(buckets) == 1

    configs = calls(tree, "CloudBucketConfig")
    assert len(configs) == 1
    endpoint = keyword(configs[0], "endpoint")
    assert isinstance(endpoint, ast.Constant)
    assert endpoint.value == "https://storage.googleapis.com"
    read_only = keyword(configs[0], "read_only")
    assert isinstance(read_only, ast.Constant)
    assert read_only.value is True
    access_key = keyword(configs[0], "access_key")
    assert isinstance(access_key, ast.Constant)
    assert access_key.value == "GCS_ACCESS_KEY_ID"

    images = calls(tree, "from_dockerfile")
    assert len(images) == 1
    context_dir = keyword(images[0], "context_dir")
    assert context_dir is not None
    assert "ROOT" in ast.unparse(context_dir)

    volumes = calls(tree, "Volume")
    assert len(volumes) == 1
    mount_path = keyword(volumes[0], "mount_path")
    assert mount_path is not None
    assert ast.unparse(mount_path) == "str(plan.settings.output_dir)"

    assert _assigned_dict_keys(tree, "runtime_env") >= EXPECTED_RUNTIME_ENV_KEYS

    pods = calls(tree, "Pod")
    assert len(pods) == 1
    ports = keyword(pods[0], "ports")
    assert isinstance(ports, ast.List)
    assert ast.unparse(ports.elts[0]) == "plan.port"
    env = keyword(pods[0], "env")
    assert isinstance(env, ast.Name)
    assert env.id == "runtime_env"
    assert keyword(pods[0], "keep_warm_seconds") is not None


def test_dockerfile_creates_non_root_user_and_writable_outputs():
    dockerfile = Path("deploy/Dockerfile").read_text(encoding="utf-8")
    assert "HOME=/home/comfy" in dockerfile
    assert "useradd --uid 1000 --gid 1000" in dockerfile
    assert "mkdir -p /outputs /models" in dockerfile
    assert "chown -R 1000:1000 /app /opt/ComfyUI /outputs /home/comfy" in dockerfile
    assert "USER 1000:1000" in dockerfile
    assert "pydantic>=2.11,<3" in dockerfile
