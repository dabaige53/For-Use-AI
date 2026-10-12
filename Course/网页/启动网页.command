#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON=${PYTHON:-python3}
command -v "$PYTHON" >/dev/null 2>&1 || { echo "Python 3 is required; set PYTHON to its executable." >&2; exit 1; }
printf '%s\n' "阅读网页：http://127.0.0.1:${PORT:-4189}/网页/index.html" "PPT：http://127.0.0.1:${PORT:-4189}/PPT/AI协作-动态幻灯片.html"
exec "$PYTHON" -m http.server "${PORT:-4189}" --bind 127.0.0.1
