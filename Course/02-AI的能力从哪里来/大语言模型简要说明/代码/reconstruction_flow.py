"""Original 3Blue1Brown Transformer-flow scenes adapted to the CHM film text.

The upstream snapshot stays read-only.  Optional ML packages are stubbed because
these two scenes only display fixed illustrative values and never load a model.
"""
# pyright: reportOperatorIssue=false, reportArgumentType=false

from __future__ import annotations


import sys
import types
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
import tex_support  # noqa: E402,F401

for _module_name in ("torch", "gensim", "tiktoken"):
    if _module_name not in sys.modules:
        sys.modules[_module_name] = types.ModuleType(_module_name)
setattr(sys.modules["torch"], "Tensor", type("Tensor", (), {}))

sys.path.insert(0, str(ROOT / "upstream"))

from manim_imports_ext import (  # noqa: E402
    Arrow,
    BLACK,
    BLUE,
    Brace,
    DEGREES,
    DOWN,
    FadeIn,
    FadeOut,
    Group,
    GrowArrow,
    GrowFromCenter,
    IN,
    ImageMobject,
    LEFT,
    LaggedStartMap,
    ORIGIN,
    OUT,
    PI,
    RIGHT,
    Restore,
    ShowCreation,
    ShowCreationThenFadeOut,
    SurroundingRectangle,
    TEAL,
    Tex,
    Text,
    UP,
    VGroup,
    WHITE,
    Write,
    cross,
    normalize,
    rotate_vector,
)  # noqa: E402
import _2024.transformers.network_flow as _network_flow_module  # noqa: E402
from _2024.transformers.embedding import (  # noqa: E402
    SimpleSpaceExample as _SimpleSpaceExample,
    get_direction_lines,
)
from _2024.transformers.network_flow import (  # noqa: E402
    FlowForCHM as _FlowForCHM,
    SimplifiedFlow as _SimplifiedFlow,
)

FONT = "PingFang SC"
_OriginalText = Text
_original_piece_rectangles = _network_flow_module.get_piece_rectangles


def _noto_text(*args, **kwargs):
    if args and args[0] == "Tokens":
        args = ("词元", *args[1:])
    kwargs.setdefault("font", FONT)
    return _OriginalText(*args, **kwargs)


def _compact_piece_rectangles(*args, **kwargs):
    rects = _original_piece_rectangles(*args, **kwargs)
    phrase_pieces = args[0]
    v_buff = kwargs.get("v_buff", 0.1)
    # Size each box from its own visible glyphs.  The upstream helper uses the
    # whole phrase's line box, which overstates mixed CJK/Latin token heights.
    for rect, piece in zip(rects, phrase_pieces):
        rect.set_height(piece.get_height() + 2 * v_buff, stretch=True)
    return rects


# Methods inherited from network_flow resolve Text in their defining module.
_network_flow_module.Text = _noto_text
_network_flow_module.get_piece_rectangles = _compact_piece_rectangles


