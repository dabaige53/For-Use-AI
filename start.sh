#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
exec uv run --locked sh Course/网页/启动网页.command "$@"
