"""Generated upstream scene excerpts for render group A.

Regenerate with ``.venv/bin/python build_group_a.py``. Scene definitions retain
their upstream source text except the explicitly documented asset/API adapters.
"""

from __future__ import annotations

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent)) if 'Path' in globals() else None
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import tex_support
from manimlib import *
import manimlib.utils.tex_file_writing as _tex_writing
from typing import Optional, Tuple
import itertools as it
import math
import os
import random
import re
import warnings

ROOT = Path(__file__).parent
DATA_DIR = ROOT / "assets" / "data"
WORD_FILE = DATA_DIR / "OWL3_Dictionary.txt"

_original_tex_renderer = _tex_writing.full_tex_to_svg
def _group_a_tex_renderer(full_tex, compiler='latex', message=''):
    # Tectonic uses XeTeX; this pdfTeX-only preamble directive is non-semantic.
    full_tex = full_tex.replace(r'\DisableLigatures{encoding = *, family = *}', '')
    return _original_tex_renderer(full_tex, compiler, message)
_tex_writing.full_tex_to_svg = _group_a_tex_renderer


# Execute in this group's namespace so its data paths and adapters stay local.
_dependencies = Path(__file__).parent / 'group_dependencies.py'
exec(compile(_dependencies.read_text(), str(_dependencies), 'exec'), globals())

# Upstream: upstream/_2024/transformers/chm.py:251-255
class WriteTransformer(InteractiveScene):
    def construct(self):
        text = Text("Transformer", font_size=120)
        self.play(Write(text))
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:258-269
class LabelVector(InteractiveScene):
    def construct(self):
        brace = Brace(Line(UP, DOWN).set_height(4), RIGHT)
        name = Text("Vector", font_size=72)
        name.next_to(brace, RIGHT)
        name.set_backstroke(BLACK, 5)

        self.play(
            GrowFromCenter(brace),
            Write(name),
        )
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:272-300
class AdjustingTheMachine(InteractiveScene):
    def construct(self):
        # Add a machine and repeatedly tweak it
        frame = self.frame
        self.set_floor_plane("xz")
        frame.reorient(-28, -17, 0, ORIGIN, 8.91)
        self.camera.light_source.move_to([-10, 10, 10])

        machine = MachineWithDials(n_rows=10, n_cols=12)
        machine.set_height(6)
        blocks = VCube().replicate(10)
        blocks.set_shape(machine.get_width(), machine.get_height(), 1.0)
        blocks.deactivate_depth_test()
        cam_loc = self.frame.get_implied_camera_location() 
        for block in blocks:
            block.sort(lambda p: -get_norm(p - cam_loc))
        blocks.set_fill(GREY_D, 1)
        blocks.set_shading(0.2, 0.5, 0.25)
        blocks.arrange(OUT, buff=0.5)
        blocks.move_to(machine, OUT)

        self.add(blocks)
        self.add(machine)

        frame.clear_updaters()
        frame.add_updater(lambda f: f.set_theta(-30 * DEGREES * math.cos(0.1 * self.time)))
        self.add(frame)
        for x in range(6):
            self.play(machine.random_change_animation(lag_factor=0.1))

# Upstream: upstream/_2024/transformers/chm.py:445-452
class DownByTheRiverHeader(InteractiveScene):
    def construct(self):
        words = Text("Down by the river bank ...")
        rect = SurroundingRectangle(words["bank"])
        rect.set_fill(BLUE, 0.5)
        rect.set_stroke(BLUE, 3)
        brace = Brace(rect, DOWN, buff=SMALL_BUFF)
        self.add(rect, words, brace)
        self.wait(1)

