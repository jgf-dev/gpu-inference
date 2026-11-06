# comfyui-spec-first

Spec-first ComfyUI deployment for Modal and Beam. The application logic is
three sealed cells (`settings`, `argv`, `launcher`) plus a composition root
(`main`). `deploy/` contains the zero-inference image and platform envelopes.

## How it works

1. `dist/settings` parses the environment into an immutable `Settings`.
2. `dist/argv` renders `--listen 0.0.0.0 --port 8188 --disable-mmap ...`.
3. `dist/launcher` chdirs to ComfyUI and replaces the process.
4. `dist/main` is the only cell that reads `os.environ`.

`--disable-mmap` is mandatory: ComfyUI's default safetensors mmap is 30–50x
slower on FUSE and can deadlock under concurrent page faults.

## Bucket layout

```
gs://<bucket>/checkpoints/  clip/  clip_vision/  controlnet/
               embeddings/  loras/  text_encoders/  unet/
               upscale_models/  vae/
```

## Local verification

```bash
uv sync --frozen
uv run pyright contracts/ dist/
uv run pytest
find dist -type d -name __pycache__ -prune -exec rm -rf {} +
python3 scripts/regen_guard.py verify
python3 scripts/regen_guard.py stale
uv run python -m dist.main --dry-run --once
docker build -f deploy/Dockerfile -t comfyui-spec:local .
docker run --rm comfyui-spec:local --dry-run --once
```

## GCS HMAC setup

```bash
export PROJECT_ID=your-project
export GCS_BUCKET=my-comfy-models
export SA="comfyui-fuse@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud iam service-accounts create comfyui-fuse --display-name="ComfyUI FUSE"
gcloud storage buckets add-iam-policy-binding "gs://${GCS_BUCKET}" \
  --member="serviceAccount:${SA}" \
  --role="roles/storage.objectViewer"

read -r ACCESS_ID SECRET <<< "$(gcloud storage hmac create "$SA" --format='value(accessId,secret)')"
```

Create platform secrets:

```bash
modal secret create gcs-hmac \
  GOOGLE_ACCESS_KEY_ID="$ACCESS_ID" \
  GOOGLE_ACCESS_KEY_SECRET="$SECRET"

beam secret create GCS_ACCESS_KEY_ID "$ACCESS_ID"
beam secret create GCS_SECRET_ACCESS_KEY "$SECRET"
```

## Deploy

Modal:

```bash
export GCS_BUCKET=my-comfy-models
modal deploy deploy/modal_app.py
```

Beam:

```bash
export GCS_BUCKET=my-comfy-models
beam volume create comfyui-outputs
beam deploy deploy/beam_app.py:comfyui
```

Both print a public HTTPS URL.

## Smoke test

```bash
curl -fsS "$URL/system_stats"
curl -fsS "$URL/queue"
curl -fsS "$URL/object_info/CheckpointLoaderSimple"
```

The last call must list at least one checkpoint from GCS.

## Regeneration workflow

```bash
python3 scripts/regen_guard.py stale
python3 scripts/regen_guard.py prepare <cell>
# synthesize dist/<cell>/ from scratch/context_<cell>.md
uv run pytest tests/
python3 scripts/regen_guard.py seal <cell> [--adapter|--entrypoint]
```

Never edit `dist/` by hand. Never modify `contracts/`, `specs/`, or `tests/`
after `prepare`; `seal` will reject the tamper.

## Security

The deployed URL is public. Add Cloudflare Access, a basic-auth sidecar, or
Modal proxy auth before exposing real data. ComfyUI has no built-in auth.