class ReconstructionFlowForCHM(_FlowForCHM):
    """FlowForCHM with the labels and fixed next-token data seen in the film."""

    random_seed = 1
    example_text = "沿着 河岸 bank ... 直到 他们 跳进 [空缺]"
    possible_next_tokens = [
        ("水", 0.706),
        ("河流", 0.128),
        ("湖泊", 0.078),
        ("池塘", 0.006),
        ("岸边", 0.003),
        ("溪流", 0.002),
        ("bank", 0.002),
        ("海洋", 0.002),
    ]

    def construct(self):
        self.camera.light_source.set_z(20)
        self.show_initial_text_embedding(word_scale_factor=0.6)
        print(f"TIMING input_embeddings_end={float(self.time):.6f}")
        self.play(self.frame.animate.scale(1.25))
        self.show_simple_flow(self.x_range)
        print(f"TIMING alternating_layers_end={float(self.time):.6f}")
        self.remove_mlps()
        self.mention_repetitions()
        print(f"TIMING repetitions_end={float(self.time):.6f}")
        self.frame.clear_updaters()
        self.focus_on_last_layer()
        print(f"TIMING last_layer_focus_end={float(self.time):.6f}")
        self.play(self.frame.animate.scale(1.15).shift(RIGHT))
        self.show_unembedding()
        print(f"TIMING probabilities_end={float(self.time):.6f}")

    def progress_through_attention_block(self, *args, **kwargs):
        kwargs.update(label_text="注意力")
        _SimplifiedFlow.progress_through_attention_block(self, *args, **kwargs)

    def progress_through_mlp_block(self, *args, **kwargs):
        kwargs.update(label_text="前馈网络", title_font_size=92)
        _SimplifiedFlow.progress_through_mlp_block(self, *args, **kwargs)

    def mention_repetitions(self, depth=8):
        frame = self.frame
        layer = self.layers[-1]
        block = self.blocks[-1].body
        thin_blocks = block.replicate(2)
        thin_blocks.set_depth(1.0, stretch=True)
        dots = Tex(".....", font_size=250)
        brace = Brace(dots, UP)
        brace_text = Text("重复多层", font=FONT, font_size=44)
        rep_label = Group(dots, brace, brace_text)
        rep_label.set_width(depth)
        rep_label.rotate(PI / 2, DOWN)
        rep_label.next_to(layer, OUT, buff=3.0)
        rep_label.align_to(ORIGIN, DOWN)
        thin_blocks[0].align_to(brace, IN)
        thin_blocks[1].align_to(brace, OUT)
        dots.scale(0.5)
        VGroup(brace, brace_text).next_to(thin_blocks, UP)
        final_layer = self.get_next_layer_array(layer)
        final_layer.set_z(rep_label.get_z(OUT) + 1)
        final_layer.save_state()
        final_layer.become(layer)
        final_layer.set_opacity(0)
        self.play(
            frame.animate.reorient(-57, -8, 0, (-6.59, 1.2, 57.84), 30),
            FadeIn(thin_blocks, lag_ratio=0.1),
            GrowFromCenter(brace),
            Write(brace_text, time_span=(1, 2)),
            Write(dots),
            run_time=3,
        )
        self.play(Restore(final_layer, run_time=2))
        self.wait()
        self.rep_label = rep_label
        self.blocks.add(*thin_blocks)
        self.layers.add(final_layer)