# Upstream: upstream/_2024/transformers/chm.py:486-546
class FourStepsWithParameters(InteractiveScene):
    def construct(self):
        # Add rectangles and titles
        self.add(FullScreenRectangle(fill_color=GREY_E))
        rects = Square().replicate(4)
        rects.arrange(RIGHT, buff=0.25 * rects[0].get_width())
        rects.set_width(FRAME_WIDTH - 1.0)
        rects.center().to_edge(UP, buff=0.5)
        rects.set_fill(BLACK, 1)
        rects.set_stroke(WHITE, 2)
        names = VGroup(*map(TexText, [
            R"Text snippets\\$\downarrow$\\Vectors",
            R"Attention",
            R"Feedforward",
            R"Final prediction",
        ]))
        for name, rect in zip(names, rects):
            name.scale(0.8)
            name.next_to(rect, DOWN)

        self.add(rects)
        self.play(LaggedStartMap(FadeIn, names, shift=0.25 * DOWN, lag_ratio=0.25))
        self.wait()

        # Show many dials
        machines = VGroup(
            MachineWithDials(
                width=rect.get_width(),
                height=3.0,
                n_rows=9,
                n_cols=6,
            )
            for rect in rects
        )
        for machine, rect in zip(machines, rects):
            machine.next_to(rect, DOWN, buff=0)
            machine[0].set_opacity(0)
            machine.scale(rect.get_width() / machine.dials.get_width(), about_edge=UP)
            machine.dials.shift(0.25 * UP)
            for dial in machine.dials:
                dial.set_value(0)

        self.play(
            LaggedStart((
                LaggedStart(
                    (GrowFromPoint(dial, machine.get_top())
                    for dial in machine.dials),
                    lag_ratio=0.025,
                )
                for machine in machines
            ), lag_ratio=0.25),
            LaggedStartMap(FadeOut, names)
        )
        for _ in range(2):
            self.play(
                LaggedStart(
                    (machine.random_change_animation()
                    for machine in machines),
                    lag_ratio=0.2,
                )
            )

# Upstream: upstream/_2024/transformers/chm.py:549-619
class ChatbotFeedback(InteractiveScene):
    random_seed = 404

    def construct(self):
        # Test
        self.frame.set_height(10).move_to(DOWN)
        user_prompt = "User: How and when was the internet invented?"

        prompt_mob = Text(user_prompt)
        prompt_mob.to_edge(UP)
        prompt_mob["User:"].set_color(BLUE)

        self.answer_mob = Text("AI Assistant:")
        self.answer_mob.next_to(prompt_mob, DOWN, buff=1.0, aligned_edge=LEFT)
        self.answer_mob.set_color(YELLOW)
        self.og_answer_mob = self.answer_mob

        self.add(prompt_mob, self.answer_mob)

        # Show multiple answer
        for n in range(8):
            self.give_answer(prompt_mob)
            mark = self.judge_answer()
            self.add(self.og_answer_mob)
            self.play(FadeOut(self.answer_mob), FadeOut(mark))
            self.answer_mob = self.og_answer_mob

    def display_answer(self, text):
        new_answer_mob = get_paragraph(text.replace("\n", " ").split(" "))
        new_answer_mob[:len(self.og_answer_mob)].match_style(self.og_answer_mob)
        new_answer_mob.move_to(self.og_answer_mob, UL)
        self.remove(self.answer_mob)
        self.answer_mob = new_answer_mob
        self.add(self.answer_mob)

    def give_answer(self, prompt_mob, max_responses=100):
        answer = self.og_answer_mob.get_text()
        user_prompt = prompt_mob.get_text()
        for n in range(max_responses):
            answer, stop = self.add_to_answer(user_prompt, answer)
            if stop:
                break
            self.display_answer(answer)
            self.wait(2 / 30)

    def judge_answer(self):
        mark = random.choice([
            Text("✓", font_size=72).set_color(GREEN),
            Text("✗", font_size=72).set_color(RED),
        ])
        mark.scale(5)
        mark.next_to(self.answer_mob, RIGHT, aligned_edge=UP)
        rect = SurroundingRectangle(self.answer_mob)
        rect.match_color(mark)
        self.play(FadeIn(mark, scale=2), FadeIn(rect, scale=1.05))
        self.wait()
        return VGroup(mark, rect)

    def add_to_answer(self, user_prompt: str, answer: str):
        try:
            tokens, probs = gpt3_predict_next_token("\n\n".join([user_prompt, answer]))
            token = random.choices(tokens, np.array(probs) / sum(probs))[0]
        except Exception:
            fallback = " The internet developed through several research networks and standards."
            if fallback.strip() in answer:
                return answer, True
            return answer + fallback, False

        stop = False
        if token == '<|endoftext|>':
            stop = True
        else:
            answer += token
        return answer, stop

