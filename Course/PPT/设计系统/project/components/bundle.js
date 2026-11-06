/* @ds-bundle: {"format": 4, "namespace": "AIWorkDeck", "components": [{"name": "CaseCompare"}, {"name": "CaseSingle"}, {"name": "ChatWindow"}, {"name": "Attachment"}, {"name": "DocumentCard"}, {"name": "Annotation"}, {"name": "ActionBar"}, {"name": "CoverSlide"}, {"name": "AgendaList"}, {"name": "SectionDivider"}, {"name": "ChapterNav"}, {"name": "KeyStatement"}, {"name": "TwoColumnCompare"}, {"name": "ContextBranch"}, {"name": "PromptProbability"}, {"name": "StepFlow"}, {"name": "VideoStillTimeline"}, {"name": "DiscussionList"}, {"name": "StoryPanels"}, {"name": "QuizColumns"}, {"name": "TakeawaySummary"}, {"name": "InstructorProfile"}]} */
// 组件目录：名称与一句话用途。页面由 bundle.css 的 ds-* 类和 preview.html 中的坐标搭建。
window.AIWorkDeck = {
  canvas: { width: 1254, height: 705.75, unit: "pt" },
  layouts: {
      "CaseCompare": "A/B 对照案例页：同一份材料、两种问法，比较 AI 的两个回复。",
      "CaseSingle": "单案例页：对话窗口是主角，右侧解读栏说明这次回复为什么合格。",
      "ChatWindow": "对话窗口：模拟一次和 AI 的对话，用户在右、AI 在左。",
      "Attachment": "附件卡和迷你表格：把用户提供的文件和 AI 产出的表格画出来。",
      "DocumentCard": "文档卡片：把邮件、通知、周报这类成品画成一张“纸”。",
      "Annotation": "高亮和标注：指出对话里哪一句、哪一个词起了作用。",
      "ActionBar": "横栏：共同材料或任务、上一轮缩略、学员动作条。",
      "CoverSlide": "课程封面：全幅山顶照片，左上两行主标题，左下写讲师信息。",
      "AgendaList": "目录页：左侧三个带圆圈序号的章节，右侧一张照片。",
      "SectionDivider": "章节扉页：大号蓝色章节号、章节名、一句问题，右侧露出照片。",
      "ChapterNav": "章节导航页：淡色章节号、章节名、跳转链接和三段式面包屑。",
      "KeyStatement": "核心句页：整页只有两行 54pt 结论，第二行用蓝色。",
      "TwoColumnCompare": "左右对照页：两栏输入，中间一条竖线，每栏下方配一张插画。",
      "ContextBranch": "分叉对照页：一句话分成两种背景，各自下方是一组横向概率条。",
      "PromptProbability": "输入与预测页：两栏原文面板，下方是选项和小概率条。",
      "StepFlow": "五步流程页：上排三步、下排两步，用细箭头连接。",
      "VideoStillTimeline": "视频静帧页：左侧 16:9 静帧和分段进度条，右侧两行要点。",
      "DiscussionList": "讨论题页：左侧三道带淡色大序号的问题，右侧一张插画。",
      "StoryPanels": "三格分镜页：同一场景的三个阶段，每格下方是评分和改写。",
      "QuizColumns": "三栏测验页：每栏一道题，题号、插画、题干和选项。",
      "TakeawaySummary": "收获总结页：左侧淡色大“3”加三个问题，右侧两个蓝色大数字，底部一句口号。",
      "InstructorProfile": "讲师介绍页：头像字卡、个人信息、四张统计卡片和一年用量热力图。"
  }
};
