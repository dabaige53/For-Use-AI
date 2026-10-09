# Design Tokens

## Concept · 晨光蓝

克制、留白、一点晨光。配色取自封面山景：墨蓝做骨架，钴蓝标编号、数据和图标，晨光琥珀每页最多出现一次（标题短线或唯一重点）。层级靠字重和留白，不靠色块；卡片用中性浅灰面，不加描边和阴影。数字（章节号、小结序号、统计值）用细字重。

| Token | Value |
| --- | --- |
| color.faint | #a3acba |
| color.border-strong | #d5d9e0 |
| color.accent-soft | #eaf0fb |
| color.sun | #d98b3a |
| color.sun-soft | #fbf3e8 |
| color.negative | #b5483b |
| color.negative-soft | #fbefec |
| color.positive | #2e7d5b |
| color.positive-soft | #edf6f1 |
| font.number | -apple-system, "SF Pro Display", "Helvetica Neue", "PingFang SC", Arial, sans-serif |
| title.desc.font-size | 26px |
| title.desc.color | #6b778a |
| title.tag.font-size | 22px |
| title.tag.radius | 999px |
| title.tag.negative | 反例：#b5483b on #fbefec |
| title.tag.positive | 正例：#2e7d5b on #edf6f1 |
| title.tag.neutral | 原理 / 探索 / 回滚：#2f5bd3 on #eaf0fb |
| chapter.num.font-size | 240px |
| chapter.num.font-weight | 200 |
| chapter.num.color | #2f5bd3 |
| chapter.title.font-size | 72px |
| chapter.title.font-weight | 600 |
| chapter.rule | 40px × 3px #d98b3a |
| summary.num.font-size | 72px |
| summary.num.font-weight | 200 |
| footer.chapter.x | right 72px |
| footer.chapter.content | 章节号（钴蓝）+ 章名，取自前一个章节页；封面、结尾、全屏 iframe 页不显示 |
| ending.layout | 同章节页：山景背景 + 左侧白色渐变，左对齐标题、琥珀短线、结语 |

## Canvas

| Token | Value |
| --- | --- |
| canvas.width | 1672px |
| canvas.height | 941px |
| canvas.scale | min(viewport.width / 1672, viewport.height / 941) |
| canvas.transform-origin | 0 0 |
| canvas.overflow | hidden |
| viewport.background | #ffffff |
| slide.background | #ffffff |
| slide.box-sizing | border-box |
| safe.left | 72px |
| safe.right | 72px |
| safe.bottom | 104px |
| content.x | 72px |
| content.y | 210px |
| content.width | 1528px |
| content.bottom | 837px |
| content.height | 627px |
| content.with-summary.bottom | 714px |
| content.with-summary.height | 504px |

## Footer

| Token | Value |
| --- | --- |
| pagination.display | none |
| footer.x | 72px |
| footer.y | 901px |
| footer.width | 200px |
| footer.height | 26px |
| footer.font-size | 15px |
| footer.font-weight | 400 |
| footer.line-height | 1.4 |
| footer.letter-spacing | 3px |
| footer.color | #a3acba |
| footer.text-align | left |
| footer.cover.color | rgba(255,255,255,.85) |
| footer.cover.text-shadow | 0 1px 3px rgba(0,0,0,0.5) |

## Title

| Token | Value |
| --- | --- |
| title.x | 72px |
| title.y | 72px |
| title.width | 1528px |
| title.max-width | 100% of text column |
| title.height | 72px |
| title.font-size | 52px |
| title.font-weight | 600 |
| title.line-height | 1.25 |
| title.letter-spacing | 0.02em |
| title.color | #0e1e36 |
| title.text-align | left |
| title.margin | 0 |
| title.padding | 0 |
| title.max-lines | 1 |
| title.rule.x | 72px |
| title.rule.y | 163px |
| title.rule.width | 40px |
| title.rule.height | 3px |
| title.rule.color | #d98b3a |
| title.multiline.max-lines | 2 |
| title.multiline.height | 138px |
| title.multiline.rule.y | 229px |
| title.multiline.content.y | 276px |
| title.multiline.content.height | 561px |
| title.multiline.content.with-summary.height | 438px |

