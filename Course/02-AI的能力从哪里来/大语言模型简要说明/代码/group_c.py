"""Compatibility adaptation of eight original chm.py scenes (group C)."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import numpy as np
from numpy.typing import NDArray as NumpyArray

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import tex_support  # noqa: E402,F401 - installs the Tectonic TeX renderer

sys.path.insert(0, str(ROOT / "upstream"))

from manim_imports_ext import *  # noqa: F403,E402
from manimlib import Group  # noqa: E402
from custom.characters.pi_creature import PiCreature  # noqa: E402

if TYPE_CHECKING:
    from manimlib.typing import Vect3 as ManimVect3


PLACEHOLDERS = ROOT / "assets" / "placeholders-c"


def direction(value: object) -> NumpyArray[Any]:
    """Normalize Manim's fixed-shape vector alias for NumPy-based APIs."""
    return np.asarray(value, dtype=np.float64)


def point(value: object) -> ManimVect3:
    """Return the fixed three-component vector type used by Mobject geometry."""
    return cast("ManimVect3", np.asarray(value, dtype=np.float64))


class BotSVG(SVGMobject):  # noqa: F405
    eyes: VGroup[Dot]  # noqa: F405


def _placeholder_pi_path(self, mode):
    path = PLACEHOLDERS / "pi" / f"{mode}.svg"
    return str(path if path.exists() else PLACEHOLDERS / "pi" / "plain.svg")


PiCreature.get_svg_file_path = _placeholder_pi_path


def add_placeholder_mark(scene, text):
    mark = Text(f"PLACEHOLDER: {text}", font_size=18).set_color(GREY_B)  # noqa: F405
    mark.to_corner(DR, buff=0.12).fix_in_frame()  # noqa: F405
    scene.add(mark)


class MarkedTeacherStudentsScene(TeacherStudentsScene):  # noqa: F405
    def setup(self):
        super().setup()
        add_placeholder_mark(self, "PiCreature mode SVGs")


# Upstream: upstream/_2024/transformers/chm.py:10-29
class HoldUpThumbnail(MarkedTeacherStudentsScene):
    def construct(self):
        im = ImageMobject(str(PLACEHOLDERS / "images" / "Chapter5_TN3.png"))  # noqa: F405
        im_group = Group(
            SurroundingRectangle(im, buff=0).set_stroke(WHITE, 3),  # noqa: F405
            im,
        )
        im_group.set_height(3)
        im_group.move_to(self.hold_up_spot, DOWN)  # noqa: F405
        morty = self.teacher
        self.play(
            FadeIn(im_group, direction(UP)),  # noqa: F405
            morty.change("raise_right_hand", look_at=im_group),
            self.change_students("tease", "happy", "tease", look_at=im_group),
        )
        self.wait(4)


# Upstream: upstream/_2024/transformers/chm.py:32-42
class IsThisUsefulToShare(MarkedTeacherStudentsScene):
    def construct(self):
        morty = self.teacher
        self.play(
            morty.says("Do you find\nthis useful?"),
            self.change_students("pondering", "hesitant", "well", look_at=self.screen),
        )
        self.wait(3)
        self.play(self.change_students("thinking", "pondering", "tease"))
        self.wait(3)


# Upstream: upstream/_2024/transformers/chm.py:45-58
class AskAboutAttention(MarkedTeacherStudentsScene):
    def construct(self):
        stds = self.students
        morty = self.teacher
        self.play(
            morty.change("tease"),
            stds[2].says("Can you explain what\nAttention does?", mode="raise_left_hand", bubble_direction=LEFT),  # noqa: F405
            stds[1].change("pondering", self.screen),
            stds[0].change("pondering", self.screen),
        )
        self.wait(4)


