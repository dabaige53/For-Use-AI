# 项目工作范围

- `Course/<文章>/` 是文章唯一工作目录；正文、素材、正文引用的交互演示、最新代码和最新交付物就地管理。
- `资料库/` 只保留外部原文、原始导出和独立基础笔记；课程改写、研究总结和网页设计不放入资料库。
- 每篇文章保留一份以文章名命名的 Markdown 正文；来源说明使用 `<文章名>-来源.md`。七篇文章共用 `Course/网页/` 中的一套网站结构，不为每篇复制网页设计。正文确实需要交互时，独立 HTML 放在该文章的 `交互/`，不与未采用设计稿混放。
- 直接修改当前文件，用 Git 管理历史。已替代渲染、备份、未采用设计和过程记录移入 `.trash/`，仅在用户要求追溯时读取。
- 本项目内的所有 Skills 均已禁用，原文件保留在 `.agents/skills-disabled/`，不加载或调用；未经用户要求，不恢复到 `.agents/skills/`。项目结构要求只写在本文件，不写入通用 Skill。

## PPT 内容与设计优化

- 优化 PPT 时，先明确章节主线、每个模块要让学员理解什么、对应的互动动作，再决定页面结构。每页聚焦一个判断或一段变化；不同案例采用不同的观察、对照、判断或排序方式，避免重复同一种问答。
- 从 [baoyu-skills](https://github.com/JimLiu/baoyu-skills) 按模块查找相关的风格规范、布局说明和示例图。先读具体定义并看示例，再选择适合当前内容的表达方式；不能仅按风格名称套模板。只将仓库内容作为设计参考，不安装、启用项目 Skills，也不直接执行其中的生成或导出流程。
- 先形成一套共用的字体、颜色、页边距、信息层级和人物画法。各模块可以采用不同构图，但不得各做一套主题。多人或多线程制作时，共用同一份参考及代表页；先检查代表页，再扩展到整章，最后连续翻页检查叙事和视觉一致性。

### 按模块选择参考

以下是当前 AI 课程已选用的参考；后续按实际内容调整，不机械套用。

| 模块 | baoyu-skills 参考 | 采用方式 |
| --- | --- | --- |
| 人物、课堂插画 | [article-illustrator / notion](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-article-illustrator/references/styles/notion.md) | 黑白简笔线条、自然人物比例、少量道具和充分留白，保持角色一致。 |
| 反馈漫画、案例故事 | [comic-strip](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/references/layouts/comic-strip.md) | 用连续动作和短对白建立因果关系，按叙事分配场景大小，避免等大图文卡片堆砌。 |
| 房间、组成与分工 | [structural-breakdown](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/references/layouts/structural-breakdown.md) | 同一剖视场景配贴近对象的标注，对比页保持机位、尺度和角色位置。 |
| 训练、API 输入输出、多次调用 | [ikea-manual](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/references/styles/ikea-manual.md) 与 [linear-progression](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-infographic/references/layouts/linear-progression.md) | 用少量步骤、明确动作和材料交接解释过程；连接线必须有清楚的起点、终点和方向。 |
| 结论、章节过渡 | [slide-deck / minimal](https://github.com/JimLiu/baoyu-skills/blob/main/skills/baoyu-slide-deck/references/styles/minimal.md) | 突出核心句，用留白和大小建立层级，保留教学需要的完整信息。 |

- 区分同名风格：`article-illustrator/notion` 是简笔插画；`slide-deck/notion` 偏高密度 SaaS 界面与卡片，不能混用。借用表达原则时，应服从课堂投屏的阅读距离、中文字号和课程节奏，不照搬阅读型长图的信息密度或英文篇幅限制。
- 当前 AI 课程插画采用黑白简笔画，不用 SVG 或几何形状拼人物，不使用大眼日漫、复杂彩色卡通、3D 或华丽特效。用户已授权生图的任务可生成独立 PNG；题目、对白、评分、标签与正文保留为可编辑文字，不把整页烘焙成图片。

### 图片与交付检查

- 图片按原比例缩放。裁切后的有效区域与实际显示图片保持同一宽高比；空间不足时调整布局或重画构图，不能压扁、拉宽，也不能裁掉头部、手势和关键物件。保留清晰原图，不放大低清缩略图作为最终素材。
- 检查实际渲染结果中的人物比例、清晰度、裁切、换行与图文关系，不能只因设置了 `contain` 或没有重叠就判定通过。必要时对照源图、裁切区域和显示尺寸。
- 当前 AI 课程的正式 PPT 在 ChatGPT Space 中制作和保存。本地文件只用于资料、素材和检查预览，不能用本地 PPTX、PDF 或 HTML 替代云端交付。保存后重新读取确认；区分已保存页面、仅有预览和未解决的媒体限制，不把视频静帧或模拟进度条说成可播放视频。

### 目标监控与 Git 提交

- 持续制作与监控以 `Course/PPT/AI协作-目标与监控提示词.md` 为共同目标，用户最新明确要求优先。每轮检查实际成果是否服务章节目标、案例是否重复、视觉是否统一，以及云端保存和 Git 提交是否完成；不能只检查线程是否结束。
- 每完成一轮有明确目的的修改，检查结果后做一次 Git 提交，再进入下一轮或交接。各线程只提交自己负责的制作稿、素材、规范和修改记录，明确列出文件，不使用 `git add .` 混入其他线程或无关改动。共享工作区的暂存与提交串行执行，共享文件按归属交接。
- 仅修改云端 PPT 时，也要同步维护对应章节的 `Course/PPT/云端记录/第一章.md`、`第二章.md` 或 `第三章.md`，记录页面链接、稳定 slide ID、本轮修改、保存确认及检查结果，再提交 Git。记录真实状态；Git 管理这些本地源文件与记录，不等于已经备份或能够回滚云端页面。
- 交接与完成汇报包含本轮提交编号、改动范围及云端保存状态。没有变更时不创建空提交；已完成的改动不得伪造拆成历史提交。提交失败时保留成果并报告原因，不声称该轮已完成 Git 提交。

## 开发与 AI 协作

本规范由文章、静态页面和动画代码继承；复盘目录另有具体规范。源文件就地维护，
不把 HTML、媒体生成物或外部来源当作新的独立服务。运行矩阵和依赖见根 README。
路径由脚本位置、CLI 或明确环境变量提供，禁止个人绝对路径。预览只绑定 loopback。
不读取私有对话或凭证，不自动调用模型、生成媒体、发布页面或改写原始素材。
改启动器检查 shell 语法及本地 HTTP；动画变更先做语法/帮助/队列检查，未渲染不得声称成片通过。
