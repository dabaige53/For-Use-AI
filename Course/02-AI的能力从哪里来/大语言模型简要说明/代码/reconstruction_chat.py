"""Original-layout reconstruction scenes for the 0:00--6:59 edit.

The source scene bodies live in the read-only upstream snapshot and in the
generated ``group_a`` / ``group_b`` excerpts.  These subclasses only provide
the fixed display data and isolate the portions needed by the reconstruction.
No model, API, or model weights are used.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Iterable, cast

import numpy as np
from numpy.typing import NDArray

sys.path.insert(0, str(Path(__file__).resolve().parent))
import group_a as ga  # noqa: E402
from group_a import (
    Animation,
    BLUE,
    BLUE_B,
    ChatBotPrompt,
    DEGREES,
    DOWN,
    Dial,
    FadeIn,
    FadeOut,
    GREEN,
    GREEN_B,
    Group,
    GrowArrow,
    IN,
    ImageMobject,
    LEFT,
    PI,
    ParametricSurface,
    PremiseOfMLWithText,
    RIGHT,
    ReplacementTransform,
    SMALL_BUFF,
    ShowCreation,
    SurroundingRectangle,
    TEAL,
    Text as _ManimText,
    TexturedSurface,
    Transform,
    TransformFromCopy,
    UL,
    UP,
    VGroup,
    VMobject,
    Vector,
    WHITE,
    YELLOW,
    there_and_back,
)  # noqa: E402
import group_b as gb  # noqa: E402


if TYPE_CHECKING:
    from manimlib.typing import Vect3
else:
    Vect3 = Any

ROOT = Path(__file__).resolve().parent


def Text(*args, **kwargs):
    """Use the locally verified Chinese Pango font for every derived scene."""
    kwargs.setdefault("font", "PingFang SC")
    return _ManimText(*args, **kwargs)


# Inherited methods resolve Text in their defining modules, so bind both
# generated upstream excerpts to the same verified font for this renderer.
ga.Text = Text
gb.Text = Text


def get_chinese_script_texture() -> str:
    """Generate the paper artwork which the upstream scene wraps on its surfaces."""
    from PIL import Image, ImageDraw, ImageFont

    target = ROOT / "logs/reconstruction-chat/zh-480p/chinese-script-paper.png"
    target.parent.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (1200, 1600), "#fcf5e5")
    draw = ImageDraw.Draw(image)
    font_path = "/System/Library/Fonts/STHeiti Medium.ttc"
    title_font = ImageFont.truetype(font_path, 105)
    body_font = ImageFont.truetype(font_path, 84)
    draw.text((90, 100), "用户：", fill="#168fa4", font=title_font)
    lines = [
        "能否解释晶体管的历史，",
        "以及它与计算机有什么关系？",
        "晶体管是什么，它究竟怎样",
        "用于执行计算？",
        "",
        "AI 助手：",
    ]
    y = 230
    for line in lines:
        color = "#168f7a" if line == "AI 助手：" else "#191919"
        draw.text((90, y), line, fill=color, font=body_font)
        y += 132
    # A ragged lower edge remains visible after the second surface is swapped in.
    draw.polygon(
        [
            (0, 1470),
            (120, 1515),
            (240, 1460),
            (360, 1530),
            (480, 1475),
            (600, 1540),
            (720, 1470),
            (840, 1520),
            (960, 1460),
            (1080, 1510),
            (1200, 1470),
            (1200, 1600),
            (0, 1600),
        ],
        fill="#101010",
    )
    image.save(target)
    return str(target)


class ReconstructionPartialScriptIntro(gb.PartialScript):
    """The upstream scroll/unfurl intro with a local Chinese paper texture."""

    def construct(self):
        frame = self.frame
        self.set_floor_plane("xz")
        texture = get_chinese_script_texture()
        curled_script_img = ImageMobject(texture).set_height(7)

        curves = VGroup()
        for phase in (0, PI):
            curve = VMobject()
            points = [
                np.array(
                    [0.55 * np.sin(2.5 * t + phase), 5 * (t - 0.5), 0], dtype=np.float64
                )
                for t in np.linspace(0, 1, 31)
            ]
            curve.set_points_smoothly(cast(Iterable[Vect3], points)).insert_n_curves(
                100
            )
            curve.set_stroke(WHITE, 3).set_fill(opacity=0)
            curves.add(curve)
        resolution = (2, 200)
        surface_kw = dict(u_range=(-6, 6), v_range=(0.05, 0.95), resolution=resolution)
        templates = Group(
            ParametricSurface(lambda u, v, c=curve: (*c.pfp(v)[:2], u), **surface_kw)
            for curve in curves
        )
        templates[1].rotate(PI / 2, UP)
        templates[0].rotate(-PI / 2)
        flat_template = ParametricSurface(lambda u, v: (u, v, 0), **surface_kw)
        curled0 = TexturedSurface(templates[0], texture)
        curled1 = TexturedSurface(templates[1], texture)
        curled1_torn = TexturedSurface(templates[1], texture)
        flat_script = TexturedSurface(flat_template, texture).replace(
            curled_script_img, stretch=True
        )
        for script in (curled0, curled1):
            script.set_shading(0.25, 0.25, 0.35)
        curled1_torn.set_shading(0, 0, 0)
        flat_script.set_shading(0, 0, 0)

        frame.reorient(0, -1, 0, (-0.28, 0.69, 0.0), 14.43)
        self.play(
            TransformFromCopy(curled0, curled1),
            frame.animate.reorient(56, -17, 0, (-0.2, -1.52, -2.39), 20.05),
            run_time=3,
        )
        self.play(
            frame.animate.reorient(-6, -11, 0, (1.06, -1.22, -2.65), 20.05), run_time=8
        )
        tiny_in_shift = 1e-2 * cast(NDArray[np.float64], IN)
        self.play(
            FadeOut(curled1, shift=cast(Vect3, tiny_in_shift)),
            FadeIn(curled1_torn, shift=cast(NDArray[Any], tiny_in_shift)),
        )
        self.play(
            ReplacementTransform(curled1_torn, flat_script),
            frame.animate.to_default_state(),
            run_time=2,
        )
        self.wait()

        machine = self.get_transformer_drawing()
        machine[1].set_height(0.7).set_stroke(width=2).set_opacity(0)
        machine.remove(machine[-1])
        machine.set_height(3).to_edge(RIGHT)
        machine[1].become(Text("下一词\n预测器", font_size=32).move_to(machine[0][-1]))
        self.play(
            flat_script.animate.set_height(5).to_edge(LEFT),
            FadeIn(machine, lag_ratio=0.01),
        )
        self.add(machine)
        self.wait()

        out_arrow = Vector(DOWN, thickness=6).next_to(machine, DOWN)
        in_arrow = out_arrow.copy().next_to(machine, UP, SMALL_BUFF)
        in_text = Text("生存还是毁灭，这是一个 _").next_to(in_arrow, UP)
        in_text[-1].stretch(3, 0, about_edge=LEFT)
        prediction = Text("问题", font_size=72).next_to(out_arrow, DOWN)
        self.play(FadeIn(in_text), GrowArrow(in_arrow))
        self.animate_text_input(in_text, machine, position_text_over_machine=False)
        self.play(GrowArrow(out_arrow), FadeIn(prediction, cast(NDArray[Any], DOWN)))
        self.wait()

        script_text = Text(
            "用户：\n能否解释晶体管的历史，以及它与\n计算机有什么关系？晶体管是什么，\n它究竟怎样用于执行计算？\n\nAI 助手：",
            alignment="LEFT",
        )
        script_text["用户"].set_color(BLUE)
        script_text["AI 助手"].set_color(TEAL)
        script_text.set_width(0.89 * flat_script.get_width())
        script_text.next_to(flat_script.get_top(), DOWN, buff=0.33)
        self.play(
            FadeIn(script_text),
            FadeOut(flat_script),
            FadeOut(VGroup(in_text, in_arrow, prediction)),
        )
        self.wait()


SANTIAGO_COMPLETION = (
    "当然，圣地亚哥有很多值得体验的活动！你可以步行游览历史中心，参观武器广场和大教堂，"
    "也可以逛博物馆和城市公园。"
)


class ReconstructionChatBotPrompt(ChatBotPrompt):
    """Upstream ChatBotPrompt with the Santiago text shown in the final film."""

    system_prompt = "以下是用户与一位乐于助人、知识丰富的 AI 助手之间的对话。"
    user_prompt = "用户：请给我一些游览圣地亚哥时可以做什么的建议。"
    ai_seed = "AI 助手："
    machine_name = "大型\n语言\n模型"
    n_predictions = len(SANTIAGO_COMPLETION)

    def setup(self):
        super().setup()
        self._fixed_words = list(SANTIAGO_COMPLETION)
        self._fixed_index = 0

    def predict_next_token(self, text):
        index = min(self._fixed_index, len(self._fixed_words) - 1)
        selected = self._fixed_words[index]
        self._fixed_index += 1
        alternatives = list("的了是在和也可有去到参观游览体验")
        words = [selected] + [word for word in alternatives if word != selected][:11]
        probs = np.array(
            [
                0.70,
                0.09,
                0.06,
                0.04,
                0.03,
                0.025,
                0.02,
                0.015,
                0.01,
                0.005,
                0.003,
                0.002,
            ]
        )
        return words, probs / probs.sum()

    def animate_random_sample(self, bar_groups):
        highlight = SurroundingRectangle(bar_groups[0], buff=0.025)
        highlight.set_stroke(YELLOW, 2).set_fill(YELLOW, 0.25)
        self.play(FadeIn(highlight), Animation(bar_groups))
        bar_groups.add_to_back(highlight)

    def string_to_mob(self, text):
        seed = self.ai_seed.strip()
        if seed in text:
            text = text[text.index(seed) :]
        compact = text.replace(" ", "").replace("\n", "")
        wrapped = "\n".join(compact[n : n + 14] for n in range(0, len(compact), 14))
        result = Text(wrapped, font_size=self.font_size, alignment="LEFT")
        result.move_to(self.text_corner, UL)
        return result

    def construct(self):
        text_mob, next_word_line, machine = self.init_text_and_machine()
        machine.set_x(1.0)
        system_prompt = Text(
            "以下是用户与一位乐于助人、\n知识丰富的 AI 助手之间的对话。",
            font_size=32,
            alignment="LEFT",
        )
        user_prompt = Text(
            "用户：请给我一些游览圣地亚哥时\n可以做什么的建议。",
            font_size=32,
            alignment="LEFT",
        )
        ai_seed = Text(self.ai_seed, font_size=32)
        all_text = VGroup(system_prompt, user_prompt, ai_seed).arrange(
            DOWN, aligned_edge=LEFT, buff=0.75
        )
        top_left = cast(
            Vect3,
            3.5 * cast(NDArray[np.float64], UP) + 6.7 * cast(NDArray[np.float64], LEFT),
        )
        all_text.move_to(top_left, UL)
        self.remove(text_mob)
        self.add(all_text)
        text_mob = ai_seed
        self.text_corner = text_mob.get_corner(UL)
        next_word_line.next_to(ai_seed, RIGHT, aligned_edge=DOWN)
        self.cur_str = "\n\n".join([self.system_prompt, self.user_prompt, self.ai_seed])

        sys_rect = SurroundingRectangle(system_prompt).set_stroke(GREEN, 2)
        self.play(ShowCreation(sys_rect), system_prompt.animate.set_color(GREEN_B))
        self.wait()
        user_rect = SurroundingRectangle(user_prompt).set_stroke(BLUE, 2)
        sys_rect.insert_n_curves(100)
        self.play(
            ReplacementTransform(sys_rect, user_rect),
            user_prompt.animate.set_color(BLUE_B),
        )
        self.wait()
        self.play(FadeOut(user_rect))
        text_mob = all_text
        self.add(all_text.copy())
        for n in range(self.n_predictions):
            text_mob = self.new_selection_cycle(
                text_mob, next_word_line, machine, skip_anims=(n > 0)
            )


class ReconstructionTrainingExamples(PremiseOfMLWithText):
    """The rapid text-example cycle used at 142.5667 and inside Training."""

    n_examples = 13

    def init_data(self):
        self.examples = [
            ("那是最美好的，也是最糟糕的", "时代"),
            ("人们心里什么都有，人们面前一无", "所有"),
            ("我们正走向天堂，也正走向相反的", "方向"),
            ("消息在人群中迅速传开，所有声音汇成", "一片"),
            ("远处的火光穿过烟雾，映亮了", "夜空"),
        ]

    def new_input_output_example(self, in_arrow, out_arrow):
        sentence, output = random.choice(self.examples)
        in_text = Text(sentence, font_size=28).set_max_width(4).next_to(in_arrow, LEFT)
        out_text = Text(output).next_to(out_arrow, RIGHT)
        return in_text, out_text

    def construct(self):
        random.seed(self.random_seed)
        np.random.seed(self.random_seed)
        self.init_data()

        machine = self.get_machine()
        machine.set_width(4)
        machine.move_to(self.box_center)
        in_arrow = Vector(RIGHT).next_to(machine, LEFT)
        out_arrow = Vector(RIGHT).next_to(machine, RIGHT)
        param_label = Text("可调参数").next_to(machine, UP).set_color(BLUE)
        in_data, out_data = self.new_input_output_example(in_arrow, out_arrow)
        self.add(
            in_data,
            in_arrow,
            machine.box,
            machine.dials,
            param_label,
            out_arrow,
            out_data,
        )
        self.wait(1 / 30)

        for _ in range(self.n_examples):
            new_in_data, new_out_data = self.new_input_output_example(
                in_arrow, out_arrow
            )
            self.play(
                machine.random_change_animation(run_time=0.5),
                FadeOut(in_data, time_span=(0, 0.35)),
                FadeOut(out_data, time_span=(0, 0.35)),
                FadeIn(new_in_data, time_span=(0, 0.35)),
                FadeIn(new_out_data, time_span=(0, 0.35)),
                run_time=0.5,
            )
            in_data, out_data = new_in_data, new_out_data


TRANSISTOR_COMPLETION = (
    "晶体管是一种用于放大或切换电子信号的半导体器件。它由多层半导体材料构成，"
    "并通过发射极、基极和集电极等端子控制电流，从而执行计算。"
)


class ReconstructionPartialCompletion(gb.PartialScript):
    """Only PartialScript's post-scroll, word-by-word completion animation."""

    def construct(self):
        random.seed(1)
        np.random.seed(1)
        script_text = self.get_text()
        script_text.set_width(5.1).to_edge(LEFT)

        machine = self.get_transformer_drawing()
        machine[1].set_height(0.7).set_stroke(width=2).set_opacity(0)
        machine.remove(machine[-1])
        machine.set_height(3).to_edge(RIGHT)
        machine.scale(1.25, about_edge=RIGHT)
        out_arrow = Vector(DOWN, thickness=6).next_to(machine, DOWN, buff=0.5)

        blocks = machine[0]
        dials = Dial().get_grid(11, 16)
        dials.set_width(blocks[-1].get_width() * 0.95)
        dials.rotate(5 * DEGREES, RIGHT).rotate(10 * DEGREES, UP)
        dials.move_to(blocks[-1]).set_stroke(opacity=0.5).set_z_index(2)
        for dial in dials:
            dial.set_value(dial.get_random_value())

        font_size = 48 * (script_text[0].get_height() / Text("H").get_height())
        words = list(TRANSISTOR_COMPLETION)
        curr_answer = Text("", font_size=font_size)
        curr_answer.next_to(script_text, DOWN, aligned_edge=LEFT)
        self.add(script_text, machine, dials)
        self.wait(1 / 30)

        for index, word in enumerate(words):
            prediction = Text(word, font_size=72).next_to(out_arrow, DOWN)
            mover = VGroup(script_text, curr_answer).copy()
            mover.set_height(1.8).next_to(machine, UP, SMALL_BUFF)
            prefix = TRANSISTOR_COMPLETION[: index + 1]
            wrapped = "\n".join(prefix[n : n + 18] for n in range(0, len(prefix), 18))
            new_answer = Text(wrapped, font_size=font_size, alignment="LEFT")
            new_answer.next_to(script_text, DOWN, aligned_edge=LEFT).set_color(WHITE)
            target = new_answer[-1].copy().set_color(YELLOW)
            new_answer[-1].set_opacity(0)
            curr_answer.become(new_answer)
            self.add(curr_answer, mover, prediction)
            self.play(
                Transform(prediction, target),
                FadeOut(mover),
                cast(Any, blocks.animate.set_color(TEAL)).set_anim_args(
                    rate_func=there_and_back
                ),
                run_time=0.16,
            )
            curr_answer[-1].set_opacity(1).set_color(YELLOW)
            self.remove(prediction)

    def get_text(self):
        script_text = Text(
            "用户：\n能否解释晶体管的历史，以及它与\n计算机有什么关系？晶体管是什么，\n它究竟怎样用于执行计算？\n\nAI 助手：",
            alignment="LEFT",
        )
        script_text["用户"].set_color(BLUE)
        script_text["AI 助手"].set_color(TEAL)
        script_text.set_height(4).to_edge(UP)
        return script_text
