# 你只发了一句话，模型实际收到了什么？

你第一次对助手说：“把这段本地录音整理成会议纪要。”从这句话到最后的回答，中间发生了什么？

先设定一个教学场景：应用连接了转写工具，起初只向文本模型提供录音的位置。录音、路径和后面的内容都是假设示例，没有读取真实文件；能够直接接收音频的产品，也可以采用其他流程。

## 先看这次输入

用户的话只是一部分。应用还可以加入系统指令，例如“使用中文，依据取得的资料回答”；加入环境信息，例如录音位于 `/audio/meeting.wav`；以及本次可用工具的定义。这些信息由应用程序组织，再提供给模型。

这些内容合起来，构成本次提供给模型的上下文。它们有不同来源和作用，需要保留相应边界。这是第一次提问，尚无此前对话；文件路径虽然已经出现，录音内容还没有进入输入。[上下文组织](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) · [消息边界](https://huggingface.co/docs/transformers/en/chat_templating)

工具定义让模型知道怎样提出操作请求。以公开的 `transcribe_audio` 为例，它的 MCP 定义用 `inputSchema` 描述参数：`file_path` 是字符串，也是唯一必填项；另有 `model`、`language` 和 `output_format`。这份定义是接口说明，实际转写由另一个程序完成。[工具注册源码](https://github.com/jwulff/whisper-mcp/blob/ad0199987512700132cc19155a430cc5b76ebace/src/index.ts)

## 输出先交给程序

收到这些输入后，模型可以先生成转写请求：选择 `transcribe_audio`，把文件路径填入 `file_path`。本例还假设指定 `model=large`、`language=zh`、`output_format=timestamps`，用于中文录音的教学演示。这里的 `model` 选择转写工具所用的 Whisper 模型，与生成请求的语言模型分开。

这也是模型的输出，只是接收者是程序。请求说明要做什么，此时录音还没有被读取。

应用程序接收请求，落实访问与执行条件，再调用转写程序。程序读取指定录音，返回结果。写在提示词里的要求只是指导，实际允许访问什么、能否执行，仍由程序机制控制。[工具执行流程](https://platform.claude.com/docs/en/agents-and-tools/tool-use/how-tool-use-works) · [MCP 调用与结果](https://modelcontextprotocol.io/specification/2025-06-18/server/tools)

## 结果成为下一次输入

假设转写成功，应用程序将返回的转写内容与对应请求、仍需使用的原有信息组织在一起，再次调用模型。这时，模型才取得本例中的录音文字。如果返回错误，后续输入得到的就是错误，不能当作已经取得录音内容。

用户没有再问一次，模型却已被调用两次。第二次，模型可以依据转写内容生成会议纪要，由应用程序交给用户阅读。

上下文因此会随过程变化。保存下来的全部记录，与本次实际提供给模型的内容，是两回事；应用程序可以选择或概括所需信息，也不必每次提供所有工具定义。[上下文维护](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)

一次对话里，输入可以来自用户和应用；输出可以交给人，也可以交给程序。工具请求、应用程序执行、结果回到输入，把这几步连接起来。理解这个过程，才能分清“模型提出了操作”与“系统已经取得了结果”。