# Upstream: upstream/_2024/transformers/chm.py:622-647
class ContrastWithEarlierFrame(InteractiveScene):
    def construct(self):
        # Test
        vline = Line(UP, DOWN)
        vline.set_height(FRAME_HEIGHT)
        self.add(vline)

        titles = VGroup(
            VGroup(
                Text("Most earlier models"),
                # Vector(0.75 * DOWN, thickness=4),
                # Text("One word at a time")
            ),
            VGroup(
                Text("Transformers"),
                # Vector(0.75 * DOWN, thickness=4),
                # Text("All words in parallel")
            ),
        )
        for title, vect in zip(titles, [LEFT, RIGHT]):
            title.arrange(DOWN, buff=0.2)
            title.scale(1.5)
            title.move_to(FRAME_WIDTH * vect / 4)
            title.to_edge(UP)

        self.add(titles)
        self.wait(1)

# Upstream: upstream/_2024/transformers/chm.py:650-682
class SequentialProcessing(InteractiveScene):
    def construct(self):
        # Add text
        text = Text("Down by the river bank, where I used to go fishing ...")
        text.move_to(1.0 * DOWN)
        words = break_into_words(text)
        rects = get_piece_rectangles(words)
        blocks = VGroup(VGroup(rect, word) for rect, word in zip(rects, words))
        blocks.save_state()
        self.add(blocks)

        # Vector wandering over
        vect = NumericEmbedding()
        vect.set_width(1.0)
        vect.next_to(rects[0], UP)

        for n in range(len(blocks) - 1):
            blocks.target = blocks.saved_state.copy()
            blocks.target[:n].fade(0.75)
            blocks.target[n + 1:].fade(0.75)
            self.play(
                vect.animate.next_to(blocks[n], UP),
                MoveToTarget(blocks)
            )
            self.play(
                LaggedStart(
                    (ContextAnimation(elem, blocks[n][1], lag_ratio=0.01)
                    for elem in vect.get_entries()),
                    lag_ratio=0.01,
                ),
                RandomizeMatrixEntries(vect),
                run_time=2
            )

# Upstream: upstream/_2024/transformers/chm.py:1220-1236
class ParameterWeight(InteractiveScene):
    def construct(self):
        # Test
        text = Text("Parameter / Weight", font_size=72)
        text.to_edge(UP)
        text.set_color(YELLOW)
        param = text["Parameter"][0]
        param.save_state()
        param.set_x(0)

        self.play(Write(param))
        self.wait()
        self.play(LaggedStart(
            Restore(param),
            FadeIn(text["/ Weight"]),
        ))
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1239-1254
class LargeInLargeLanguageModel(InteractiveScene):
    def construct(self):
        # Test
        text = Text("Large Language Model", font_size=72)
        text.to_edge(UP)
        large = text["Large"][0]
        large.save_state()
        large.set_x(0)

        self.add(large)
        self.play(FlashUnder(large), large.animate.set_color(YELLOW))
        self.play(
            Restore(large, path_arc=-30 * DEGREES),
            Write(text[len(large):], time_span=(0.5, 1.5))
        )
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1257-1270
class ThousandsOfWords(InteractiveScene):
    def construct(self):
        # Find passage
        file = DATA_DIR / "tale_of_two_cities.txt"
        novel = file.read_text()
        start_index = novel.index("It was the best of times")
        end_index = novel.index("There were a king with a large jaw")

        # Add text
        passage = novel[start_index:start_index + 5000].replace("\n", " ")
        text = get_paragraph(passage.split(" "), line_len=150)
        text.set_width(14)
        text.to_edge(UP)
        self.add(text)
        self.wait(1)

