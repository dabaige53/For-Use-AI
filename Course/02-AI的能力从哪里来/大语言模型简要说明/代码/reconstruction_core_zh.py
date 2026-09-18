"""Chinese adaptations of original scenes; old render files are never changed."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, cast

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import group_b as base  # noqa: E402
import group_a as extra  # noqa: E402
from group_b import (  # noqa: E402
    Animation,
    AnimationGroup,
    Arrow,
    BLACK,
    BLUE,
    ChangeDecimalToValue,
    ContextAnimation,
    DEGREES,
    DL,
    DOWN,
    DR,
    Dial,
    DrawBorderThenFill,
    FadeIn,
    FadeOut,
    FadeTransform,
    FlashAround,
    FlashUnder,
    GREY_B,
    GrowArrow,
    GrowFromCenter,
    GrowFromPoint,
    InteractiveScene,
    LARGE_BUFF,
    LEFT,
    LaggedStart,
    LaggedStartMap,
    Line,
    Mobject,
    MoveToTarget,
    ORIGIN,
    OUT,
    RED,
    RIGHT,
    Restore,
    ShowCreation,
    SMALL_BUFF,
    SimpleAutogregression,
    Square,
    SurroundingRectangle,
    TEAL,
    Tex,
    Text as _OriginalText,
    Transform,
    TransformFromCopy,
    UL,
    UP,
    UR,
    Uncreate,
    UpdateFromFunc,
    VFadeInThenOut,
    VGroup,
    VShowPassingFlash,
    Vector,
    VectorizedPoint,
    VMobject,
    WHITE,
    Write,
    YELLOW,
    break_into_words,
    get_piece_rectangles,
    it,
    np,
    random,
    softmax,
    there_and_back,
    value_to_color,
)


def _as_manim_value(value: object) -> Any:
    """Keep ManimGL's runtime value while crossing its dynamic typing boundary."""
    return cast(Any, value)


TRANSLATIONS = {
    "Large\nLanguage\nModel": "大型\n语言\n模型",
    "France": "法国",
    "Seed text": "起始文本",
    "Initially random": "初始参数随机",
    "It was the best\nof times it was\nthe _": "这是最好的时代，\n也是最 _",
    "It was the best of times it was the": "这是最好的时代，也是最",
    "Parameter / Weight": "参数 / 权重",
    "Parameter": "参数",
    "/ Weight": "/ 权重",
    "Large Language Model": "大型语言模型",
    "Large": "大型",
    "worst": "坏",
    "age": "久",
    "worse": "差",
    "best": "好",
    "most": "多",
    "end": "后",
    "very": "近",
    "blur": "模糊",
}


def Text(text, **kwargs):
    kwargs.setdefault("font", "PingFang SC")
    return _OriginalText(cast(str, TRANSLATIONS.get(text, text)), **kwargs)


base._DEMO_TOKENS = (
    " 法国",
    " 欧洲",
    " 巴黎",
    " 意大利",
    " 德国",
    " 西班牙",
    " 英国",
    " 亚洲",
    " 美国",
    " 中国",
    " 北部",
    " 南部",
)


def _fixed_paris_prediction(text, n_shown=7, random_seed=0):
    """Fixed demonstration distribution: France is the most likely continuation."""
    tokens = list(base._DEMO_TOKENS[:n_shown])
    weights = np.exp(-1.15 * np.arange(len(tokens), dtype=float))
    return tokens, weights / weights.sum()


base._demo_predict_next_token = _fixed_paris_prediction
base.Text = Text
extra.Text = Text


