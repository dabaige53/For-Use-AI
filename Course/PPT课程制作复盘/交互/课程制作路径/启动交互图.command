#!/bin/sh
set -eu
DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
COURSE="$(CDPATH= cd -- "$DIR/../../.." && pwd)"
PYTHON=${PYTHON:-python3}
command -v "$PYTHON" >/dev/null 2>&1 || { echo "Python 3 is required; set PYTHON to its executable." >&2; exit 1; }
exec "$PYTHON" "$DIR/../../图解/mermaid-preview.py" "$DIR/../../图解/课程制作主路径.mmd" --details "$DIR/节点材料.json" --materials-root "$COURSE" --port "${PORT:-0}" --open