## Typography

| Token | Value |
| --- | --- |
| font.family | "PingFang SC", -apple-system, "Helvetica Neue", "Microsoft YaHei", "Noto Sans CJK SC", Arial, sans-serif |
| font.style | normal |
| text.letter-spacing | 0 |
| text.word-break | normal |
| text.overflow-wrap | break-word |
| text.white-space | normal |
| text.margin | 0 |
| text.padding | 0 |
| heading.font-size | 36px |
| heading.font-weight | 600 |
| heading.line-height | 1.3 |
| heading.color | #0e1e36 |
| heading.compact.font-size | 31px |
| heading.compact.font-weight | 600 |
| heading.compact.line-height | 1.3 |
| body.font-size | 27px |
| body.font-weight | 400 |
| body.line-height | 1.6 |
| body.color | #46556b |
| caption.font-size | 24px |
| caption.font-weight | 400 |
| caption.line-height | 1.4 |
| caption.color | #6b778a |
| summary.font-size | 32px |
| summary.font-weight | 600 |
| summary.line-height | 1.4 |
| summary.color | #0e1e36 |
| text.box.min-height | ceil(font-size × line-height × lines) |

## Color

| Token | Value |
| --- | --- |
| color.background | #ffffff |
| color.surface | #f5f6f8 |
| color.surface-subtle | #fafbfc |
| color.ink | #0e1e36 |
| color.body | #46556b |
| color.muted | #6b778a |
| color.header | #46556b |
| color.accent | #2f5bd3 |
| color.danger | #b5483b |
| color.border | #e6e8ec |
| color.inverse | #ffffff |
| color.media-background | #0b1220 |
| color.quadrant.blue | #eef2fb |
| color.quadrant.green | #edf6f1 |
| color.quadrant.yellow | #fbf3e8 |
| color.quadrant.red | #fbefec |

## Spacing & Grid

| Token | Value |
| --- | --- |
| spacing.unit | 8px |
| spacing.xs | 8px |
| spacing.sm | 16px |
| spacing.md | 24px |
| spacing.lg | 32px |
| spacing.xl | 48px |
| spacing.2xl | 64px |
| grid.width | 1528px |
| grid.column-gap | 32px |
| grid.row-gap | 32px |
| grid.align-items | start |
| grid.equal-column.width | (1528px - (columns - 1) × 32px) / columns |
| grid.2-column.width | 748px |
| grid.3-column.width | 488px |
| grid.4-column.width | 358px |
| grid.5-column.width | 280px |
| grid.split.text.width | 536px |
| grid.split.media.width | 960px |
| grid.split.media.x | 640px |
| grid.same-row.card-height | equal |
| grid.same-row.heading-y | equal |
| grid.same-row.icon-y | equal |
| grid.same-row.body-y | equal |

## Card

| Token | Value |
| --- | --- |
| card.background | #f5f6f8 |
| card.border | none |
| card.border-radius | 12px |
| card.box-shadow | none |
| card.padding | 32px |
| card.compact.padding | 24px |
| card.heading-body.gap | 16px |
| card.item.gap | 16px |
| card.min-height | padding-top + content-height + padding-bottom + border-top + border-bottom |
| card.text.overflow | visible |
| card.arch.border-radius | 160px 160px 12px 12px |
| card.circle.border-radius | 50% |

## Summary

| Token | Value |
| --- | --- |
| summary.x | 72px |
| summary.y | 746px |
| summary.width | 1528px |
| summary.height | 91px |
| summary.padding-x | 32px |
| summary.padding-y | 16px |
| summary.background | #f5f6f8 |
| summary.border | none |
| summary.border-radius | 12px |
| summary.text-align | center |
| summary.align-items | center |
| summary.max-lines | 1 |
| summary.content-gap.min | 32px |

