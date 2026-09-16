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
