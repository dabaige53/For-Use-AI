# 转写工具定义来源

来源：https://github.com/jwulff/whisper-mcp/blob/ad0199987512700132cc19155a430cc5b76ebace/src/index.ts

固定提交：ad0199987512700132cc19155a430cc5b76ebace。已读取工具注册与调用分派代码；JSON 文件按该注册对象转录，字段未翻译。未安装或运行此工具，不能当作实测转写结果。

画面是原始定义的局部放大，完整定义保存为 transcribe_audio.schema.json。没有把 MCP 的 inputSchema 改名为 parameters。后续示例调用采用 file_path、model: large、language: zh、output_format: timestamps，避免默认英语模型与中文案例冲突。调用参数值和系统指令仍为教学示例。
