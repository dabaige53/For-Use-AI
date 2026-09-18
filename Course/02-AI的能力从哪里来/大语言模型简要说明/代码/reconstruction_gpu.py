"""Original attention.py Parallelizability; GPU icon cropped from official lesson image."""

import sys
from typing import Any, cast
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import tex_support  # noqa: E402,F401
from manimlib import (  # noqa: E402
    BLUE,
    DOWN,
    GREY_B,
    ImageMobject,
    InteractiveScene,
    LEFT,
    LaggedStartMap,
    RIGHT,
    SMALL_BUFF,
    ShowPassingFlash,
    TEAL,
    Tex,
    Text,
    UP,
    VGroup,
    VMobject,
)  # noqa: E402


class Parallelizability(InteractiveScene):
    def construct(self):
        # Set up curves
        n_instances = 20
        comp_syms = Tex(R"+\,\times").replicate(n_instances)
        comp_syms.arrange(cast(Any, DOWN))
        comp_syms.set_height(5.5)
        comp_syms.to_edge(cast(Any, DOWN))
        left_point = comp_syms.get_left() + 2 * cast(Any, LEFT)
        right_point = comp_syms.get_right() + 2 * cast(Any, RIGHT)
        curves = VGroup()
        for sym in comp_syms:
            curve = VMobject()
            curve.start_new_path(left_point)
            curve.add_cubic_bezier_curve_to(
                left_point + cast(Any, RIGHT),
                sym.get_left() + cast(Any, LEFT),
                sym.get_left(),
            )
            curve.add_line_to(sym.get_right())
            curve.add_cubic_bezier_curve_to(
                sym.get_right() + cast(Any, RIGHT),
                right_point + cast(Any, LEFT),
                right_point,
            )
            curve.insert_n_curves(10)
            curves.add(curve)
        curves.set_stroke(width=(0, 2, 2, 2, 0))
        curves.set_submobject_colors_by_gradient(TEAL, BLUE)

        # Setup words
        in_word = Text("Input")
        out_word = Text("output")
        in_word.next_to(left_point, cast(Any, LEFT), SMALL_BUFF)
        out_word.next_to(right_point, cast(Any, RIGHT), SMALL_BUFF)
        self.add(comp_syms, in_word, out_word)

        # GPU symbol
        gpu = ImageMobject(
            str(ROOT / "assets/images/gpu-icon-original.png")
        )
        gpu.set_width(1.5)
        gpu.next_to(comp_syms, cast(Any, UP))
        gpu_name = Text("GPU")
        gpu_name.next_to(gpu, cast(Any, UP))
        gpu_name.set_fill(GREY_B)
        self.add(gpu, gpu_name)

        # Animation
        for n in range(4):
            curves.shuffle()
            self.play(
                LaggedStartMap(
                    ShowPassingFlash, curves, lag_ratio=5e-3, time_width=1.5, run_time=4
                )
            )
