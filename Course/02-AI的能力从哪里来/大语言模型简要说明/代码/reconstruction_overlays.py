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
    DEGREES,
    DOWN,
    FadeIn,
    FadeTransform,
    Group,
    ImageMobject,
    InteractiveScene,
    LEFT,
    LaggedStart,
    LaggedStartMap,
    MED_SMALL_BUFF,
    ORIGIN,
    PI,
    Restore,
    SurroundingRectangle,
    TEAL,
    Text,
    TransformFromCopy,
    UP,
    VGroup,
    Write,
)  # noqa: E402


class BankContextOverlay(InteractiveScene):
    def construct(self):
        phrases = VGroup(
            Text("Down by the river bank"), Text("Deposit a check at the bank")
        )
        for phrase in phrases:
            phrase["bank"].set_color(TEAL)
        phrases.arrange(
            cast(Any, DOWN), buff=3.5, aligned_edge=cast(Any, LEFT)
        ).move_to(0.5 * cast(Any, UP))
        banks = VGroup(*(phrase["bank"][0] for phrase in phrases))
        # Recreate
        word = Text("bank", font_size=72)
        word.set_color(TEAL)
        self.clear()

        self.add(word)
        self.wait()
        self.remove(word)
        self.play(
            *(
                FadeIn(phrase[cast(Text, phrase).get_text().replace("bank", "")])
                for phrase in phrases
            ),
            *(TransformFromCopy(word, phrase["bank"][0]) for phrase in phrases),
        )
        self.add(phrases)

        # Show influence
        banks = VGroup(*(phrase["bank"][0] for phrase in phrases))
        query_rects = VGroup(SurroundingRectangle(bank) for bank in banks)
        query_rects.set_stroke(TEAL, 2)
        query_rects.set_fill(TEAL, 0.25)
        key_rects = VGroup(
            SurroundingRectangle(phrases[0]["river"]),
            SurroundingRectangle(phrases[1]["Deposit"]),
            SurroundingRectangle(phrases[1]["check"]),
        )
        key_rects.set_stroke(BLUE, 2)
        key_rects.set_fill(BLUE, 0.5)
        key_rects[2].match_height(key_rects[1], about_edge=cast(Any, UP), stretch=True)
        arrows = VGroup(
            Arrow(
                key_rects[0].get_top(),
                banks[0].get_top(),
                path_arc=-180 * DEGREES,
                buff=0.1,
            ),
            Arrow(key_rects[1].get_top(), banks[1].get_top(), path_arc=-90 * DEGREES),
            Arrow(key_rects[2].get_top(), banks[1].get_top(), path_arc=-90 * DEGREES),
        )
        arrows.set_color(BLUE)

        key_rects.save_state()
        key_rects[0].become(query_rects[0])
        key_rects[1].become(query_rects[1])
        key_rects[2].become(query_rects[1])
        key_rects.set_opacity(0)

        self.add(query_rects, phrases)
        self.play(FadeIn(query_rects, lag_ratio=0.25))
        self.wait()

        self.add(key_rects, phrases)
        self.play(Restore(key_rects, lag_ratio=0.1, path_arc=PI / 4, run_time=2))
        self.play(LaggedStartMap(cast(Any, Write), arrows, stroke_width=5, run_time=3))
        self.wait()

        # Show images
        images = Group(
            ImageMobject(str(ROOT / "assets/images/river-bank-original.png")),
            ImageMobject(
                str(ROOT / "assets/placeholders-c/images/FederalReserve.png")
            ),
        )
        for image, bank in zip(images, banks):
            image.set_height(2.0)
            image.next_to(
                bank, cast(Any, DOWN), MED_SMALL_BUFF, aligned_edge=cast(Any, LEFT)
            )

        self.play(
            LaggedStart(
                (
                    FadeTransform(Group(word).copy(), image)
                    for word, image in zip(banks, images)
                ),
                lag_ratio=0.5,
                group_type=Group,
            )
        )
        self.wait(2)


class OriginalOpeningTitle(InteractiveScene):
    def construct(self):
        title = Text("Large Language Models", font_size=54)
        subtitle = Text("for the curious beginner", font_size=36)
        Group(title, subtitle).arrange(cast(Any, DOWN), buff=0.2).move_to(
            cast(Any, ORIGIN)
        )
        self.add(title, subtitle)
        self.wait(1.3)
