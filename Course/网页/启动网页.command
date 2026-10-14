#!/bin/sh
set -eu
cd "$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)"
PYTHON=${PYTHON:-python3}
command -v "$PYTHON" >/dev/null 2>&1 || { echo "Python 3 is required; set PYTHON to its executable." >&2; exit 1; }
printf '%s\n' "阅读网页：http://127.0.0.1:${PORT:-4189}/网页/index.html" "PPT：http://127.0.0.1:${PORT:-4189}/PPT/AI协作-动态幻灯片.html"
exec "$PYTHON" PPT课程制作复盘/图解/mermaid-preview.py \
  PPT课程制作复盘/图解/课程制作主路径.mmd \
  --details PPT课程制作复盘/交互/课程制作路径/节点材料.json \
  --materials-root . --deck PPT/AI协作-动态幻灯片.html --port "${PORT:-4189}" "$@"
