# syntax=docker/dockerfile:1.7
FROM python:3.13-slim-bookworm

ARG COMFYUI_VERSION=v0.44.0
ARG TORCH_INDEX=https://download.pytorch.org/whl/cu128

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app \
    COMFYUI_HOME=/opt/ComfyUI \
    COMFYUI_OUTPUT_DIR=/outputs

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      bash \
      ca-certificates \
      curl \
      ffmpeg \
      git \
      libgl1 \
      libglib2.0-0 \
 && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip \
 && pip install --index-url "${TORCH_INDEX}" \
      torch==2.8.0 \
      torchvision==0.23.0 \
      torchaudio==2.8.0

RUN git clone --depth 1 --branch "${COMFYUI_VERSION}" \
      https://github.com/Comfy-Org/ComfyUI.git /opt/ComfyUI \
 && pip install -r /opt/ComfyUI/requirements.txt

WORKDIR /app
RUN pip install --no-cache-dir pydantic==2.11.0

COPY contracts/ ./contracts/
COPY dist/ ./dist/
COPY config/extra_model_paths.yaml /opt/ComfyUI/extra_model_paths.yaml
COPY deploy/entrypoint.sh /usr/local/bin/comfyui-entrypoint

RUN chmod +x /usr/local/bin/comfyui-entrypoint \
 && chown -R 1000:1000 /app /opt/ComfyUI

USER 1000:1000
EXPOSE 8188

ENTRYPOINT ["/usr/local/bin/comfyui-entrypoint"]
