# AI 输入输出动画工程

依据课程正文和三个正式镜头 JSON，用 ManimGL 原生对象重建图形与文字。当前目标为 480p 静音验证视频，旁白、音频与正式字幕另属有声成片阶段。

初始化：`./init.sh`。渲染及合成：`uv run python render.py --scene all --quality 480p`。单镜可选 `FirstInput`、`GenerateExecute`、`ReturnAnswer`，代表段选 `ContinuityPreview`。完整参数见 `--help`，配置见课程 `CONFIG.md`。

`objects.py` 管理稳定图形，`scenes.py` 管理动作，`render.py` 管理渲染、时间线、解码验证。工具字段读取课程真实 Schema；所有路径、调用值和结果均为教学示例，不访问录音或调用工具。

输出位于课程 `临时渲染/代码验证/`，独立片段及整片各自保留。每次运行必须指定未使用的输出目录，默认按时间生成。视频不进 Git，代码、依赖锁与文档由 Git 管理。

抽帧检查：`uv run python inspect_media.py <输出目录>`，生成每个提示点末段的检查帧及总览图；查看动作还需额外抽取连续帧。最新验收为 `../../计划/480p代码验收.md`。