class PredictTheNextWord(SimpleAutogregression):
    text_corner = 3.5 * _as_manim_value(UP) + 6.5 * _as_manim_value(LEFT)
    machine_name = "Large\nLanguage\nModel"
    seed_text = "巴黎 这座 城市 位于"
    model = "gpt3"
    n_shown_predictions = 12
    random_seed = 2

    def construct(self):
        # Setup machine
        text_mob, next_word_line, machine = self.init_text_and_machine()
        machine.move_to(ORIGIN)
        machine[1].set_backstroke(BLACK, 3)

        text_group = VGroup(text_mob, next_word_line)
        text_group.save_state()
        text_group.scale(1.5)
        text_group.match_x(machine[0]).to_edge(UP)

        # Introduce the machine
        in_arrow = Arrow(text_group, machine[0].get_top(), thickness=5)
        frame = self.frame
        self.set_floor_plane("xz")
        blocks = machine[0]
        llm_text = machine[1]
        block_outlines = blocks.copy()
        block_outlines.set_fill(opacity=0)
        block_outlines.set_stroke(GREY_B, 2)
        block_outlines.insert_n_curves(20)

        flat_dials, last_dials = self.get_machine_dials(blocks)

        self.clear()
        frame.reorient(-31, -4, -5, (-0.24, -0.26, -0.06), 3)
        self.play(
            FadeIn(blocks, shift=_as_manim_value(0.0), lag_ratio=0.01),
            LaggedStartMap(
                VShowPassingFlash,
                block_outlines.family_members_with_points(),
                time_width=2.0,
                lag_ratio=0.01,
                remover=True,
            ),
            LaggedStartMap(VFadeInThenOut, flat_dials, lag_ratio=0.001, remover=True),
            Write(llm_text, time_span=(2, 4), stroke_color=WHITE),
            FadeIn(last_dials, time_span=(4, 5)),
            frame.animate.reorient(0, 0, 0, (-0.17, -0.12, 0.0), 4.50),
            run_time=6,
        )
        blocks[-1].add(last_dials)
        self.play(
            frame.animate.to_default_state(),
            FadeIn(text_group, _as_manim_value(UP)),
            GrowFromCenter(in_arrow),
            run_time=3,
        )

        # Single word prediction
        out_arrow = Vector(1.5 * _as_manim_value(RIGHT), thickness=5)
        out_arrow.next_to(machine[0][-1], RIGHT)
        prediction = Text("France", font_size=72)
        prediction.next_to(out_arrow, RIGHT)

        self.animate_text_input(
            text_mob,
            machine,
            position_text_over_machine=False,
        )
        self.play(
            LaggedStart(
                (
                    TransformFromCopy(
                        VectorizedPoint(_as_manim_value(machine.get_right())), letter
                    )
                    for letter in prediction
                ),
                lag_ratio=0.05,
            ),
            GrowArrow(out_arrow),
        )
        self.wait()
        machine.replace_submobject(2, out_arrow)

        # Probability distribution
        self.play(FadeOut(prediction, DOWN))
        self.animate_prediction_ouptut(machine, self.cur_str)
        self.wait()

    def get_machine_dials(self, blocks):
        dials = VGroup(
            Dial().get_grid(8, 12).set_width(0.9 * block.get_width()).move_to(block)
            for block in blocks
        )
        dials.set_stroke(opacity=0.5)
        for group in dials:
            for dial in group:
                dial_mob = cast(Dial, dial)
                dial_mob.set_value(dial_mob.get_random_value())
        flat_dials = VGroup(*it.chain(*dials))
        last_dials = dials[-1].copy()
        last_dials.set_stroke(opacity=0.1)

        return flat_dials, last_dials


