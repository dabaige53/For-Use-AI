#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
for tool in uv ffmpeg ffprobe; do
  command -v "$tool" >/dev/null 2>&1 || { echo "Missing dependency: $tool" >&2; exit 1; }
done
uv sync --locked
uv run --no-sync python -c 'import manimlib; print(manimlib.__file__)'