## Media

| Token | Value |
| --- | --- |
| media.border-radius | 18px |
| media.overflow | hidden |
| media.background | #07111d |
| media.border | 1px solid #e3edf7 |
| media.box-shadow | none |
| photo.embedded-text | none |
| photo.embedded-pagination | none |
| photo.text-mask | none |
| photo.object-fit | cover |
| photo.object-position | center |
| diagram.object-fit | contain |
| diagram.object-position | center |
| video.object-fit | contain |
| video.object-position | center |
| video.aspect-ratio | source.width / source.height |
| video.controls | true |
| video.playsinline | true |
| video.preload | metadata |
| video.with-summary.max-height | 504px |

## Diagram & Icon

| Token | Value |
| --- | --- |
| diagram.label.font-size | 24px |
| diagram.label.line-height | 1.4 |
| diagram.axis.stroke-width | 2px |
| diagram.connector.stroke-width | 3px |
| diagram.connector.color | #1976f3 |
| diagram.label-gap | 16px |
| diagram.safe.left | 72px |
| diagram.safe.right | 72px |
| diagram.safe.bottom | 104px |
| icon.style | outline |
| icon.stroke-width | 2px |
| icon.color | #08244c |
| icon.background | #eef6fb |
| icon.container.sm | 72px |
| icon.container.md | 96px |
| icon.container.lg | 120px |
| icon.container.border-radius | 50% |
| icon.text-gap | 24px |
| flow.connector-slot.width | 48px |
| flow.card.width | (1528px - (steps - 1) × 48px) / steps |
| flow.connector.align | center |

## Cover

| Token | Value |
| --- | --- |
| cover.background-size | cover |
| cover.background-position | center |
| cover.title.x | 88px |
| cover.title.y | 174px |
| cover.title.width | 720px |
| cover.title.height | 190px |
| cover.title.font-size | 59px |
| cover.title.font-weight | 600 |
| cover.title.line-height | 1.35 |
| cover.title.color | #0e1e36 |
| cover.title.max-lines | 2 |
| cover.rule.x | 90px |
| cover.rule.y | 391px |
| cover.rule.width | 48px |
| cover.rule.height | 3px |
| cover.rule.color | #d98b3a |
| cover.subtitle.x | 89px |
| cover.subtitle.y | 454px |
| cover.subtitle.width | 660px |
| cover.subtitle.height | 55px |
| cover.subtitle.font-size | 35px |
| cover.subtitle.line-height | 1.4 |
| cover.subtitle.color | #24344d |

## Interaction & Layers

| Token | Value |
| --- | --- |
| layer.background | 0 |
| layer.photo | 1 |
| layer.diagram | 2 |
| layer.card | 3 |
| layer.connector | 4 |
| layer.text | 5 |
| slide.inactive.display | none |
| slide.active.display | block |
| text.contenteditable | true |
| text.focus.outline | 2px dashed #9fb4ea |
| text.focus.border-radius | 8px |
| text.focus.background | rgba(255,255,255,0.4) |
| navigation.next | ArrowRight, PageDown |
| navigation.previous | ArrowLeft, PageUp |
| navigation.first | Home |
| navigation.last | End |
| navigation.total | slide.count |
| navigation.hash | slide.index + 1 |

## Constraints

| Token | Value |
| --- | --- |
| title.position.deviation | 0px |
| title.font-size.deviation | 0px |
| title.line-height.deviation | 0 |
| same-row.alignment.deviation | 0px |
| content.unintended-overlap | 0px |
| text.clipped-lines | 0 |
| content.outside-safe-area | 0px |
| media.aspect-ratio-distortion | 0 |
| video.content-crop | 0px |

## Video Annotation