class ShowMachineWithDials(PredictTheNextWord):
    words = ["坏", "久", "差", "好", "多", "后", "近", "模糊"]
    logprobs = [4.0, 2.15, 1.89, 1.4, 0.1, -0.18, -0.23, -0.61]

    def construct(self):
        # Show machine (same position as in PredictTheNextWord)
        frame = self.frame
        self.set_floor_plane("xz")
        blocks, llm_text, flat_dials, last_dials = self.get_blocks_and_dials()

        self.clear()
        self.add(frame)
        frame.reorient(0, 0, 0, (-0.17, -0.12, 0.0), 4.50)
        self.add(blocks, llm_text, last_dials)

        # Prepare dial highlight
        last_dials.target = last_dials.generate_target()
        self.fix_dials(last_dials.target)

        small_rect = SurroundingRectangle(last_dials[0], buff=0.025)
        small_rect.set_stroke(BLUE, 2)
        big_rect = small_rect.copy().scale(4)
        big_rect.next_to(
            blocks,
            UP,
            buff=SMALL_BUFF,
            aligned_edge=_as_manim_value(LEFT) + _as_manim_value(OUT),
        )
        big_rect.shift(1.5 * _as_manim_value(RIGHT))
        big_dial = last_dials[0].copy().scale(4).set_stroke(opacity=1)
        big_dial.move_to(big_rect)
        rect_lines = VGroup(
            Line(small_rect.get_corner(UL), big_rect.get_corner(DL)),
            Line(small_rect.get_corner(UR), big_rect.get_corner(DR)),
        )
        rect_lines.set_stroke(WHITE, width=(1, 3))
        highlighed_parameter_group = VGroup(small_rect, rect_lines, big_rect, big_dial)

        last_dials.set_stroke(width=1, opacity=1)
        self.play(
            MoveToTarget(last_dials),
            FadeOut(llm_text),
            FadeIn(small_rect),
        )

        # Show an example input and output
        example = self.get_example(blocks)
        in_text, in_arrow, out_arrow, bar_groups = example
        in_arrow = cast(Arrow, in_arrow)
        out_arrow = cast(Arrow, out_arrow)
        logprobs = cast(Any, example).logprobs
        true_probs = 100 * softmax(logprobs)
        bar_groups = self.get_output_distribution(self.words, 0.1 * logprobs, out_arrow)

        self.play(
            LaggedStart(
                ShowCreation(rect_lines, lag_ratio=0),
                TransformFromCopy(small_rect, big_rect),
                TransformFromCopy(last_dials[0], big_dial),
                FadeIn(in_text),
                GrowArrow(in_arrow),
                FadeIn(bar_groups),
                GrowArrow(out_arrow),
            ),
            frame.animate.reorient(0, 0, 0, (-0.43, 0.38, 0.0), 7.05),
            run_time=2,
        )
        self.play(
            last_dials[0].animate_set_value(0.8),
            big_dial.animate_set_value(0.8),
            LaggedStart(
                (
                    dial.animate_set_value(dial.get_random_value())
                    for dial in last_dials[1:]
                ),
                lag_ratio=1.0 / len(last_dials),
            ),
            *(
                self.bar_group_change_animation(bg, value)
                for bg, value in zip(bar_groups[:-1], true_probs)
            ),
            run_time=3,
        )
        self.wait()

        # Play around tweaking the parameters, and seeing the output change
        self.play(
            LaggedStart(
                (dial.animate_set_value(0) for dial in last_dials[:12]),
                lag_ratio=0.01,
            ),
            big_dial.animate_set_value(0),
            self.bar_group_change_animation(bar_groups[0], 50),
            self.bar_group_change_animation(bar_groups[1], 34),
            self.bar_group_change_animation(bar_groups[2], 5),
            run_time=4,
        )
        self.play(
            LaggedStart(
                (dial.animate_set_value(1) for dial in last_dials[:12]),
                lag_ratio=0.01,
            ),
            big_dial.animate_set_value(1),
            self.bar_group_change_animation(bar_groups[0], 80),
            self.bar_group_change_animation(bar_groups[1], 5),
            self.bar_group_change_animation(bar_groups[2], 15),
            run_time=4,
        )
        self.wait()

        # Mention randomness
        random_words = Text("Initially random")
        random_words.next_to(blocks, UP)
        random_words.set_color(RED)
        out_dots = Tex(R"...", font_size=120)
        out_dots.next_to(out_arrow, RIGHT)

        self.play(
            FadeOut(big_rect),
            Uncreate(rect_lines, lag_ratio=0),
            FadeOut(small_rect),
            Transform(big_dial, last_dials[0]),
        )
        self.play(
            Write(random_words),
            LaggedStart(
                (
                    dial.animate_set_value(dial.get_random_value())
                    for dial in last_dials
                ),
                lag_ratio=0.5 / len(last_dials),
                run_time=2,
            ),
            FadeOut(bar_groups),
        )
        self.play(Write(out_dots))
        self.wait()
        self.play(
            FadeOut(out_dots),
            FadeOut(random_words),
            FadeIn(bar_groups),
        )

        # Show many many parameters
        example.save_state()
        blocks.save_state()
        last_dials.save_state()
        all_dials = VGroup(*flat_dials, *last_dials)
        all_dials.generate_target()
        all_dials_target = cast(VGroup, all_dials.target)
        all_dials_target.space_out_submobjects(3)
        new_dials = VGroup(
            all_dials_target.copy().shift(
                3
                * 2
                * x
                * (
                    _as_manim_value(flat_dials.get_center())
                    - _as_manim_value(last_dials.get_center())
                )
            )
            for x in range(1, 9)
        )

        self.play(
            FadeOut(example),
            FadeOut(blocks),
            FadeIn(flat_dials),
            FadeOut(bar_groups),
            FadeOut(out_arrow),
        )
        self.play(
            FadeOut(highlighed_parameter_group),
            MoveToTarget(all_dials),
            LaggedStart(
                (
                    TransformFromCopy(all_dials.copy().set_opacity(0), nd)
                    for nd in new_dials
                ),
                lag_ratio=0.05,
            ),
            frame.animate.reorient(-9, 0, 0, (-0.71, -0.07, -0.06), 9.64),
            run_time=4,
        )
        self.wait()

    def get_blocks_and_dials(self):
        machine = self.get_transformer_drawing()
        machine.move_to(ORIGIN)
        self.machine = machine

        blocks = machine[0]
        llm_text = machine[1]
        llm_text.set_backstroke(BLACK, 2)
        flat_dials, last_dials = self.get_machine_dials(blocks)
        return blocks, llm_text, flat_dials, last_dials

    def get_example(self, blocks):
        in_text = Text(
            "It was the best\nof times it was\nthe _", alignment="LEFT", font_size=30
        )
        in_text[-1].stretch(4, 0, about_edge=LEFT)
        in_text.next_to(blocks, LEFT, LARGE_BUFF)
        in_arrow = Arrow(in_text, blocks)

        out_arrow = Vector(RIGHT)
        out_arrow.next_to(blocks[-1], RIGHT, buff=0.1)
        logprobs = np.array(self.logprobs)
        bar_groups = self.get_output_distribution(self.words, logprobs, out_arrow)
        example = VGroup(in_text, in_arrow, out_arrow, bar_groups)
        cast(Any, example).logprobs = logprobs
        return example

    def fix_dials(self, dials):
        for dial in dials:
            dial.set_stroke(width=1, opacity=1)
            dial.needle.set_stroke(width=(2, 0))
        return dials

    def bar_group_change_animation(self, bar_group, new_value):
        text, rect, value_mob = bar_group
        buff = value_mob.get_left() - rect.get_right()
        factor = new_value / value_mob.get_value()

        return AnimationGroup(
            rect.animate.stretch(factor, 0, about_edge=LEFT),
            ChangeDecimalToValue(value_mob, new_value),
            UpdateFromFunc(
                text, lambda m: value_mob.move_to(rect.get_right() + buff, LEFT)
            ),
        )

    def get_output_distribution(self, words, logprobs, out_arrow):
        probs = softmax(logprobs)
        bar_groups = self.get_distribution(words, probs, self.machine, width_100p=1.0)
        bar_groups.next_to(out_arrow, RIGHT)
        return bar_groups