# Upstream: upstream/_2024/transformers/chm.py:303-354
class FirthQuote(InteractiveScene):  # noqa: F405
    def construct(self):
        quote = TexText(R"``You shall know a word\\by the company it keeps!''", font_size=60)  # noqa: F405
        image = ImageMobject(str(PLACEHOLDERS / "images" / "JohnRFirth.png"))  # noqa: F405
        image.set_height(6.5)
        image.to_corner(UL, buff=0.5)  # noqa: F405
        name = Text("John R. Firth")  # noqa: F405
        name.next_to(image, DOWN)  # noqa: F405
        quote.move_to(midpoint(image.get_right(), RIGHT_SIDE))  # noqa: F405
        quote.to_edge(UP)  # noqa: F405
        self.play(FadeIn(image, 0.25 * direction(UP)), FadeIn(name, lag_ratio=0.1))  # noqa: F405
        self.play(Write(quote))  # noqa: F405
        self.wait()
        phrases = VGroup(  # noqa: F405
            Text("Down by the river bank"),  # noqa: F405
            Text("Deposit a check at the bank"),  # noqa: F405
        )
        bank = Text("bank", font_size=90)  # noqa: F405
        bank.set_color(TEAL)  # noqa: F405
        bank.match_x(quote).match_y(image)
        for phrase in phrases:
            phrase["bank"].set_color(TEAL)  # noqa: F405
        phrases.arrange(DOWN, buff=1.0, aligned_edge=LEFT)  # noqa: F405
        phrases.next_to(quote, DOWN, buff=2.5)  # noqa: F405
        phrases[1].set_opacity(0.15)
        banks = VGroup(phrase["bank"][0] for phrase in phrases)  # noqa: F405
        self.play(FadeIn(bank, scale=2, lag_ratio=0.25), quote.animate.scale(0.7, about_edge=UP).set_opacity(0.75))  # noqa: F405
        self.wait()
        self.remove(bank)
        self.play(
            FadeIn(phrases[0][:len("downbytheriver")], lag_ratio=0.1),  # noqa: F405
            FadeIn(phrases[1][:len("depositacheckatthe")], lag_ratio=0.1),  # noqa: F405
            *(TransformFromCopy(bank, bank2) for bank2 in banks),  # noqa: F405
        )
        self.wait()
        self.play(phrases[0].animate.set_opacity(0.5), phrases[1].animate.set_opacity(1))
        self.wait()
        self.play(LaggedStart(  # noqa: F405
            FadeOut(image, LEFT, scale=0.5),  # noqa: F405
            FadeOut(name, LEFT, scale=0.5),  # noqa: F405
            FadeOut(quote, LEFT, scale=0.5),  # noqa: F405
            phrases.animate.set_opacity(1).arrange(DOWN, buff=3.5, aligned_edge=LEFT).move_to(point(0.5 * direction(UP))),  # noqa: F405
        ))
        self.wait()
        word = Text("bank", font_size=72)  # noqa: F405
        word.set_color(TEAL)  # noqa: F405
        self.clear()
        self.add(word)
        self.wait()
        self.remove(word)
        self.play(
            *(FadeIn(cast(Text, phrase)[cast(Text, phrase).get_text().replace("bank", "")]) for phrase in phrases),  # noqa: F405
            *(TransformFromCopy(word, phrase["bank"][0]) for phrase in phrases),  # noqa: F405
        )
        self.add(phrases)
        query_rects = VGroup(*(SurroundingRectangle(bank) for bank in banks))  # noqa: F405
        query_rects.set_stroke(TEAL, 2).set_fill(TEAL, 0.25)  # noqa: F405
        key_rects = VGroup(  # noqa: F405
            SurroundingRectangle(phrases[0]["river"]),  # noqa: F405
            SurroundingRectangle(phrases[1]["Deposit"]),  # noqa: F405
            SurroundingRectangle(phrases[1]["check"]),  # noqa: F405
        )
        key_rects.set_stroke(BLUE, 2).set_fill(BLUE, 0.5)  # noqa: F405
        key_rects[2].match_height(key_rects[1], about_edge=UP, stretch=True)  # noqa: F405
        arrows = VGroup(  # noqa: F405
            Arrow(key_rects[0].get_top(), banks[0].get_top(), path_arc=-180 * DEGREES, buff=0.1),  # noqa: F405
            Arrow(key_rects[1].get_top(), banks[1].get_top(), path_arc=-90 * DEGREES),  # noqa: F405
            Arrow(key_rects[2].get_top(), banks[1].get_top(), path_arc=-90 * DEGREES),  # noqa: F405
        )
        arrows.set_color(BLUE)  # noqa: F405
        key_rects.save_state()
        key_rects[0].become(query_rects[0])
        key_rects[1].become(query_rects[1])
        key_rects[2].become(query_rects[1])
        key_rects.set_opacity(0)
        self.add(query_rects, phrases)
        self.play(FadeIn(query_rects, lag_ratio=0.25))  # noqa: F405
        self.wait()
        self.add(key_rects, phrases)
        self.play(Restore(key_rects, lag_ratio=0.1, path_arc=PI / 4, run_time=2))  # noqa: F405
        self.play(LaggedStartMap(lambda mob: Write(cast(VMobject, mob)), arrows, stroke_width=5, run_time=3))  # noqa: F405
        self.wait()
        images = Group(  # noqa: F405
            ImageMobject(str(PLACEHOLDERS / "images" / "RiverBank.png")),  # noqa: F405
            ImageMobject(str(PLACEHOLDERS / "images" / "FederalReserve.png")),  # noqa: F405
        )
        for context_image, bank_word in zip(images, banks):
            context_image.set_height(2.0)
            context_image.next_to(bank_word, DOWN, MED_SMALL_BUFF, aligned_edge=LEFT)  # noqa: F405
        self.play(LaggedStart(  # noqa: F405
            (FadeTransform(Group(bank_word).copy(), context_image) for bank_word, context_image in zip(banks, images)),  # noqa: F405
            lag_ratio=0.5,
            group_type=Group,  # noqa: F405
        ))
        self.wait(2)