class ReconstructionBankSemanticSpace(_SimpleSpaceExample):
    """SimpleSpaceExample using the bank meanings present in the source comments."""

    random_seed = 1

    def construct(self):
        frame = self.frame
        plane, axes = self.add_plane_and_axes()
        frame.reorient(14, 77, 0, (2.23, 0.25, 1.13), 4.46)

        frame.add_ambient_rotation()
        vect = Arrow(axes.c2p(0, 0, 0), axes.c2p(2, -1, 1), buff=0)
        vect.set_color(BLUE)
        vect.always.set_perpendicular_to_camera(self.frame)
        label = Text("bank\n（河岸 / 银行）", font=FONT, font_size=24)
        label.rotate(PI / 2, RIGHT)
        label.next_to(vect.get_center(), OUT + LEFT, buff=0)

        self.play(ShowCreation(vect), FadeIn(label, vect.get_vector()))
        self.wait(5)
        print(f"TIMING bank_vector_end={float(self.time):.6f}")

        ideas = VGroup(
            Text("河岸", font=FONT),
            Text("故事开头", font=FONT),
            Text("交代场景", font=FONT),
        )
        ideas.set_backstroke(BLACK, 3)
        ideas.scale(0.35)
        ideas.rotate(PI / 2, RIGHT)

        last_idea = VGroup()
        last_direction = 1.0 * normalize(cross(RIGHT, vect.get_vector()))
        for idea in ideas:
            direction = rotate_vector(last_direction, PI / 3, vect.get_vector())
            new_vect = self.get_added_vector(vect, direction)
            new_vect.set_perpendicular_to_camera(self.frame)
            idea.next_to(new_vect.get_center(), buff=0.1)
            lines = get_direction_lines(
                axes, new_vect.get_vector(), color=new_vect.get_color()
            )
            self.play(
                FadeOut(last_idea),
                ShowCreation(new_vect),
                FadeIn(idea, new_vect.get_vector()),
                LaggedStartMap(
                    ShowCreationThenFadeOut, lines, lag_ratio=2 / len(lines), run_time=2
                ),
            )
            self.wait(1)
            last_idea = VGroup(new_vect, idea)
            last_direction = direction
        self.play(FadeOut(last_idea))
        self.wait(5)
        print(f"TIMING meaning_preview_end={float(self.time):.6f}")

        ideas = VGroup(
            Text("河岸", font=FONT),
            Text("故事开头", font=FONT),
            Text("交代场景", font=FONT),
        )
        ideas.scale(0.4)
        ideas.rotate(PI / 2, RIGHT)
        directions = [
            (-0.25, -1, 0.75),
            (-0.5, -0.25, 0.5),
            (1.0, -0.5, 1.0),
        ]
        orientations = [
            (11, 92, 0, (2.69, 0.55, 1.12), 6.25),
            (-8, 83, 0, (2.73, 0.56, 1.24), 6.80),
            (-14, 79, 0, (2.49, 0.61, 1.41), 7.64),
        ]

        vects = VGroup(vect)
        for idea, direction, orientation in zip(ideas, directions, orientations):
            new_vect = self.get_added_vector(vects[-1], direction)
            new_vect.always.set_perpendicular_to_camera(self.frame)
            idea.next_to(new_vect.get_center())
            self.play(
                frame.animate.reorient(*orientation),
                GrowArrow(new_vect),
                FadeIn(idea, 0.5 * new_vect.get_vector()),
            )
            self.wait(2)
            vects.add(new_vect)
        self.wait(15)
        print(f"TIMING three_meanings_end={float(self.time):.6f}")


class ReconstructionBankAttentionCloseup(ReconstructionFlowForCHM):
    """Film insert: front-facing first Attention layer with the bank column isolated."""

    def construct(self):
        self.camera.light_source.set_z(20)
        with self.temp_skip():
            self.show_initial_text_embedding(word_scale_factor=0.6)
            self.play(self.frame.animate.scale(1.25))
            self.progress_through_attention_block(
                target_orientation=(0, 0, 0),
                target_frame_height=8.5,
                target_frame_x=0,
                target_frame_y=0,
                attention_anim_run_time=1,
            )
            self.frame.reorient(0, 0, 0, self.layers[-1].get_center(), 8.5)

        index = self.example_text.split(" ").index("bank")
        layer = self.layers[-1]
        embedding = layer.embeddings[index]
        highlight = embedding.copy()
        highlight.set_backstroke(BLACK, 3)
        rect = SurroundingRectangle(highlight, buff=0.08)
        rect.set_stroke(TEAL, 3)
        bank_token = self.token_blocks[index]
        arrow = Arrow(
            bank_token.get_bottom(),
            rect.get_top(),
            tip_angle=45 * DEGREES,
            buff=0.08,
        )
        arrow.set_color(WHITE)
        image = ImageMobject(
            str(ROOT / "assets" / "images" / "river-bank-original.png")
        )
        image.set_height(2.2)
        image.next_to(rect, RIGHT, buff=0.35)
        image_border = SurroundingRectangle(image, buff=0).set_stroke(WHITE, 2)

        dimmed = VGroup(
            *(item for n, item in enumerate(layer.embeddings) if n != index)
        )
        self.add(layer, bank_token)
        self.play(
            dimmed.animate.set_opacity(0.12),
            self.token_blocks[:index].animate.set_opacity(0.12),
            self.token_blocks[index + 1 :].animate.set_opacity(0.12),
            FadeIn(highlight),
            ShowCreation(rect),
            GrowArrow(arrow),
            bank_token.animate.scale(1.8, about_edge=DOWN),
            run_time=3,
        )
        self.wait(2)
        self.play(FadeIn(image, 0.25 * RIGHT), ShowCreation(image_border), run_time=2)
        self.wait(3)