class ShowSingleTrainingExample(ShowMachineWithDials):
    logprobs = [4.0, 6.15, 1.89, 1.4, 0.1, -0.18, -0.23, -0.61]

    def construct(self):
        # Add state from before
        frame = self.frame
        self.set_floor_plane("xz")

        blocks, llm_text, flat_dials, last_dials = self.get_blocks_and_dials()
        self.fix_dials(last_dials)
        example = self.get_example(blocks)
        in_text, in_arrow, out_arrow, bar_groups = example

        self.add(blocks, last_dials)

        # Show example up top
        parts = ("这是最好的时代，也是最", "坏")
        sentence = Text(" ".join(parts))
        start = sentence[parts[0]][0]
        end = sentence[parts[1]][0]
        sentence.set_width(10)
        sentence.next_to(blocks, UP, buff=1.5)

        start_rect = SurroundingRectangle(start)
        start_rect.set_stroke(BLUE, 2)
        start_rect.set_fill(BLUE, 0.2)
        end_rect = SurroundingRectangle(end)
        end_rect.match_height(start_rect, stretch=True).match_y(start_rect)
        end_rect.set_stroke(YELLOW, 2)
        end_rect.set_fill(YELLOW, 0.2)
        arrow = Arrow(
            start_rect.get_top(),
            end_rect.get_top(),
            path_arc=-90 * DEGREES,
            thickness=5,
        )
        arrow.set_fill(border_width=1)

        frame.reorient(0, 0, 0, _as_manim_value((-0.36, 0.97, 0.0)), 7.52)
        self.play(FadeIn(sentence, _as_manim_value(UP)))
        self.play(
            LaggedStartMap(DrawBorderThenFill, VGroup(start_rect, end_rect)),
            FadeIn(arrow),
        )
        self.remove(last_dials)
        self.play(
            LaggedStart(
                AnimationGroup(
                    TransformFromCopy(start, in_text[:-1]),
                    TransformFromCopy(end_rect, in_text[-1]),
                    FadeIn(in_arrow),
                ),
                LaggedStart(
                    (
                        _as_manim_value(block.animate)
                        .set_color(block.get_color() if block is blocks[-1] else TEAL)
                        .set_anim_args(rate_func=there_and_back)
                        for block in blocks
                    ),
                    group=blocks,
                    lag_ratio=0.1,
                    run_time=1,
                ),
                Animation(last_dials),
                GrowArrow(cast(Arrow, out_arrow)),
                LaggedStartMap(GrowFromPoint, bar_groups, point=out_arrow.get_start()),
                lag_ratio=0.3,
            )
        )
        self.wait()

        # Flag bad prediction
        out_rects = VGroup(SurroundingRectangle(bg) for bg in bar_groups[:2])
        out_rects.set_stroke(RED, 3)
        annotations = VGroup(
            Tex(tex, font_size=60).next_to(rect, LEFT, buff=SMALL_BUFF)
            for rect, tex in zip(out_rects, [R"\uparrow", R"\downarrow"])
        )
        annotations.set_color(RED)

        self.play(
            FadeTransform(end_rect.copy(), out_rects[0]),
            Write(annotations[0]),
        )
        self.wait()
        self.play(
            FadeTransform(cast(Mobject, out_rects[0]), cast(Mobject, out_rects[1])),
            FadeTransform(cast(Mobject, annotations[0]), cast(Mobject, annotations[1])),
        )
        self.wait()
        self.play(
            FadeOut(out_rects[1]),
            FadeOut(annotations[1]),
        )

        # Adjust
        self.play(
            LaggedStart(
                (
                    dial.animate_set_value(dial.get_random_value())
                    for dial in last_dials
                ),
                lag_ratio=1.0 / len(last_dials),
            ),
            LaggedStart(
                (
                    FlashAround(
                        dial, stroke_width=2, color=YELLOW, time_width=1, buff=0.025
                    )
                    for dial in last_dials
                ),
                lag_ratio=1.0 / len(last_dials),
            ),
            self.bar_group_change_animation(bar_groups[0], 70),
            self.bar_group_change_animation(bar_groups[1], 20),
            self.bar_group_change_animation(bar_groups[2], 8),
            run_time=6,
        )


