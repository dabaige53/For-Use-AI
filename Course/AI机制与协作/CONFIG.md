# 配置与运行

七个编号板块各自以 `正文.md` 为真源，配图位于该板块的 `配图/`，案例位于 `案例/`；`网页/dist/` 是可删除并重新生成的静态站点。网页没有后端、凭证或外部服务依赖。

## 本地运行

需要 Node.js 22+ 与 pnpm 10+。在 `网页/` 中执行：

```bash
pnpm run init     # 按锁文件安装依赖
pnpm run build    # 构建七篇 HTML 并复制素材
pnpm run check    # 核对 Markdown、页面、锚点、图片和内部链接
pnpm run preview  # 默认在 http://localhost:4173 预览
```

可通过 `PORT=其他端口 pnpm run preview` 修改本地预览端口。构建要求 README 所列七篇文章全部存在；缺少文章时会列出缺失文件并退出。

## 容器运行

在 `网页/` 中执行 `docker compose up --build -d`，访问 `http://localhost:8080`。复制 `.env.example` 为 `.env` 并修改 `SITE_PORT` 可调整宿主机端口。容器通过 HTTP 首页执行健康检查，静态文件由 nginx 提供。

## 读写范围

构建只读取 七个编号板块的 `正文.md`、`配图/` 和 `案例/`，并重建 `网页/dist/`。不要直接修改 `dist/`；样式与交互源文件在 `网页/public/`，构建与校验入口在 `网页/scripts/`。

## 图解重建

在课程根目录执行 `python 工具/rebuild_diagrams.py`，使用 Python 标准库，生成各板块配图 HTML 和 SVG；局部样式见 `计划/图形风格.md`。图形字体使用系统中文回退，不需要网络字体。

## 停止与排错

本地预览前台运行，Ctrl+C 停止。端口被占用时设置其他 PORT。预览仅绑定 127.0.0.1。修改正文或配图后重新 build、check。容器使用 `docker compose down` 停止；本项目无运行期持久数据，修改内容保留在板块源目录。Docker daemon 未运行时先启动本机容器服务。

## 第 04 章原风格 GIF 导出

在 `网页/` 执行 `pnpm run gifs:04`。支持 `--only balance|entangle|case-better|drift|distill|purify|reason|anneal` 和 `--output 目录`，帮助见 `pnpm run gifs:04 --help`。依赖锁文件中的 Node Canvas 及 PATH 上的 ffmpeg，不启动浏览器。

导出复用 `04-表达需求与反馈/案例/思维地形-体素沙盘.html` 的原场景、标签、字体与相机，保留黑底、A/B 对照及 26 帧/16 fps 节奏。只提高导出像素至 2040×1140，并逐帧清底、检查标签是否完成绘制。原文字号保持不变；第 04 章正文按“GIF → 对应原文 → GIF → 对应原文”纵向排列。源帧与检查数据保存在命令返回的系统临时目录。

## 阅读宽度与目录收起

桌面左目录宽 13rem、右目录宽 12rem，栏间距 1.5rem；正文自动占用剩余宽度。左右箭头分别收起对应目录至 2rem 的展开按钮栏。状态通过本地存储 `course-nav-collapsed`、`course-toc-collapsed` 保存；浏览器禁用存储时仍可操作。1100px 及以下沿用正文上方目录，760px 及以下沿用移动菜单。

## 第四章 GIF 阅读裁边

`04-表达需求与反馈/案例/gif-display.json` 记录每组 GIF 全部帧的联合内容边界，四周保留 24px。网页按此范围显示，最大宽度 40rem；原 GIF 文件不变。重新生成动画后需核对并更新范围，避免裁掉新增标签或轨迹。

## 阅读界面与全文搜索

2026-09-17 最新确认采用系统无衬线字体，替代此前仿宋要求。正文 16px/1.75，导语 19px/1.6，主标题桌面 36px、移动端 32px；正文最大 800px，顶栏最大 1280px。两侧保留收起把手。

构建从七篇 Markdown 生成 `search-index.json` 和 `markdown/01.md` 至 `07.md`。搜索支持中文、英文及空格分隔的多个关键词，Cmd/Ctrl+K 打开，方向键选择、Enter 跳转、Esc 关闭。检索完全在浏览器本地执行。

Copy page 菜单可复制 Markdown、正文纯文本或页面链接；标题链条图标复制章节链接。浏览器剪贴板权限不可用时显示失败提示。顶部更多菜单提供下载 Markdown、文档索引和打印。机器入口为 `llms.txt`，同时在页面链接声明中暴露。

本课程使用自己的品牌、课程卡片与来源信息，不标记为 CE 101 或 Mintlify 制作。Logo 和控件图标为本地 SVG；图片、GIF 内嵌文字仍沿用已确认素材。

## CE101 实测布局（2026-09-17）
网页以 `网页/设计研究/ce101/参数实测.md` 为尺寸依据：外层1472px，左栏288px，右栏304px，1024/1280px断点；正文流式。保留课程自己的内容、搜索及两侧收起把手。
