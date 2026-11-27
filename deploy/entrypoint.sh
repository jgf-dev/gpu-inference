#!/usr/bin/env bash
set -euo pipefail

# Modal appends its own container command to the image ENTRYPOINT, e.g.
#   python -u -R --check-hash-based-pycs never -m modal._container_entrypoint
# Exec that unchanged so Modal's runtime can start the function. For a plain
# Docker/Compose run (no args, or dist.main flags like --dry-run / --once),
# start the sealed app.
case "${1:-}" in
  python|python3|python3.*|*/python|*/python3|*/python3.*)
    exec "$@"
    ;;
esac

exec python -m dist.main "$@"
