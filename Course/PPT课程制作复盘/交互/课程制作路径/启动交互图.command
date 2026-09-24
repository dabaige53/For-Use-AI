#!/bin/zsh
DIR="${0:A:h}"
COURSE="${DIR:h:h:h}"
exec /Users/w/miniforge3/envs/work/bin/python "$DIR/../../图解/mermaid-preview.py" "$DIR/../../图解/课程制作主路径.mmd" --details "$DIR/节点材料.json" --materials-root "$COURSE" --port 0 --open
