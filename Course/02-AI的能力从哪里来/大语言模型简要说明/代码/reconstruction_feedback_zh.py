"""Original feedback scenes with restored author worker image and replacement robot."""

import sys
from typing import Any, cast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from reconstruction_core_zh import (  # noqa: E402
    BLACK,
    DOWN,
    GREY_B,
    LARGE_BUFF,
    LEFT,
    LaggedStart,
    RIGHT,
    ShowMachineWithDials,
    Text,
    VGroup,
    there_and_back,
)  # noqa: E402
import group_c  # noqa: E402
from manimlib import (  # noqa: E402
    ImageMobject,
    SVGMobject,
    FullScreenRectangle,
    GREY_E,
    Rectangle,
    Group,
)  # noqa: E402


class RLHFWorkersChinese(ShowMachineWithDials):
    def construct(self):
        self.add(FullScreenRectangle().set_fill(GREY_E, 1))
        worker = ImageMobject(
            str(ROOT / "assets/images/worker-original.png")
        ).set_height(2)
        # Keep the original photograph silhouette and monitor; replace tiny screen text.
        screen = (
            Rectangle(width=1.13, height=0.57).set_fill(BLACK, 1).set_stroke(width=0)
        )
        screen.move_to(worker.get_center() + 0.57 * cast(Any, DOWN))
        label = Text("检查回答\n核对事实\n给出反馈", font_size=13).move_to(screen)
        workers = Group(worker, screen, label).get_grid(3, 2, buff=0.5)
        workers.set_height(7).to_edge(cast(Any, LEFT))
        self.add(workers)
        blocks, llm_text, flat_dials, last_dials = self.get_blocks_and_dials()
        machine = (
            VGroup(blocks, last_dials)
            .set_height(4)
            .center()
            .to_edge(cast(Any, RIGHT), buff=LARGE_BUFF)
        )
        last_dials.set_stroke(opacity=1)
        self.add(machine)
        for _ in range(4):
            self.play(
                LaggedStart(
                    (
                        dial.animate_set_value(dial.get_random_value())
                        for dial in last_dials
                    ),
                    lag_ratio=0.5 / len(last_dials),
                    run_time=2,
                )
            )
            self.wait()


class BadChatBotChinese(group_c.BadChatBot):
    def construct(self):
        # The original construct includes a legacy placeholder watermark; suppress it here.
        original_mark = group_c.add_placeholder_mark
        group_c.add_placeholder_mark = lambda *args: None
        try:
            super().construct()
        finally:
            group_c.add_placeholder_mark = original_mark

    def get_bot(self) -> Any:
        bot = SVGMobject(str(ROOT / "../素材/网络补充/robot-fontawesome.svg"))
        bot.set_fill(GREY_B).set_stroke(width=0).set_height(3)
        return bot

    def blink(self, bot):
        self.play(
            bot.animate.stretch(0.96, 1).set_anim_args(rate_func=there_and_back),
            run_time=0.3,
        )
