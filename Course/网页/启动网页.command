#!/bin/zsh
cd "${0:A:h}/.."
print "阅读网页：http://localhost:4189/网页/index.html"
print "PPT：http://localhost:4189/PPT/AI协作-动态幻灯片.html"
/Users/w/miniforge3/envs/work/bin/python -m http.server 4189 --bind 127.0.0.1
