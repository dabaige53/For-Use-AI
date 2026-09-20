# Design Tokens

## Canvas

| Token | Value |
| --- | --- |
| canvas.width | 1672px |
| canvas.height | 941px |
| canvas.scale | min(viewport.width / 1672, viewport.height / 941) |
| canvas.transform-origin | 0 0 |
| canvas.overflow | hidden |
| viewport.background | #0f1720 |
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
| footer.font-size | 18px |
| footer.font-weight | 400 |
| footer.line-height | 1.4 |
| footer.letter-spacing | 1px |
| footer.color | #536d90 |
| footer.text-align | left |
| footer.cover.color | #ffffff |
| footer.cover.text-shadow | 0 1px 3px rgba(0,0,0,0.5) |

## Title

| Token | Value |
| --- | --- |
| title.x | 72px |
| title.y | 72px |
| title.width | 1528px |
| title.max-width | 100% of text column |
| title.height | 72px |
| title.font-size | 55px |
| title.font-weight | 700 |
| title.line-height | 1.2 |
| title.letter-spacing | 0 |
| title.color | #08244c |
| title.text-align | left |
| title.margin | 0 |
| title.padding | 0 |
| title.max-lines | 1 |
| title.rule.x | 72px |
| title.rule.y | 163px |
| title.rule.width | 76px |
| title.rule.height | 3px |
| title.rule.color | #08244c |
| title.multiline.max-lines | 2 |
| title.multiline.height | 138px |
| title.multiline.rule.y | 229px |
| title.multiline.content.y | 276px |
| title.multiline.content.height | 561px |
| title.multiline.content.with-summary.height | 438px |

## Typography

| Token | Value |
| --- | --- |
| font.family | Arial, "PingFang SC", "Microsoft YaHei", "Noto Sans CJK SC", sans-serif |
| font.style | normal |
| text.letter-spacing | 0 |
| text.word-break | normal |
| text.overflow-wrap | break-word |
| text.white-space | normal |
| text.margin | 0 |
| text.padding | 0 |
| heading.font-size | 36px |
| heading.font-weight | 700 |
| heading.line-height | 1.3 |
| heading.color | #08244c |
| heading.compact.font-size | 31px |
| heading.compact.font-weight | 700 |
| heading.compact.line-height | 1.3 |
| body.font-size | 27px |
| body.font-weight | 400 |
| body.line-height | 1.6 |
| body.color | #314f75 |
| caption.font-size | 24px |
| caption.font-weight | 400 |
| caption.line-height | 1.4 |
| caption.color | #536d90 |
| summary.font-size | 32px |
| summary.font-weight | 600 |
| summary.line-height | 1.4 |
| summary.color | #08244c |
| text.box.min-height | ceil(font-size × line-height × lines) |

## Color

| Token | Value |
| --- | --- |
| color.background | #ffffff |
| color.surface | #eef6fb |
| color.surface-subtle | #f7fbff |
| color.ink | #08244c |
| color.body | #314f75 |
| color.muted | #536d90 |
| color.header | #395675 |
| color.accent | #1976f3 |
| color.danger | #ff4b2b |
| color.border | #e3edf7 |
| color.inverse | #ffffff |
| color.media-background | #07111d |
| color.quadrant.blue | #e8f4ff |
| color.quadrant.green | #e7f7ed |
| color.quadrant.yellow | #fff2da |
| color.quadrant.red | #ffe8e8 |

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
| card.background | #eef6fb |
| card.border | 1px solid #e3edf7 |
| card.border-radius | 16px |
| card.box-shadow | none |
| card.padding | 32px |
| card.compact.padding | 24px |
| card.heading-body.gap | 16px |
| card.item.gap | 16px |
| card.min-height | padding-top + content-height + padding-bottom + border-top + border-bottom |
| card.text.overflow | visible |
| card.arch.border-radius | 160px 160px 16px 16px |
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
| summary.background | #eef6fb |
| summary.border | 1px solid #e3edf7 |
| summary.border-radius | 16px |
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
| cover.title.font-weight | 700 |
| cover.title.line-height | 1.35 |
| cover.title.color | #06264d |
| cover.title.max-lines | 2 |
| cover.rule.x | 90px |
| cover.rule.y | 391px |
| cover.rule.width | 82px |
| cover.rule.height | 3px |
| cover.rule.color | #09294d |
| cover.subtitle.x | 89px |
| cover.subtitle.y | 454px |
| cover.subtitle.width | 660px |
| cover.subtitle.height | 55px |
| cover.subtitle.font-size | 35px |
| cover.subtitle.line-height | 1.4 |
| cover.subtitle.color | #12385c |

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
| text.focus.outline | 2px dashed #9bbcff |
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
| video.timeline.accent | #1976f3 |
| video.annotation.diagram.node.font-size | 23px |
| video.annotation.diagram.node.padding | 14px 16px |
| video.annotation.diagram.node.radius | 10px |
| video.annotation.diagram.node.background | #f7fbff |
| video.annotation.diagram.operation.background | #eef6fb |
| video.annotation.diagram.arrow.height | 30px |
| video.annotation.diagram.gap | 24px |
