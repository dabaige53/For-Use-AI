"""Original paper/model reveal composition, using published paper and Google mark."""

import sys
from typing import Any, cast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from reconstruction_core_zh import (  # noqa: E402
    DOWN,
    FadeIn,
    LEFT,
    PredictTheNextWord,
    RIGHT,
    Text,
    UP,
    Write,
)  # noqa: E402
from manimlib import ImageMobject, SVGMobject  # noqa: E402


class PaperRevealChinese(PredictTheNextWord):
    def construct(self):
        paper = ImageMobject(
            str(ROOT / "../素材/网络补充/attention-paper-cover.png")
        )
        paper.set_width(5.4).move_to(3.7 * cast(Any, LEFT) + 0.9 * cast(Any, DOWN))
        google = SVGMobject(str(ROOT / "../素材/网络补充/google-g.svg")).set_height(
            1.7
        )
        google.next_to(paper, cast(Any, UP), buff=0.5).align_to(paper, cast(Any, LEFT))
        machine = self.get_transformer_drawing()
        machine[1].set_opacity(0)
        machine.set_width(6.2).move_to(3.1 * cast(Any, RIGHT) + 0.7 * cast(Any, DOWN))
        title = Text("Transformer 架构", font_size=52).move_to(
            3.1 * cast(Any, RIGHT) + 2 * cast(Any, UP)
        )
        self.add(machine)
        self.play(FadeIn(paper), FadeIn(google), run_time=1)
        self.wait(1)
        self.play(Write(title), run_time=2)
        self.wait(2)