| Token | Value |
| --- | --- |
| video.annotation.x | 72px |
| video.annotation.y | 210px |
| video.annotation.width | 344px |
| video.annotation.heading.font-size | 32px |
| video.annotation.body.font-size | 24px |
| video.annotation.body.line-height | 1.6 |
| video.annotated.x | 480px |
| video.annotated.y | 210px |
| video.annotated.width | 1120px |
| video.annotated.height | 560px |
| video.timeline.x | 480px |
| video.timeline.y | 788px |
| video.timeline.width | 1120px |
| video.timeline.height | 96px |
| video.timeline.time.font-size | 18px |
| video.timeline.label.font-size | 20px |
| video.timeline.step | 0.1s |
| video.timeline.accent | #2f5bd3 |
| video.annotation.diagram.node.font-size | 23px |
| video.annotation.diagram.node.padding | 14px 16px |
| video.annotation.diagram.node.radius | 10px |
| video.annotation.diagram.node.background | #f8f9fb |
| video.annotation.diagram.operation.background | #f5f6f8 |
| video.annotation.diagram.arrow.height | 30px |
| video.annotation.diagram.gap | 24px |

## Terrain

| Token | Value |
| --- | --- |
| terrain.background | #ffffff |
| terrain.single.x | 72px |
| terrain.single.y | 210px |
| terrain.single.width | 1528px |
| terrain.single.height | 620px |
| terrain.dialogue.width | 624px |
| terrain.column.gap | 32px |
| terrain.single.canvas.width | 872px |
| terrain.dialogue.font-size | 22px |
| terrain.dialogue.line-height | 1.55 |
| terrain.pair.y | 300px |
| terrain.pair.height | 530px |
| terrain.pair.column.width | 748px |
| terrain.definition.y | 190px |
| terrain.definition.font-size | 27px |
| terrain.controls.y | 836px |
| terrain.initial.progress | 0 |
| terrain.initial.playing | true |
| terrain.reset.progress | 0 |
| terrain.dialogue.reveal | progressive |
| terrain.pair.clock | shared |

| terrain.speed | 2 |
| terrain.controls.icon.size | 24px |
| terrain.controls.alignment | center below terrain |
| terrain.controls.height | 60px |
| terrain.controls.padding | 10px 14px |
| terrain.controls.gap | 14px |
| terrain.controls.radius | 12px |
| terrain.controls.background | #f8f9fb |
| terrain.controls.pair.x | 400px |
| terrain.controls.pair.width | 872px |
| terrain.controls.button.size | 40px 36px |
| terrain.controls.time.font-size | 17px |
| terrain.controls.seek.step | 0.1s |
| terrain.controls.seek.playing | false |
| terrain.controls.speed.options | 0.5, 1, 1.5, 2, 3, 4 |
| terrain.controls.speed.default | 2 |
| terrain.chat.roles | user, ai |
| terrain.chat.bubble.radius | 14px |

| terrain.chat.code.font-size | 19px |
| terrain.chat.role.font-size | 16px |
| terrain.timeline.source | assets/terrain-stories.js |
| terrain.timeline.unit | seconds at 1× |
| terrain.timeline.event.duration | clamp(text.delta.length / 14 + 4, 5, 28)s |
| terrain.timeline.end-hold | 3s |
| terrain.timeline.terrain.transition | event.duration × [0.08, 0.40] |
| terrain.timeline.path.transition | event.duration × [0.44, 0.95] |
| terrain.timeline.start | all frames configured |
| terrain.reentry.progress | 0 |
| terrain.reset.playing | false |
| terrain.labels.max-visible | 3 |

| terrain.pair.initial.progress | 1 |
| terrain.pair.initial.playing | false |
| terrain.pair.reentry.progress | 1 |
| terrain.pair.run-from-result.progress | 0 |

| slide.transition.duration | 0ms |
| slide.inactive.opacity | 0 |
| slide.inactive.inert | true |
| terrain.navigation.wait | target frame painted |
| terrain.preload.ahead | 1 slide |