# Upstream: upstream/_2024/transformers/chm.py:1350-1407
class BadChatBot(InteractiveScene):  # noqa: F405
    def construct(self):
        add_placeholder_mark(self, "Bot.svg")
        bot = self.get_bot()
        bot.set_height(3)
        lines = Line(LEFT, RIGHT).get_grid(4, 1, buff=0.25)  # noqa: F405
        lines.set_stroke(WHITE, 1)  # noqa: F405
        lines[-1].stretch(0.5, 0, about_edge=LEFT)  # noqa: F405
        lines.set_width(3)
        bubble = SpeechBubble(lines, buff=MED_LARGE_BUFF)  # noqa: F405
        bubble.set_stroke(width=5)
        bubble.pin_to(bot).shift(DOWN)  # noqa: F405
        self.add(bot)
        self.play(Write(bubble, run_time=3))  # noqa: F405
        self.blink(bot)
        self.wait()
        self.play(LaggedStart((Transform(line, self.get_scribble(line)) for line in lines), lag_ratio=0.1, run_time=2))  # noqa: F405
        for _ in range(2):
            self.blink(bot)
            self.wait(2)

    def get_scribble(self, line):
        freqs = np.random.random(5)  # noqa: F405
        graph = FunctionGraph(lambda x: 0.05 * sum(math.sin(freq * TAU * x) for freq in freqs), x_range=(0, 5, 0.1))  # noqa: F405
        graph.put_start_and_end_on(*line.get_start_and_end())
        graph.match_style(line)
        graph.set_stroke(color=RED)  # noqa: F405
        return graph

    def get_bot(self):
        bot = BotSVG(str(PLACEHOLDERS / "svg" / "Bot.svg"))
        body = cast(VMobject, bot[0])  # noqa: F405
        subpaths = body.get_subpaths()
        body.set_points([*subpaths[0], subpaths[0][-1], *subpaths[1]])
        eyes = VGroup(Dot().replace(VMobject().set_points(subpath)) for subpath in subpaths[2:])  # noqa: F405
        bot.eyes = eyes
        bot.add(eyes)
        bot.set_stroke(width=0)
        bot.set_height(4)
        bot.set_fill(GREY_B)  # noqa: F405
        bot.set_shading(0.5, 0.5, 1)
        return bot

    def blink(self, bot: BotSVG):
        self.play(bot.eyes.animate.stretch(0, 1).set_anim_args(rate_func=squish_rate_func(there_and_back)))  # noqa: F405


