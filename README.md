# For-Use-AI

面向 AI 原理与使用方法的中文课程内容。

## 当前内容

- `Course/<文章>/<文章名>.md`：每篇文章的唯一正文。
- `Course/<文章>/素材/`：文章、动画和视频共同使用的素材。
- `Course/<文章>/交互/`：正文直接引用的独立交互演示（如有）。
- `Course/<文章>/代码/`：仅保留当前可维护代码（如有）。
- `Course/网页/`：共享的静态课程页面；当前入口为 `index.html`，无需 source/dist 构建。

## 目录

- `Course/`：文章、素材、交互演示、当前代码、当前交付物和统一课程网站。
- `资料库/`：外部原文、原始导出和独立基础笔记。
- `.trash/`：已替代版本和过程材料，不作为当前内容读取。

## 公开范围

本仓库只发布已审查的原创课程内容。私人归档、本机路径、工作日志、临时文件、交付媒体、第三方原文与来源素材不进入公开版本。

引用的外部资料仍归原作者所有；本仓库仅保留链接和原创整理。仓库当前未授予统一的再许可，第三方内容以其各自许可为准。

## 本地阅读与开发

安装 Python 3，在仓库根运行 `sh start.sh`，访问终端给出的课程或 PPT 地址。
默认仅监听 `127.0.0.1:4189`；可用 `PORT=4190 sh start.sh` 更换端口，
用 `PYTHON=python3` 选择解释器。Ctrl-C 停止。纯静态阅读无需 `.env`、密钥或 npm 安装。
页面引用的外部 CDN、字体及视频素材仍可能需要网络或另行取得的媒体；HTTP 成功不代表所有媒体完整。

| 可执行单元 | 入口与依赖 | 验证边界 |
| --- | --- | --- |
| 课程/PPT 页面 | 根 `sh start.sh`；内容位于 `Course/网页/`、`Course/PPT/` | 本地 HTTP；不生成页面 |
| 制作路径交互 | `sh Course/PPT课程制作复盘/交互/课程制作路径/启动交互图.command`；Python 3，首次启动下载 npm 前端资源 | 支持 `PYTHON`/`PORT`；复盘私有对话未随仓库发布，相关链接不保证可用 |
| LLM 动画 | 进入 `Course/02-AI的能力从哪里来/大语言模型简要说明/代码/`，`sh init.sh`，`uv run --no-sync python render_zh_final.py --check` | init 检查 uv、ffmpeg、ffprobe、tectonic；--check 只列队列，正式合成另需既有视频与中文字体 |
| AI 输入输出动画 | 进入 `Course/03-信息输入与工具执行/AI的输入与输出/代码/`，`sh init.sh`，`uv run --no-sync python render.py --help` | Python 3.11、ManimGL、ffmpeg/ffprobe；实际渲染需要图形环境 |

LLM 的 `render_all.py` 是上游 38 场景的旧批量入口，需要未随当前仓库提供的场景清单；
可通过 `--inventory` 显式提供。它不替代 `render_zh_final.py`，也不能据其缺失输入断言中文视频管线不可用。
`compose_reconstruction.py` 的中文字体通过 `COURSE_FONT` 配置，字体集合索引用 `COURSE_FONT_INDEX`（默认 0）。
原始第三方素材中的历史路径保留作来源证据，不作为本机运行说明。