# Upstream: upstream/_2024/transformers/chm.py:1414-1430
class WriteRLHF(InteractiveScene):
    def construct(self):
        text = Text("Step 2: RLHF")
        full_text = Text("Reinforcement Learning\nwith Human Feedback")
        full_text.next_to(text, UP, LARGE_BUFF)
        full_text.align_to(text, RIGHT).shift(RIGHT)
        initials = VGroup(full_text[letter[0]][0][0] for letter in "RLHF")
        full_text.remove(*initials)

        self.add(text)
        self.wait()
        self.play(
            TransformFromCopy(text["RLHF"][0], initials, lag_ratio=0.25),
            Write(full_text, time_span=(1.5, 3)),
            run_time=3
        )
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1482-1533
class SerialProcessing(InteractiveScene):
    phrase = "It was the best of times it was the worst of times"
    phrase_center = 2 * UP

    def construct(self):
        # Set up words
        words = self.get_words()
        rects = get_piece_rectangles(words)

        self.add(rects)
        self.add(words)

        # Animate in the vectors
        vectors = VGroup(
            self.get_abstract_vector().next_to(word, DOWN, LARGE_BUFF)
            for word in words
        )
        last_vect = VGroup(VectorizedPoint(rects[0].get_bottom()))

        for word, vect in zip(words, vectors):
            self.play(
                FadeIn(vect, run_time=2),
                LaggedStart(
                    (ContextAnimation(
                        square, VGroup(*word, *last_vect),
                        direction=DOWN,
                        lag_ratio=0.01,
                        path_arc=30 * DEGREES
                    )
                    for square in vect),
                    lag_ratio=0.05,
                    run_time=2
                ),
                last_vect.animate.set_opacity(0.2)
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

# Upstream: upstream/_2024/transformers/chm.py:1536-1574
class ParallelProcessing(SerialProcessing):
    def construct(self):
        # Set up words
        words = self.get_words()
        rects = get_piece_rectangles(words)

        self.add(rects)
        self.add(words)

        # Animate in the vectors
        vectors = VGroup(
            self.get_abstract_vector().next_to(word, DOWN, buff=1.5)
            for word in words
        )

        lines = VGroup(
            Line(
                rect.get_bottom(), vect.get_top(),
                buff=0.05,
                stroke_color=WHITE,
                stroke_width=2 * random.random()**3
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
            LaggedStartMap(Restore, vectors, lag_ratio=0)
        )
        self.play(lines.animate.set_stroke(opacity=0.25))
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1577-1807
class ManyComputationsPerUnitTimeV2(InteractiveScene):
    def construct(self):
        # Add computations
        box = Rectangle(5, 5)
        label = Text("1 Billion computations per Second")
        label.next_to(box, UP)
        self.add(box)
        self.add(label)

        comps = self.get_computations(box)
        self.add(comps)
        self.wait(3)

        # Place box into minute interval
        width = FRAME_WIDTH - 1
        number_lines = VGroup(
            minute_line := NumberLine((0, 60, 1), width=width, big_tick_spacing=10),
            hour_line := NumberLine((0, 60, 1), width=width, big_tick_spacing=10),
            day_line := NumberLine((0, 24, 1), width=width, big_tick_spacing=6),
            month_line := NumberLine((0, 31, 1), width=width),
            year_line := NumberLine((0, 12, 1), width=width),
            y100_line := NumberLine((0, 100, 1), width=width),
            y10k_line := NumberLine((0, 100, 1), width=width),
            y1M_line := NumberLine((0, 100, 1), width=width),
            y100M_line := NumberLine((0, 100, 1), width=width),
        )
        number_lines.move_to(DOWN)

        first_ticks = minute_line.ticks[:2]
        sec_brace = Brace(first_ticks, DOWN, buff=0, tex_string=R"\underbrace{\qquad\qquad}")
        sec_label = Text("Second", font_size=30).next_to(sec_brace, DOWN, SMALL_BUFF)

        self.play(
            ShowCreation(minute_line, lag_ratio=0.01),
            box.animate.match_width(first_ticks).move_to(first_ticks.get_center(), DOWN).set_stroke(width=1),
            TransformFromCopy(label["Second"][0], sec_label),
            GrowFromCenter(sec_brace),
            run_time=2
        )

        # Add other boxes
        minute_label = self.get_timeline_full_label(number_lines[1], "Minute")
        new_boxes = VGroup(
            box.copy().move_to(tick.get_center(), DL)
            for tick in minute_line.ticks[1:-1]
        )
        for new_box in new_boxes:
            new_box.save_state()
            new_box.move_to(box)
        computations = VGroup(
            self.get_computations(new_box, n_iterations=1)
            for new_box in new_boxes
        )
        # computations = VGroup()  # If needed

        self.add(computations)
        self.play(
            FadeIn(minute_label, DOWN),
            LaggedStartMap(Restore, new_boxes, lag_ratio=0.1),
            run_time=2
        )
        self.wait(2)

        # Add labels
        minute_line.add(minute_label)
        names = ["Hour", "Day", "Month", "Year", "100 Years", "10,000 Years", "1,000,000 Years", "100,000,000 Years"]
        for line, name in zip(number_lines[1:], names):
            line.label = self.get_timeline_full_label(line, name)
            line.add(line.label)

        # Arrange all lines
        number_lines[1:].arrange(DOWN, buff=2.0)
        number_lines[1:].next_to(minute_line, DOWN, buff=2.0)

        scale_lines = VGroup()
        for nl1, nl2 in zip(number_lines, number_lines[1:]):
            n = len(nl2.ticks) // 2
            mini_line = Line(nl2.ticks[n - 1].get_center(), nl2.ticks[n].get_center())
            pair = VGroup(
                DashedLine(nl1.get_start(), mini_line.get_start()),
                DashedLine(nl1.get_end(), mini_line.get_end()),
            )
            pair.set_stroke(WHITE, 2)
            nl1.target = nl1.copy()
            nl1.target.replace(mini_line, dim_to_match=0)
            nl1.target.shift(mini_line.pfp(0.5) - nl1.target.pfp(0.5))
            scale_lines.add(pair)

        # Start panning down
        lag_ratio = 1.5
        self.play(
            LaggedStart(
                *(AnimationGroup(*(ShowCreation(sl) for sl in pair)) for pair in scale_lines),
                lag_ratio=lag_ratio,
            ),
            LaggedStart(
                *(FadeIn(nl) for nl in number_lines[1:]),
                lag_ratio=lag_ratio,
            ),
            LaggedStart(
                *(TransformFromCopy(nl, nl.target) for nl in number_lines[:-1]),
                lag_ratio=lag_ratio,
            ),
            self.frame.animate.set_y(number_lines[-1].get_y() + 2).set_width(18).set_anim_args(
                rate_func=lambda t: interpolate(smooth(t), linear(t), there_and_back_with_pause(t, pause_ratio=0.8))
            ),
            run_time=30
        )
        self.play(self.frame.animate.reorient(0, 0, 0, (-0.03, -11.55, 0.0), 31.76), run_time=4)
        self.wait(4)

    def fade_in_bigger_interval(self, new_interval, prev_interval, fader, scale_factor, added_anims=[]):
        pivot = prev_interval.n2p(0)
        new_interval.save_state()
        new_interval.scale(scale_factor, about_point=pivot)
        new_interval[:-1].set_opacity(0)
        new_interval[-1].set_fill(BLACK)

        self.play(
            Restore(new_interval),
            prev_interval.animate.scale(1.0 / scale_factor, about_point=pivot).set_fill(border_width=0),
            fader.animate.scale(1.0 / scale_factor, about_point=pivot).set_opacity(0),
            *added_anims,
            run_time=4,
            rate_func=rush_from
        )
        self.remove(fader)

    def get_timeline_full_label(self, timeline, name):
        brace = Brace(Line().set_width(7), UP, buff=MED_SMALL_BUFF)
        brace.set_fill(border_width=5)
        brace.match_width(timeline)
        brace.next_to(timeline, UP, buff=MED_SMALL_BUFF)
        label = Text(name, font_size=72)
        label.next_to(brace, UP, MED_SMALL_BUFF)

        label.next_to(timeline, DOWN)
        return label

        return VGroup(brace, label)

    def get_computations(self, box, n_lines=10, n_iterations=3, n_digits=4, cycle_time=0.5):
        # Try adding lines
        lines = VGroup()
        for iteration in range(n_iterations):
            cluster = VGroup()
            for n in range(n_lines):
                x = random.uniform(0, 10**(n_digits))
                y = random.uniform(0, 10**(n_digits))
                if random.choice([True, False]):
                    comb = x * y
                    sym = Tex(R"\times")
                else:
                    comb = x + y
                    sym = Tex(R"+")
                line = VGroup(
                    DecimalNumber(x, num_decimal_places=3), sym,
                    DecimalNumber(y, num_decimal_places=3), Tex("="),
                    DecimalNumber(comb, num_decimal_places=3)
                )
                line.arrange(RIGHT, buff=SMALL_BUFF)
                lines.add(line)
                cluster.add(line)
            cluster.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
            cluster.set_max_height(0.9 * box.get_height())
            cluster.set_max_width(0.9 * box.get_width())
            cluster.move_to(box)

        # Add updater
        def update_lines(lines):
            sigma = 0.12
            alpha = (self.time / (cycle_time * n_iterations)) % 1
            step = 1.0 / len(lines)
            for n, line in enumerate(lines):
                x = min((
                    abs(a - n * step)
                    for a in (alpha - 1, alpha, alpha + 1)
                ))
                y = np.exp(-x**2 / sigma**2)
                line.set_fill(opacity=y)

            lines.set_height(0.9 * box.get_height())
            lines.move_to(box)

        lines.clear_updaters()
        lines.add_updater(update_lines)

        return lines

    def old(self):
        # Repeatedly scale down
        to_fade = VGroup(sec_brace, sec_label, box, comps, new_boxes, computations)
        scale_factors = [60, 24, 365, 1000]
        for new_int, prev_int, scale_factor in zip(number_lines[1:], number_lines[0:], scale_factors):
            self.fade_in_bigger_interval(
                new_int, prev_int, to_fade, scale_factor,
                added_anims=[label.animate.set_opacity(0)],
            )
            self.wait(2)
            to_fade = prev_int

        # Multiply last line by 100
        self.fade_in_bigger_interval(
            y1M_line, millenium_line, year_line, 1000,
            added_anims=[self.frame.animate.reorient(0, 0, 0, (-3.51, -5.18, 0.0), 12.93)],
        )

        lines = Line(LEFT, RIGHT).replicate(100)
        lines.match_width(y1M_line)
        lines.arrange_to_fit_height(10)
        lines.sort(lambda p: -p[1])
        lines.set_stroke(WHITE, 1)
        lines.move_to(y1M_line[0].get_center(), UP)

        side_brace, label100M = self.get_timeline_full_label(y1M_line, "100,000,000 Years")
        side_brace.rotate(PI / 2)
        side_brace.match_height(lines)
        side_brace.next_to(lines, LEFT)
        label100M.next_to(side_brace, LEFT)

        self.play(
            LaggedStart(
                (TransformFromCopy(lines[0].copy().set_opacity(0), line)
                for line in lines),
                lag_ratio=0.03,
                run_time=2
            ),
            FadeIn(side_brace, scale=10, shift=2 * DOWN, time_span=(1, 2)),
            FadeIn(label100M, time_span=(1, 2)),
        )
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1810-1827
class VectorLabel(InteractiveScene):
    def construct(self):
        # Test
        brace = Brace(Line(4 * UP, ORIGIN), LEFT)
        brace.center()
        brace.set_stroke(WHITE, 3)
        text = Text("Vector", font_size=90)
        text.next_to(brace, LEFT, MED_SMALL_BUFF)
        text.shift(SMALL_BUFF * UP)

        self.play(
            GrowFromCenter(brace),
            Write(text)
        )
        self.play(
            FlashUnder(text, color=YELLOW)
        )
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1830-1852
class ParameterToVectorAnnotation(InteractiveScene):
    def construct(self):
        # Test
        dials = VGroup(Dial(value_range=(-10, 10, 1)) for _ in range(10))
        dials.arrange(DOWN)
        dials.set_height(5)

        values = [1, 4.3, 2, 0.9, -1.5, 2.9, -1.2, 7.8, 0, -2.3]
        arrows = VGroup(
            Vector(0.5 * RIGHT, thickness=2).next_to(dial, RIGHT, buff=SMALL_BUFF)
            for dial in dials
        )

        self.play(
            Write(dials, lag_ratio=0.01),
            LaggedStartMap(GrowArrow, arrows),
        )
        self.play(LaggedStart(
            (dial.animate_set_value(value)
            for dial, value in zip(dials, values)),
            lag_ratio=0.05,
        ))
        self.wait()

# Upstream: upstream/_2024/transformers/chm.py:1921-1935
class ExamplePhraseHeader(InteractiveScene):
    def construct(self):
        # Test
        phrase = Text("The Computer History Museum\nis located in ?????")
        phrase.to_edge(UP)
        rect = SurroundingRectangle(phrase).set_stroke(WHITE, 2)

        q_marks = phrase["?????"][0]
        q_marks[::4].set_fill(opacity=0)
        q_rect = SurroundingRectangle(q_marks)
        q_rect.set_fill(YELLOW, 0.25)
        q_rect.set_stroke(YELLOW, 2)

        self.add(q_rect)
        self.add(phrase)
        self.wait(1)

# Upstream: upstream/_2024/transformers/chm.py:2107-2153
class ShowPreviousVideos(InteractiveScene):
    def construct(self):
        # Backdrop
        background = FullScreenRectangle()
        self.add(background)

        line = Line(UP, DOWN).set_height(FRAME_HEIGHT)
        line.set_stroke(WHITE, 2)

        series_name = Text("Deep Learning Series", font_size=68)
        series_name.to_edge(UP, buff=0.35)
        self.add(series_name)

        # Show thumbnails
        thumbnails = Group(
            Group(
                Rectangle(16, 9).set_height(1).set_stroke(WHITE, 2),
                ImageMobject(ROOT / "assets" / "placeholders-a" / f"{slug}.jpg", height=1)
            )
            for slug in [
                "aircAruvnKk",
                "IHZwWFHWa-w",
                "Ilg3gGewQ5U",
                "tIeHLnjs5U8",
                "wjZofJX0v4M",
                "eMlx5fFNoYc",
                "9-Jl0dxWQs8",
            ]
        )

        thumbnails.arrange_in_grid(n_cols=4, buff=0.2)
        thumbnails.set_width(FRAME_WIDTH - 1)
        thumbnails.next_to(series_name, DOWN, buff=1.0)
        thumbnails[-3:].set_x(0)

        self.play(LaggedStartMap(FadeIn, thumbnails, shift=0.3 * UP, lag_ratio=0.35, run_time=4))
        self.wait()

        # Rearrange
        left_x = -FRAME_WIDTH / 4
        self.play(
            series_name.animate.set_x(left_x),
            thumbnails.animate.arrange_in_grid(n_cols=2, buff=0.25).set_height(6).set_x(left_x).to_edge(DOWN),
            ShowCreation(line, time_span=(1, 2)),
            run_time=2,
        )
        self.wait()


# Fixed illustrative prediction data: never calls a model or remote API.
def gpt3_predict_next_token(text):
    sample = " The internet developed through several research networks and standards."
    if sample.strip() in text:
        return ["<|endoftext|>"], [1.0]
    return [sample], [1.0]