class ParameterWeight(InteractiveScene):
    def construct(self):
        # Test
        text = Text("Parameter / Weight", font_size=72)
        text.to_edge(UP)
        text.set_color(YELLOW)
        param = text["参数"][0]
        param.save_state()
        param.set_x(0)

        self.play(Write(cast(VMobject, param)))
        self.wait()
        self.play(
            LaggedStart(
                Restore(param),
                FadeIn(text["/ 权重"]),
            )
        )
        self.wait()


class LargeInLargeLanguageModel(InteractiveScene):
    def construct(self):
        # Test
        text = Text("Large Language Model", font_size=72)
        text.to_edge(UP)
        large = text["大型"][0]
        large.save_state()
        large.set_x(0)

        self.add(large)
        self.play(FlashUnder(large), large.animate.set_color(YELLOW))
        self.play(
            Restore(large, path_arc=-30 * DEGREES),
            Write(text[len(large) :], time_span=(0.5, 1.5)),
        )
        self.wait()


class SerialProcessing(InteractiveScene):
    phrase = "这 是 最好 的 时代 也 是 最坏 的 时代"
    phrase_center = 2 * _as_manim_value(UP)

    def construct(self):
        # Set up words
        words = self.get_words()
        rects = get_piece_rectangles(words)

        self.add(rects)
        self.add(words)

        # Animate in the vectors
        vectors = VGroup(
            self.get_abstract_vector().next_to(word, DOWN, LARGE_BUFF) for word in words
        )
        last_vect = VGroup(VectorizedPoint(rects[0].get_bottom()))

        for word, vect in zip(words, vectors):
            self.play(
                FadeIn(vect, run_time=2),
                LaggedStart(
                    (
                        ContextAnimation(
                            square,
                            VGroup(*word, *last_vect),
                            direction=DOWN,
                            lag_ratio=0.01,
                            path_arc=30 * DEGREES,
                        )
                        for square in vect
                    ),
                    lag_ratio=0.05,
                    run_time=2,
                ),
                last_vect.animate.set_opacity(0.2),
            )
            last_vect = vect

    def get_words(self):
        result = break_into_words(Text(self.phrase))
        result.move_to(self.phrase_center)
        return result

    def get_abstract_vector(self, values=None, default_length=10, elem_size=0.2):
        if values is None:
            values = np.random.uniform(-1, 1, default_length)
        result = Square().get_grid(len(values), 1, buff=0)
        result.set_width(elem_size)
        result.set_stroke(WHITE, 1)
        for square, value in zip(result, values):
            color = value_to_color(value, min_value=0, max_value=1)
            square.set_fill(color, opacity=1)
        return result


