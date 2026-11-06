import ast

from tests.ast_utils import calls, keyword, parse


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

    functions = calls(tree, "function")
    assert len(functions) == 1
    min_containers = keyword(functions[0], "min_containers")
    assert isinstance(min_containers, ast.Constant)
    assert min_containers.value == 0
    max_containers = keyword(functions[0], "max_containers")
    assert isinstance(max_containers, ast.Constant)
    assert max_containers.value == 1
    assert keyword(functions[0], "scaledown_window") is not None

    servers = calls(tree, "web_server")
    assert len(servers) == 1
    assert isinstance(servers[0].args[0], ast.Constant)
    assert servers[0].args[0].value == 8188


def test_beam_mounts_gcs_as_s3_compatible_and_serves_8188():
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

    pods = calls(tree, "Pod")
    assert len(pods) == 1
    ports = keyword(pods[0], "ports")
    assert isinstance(ports, ast.List)
    assert isinstance(ports.elts[0], ast.Constant)
    assert ports.elts[0].value == 8188
    assert keyword(pods[0], "keep_warm_seconds") is not None