# Upstream: upstream/_2024/transformers/chm.py:1433-1451
class RLHFWorker(InteractiveScene):  # noqa: F405
    def construct(self):
        add_placeholder_mark(self, "comp_worker.svg")
        self.add(FullScreenRectangle().set_fill(GREY_E, 1))  # noqa: F405
        worker = SVGMobject(str(PLACEHOLDERS / "svg" / "comp_worker.svg"))  # noqa: F405
        worker.set_height(4)
        worker.move_to(point(4 * direction(LEFT)))  # noqa: F405
        worker.set_fill(GREY_C, 1)  # noqa: F405
        rect = Rectangle(7, 5)  # noqa: F405
        rect.to_edge(RIGHT)  # noqa: F405
        rect.set_stroke(WHITE, 2)  # noqa: F405
        rect.set_fill(BLACK, 1)  # noqa: F405
        self.add(worker)
        self.add(rect)
        # Compatibility: current ManimGL writes no frames for a purely static scene.
        self.wait()


# Upstream: upstream/_2024/transformers/chm.py:1855-1911
class ThreeWordsToOne(InteractiveScene):  # noqa: F405
    def construct(self):
        add_placeholder_mark(self, "CHM images and three icons")
        phrase = Text("Computer History Museum", font_size=61)  # noqa: F405
        words = VGroup(*(cast(VMobject, phrase[word][0]) for word in phrase.get_text().split(" ")))  # noqa: F405
        words.set_x(0).set_y(2.627)
        og_words = words.copy().shift(point(DOWN))  # noqa: F405
        words[0].shift(point(0.13 * direction(LEFT)))  # noqa: F405
        words[2].shift(point(0.4 * direction(RIGHT)))  # noqa: F405
        colors = ["#63DCF7", "#90C9FA", "#85D4FE"]
        for word, color in zip(words, colors):
            word.set_color(color)
        words.save_state()
        assert words.saved_state is not None
        saved_words = cast(VGroup[VMobject], words.saved_state)  # noqa: F405
        self.add(words)
        self.wait()
        rect = SurroundingRectangle(og_words)  # noqa: F405
        rect.set_color(RED)  # noqa: F405
        chm_image = ImageMobject(str(PLACEHOLDERS / "images" / "CHM_Exterior.png"))  # noqa: F405
        chm_image.match_width(rect)
        chm_image.next_to(rect, DOWN)  # noqa: F405
        self.play(Transform(words, og_words))  # noqa: F405
        self.play(ShowCreation(rect), FadeIn(chm_image, direction(DOWN)))  # noqa: F405
        self.wait()
        rects = VGroup(*(SurroundingRectangle(word).set_fill(color, 0.2).set_stroke(color, 2) for word, color in zip(saved_words, colors)))  # noqa: F405
        words.set_z_index(1)
        icons = VGroup(*(SVGMobject(str(PLACEHOLDERS / "svg" / name)) for name in ("GenericComputer.svg", "History.svg", "Museum.svg")))  # noqa: F405
        for word, icon in zip(saved_words, icons):
            icon.set_fill(word.get_color(), 1, border_width=1)
            icon.set_height(1)
            icon.next_to(word, DOWN)  # noqa: F405
        self.remove(chm_image)
        self.play(
            ReplacementTransform(VGroup(rect), rects),  # noqa: F405
            Restore(words),  # noqa: F405
            *(FadeTransform(chm_image.copy(), icon) for icon in icons),  # noqa: F405
        )
        self.wait()


# Upstream: upstream/_2024/transformers/chm.py:2156-2161
class EndScreen(PatreonEndScreen):  # noqa: F405
    title_text = "Where to dig deeper"
    thanks_words = """
        Special thanks to these Patreon supporters
    """

    def setup(self):
        super().setup()
        add_placeholder_mark(self, "PiCreature SVGs and patron names")

    def get_names(self):
        return ["Patron data unavailable", "Placeholder supporter list"]