class ParallelProcessing(SerialProcessing):
    def construct(self):
        # Set up words
        words = self.get_words()
        rects = get_piece_rectangles(words)

        self.add(rects)
        self.add(words)

        # Animate in the vectors
        vectors = VGroup(
            self.get_abstract_vector().next_to(word, DOWN, buff=1.5) for word in words
        )

        lines = VGroup(
            Line(
                rect.get_bottom(),
                vect.get_top(),
                buff=0.05,
                stroke_color=WHITE,
                stroke_width=2 * random.random() ** 3,
            )
            for rect in rects
            for vect in vectors
        )
        lines.shuffle()

        for vect, word in zip(vectors, words):
            vect.save_state()
            for square in vect:
                square.move_to(word)
                square.set_opacity(0)

        self.play(
            LaggedStartMap(ShowCreation, lines, lag_ratio=0.01),
            LaggedStartMap(Restore, vectors, lag_ratio=0),
        )
        self.play(lines.animate.set_stroke(opacity=0.25))
        self.wait()


class ChineseMachineFront(ShowMachineWithDials):
    def construct(self):
        # Show machine (same position as in PredictTheNextWord)
        frame = self.frame
        self.set_floor_plane("xz")
        blocks, llm_text, flat_dials, last_dials = self.get_blocks_and_dials()

        self.clear()
        self.add(frame)
        frame.reorient(0, 0, 0, (-0.17, -0.12, 0.0), 4.50)
        self.add(blocks, llm_text, last_dials)

        # Prepare dial highlight
        last_dials.target = last_dials.generate_target()
        self.fix_dials(last_dials.target)

        small_rect = SurroundingRectangle(last_dials[0], buff=0.025)
        small_rect.set_stroke(BLUE, 2)
        big_rect = small_rect.copy().scale(4)
        big_rect.next_to(
            blocks,
            UP,
            buff=SMALL_BUFF,
            aligned_edge=_as_manim_value(LEFT) + _as_manim_value(OUT),
        )
        big_rect.shift(1.5 * _as_manim_value(RIGHT))
        big_dial = last_dials[0].copy().scale(4).set_stroke(opacity=1)
        big_dial.move_to(big_rect)
        rect_lines = VGroup(
            Line(small_rect.get_corner(UL), big_rect.get_corner(DL)),
            Line(small_rect.get_corner(UR), big_rect.get_corner(DR)),
        )
        rect_lines.set_stroke(WHITE, width=(1, 3))

        last_dials.set_stroke(width=1, opacity=1)
        self.play(
            MoveToTarget(last_dials),
            FadeOut(llm_text),
            FadeIn(small_rect),
        )

        # Show an example input and output
        example = self.get_example(blocks)
        in_text, in_arrow, out_arrow, bar_groups = example
        in_arrow = cast(Arrow, in_arrow)
        out_arrow = cast(Arrow, out_arrow)
        logprobs = cast(Any, example).logprobs
        true_probs = 100 * softmax(logprobs)
        bar_groups = self.get_output_distribution(self.words, 0.1 * logprobs, out_arrow)

        self.play(
            LaggedStart(
                ShowCreation(rect_lines, lag_ratio=0),
                TransformFromCopy(small_rect, big_rect),
                TransformFromCopy(last_dials[0], big_dial),
                FadeIn(in_text),
                GrowArrow(in_arrow),
                FadeIn(bar_groups),
                GrowArrow(out_arrow),
            ),
            frame.animate.reorient(0, 0, 0, (-0.43, 0.38, 0.0), 7.05),
            run_time=2,
        )
        self.play(
            last_dials[0].animate_set_value(0.8),
            big_dial.animate_set_value(0.8),
            LaggedStart(
                (
                    dial.animate_set_value(dial.get_random_value())
                    for dial in last_dials[1:]
                ),
                lag_ratio=1.0 / len(last_dials),
            ),
            *(
                self.bar_group_change_animation(bg, value)
                for bg, value in zip(bar_groups[:-1], true_probs)
            ),
            run_time=3,
        )
        self.wait()

        # Play around tweaking the parameters, and seeing the output change
        self.play(
            LaggedStart(
                (dial.animate_set_value(0) for dial in last_dials[:12]),
                lag_ratio=0.01,
            ),
            big_dial.animate_set_value(0),
            self.bar_group_change_animation(bar_groups[0], 50),
            self.bar_group_change_animation(bar_groups[1], 34),
            self.bar_group_change_animation(bar_groups[2], 5),
            run_time=4,
        )
        self.play(
            LaggedStart(
                (dial.animate_set_value(1) for dial in last_dials[:12]),
                lag_ratio=0.01,
            ),
            big_dial.animate_set_value(1),
            self.bar_group_change_animation(bar_groups[0], 80),
            self.bar_group_change_animation(bar_groups[1], 5),
            self.bar_group_change_animation(bar_groups[2], 15),
            run_time=4,
        )
        self.wait()

        # Mention randomness
        random_words = Text("Initially random")
        random_words.next_to(blocks, UP)
        random_words.set_color(RED)
        out_dots = Tex(R"...", font_size=120)
        out_dots.next_to(out_arrow, RIGHT)

        self.play(
            FadeOut(big_rect),
            Uncreate(rect_lines, lag_ratio=0),
            FadeOut(small_rect),
            Transform(big_dial, last_dials[0]),
        )
        self.play(
            Write(random_words),
            LaggedStart(
                (
                    dial.animate_set_value(dial.get_random_value())
                    for dial in last_dials
                ),
                lag_ratio=0.5 / len(last_dials),
                run_time=2,
            ),
            FadeOut(bar_groups),
        )
        self.play(Write(out_dots))
        self.wait()
        self.play(
            FadeOut(out_dots),
            FadeOut(random_words),
            FadeIn(bar_groups),
        )
