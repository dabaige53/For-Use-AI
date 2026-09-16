FROM node:22-alpine AS build
WORKDIR /course/网页
RUN corepack enable
COPY 网页/package.json 网页/pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile
COPY 网页/scripts ./scripts
COPY 网页/public ./public
COPY 01-使用AI的问题 /course/01-使用AI的问题
COPY 02-AI的能力从哪里来 /course/02-AI的能力从哪里来
COPY 03-输入输出与执行 /course/03-输入输出与执行
COPY 04-表达需求与反馈 /course/04-表达需求与反馈
COPY 05-执行任务 /course/05-执行任务
COPY 06-行动与投入 /course/06-行动与投入
COPY 07-课程制作 /course/07-课程制作
RUN pnpm build

FROM nginx:1.27-alpine
COPY 网页/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /course/网页/dist /usr/share/nginx/html
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD wget -q -O /dev/null http://127.0.0.1:8080/ || exit 1
