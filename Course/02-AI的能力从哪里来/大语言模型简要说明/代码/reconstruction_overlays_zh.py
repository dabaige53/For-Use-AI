"""Original FirthQuote tail, with stale bank selections refreshed after transforms."""

import sys
from typing import Any, cast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import tex_support  # noqa: E402,F401
from manimlib import (  # noqa: E402
    Arrow,
    BLUE,
    DOWN,
    FadeIn,
    FadeOut,
    Group,
    GrowArrow,
    ImageMobject,
    InteractiveScene,
    LEFT,
    LaggedStart,
    ORIGIN,
    PI,
    RIGHT,
    SurroundingRectangle,
    TEAL,
    Text,
    UP,
    VGroup,
)  # noqa: E402


def CNText(text, **kwargs):
    kwargs.setdefault("font", "PingFang SC")
    return Text(text, **kwargs)


class BankContextOverlayChinese(InteractiveScene):
    def construct(self):
        top = VGroup(*(CNText(w, font_size=42) for w in ["沿着", "河流", "的", "bank"]))
        bottom = VGroup(
            *(CNText(w, font_size=42) for w in ["把", "支票", "存入", "bank"])
        )
        for line, y in [(top, 2.8), (bottom, -1.2)]:
            line.arrange(cast(Any, RIGHT), buff=0.10).move_to(y * cast(Any, UP))
            line[-1].set_color(TEAL)
        word = CNText("bank", font_size=72).set_color(TEAL)
        self.add(word)
        self.wait()
        self.play(FadeOut(word), FadeIn(top), FadeIn(bottom))
        banks = [top[-1], bottom[-1]]
        queries = VGroup(
            *(
                SurroundingRectangle(w, buff=0.05)
                .set_stroke(TEAL, 2)
                .set_fill(TEAL, 0.25)
                for w in banks
            )
        )
        self.play(FadeIn(queries))
        self.wait()
        targets = [top[1], bottom[1], bottom[2]]
        keys = VGroup(
            *(
                SurroundingRectangle(w, buff=0.05)
                .set_stroke(BLUE, 2)
                .set_fill(BLUE, 0.35)
                for w in targets
            )
        )
        self.play(LaggedStart(*(FadeIn(key) for key in keys)), run_time=2)
        arrows = VGroup()
        for target, bank in zip(targets, [banks[0], banks[1], banks[1]]):
            arrow = Arrow(
                target.get_top() + 0.14 * cast(Any, UP),
                bank.get_top() + 0.14 * cast(Any, UP),
                path_arc=-PI / 2,
                buff=0,
                thickness=2,
                tip_width_ratio=3,
            )
            arrow.set_color(BLUE)
            arrows.add(arrow)
        self.play(
            LaggedStart(*(GrowArrow(cast(Arrow, arrow)) for arrow in arrows)),
            run_time=3,
        )
        self.wait()
        pictures = Group(
            ImageMobject(str(ROOT / "assets/images/river-bank-original.png")),
            ImageMobject(str(ROOT / "../素材/网络补充/federal-reserve-eccles.jpg")),
        )
        for pic, bank in zip(pictures, banks):
            pic.set_height(1.8).next_to(bank, cast(Any, DOWN), buff=0.25).shift(
                0.3 * cast(Any, LEFT)
            )
        self.play(LaggedStart(*(FadeIn(pic) for pic in pictures)), run_time=1.5)
        self.wait(2)


class OriginalOpeningTitleChinese(InteractiveScene):
    def construct(self):
        title = CNText("大型语言模型", font_size=54)
        subtitle = CNText("写给好奇的初学者", font_size=36)
        Group(title, subtitle).arrange(cast(Any, DOWN), buff=0.2).move_to(
            cast(Any, ORIGIN)
        )
        self.add(title, subtitle)
        self.wait(1.3)
