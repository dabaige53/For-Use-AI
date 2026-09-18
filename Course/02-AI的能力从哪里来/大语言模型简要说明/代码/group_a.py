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


# Upstream: upstream/_2024/transformers/helpers.py:18-34
def get_paragraph(words, line_len=40, font_size=48):
    """
    Handle word wrapping
    """
    words = list(map(str.strip, words))
    word_lens = list(map(len, words))
    lines = []
    lh, rh = 0, 0
    while rh < len(words):
        rh += 1
        if sum(word_lens[lh:rh]) > line_len:
            rh -= 1
            lines.append(words[lh:rh])
            lh = rh
    lines.append(words[lh:])
    text = "\n".join([" ".join(line).strip() for line in lines])
    return Text(text, alignment="LEFT", font_size=font_size)

# Upstream: upstream/_2024/transformers/helpers.py:37-48
def softmax(logits, temperature=1.0):
    logits = np.array(logits)
    with warnings.catch_warnings():
        warnings.filterwarnings('ignore')  # Ignore all warnings within this block
        logits = logits - np.max(logits)  # For numerical stability
        exps = np.exp(np.divide(logits, temperature, where=temperature != 0))
    
    if np.isinf(exps).any() or np.isnan(exps).any() or temperature == 0:
        result = np.zeros_like(logits)
        result[np.argmax(logits)] = 1
        return result
    return exps / np.sum(exps)

# Upstream: upstream/_2024/transformers/helpers.py:51-65
def value_to_color(
    value,
    low_positive_color=BLUE_E,
    high_positive_color=BLUE_B,
    low_negative_color=RED_E,
    high_negative_color=RED_B,
    min_value=0.0,
    max_value=10.0
):
    alpha = clip(float(inverse_interpolate(min_value, max_value, abs(value))), 0, 1)
    if value >= 0:
        colors = (low_positive_color, high_positive_color)
    else:
        colors = (low_negative_color, high_negative_color)
    return interpolate_color_by_hsl(*colors, alpha)

# Upstream: upstream/_2024/transformers/helpers.py:68-69
def read_in_book(name="tale_of_two_cities"):
    return Path(DATA_DIR, name).with_suffix(".txt").read_text()

# Upstream: upstream/_2024/transformers/helpers.py:72-94
def load_image_net_data(dataset_name="image_net_1k"):
    data_path = Path(Path.home(), "Documents", dataset_name)
    image_dir = Path(data_path, "images")
    label_category_path = Path(DATA_DIR, "image_categories.txt")
    image_label_path = Path(data_path, "image_labels.txt")

    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
        image_data = datasets.load_from_disk(str(data_path))
        indices = range(len(image_data))
        categories = label_category_path.read_text().split("\n")
        labels = [categories[image_data[index]['label']] for index in indices]
        image_label_path.write_text("\n".join(labels))
        for index in ProgressDisplay(indices):
            image = image_data[index]['image']
            image.save(str(Path(image_dir, f"{index}.jpeg")))


    labels = image_label_path.read_text().split("\n")
    return [
        (Path(image_dir, f"{index}.jpeg"), label)
        for index, label in enumerate(labels)
    ]

# Upstream: upstream/_2024/transformers/helpers.py:97-129
def show_matrix_vector_product(scene, matrix, vector, buff=0.25, x_max=999, fix_in_frame=False):
    # Show product
    eq = Tex("=")
    eq.set_width(0.5 * vector.get_width())
    shape = (matrix.shape[0], 1)
    rhs = NumericEmbedding(
        values=x_max * np.ones(shape),
        value_range=(-x_max, x_max),
        decimal_config=dict(include_sign=True, edge_to_fix=ORIGIN),
        ellipses_row=matrix.ellipses_row,
    )
    rhs.scale(vector.elements[0].get_height() / rhs.elements[0].get_height())
    eq.next_to(vector, RIGHT, buff=buff)
    rhs.next_to(eq, RIGHT, buff=buff)
    if fix_in_frame:
        eq.fix_in_frame()
        rhs.fix_in_frame()

    scene.play(FadeIn(eq), FadeIn(rhs.get_brackets()))

    last_rects = VGroup()
    n_rows = len(matrix.rows)
    for n, row, entry in zip(it.count(), matrix.get_rows(), rhs[:-2]):
        if matrix.ellipses_row is not None and n == (matrix.ellipses_row % n_rows):
            scene.add(entry)
        else:
            last_rects = matrix_row_vector_product(
                scene, row, vector, entry, last_rects,
                fix_in_frame=fix_in_frame
            )
    scene.play(FadeOut(last_rects))

    return eq, rhs

# Upstream: upstream/_2024/transformers/helpers.py:132-159
def matrix_row_vector_product(scene, row, vector, entry, to_fade, fix_in_frame=False):
    def get_rect(elem):
        return SurroundingRectangle(elem, buff=0.1, is_fixed_in_frame=fix_in_frame).set_stroke(YELLOW, 2)

    row_rects = VGroup(*map(get_rect, row))
    vect_rects = VGroup(*map(get_rect, vector[:-2]))
    partial_values = [0]
    for e1, e2 in zip(row, vector[:-2]):
        if not isinstance(e1, DecimalNumber) and isinstance(e2, DecimalNumber):
            increment = 0
        else:
            val1 = round(e1.get_value(), e1.num_decimal_places)
            val2 = round(e2.get_value(), e2.num_decimal_places)
            increment = val1 * val2
        partial_values.append(partial_values[-1] + increment)
    n_values = len(partial_values)

    scene.play(
        ShowIncreasingSubsets(row_rects),
        ShowIncreasingSubsets(vect_rects),
        UpdateFromAlphaFunc(entry, lambda m, a: m.set_value(
            partial_values[min(int(np.round(a * n_values)), n_values - 1)]
        )),
        FadeOut(to_fade),
        rate_func=linear,
    )

    return VGroup(row_rects, vect_rects)

# Upstream: upstream/_2024/transformers/helpers.py:162-218
def get_full_matrix_vector_product(
    mat_sym="w",
    vect_sym="x",
    n_rows=5,
    n_cols=5,
    mat_sym_color=BLUE,
    height=3.0,
    ellipses_row=-2,
    ellipses_col=-2,
):
    m_indices = list(map(str, [*range(1, n_cols), "m"]))
    n_indices = list(map(str, [*range(1, n_rows), "n"]))
    matrix = TexMatrix(
        [
            [Rf"{mat_sym}_{{{m}, {n}}}" for n in n_indices]
            for m in m_indices
        ],
        ellipses_row=ellipses_row,
        ellipses_col=ellipses_col,
    )
    matrix.set_height(height)
    matrix.get_entries().set_color(mat_sym_color)
    vector = TexMatrix(
        [[Rf"x_{{{n}}}"] for n in n_indices],
        ellipses_row=ellipses_row,
    )
    vector.match_height(matrix)
    vector.next_to(matrix, RIGHT)
    equals = Tex("=", font_size=72)
    equals.next_to(vector, RIGHT)

    result_terms = [
        [Rf"w_{{{m}, {n}}} x_{n}" for n in n_indices]
        for m in m_indices
    ]
    rhs = TexMatrix(
        result_terms,
        ellipses_row=ellipses_row,
        ellipses_col=ellipses_col,
    )
    rhs.match_height(matrix)
    rhs.next_to(equals, RIGHT)
    for m, row in enumerate(rhs.get_rows()):
        if m == (ellipses_row % len(m_indices)):
            continue
        for n, entry in enumerate(row):
            if n != (ellipses_col % len(n_indices)):
                entry[:4].set_color(mat_sym_color)
        for e1, e2 in zip(row, row[1:]):
            plus = Tex("+")
            plus.match_height(e1)
            points = [e1.get_right(), e2.get_left()]
            plus.move_to(midpoint(*points))
            plus.align_to(e1, UP)
            e2.add(plus)

    return matrix, vector, equals, rhs

# Upstream: upstream/_2024/transformers/helpers.py:221-237
def show_symbolic_matrix_vector_product(scene, matrix, vector, rhs, run_time_per_row=0.75):
    last_rects = VGroup()
    for mat_row, rhs_row in zip(matrix.get_rows(), rhs.get_rows()):
        mat_rects = VGroup(*map(SurroundingRectangle, mat_row))
        vect_rects = VGroup(*map(SurroundingRectangle, vector.get_columns()[0]))
        rect_group = VGroup(mat_rects, vect_rects)
        rect_group.set_stroke(YELLOW, 2)
        scene.play(
            FadeOut(last_rects),
            *(
                ShowIncreasingSubsets(group, rate_func=linear)
                for group in [mat_rects, vect_rects, rhs_row]
            ),
            run_time=run_time_per_row,
        )
        last_rects = rect_group
    scene.play(FadeOut(last_rects))

# Upstream: upstream/_2024/transformers/helpers.py:240-255
def data_flying_animation(
    point,
    vect=2 * DOWN + RIGHT,
    color=GREY_C,
    max_opacity=0.75,
    font_size=48,
    fix_in_frame=False
    ):
    word = Text("Data", color=color, font_size=font_size)
    if fix_in_frame:
        word.fix_in_frame()
    return UpdateFromAlphaFunc(
        word, lambda m, a: m.move_to(
            interpolate(point, point + vect, a)
        ).set_opacity(there_and_back(a) * max_opacity)
    )

# Upstream: upstream/_2024/transformers/helpers.py:258-287
def get_data_modifying_matrix_anims(
    matrix,
    word_shape=(5, 10),
    alpha_maxes=(0.7, 0.9),
    shift_vect=2 * DOWN + RIGHT,
    run_time=3,
    fix_in_frame=False,
    font_size=48,
):
    x_min, x_max = [matrix.get_x(LEFT), matrix.get_x(RIGHT)]
    y_min, y_max = [matrix.get_y(UP), matrix.get_y(DOWN)]
    z = matrix.get_z()
    points = np.array([
        [
            interpolate(x_min, x_max, a1),
            interpolate(y_min, y_max, a2),
            z,
        ]
        for a1 in np.linspace(0, alpha_maxes[1], word_shape[1])
        for a2 in np.linspace(0, alpha_maxes[0], word_shape[0])
    ])
    return [
        LaggedStart(
            (data_flying_animation(p, vect=shift_vect, fix_in_frame=fix_in_frame, font_size=font_size)
            for p in points),
            lag_ratio=1 / len(points),
            run_time=run_time
        ),
        RandomizeMatrixEntries(matrix, run_time=run_time),
    ]

# Upstream: upstream/_2024/transformers/helpers.py:290-292
def data_modifying_matrix(scene, matrix, *args, **kwargs):
    anims = get_data_modifying_matrix_anims(matrix, *args, **kwargs)
    scene.play(*anims)

# Upstream: upstream/_2024/transformers/helpers.py:295-310
def create_pixels(image_mob, pixel_width=0.1):
    x0, y0, z0 = image_mob.get_corner(UL)
    x1, y1, z1 = image_mob.get_corner(DR)
    points = np.array([
        [x, y, 0]
        for y in np.arange(y0, y1, -pixel_width)
        for x in np.arange(x0, x1, pixel_width)
    ])
    square = Square(pixel_width).set_fill(WHITE, 1).set_stroke(width=0)
    pixels = VGroup(
        square.copy().move_to(point, UL).set_color(
            Color(rgb=image_mob.point_to_rgb(point))
        )
        for point in points
    )
    return pixels

# Upstream: upstream/_2024/transformers/helpers.py:313-323
def get_network_connections(layer1, layer2, max_width=2.0, opacity_exp=1.0):
    radius = layer1[0].get_width() / 2
    return VGroup(
        Line(n1.get_center(), n2.get_center(), buff=radius).set_stroke(
            color=value_to_color(random.uniform(-10, 10)),
            width=max_width * random.random(),
            opacity=random.random()**opacity_exp,
        )
        for n1 in layer1
        for n2 in layer2
    )

# Upstream: upstream/_2024/transformers/helpers.py:326-339
def get_vector_pair(angle_in_degrees=90, length=1.0, colors=(BLUE, BLUE)):
    angle = angle_in_degrees * DEGREES
    v1 = Vector(length * RIGHT)
    v2 = v1.copy().rotate(angle, about_point=ORIGIN)
    v1.set_color(colors[0])
    v2.set_color(colors[1])
    arc = Arc(radius=0.2, angle=angle)
    arc.set_stroke(WHITE, 2)
    label = Tex(Rf"180^\circ", font_size=24)
    num = label.make_number_changeable("180")
    num.set_value(angle_in_degrees)
    label.next_to(arc.pfp(0.5), normalize(arc.pfp(0.5)), buff=SMALL_BUFF)

    return VGroup(v1, v2, arc, label)

# Upstream: upstream/_2024/transformers/helpers.py:342-393
class NeuralNetwork(VGroup):
    def __init__(
        self,
        layer_sizes=[6, 12, 6],
        neuron_radius=0.1,
        v_buff_ratio=1.0,
        h_buff_ratio=7.0,
        max_stroke_width=2.0,
        stroke_decay=2.0,
    ):
        self.max_stroke_width = max_stroke_width
        self.stroke_decay = stroke_decay
        layers = VGroup(*(
            Dot(radius=neuron_radius).get_grid(n, 1, v_buff_ratio=v_buff_ratio)
            for n in layer_sizes
        ))
        layers.arrange(RIGHT, buff=h_buff_ratio * layers[0].get_width())

        lines = VGroup(*(
            VGroup(*(
                Line(
                    n1.get_center(),
                    n2.get_center(),
                    buff=n1.get_width() / 2,
                )
                for n1, n2 in it.product(l1, l2)
            ))
            for l1, l2 in zip(layers, layers[1:])
        ))

        super().__init__(layers, lines)
        self.layers = layers
        self.lines = lines

        self.randomize_layer_values()
        self.randomize_line_style()

    def randomize_layer_values(self):
        for group in self.lines:
            for line in group:
                line.set_stroke(
                    value_to_color(random.uniform(-10, 10)),
                    self.max_stroke_width * random.random()**self.stroke_decay,
                )
        return self

    def randomize_line_style(self):
        for layer in self.layers:
            for dot in layer:
                dot.set_stroke(WHITE, 1)
                dot.set_fill(WHITE, random.random())
        return self

# Upstream: upstream/_2024/transformers/helpers.py:396-442
class ContextAnimation(LaggedStart):
    def __init__(
        self,
        target,
        sources,
        direction=UP,
        hue_range=(0.1, 0.3),
        time_width=2,
        min_stroke_width=0,
        max_stroke_width=5,
        lag_ratio=None,
        strengths=None,
        run_time=3,
        fix_in_frame=False,
        path_arc=PI / 2,
        **kwargs,
    ):
        arcs = VGroup()
        if strengths is None:
            strengths = np.random.random(len(sources))**2
        for source, strength in zip(sources, strengths):
            sign = direction[1] * (-1)**int(source.get_x() < target.get_x())
            arcs.add(Line(
                source.get_edge_center(direction),
                target.get_edge_center(direction),
                path_arc=sign * path_arc,
                stroke_color=random_bright_color(hue_range=hue_range),
                stroke_width=interpolate(
                    min_stroke_width,
                    max_stroke_width,
                    strength,
                )
            ))
        if fix_in_frame:
            arcs.fix_in_frame()
        arcs.shuffle()
        lag_ratio = 0.5 / len(arcs) if lag_ratio is None else lag_ratio

        super().__init__(
            *(
                VShowPassingFlash(arc, time_width=time_width)
                for arc in arcs
            ),
            lag_ratio=lag_ratio,
            run_time=run_time,
            **kwargs,
        )

# Upstream: upstream/_2024/transformers/helpers.py:445-468
class LabeledArrow(Arrow):
    def __init__(
        self,
        *args,
        label_text: Optional[str] = None,
        font_size: float = 24,
        label_buff: float = 0.1,
        direction: Optional[Vect3] = None,
        label_rotation: float = PI / 2,
        **kwargs
    ):
        super().__init__(*args, **kwargs)
        if label_text is not None:
            start, end = self.get_start_and_end()
            label = Text(label_text, font_size=font_size)
            label.set_fill(self.get_color())
            label.set_backstroke()
            label.rotate(label_rotation, RIGHT)
            if direction is None:
                direction = normalize(end - start)
            label.next_to(end, direction, buff=label_buff)
            self.label = label
        else:
            self.label = None

# Upstream: upstream/_2024/transformers/helpers.py:471-521
class WeightMatrix(DecimalMatrix):
    def __init__(
        self,
        values: Optional[np.ndarray] = None,
        shape: tuple[int, int] = (6, 8),
        value_range: tuple[float, float] = (-9.9, 9.9),
        ellipses_row: Optional[int] = -2,
        ellipses_col: Optional[int] = -2,
        num_decimal_places: int = 1,
        bracket_h_buff: float = 0.1,
        decimal_config=dict(include_sign=True),
        low_positive_color: ManimColor = BLUE_E,
        high_positive_color: ManimColor = BLUE_B,
        low_negative_color: ManimColor = RED_E,
        high_negative_color: ManimColor = RED_B,
    ):
        if values is not None:
            shape = values.shape
        self.shape = shape
        self.value_range = value_range
        self.low_positive_color = low_positive_color
        self.high_positive_color = high_positive_color
        self.low_negative_color = low_negative_color
        self.high_negative_color = high_negative_color
        self.ellipses_row = ellipses_row
        self.ellipses_col = ellipses_col

        if values is None:
            values = np.random.uniform(*self.value_range, size=shape)

        super().__init__(
            values,
            num_decimal_places=num_decimal_places,
            bracket_h_buff=bracket_h_buff,
            decimal_config=decimal_config,
            ellipses_row=ellipses_row,
            ellipses_col=ellipses_col,
        )
        self.reset_entry_colors()

    def reset_entry_colors(self):
        for entry in self.get_entries():
            entry.set_fill(color=value_to_color(
                entry.get_value(),
                self.low_positive_color,
                self.high_positive_color,
                self.low_negative_color,
                self.high_negative_color,
                0, max(self.value_range),
            ))
        return self

# Upstream: upstream/_2024/transformers/helpers.py:524-565
class NumericEmbedding(WeightMatrix):
    def __init__(
        self,
        values: Optional[np.ndarray] = None,
        shape: Optional[Tuple[int, int]] = None,
        length: int = 7,
        num_decimal_places: int = 1,
        ellipses_row: int = -2,
        ellipses_col: int = -2,
        value_range: tuple[float, float] = (-9.9, 9.9),
        bracket_h_buff: float = 0.1,
        decimal_config=dict(include_sign=True),
        dark_color: ManimColor = GREY_C,
        light_color: ManimColor = WHITE,
        **kwargs,
    ):
        if values is not None:
            if len(values.shape) == 1:
                values = values.reshape((values.shape[0], 1))
            shape = values.shape
        if shape is None:
            shape = (length, 1)
        super().__init__(
            values,
            shape=shape,
            value_range=value_range,
            num_decimal_places=num_decimal_places,
            bracket_h_buff=bracket_h_buff,
            decimal_config=decimal_config,
            low_positive_color=dark_color,
            high_positive_color=light_color,
            low_negative_color=dark_color,
            high_negative_color=light_color,
            ellipses_row=ellipses_row,
            ellipses_col=ellipses_col,
            **kwargs,
        )

        # No sign on zeros
        for entry in self.get_entries():
            if entry.get_value() == 0:
                entry[0].set_opacity(0)

# Upstream: upstream/_2024/transformers/helpers.py:568-627
class EmbeddingArray(VGroup):
    def __init__(
        self,
        shape=(10, 9),
        height=4,
        dots_index=-4,
        buff_ratio=0.4,
        bracket_color=GREY_B,
        backstroke_width=3,
        add_background_rectangle=False,
    ):
        super().__init__()

        # Embeddings
        embeddings = VGroup(
            NumericEmbedding(length=shape[0])
            for n in range(shape[1])
        )
        embeddings.set_height(height)
        buff = buff_ratio * embeddings[0].get_width()
        embeddings.arrange(RIGHT, buff=buff)

        # Background rectangle
        if add_background_rectangle:
            for embedding in embeddings:
                embedding.add_background_rectangle()

        # Add brackets
        brackets = Tex("".join((
            R"\left[\begin{array}{c}",
            *(shape[1] // 3) * [R"\quad \\"],
            R"\end{array}\right]",
        )))
        brackets.set_height(1.1 * embeddings.get_height())
        lb = brackets[:len(brackets) // 2]
        rb = brackets[len(brackets) // 2:]
        lb.next_to(embeddings, LEFT, buff=0)
        rb.next_to(embeddings, RIGHT, buff=0)
        brackets.set_fill(bracket_color)

        # Assemble result
        dots = VGroup()
        self.add(embeddings, dots, brackets)
        self.embeddings = embeddings
        self.dots = dots
        self.brackets = brackets
        self.set_backstroke(BLACK, backstroke_width)

        if dots_index is not None:
            self.swap_embedding_for_dots(dots_index)


    def swap_embedding_for_dots(self, dots_index=-4):
        to_replace = self.embeddings[dots_index]
        dots = Tex(R"\dots", font_size=60)
        dots.set_width(0.75 * to_replace.get_width())
        dots.move_to(to_replace)
        self.embeddings.remove(to_replace)
        self.dots.add(dots)
        return self

# Upstream: upstream/_2024/transformers/helpers.py:630-648
class RandomizeMatrixEntries(Animation):
    def __init__(self, matrix, **kwargs):
        self.matrix = matrix
        self.entries = matrix.get_entries()
        self.start_values = [entry.get_value() for entry in self.entries]
        self.target_values = np.random.uniform(
            matrix.value_range[0],
            matrix.value_range[1],
            len(self.entries)
        )
        super().__init__(matrix, **kwargs)

    def interpolate_mobject(self, alpha: float) -> None:
        for index, entry in enumerate(self.entries):
            start = self.start_values[index]
            target = self.target_values[index]
            sub_alpha = self.get_sub_alpha(alpha, index, len(self.entries))
            entry.set_value(interpolate(start, target, sub_alpha))
        self.matrix.reset_entry_colors()

# Upstream: upstream/_2024/transformers/helpers.py:651-652
class AbstractEmbeddingSequence(MobjectMatrix):
    pass

# Upstream: upstream/_2024/transformers/helpers.py:655-758
class Dial(VGroup):
    def __init__(
        self,
        radius=0.5,
        relative_tick_size=0.2,
        value_range=(0, 1, 0.1),
        initial_value=0,
        arc_angle=270 * DEGREES,
        stroke_width=2,
        stroke_color=WHITE,
        needle_color=BLUE,
        needle_stroke_width=5.0,
        value_to_color_config=dict(),
        set_anim_streak_color=TEAL,
        set_anim_streak_width=4,
        set_value_anim_streak_density=6,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.value_range = value_range
        self.value_to_color_config = value_to_color_config
        self.set_anim_streak_color = set_anim_streak_color
        self.set_anim_streak_width = set_anim_streak_width
        self.set_value_anim_streak_density = set_value_anim_streak_density

        # Main dial
        self.arc = Arc(arc_angle / 2, -arc_angle, radius=radius)
        self.arc.rotate(90 * DEGREES, about_point=ORIGIN)

        low, high, step = value_range
        n_values = int(1 + (high - low) / step)
        tick_points = map(self.arc.pfp, np.linspace(0, 1, n_values))
        self.ticks = VGroup(*(
            Line((1.0 - relative_tick_size) * point, point)
            for point in tick_points
        ))
        self.bottom_point = VectorizedPoint(radius * DOWN)
        for mob in self.arc, self.ticks:
            mob.set_stroke(stroke_color, stroke_width)

        self.add(self.arc, self.ticks, self.bottom_point)

        # Needle
        self.needle = Line()
        self.needle.set_stroke(
            color=needle_color,
            width=[needle_stroke_width, 0]
        )
        self.add(self.needle)

        # Initialize
        self.set_value(initial_value)

    def value_to_point(self, value):
        low, high, step = self.value_range
        alpha = inverse_interpolate(low, high, value)
        return self.arc.pfp(alpha)

    def set_value(self, value):
        self.needle.put_start_and_end_on(
            self.get_center(),
            self.value_to_point(value)
        )
        self.needle.set_color(value_to_color(
            value,
            min_value=self.value_range[0],
            max_value=self.value_range[1],
            **self.value_to_color_config
        ))

    def animate_set_value(self, value, **kwargs):
        kwargs.pop("path_arc", None)
        center = self.get_center()
        points = [self.needle.get_end(), self.value_to_point(value)]
        vects = [point - center for point in points]
        angle1, angle2 = [
            (angle_of_vector(vect) + TAU / 4) % TAU - TAU / 4
            for vect in vects
        ]
        path_arc = angle2 - angle1

        density = self.set_value_anim_streak_density
        radii = np.linspace(0, 0.5 * self.get_width(), density + 1)[1:]
        diff_arcs = VGroup(*(
            Arc(
                angle1, angle2 - angle1,
                radius=radius,
                arc_center=center,
            )
            for radius in radii
        ))
        diff_arcs.set_stroke(self.set_anim_streak_color, self.set_anim_streak_width)

        return AnimationGroup(
            self.animate.set_value(value).set_anim_args(path_arc=path_arc, **kwargs),
            *(
                VShowPassingFlash(diff_arc, time_width=1.5, **kwargs)
                for diff_arc in diff_arcs
            )
        )

    def get_random_value(self):
        low, high, step = self.value_range
        return interpolate(low, high, random.random())

# Upstream: upstream/_2024/transformers/helpers.py:761-819
class MachineWithDials(VGroup):
    default_dial_config = dict(
        stroke_width=1.0,
        needle_stroke_width=5.0,
        relative_tick_size=0.25,
        set_anim_streak_width=2,
    )

    def __init__(
        self,
        width=5.0,
        height=4.0,
        n_rows=6,
        n_cols=8,
        dial_buff_ratio=0.5,
        stroke_color=WHITE,
        stroke_width=1,
        fill_color=GREY_D,
        fill_opacity=1.0,
        dial_config=dict(),
    ):
        super().__init__()
        box = Rectangle(width, height)
        box.set_stroke(stroke_color, stroke_width)
        box.set_fill(fill_color, fill_opacity)
        self.box = box

        dial_config = dict(**self.default_dial_config, **dial_config)
        dials = Dial(**dial_config).get_grid(n_rows, n_cols, buff_ratio=dial_buff_ratio)
        buff = dials[0].get_width() * dial_buff_ratio
        dials.set_width(box.get_width() - buff)
        dials.set_max_height(box.get_width() - buff)
        dials.move_to(box)
        for dial in dials:
            dial.set_value(dial.get_random_value())
        self.dials = dials

        self.add(box, dials)

    def random_change_animation(self, lag_factor=0.5, run_time=3.0, **kwargs):
        return LaggedStart(
            *(
                dial.animate_set_value(dial.get_random_value())
                for dial in self.dials
            ), lag_ratio=lag_factor / len(self.dials),
            run_time=run_time,
            **kwargs
        )

    def rotate_all_dials(self, run_time=2, lag_factor=1.0):
        shuffled_dials = list(self.dials)
        random.shuffle(shuffled_dials)
        return LaggedStart(
            *(
                Rotate(dial.needle, TAU, about_point=dial.get_center())
                for dial in shuffled_dials
            ),
            lag_ratio=lag_factor / len(self.dials)
        )

# Upstream: upstream/_2024/transformers/generation.py:14-15
def get_gpt2_tokenizer(model_name='gpt2'):
    return GPT2Tokenizer.from_pretrained(model_name)

# Upstream: upstream/_2024/transformers/generation.py:19-20
def get_gpt2_model(model_name='gpt2'):
    return GPT2LMHeadModel.from_pretrained(model_name)

# Upstream: upstream/_2024/transformers/generation.py:23-43
def gpt2_predict_next_token(text, n_shown=7):
    tokenizer = get_gpt2_tokenizer()
    model = get_gpt2_model()
    # Encode the input text
    indexed_tokens = tokenizer.encode(
        text, add_special_tokens=False, return_tensors='pt'
    )

    # Predict all tokens
    with torch.no_grad():
        outputs = model(indexed_tokens)
        # Pull out the first batch, and the last token prediction
        predictions = outputs[0][0, -1, :]

    # Get the predicted next token
    indices = torch.argsort(predictions)
    top_indices = reversed(indices[-n_shown:])
    tokens = list(map(tokenizer.decode, top_indices))
    probs = softmax(predictions)[top_indices]

    return tokens, probs

# Upstream: upstream/_2024/transformers/generation.py:46-63
def gpt3_predict_next_token(text, n_shown=10, random_seed=0):
    openai.api_key = os.getenv('OPENAI_KEY')
    response = openai.Completion.create(
        # Or another model version, adjust as necessary
        engine="gpt-3.5-turbo-instruct",
        prompt=text,
        max_tokens=1,
        n=1,
        temperature=1.0,
        user=str(random_seed),
        logprobs=50  # I think this is actually set to a max of 20?
    )
    top_logprob_dict = response.choices[0]["logprobs"]["top_logprobs"][0]
    tokens, logprobs = zip(*top_logprob_dict.items())
    probs = np.exp(logprobs)
    indices = np.argsort(-probs)
    shown_tokens = [tokens[i] for i in indices[:n_shown]]
    return shown_tokens, probs[indices[:n_shown]]

# Upstream: upstream/_2024/transformers/generation.py:66-67
def clean_text(text):
    return " ".join(filter(lambda s: s.strip(), re.split(r"\s", text)))

# Upstream: upstream/_2024/transformers/generation.py:70-109
def next_token_bar_chart(
    words, probs,
    reference_point=ORIGIN,
    font_size=24,
    width_100p=1.0,
    prob_exp=0.75,
    bar_height=0.25,
    bar_space_factor=0.5,
    buff=1.2,
    show_ellipses=True,
    use_percent=True,
):
    labels = VGroup(Text(word, font_size=font_size) for word in words)
    bars = VGroup(
        Rectangle(prob**(prob_exp) * width_100p, bar_height)
        for prob, label in zip(probs, labels)
    )
    bars.arrange(DOWN, aligned_edge=LEFT, buff=bar_space_factor * bar_height)
    bars.set_fill(opacity=1)
    bars.set_submobject_colors_by_gradient(TEAL, YELLOW)
    bars.set_stroke(WHITE, 1)

    bar_groups = VGroup()
    for label, bar, prob in zip(labels, bars, probs):
        if use_percent:
            prob_label = Integer(int(100 * prob), unit="%", font_size=0.75 * font_size)
        else:
            prob_label = DecimalNumber(prob, font_size=0.75 * font_size)
        prob_label.next_to(bar, RIGHT, buff=SMALL_BUFF)
        label.next_to(bar, LEFT)
        bar_groups.add(VGroup(label, bar, prob_label))

    if show_ellipses:
        ellipses = Tex(R"\vdots", font_size=font_size)
        ellipses.next_to(bar_groups[-1][0], DOWN)
        bar_groups.add(ellipses)

    bar_groups.shift(reference_point - bars.get_left() + buff * RIGHT)

    return bar_groups

# Upstream: upstream/_2024/transformers/generation.py:112-396
class SimpleAutogregression(InteractiveScene):
    text_corner = 3.5 * UP + 0.75 * RIGHT
    line_len = 31
    font_size = 35
    n_shown_predictions = 12
    seed_text = "Behold, a wild pi creature, foraging in its native"
    seed_text_color = BLUE_B
    machine_name = "Transformer"
    machine_phi = 10 * DEGREES
    machine_theta = 12 * DEGREES
    n_predictions = 120
    skip_through = False
    random_seed = 0
    model = "gpt2"

    def construct(self):
        # Repeatedly generate
        text_mob, next_word_line, machine = self.init_text_and_machine()
        for n in range(self.n_predictions):
            text_mob = self.new_selection_cycle(
                text_mob, next_word_line, machine,
                quick=(n > 10),
                skip_anims=self.skip_through,
            )

    def init_text_and_machine(self):
        # Set up active text
        self.cur_str = self.seed_text
        text_mob = self.string_to_mob(self.cur_str)
        text_mob.set_color(self.seed_text_color)
        next_word_line = self.get_next_word_line(text_mob)

        # Set up Transformer as some sort of machine
        machine = self.get_transformer_drawing()
        machine.set_y(0).to_edge(LEFT, buff=-0.6)

        self.add(text_mob)
        self.add(next_word_line)
        self.add(machine)

        return text_mob, next_word_line, machine

    def string_to_mob(self, text):
        text += " l"  # Dumb hack for alignment
        result = get_paragraph(
            text.replace("\n", " ").split(" "),
            self.line_len,
            self.font_size
        )
        result.move_to(self.text_corner, UL)
        result[-1].set_fill(BLACK, 0)  # Continue dumb hack
        result[-1].stretch(0, 0, about_edge=LEFT)
        return result

    def get_next_word_line(self, text_mob, char_len=7):
        next_word_line = Underline(text_mob[:char_len])
        next_word_line.set_stroke(TEAL, 2)
        next_word_line.next_to(text_mob[-1], RIGHT, SMALL_BUFF, aligned_edge=DOWN)
        if self.skip_through:
            next_word_line.set_opacity(0)
        return next_word_line

    def get_transformer_drawing(self):
        self.camera.light_source.move_to([-5, 5, 10])
        self.frame.set_field_of_view(20 * DEGREES)
        blocks = VGroup(
            VPrism(3, 2, 0.2)
            for n in range(10)
        )
        blocks.set_fill(GREY_D, 1)
        blocks.set_stroke(width=0)
        blocks.set_shading(0.25, 0.5, 0.2)
        blocks.arrange(OUT)
        blocks.move_to(ORIGIN, OUT)
        blocks.rotate(self.machine_phi, RIGHT, about_edge=OUT)
        blocks.rotate(self.machine_theta, UP, about_edge=OUT)

        blocks.deactivate_depth_test()
        for block in blocks:
            block.sort(lambda p: p[2])

        word = Text(self.machine_name, alignment="LEFT")
        word.next_to(blocks[-1], UP)
        word.shift(0.1 * UP + 0.4 * LEFT)
        word.move_to(blocks[-1])
        word.set_backstroke(BLACK, 5)
        out_arrow = Vector(
            0.5 * RIGHT, stroke_width=10,
            max_tip_length_to_length_ratio=0.5,
            max_width_to_length_ratio=12
        )
        out_arrow.next_to(blocks[-1], RIGHT, buff=SMALL_BUFF)
        out_arrow.set_opacity(0)

        result = VGroup(blocks, word, out_arrow)
        return result

    def get_distribution(
        self, words, probs, machine,
        font_size=24,
        width_100p=1.8,
        bar_height=0.25,
        show_ellipses=True
    ):
        labels = VGroup(Text(word, font_size=font_size) for word in words)
        bars = VGroup(
            Rectangle(prob * width_100p, bar_height)
            for prob, label in zip(probs, labels)
        )
        bars.arrange(DOWN, aligned_edge=LEFT, buff=0.5 * bar_height)
        bars.set_fill(opacity=1)
        bars.set_submobject_colors_by_gradient(TEAL, YELLOW)
        bars.set_stroke(WHITE, 1)

        bar_groups = VGroup()
        for label, bar, prob in zip(labels, bars, probs):
            prob_label = Integer(int(100 * prob), unit="%", font_size=0.75 * font_size)
            prob_label.next_to(bar, RIGHT, buff=SMALL_BUFF)
            label.next_to(bar, LEFT)
            bar_groups.add(VGroup(label, bar, prob_label))

        if show_ellipses:
            ellipses = Tex(R"\vdots", font_size=font_size)
            ellipses.next_to(bar_groups[-1][0], DOWN)
            bar_groups.add(ellipses)

        arrow_point = machine[-1].get_right()
        bar_groups.shift(arrow_point - bars.get_left() + 1.5 * RIGHT)
        bar_groups.align_to(machine, UP)

        return bar_groups

    def animate_text_input(self, text_mob, machine, position_text_over_machine=True, added_anims=[], lag_ratio=0.02):
        blocks = machine[0]
        text_copy = text_mob.copy()
        if position_text_over_machine:
            text_copy.target = text_copy.generate_target()
            text_copy.target.set_max_width(4)
            text_copy.target.next_to(blocks[0], UP)
            text_copy.target.shift_onto_screen()
            self.play(MoveToTarget(text_copy, path_arc=-45 * DEGREES))
        self.play(LaggedStart(
            *added_anims,
            Transform(
                text_copy,
                VGroup(VectorizedPoint(machine.get_top())),
                lag_ratio=lag_ratio,
                run_time=1,
                path_arc=-45 * DEGREES,
                remover=True,
            ),
            LaggedStart(
                (
                    block.animate.set_color(
                        block.get_color() if block is blocks[-1] else TEAL
                    ).set_anim_args(rate_func=there_and_back)
                    for block in blocks
                ),
                lag_ratio=0.1,
                run_time=1
            ),
            Animation(machine[1:]),
            lag_ratio=0.5
        ))

    def animate_prediction_ouptut(self, machine, cur_str):
        words, probs = self.predict_next_token(cur_str)
        bar_groups = self.get_distribution(words, probs, machine)
        self.play(
            LaggedStart(
                (FadeInFromPoint(bar_group, machine[0][-1].get_right())
                for bar_group in bar_groups),
                lag_ratio=0.025,
                group=bar_groups,
                run_time=1
            )
        )
        return bar_groups

    def animate_random_sample(self, bar_groups):
        widths = np.array([group[1].get_width() for group in bar_groups[:-1]])
        dist = widths / widths.sum()
        seed = random.randint(0, 1000)
        buff = 0.025
        highlight_rect = SurroundingRectangle(bar_groups[0], buff=buff)
        highlight_rect.set_stroke(YELLOW, 2)
        highlight_rect.set_fill(YELLOW, 0.25)

        def highlight_randomly(rect, dist, alpha):
            np.random.seed(seed + int(10 * alpha))
            index = np.random.choice(np.arange(len(dist)), p=dist)
            rect.surround(bar_groups[index], buff=buff)
            rect.stretch(1.1, 0)

        self.play(
            UpdateFromAlphaFunc(highlight_rect, lambda rect, a: highlight_randomly(rect, dist, a)),
            Animation(bar_groups)
        )

        bar_groups.add_to_back(highlight_rect)

    def animate_word_addition(self, bar_groups, text_mob, next_word_line, force_unskip=False):
        # Choose the highlighted_group
        bar_group = None
        if isinstance(bar_groups[0], Rectangle):
            # Use the highlight rect to find the group element
            bars = bar_groups[1:-1]
            diffs = [abs(bg.get_y() - bar_groups[0].get_y()) for bg in bars]
            bar_group = bar_groups[1:][np.argmin(diffs)]
        if bar_group is None:
            bar_group = bar_groups[0]

        # Animate selection
        word = bar_group[0].get_text()
        new_str = self.cur_str + word
        new_text_mob = self.string_to_mob(new_str)
        new_text_mob[:len(self.seed_text.replace(" ", ""))].set_color(self.seed_text_color)

        word_targets = new_text_mob[word.strip()]
        if len(word_targets) > 0:
            target = word_targets[-1]
        else:
            target = new_text_mob[-len(word) - 1:-1]

        # target = new_text_mob[-len(word):]

        self.add(bar_groups)
        self.play(
            FadeTransform(bar_group[0].copy(), target),
            Transform(
                next_word_line,
                self.get_next_word_line(new_text_mob),
            ),
        )
        if force_unskip:
            self.skip_animations = False
            target.save_state()
            target.set_fill(YELLOW)
            self.wait(0.5)
            target.restore()
            self.skip_animations = True
        self.play(
            FadeOut(bar_groups),
        )

        self.remove(text_mob)
        self.add(new_text_mob)

        self.cur_str = new_str

        return new_text_mob

    def new_selection_cycle(self, text_mob, next_word_line, machine, quick=False, skip_anims=False):
        if skip_anims:
            self.skip_animations = True

        if quick:
            words, probs = self.predict_next_token(self.cur_str)
            bar_groups = self.get_distribution(words, probs, machine)
            self.add(bar_groups)
        else:
            self.animate_text_input(text_mob, machine)
            bar_groups = self.animate_prediction_ouptut(machine, self.cur_str)
        self.animate_random_sample(bar_groups)
        new_text_mob = self.animate_word_addition(
            bar_groups, text_mob, next_word_line,
            force_unskip=skip_anims
        )
        return new_text_mob

    #

    def predict_next_token(self, text):
        result = None
        n_shown = self.n_shown_predictions
        if self.model == "gpt3":
            try:
                result = gpt3_predict_next_token(
                    text, n_shown, random_seed=self.random_seed
                )
            except Exception as e:
                pass
        if result is None:
            result = gpt2_predict_next_token(text, n_shown)
        return result

# Upstream: upstream/_2024/transformers/generation.py:399-409
class AltSimpleAutoRegression(SimpleAutogregression):
    n_predictions = 1
    line_len = 25

    def reposition_transformer_drawing(self, machine):
        machine.move_to(0.5 * RIGHT)
        in_arrow = machine[-1].copy()
        in_arrow.rotate(-45 * DEGREES)
        in_arrow.next_to(machine, UL)
        self.add(in_arrow)
        return machine

# Upstream: upstream/_2024/transformers/generation.py:412-453
class AnnotateNextWord(SimpleAutogregression):
    def construct(self):
        text_mob, next_word_line, machine = self.init_text_and_machine()
        self.add(machine, *machine[1:])
        words, probs = self.predict_next_token(self.cur_str)
        bar_groups = self.get_distribution(words, probs, machine[-1].get_right())

        self.add(bar_groups)

        # Initial text
        from manimlib.mobject.boolean_ops import Union
        highlight = Union(
            SurroundingRectangle(text_mob["Behold, a wild pi creature,"]),
            SurroundingRectangle(text_mob["foraging in its native"]),
        )
        highlight.set_stroke(BLUE, 3)
        arrow = Vector(LEFT, stroke_width=10)
        arrow.next_to(highlight, RIGHT).match_y(text_mob[0])

        dist_rect = SurroundingRectangle(bar_groups)
        dist_rect.set_stroke(YELLOW, 2)

        self.play(
            ShowCreation(highlight),
            GrowArrow(arrow)
        )
        self.wait()
        self.play(
            arrow.animate.rotate(PI / 2).next_to(dist_rect, UP),
            ReplacementTransform(highlight, dist_rect),
        )
        self.wait()
        self.play(
            FadeOut(dist_rect),
            FadeOut(arrow),
        )

        # Flash through
        self.remove(bar_groups)
        text_mob = self.new_selection_cycle(
            text_mob, next_word_line, machine,
        )

# Upstream: upstream/_2024/transformers/generation.py:456-457
class QuickerRegression(SimpleAutogregression):
    skip_through = True

# Upstream: upstream/_2024/transformers/generation.py:460-461
class AutoregressionGPT3(SimpleAutogregression):
    model = "gpt3"

# Upstream: upstream/_2024/transformers/generation.py:464-466
class QuickRegressionGPT3(SimpleAutogregression):
    skip_through = True
    model = "gpt3"

# Upstream: upstream/_2024/transformers/generation.py:469-480
class GPT3CleverestAutocomplete(QuickRegressionGPT3):
    seed_text = "To date, the cleverest thinker of all time was"
    n_predictions = 70

    def construct(self):
        # Test
        text_mob, next_word_line, machine = self.init_text_and_machine()
        for n in range(self.n_predictions):
            text_mob = self.new_selection_cycle(
                text_mob, next_word_line, machine,
                skip_anims=(n > 2),
            )

# Upstream: upstream/_2024/transformers/generation.py:483-531
class GPT3OnLearningSimpler(QuickRegressionGPT3):
    seed_text = "The most effective way to learn computer science is"
    text_corner = 3.5 * UP + 3 * LEFT
    line_len = 35
    font_size = 35
    n_predictions = 300
    time_per_prediction = 0.2
    random_seed = 313
    model = "gpt3"
    min_y = -3
    up_shift = 5 * UP
    show_dist = False

    def construct(self):
        # Test
        cur_str = self.seed_text
        text_mob = VGroup()
        for n in range(self.n_predictions):
            self.clear()
            words, probs = self.predict_next_token(cur_str, n_shown=20)
            index = np.random.choice(np.arange(len(words)), p=(probs / probs.sum()))
            new_word = words[index]
            cur_str += new_word
            text_mob = self.string_to_mob(cur_str)

            # Color seed
            if self.color_seed:
                text_mob[:len(self.seed_text.replace(" ", ""))].set_color(BLUE)

            # Add to text, shift if necessary
            text_mob[new_word.strip()][-1].set_color(YELLOW)
            if text_mob.get_bottom()[1] < self.min_y:
                text_mob.shift(self.up_shift)
                self.text_corner += self.up_shift
            self.add(text_mob)

            # Add the distribution
            if self.show_dist:
                dist = self.get_distribution(
                    words[:self.n_shown_predictions],
                    probs[:self.n_shown_predictions],
                    buff=0
                )
                dist.set_height(4)
                dist.to_edge(DOWN)
                rect = SurroundingRectangle(dist[min(index, len(dist) - 1)])
                self.add(dist, rect)

            self.wait(self.time_per_prediction)

# Upstream: upstream/_2024/transformers/generation.py:534-537
class GPT3OnLongPassages(GPT3OnLearningSimpler):
    seed_text = "Writing long passages seems to involve more foresight and planning than what single-word prediction"
    n_predictions = 100
    color_seed = False

# Upstream: upstream/_2024/transformers/generation.py:540-542
class GPT3CreaturePrediction(GPT3CleverestAutocomplete):
    seed_text = "the fluffy blue creature"
    n_predictions = 1

# Upstream: upstream/_2024/transformers/generation.py:545-547
class GPT3CreaturePrediction2(GPT3CleverestAutocomplete):
    seed_text = "the fluffy blue creature roamed the"
    n_predictions = 1

# Upstream: upstream/_2024/transformers/generation.py:550-568
class LowTempExample(GPT3OnLearningSimpler):
    seed_text = "Once upon a time, there was a"
    model = "gpt3"
    min_y = 1
    up_shift = 2 * UP
    show_dist = True
    temp = 0
    n_predictions = 200
    time_per_prediction = 0.25

    def predict_next_token(self, text, n_shown=None):
        words, probs = super().predict_next_token(text, n_shown)
        if self.temp == 0:
            probs = np.zeros_like(probs)
            probs[0] = 1
        else:
            probs = probs**(1 / self.temp)
            probs /= probs.sum()
        return words, probs

# Upstream: upstream/_2024/transformers/generation.py:571-573
class HighTempExample(LowTempExample):
    temp = 5
    model = "gpt3"

# Upstream: upstream/_2024/transformers/generation.py:576-579
class MidTempExample(LowTempExample):
    seed_text = "If you could see the underlying probability distributions a large language model uses when generating text, then"
    temp = 1
    model = "gpt3"

# Upstream: upstream/_2024/transformers/generation.py:582-669
class ChatBotPrompt(SimpleAutogregression):
    system_prompt = """
        What follows is a conversation between a user and a helpful,
        very knowledgeable AI assistant.
    """
    user_prompt = "User: Give me some ideas for what to do when visiting Paris."
    ai_seed = "AI Assistant: "
    machine_name = "Large\nLanguage\nModel"

    line_len = 28
    font_size = 36
    color_seed = False

    n_predictions = 60
    model = "gpt3"
    random_seed = 12

    def construct(self):
        # Test
        text_mob, next_word_line, machine = self.init_text_and_machine()

        all_strs = list(map(clean_text, [self.system_prompt, self.user_prompt, self.ai_seed]))

        system_prompt, user_prompt, ai_seed = all_text = VGroup(
            get_paragraph(
                s.split(" "),
                font_size=self.font_size,
                line_len=self.line_len
            )
            for s in all_strs
        )
        all_text.arrange(DOWN, aligned_edge=LEFT, buff=0.75)
        all_text.move_to(self.text_corner, UL)
        self.remove(text_mob)
        self.add(all_text)

        text_mob = ai_seed
        self.text_corner = text_mob.get_corner(UL)
        next_word_line.next_to(ai_seed, RIGHT, aligned_edge=DOWN)

        self.cur_str = "\n\n".join(all_strs)

        # Comment on system prompt
        sys_rect = SurroundingRectangle(system_prompt)
        sys_rect.set_stroke(GREEN, 2)

        self.play(
            ShowCreation(sys_rect),
            system_prompt.animate.set_color(GREEN_B)
        )
        self.wait()

        # Users prompt
        from manimlib.mobject.boolean_ops import Union

        top_line = user_prompt["Give me some ideas for what"]
        low_line = user_prompt["to do when visiting Santiago."]
        user_rect = Union(
            SurroundingRectangle(low_line),
            SurroundingRectangle(top_line),
        )
        user_rect.set_stroke(BLUE, 2)

        sys_rect.insert_n_curves(100)
        self.play(
            ReplacementTransform(sys_rect, user_rect),
            top_line.animate.set_color(BLUE_B),
            low_line.animate.set_color(BLUE_B),
        )
        self.wait()
        self.play(
            FadeOut(user_rect),
        )

        # Run predictions
        text_mob = all_text
        self.add(all_text.copy())
        for n in range(self.n_predictions):
            text_mob = self.new_selection_cycle(
                text_mob, next_word_line, machine,
                skip_anims=(n > 0),
            )

    def string_to_mob(self, text):
        seed = self.ai_seed.strip()
        if seed in text:
            text = text[text.index(seed):]
        return super().string_to_mob(text)

# Upstream: upstream/_2024/transformers/generation.py:672-673
class ChatBotPrompt2(ChatBotPrompt):
    user_prompt = "User: Can you explain what temperature is, in the context of softmax?"

# Upstream: upstream/_2024/transformers/generation.py:676-677
class ChatBotPrompt3(ChatBotPrompt):
    user_prompt = "User: Can you give me some ideas for what to do while visiting Munich?"

# Upstream: upstream/_2024/transformers/generation.py:680-741
class VoiceToTextExample(SimpleAutogregression):
    model_name = "voice-to-text"

    def construct(self):
        # Add model
        box = Rectangle(4, 3)
        box.set_stroke(WHITE, 2)
        name = Text(self.model_name, font_size=60)
        name.set_max_width(box.get_width())
        name.next_to(box, UP)
        machine = self.get_transformer_drawing()
        machine.center()
        machine.set_max_width(0.75 * box.get_width())
        machine.move_to(box)
        arrows = Vector(0.75 * RIGHT, stroke_width=8).replicate(2)
        arrows[0].next_to(box, LEFT, SMALL_BUFF)
        arrows[1].next_to(box, RIGHT, SMALL_BUFF)
        model = Group(box, name, arrows, machine)

        self.add(*model)
        self.add(Point())

        # Process input
        max_width = 3.75
        in_mob = self.get_input().set_max_width(max_width)
        out_mob = self.get_output().set_max_width(max_width)
        in_mob.next_to(arrows, LEFT)
        out_mob.next_to(arrows, RIGHT)

        self.add(in_mob)
        self.play(LaggedStart(
            FadeOutToPoint(
                in_mob.copy(), machine.get_left(),
                path_arc=-45 * DEGREES,
                lag_ratio=0.01,
            ),
            LaggedStart(
                (block.animate.set_color(TEAL).set_anim_args(rate_func=there_and_back)
                for block in machine[0][:-1]),
                lag_ratio=0.1,
                run_time=1,
            ),
            FadeInFromPoint(
                out_mob.copy(), machine.get_right(),
                path_arc=45 * DEGREES,
                lag_ratio=0.02
            ),
            lag_ratio=0.7
        ))
        self.wait()

    def get_input(self) -> Mobject:
        result =ImageMobject("AudioSnippet").set_width(3.75)
        result.set_height(3, stretch=True)
        return result

    def get_output(self) -> Mobject:
        return Text("""
            Some models take
            in audio and
            produce a transcript
        """, alignment="LEFT")

# Upstream: upstream/_2024/transformers/generation.py:744-757
class TextToVoiceExample(VoiceToTextExample):
    model_name = "text-to-voice"

    def get_input(self):
        return Text("""
            This sentence comes from
            a model going the other
            way around, producing
            synthetic speech just
            from text.
        """, alignment="LEFT")

    def get_output(self):
        return super().get_input()

# Upstream: upstream/_2024/transformers/generation.py:760-811
class TextToImage(VoiceToTextExample):
    model_name = "text-to-image"
    prompt = """
        1960s photograph of a cute fluffy blue wild pi
        creature, a creature whose body is shaped like
        the symbol π, who is foraging in its native territory,
        staring back at the camera with an exotic scene
        in the background.
    """
    image_name = "PiCreatureDalle3_5"

    def get_clean_prompt(self):
        return clean_text(self.prompt)

    def get_input(self):
        return get_paragraph(self.get_clean_prompt().split(" "), line_len=25)

    def get_output(self):
        return ImageMobject(self.image_name)

    def generate_output(self):
        # Test
        self.prompt = """
            1960s photograph of a cute fluffy blue wild pi
            creature, a creature whose face bears a subtle resemblence
            to the shape of the symbol π, who is foraging in its native
            territory, staring back at the camera with an exotic scene
            in the background.
        """

        self.prompt = "abstract depiction of furry fluffiness"

        openai.api_key = os.getenv('OPENAI_KEY')
        prompt = self.get_clean_prompt()

        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        print(prompt)
        print(image_url)

        response = openai.Image.create_variation(
          image=open("/Users/grant/3Blue1Brown Dropbox/3Blue1Brown/images/raster/PiCreatureDalle3_17.png", "rb"),
          n=1,
          size="1024x1024"
        )

# Upstream: upstream/_2024/transformers/generation.py:814-821
class TranslationExample(VoiceToTextExample):
    model_name = "machine translation"

    def get_input(self):
        return Text("Attention is all\nyou need")

    def get_output(self):
        return Group(Point(), *Text("注意力就是你所需要的一切"))

# Upstream: upstream/_2024/transformers/generation.py:824-872
class PredictionVsGeneration(SimpleAutogregression):
    model = "gpt2"

    def construct(self):
        # Setup
        self.add(FullScreenRectangle())
        morty = Mortimer()
        morty.to_edge(DOWN)
        morty.body.insert_n_curves(100)
        self.add(morty)

        # Words
        words = VGroup(Text("Prediction"), Text("Generation"))
        words.scale(1.5)
        for vect, word in zip([UL, UR], words):
            word.next_to(morty, vect)
            word.shift(0.5 * UP)

        # Create prediction object
        seed_text = "The goal of predicting the next"
        self.n_shown_predictions = 8
        tokens, probs = self.predict_next_token(seed_text)
        dist = self.get_distribution(tokens, probs)
        brace = Brace(dist, LEFT, SMALL_BUFF)
        words = Text(seed_text, font_size=36).next_to(brace, LEFT)
        prediction = VGroup(words, brace, dist)
        prediction.set_width(FRAME_WIDTH / 2 - 1)
        prediction.next_to(morty, UL)
        prediction.shift(0.5 * UP).shift_onto_screen()
        self.add(prediction)

        # Animations
        self.play(
            morty.change("raise_right_hand", prediction),
            FadeIn(prediction[0], UP),
            GrowFromCenter(prediction[1]),
            LaggedStart(
                (FadeInFromPoint(bar, prediction[1].get_center())
                for bar in prediction[2]),
                lag_ratio=0.05,
            )
        )
        self.play(Blink(morty))
        self.play(
            morty.change("raise_left_hand", 3 * UR),
        )
        self.wait()
        self.play(Blink(morty))
        self.wait()

# Upstream: upstream/_2024/transformers/generation.py:875-950
class ManyParallelPredictions(SimpleAutogregression):
    line_len = 200
    n_shown_predictions = 8
    model = "gpt3"

    def construct(self):
        # Setup
        self.fake_machine = VectorizedPoint().replicate(3)
        full_string = "Harry Potter was a highly unusual boy"

        # Draw last layer vectors
        last_layer = VGroup(
            NumericEmbedding(length=10)
            for n in range(12)
        )
        last_layer.arrange(RIGHT, buff=0.35 * last_layer[0].get_width())
        last_layer.set_height(3)
        last_layer.to_edge(DOWN)
        # self.add(last_layer)

        rects = VGroup(map(SurroundingRectangle, last_layer))
        rects.set_stroke(YELLOW, 2)
        arrows = VGroup(Vector(0.5 * UP).next_to(rect, UP, buff=0.1) for rect in rects)
        arrows.set_stroke(YELLOW)

        # Show prediction groups
        words = full_string.split(" ")
        substrings = [
            " ".join(words[:n + 1])
            for n in range(len(words))
        ]

        predictions = VGroup(
            self.get_prediction_group(substring)
            for substring in substrings
        )
        predictions[0].to_edge(UP, buff=1.25).align_to(rects[1], LEFT)
        for prediction, arrow, rect in zip(predictions, arrows, rects):
            prediction.move_to(predictions[0], LEFT)
            arrow.become(Arrow(
                rect.get_top(),
                prediction[1].get_left(),
            ))
            arrow.set_stroke(YELLOW)

        last_group = VGroup(
            rects[0].copy().set_opacity(0),
            arrows[0].copy().set_opacity(0),
            predictions[0].copy().set_opacity(0),
        )
        for rect, arrow, prediction in zip(rects, arrows, predictions):
            self.remove(last_group)
            self.play(
                TransformFromCopy(last_group[0], rect),
                TransformFromCopy(last_group[1], arrow),
                TransformMatchingStrings(last_group[2][0].copy(), prediction[0], run_time=1),
                FadeTransform(last_group[2][1].copy(), prediction[1]),
                FadeTransform(last_group[2][2].copy(), prediction[2]),
            )
            self.wait()
            last_group = VGroup(rect, arrow, prediction)

    def get_prediction_group(self, text):
        words, probs = self.predict_next_token(text)
        dist = self.get_distribution(
            words, probs,
            width_100p=2.0
        )
        dist.set_max_height(2.5)
        brace = Brace(dist, LEFT)
        prefix = Text(text, font_size=30)
        prefix.next_to(brace, LEFT)

        result = VGroup(prefix, brace, dist)

        return result

# Upstream: upstream/_2024/transformers/generation.py:953-987
class PeekUnderTheHood(SimpleAutogregression):
    def construct(self):
        # Add parts
        text_mob, next_word_line, machine = self.init_text_and_machine()
        blocks, label, arrow = machine
        self.remove(text_mob, next_word_line)

        # Zoom in
        self.camera.light_source.move_to([-15, 5, 10])
        self.set_floor_plane("xz")

        blocks.rotate(-5 * DEGREES, UP, about_edge=OUT)
        blocks.rotate(-10 * DEGREES, RIGHT, about_edge=OUT)
        blocks.target = blocks.generate_target()
        blocks.target.set_height(5)
        blocks.target.center()
        blocks.target[5:].set_opacity(0.3)

        self.play(
            self.frame.animate.reorient(-23, -12, 0, (1.79, -0.56, 1.27), 8.40).set_anim_args(run_time=3),
            MoveToTarget(blocks, run_time=3),
            FadeOut(arrow, RIGHT),
            FadeOut(label, 2 * OUT),
        )
        self.wait()

        blocks[5:].set_opacity(0.3)

        # Add matrices
        matrices = VGroup(WeightMatrix(shape=(8, 8)) for x in range(9))
        matrices.arrange_in_grid(h_buff_ratio=0.25, v_buff_ratio=0.4)
        matrices.match_width(blocks)
        index = 6
        matrices.move_to(blocks[index], OUT)
        self.add(matrices, blocks[index:])

# Upstream: upstream/_2024/transformers/embedding.py:9-10
def get_token_encoding():
    return tiktoken.encoding_for_model("davinci")

# Upstream: upstream/_2024/transformers/embedding.py:13-19
def get_principle_components(data, n_components=3):
    covariance_matrix = np.cov(data, rowvar=False)
    eigenvalues, eigenvectors = np.linalg.eig(covariance_matrix)

    order_of_importance = np.argsort(eigenvalues)[::-1]
    sorted_eigenvectors = eigenvectors[:, order_of_importance]  # sort the columns
    return sorted_eigenvectors[:, :n_components]

# Upstream: upstream/_2024/transformers/embedding.py:22-25
def find_nearest_words(model, vector, n=20):
    data = model.vectors
    indices = np.argsort(((data - vector)**2).sum(1))
    return [model.index_to_key[i] for i in indices[:n]]

# Upstream: upstream/_2024/transformers/embedding.py:28-38
def break_into_pieces(phrase_mob: Text, offsets: list[int]):
    phrase = phrase_mob.get_string()
    lhs = offsets
    rhs = [*offsets[1:], len(phrase)]
    result = []
    for lh, rh in zip(lhs, rhs):
        substr = phrase[lh:rh]
        start = phrase_mob.substr_to_path_count(phrase[:lh])
        end = start + phrase_mob.substr_to_path_count(substr)
        result.append(phrase_mob[start:end])
    return VGroup(*result)

# Upstream: upstream/_2024/transformers/embedding.py:41-43
def break_into_words(phrase_mob):
    offsets = [m.start() for m in re.finditer(" ", phrase_mob.get_string())]
    return break_into_pieces(phrase_mob, [0, *offsets])

# Upstream: upstream/_2024/transformers/embedding.py:46-50
def break_into_tokens(phrase_mob):
    tokenizer = get_token_encoding()
    tokens = tokenizer.encode(phrase_mob.get_string())
    _, offsets = tokenizer.decode_with_offsets(tokens)
    return break_into_pieces(phrase_mob, offsets)

# Upstream: upstream/_2024/transformers/embedding.py:53-90
def get_piece_rectangles(
    phrase_pieces,
    h_buff=0.05,
    v_buff=0.1,
    fill_opacity=0.15,
    fill_color=None,
    stroke_width=1,
    stroke_color=None,
    hue_range=(0.5, 0.6),
    leading_spaces=False,
):
    rects = VGroup()
    height = phrase_pieces.get_height() + 2 * v_buff
    last_right_x = phrase_pieces.get_x(LEFT)
    for piece in phrase_pieces:
        left_x = last_right_x if leading_spaces else piece.get_x(LEFT)
        right_x = piece.get_x(RIGHT)
        fill = random_bright_color(hue_range) if fill_color is None else fill_color
        stroke = fill if stroke_color is None else stroke_color
        rect = Rectangle(
            width=right_x - left_x + 2 * h_buff,
            height=height,
            fill_color=fill,
            fill_opacity=fill_opacity,
            stroke_color=stroke,
            stroke_width=stroke_width
        )
        if leading_spaces:
            rect.set_x(left_x, LEFT)
        else:
            rect.move_to(piece)
        rect.set_y(0)
        rects.add(rect)

        last_right_x = right_x

    rects.match_y(phrase_pieces)
    return rects

# Upstream: upstream/_2024/transformers/embedding.py:93-99
def get_word_to_vec_model(model_name="glove-wiki-gigaword-50"):
    filename = str(Path(DATA_DIR, model_name))
    if os.path.exists(filename):
        return gensim.models.keyedvectors.KeyedVectors.load(filename)
    model = gensim.downloader.load(model_name)
    model.save(filename)
    return model

# Upstream: upstream/_2024/transformers/embedding.py:102-113
def get_direction_lines(axes, direction, n_lines=500, color=YELLOW, line_length=1.0, stroke_width=3):
    line = Line(ORIGIN, line_length * normalize(direction))
    line.insert_n_curves(20).set_stroke(width=(0, stroke_width, stroke_width, stroke_width, 0))
    lines = line.replicate(n_lines)
    lines.set_color(color)
    for line in lines:
        line.move_to(axes.c2p(
            random.uniform(*axes.x_range[:2]),
            random.uniform(*axes.y_range[:2]),
            random.uniform(*axes.z_range[:2]),
        ))
    return lines

# Upstream: upstream/_2024/transformers/embedding.py:119-257
class LyingAboutTokens2(InteractiveScene):
    def construct(self):
        # Mention next word prediction task
        phrase = Text("The goal of our model is to predict the next word")

        words = break_into_tokens(phrase)
        rects = get_piece_rectangles(words, leading_spaces=True, h_buff=0)

        words.remove(words[-1])
        q_marks = Text("???")
        rects[-1].set_color(YELLOW)
        q_marks.next_to(rects[-1], DOWN)

        big_rect = Rectangle()
        big_rect.replace(rects[:-1], stretch=True)
        big_rect.set_stroke(GREY_B, 2)
        arrow = Arrow(big_rect.get_top(), rects[-1].get_top(), path_arc=-120 * DEGREES)
        arrow.scale(0.5, about_edge=DR)

        self.play(ShowIncreasingSubsets(words, run_time=1))
        self.add(rects[-1])
        self.play(LaggedStart(
            FadeIn(big_rect),
            ShowCreation(arrow),
            Write(q_marks),
            lag_ratio=0.3,
        ))
        self.wait()
        self.play(
            FadeOut(big_rect),
            LaggedStart(*(
                DrawBorderThenFill(rect)
                for rect in rects[:-1]
            ), lag_ratio=0.02),
            LaggedStart(*(
                word.animate.match_color(rect)
                for word, rect in zip(words, rects)
            )),
            FadeOut(arrow)
        )
        self.wait()

        # Show words into vectors
        vectors = VGroup(*(
            NumericEmbedding(length=8)
            for word in words
        ))
        vectors.arrange(RIGHT, buff=1.0 * vectors[0].get_width())
        vectors.set_width(12)
        vectors.to_edge(DOWN, buff=1.0)
        vectors.to_edge(LEFT, buff=0.5)
        for vector, word in zip(vectors, words):
            vector.get_brackets().match_color(word[0])

        blocks = VGroup(*(VGroup(rect, word) for rect, word in zip(rects, words)))
        q_group = VGroup(rects[-1], q_marks)
        blocks.target = blocks.generate_target()
        for block, vector in zip(blocks.target, vectors):
            block.next_to(vector, UP, buff=1.5)

        arrows = VGroup(*(
            Arrow(block, vect, stroke_width=3)
            for block, vect in zip(blocks.target, vectors)
        ))

        self.play(
            MoveToTarget(blocks),
            q_group.animate.next_to(blocks.target, RIGHT, aligned_edge=UP),
            LaggedStartMap(FadeIn, vectors, shift=0.5 * DOWN),
            LaggedStartMap(GrowFromCenter, arrows),
        )
        self.wait()

        # Setup titles
        h_line = Line(LEFT, RIGHT).set_width(FRAME_WIDTH)
        title1, title2 = titles = VGroup(
            Text("The Truth", font_size=72).to_edge(UP),
            Text("A Convenient Lie", font_size=72).next_to(h_line, DOWN),
        )
        h_line.set_stroke(WHITE, 2)
        h_line.next_to(titles[1], UP)
        for title in titles:
            title.add(Underline(title))

        # Show the lie
        phrase1, phrase2 = phrases = VGroup(
            Text("This process (known fancifully as tokenization) frequently subdivides words"),
            # Text("It's nice to sometimes pretend tokens are words"),
            Text("Let's pretend that tokens are always simply words"),
        )
        for phrase, title in zip(phrases, titles):
            phrase.set_width(FRAME_WIDTH - 1)
            phrase.next_to(title, DOWN, buff=1.0)

        tokens = break_into_tokens(phrase1)
        words = break_into_words(phrase2)
        token_rects = get_piece_rectangles(tokens, hue_range=(0.1, 0.2), leading_spaces=True, h_buff=0.0)
        word_rects = get_piece_rectangles(words, hue_range=(0.5, 0.6))

        self.play(
            FadeOut(blocks),
            FadeOut(q_group),
            FadeOut(arrows),
            FadeOut(vectors),
            ShowCreation(h_line),
            FadeIn(title1, lag_ratio=0.1),
            FadeIn(tokens),
        )
        self.add(token_rects, tokens)
        self.play(
            LaggedStartMap(FadeIn, token_rects),
            LaggedStart(*(
                token.animate.set_color(rect.get_color())
                for token, rect in zip(tokens, token_rects)
            ))
        )
        self.wait()
        self.play(
            FadeIn(title2, lag_ratio=0.1),
            FadeIn(words),
        )
        self.add(word_rects, words)
        self.play(
            LaggedStartMap(FadeIn, word_rects),
            LaggedStart(*(
                token.animate.set_color(rect.get_color())
                for token, rect in zip(words, word_rects)
            ))
        )
        self.wait()

        # Analyze tokenization
        brace = Brace(token_rects[8], buff=0.05)

        self.play(GrowFromCenter(brace))
        self.wait()
        for index in [2, 4, 5, 7, 8, 9, 11, 12]:
            self.play(brace.animate.become(Brace(token_rects[index], buff=0.05)))
            self.wait()

# Upstream: upstream/_2024/transformers/embedding.py:260-262
class DiscussTokenization(InteractiveScene):
    def construct(self):
        pass

# Upstream: upstream/_2024/transformers/embedding.py:265-296
class ImageTokens(InteractiveScene):
    n_divisions = 52

    def construct(self):
        # Add image
        image = ImageMobject("SmallFluffCreature")  # Change
        image.set_height(5)
        self.add(image)

        # Add pixels
        pixels = create_pixels(image, pixel_width=image.get_width() / self.n_divisions)
        big_pixels = create_pixels(image, pixel_width=image.get_width() / (self.n_divisions / 4))

        patches = big_pixels.copy().set_fill(opacity=0)
        p_points = np.array([p.get_center() for p in pixels])
        bp_points = np.array([bp.get_center() for bp in big_pixels])

        for pixel in pixels:
            dists = np.linalg.norm(bp_points - pixel.get_center(), axis=1)
            patches[np.argmin(dists)].add(pixel)

        # Anim test
        self.play(FadeIn(patches))
        self.remove(image)
        self.play(patches.animate.space_out_submobjects(2.0).scale(0.75))
        self.wait()
        self.play(LaggedStart(
            (patch.animate.set_stroke(TEAL, 3).set_anim_args(rate_func=there_and_back)
            for patch in patches),
            lag_ratio=5.0 / len(patches),
        ))
        self.wait()

# Upstream: upstream/_2024/transformers/embedding.py:299-338
class SoundTokens(InteractiveScene):
    def construct(self):
        # Add wave form
        n_lines = 100
        wave_form = Line(UP, DOWN).replicate(n_lines)
        wave_form.arrange(RIGHT)
        wave_form.arrange_to_fit_width(5)
        wave_form.next_to(ORIGIN, RIGHT)

        def func(x):
            x *= 1.7
            return sum([
                math.sin(x),
                0.5 * math.sin(2 * x),
                0.3 * math.sin(3 * x),
                0.2 * math.sin(4 * x),
                0.1 * math.sin(5 * x),
                0.15 * math.sin(6 * x),
            ])

        for line in wave_form:
            line.set_height(abs(func(line.get_x())))

        wave_form.center()
        self.add(wave_form)

        # Subdivide
        step = 5
        chunks = VGroup(wave_form[i:i + step] for i in range(0, len(wave_form), step))

        self.add(chunks)
        self.wait()
        self.play(chunks.animate.space_out_submobjects(2.0).scale(0.75))
        self.play(LaggedStart(
            (chunk.animate.set_stroke(TEAL, 3).scale(1.5).set_anim_args(rate_func=there_and_back)
            for chunk in chunks),
            lag_ratio=2.0 / len(chunks),
            run_time=2
        ))
        self.wait()

# Upstream: upstream/_2024/transformers/embedding.py:341-609
class IntroduceEmbeddingMatrix(InteractiveScene):
    def construct(self):
        # Load words
        words = [
            'aah',
            'aardvark',
            'aardwolf',
            'aargh',
            'ab',
            'aback',
            'abacterial',
            'abacus',
            'abalone',
            'abandon',
            'zygoid',
            'zygomatic',
            'zygomorphic',
            'zygosis',
            'zygote',
            'zygotic',
            'zyme',
            'zymogen',
            'zymosis',
            'zzz'
        ]

        # Get all words
        dots = Tex(R"\vdots")
        shown_words = VGroup(
            *map(Text, words[:10]),
            dots,
            *map(Text, words[-10:]),
        )
        shown_words.arrange(DOWN, aligned_edge=LEFT)
        dots.match_x(shown_words[:5])
        shown_words.set_height(FRAME_HEIGHT - 1)
        shown_words.move_to(LEFT)
        shown_words.set_fill(border_width=0)

        brace = Brace(shown_words, RIGHT)
        brace_text = brace.get_tex(R"\text{All words, } \sim 50\text{k}")

        self.play(
            LaggedStartMap(FadeIn, shown_words, shift=0.5 * LEFT, lag_ratio=0.1, run_time=2),
            GrowFromCenter(brace, time_span=(0.5, 2.0)),
            FadeIn(brace_text, time_span=(0.5, 1.5)),
        )
        self.wait()

        # Show embedding matrix
        dots_index = shown_words.submobjects.index(dots)
        matrix = WeightMatrix(
            shape=(10, len(shown_words)),
            ellipses_col=dots_index
        )
        matrix.set_width(13.5)
        matrix.center()
        columns = matrix.get_columns()

        matrix_name = Text("Embedding matrix", font_size=90)
        matrix_name.next_to(matrix, DOWN, buff=0.5)

        shown_words.target = shown_words.generate_target()
        shown_words.target.rotate(PI / 2)
        shown_words.target.next_to(matrix, UP)
        for word, column in zip(shown_words.target, columns):
            word.match_x(column)
            word.rotate(-45 * DEGREES, about_edge=DOWN)
        shown_words.target[dots_index].rotate(45 * DEGREES).move_to(
            shown_words.target[dots_index - 1:dots_index + 2]
        )
        new_brace = Brace(shown_words.target, UP, buff=0.0)
        column_rects = VGroup(*(
            SurroundingRectangle(column, buff=0.05)
            for column in columns
        ))
        column_rects.set_stroke(WHITE, 1)

        self.play(
            MoveToTarget(shown_words),
            brace.animate.become(new_brace),
            brace_text.animate.next_to(new_brace, UP, buff=0.1),
            LaggedStart(*(
                Write(column, lag_ratio=0.01, stroke_width=1)
                for column in columns
            ), lag_ratio=0.2, run_time=2),
            LaggedStartMap(FadeIn, matrix.get_brackets(), scale=0.5, lag_ratio=0)
        )
        self.play(Write(matrix_name, run_time=1))
        self.wait()

        # Show a few columns
        last_rect = VMobject()
        # for index in [9, -7, 7, -5, -6]:
        for index in range(len(columns)):
            for group in shown_words, columns:
                group.target = group.generate_target()
                group.target.set_opacity(0.2)
                group.target[index].set_opacity(1)
            rect = column_rects[index]
            self.play(
                *map(MoveToTarget, [shown_words, columns]),
                FadeIn(rect),
                FadeOut(last_rect),
            )
            last_rect = rect
            self.wait(0.5)
        self.play(
            FadeOut(last_rect),
            shown_words.animate.set_opacity(1),
            columns.animate.set_opacity(1),
        )

        # Label as W_E
        frame = self.frame
        lhs = Tex("W_E = ", font_size=90)
        lhs.next_to(matrix, LEFT)

        self.play(
            frame.animate.set_width(FRAME_WIDTH + 3, about_edge=RIGHT),
            Write(lhs)
        )
        self.wait()

        # Randomize entries
        rects = VGroup(*(
            SurroundingRectangle(entry).insert_n_curves(20)
            for entry in matrix.get_entries()
            if entry not in matrix.ellipses
        ))
        rects.set_stroke(WHITE, 1)
        for x in range(1):
            self.play(
                RandomizeMatrixEntries(matrix, lag_ratio=0.01),
                LaggedStartMap(VShowPassingFlash, rects, lag_ratio=0.01, time_width=1.5),
                run_time=2,
            )
        data_modifying_matrix(self, matrix)
        self.wait()

        # Highlight just one word
        matrix_group = VGroup(lhs, matrix, shown_words, matrix_name)
        index = words.index("aardvark")
        vector = VGroup(
            matrix.get_brackets()[0],
            matrix.get_columns()[index],
            matrix.get_brackets()[1],
        ).copy()
        vector.target = vector.generate_target()
        vector.target.arrange(RIGHT, buff=0.1)
        vector.target.set_height(4.5)
        vector.target.move_to(frame, DOWN).shift(0.5 * UP)
        vector.target.set_x(-3)

        word = shown_words[index].copy()
        word.target = word.generate_target()
        word.target.rotate(-45 * DEGREES)
        word.target.scale(3)
        word.target.next_to(vector.target, LEFT, buff=1.5)
        arrow = Arrow(word.target, vector.target)

        self.play(LaggedStart(
            matrix_group.animate.scale(0.5).next_to(frame.get_top(), DOWN, 0.5),
            FadeOut(brace, UP),
            FadeOut(brace_text, 0.5 * UP),
            MoveToTarget(word),
            MoveToTarget(vector),
            GrowFromPoint(arrow, word.get_center()),
        ), lag_ratio=0.15)
        self.wait()

        word_group = VGroup(word, arrow, vector)

        # Pull the matrix back up
        self.play(
            FadeOut(word_group, DOWN),
            matrix_group.animate.scale(2.0).move_to(frame)
        )

        # Have data fly across
        data_modifying_matrix(self, matrix, word_shape=(3, 10), alpha_maxes=(0.5, 0.9))
        self.wait()

        # Prep tokens
        encoding = get_token_encoding()
        n_vocab = encoding.n_vocab
        kw = dict(font_size=24)
        shown_tokens = VGroup(
            *(Text(encoding.decode([i]), **kw) for i in range(10)),
            shown_words[dots_index].copy().rotate(-45 * DEGREES),
            *(Text(encoding.decode([i]), **kw) for i in range(n_vocab - 10, n_vocab)),
        )
        for token, word in zip(shown_tokens, shown_words):
            token.rotate(45 * DEGREES)
            token.move_to(word, DL)
        shown_tokens[dots_index].move_to(
            shown_tokens[dots_index-1:dots_index + 2:2]
        )

        # Show dimensions
        top_brace = Brace(shown_words, UP)
        left_brace = Brace(matrix, LEFT, buff=SMALL_BUFF)
        vocab_count = Integer(50257)
        vocab_label = VGroup(vocab_count, Text("words"))
        vocab_label.arrange(RIGHT, aligned_edge=UP)
        vocab_label.next_to(top_brace, UP, SMALL_BUFF)
        token_label = Text("tokens", fill_color=YELLOW)
        token_label.move_to(vocab_label[1], LEFT)

        dim_count = Integer(12288)
        dim_count.next_to(left_brace, LEFT, SMALL_BUFF)

        self.play(
            GrowFromCenter(top_brace),
            CountInFrom(vocab_count, 0),
            FadeIn(vocab_label[1]),
        )
        self.wait()
        self.play(
            FadeOut(vocab_label[1], 0.5 * UP),
            FadeIn(token_label, 0.5 * UP),
            LaggedStartMap(FadeOut, shown_words, shift=0.25 * UP, lag_ratio=0.1),
            LaggedStartMap(FadeIn, shown_tokens, shift=0.25 * UP, lag_ratio=0.1),
        )
        self.wait()

        matrix_name.target = matrix_name.generate_target()
        matrix_name.target.shift(RIGHT)
        self.play(
            MoveToTarget(matrix_name),
            lhs.animate.next_to(matrix_name.target, LEFT),
            GrowFromCenter(left_brace),
            CountInFrom(dim_count, 0),
        )
        self.play(FlashAround(dim_count))
        self.wait()

        # Count total parameters
        matrix_group = VGroup(
            top_brace, vocab_count,
            left_brace, dim_count,
            matrix, shown_words, matrix_name, lhs
        )

        top_equation = VGroup(
            Text("Total parameters = "),
            dim_count.copy(),
            Tex(R"\times"),
            vocab_count.copy(),
            Tex("="),
            Integer(vocab_count.get_value() * dim_count.get_value()).set_color(YELLOW),
        )
        top_equation.arrange(RIGHT)
        top_equation.set_height(0.5)
        top_equation.next_to(matrix_group, UP, buff=1.0)
        result_rect = SurroundingRectangle(top_equation[-1])
        result_rect.set_stroke(YELLOW, 2)

        self.play(
            LaggedStartMap(FadeIn, top_equation[::2], shift=0.25 * UP, lag_ratio=0.5),
            TransformFromCopy(dim_count, top_equation[1]),
            TransformFromCopy(vocab_count, top_equation[3]),
            frame.animate.set_height(11).move_to(matrix_group, DOWN).shift(DOWN),
        )
        self.play(FadeTransform(
            top_equation[1:5:2].copy(), top_equation[-1]
        ))
        self.play(ShowCreation(result_rect))
        self.wait()

# Upstream: upstream/_2024/transformers/embedding.py:612-693
class Word2VecScene(InteractiveScene):
    default_frame_orientation = (-30, 70)

    axes_config = dict(
        x_range=(-5, 5, 1),
        y_range=(-5, 5, 1),
        z_range=(-4, 4, 1),
        width=8,
        height=8,
        depth=6.4,
    )
    label_rotation = PI / 2
    # embedding_model = "word2vec-google-news-300"
    embedding_model = "glove-wiki-gigaword-50"

    def setup(self):
        super().setup()

        # Load model
        self.model = get_word_to_vec_model(self.embedding_model)

        # Decide on basis
        self.basis = self.get_basis(self.model)

        # Add axes
        self.axes = ThreeDAxes(**self.axes_config)
        self.add(self.axes)

    def get_basis(self, model):
        return get_principle_components(model.vectors, 3).T

    def add_plane(self, color=GREY, stroke_width=1.0):
        axes = self.axes
        plane = NumberPlane(
            axes.x_range, axes.y_range,
            width=axes.get_width(),
            height=axes.get_height(),
            background_line_style=dict(
                stroke_color=color,
                stroke_width=stroke_width,
            ),
            faded_line_style=dict(
                stroke_opacity=0.25,
                stroke_width=0.5 * stroke_width,
            ),
            faded_line_ratio=1,
        )
        self.plane = plane
        self.add(plane)
        return plane

    def get_labeled_vector(
        self,
        word,
        coords=None,
        thickness=5,
        color=YELLOW,
        func_name: str | None = "E",
        buff=0.05,
        direction=None,
        label_config: dict = dict()
    ):
        # Return an arrow with word label next to it
        axes = self.axes
        if coords is None:
            coords = self.basis @ self.model[word.lower()]
        point = axes.c2p(*coords)
        label_config.update(label_buff=buff)
        if "label_rotation" not in label_config:
            label_config.update(label_rotation=self.label_rotation)
        arrow = LabeledArrow(
            axes.get_origin(),
            point,
            thickness=thickness,
            fill_color=color,
            label_text=word if func_name is None else f"{func_name}({word})",
            buff=0,
            direction=direction,
            **label_config,
        )
        arrow.always.set_perpendicular_to_camera(self.frame)
        return arrow

# Upstream: upstream/_2024/transformers/embedding.py:696-775
class AmbientWordEmbedding(Word2VecScene):
    def construct(self):
        # Setup
        frame = self.frame
        frame.reorient(-30, 82, 0)
        frame.add_ambient_rotation(3 * DEGREES)

        axes = self.axes
        axes.set_stroke(width=2)
        axes.set_height(7)
        axes.move_to(0.2 * FRAME_WIDTH * RIGHT + 1.0 * IN)

        # Add titles
        titles = VGroup(Text("Words"), Text("Vectors"))
        colors = [YELLOW, BLUE]
        titles.set_height(0.5)
        xs = [-4.0, axes.get_x()]
        for title, x, color in zip(titles, xs, colors):
            title.move_to(x * RIGHT)
            title.to_edge(UP)
            title.add(Underline(title))
            title.fix_in_frame()
            title.set_color(color)

        arrow = Arrow(titles[0], titles[1], buff=0.5)
        arrow.fix_in_frame()

        arrow_label = TexText("``Embedding''")
        arrow_label.set_submobject_colors_by_gradient(YELLOW, BLUE)
        arrow_label.next_to(arrow, UP, SMALL_BUFF)
        arrow_label.fix_in_frame()

        self.add(titles)
        self.add(arrow)

        # Add words
        words = "All data in deep learning must be represented as vectors".split(" ")
        pre_labels = VGroup(*(Text(word) for word in words))
        pre_labels.fix_in_frame()
        pre_labels.arrange(DOWN, aligned_edge=LEFT)
        pre_labels.next_to(titles[0], DOWN, buff=0.5)
        pre_labels.align_to(titles[0][0], LEFT)
        pre_labels.set_backstroke()

        coords = np.array([
            self.basis @ self.model[word.lower()]
            for word in words
        ])
        coords -= coords.mean(0)
        max_coord = max(coords.max(), -coords.min())
        coords *= 4.0 / max_coord

        embeddings = VGroup(*(
            self.get_labeled_vector(
                word,
                coord,
                stroke_width=2,
                color=interpolate_color(BLUE_D, BLUE_A, random.random()),
                func_name=None,
                label_config=dict(font_size=24)
            )
            for word, coord in zip(words, coords)
        ))

        self.play(LaggedStartMap(FadeIn, pre_labels, shift=0.2 * UP, lag_ratio=0.1, run_time=1))

        # Transition
        self.add(turn_animation_into_updater(
            Write(arrow_label, time_span=(1, 3))
        ))
        for label, vect in zip(pre_labels, embeddings):
            self.add(turn_animation_into_updater(
                TransformFromCopy(label, vect.label, run_time=2)
            ))
            self.add(turn_animation_into_updater(
                FadeIn(vect, run_time=1)
            ))
            self.wait(0.5)
        self.play(FlashAround(arrow_label, time_width=1.5, run_time=3))
        self.wait(15)

# Upstream: upstream/_2024/transformers/embedding.py:778-903
class ThreeDSpaceExample(InteractiveScene):
    def construct(self):
        # Set up axes
        frame = self.frame
        frame.reorient(-15, 78, 0, (1.07, 1.71, 1.41), 6.72)
        frame.add_ambient_rotation(1 * DEGREES)
        axes = ThreeDAxes((-5, 5), (-5, 5), (-4, 4))
        plane = NumberPlane((-5, 5), (-5, 5))
        plane.fade(0.5)

        self.add(plane)
        self.add(axes)

        # Show coordiantes creating directions
        x, y, z = coordinates = np.array([3, 1, 2])
        colors = [RED, GREEN, BLUE]

        coords = DecimalMatrix(np.zeros((3, 1)), num_decimal_places=1)
        coords.fix_in_frame()
        coords.to_corner(UR)
        coords.shift(1.5 * LEFT)
        coords.get_entries().set_submobject_colors_by_gradient(*colors)

        lines = VGroup(
            Line(axes.c2p(0, 0, 0), axes.c2p(x, 0, 0)),
            Line(axes.c2p(x, 0, 0), axes.c2p(x, y, 0)),
            Line(axes.c2p(x, y, 0), axes.c2p(x, y, z)),
        )
        lines.set_flat_stroke(False)
        lines.set_submobject_colors_by_gradient(*colors)
        labels = VGroup(*map(Tex, "xyz"))
        labels.rotate(89 * DEGREES, RIGHT)
        directions = [OUT, OUT + RIGHT, RIGHT]
        for label, line, direction in zip(labels, lines, directions):
            label.next_to(line, direction, buff=SMALL_BUFF)
            label.match_color(line)

        dot = GlowDot(color=WHITE)
        dot.move_to(axes.get_origin())

        vect = Arrow(axes.get_origin(), axes.c2p(x, y, z), buff=0)
        vect.set_flat_stroke(False)

        self.add(coords)
        for entry, line, label, value in zip(coords.get_entries(), lines, labels, coordinates):
            rect = SurroundingRectangle(entry)
            rect.set_fill(line.get_color(), 0.3)
            rect.set_stroke(line.get_color(), width=2)
            self.play(
                ShowCreation(line),
                FadeInFromPoint(label, line.get_start()),
                VFadeInThenOut(rect),
                ChangeDecimalToValue(entry, value),
                dot.animate.move_to(line.get_end()),
            )
            self.wait(0.5)
        self.play(ShowCreation(vect))

        # Wait for a bit
        self.wait(15)

        # Show many points
        points = GlowDots(np.random.uniform(-3, 3, size=(50, 3)), radius=0.1)
        frame.clear_updaters()
        self.play(
            FadeOut(coords),
            FadeOut(dot),
            FadeOut(plane),
            LaggedStartMap(FadeOut, VGroup(*lines, vect, *labels)),
            frame.animate.reorient(-81, 61, 0, (-0.82, 0.6, 0.36), 8.95),
            ShowCreation(points),
            run_time=2,
        )
        frame.add_ambient_rotation(5 * DEGREES)
        self.wait(2)

        # Take a 2d slice
        plane = Square3D()
        plane.set_height(10)
        plane.set_color([GREY_E, GREY_C])
        plane.set_opacity(0.25)
        grid = NumberPlane(
            (-5, 5), (-5, 5),
            background_line_style=dict(stroke_color=GREY_B, stroke_width=1),
            faded_line_ratio=0,
        )
        grid.axes.match_style(grid.background_lines)
        grid.match_height(plane)
        plane_group = Group(plane, grid)
        plane_group.rotate(60 * DEGREES, UR)

        bases = [
            normalize(point)
            for point in plane.get_points()[:2]
        ]

        def project(points):
            return np.array([
                sum(np.dot(point, b) * b for b in bases)
                for point in points
            ])

        projected_points = points.copy()
        projected_points.apply_points_function(project)

        projection_lines = VGroup(*(
            Line(p1, p2)
            for p1, p2 in zip(points.get_points(), projected_points.get_points())
        ))
        projection_lines.set_stroke()

        self.play(ShowCreation(plane), Write(grid, lag_ratio=0.01, stroke_width=1))
        self.wait(2)
        self.play(
            axes.animate.set_stroke(opacity=0.25),
            points.animate.set_opacity(0.5),
            TransformFromCopy(points, projected_points),
            ShowCreation(projection_lines, lag_ratio=0.05),
            run_time=3
        )
        self.play(
            FadeOut(points),
            FadeOut(projection_lines),
            FadeOut(axes)
        )
        self.wait(15)

# Upstream: upstream/_2024/transformers/embedding.py:906-1016
class HighDimensionalSpaceCompanion(InteractiveScene):
    def construct(self):
        # Vector example
        word = Text("bank")
        vect = WeightMatrix(shape=(8, 1))
        vect.next_to(word, RIGHT, buff=LARGE_BUFF)
        vect.set_height(3)
        arrow = Arrow(word, vect)
        group = VGroup(word, arrow, vect)
        group.move_to(RIGHT)
        group.to_edge(UP, buff=0.1)
        self.add(group)

        # Draw vague embedding space
        bubble_center = np.array([0.5, -2.25, 0])
        base_bubble: VMobject = OldThoughtBubble()[-2][-1]
        base_bubble.set_shape(8, 7)
        base_bubble.rotate(PI)
        base_bubble.set_fill(GREY_D, opacity=[0.25, 1, 0.25])
        base_bubble.move_to(bubble_center)
        bubble_label = Text("Word vector space", font_size=60)
        bubble_label.move_to(base_bubble)
        bubble_label.shift(2.0 * UP)
        # bubble_label = Text("Embedding space", font_size=72)
        q_marks = Tex("???", font_size=120)
        q_marks.next_to(bubble_label, DOWN, buff=0.5)
        base_bubble.add(bubble_label, q_marks)

        def get_bubble():
            result = base_bubble.copy()
            result.apply_complex_function(
                lambda z: z * (1 + 0.025 * np.cos(5 * np.log(z).imag + self.time))
            )
            result.move_to(bubble_center)
            return result

        bubble = always_redraw(get_bubble)
        self.add(bubble)
        self.wait(10)

        # Show dimension
        brace = Brace(vect, RIGHT)
        label = VGroup(
            # Integer(12288),
            Integer(10000),
            Text("coordinates")
        )
        label.arrange(DOWN, aligned_edge=LEFT)
        label.set_height(1)
        label.set_color(YELLOW)
        label.next_to(brace, RIGHT)

        dimension_label = VGroup(
            label[0].copy(),
            Text("-dimensional")
        )
        dimension_label.arrange(RIGHT, buff=0.05, aligned_edge=UP)
        dimension_label.match_height(bubble_label).scale(0.8)
        dimension_label.set_color(YELLOW)
        dimension_label.next_to(q_marks, DOWN, buff=0.5)

        self.play(
            GrowFromCenter(brace),
            CountInFrom(label[0], 0),
            FadeIn(label[1]),
        )
        self.wait()
        self.play(
            TransformFromCopy(label[0], dimension_label[0]),
            FadeInFromPoint(dimension_label[1], label[0].get_center()),
        )
        self.remove(dimension_label)
        bubble_label.add(*dimension_label)

        self.wait(10)

        # Show 3d slice
        axes = ThreeDAxes()
        axes.rotate(20 * DEGREES, OUT)
        axes.rotate(80 * DEGREES, LEFT)
        axes.set_height(3)
        axes.move_to(bubble)
        axes.shift(0.5 * RIGHT)
        axes_label = TexText("3d ``slice''")
        axes_label.next_to(axes, RIGHT)
        axes_label.shift(0.35 * DOWN + 1.5 * LEFT)

        self.play(
            bubble_label.animate.scale(0.5).shift(1.2 * UP + 1.5 * LEFT),
            FadeOut(q_marks),
            Write(axes, lag_ratio=0.01),
            Write(axes_label)
        )
        self.wait(2)

        # Show some vector projections
        vectors = VGroup(*(
            Arrow(
                axes.get_origin(),
                axes.c2p(*np.random.uniform(-3, 3, 3)),
                buff=0,
                stroke_color=random_bright_color(hue_range=(0.55, 0.65))
            )
            for x in range(5)
        ))
        vectors.set_flat_stroke(False)

        self.play(LaggedStartMap(FadeIn, vectors, scale=0.5, lag_ratio=0.3))
        z_direction = axes.z_axis.get_vector()
        axes.add(vectors)
        self.play(Rotate(axes, -200 * DEGREES, axis=z_direction, run_time=10))

# Upstream: upstream/_2024/transformers/embedding.py:1019-1104
class LearningEmbeddings(Word2VecScene):
    def construct(self):
        # Setup
        self.add_plane()
        axes = self.axes
        plane = self.plane
        frame = self.frame
        frame.reorient(0, 90, 0)

        # Get sample words
        # phrase = "The first big idea is that as a model tweaks and tunes its weights"
        # phrase = "The big idea as a model tweaks and tunes its weights"
        phrase = "Features can be encoded with directions in a big space"
        words = [word.lower() for word in phrase.split(" ")]

        # Get initial and final states
        colors = [random_bright_color(hue_range=(0.5, 0.6)) for word in words]
        true_embeddings = np.array([
            self.basis @ self.model[word]
            for word in words
        ])
        true_embeddings -= true_embeddings.mean(0)
        true_embeddings *= 5 / np.abs(true_embeddings).max(0)

        np.random.seed(2)
        thetas = np.arange(0, TAU, TAU / len(words))
        thetas += np.random.uniform(-0.5, 0.5, thetas.size)
        amps = np.random.uniform(3, 5, thetas.size)
        initial_coords = [
            rotate_vector(amp * OUT, theta, axis=UP)
            for theta, amp in zip(thetas, amps)
        ]

        # Create word vectors
        word_vects = VGroup(*(
            self.get_labeled_vector(
                word,
                coords=coords,
                color=color,
                buff=0.05,
                func_name=None,
                label_config=dict(font_size=36)
            )
            for word, color, coords in zip(words, colors, initial_coords)
        ))
        labels = VGroup()
        for vect in word_vects:
            label = vect.label
            label.set_backstroke(BLACK, 3)
            label.vect = vect
            label.add_updater(lambda m: m.move_to(
                m.vect.get_end() + 0.25 * normalize(m.vect.get_vector())
            ))
            labels.add(label)

        self.play(
            LaggedStartMap(GrowArrow, word_vects, lag_ratio=0.2),
            LaggedStartMap(FadeIn, labels, lag_ratio=0.2),
            run_time=4
        )
        self.wait()

        # Tweak and tune weights
        turn_animation_into_updater(
            ApplyMethod(frame.reorient, 4, 72, 0, (-0.04, -0.18, -0.5), 8.00),
            run_time=8
        )
        self.progressive_nudges(word_vects, true_embeddings, 8)
        frame.clear_updaters()
        turn_animation_into_updater(
            ApplyMethod(frame.reorient, 38, 69, 0, (-0.32, 0.02, -0.54), 7.68),
            run_time=12
        )
        self.progressive_nudges(word_vects, true_embeddings, 12)

    def progressive_nudges(self, word_vects, true_embeddings, n_nudges, step_size=0.2):
        for x in range(n_nudges):
            anims = [
                vect.animate.put_start_and_end_on(
                    self.axes.get_origin(),
                    interpolate(vect.get_end(), self.axes.c2p(*embedding), step_size)
                )
                for vect, embedding in zip(word_vects, true_embeddings)
            ]
            self.play(*anims, run_time=0.5)
            self.wait(0.5)

# Upstream: upstream/_2024/transformers/embedding.py:1107-1382
class KingQueenExample(Word2VecScene):
    default_frame_orientation = (20, 70)

    def get_basis(self, model):
        basis = super().get_basis(model)
        basis[1] *= 2
        return basis

    def construct(self):
        # Axes and frame
        axes = self.axes
        frame = self.frame
        self.add_plane()
        self.plane.rotate(90 * DEGREES, LEFT)
        frame.reorient(-178, 9, 178, (2.15, 1.12, 0.56), 6.84)

        # Initial word vectors
        words = ["man", "woman", "king", "queen"]
        colors = [BLUE_B, RED_B, BLUE_D, RED_D]
        directions = [UR, RIGHT, UR, LEFT]
        all_coords = np.array([self.basis @ self.model[word] for word in words])
        all_coords[:2] += DOWN
        all_coords[2:] += 4 * LEFT + 1 * DOWN + IN

        label_config = dict(
            font_size=30,
            label_rotation=0,
        )
        man, woman, king, queen = word_vects = [
            self.get_labeled_vector(
                word,
                coords=coords,
                color=color,
                buff=0.05,
                direction=direction,
                label_config=label_config,
            )
            for word, color, direction, coords in zip(words, colors, directions, all_coords)
        ]
        woman.label.shift(SMALL_BUFF * DOWN)

        fake_queen_coords = all_coords[2] - all_coords[0] + all_coords[1]  # Tweak queen for demo purposes
        fake_queen = self.get_labeled_vector(
            "queen", fake_queen_coords,
            color=colors[3],
            label_config=label_config,
        )
        fake_queen.label.shift(0.1 * LEFT + 0.2 * DOWN)

        # Equation
        equation = self.get_equation1("queen", "king", "woman", "man")
        equation.set_x(0)
        eq, minus1, ek, approx, ew, minus2, em = equation
        top_rect = FullScreenFadeRectangle().set_fill(BLACK, 1)
        top_rect.set_height(1.5, about_edge=UP, stretch=True)
        top_rect.fix_in_frame()

        for part, vect in zip([em, ew, ek, eq], word_vects):
            part.set_fill(vect.get_color())

        # Show man and woman vectors
        diff = Arrow(man.get_end(), woman.get_end(), buff=0, stroke_color=YELLOW)
        diff.set_fill(YELLOW, opacity=0.8)
        diff.set_backstroke(BLACK, 3)
        self.play(
            LaggedStart(*map(Write, [ew, minus2, em])),
            GrowArrow(woman),
            FadeInFromPoint(woman.label, man.get_center()),
            GrowArrow(man),
            FadeInFromPoint(man.label, man.get_center()),
            frame.animate.reorient(0, 0, 0, (2.04, 2.06, 0.38), 4.76).set_anim_args(run_time=6)
        )
        self.play(
            GrowArrow(diff, time_span=(1, 3)),
            frame.animate.reorient(-179, 19, 179, (2.49, 1.96, 0.4), 4.76),
            run_time=5
        )

        # Show king and fake queen
        self.add(top_rect, *equation)
        new_diff = diff.copy()
        new_diff.shift(king.get_end() - man.get_end())

        self.play(
            FadeIn(top_rect),
            *map(Write, [eq, minus1, ek, approx]),
            LaggedStart(
                TransformFromCopy(man, king),
                TransformFromCopy(man.label, king.label),
                TransformFromCopy(woman, fake_queen),
                TransformFromCopy(woman.label, fake_queen.label),
            ),
            TransformFromCopy(diff, new_diff, time_span=(2, 3)),
            frame.animate.reorient(0, 2, 0, (0.04, 1.96, -0.13), 5.51).set_anim_args(run_time=3)
        )
        self.play(
            frame.animate.reorient(-110, 10, 110, (0.22, 1.6, -0.07), 6.72),
            run_time=10
        )

        # Rearrange the equation
        for mob in [ek, approx]:
            mob.target = mob.generate_target()
        approx.target.move_to(minus1, LEFT)
        ek.target.next_to(approx.target, RIGHT)
        minus1.target = Tex("+").next_to(ek.target, RIGHT, SMALL_BUFF)
        minus1.target.move_to(midpoint(ek.target.get_right(), ew.get_left()))
        minus1.target.fix_in_frame()

        self.play(
            FadeOut(fake_queen),
            FadeOut(fake_queen.label),
            FadeOut(new_diff),
        )
        self.play(
            LaggedStartMap(MoveToTarget, [minus1, ek, approx], path_arc=PI / 2)
        )
        self.play(FlashAround(VGroup(ek, em), run_time=3, time_width=1.5))
        self.play(TransformFromCopy(diff, new_diff))

        # Search near tip
        n_circs = 5
        src_circles = Circle(radius=1e-2).set_stroke(width=5, opacity=1).replicate(n_circs)
        trg_circles = Circle(radius=1).set_stroke(width=0, opacity=1).replicate(n_circs)
        circs = VGroup(src_circles, trg_circles)
        circs.set_stroke(WHITE)
        circs.move_to(new_diff.get_end())
        self.play(
            LaggedStart(*(
                Transform(src, trg)
                for src, trg in zip(src_circles, trg_circles)
            ), lag_ratio=0.15, run_time=3)
        )
        self.play(
            FadeIn(fake_queen),
            FadeIn(fake_queen.label),
        )
        self.wait()

        # Correct it
        self.play(
            TransformFromCopy(fake_queen, queen),
            TransformFromCopy(fake_queen.label, queen.label),
            VGroup(fake_queen, fake_queen.label).animate.set_opacity(0.2),
        )
        self.play(
            FadeOut(fake_queen),
            FadeOut(fake_queen.label),
            frame.animate.reorient(103, 9, -101, (0.01, 1.45, 0.07), 6.72),
            run_time=10
        )

        # Show a few other examples
        word_pairs = [
            ("uncle", "aunt"),
            ("brother", "sister"),
            ("nephew", "niece"),
            ("father", "mother"),
            ("son", "daughter"),
        ]
        turn_animation_into_updater(
            ApplyMethod(frame.reorient, -116, 21, 114, (0.37, 1.45, 0.23), 7.59, run_time=12)
        )

        last_group = VGroup(king, queen, king.label, queen.label, new_diff)
        last_equation = equation
        for word1, word2 in word_pairs:
            new_coords = np.array([self.basis @ self.model[w] for w in [word1, word2]])
            adj_point = np.array([
                np.random.uniform(-5, 0),
                np.random.uniform(2, 4),
                np.random.uniform(-3, 3),
            ])
            new_coords += (adj_point - new_coords[0])
            vect1 = self.get_labeled_vector(word1, color=colors[2], label_config=label_config, coords=new_coords[0])
            vect2 = self.get_labeled_vector(word2, color=colors[3], label_config=label_config, coords=new_coords[1])
            vect2.put_start_and_end_on(ORIGIN, vect1.get_end() + diff.get_vector() + np.random.uniform(-0.1, 0.1, 3))
            vect2.label.next_to(vect2.get_end(), LEFT)

            new_equation = self.get_equation1(word2, word1, "woman", "man")
            new_equation.move_to(equation, RIGHT)
            new_equation.match_style(equation)
            new_equation.set_fill(opacity=1)
            new_equation.fix_in_frame()

            diff_copy = diff.copy()
            diff_copy.shift(vect1.get_end() - diff_copy.get_start())

            self.play(
                LaggedStart(
                    FadeOut(last_group),
                    GrowArrow(vect1),
                    FadeIn(vect1.label),
                    GrowArrow(vect2),
                    FadeIn(vect2.label),
                ),
                *(
                    FadeTransform(sm1, sm2)
                    for sm1, sm2 in zip(last_equation, new_equation)
                ),
            )
            self.play(TransformFromCopy(diff, diff_copy))
            self.wait(2)

            last_equation = new_equation
            last_group = VGroup(vect1, vect2, vect1.label, vect2.label, diff_copy)
        self.wait(4)

        # Flash in direction
        vect = diff.get_vector()
        color = YELLOW
        lines = Line(ORIGIN, 2 * normalize(vect)).replicate(200)
        lines.insert_n_curves(20)
        lines.set_stroke(color, 3)
        for line in lines:
            line.move_to(np.random.uniform(-3, 3, 3))
        self.play(
            LaggedStartMap(
                VShowPassingFlash, lines,
                lag_ratio=1 / len(lines),
                run_time=4
            )
        )

    def get_labeled_vector(self, *args, **kwargs):
        kwargs.update(func_name = None)
        kwargs.update(thickness=3)
        return super().get_labeled_vector(*args, **kwargs)

    def get_equation1(self, word1, word2, word3, word4, colors=None):
        equation = TexText(
            # Rf"E({word1}) - E({word2}) $\approx$ E({word3}) - E({word4})",
            Rf"{{{word1}}} - {{{word2}}} $\approx$ {{{word3}}} - {{{word4}}}",
            font_size=48
        )
        equation.fix_in_frame(True)
        equation.to_corner(UR)
        if colors:
            words = [word1, word2, word3, word4]
            for word, color in zip(words, colors):
                equation[word].set_fill(color)
        pieces = VGroup(
            equation[f"{{{word1}}}"][0],
            equation["-"][0],
            equation[f"{{{word2}}}"][0],
            equation[R"$\approx$"][0],
            equation[f"{{{word3}}}"][0],
            equation["-"][1],
            equation[f"{{{word4}}}"][0],
        )
        pieces.fix_in_frame(True)
        return pieces

    def get_equation2(self, word1, word2, word3, word4, colors=None):
        equation = TexText(
            # Rf"E({word1}) + E({word2}) - E({word3}) $\approx$ E({word4})",
            Rf"{{{word1}}} + {{{word2}}} - {{{word3}}} $\approx$ {{{word4}}}",
            font_size=48
        )
        equation.fix_in_frame(True)
        equation.to_corner(UR)
        if colors:
            words = [word1, word2, word3, word4]
            for word, color in zip(words, colors):
                equation[word].set_fill(color)
        pieces = VGroup(
            equation[f"{{{word1}}}"],
            equation["+"],
            equation[f"{{{word2}}}"],
            equation["-"],
            equation[f"{{{word3}}}"],
            equation[R"$\approx$ "],
            equation[f"{{{word4}}}"],
        )
        pieces.fix_in_frame(True)
        return pieces

# Upstream: upstream/_2024/transformers/embedding.py:1385-1492
class HitlerMussoliniExample(KingQueenExample):
    words = ["Hitler", "Italy", "Germany", "Mussolini"]
    colors = [GREY_C, "#008C45", "#FFCC00", GREY_B]
    default_frame_orientation = (-17, 75, 0)
    second_frame_orientation = (-24, 66, 0)
    interpolation_factor = 0.2
    diff_color = RED_B

    def get_basis(self, model):
        v1, v2, v3, v4 = [model[word.lower()] for word in self.words]
        b1 = normalize(v2 - v3)
        b2 = normalize(v1 - v3)
        b3 = normalize(get_principle_components(model.vectors)[:, 0])
        return np.array([b1, b2, b3])

    def construct(self):
        # Set up
        frame = self.frame
        frame.move_to(1.0 * UP)
        frame.add_updater(lambda f, dt: f.increment_theta(dt * 1 * DEGREES))
        axes = self.axes

        # Add equation
        equation = self.get_equation2(*self.words, colors=self.colors)
        equation.center().to_edge(UP)
        self.add(equation[:-1])

        # Initialize vectors
        v1, v2, v3, v4 = vects = [
            self.get_labeled_vector(word, color=color)
            for word, color in zip(self.words, self.colors)
        ]
        fudged_v4 = self.get_labeled_vector(
            self.words[3],
            axes.p2c(interpolate(
                v1.get_end() + v2.get_end() - v3.get_end(),
                v4.get_end(),
                self.interpolation_factor,
            )),
            color=self.colors[3]
        )
        vects[3] = fudged_v4
        for vect in vects:
            vect.apply_depth_test()

        # Show (v3 - v2) difference
        diff = Arrow(
            v3.get_end(), v2.get_end(),
            buff=0,
            stroke_color=self.diff_color,
            stroke_width=2,
            flat_stroke=False,
        )
        diff.apply_depth_test()
        rect = SurroundingRectangle(equation[2:5])
        rect.set_stroke(diff.get_stroke_color(), 2)
        self.play(
            GrowArrow(v2),
            GrowArrow(v3),
            FadeIn(v2.label),
            FadeIn(v3.label),
        )
        self.play(
            ShowCreation(rect),
            Transform(v3.copy(), v2, remover=True),
            ShowCreation(diff)
        )
        self.wait(2)

        # Add to v1
        diff_copy = diff.copy()
        diff_copy.shift(v1.get_end() - diff.get_start())

        self.play(
            GrowArrow(v1),
            FadeIn(v1.label),
            frame.animate.reorient(*self.second_frame_orientation),
        )
        self.play(
            TransformFromCopy(diff, diff_copy),
            rect.animate.surround(equation[:5])
        )
        self.wait(2)
        self.play(
            rect.animate.surround(equation[-1]),
            FadeIn(equation[-1]),
            GrowArrow(fudged_v4),
            FadeIn(fudged_v4.label),
        )
        self.play(FadeOut(rect))
        self.wait(6)

        # Emphasize directions
        italy_vect = diff.get_vector()
        axis_vect = v1.get_end() - v3.get_end()
        for vect, color in [(italy_vect, RED), (axis_vect, GREY)]:
            lines = Line(ORIGIN, 2 * normalize(vect)).replicate(200)
            lines.insert_n_curves(20)
            lines.set_stroke(color, 3)
            for line in lines:
                line.move_to(np.random.uniform(-3, 3, 3))
            self.play(
                LaggedStartMap(
                    VShowPassingFlash, lines,
                    lag_ratio=1 / len(lines),
                    run_time=4
                )
            )

# Upstream: upstream/_2024/transformers/embedding.py:1495-1508
class SushiBratwurstExample(HitlerMussoliniExample):
    words = ["Sushi", "Germany", "Japan", "Bratwurst"]
    colors = [WHITE, "#FFCC00", "#BC002D", interpolate_color(GREY_BROWN, WHITE, 0.25)]
    interpolation_factor = -0.1
    default_frame_orientation = (-17, 80, 0)
    second_frame_orientation = (-24, 75, 0)
    diff_color = GREY_B

    def get_basis(self, model):
        basis = super().get_basis(model)
        basis = basis[[1, 2, 0]]
        basis[1] /= -2
        basis[2] /= 3
        return basis

# Upstream: upstream/_2024/transformers/embedding.py:1511-1566
class SizeDirection(Word2VecScene):
    def construct(self):
        # To illustrate "You could imagine many other directions in this space corresponding to semantic meaning"

        # Set up axes
        axes = self.axes
        frame = self.frame
        self.basis *= 1.5

        # Add vectors
        frame.reorient(35, 80, 0)
        colors = [BLUE_B, BLUE_C, BLUE_D]
        word_lists = [
            ["micrometer", "millimeter", "meter"],
            ["microgram", "milligram", "gram"],
            ["microliter", "milliliter", "liter"],
        ]
        vect_groups = VGroup(
            VGroup(
                self.get_labeled_vector(word, color=color, func_name=None)
                for word, color in zip(word_list, colors)
            )
            for word_list in word_lists
        )

        over_arrow = Arrow(2 * LEFT, 2 * RIGHT).shift(UP)
        over_arrow.set_stroke(YELLOW, width=10)
        over_words = Text("Size", font_size=72)
        over_words.set_color(YELLOW)
        over_words.set_backstroke(BLACK, 5)
        over_words.next_to(over_arrow, UP)
        annotation = VGroup(over_arrow, over_words)
        annotation.shift(LEFT)
        annotation.fix_in_frame()

        for vect_group in vect_groups:
            vect_group.labels = VGroup()
            for vect in vect_group:
                vect.label.rotate(45 * DEGREES, OUT)
                vect.label.next_to(vect.get_end(), normalize(vect.get_vector()), SMALL_BUFF)
                vect_group.labels.add(vect.label)

        self.play(
            frame.animate.reorient(49, 87, 0),
            LaggedStartMap(FadeIn, vect_groups[0], lag_ratio=0.25),
            LaggedStartMap(FadeIn, vect_groups[0].labels, lag_ratio=0.25),
            FadeIn(annotation, lag_ratio=0.1, time_span=(2, 3)),
            run_time=3
        )
        self.wait()
        for i in [0, 1]:
            self.play(
                ReplacementTransform(vect_groups[i], vect_groups[i + 1]),
                ReplacementTransform(vect_groups[i].labels, vect_groups[i + 1].labels),
            )
            self.wait()

# Upstream: upstream/_2024/transformers/embedding.py:1569-1598
class PluralityDirection(Word2VecScene):
    def construct(self):
        self.add_plane()
        self.axes.x_axis.set_stroke(opacity=0)
        self.axes.y_axis.set_stroke(opacity=0)

        # Test
        self.frame.reorient(-21, 77, 0, (1.97, -0.73, 0.54), 3.67)
        self.frame.add_updater(lambda m, dt: m.increment_theta(dt * DEGREES))
        words = ["cat", "cats"]
        all_coords = 2 * np.array([self.basis @ self.model[word] for word in words])
        colors = [BLUE, RED]
        cat, cats = [
            self.get_labeled_vector(
                word,
                coords=coords,
                color=color,
                buff=0.05,
            )
            for word, color, coords in zip(words, colors, all_coords)
        ]
        diff = Arrow(cat.get_end(), cats.get_end(), buff=0)
        diff.set_color(YELLOW)

        self.add(cat, cats)
        self.add(cat.label, cats.label)

        self.wait(5)
        self.play(ShowCreation(diff))
        self.wait(10)

# Upstream: upstream/_2024/transformers/embedding.py:1601-1691
class ShowNearestNeighbors(Word2VecScene):
    seed_word = "tower"
    color = YELLOW
    n_shown = 10
    frame_height = 4
    frame_center = (2.18, 0.09, 0.72)
    frame_orientation = (-21, 87, 0)
    wait_time_per_example = 0.5

    def construct(self):
        # Setup
        frame = self.frame
        frame.reorient(*self.frame_orientation, self.frame_center, self.frame_height)
        frame.add_updater(lambda f, dt: f.increment_theta(dt * DEGREES))
        self.add_plane()

        # Add seed
        word = self.seed_word.lower()
        seed_vect = self.get_labeled_vector(word, color=self.color)
        seed_group = VGroup(seed_vect, seed_vect.label)
        self.add(seed_group)

        # Add neighbors
        nearest_words = self.get_nearest_words(word)
        neighbors = VGroup(*(
            self.get_labeled_vector(
                word,
                # coords=seed_vect.get_end() + np.random.uniform(-0.5, 0.5, 3),
                color=WHITE
            )
            for word in nearest_words
        ))
        for neighbor in neighbors:
            neighbor.label.scale(0.75, about_edge=LEFT)
            neighbor.label.set_fill(border_width=0)
            neighbor.add(neighbor.label)

        # Description
        title = Text(f"Embeddings closest to E({self.seed_word})")
        underline = Underline(title)
        items = VGroup(*(
            Text(f"E({word})", font_size=36)
            for word in nearest_words
        ))
        items.arrange(DOWN, aligned_edge=LEFT)
        items.next_to(underline, DOWN, buff=0.5)
        items.align_to(title["E"][-1], LEFT)
        items.set_backstroke(BLACK, 8)

        desc = VGroup(title, underline, items)
        desc.fix_in_frame()
        desc.to_corner(UR)

        self.add(title, underline)

        # Add them all
        last_neighbor = VectorizedPoint()
        for item, neighbor in zip(items, neighbors):
            faded_last_neighbor = last_neighbor.copy()
            faded_last_neighbor.set_opacity(0.2)
            self.add(faded_last_neighbor, seed_group, neighbor)
            self.play(
                FadeIn(item),
                FadeIn(neighbor),
                FadeOut(last_neighbor),
                FadeIn(faded_last_neighbor),
            )
            last_neighbor = neighbor
            self.wait(self.wait_time_per_example)
        self.play(last_neighbor.animate.set_opacity(0.2))

        self.wait(10)

    def get_nearest_words(self, word):
        return find_nearest_words(self.model, self.model[word], self.n_shown + 1)[1:]

    def animate_in_neighbors(self, neighbors):
        # Old
        to_fade = VGroup()
        for neighbor in neighbors:
            neighbor.label.set_fill(border_width=0)
            self.add(to_fade, neighbor.label, seed_vect, seed_vect.label)
            self.play(
                FadeIn(neighbor),
                FadeIn(neighbor.label),
                to_fade.animate.set_opacity(0.25),
            )
            to_fade = VGroup(neighbor, neighbor.label)
        self.add(to_fade, neighbor.label, seed_vect, seed_vect.label)
        self.play(to_fade.animate.set_opacity(0.2))
        self.wait(5)

# Upstream: upstream/_2024/transformers/embedding.py:1694-1697
class ShowNearestNeighborsToWikipedia(ShowNearestNeighbors):
    seed_word = "wikipedia"
    color = BLUE
    default_frame_orientation = (10, 70)

# Upstream: upstream/_2024/transformers/embedding.py:1700-1702
class ShowNearestNeighborsToCat(ShowNearestNeighbors):
    seed_word = "cat"
    color = YELLOW

# Upstream: upstream/_2024/transformers/embedding.py:1705-1707
class ShowNearestNeighborsToNavy(ShowNearestNeighbors):
    seed_word = "navy"
    color = RED

# Upstream: upstream/_2024/transformers/embedding.py:1710-1721
class ShowNearestNeighborsToJump(ShowNearestNeighbors):
    seed_word = "jump"
    color = BLUE
    wait_time_per_example = 1.0
    frame_center = (2.18, -2.0, 0.0)
    random_seed = 1

    def add_plane(self):
        return VGroup()

    def get_nearest_words(self, word):
        return ["hop", "skip", "leap", "bound", "bounce", "drop", "vault"]

# Upstream: upstream/_2024/transformers/embedding.py:1724-1882
class DotProducts(InteractiveScene):
    def construct(self):
        # Add vectors
        plane = NumberPlane(
            (-4, 4), (-4, 4),
            background_line_style=dict(
                stroke_width=2,
                stroke_opacity=0.5,
                stroke_color=BLUE,
            ),
            faded_line_ratio=1
        )
        plane.set_height(6)
        plane.to_edge(LEFT, buff=0)
        vects = VGroup(
            Vector(0.5 * RIGHT + 2 * UP).set_stroke(MAROON_B, 6),
            Vector(1.0 * RIGHT + 0.5 * UP).set_stroke(YELLOW, 6),
        )
        vects.shift(plane.get_center())

        def get_dot_product():
            coords = np.array([plane.p2c(v.get_end()) for v in vects])
            return np.dot(coords[0], coords[1])

        self.add(plane)
        self.add(vects)

        # Vector labels
        vect_labels = VGroup(*(
            Tex(Rf"\vec{{\textbf{{ {char} }} }}")
            for char in "vw"
        ))
        for label, vect in zip(vect_labels, vects):
            label.vect = vect
            label.match_color(vect)
            label.add_updater(lambda l: l.move_to(
                l.vect.get_end() + 0.25 * normalize(l.vect.get_vector())
            ))

        self.add(vect_labels)

        # Add coordinate expressions
        vect_coords = VGroup(*(
            TexMatrix(
                [
                    [char + f"_{{{str(n)}}}"]
                    for n in [1, 2, 3, 4, "n"]
                ],
                bracket_h_buff=0.1,
                ellipses_row=-2,
            )
            for char in "vw"
        ))
        vect_coords.arrange(RIGHT, buff=0.75)
        vect_coords.next_to(plane, RIGHT, buff=1)
        vect_coords.set_y(1)
        for coords, vect in zip(vect_coords, vects):
            coords.get_entries().match_color(vect)
        dot = Tex(R"\cdot", font_size=72)
        dot.move_to(vect_coords)

        self.add(vect_coords, dot)

        # Add right hand side
        rhs = Tex("= +0.00", font_size=60)
        rhs.next_to(vect_coords, RIGHT)
        result = rhs.make_number_changeable("+0.00", include_sign=True)
        result.add_updater(lambda m: m.set_value(get_dot_product()))

        self.add(rhs)

        # Add dot product label
        brace = Brace(vect_coords, DOWN, buff=0.25)
        dp_label = brace.get_text("Dot product", buff=0.25)

        self.add(brace, dp_label)

        # Play around
        def dual_rotate(angle1, angle2, run_time=2):
            self.play(
                Rotate(vects[0], angle1 * DEGREES, about_point=plane.get_origin()),
                Rotate(vects[1], angle2 * DEGREES, about_point=plane.get_origin()),
                run_time=run_time
            )

        dual_rotate(-20, 20)
        dual_rotate(50, -60)
        dual_rotate(0, 80)
        dual_rotate(20, -80)

        # Show computation
        equals = rhs[0].copy()
        entry_pairs = VGroup(*(
            VGroup(*pair)
            for pair in zip(*[vc.get_columns()[0] for vc in vect_coords])
        ))
        prod_terms = entry_pairs.copy()
        for src_pair, trg_pair in zip(entry_pairs, prod_terms):
            trg_pair.arrange(RIGHT, buff=0.1)
            trg_pair.next_to(equals, RIGHT, buff=0.5)
            trg_pair.match_y(src_pair)
        prod_terms[-2].space_out_submobjects(1e-3)
        prod_terms[-2].match_x(prod_terms)
        prod_terms.target = prod_terms.generate_target()
        prod_terms.target.space_out_submobjects(1.5).match_y(vect_coords)
        plusses = VGroup(*(
            Tex("+", font_size=48).move_to(midpoint(m1.get_bottom(), m2.get_top()))
            for m1, m2 in zip(prod_terms.target, prod_terms.target[1:])
        ))

        rhs.target = rhs.generate_target()
        rhs.target[0].rotate(PI / 2)
        rhs.target.arrange(DOWN)
        rhs.target.next_to(prod_terms, DOWN)

        self.add(equals)
        self.play(
            LaggedStart(*(
                TransformFromCopy(m1, m2)
                for m1, m2 in zip(entry_pairs, prod_terms)
            ), lag_ratio=0.1, run_time=2),
            MoveToTarget(rhs)
        )
        self.wait()
        self.play(
            MoveToTarget(prod_terms),
            rhs.animate.next_to(prod_terms.target, DOWN),
            LaggedStartMap(Write, plusses),
        )
        self.wait()

        # Positive value
        dual_rotate(-65, 65)
        self.play(FlashAround(result, time_width=1.5, run_time=3))
        self.wait()

        # Orthogonal
        elbow = Elbow(width=0.25, angle=vects[0].get_angle())
        elbow.shift(plane.get_origin())
        zero = DecimalNumber(0)
        zero.replace(result, 1)
        dual_rotate(
            (vects[1].get_angle() + PI / 2 - vects[0].get_angle()) / DEGREES,
            0,
        )
        self.remove(result)
        self.add(zero)
        self.play(ShowCreation(elbow))
        self.wait()
        self.remove(elbow, zero)
        self.add(result)

        # Negative
        dual_rotate(20, -60)
        self.play(FlashAround(result, time_width=1.5, run_time=3))
        self.wait()

        # Play again
        dual_rotate(75, -95, run_time=8)

# Upstream: upstream/_2024/transformers/embedding.py:1885-2064
class DotProductWithPluralDirection(InteractiveScene):
    vec_tex = R"\vec{\text{plur}}"
    ref_words = ["cat", "cats"]
    word_groups = [
        ["puppy", "puppies"],
        ["octopus", "octopi", "octopuses", "octopodes"],
        ["student", "students"],
        ["one", "two", "three", "four"],
    ]
    x_range = (-4, 4 + 1e-4, 0.25)
    colors = [BLUE, RED]
    threshold = -1.0

    def construct(self):
        # Initialize equation
        self.model = get_word_to_vec_model()
        word_groups = self.word_groups
        words = list(it.chain(*word_groups))

        # Write plurality equation
        gen_lhs = self.get_equation_lhs(words[0])[0].copy()
        equals = Tex(":=")
        rf1, rf2 = self.ref_words
        rhs = Tex(
            Rf"E(\text{{{rf2}}}) - E(\text{{{rf1}}})",
            tex_to_color_map={
                Rf"\text{{{ref_word}}}": color
                for ref_word, color in zip(self.ref_words, self.colors)
            }
        )
        top_eq = VGroup(gen_lhs, equals, rhs)
        top_eq.arrange(RIGHT)
        gen_lhs.align_to(rhs, DOWN)
        top_eq.center().to_edge(UP, buff=0.5)

        self.play(FadeIn(rhs, UP))
        self.play(LaggedStart(
            FadeIn(equals, 0.5 * LEFT),
            FadeIn(gen_lhs, 1.0 * LEFT),
        ))
        self.wait()

        # Show on number line
        x_range = self.x_range
        number_line = NumberLine(
            x_range,
            big_tick_numbers=list(np.arange(*x_range[:2])),
            tick_size=0.05,
            longer_tick_multiple=3.0,
            width=12
        )
        number_line.rotate(PI / 2)
        number_line.add_numbers(
            np.arange(*x_range[:2]),
            num_decimal_places=1,
            font_size=40,
            direction=LEFT,
        )
        number_line.numbers.shift(SMALL_BUFF * LEFT)
        number_line.set_max_height(FRAME_HEIGHT - 1)
        number_line.to_edge(LEFT, buff=1.0)

        eq_lhs = self.get_equation_lhs(words[0])
        eq_rhs = self.get_equation_rhs(eq_lhs, words[0])
        equation = VGroup(eq_lhs, eq_rhs)
        brace = Brace(eq_lhs[2], LEFT, buff=0.1)
        brace.next_to(equation, LEFT, SMALL_BUFF, DOWN)
        equation_group = VGroup(brace, equation)
        dp = eq_rhs.get_value()

        word = eq_lhs[2][2:-1]
        lil_word = word.copy().scale(0.25)
        dot = GlowDot(color=word[0].get_color())
        dot.move_to(number_line.n2p(dp))

        lil_word.next_to(dot, RIGHT, buff=0)
        equation_group.next_to(dot, RIGHT, buff=0, submobject_to_align=brace)

        self.play(
            top_eq.animate.scale(0.75).to_corner(UR),
            TransformFromCopy(gen_lhs, eq_lhs[0]),
            FadeIn(eq_lhs[1:], shift=DOWN),
            FadeIn(brace, shift=DOWN),
            UpdateFromAlphaFunc(
                eq_rhs,
                lambda m, a: m.set_value(a * dp).next_to(eq_lhs[-1], RIGHT),
                run_time=1,
            ),
            Write(number_line, run_time=1)
        )
        self.add_dot(word, dot)
        self.wait()

        # Show some alternate
        new_rhs = eq_rhs.copy()
        eq_rhs.set_opacity(0)
        new_rhs.f_always.set_value(lambda: number_line.p2n(brace.get_center()))
        new_rhs.always.next_to(eq_lhs[-1], RIGHT)
        self.add(new_rhs)

        to_fade = Group(dot)
        for word_group in self.word_groups:
            for new_word in word_group:
                new_dp = self.get_dot_with_key_word(new_word)
                nl_point = number_line.n2p(new_dp)
                color = self.colors[int(new_dp > self.threshold)]
                new_dot = GlowDot(number_line.n2p(new_dp), color=color)
                new_lhs = self.get_equation_lhs(new_word)
                new_rhs = self.get_equation_rhs(new_lhs, new_word)
                new_rhs.set_opacity(0)
                new_equation = VGroup(new_lhs, new_rhs)
                new_equation.move_to(equation, LEFT)
                new_brace = brace.copy()
                new_equation_group = VGroup(new_brace, new_equation)
                y_shift = new_dot.get_y() - brace.get_y()
                new_equation_group.shift(y_shift * UP)

                if new_word == word_group[0]:
                    added_anim = FadeOut(to_fade)
                    to_fade = Group()
                else:
                    ghost = equation_group.copy()
                    ghost.target = ghost.generate_target()
                    ghost.target.set_fill(opacity=0.75)
                    ghost.target.scale(0.5, about_point=ghost[0].get_left())
                    added_anim = MoveToTarget(ghost)
                    to_fade.add(ghost)
                self.play(
                    Transform(equation_group, new_equation_group),
                    added_anim,
                )
                self.add_dot(new_lhs[2][2:-1], new_dot)
                to_fade.add(new_dot)

    def add_dot(self, word, dot):
        self.play(
            FadeInFromPoint(dot, word.get_center()),
            LaggedStart(
                (FadeTransform(char.copy(), dot.copy().set_opacity(0))
                for char in word),
                lag_ratio=2e-2,
                group_type=Group
            ),
            run_time=1
        )

    def get_equation_lhs(self, word):
        tex_pieces = [
            self.vec_tex, R"\cdot", Rf"E(\text{{{word}}})", "="
        ]
        expression = Tex(
            " ".join(tex_pieces),
            tex_to_color_map={self.vec_tex: YELLOW}
        )
        parts = [
            expression[tex_piece][0]
            for tex_piece in tex_pieces
        ]
        gen_part = parts[0]
        gen_part[0].set_width(0.75 * gen_part.get_width(), about_edge=DOWN)
        gen_part[0].shift(SMALL_BUFF * DOWN)
        value = self.get_dot_with_key_word(word)
        parts[2][2:-1].set_color(self.colors[int(value > self.threshold)])
        return VGroup(*parts)

    def get_equation_rhs(self, equation_lhs, word):
        rhs = DecimalNumber(self.get_dot_with_key_word(word))
        rhs.next_to(equation_lhs[-1], RIGHT)
        return rhs

    def get_dot_with_key_word(self, word):
        if word == "octopodes":
            return 2.3  # Hack
        elif word == "four":
            return 1.80  # To make the spacing nicer
        rf1, rf2 = self.ref_words
        return np.dot(
            (self.model[rf2] - self.model[rf1]).flatten(),
            self.model[word].flatten(),
        )

# Upstream: upstream/_2024/transformers/embedding.py:2067-2078
class DotProductWithGenderDirection(DotProductWithPluralDirection):
    vec_tex = R"\vec{\text{gen}}"
    ref_words = ["man", "woman"]
    words = [
        "mother", "father",
        "aunt", "uncle",
        "sister", "brother",
        "mama", "papa",
    ]
    x_range = (-5, 7 + 1e-4, 0.25)
    colors = [BLUE, RED]
    threshold = 1.0

# Upstream: upstream/_2024/transformers/embedding.py:2081-2227
class RicherEmbedding(InteractiveScene):
    def construct(self):
        # Add phrase
        phrase = Text("The King doth wake tonight and takes his rouse ...")
        phrase.to_edge(UP)
        words = break_into_words(phrase)
        rects = get_piece_rectangles(words)
        king_index = 1

        words.fix_in_frame()
        rects.fix_in_frame()

        self.add(words)

        # Setup axes
        self.set_floor_plane("xz")
        frame = self.frame
        frame.reorient(9, -6, 0)
        axes = ThreeDAxes((-5, 5), (-2, 2), (-5, 5))
        axes.shift(DOWN)
        plane = NumberPlane(
            (-5, 5), (-5, 5),
            background_line_style=dict(stroke_width=1, stroke_color=BLUE_E),
            faded_line_ratio=1,
        )
        plane.axes.set_stroke(GREY)
        plane.set_flat_stroke(False)
        plane.rotate(PI / 2, RIGHT)
        plane.move_to(axes)

        self.add(axes)
        self.add(plane)

        # Embed the word
        king_rect = rects[king_index]
        vector = Vector([-1, 1, 1])
        vector.shift(axes.get_origin())
        vector.match_color(king_rect)
        vector.set_flat_stroke(False)
        label = Text("King", font_size=24)
        label.next_to(vector.get_end(), normalize(vector.get_vector()), buff=0.1)

        self.play(DrawBorderThenFill(king_rect))
        self.play(
            TransformFromCopy(words[king_index], label),
            GrowArrow(vector),
        )
        self.wait(3)

        # Mention position
        index_labels = VGroup(*(
            Integer(n + 1, font_size=36).next_to(rect, DOWN, buff=0.2)
            for n, rect in enumerate(rects)
        ))
        index_labels.fix_in_frame()
        idx_vect, idx_label = self.get_added_vector(
            vector.get_end(), 0.5 * (RIGHT + OUT), "Pos. 2", TEAL,
            next_to_direction=UP,
            font_size=16
        )
        idx_label.rotate(45 * DEGREES, DOWN)
        idx_label.set_backstroke(BLACK, 1)

        self.play(
            LaggedStartMap(FadeIn, index_labels, shift=0.5 * DOWN),
        )
        self.play(
            TransformFromCopy(index_labels[king_index].set_backstroke(), idx_label),
            GrowArrow(idx_vect),
            frame.animate.reorient(-28, -22, 0).set_anim_args(run_time=3)
        )
        self.play(
            frame.animate.reorient(-11, -4, 0),
            LaggedStartMap(FadeOut, index_labels, lag_ratio=0.05, shift=0.5 * DOWN, time_span=(6, 7)),
            run_time=7
        )

        # Show king ingesting context
        self.play(
            LaggedStart(*(
                ContextAnimation(
                    words[king_index],
                    [*words[:king_index], *words[king_index + 1:]],
                    direction=DOWN,
                    fix_in_frame=True,
                    time_width=3,
                    min_stroke_width=3,
                    lag_ratio=0.05,
                    path_arc=PI / 3,
                )
                for n in range(3)
            ), lag_ratio=0.5),
            frame.animate.reorient(-5, -12, 0),
            run_time=5,
        )

        # Knock in many directions
        new_labeled_vector_args = [
            ([2, 1, 0], "lived in Scotland", None, DR),
            ([0, -1, -1], "murdered predecessor", None, RIGHT),
            ([-1.5, 1, -2], "in Shakespearean language", None, RIGHT),
        ]
        new_labeled_vects = VGroup()
        last_vect = idx_vect
        for args in new_labeled_vector_args:
            new_labeled_vects.add(self.get_added_vector(
                last_vect.get_end(), *args
            ))
            last_vect = new_labeled_vects[-1][0]
            last_vect.apply_depth_test()


        (vect1, label1), (vect2, label2), (vect3, label3) = new_labeled_vects
        self.play(
            GrowArrow(vect1),
            FadeIn(label1, 0.5 * DOWN),
            frame.animate.reorient(2, -16, 0, (0.6, -0.04, 0.02), 6.01).set_anim_args(run_time=8),
        )
        self.play(
            GrowArrow(vect2),
            FadeIn(label2, 0.5 * DOWN),
            frame.animate.reorient(35, -23, 0, (0.6, -0.04, 0.02), 6.01).set_anim_args(run_time=5),
        )
        self.play(
            GrowArrow(vect3),
            FadeIn(label3, 0.5 * DOWN),
            frame.animate.reorient(20, -29, 0, (0.61, 0.01, 0.0), 6.10).set_anim_args(run_time=5),
        )
        self.play(
            frame.animate.reorient(-19, -25, 0, (0.61, 0.01, 0.0), 6.10),
            run_time=5
        )

    def get_added_vector(self, curr_tip, direction, label, color=None, next_to_direction=UP, buff=0.1, font_size=24):
        if color is None:
            color = random_bright_color(hue_range=(0.45, 0.65))
        vect = Vector(direction)
        vect.set_color(color)
        vect.set_flat_stroke(False)
        vect.shift(curr_tip)
        text = Text(label, font_size=font_size)
        text.set_backstroke(BLACK, 4)
        text.next_to(vect.get_center(), next_to_direction, buff=buff)
        text.set_fill(border_width=0)

        result = VGroup(vect, text)
        return result

# Upstream: upstream/_2024/transformers/embedding.py:2232-2362
class MultipleMoleEmbeddings(Word2VecScene):
    default_frame_orientation = (0, 0)
    label_rotation = 0

    def setup(self):
        super().setup()
        self.set_floor_plane("xz")
        self.frame.add_ambient_rotation()
        self.add_plane()
        for mob in [self.plane, self.axes]:
            mob.rotate(-90 * DEGREES, RIGHT)

    def construct(self):
        # Show generic mole embedding
        frame = self.frame
        frame.reorient(-6, -6, 0, (-0.73, 1.29, -0.57), 5.27)
        phrases = VGroup(map(Text, [
            "American shrew mole",
            "One mole of carbon dioxide",
            "Take a biopsy of the mole",
        ]))
        for phrase in phrases:
            phrases.fix_in_frame()
            phrases.to_corner(UL)
            phrase["mole"][0].set_color(YELLOW)

        gen_vector = self.get_labeled_vector("mole", coords=(-2, 1.0, 1.5))
        curr_phrase = phrases[1]
        mover = curr_phrase["mole"][0]
        mover.set_backstroke(BLACK, 4)

        self.add(curr_phrase)
        self.wait()
        self.play(
            GrowArrow(gen_vector),
            TransformFromCopy(mover, gen_vector.label),
        )
        self.wait(10)

        # Show three refined meanings
        images = Group(
            ImageMobject("ShrewMole"),
            Tex(R"6.02 \times 10^{23}", font_size=24).set_color(BLUE),
            ImageMobject("LipMole"),
        )
        for image in images[::2]:
            image.set_height(0.5)
            image.set_opacity(0.75)

        colors = [GREY_BROWN, BLUE, ORANGE]
        ref_vects = VGroup(
            self.get_labeled_vector("", coords=coords)
            for coords in [
                (-1.0, -1.5, 1.5),
                (-4.0, 0.5, 1.0),
                (-0.5, 1.0, 2.5),
            ]
        )
        for vect, image, color in zip(ref_vects, images, colors):
            vect.set_color(color)
            image.next_to(vect.get_end(), UP, SMALL_BUFF)

        gen_vect_group = VGroup(gen_vector, gen_vector.label)

        self.play(
            frame.animate.reorient(-30, -5, 0, (-1.11, 1.35, -0.72), 5.27),
            LaggedStart(
                (TransformFromCopy(gen_vector, ref_vect)
                for ref_vect in ref_vects),
                lag_ratio=0.25,
                run_time=2,
            ),
            LaggedStart(
                (FadeInFromPoint(image, gen_vector.label.get_center())
                for image in images),
                lag_ratio=0.25,
                run_time=2,
                group_type=Group,
            ),
            gen_vect_group.animate.set_opacity(0.25).set_anim_args(run_time=2),
            run_time=2,
        )
        self.wait(3)

        ref_vect_groups = Group(
            Group(*pair) for pair in zip(ref_vects, images)
        )

        # Oscillate between meanings based on context
        diff_vects = VGroup(
            Arrow(gen_vector.get_end(), ref_vect.get_end(), buff=0)
            for ref_vect in ref_vects
        )
        diff_vects.set_color(GREY_B)

        last_phrase = curr_phrase
        last_diff = VGroup()
        for n, diff in enumerate(diff_vects):
            ref_vect_groups.target = ref_vect_groups.generate_target()
            ref_vect_groups.target.set_opacity(0.2)
            ref_vect_groups.target[n].set_opacity(1)
            if n != 2:
                ref_vect_groups.target[2][1].set_opacity(0.1)
            phrase = phrases[n]
            self.play(
                gen_vect_group.animate.set_opacity(1),
                MoveToTarget(ref_vect_groups),
                FadeOut(last_phrase, UP),
                FadeIn(phrase, UP),
                FadeOut(last_diff)
            )
            self.play(
                ShowCreation(diff, time_span=(1, 2)),
                TransformFromCopy(gen_vector, ref_vects[n], time_span=(1, 2)),
                ContextAnimation(
                    phrase["mole"][0], phrase,
                    direction=DOWN,
                    fix_in_frame=True,
                ),
            )
            self.wait(3)

            last_phrase = phrase
            last_diff = diff

        self.wait(5)

    def get_basis(self, model):
        basis = super().get_basis(model) * 2
        basis[2] *= -1
        return basis

# Upstream: upstream/_2024/transformers/embedding.py:2365-2467
class RefineTowerMeaning(MultipleMoleEmbeddings):
    def construct(self):
        # Set up vectors and images
        frame = self.frame
        frame.reorient(-26, -4, 0, (3.27, 1.57, 0.59), 5.28)
        frame.add_ambient_rotation(0.5 * DEGREES)

        words = VGroup(Text(word) for word in "Miniature Eiffel Tower".split(" "))
        words.scale(1.25)
        words.to_edge(UP)
        words.fix_in_frame()

        tower_images = Group(
            ImageMobject(f"Tower{n}")
            for n in range(1, 5)
        )
        eiffel_tower_images = Group(
            ImageMobject(f"EiffelTower{n}")
            for n in range(1, 4)
        )
        mini_eiffel_tower_images = Group(
            ImageMobject("MiniEiffelTower1")
        )
        image_groups = Group(
            tower_images,
            eiffel_tower_images,
            mini_eiffel_tower_images
        )

        vectors = VGroup(
            self.get_labeled_vector("", coords=coords)
            for coords in [
                (4, -1, 3.0),
                (5, -2, 1.5),
                (-3, -1, 2.5),
            ]
        )
        colors = [BLUE_D, GREY_B, GREY_C]
        for vector, color, image_group in zip(vectors, colors, image_groups):
            vector.set_color(color)
            for image in image_group:
                image.set_height(1.5)
                image.next_to(vector.get_end(), RIGHT * np.sign(vector.get_end()[0]))

        # Show tower
        tower = words[-1]
        tower.set_x(0)
        pre_tower_image = tower_images[0].copy()
        pre_tower_image.fix_in_frame()
        pre_tower_image.replace(tower, stretch=True)
        pre_tower_image.set_opacity(0)

        self.add(tower)
        self.wait()
        self.play(
            GrowArrow(vectors[0]),
            ReplacementTransform(pre_tower_image, tower_images[0]),
            run_time=2,
        )
        for ti1, ti2 in zip(tower_images, tower_images[1:]):
            self.play(
                FadeTransform(ti1, ti2),
                run_time=2
            )
        self.wait(2)

        # Eiffel tower
        words[:-1].set_opacity(0)
        eiffel_tower = words[-2:]

        self.play(
            frame.animate.reorient(-4, -7, 0, (2.95, 1.82, 0.49), 6.59),
            eiffel_tower.animate.set_opacity(1).arrange(RIGHT, aligned_edge=DOWN).to_edge(UP),
        )
        self.play(
            vectors[0].animate.set_opacity(0.25),
            tower_images[-1].animate.set_opacity(0.2),
            TransformFromCopy(vectors[0], vectors[1]),
            FadeTransform(tower_images[-1].copy(), eiffel_tower_images[0]),
            ContextAnimation(words[2], words[1], direction=DOWN, fix_in_frame=True),
            run_time=2,
        )
        for ti1, ti2 in zip(eiffel_tower_images, eiffel_tower_images[1:]):
            self.play(
                FadeTransform(ti1, ti2),
                run_time=2
            )
        self.wait(6)

        # Miniature eiffel tower
        self.play(
            frame.animate.reorient(-14, -2, 0, (-0.12, 2.21, 0.72), 7.05).set_anim_args(run_time=2),
            words.animate.set_opacity(1).arrange(RIGHT, aligned_edge=DOWN).to_edge(UP),
        )
        self.play(
            vectors[1].animate.set_opacity(0.25),
            eiffel_tower_images[-1].animate.set_opacity(0.2),
            TransformFromCopy(vectors[1], vectors[2]),
            FadeTransform(eiffel_tower_images[-1].copy(), mini_eiffel_tower_images[0]),
            ContextAnimation(words[2], words[0], direction=DOWN, fix_in_frame=True),
            run_time=2,
        )
        self.wait(10)

# Upstream: upstream/_2024/transformers/embedding.py:2470-2566
class UpdatingPoetryEmbedding(RicherEmbedding):
    def construct(self):
        # (Largely copied from RicherEmbedding, could factor better later)
        # Add phrase
        poem_str = "...\nTwo roads diverged in a wood, and I—\nI took the one less traveled by,"
        phrase = Text(poem_str, alignment="LEFT")
        phrase[:3].rotate(PI / 2).shift(SMALL_BUFF * UP)
        phrase.refresh_bounding_box()
        phrase.to_edge(UP, buff=SMALL_BUFF)
        words = break_into_words(phrase)
        rects = get_piece_rectangles(words)

        words.fix_in_frame()
        rects.fix_in_frame()

        self.add(words)

        # Setup axes
        self.set_floor_plane("xz")
        frame = self.frame
        frame.reorient(9, -6, 0)
        frame.reorient(9, -1, 0, 0.75 * UP)
        axes = ThreeDAxes((-5, 5), (-2, 2), (-5, 5))
        axes.shift(DOWN)
        plane = NumberPlane(
            (-5, 5), (-5, 5),
            background_line_style=dict(stroke_width=1, stroke_color=BLUE_E),
            faded_line_ratio=1,
        )
        plane.axes.set_stroke(GREY)
        plane.set_flat_stroke(False)
        plane.rotate(PI / 2, RIGHT)
        plane.move_to(axes)

        self.add(axes)
        self.add(plane)

        # Embed the word
        one_index = len(words) - 4
        one_rect = SurroundingRectangle(words[one_index])
        one_rect.set_fill(GREEN, 0.2)
        one_rect.set_stroke(GREEN, 2)
        one_rect.fix_in_frame()
        vector = Vector([-3, 1, 2])
        vector.shift(axes.get_origin())
        vector.match_color(one_rect)
        vector.set_flat_stroke(False)
        label = Text("one", font_size=36)
        label.next_to(vector.get_end(), normalize(vector.get_vector()), buff=0.1)

        self.play(DrawBorderThenFill(one_rect))
        self.play(
            TransformFromCopy(words[one_index], label),
            GrowArrow(vector),
        )
        self.wait(3)

        # Knock in many directions
        new_labeled_vector_args = [
            ([2, 1, 0], "of two roads", None, UL),
            ([2, -1, -1], "symbolizing choice", None, UR),
            ([0.5, 1, -3], "contrasting the original\nwith the familiar", None, DR),
        ]
        new_labeled_vects = VGroup()
        last_vect = vector
        for args in new_labeled_vector_args:
            new_labeled_vects.add(self.get_added_vector(
                last_vect.get_end(), *args
            ))
            last_vect = new_labeled_vects[-1][0]
            last_vect.apply_depth_test()
        orientation_args = [
            (-4, -12, 0, (-0.89, 0.03, -0.41), 8.10),
            (3, -9, 0, (-0.34, 0.49, -0.63), 8.60),
            (34, -14, 0, (-0.59, 0.49, -0.62), 9.20),
            (20, -29, 0, (0.61, 0.01, 0.0), 6.10),
        ]


        for (vect, label), orientation in zip(new_labeled_vects, orientation_args):
            self.play(
                GrowArrow(vect, time_span=(2, 3)),
                FadeIn(label, 0.5 * DOWN, time_span=(2, 3)),
                frame.animate.reorient(*orientation).set_anim_args(run_time=6),
                ContextAnimation(
                    one_rect, phrase[:-16],
                    run_time=4,
                    fix_in_frame=True,
                    path_arc=60 * DEGREES,
                    lag_ratio=1e-3,
                    direction=UP,
                ),
            )
        self.play(
            frame.animate.reorient(22, -23, 0, (-0.86, 0.4, -0.35), 7.15),
            run_time=5
        )

# Upstream: upstream/_2024/transformers/embedding.py:2571-2692
class SimpleSpaceExample(InteractiveScene):
    def construct(self):
        # Setup axes
        frame = self.frame
        plane, axes = self.add_plane_and_axes()
        frame.reorient(14, 77, 0, (2.23, 0.25, 1.13), 4.46)

        # Show an initial vector in the space
        frame.add_ambient_rotation()
        vect = Arrow(axes.c2p(0, 0, 0), axes.c2p(2, -1, 1), buff=0)
        vect.set_color(BLUE)
        vect.always.set_perpendicular_to_camera(self.frame)
        label = Text("you", font_size=24)
        # label = Text("Photo", font_size=24).set_backstroke(BLACK, 5)
        label.rotate(PI / 2, RIGHT)
        label.next_to(vect.get_center(), OUT + LEFT, buff=0)

        self.play(
            ShowCreation(vect),
            FadeIn(label, vect.get_vector())
        )
        self.wait(5)

        # Many directions -> Different kinds of meaning
        ideas = VGroup(
            Text("Part of a command"),
            Text("Affectionate"),
            Text("Sadness"),
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
            lines = get_direction_lines(axes, new_vect.get_vector(), color=new_vect.get_color())
            self.play(
                FadeOut(last_idea),
                ShowCreation(new_vect),
                FadeIn(idea, new_vect.get_vector()),
                LaggedStartMap(ShowCreationThenFadeOut, lines, lag_ratio=2 / len(lines), run_time=2)
            )
            self.wait(1)
            last_idea = VGroup(new_vect, idea)
            last_direction = direction
        self.play(FadeOut(last_idea))
        self.wait(5)

        # Specific ideas added onto "you"
        ideas = VGroup(
            # Text("Astronaut"),
            # Text("Riding a Horse"),
            # Text("On the moon"),
            #
            Text("needs an adjective next"),
            Text("preceded by \"that which does not kill\""),
            Text("related to growth and strength"),
            #
            # Text("River bank"),
            # Text("Beginning of a story"),
            # Text("Establishing a setting"),
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
        concepts = VGroup(label)
        for idea, direction, orientation in zip(ideas, directions, orientations):
            point = vects[-1].get_end()
            new_vect = self.get_added_vector(vects[-1], direction)
            new_vect.always.set_perpendicular_to_camera(self.frame)
            idea.next_to(new_vect.get_center())
            self.play(
                frame.animate.reorient(*orientation),
                GrowArrow(new_vect),
                FadeIn(idea, 0.5 * new_vect.get_vector())
            )
            self.wait(2)
            vects.add(new_vect)
        self.wait(15)

    def add_plane_and_axes(
        self,
        x_range=(-4, 4),
        y_range=(-4, 4),
        z_range=(-3, 3),
    ):
        axes = ThreeDAxes(x_range, y_range, z_range)
        plane = NumberPlane(
            x_range, y_range,
            background_line_style=dict(
                stroke_color=GREY_D,
                stroke_width=1
            ),
            faded_line_ratio=1,
        )
        plane.axes.set_stroke(GREY_D, 0)

        self.add(plane, axes)
        return plane, axes

    def get_added_vector(self, last_vect, direction):
        point = last_vect.get_end()
        new_vect = Arrow(point, point + direction, buff=0)
        new_vect.set_color(random_bright_color())
        new_vect.set_flat_stroke(False)
        return new_vect

# Upstream: upstream/_2024/transformers/embedding.py:2695-2755
class ManyIdeasManyDirections(SimpleSpaceExample):
    random_seed = 2

    def construct(self):
        # Axes
        frame = self.frame
        plane, axes = self.add_plane_and_axes()
        frame.reorient(-17, 73, 0, (-0.06, 0.11, 0.31), 6.03)
        frame.add_ambient_rotation()

        # Many directions -> Different kinds of meaning
        ideas = VGroup(
            Text(word)
            for word in [
                "Typewriter",
                "Paradigm",
                "Whimsical",
                "Gelatinous",
                "Rainbow",
                "Serendipitous",
                "Algorithm",
                "Nebulous",
                "Spatula",
                "Lethargic",
                "Effervescent",
                "Asteroid",
                "Pungent",
                "Daydream",
                "Mercurial",
                "Cactus",
                "Diaphanous",
                "Hiccup",
                "Viscous",
                "Thunderclap",
            ]
        )
        ideas.set_backstroke(BLACK, 3)
        ideas.scale(0.5)
        ideas.rotate(PI / 2, RIGHT)

        last_idea = VGroup()
        last_direction = RIGHT + OUT
        for idea in ideas:
            direction = normalize(cross(last_direction, np.random.uniform(-1, 1, 3)))
            new_vect = Vector(direction)
            new_vect.set_perpendicular_to_camera(self.frame)
            new_vect.set_color(random_bright_color())
            idea.next_to(new_vect.get_end(), direction, buff=0.1)
            lines = get_direction_lines(axes, direction, color=new_vect.get_color(), n_lines=250, stroke_width=2)
            idea.set_fill(interpolate_color(new_vect.get_color(), WHITE, 0.5))
            self.play(
                FadeOut(last_idea),
                GrowArrow(new_vect),
                FadeIn(idea, new_vect.get_vector()),
                LaggedStartMap(ShowCreationThenFadeOut, lines, lag_ratio=1 / len(lines), run_time=1.5)
            )
            self.wait()
            last_idea = VGroup(new_vect, idea)
            last_direction = direction
        self.play(FadeOut(last_idea))
        self.wait(5)

# Upstream: upstream/_2024/transformers/embedding.py:2758-3047
class MJSpace(SimpleSpaceExample):
    def construct(self):
        # Set up axes
        frame = self.frame
        plane, axes = self.add_plane_and_axes()
        axes.set_stroke(width=1)
        frame.add_ambient_rotation()

        # Show vectors landing in the space
        sentence = Text("Michael Jordan plays the sport of basketball", font_size=36)
        sentence.to_edge(UP)
        tokens = break_into_tokens(sentence)
        token_rects = get_piece_rectangles(tokens, leading_spaces=True, h_buff=0)
        arrs = VGroup(
            NumericEmbedding().scale(0.25).next_to(rect, DOWN, buff=1.0)
            for rect in token_rects
        )
        arrows = VGroup(Arrow(rect, arr, buff=0.1) for rect, arr in zip(token_rects, arrs))
        vects = VGroup(
            Vector(np.random.uniform(-3, 3, 3))
            for arr in arrs
        )
        vects.set_stroke(GREY_B)
        vects.fix_in_frame()

        VGroup(token_rects, tokens, arrows, arrs).fix_in_frame()

        frame.reorient(-18, 86, 0, (0.21, 0.12, 3.56), 11.65)
        self.add(token_rects, tokens)
        self.play(
            LaggedStartMap(FadeIn, arrs, shift=DOWN, lag_ratio=0.1),
            LaggedStartMap(GrowArrow, arrows, lag_ratio=0.1),
        )
        self.wait()
        self.play(
            frame.animate.reorient(11, 76, 0, ORIGIN, FRAME_HEIGHT),
            FadeOut(VGroup(token_rects, tokens, arrows), UP, time_span=(1, 2)),
            LaggedStart(
                (Transform(arrow, vect)
                for arrow, vect in zip(arrs, vects)),
                lag_ratio=0.05,
            ),
            run_time=3
        )
        self.remove(arrs)
        self.add(vects)
        self.wait()
        self.play(LaggedStart(
            (vect.animate.scale(0, about_point=vect.get_start())
            for vect in vects),
            lag_ratio=0.05,
            remover=True
        ))

        # Show three directions
        colors = [YELLOW, RED, "#F88158"]
        all_coords = [normalize([-1, -1, 1])]
        all_coords.append(normalize(cross(all_coords[0], IN)))
        all_coords.append(-normalize(cross(all_coords[0], all_coords[1])))
        all_coords = np.array(all_coords)[[0, 2, 1]]
        labels = VGroup(*map(Text, ["First Name Michael", "Last Name Jordan", "Basketball"]))
        label_directions = [LEFT + OUT, IN, RIGHT + OUT]

        vect_groups = VGroup()
        vects = VGroup()
        for coords, label, color, direction in zip(all_coords, labels, colors, label_directions):
            vect = Vector(2.0 * coords)
            vect.set_color(color)
            vect.always.set_perpendicular_to_camera(self.frame)
            label.scale(0.5)
            label.rotate(PI / 2, RIGHT)
            label.set_color(color)
            label.next_to(vect.get_end(), direction, buff=0.1)
            label.set_fill(border_width=0.5)
            label.set_backstroke(BLACK, 4)
            vects.add(vect)
            vect_groups.add(VGroup(vect, label))

        orientations = [
            (17, 76, 0),
            (17, 80, 0),
            (-16, 77, 0),
        ]

        for vect, label, orientation in zip(vects, labels, orientations):
            lines = get_direction_lines(axes, vect.get_vector(), color=vect.get_color())
            self.play(
                GrowArrow(vect),
                FadeIn(label, vect.get_vector()),
                frame.animate.reorient(*orientation),
            )
            self.play(
                LaggedStartMap(ShowCreationThenFadeOut, lines, lag_ratio=2 / len(lines))
            )
            self.wait(2)

        # Bring in "plucked out" vector
        emb_coords = 2.0 * all_coords[:2].sum(0)
        emb = Vector(emb_coords)
        emb.always.set_perpendicular_to_camera(self.frame)
        emb.set_flat_stroke(False)
        emb_label = Tex(R"\vec{\textbf{E}}", font_size=30)
        emb_label.rotate(89 * DEGREES, RIGHT)
        emb_label.add_updater(lambda m: m.move_to(1.1 * emb.get_end()))
        emb_label.suspend_updating()

        self.play(
            frame.animate.reorient(7, 66, 0).set_anim_args(run_time=2),
            FadeIn(emb, shift=2 * (IN + LEFT)),
            FadeIn(emb_label, shift=2 * (IN + LEFT)),
        )
        self.wait()

        # Set up dot product display
        def get_proj_point(vect1, vect2):
            v1 = vect1.get_end()
            v2 = vect2.get_end()
            return v2 * np.dot(v1, v2) / np.dot(v2, v2)

        def get_dot_product_lines(vect, proj_line_color=GREY_A):
            dashed_line = always_redraw(
                lambda: Line(emb.get_end(), get_proj_point(emb, vect)).set_stroke(WHITE, 2).set_anti_alias_width(10)
            )
            proj_line = always_redraw(
                lambda: Line(ORIGIN, get_proj_point(emb, vect)).set_stroke(proj_line_color, width=4, opacity=0.75)
            )
            return dashed_line, proj_line

        m_dashed_line, m_proj_line = get_dot_product_lines(vects[0])

        formula = Tex(R"\vec{\textbf{E}} \cdot \big(\overrightarrow{\text{First Name Michael}}\big) = ", font_size=36)
        formula[3:-1].set_color(YELLOW)
        formula.to_corner(UL)
        formula.fix_in_frame()
        rhs = DecimalNumber(font_size=42)
        rhs.fix_in_frame()
        rhs.next_to(formula[-1], RIGHT, buff=0.15)
        rhs.target_vect = vects[0]
        rhs.add_updater(lambda m: m.set_value(np.dot(m.target_vect.get_end(), emb.get_end()) / 4.0))

        m_proj_line.suspend_updating()
        self.play(
            ShowCreation(m_dashed_line),
            TransformFromCopy(Line(ORIGIN, emb.get_end(), flat_stroke=False), m_proj_line),
            FadeIn(formula, UP),
            vect_groups[1:].animate.set_opacity(0.25),
        )
        m_proj_line.resume_updating()
        self.play(
            TransformFromCopy(rhs.copy().unfix_from_frame().set_opacity(0).move_to(m_proj_line), rhs),
        )
        emb_label.resume_updating()
        for _ in range(2):
            self.play(
                emb.animate.put_start_and_end_on(ORIGIN, [-2.5, -2.0, -0.5]),
                rate_func=wiggle,
                run_time=5
            )
        self.wait(2)
        self.play(emb.animate.put_start_and_end_on(axes.get_origin(), 1.5 * all_coords[1:3].sum(0)), run_time=3)
        self.play(frame.animate.reorient(26, 68, 0), run_time=2 )
        self.play(emb.animate.put_start_and_end_on(ORIGIN, [1.0, -1.5, -1.0]), run_time=3)
        self.wait(2)
        self.play(
            frame.animate.reorient(-4, 73, 0),
            emb.animate.put_start_and_end_on(ORIGIN, emb_coords),
            run_time=3
        )
        self.wait(5)

        # Dotting against L.N. Jordan
        j_dashed_line, j_proj_line = get_dot_product_lines(vects[1])
        j_paren = Tex(R"\big(\overrightarrow{\text{Last Name Jordan}}\big) = ", font_size=36)
        j_paren[:-1].set_color(RED)
        m_paren = formula[3:]
        m_paren.fix_in_frame()
        j_paren.move_to(m_paren, LEFT)
        j_paren.fix_in_frame()
        rhs.target_vect = vects[1]

        self.play(
            frame.animate.reorient(15, 97, 0),
            FadeOut(m_paren, UP, time_span=(1, 2)),
            FadeIn(j_paren, UP, time_span=(1, 2)),
            rhs.animate.next_to(j_paren, RIGHT, buff=0.15).set_anim_args(time_span=(1, 2)),
            LaggedStart(
                vect_groups[0].animate.set_opacity(0.25),
                vect_groups[1].animate.set_opacity(1),
                FadeOut(m_dashed_line),
                FadeOut(m_proj_line),
                lag_ratio=0.25,
                run_time=2
            )
        )
        j_proj_line.suspend_updating()
        self.play(
            ShowCreation(j_dashed_line),
            TransformFromCopy(Line(ORIGIN, emb.get_end(), flat_stroke=False), j_proj_line),
        )
        j_proj_line.resume_updating()
        self.play(
            emb.animate.put_start_and_end_on(ORIGIN, [-1.5, -1.5, 0]).set_anim_args(run_time=3, rate_func=there_and_back)
        )
        self.wait()

        # Dotting against basketball
        b_dashed_line, b_proj_line = get_dot_product_lines(vects[2])
        b_paren = Tex(R"\big(\overrightarrow{\text{Basketball}}\big) = ", font_size=36)
        b_paren[:-1].set_color(vects[2].get_color())
        b_paren.move_to(m_paren, LEFT)
        b_paren.fix_in_frame()
        rhs.suspend_updating()

        self.play(
            frame.animate.reorient(2, 65, 0),
            FadeOut(j_paren, UP),
            FadeIn(b_paren, UP),
            rhs.animate.next_to(b_paren[-1], RIGHT, buff=0.2).set_value(0),
            FadeOut(j_dashed_line),
            FadeOut(j_proj_line),
            vect_groups[1].animate.set_opacity(0.25),
            vect_groups[2].animate.set_opacity(1.0),
        )
        self.wait()

        rhs.target_vect = vects[2]
        rhs.resume_updating()
        self.add(b_dashed_line, b_proj_line)
        self.play(
            emb.animate.put_start_and_end_on(ORIGIN, [0.6, -2.2, 0]),
            rate_func=there_and_back,
            run_time=6,
        )
        self.wait(3)

        # Emphasize dot products with first two names
        self.play(
            frame.animate.reorient(5, 85, 0).set_anim_args(run_time=2),
            FadeOut(formula[:3]),
            FadeOut(b_paren),
            FadeOut(rhs),
            FadeOut(b_dashed_line),
            FadeOut(b_proj_line),
            vect_groups[:2].animate.set_opacity(1),
            vect_groups[2].animate.set_opacity(0.25),
        )
        self.wait()
        self.play(
            ShowCreation(m_dashed_line),
            ShowCreation(m_proj_line),
        )
        self.wait()
        self.play(
            ShowCreation(j_dashed_line),
            ShowCreation(j_proj_line),
        )
        self.wait(20)
        self.play(
            *map(FadeOut, [j_dashed_line, j_proj_line, m_dashed_line, m_proj_line, emb, emb_label]),
        )

        # Show sum of the first two names
        j_vect_copy, m_vect_copy = vect_copies = vects[:2].copy()
        vect_copies.clear_updaters()
        vect_copies.set_stroke(opacity=0.5)
        j_vect_copy.shift(vects[1].get_vector())
        m_vect_copy.shift(vects[0].get_vector())
        emb.put_start_and_end_on(axes.get_origin(), m_vect_copy.get_end())

        self.play(frame.animate.reorient(-6, 78, 0), run_time=2)
        self.play(LaggedStart(
            TransformFromCopy(vects[1], m_vect_copy),
            TransformFromCopy(vects[0], j_vect_copy),
            lag_ratio=0.5
        ))
        self.play(GrowArrow(emb))
        self.wait(4)

        # Show the basketball direction
        self.play(
            *map(FadeOut, [m_vect_copy, j_vect_copy, emb])
        )
        self.play(
            frame.animate.reorient(-19, 77, 0, (1.32, -0.22, -0.12), 3.75),
            vect_groups[:2].animate.set_opacity(0.25),
            vect_groups[2][0].animate.set_opacity(1.0),
            vect_groups[2][1].animate.set_opacity(1.0),
            run_time=2
        )
        self.wait(20)

# Upstream: upstream/_2024/transformers/ml_basics.py:7-17
class DialTest(InteractiveScene):
    def construct(self):
        # Test
        dial = Dial(radius=0.5)
        self.add(dial)
        self.play(dial.animate_set_value(0.5, run_time=1))

        # Test
        machine = MachineWithDials()
        self.add(machine)
        self.play(machine.random_change_animation())

# Upstream: upstream/_2024/transformers/ml_basics.py:20-295
class MLWithinDeepL(InteractiveScene):
    def construct(self):
        # Organize boxes
        kw = dict(font_size=36, opacity=0.25)
        model_boxes = VGroup(
            self.get_titled_box("Multilayer Perceptrons", BLUE_D, **kw),
            self.get_titled_box("Convolutional Neural Networks", BLUE_D, **kw),
            self.get_titled_box("Transformers", BLUE, **kw),
        )
        for box in model_boxes:
            box.box.set_width(model_boxes.get_width(), stretch=True)
        dots = Tex(R"\vdots", font_size=72)
        model_boxes.add(dots)
        model_boxes.arrange(DOWN, buff=0.1)
        dots.shift(0.2 * DOWN)
        transformer_box = model_boxes[2]

        dl_box = self.get_titled_box(
            "Deep Learning", TEAL,
            font_size=60,
            y_space=model_boxes.get_height() + 1.0,
            x_space=2.75,
            opacity=0.05
        )

        model_boxes.next_to(dl_box.title, DOWN)

        # Animate in word
        transformer_box.save_state()
        transformer_box.box.set_opacity(0)
        transformer_box.set_height(1)
        transformer_box.move_to(np.array([-1.58, -2.01, 0]))

        self.add(transformer_box)
        self.wait()
        self.add(dl_box, transformer_box)
        self.play(LaggedStart(
            FadeIn(dl_box, scale=1.2),
            Restore(transformer_box),
            *(FadeIn(model_boxes[i]) for i in [0, 1, 3]),
        ), lag_ratio=0.75, run_time=2)
        self.wait()

        dl_box.add(model_boxes)
        self.add(dl_box)

        # Place within ML box
        ml_box = self.get_titled_box(
            "Machine Learning",
            GREEN,
            opacity=0.1,
            font_size=72,
            x_space=6.0,
            y_space=5.0
        )
        dl_box.target = dl_box.generate_target()
        blank_boxes = dl_box.box.replicate(2)
        inner_boxes = VGroup(*blank_boxes, dl_box.target)
        reg_drawing = self.get_regression_drawing()
        bayes_net = self.get_bayes_net_drawing()
        for drawing, box in zip([reg_drawing, bayes_net], blank_boxes):
            drawing.set_height(0.8 * box.get_height())
            drawing.move_to(box)
            box.add(drawing)
        inner_boxes.set_height(3.5)
        inner_boxes.arrange(RIGHT)
        inner_boxes.set_max_width(ml_box.get_width() - 0.5)
        inner_boxes.next_to(ml_box.title, DOWN, buff=1.0)

        self.add(ml_box, dl_box, blank_boxes)
        self.play(
            FadeIn(ml_box),
            MoveToTarget(dl_box),
            LaggedStartMap(FadeIn, blank_boxes, scale=2.0, lag_ratio=0.5)
        )
        self.wait()

        ml_box.add(dl_box, blank_boxes)

        # Learn from data
        words = Text("Learn from data", font_size=72)
        words.to_edge(UP, buff=MED_SMALL_BUFF)
        learn = words["Learn"][0]
        learn.save_state()
        learn.set_x(0)
        words["data"].set_color(YELLOW)
        ml_box.target = ml_box.generate_target()
        ml_box.target.scale(0.75)
        ml_box.target.to_edge(DOWN)
        arrow = Arrow(ml_box.target, words)

        self.play(
            MoveToTarget(ml_box),
            GrowFromCenter(arrow),
            TransformFromCopy(ml_box.title["Learn"][0], learn),
        )
        self.play(
            Restore(learn),
            FadeIn(words["from data"][0], lag_ratio=0.1, shift=0.2 * RIGHT),
        )
        self.wait()
        self.play(
            FadeOut(ml_box),
            FadeOut(arrow),
        )
        self.wait()

        # Go back to the box
        self.clear()
        ml_box.center()
        self.add(ml_box)

        # Pop out
        ml_box.remove(dl_box)
        ml_box.add(dl_box.copy())
        ml_box.target = ml_box.generate_target()
        ml_box.target.scale(0.25).to_edge(LEFT)
        dl_box.target = dl_box.generate_target()
        dl_box.target.scale(2.0)
        dl_box.target.next_to(ml_box.target, RIGHT, buff=0.75),
        lines = VGroup(*(
            Line(
                ml_box.target[-1].get_corner(RIGHT + v),
                dl_box.target.get_corner(LEFT + v)
            )
            for v in [UP, DOWN]
        ))
        lines.set_stroke(TEAL, 2)

        self.play(
            MoveToTarget(ml_box),
            MoveToTarget(dl_box),
            GrowFromPoint(lines[0], dl_box.get_corner(UR)),
            GrowFromPoint(lines[1], dl_box.get_corner(DR)),
            run_time=1.5,
        )
        self.wait()

        # Show a neural network
        network = NeuralNetwork([5, 10, 5])
        network.next_to(dl_box, RIGHT, buff=1.0)

        self.play(
            FadeIn(network.layers[0]),
            ShowCreation(network.lines[0], lag_ratio=0.01),
            FadeIn(network.layers[1], lag_ratio=0.5),
            run_time=2
        )
        self.play(
            ShowCreation(network.lines[1], lag_ratio=0.01),
            FadeIn(network.layers[2], lag_ratio=0.5),
            run_time=2
        )

        # Ambiently change the network
        for _ in range(6):
            self.play(
                network.animate.randomize_line_style().randomize_layer_values(),
                run_time=3,
                lag_ratio=1e-4
            )

        # Pile of matrices
        pile_words = Text("Pile of matrices")
        pile_words.next_to(network, UP)
        path_arc = -60 * DEGREES
        arrow = Arrow(dl_box.get_top(), pile_words.get_corner(UL), path_arc=path_arc)
        matrices = VGroup(*(
            WeightMatrix(shape=(8, 6), ellipses_row=None, ellipses_col=None)
            for x in range(10)
        ))
        matrices.match_width(network)
        matrices.move_to(network, UP)
        matrices.shift(0.5 * DOWN)
        matrix_shift = 0.5 * (IN + RIGHT)

        matrices.arrange(OUT, buff=0.25)
        matrices.move_to(network)

        for matrix in matrices[:-1]:
            matrix.target = matrix.generate_target()
            for entry in matrix.target.get_entries():
                dot = Dot(radius=0.05)
                dot.set_fill(entry.get_fill_color(), opacity=0.25)
                dot.move_to(entry)
                entry.become(dot)
            matrix.target[-1].set_opacity(0.25)
        matrices[-1].get_entries().set_backstroke(BLACK, 8)

        self.play(
            FadeOut(network, 2 * DOWN),
            ShowCreation(arrow),
            FadeInFromPoint(pile_words, dl_box.title.get_center(), path_arc=path_arc),
            FadeOut(network, DOWN)
        )
        mat_shift = 0.5 * IN + 0.25 * DOWN
        self.play(
            LaggedStart(*(
                Succession(
                    FadeIn(matrix, shift=mat_shift),
                    MoveToTarget(matrix)
                )
                for matrix in matrices[:-1]
            ), lag_ratio=0.25, run_time=5),
            Animation(Point()),
            FadeIn(matrices[-1], shift=mat_shift, time_span=(3.75, 4.75))
        )
        self.wait()

    def get_titled_box(self, text, color, font_size=48, y_space=0.5, x_space=0.5, opacity=0.1):
        title = Text(text, font_size=font_size)
        box = Rectangle(
            title.get_width() + x_space,
            title.get_height() + y_space
        )
        box.set_fill(interpolate_color(BLACK, color, opacity), 1)
        box.set_stroke(color, 2)
        title.next_to(box.get_top(), DOWN, buff=MED_SMALL_BUFF)
        result = VGroup(box, title)
        result.box = box
        result.title = title
        return result

    def get_regression_drawing(self):
        axes = Axes((-1, 10), (-1, 10))
        m = 0.5
        y0 = 2
        line = axes.get_graph(lambda x: y0 + m * x)
        line.set_stroke(YELLOW, 2)
        dots = VGroup(
            Dot(axes.c2p(x, y0 + m * x + np.random.normal()))
            for x in np.random.uniform(0, 10, 15)
        )

        reg_drawing = VGroup(axes, dots, line)
        return reg_drawing

    def get_bayes_net_drawing(self):
        radius = MED_SMALL_BUFF
        node = Circle(radius=radius)
        node.set_stroke(GREY_B, 2)
        node.shift(2 * DOWN)
        nodes = VGroup(
            node.copy().shift(x * RIGHT + y * UP)
            for x, y in [
                (-1, 0),  
                (1, 0),
                (-2, 2),
                (0, 2),
                (2, 2),
                (-2, 4),
                (0, 4),
            ]
        )
        edge_index_pairs = [
            (2, 0),
            (3, 0),
            (3, 1),
            (4, 1),
            (5, 2),
            (6, 3),
        ]
        edges = VGroup()
        for i1, i2 in edge_index_pairs:
            n1, n2 = nodes[i1], nodes[i2]
            edge = Arrow(
                n1.get_center(), 
                n2.get_center(),
                buff=radius,
                color=WHITE,
                stroke_width=3
            )
            edges.add(edge)

        network = VGroup(nodes, edges)
        return network

# Upstream: upstream/_2024/transformers/ml_basics.py:298-304
class ShowCross(InteractiveScene):
    def construct(self):
        # Test
        cross = Cross(Square(side_length=5))
        cross.set_stroke(width=[0, 30, 0])
        self.play(ShowCreation(cross))
        self.wait()

# Upstream: upstream/_2024/transformers/ml_basics.py:307-327
class FlashThroughImageData(InteractiveScene):
    time_per_example = 0.1

    def construct(self):
        # Images
        image_data = load_image_net_data()
        arrow = Vector(RIGHT)

        for path, text in ProgressDisplay(image_data):
            image = ImageMobject(str(path))
            label = Text(text.split(",")[0])
            label.use_winding_fill(False)
            image.next_to(arrow, LEFT)
            label.next_to(arrow, RIGHT)
            self.add(image, arrow, label)
            self.wait(self.time_per_example)
            self.remove(image, label)

            if hasattr(image, "shader_wrapper"):
                for tid in image.shader_wrapper.texture_names_to_ids.values():
                    release_texture(tid)

# Upstream: upstream/_2024/transformers/ml_basics.py:330-356
class FlashThroughTextData2(InteractiveScene):
    n_examples = 200
    time_per_example = 0.1
    window_size = 50
    line_len = 35
    ul_point = 5 * LEFT + 3 * UP

    def construct(self):
        # Test
        totc = read_in_book(name="tale_of_two_cities")
        words = re.split(r"\s", totc)
        words = list(filter(lambda s: s, words))

        for n in range(self.n_examples):
            index = random.randint(0, len(words) - self.window_size)
            window = words[index:index + self.window_size]
            phrase = get_paragraph(window, line_len=self.line_len)
            phrase.move_to(self.ul_point, UL)

            word = phrase[window[-1]][-1]
            rect = SurroundingRectangle(word, buff=0.1)
            rect.set_stroke(YELLOW, 2)
            rect.set_fill(YELLOW, 0.5)

            self.add(phrase)
            self.wait(self.time_per_example)
            self.remove(phrase)

# Upstream: upstream/_2024/transformers/ml_basics.py:359-389
class TweakedMachine(InteractiveScene):
    n_tweaks = 200
    time_per_example = 0.1

    def construct(self):
        # Test
        machine = MachineWithDials(
            dial_config=dict(
                value_to_color_config=dict(
                    low_negative_color=BLUE_E,
                    high_negative_color=BLUE_B,
                )
            )
        )
        machine.move_to(2 * DOWN)
        machine.set_width(4)
        arrow = Vector(DOWN, stroke_width=10)
        arrow.next_to(machine, UP)

        self.add(machine, arrow)

        values = np.array([d.get_random_value() for d in machine.dials])

        for n in range(self.n_tweaks):
            nudges = np.random.uniform(-1, 1, values.shape)
            values += 0.1 * nudges
            values[values > 1.0] = 0.9
            values[values < 0.0] = 0.1
            for dial, value in zip(machine.dials, values):
                dial.set_value(value)
            self.wait(self.time_per_example)

# Upstream: upstream/_2024/transformers/ml_basics.py:392-972
class PremiseOfML(InteractiveScene):
    box_center = RIGHT
    n_examples = 50
    random_seed = 316
    show_matrices = False

    def construct(self):
        self.init_data()

        # Set up input and output
        machine = self.get_machine()
        machine.set_width(4)
        machine.move_to(self.box_center)
        model_label = Text("Model", font_size=72)
        model_label.move_to(machine.box)
        in_arrow = Vector(RIGHT).next_to(machine, LEFT)
        out_arrow = Vector(RIGHT).next_to(machine, RIGHT)

        self.add(machine.box)
        self.add(in_arrow, out_arrow)
        self.add(model_label)

        # Show initial input and output
        in_data, out_data = self.new_input_output_example(in_arrow, out_arrow)

        in_word, out_word = [
            Text(word).next_to(machine, UP).match_x(mob).shift_onto_screen()
            for word, mob in [("Input", in_data), ("Output", out_data)]
        ]

        self.play(
            FadeIn(in_data, lag_ratio=0.001),
            FadeIn(in_word, 0.5 * UP),
        )
        self.play(FadeOutToPoint(in_data.copy(), machine.get_left(), lag_ratio=0.005, path_arc=-60 * DEGREES))
        self.play(
            FadeInFromPoint(out_data, machine.get_right(), lag_ratio=0.1, path_arc=60 * DEGREES),
            FadeIn(out_word, 0.5 * UP)
        )
        self.wait()

        # Show code
        model_label.target = model_label.generate_target()
        model_label.target.scale(in_word[0].get_height() / model_label[0].get_height())
        model_label.target.align_to(in_word, UP)
        code = self.get_code()
        code.set_height(machine.get_height() - MED_SMALL_BUFF)
        code.set_max_width(machine.get_width() - MED_SMALL_BUFF)
        code.move_to(machine, UP).shift(SMALL_BUFF * DOWN)

        self.play(
            MoveToTarget(model_label),
            ShowIncreasingSubsets(code, run_time=3),
        )
        self.wait()

        # Show tunable parameters
        param_label = Text("Tunable parameters")
        param_label.next_to(machine, UP)
        param_label.set_color(BLUE)

        self.play(
            FadeOut(code, 0.25 * DOWN, lag_ratio=0.01),
            Write(machine.dials, lag_ratio=0.001),
            FadeOut(model_label, 0.5 * UP),
            FadeIn(param_label, 0.5 * UP),
        )
        self.play(machine.rotate_all_dials())
        self.wait()

        # Show lots of new data
        for n in range(self.n_examples):
            new_in_data, new_out_data = self.new_input_output_example(in_arrow, out_arrow)
            self.add(in_data, out_data)
            time_span = (0, 0.35)
            self.play(
                machine.random_change_animation(run_time=0.5),
                FadeOut(in_data, time_span=time_span),
                FadeOut(out_data, time_span=time_span),
                FadeIn(new_in_data, time_span=time_span),
                FadeIn(new_out_data, time_span=time_span),
            )
            in_data, out_data = new_in_data, new_out_data

        if not self.show_matrices:
            return

        # Make room
        up_shift = 1.5 * UP
        down_shift = 1.75 * DOWN

        down_group = Group(in_arrow, machine, param_label, out_arrow, out_data, out_word)
        self.play(
            in_data.animate.scale(0.75).shift(up_shift + 0.5 * UP),
            UpdateFromFunc(out_data, lambda m: m.match_y(in_data)),
            in_word.animate.shift(up_shift),
            down_group.animate.shift(down_shift),
        )

        # Create pixels
        image = in_data
        pixels = create_pixels(in_data)

        # Show input array
        in_array = NumericEmbedding(shape=(10, 10), ellipses_col=-2)
        in_array.match_height(machine)
        in_array.next_to(in_arrow, LEFT)
        image.set_opacity(0.8)

        self.play(
            TransformFromCopy(
                pixels,
                VGroup(*(in_array.get_entries().family_members_with_points())),
                run_time=2,
                lag_ratio=1e-3
            ),
            FadeInFromPoint(in_array.get_brackets(), image.get_bottom()),
            Write(in_array.get_ellipses(), time_span=(1, 2))
        )
        self.play(image.animate.set_opacity(1))
        self.wait()

        # Show one dimensional array
        vector = NumericEmbedding(length=10)
        vector.replace(in_array, dim_to_match=1)
        vector.move_to(in_array, RIGHT)

        self.remove(in_array)
        self.play(
            TransformFromCopy(in_array.get_brackets(), vector.get_brackets()),
            TransformFromCopy(in_array.get_columns()[5], vector.get_columns()[0]),
            *map(FadeOut, in_array.get_columns()),
        )
        self.wait()
        self.remove(vector)
        self.play(LaggedStart(
            TransformFromCopy(vector.get_brackets(), in_array.get_brackets()),
            TransformFromCopy(vector.get_columns()[0], in_array.get_columns()[5]),
            *(
                FadeIn(col, shift=col.get_center() - vector.get_center())
                for col in in_array.get_columns()
            )
        ))
        self.wait()

        # Show 3d tensor
        self.frame.set_field_of_view(30 * DEGREES)
        dot_array = in_array.copy()
        for entry in (*dot_array.get_entries(), *dot_array.get_ellipses()):
            dot = Dot(entry.get_center(), radius=0.06)
            entry.set_submobjects([dot])

        tensor = VGroup(*(
            dot_array.copy()
            for n in range(5)
        ))
        for layer in tensor:
            for dot in (*layer.get_entries(), *layer.get_ellipses()):
                dot.set_fill(
                    interpolate_color(GREY_C, GREY_B, random.random()),
                    opacity=0.5,
                )
                dot.set_backstroke(BLACK, 2)
        tensor.arrange(OUT, buff=0.25)
        tensor.move_to(in_array, RIGHT)
        tensor.rotate(5 * DEGREES, RIGHT)
        tensor.rotate(5 * DEGREES, UP)

        self.remove(in_array)
        self.play(TransformFromCopy(VGroup(in_array), tensor))
        self.play(Rotate(tensor, 20 * DEGREES, axis=UP, run_time=4))
        self.play(Transform(tensor, VGroup(in_array), remover=True))
        self.add(in_array)

        # Express output as an array of numbers
        values = np.random.uniform(0, 1, (10, 1))
        values[5] = 9.7
        out_array = DecimalMatrix(values, ellipses_row=-2)
        out_array.match_height(machine)
        out_array.match_y(out_arrow)
        out_array.match_x(out_word)

        self.play(
            FadeInFromPoint(out_array, machine.get_right(), lag_ratio=1e-3),
            out_data.animate.scale(0.75).fade(0.5).rotate(-PI / 2).next_to(out_array, RIGHT, buff=0.25),
        )
        self.wait()

        # Describe parameters as weights
        weights_label = Text("Weights")
        weights_label.next_to(machine, UP, buff=0.5)
        weights_label.match_color(param_label)
        equiv = Tex(R"\Updownarrow")
        equiv.next_to(weights_label, UP)

        top_dials = machine.dials[:8]
        dial_rects = VGroup(*map(SurroundingRectangle, top_dials))
        dial_rects.set_stroke(TEAL, 2)
        dial_arrows = VGroup(*(
            Arrow(weights_label.get_bottom(), rect.get_top(), buff=0.05)
            for rect in dial_rects
        ))
        dial_arrows.set_stroke(TEAL)

        self.play(
            FadeIn(weights_label, scale=2),
            param_label.animate.next_to(equiv, UP),
            Write(equiv),
        )
        self.play(
            LaggedStart(*(
                VFadeInThenOut(VGroup(arrow, rect))
                for arrow, rect in zip(dial_arrows, dial_rects)
            ), lag_ratio=0.25, run_time=3)
        )
        self.wait()

        # Show weighted sum
        machine.dials.save_state()
        weights_label.set_backstroke(BLACK, 5)
        weights_label.target = weights_label.generate_target()
        weights_label.target.next_to(top_dials, DOWN, buff=0.25)
        weighted_sum = Tex(
            R"w_1 x_1 + w_2 x_2 + w_3 x_3 + \cdots + w_n x_n",
            font_size=42,
        )
        weighted_sum.next_to(machine, UP, buff=1.0)
        weight_parts = weighted_sum[re.compile(r"w_\d|w_n")]
        weight_parts.set_color(BLUE)
        data_parts = weighted_sum[re.compile(r"x_\d|x_n")]
        data_parts.set_color(GREY_A)

        indices = [0, 1, 2, -1]
        dial_lines = VGroup(*(
            Line(top_dials[n].get_top(), weight_parts[n].get_bottom(), buff=0.1)
            for n in indices
        ))
        ellipses = weighted_sum[R"\cdots"]
        dial_lines.set_stroke(BLUE_B, 1)

        column = in_array.get_columns()[-1]
        col_rect = SurroundingRectangle(column)
        col_rect.set_stroke(YELLOW, 2)

        self.play(ShowCreation(col_rect))
        self.play(
            FadeOut(VGroup(param_label, equiv), UP),
            MoveToTarget(weights_label),
            machine.dials[8:].animate.fade(0.75),
            LaggedStart(*(
                TransformFromCopy(column[n], data_parts[n])
                for n in indices
            )),
            Group(in_data, in_word).animate.to_edge(LEFT, buff=0.25)
        )
        self.play(
            Write(weighted_sum["+"]),
            Write(weighted_sum[R"\cdots"]),
            LaggedStart(*(
                FadeTransform(top_dials[n].copy(), weight_parts[n])
                for n in indices
            )),
            LaggedStartMap(ShowCreation, dial_lines),
            run_time=1
        )
        self.wait()
        for x in range(3):
            self.play(*(
                dial.animate_set_value(dial.get_random_value())
                for dial in top_dials
            ))

        # Wrap a function around it
        func_wrapper = Tex(R"f()")
        func_wrapper[:2].next_to(weighted_sum, LEFT, buff=SMALL_BUFF)
        func_wrapper[2].next_to(weighted_sum, RIGHT, buff=SMALL_BUFF)
        func_wrapper.set_color(PINK)

        nl_words = Text("Simple nonlinear\nfunction", font_size=42, alignment="LEFT")
        nl_words.next_to(func_wrapper, UP, buff=1.5, aligned_edge=LEFT)
        nl_words.match_color(func_wrapper)
        nl_arrow = Arrow(nl_words, func_wrapper[0].get_top())
        nl_arrow.match_color(nl_words)

        self.play(
            FadeIn(func_wrapper),
            FadeIn(nl_words, lag_ratio=0.1),
            ShowCreation(nl_arrow),
        )
        self.wait()

        # Show next layer
        weights_label.target = weights_label.generate_target()
        weights_label.target.next_to(weighted_sum, UP, buff=1.0)
        dial_lines.target = VGroup(*(
            Line(
                weights_label.target, weight_parts[index].get_top(),
                buff=SMALL_BUFF
            )
            for index in indices
        ))
        dial_lines.target.match_style(dial_lines)

        layer1 = NumericEmbedding(shape=(10, 5), ellipses_col=-2)
        layer1.match_height(in_array)
        layer1.next_to(in_arrow, RIGHT)
        mid_arrow = in_arrow.copy()
        mid_arrow.next_to(layer1, RIGHT)
        dots = Tex(R"\dots").next_to(mid_arrow, RIGHT)

        expr_rect = SurroundingRectangle(func_wrapper)
        expr_rect.set_stroke(PINK, 2)
        x01_rect = SurroundingRectangle(layer1.elements[0])
        x01_rect.match_style(expr_rect)
        rect_lines = VGroup(*(
            Line(expr_rect.get_corner(DOWN + v), x01_rect.get_corner(UP + v))
            for v in [LEFT, RIGHT]
        ))
        rect_lines.match_style(expr_rect)

        self.play(LaggedStart(
            FadeOut(weights_label),
            FadeOut(dial_lines),
            FadeOut(nl_words),
            FadeOut(nl_arrow),
            FadeOut(col_rect),
            FadeOut(machine),
            FadeIn(expr_rect),
        ))
        self.play(
            TransformFromCopy(in_array.get_brackets(), layer1.get_brackets()),
            TransformFromCopy(in_arrow, mid_arrow),
            out_arrow.animate.next_to(dots, RIGHT),
            Write(dots),
        )
        self.play(
            TransformFromCopy(expr_rect, x01_rect),
            ShowCreation(rect_lines, lag_ratio=0),
            FadeInFromPoint(layer1.elements[0], expr_rect.get_center()),
        )
        self.play(ShowIncreasingSubsets(layer1[1:-1]))
        self.add(layer1)
        self.wait()

        # Highlight a subset of the data
        in_subset = VGroup(*(
            elem
            for row in in_array.get_rows()[:3]
            for elem in row[:3]
        ))
        in_subset_rects = VGroup(*map(SurroundingRectangle, in_subset))
        data_part_rects = VGroup(*map(SurroundingRectangle, data_parts))
        self.play(
            LaggedStartMap(ShowCreationThenFadeOut, in_subset_rects, lag_ratio=0.02),
            LaggedStartMap(ShowCreationThenFadeOut, data_part_rects, lag_ratio=0.04),
            run_time=3
        )
        self.wait()

        # Show added layers
        to_fade = VGroup(
            func_wrapper, expr_rect, rect_lines, x01_rect,
            weighted_sum
        )

        self.play(
            LaggedStartMap(FadeOut, to_fade, run_time=1),
            in_arrow.animate.scale(0.5, about_edge=LEFT),
            layer1.animate.rotate(70 * DEGREES, UP).next_to(in_arrow, RIGHT, buff=-0.25),
            mid_arrow.animate.scale(0.5).next_to(in_arrow, RIGHT, buff=0.75),
        )

        layer1_group = VGroup(layer1, mid_arrow)
        layer2_group, layer3_group = layer1_group.replicate(2)
        layer2_group.next_to(layer1_group, RIGHT, buff=SMALL_BUFF)
        layer3_group.next_to(layer2_group, RIGHT, buff=SMALL_BUFF)
        self.play(TransformFromCopy(layer1_group, layer2_group))
        self.play(
            TransformFromCopy(layer2_group, layer3_group),
            VGroup(dots, out_arrow).animate.next_to(layer3_group, RIGHT),
        )
        self.play(
            LaggedStart(*(
                dot.animate.shift(0.1 * UP).set_anim_args(rate_func=there_and_back)
                for dot in dots
            ), lag_ratio=0.25)
        )
        self.wait()

        # Bring back machine
        layers = VGroup(layer1_group, layer2_group, layer3_group, dots)

        self.play(
            FadeIn(machine, scale=0.8),
            FadeIn(weights_label, shift=DOWN),
            ShowCreation(dial_lines, lag_ratio=0.1),
            FadeIn(weighted_sum, shift=UP),
            FadeOut(layers, scale=0.8),
        )
        self.wait()
        self.play(
            machine.random_change_animation()
        )
        self.wait()

        # Show a matrix
        frame = self.frame
        matrix, vector, equals, rhs = get_full_matrix_vector_product()
        mat_prod_group = VGroup(matrix, vector, equals, rhs)
        mat_prod_group.next_to(machine, UP, buff=2.0)
        mat_prod_group.shift(0.5 * LEFT)

        p0 = machine.get_corner(UL)
        p1 = matrix.get_corner(DL)
        p2 = machine.get_corner(UR)
        p3 = rhs.get_corner(DR)
        brace = VGroup(
            CubicBezier(p0, p0 + 2 * UP, p1 + 2 * DOWN, p1 + 0.1 * DOWN),
            CubicBezier(p2, p2 + 2 * UP, p3 + 2 * DOWN, p3 + 0.1 * DOWN),
        )
        brace.set_stroke(WHITE, 5)

        self.play(LaggedStart(
            TransformFromCopy(data_parts, vector.get_columns()[0]),
            TransformFromCopy(weight_parts, matrix.get_rows()[0]),
            FadeTransform(weighted_sum, rhs.get_rows()[0]),
            frame.animate.set_height(10, about_edge=DOWN),
            FadeOut(in_data, DOWN),
            FadeOut(out_data, DOWN),
            in_word.animate.next_to(in_array, UP),
            FadeIn(matrix, lag_ratio=0.1),
            ShowCreation(brace, lag_ratio=0),
            weights_label.animate.set_height(0.5).next_to(matrix, UP, buff=MED_SMALL_BUFF),
            Uncreate(dial_lines, lag_ratio=0.1),
            FadeOut(col_rect),
            machine.dials.animate.restore(),
            FadeIn(vector.get_brackets()),
            FadeIn(rhs.get_brackets()),
            FadeIn(equals),
            run_time=3,
            lag_ratio=0.1,
        ))
        self.wait()

        # Animate matrix vector product
        ghost_row = rhs.get_rows()[0].copy()
        ghost_row.set_opacity(0.25)
        self.add(ghost_row)
        show_symbolic_matrix_vector_product(
            self, matrix, vector, rhs,
            run_time_per_row=1.5
        )
        self.remove(ghost_row)
        self.wait()

        # Associate weights with dials
        w_elems = matrix.get_entries()
        moving_dials = machine.dials[:len(w_elems)].copy()
        moving_dials.target = moving_dials.generate_target()
        for dial, w_elem in zip(moving_dials.target, w_elems):
            dial.move_to(w_elem)
            dial.scale(2)

        self.play(
            w_elems.animate.set_opacity(0.25),
            MoveToTarget(moving_dials, run_time=2),
        )
        self.play(
            LaggedStart(*(
                dial.animate_set_value(dial.get_random_value())
                for dial in moving_dials
            ), lag_ratio=0.02, run_time=3)
        )
        self.wait()
        self.play(
            FadeOut(moving_dials),
            w_elems.animate.set_opacity(1),
        )

        # Vector an data slice
        v_rect = SurroundingRectangle(vector.get_entries())
        self.play(
            ShowCreation(v_rect),
            ShowCreation(col_rect),
        )
        self.wait()
        self.play(
            FadeOut(v_rect),
            FadeOut(col_rect),
        )
        self.wait()

        # Show many matrices
        lhs = VGroup(matrix, vector)
        small_mat_product = Tex(R"W_{10} v_{11}")
        small_mat_product[R"W_{10}"].set_color(BLUE)
        w_index = small_mat_product.make_number_changeable("10")
        v_index = small_mat_product.make_number_changeable("11")
        small_mat_products = VGroup()
        n_rows, n_cols = 16, 8
        for n in range(n_rows * n_cols):
            w_index.set_value(n + 1)
            v_index.set_value(n + 1)
            new_prod = small_mat_product.copy()
            new_prod.arrange(RIGHT, buff=SMALL_BUFF, aligned_edge=DOWN)
            small_mat_products.add(new_prod)
        small_mat_products.arrange_in_grid(n_rows, n_cols, v_buff_ratio=2.0)
        small_mat_products.replace(machine.dials)

        mv_label = Text("matrix-vector products")
        mv_label.next_to(machine, UP, buff=1.0)
        mv_label[-1].set_opacity(0)
        mv_top_label = Text("Many, many")
        mv_top_label.next_to(mv_label, UP)
        mv_arrows = VGroup(*(
            Arrow(mv_label.get_bottom(), smp.get_top(), buff=0.1)
            for smp in small_mat_products
        ))

        self.play(
            FadeTransform(mat_prod_group, small_mat_products[0]),
            Uncreate(brace, lag_ratio=0),
            FadeOut(machine.dials, run_time=0.5),
            FadeTransform(weights_label, mv_label),
            GrowFromPoint(mv_arrows[0], weights_label.get_bottom()),
            frame.animate.set_height(FRAME_HEIGHT).move_to(DOWN).set_anim_args(time_span=(1, 2)),
            run_time=2,
        )
        self.wait()
        self.remove(mv_arrows)
        self.play(
            FadeIn(mv_top_label, UP),
            mv_label[-1].animate.set_opacity(1),
            ShowIncreasingSubsets(small_mat_products, rate_func=linear, run_time=12, int_func=np.ceil),
            ShowSubmobjectsOneByOne(mv_arrows, rate_func=linear, run_time=12, int_func=np.ceil),
        )
        self.remove(mv_arrows)
        self.play(FadeOut(mv_arrows[-1]))
        self.wait()

    def init_data(self):
        self.image_data = load_image_net_data()

    def new_input_output_example(self, in_arrow, out_arrow) -> tuple[Mobject, Mobject]:
        path, label_text = random.choice(self.image_data)
        image = ImageMobject(str(path))
        image.set_width(4)
        image.next_to(in_arrow, LEFT)
        label = Text(label_text.split(",")[0])
        label.set_max_width(2.5)
        label.next_to(out_arrow, RIGHT)
        return image, label

    def get_machine(self):
        return MachineWithDials()

    def get_code(self):
        # Test
        src = """
            #include <opencv2/opencv.hpp>
            #include <iostream>

            using namespace cv;
            using namespace std;

            int main(int argc, char** argv) {
                Mat image = imread(argv[1], IMREAD_GRAYSCALE);
                if (image.empty()) {
                    cout << "Could not open image" << endl;
                    return -1;
                }

                // Blur the image to reduce noise
                Mat blurredImage;
                GaussianBlur(image, blurredImage, Size(5, 5), 0);

                // Detect edges with Canny
                Mat edges;
                Canny(blurredImage, edges, 100, 200);
        """
        return Code(src, language="C++", alignment="LEFT")

# Upstream: upstream/_2024/transformers/ml_basics.py:975-1026
class PremiseOfMLWithText(PremiseOfML):
    random_seed = 316

    def init_data(self):
        totc = read_in_book(name="tale_of_two_cities")
        words = re.split(r"\s", totc)
        words = list(filter(lambda s: s, words))
        self.all_words = words

    def new_input_output_example(self, in_arrow, out_arrow):
        words = self.all_words
        window_size = 25
        index = random.randint(0, len(words) - window_size)
        window = words[index:index + window_size]
        in_text = get_paragraph(window[:-1], line_len=25)
        in_text.set_max_width(4)
        in_text.next_to(in_arrow, LEFT)
        out_text = Text(window[-1])
        out_text.next_to(out_arrow, RIGHT)
        return in_text, out_text

    def get_machine(self):
        machine = super().get_machine()
        machine.add(VectorizedPoint().next_to(machine, DOWN, buff=0.5))
        return machine

    def get_code(self):
        # Test
        src = """
            using namespace std;

            vector<string> findCapitalizedWords(const string& text) {
                vector<string> capitalizedWords;
                stringstream ss(text);
                string word;

                while (ss >> word) {
                    // Check for uppercase
                    if (!word.empty() && isupper(word[0])) {
                        capitalizedWords.push_back(word);
                    }
                }

                return capitalizedWords;
            }

            int main() {
                string text;
                cout << "Enter text: ";
                getline(cin, text); // Using getline to read spaces
        """
        return Code(src, language="C++", alignment="LEFT")

# Upstream: upstream/_2024/transformers/ml_basics.py:1029-1033
class PremiseOfMLWithMatrices(PremiseOfML):
    # Skip to animation 9
    show_matrices = True
    n_examples = 0
    random_seed = 6

# Upstream: upstream/_2024/transformers/ml_basics.py:1036-1171
class LinearRegression(InteractiveScene):
    radom_seed = 1

    def construct(self):
        # Set up axes
        x_min, x_max = (-1, 12)
        y_min, y_max = (-1, 10)
        axes = Axes((x_min, x_max), (y_min, y_max), width=12, height=6)
        axes.to_edge(DOWN)
        self.add(axes)

        # Add data
        n_data_points = 30
        m = 0.75
        y0 = 1

        data = np.array([
            (x, y0 + m * x + 0.75 * np.random.normal(0, 1))
            for x in np.random.uniform(2, x_max, n_data_points)
        ])
        points = axes.c2p(data[:, 0], data[:, 1])
        dots = DotCloud(points)

        dots.set_color(YELLOW)
        dots.set_glow_factor(1)
        dots.set_radius(0.075)

        self.add(dots)

        # Make title
        title = Text("Linear Regression", font_size=72)
        title.to_edge(UP)

        # Show line
        m_tracker = ValueTracker(m)
        y0_tracker = ValueTracker(y0)
        line = Line()
        line.set_stroke(TEAL, 2)

        def update_line(line):
            curr_y0 = y0_tracker.get_value()
            curr_m = m_tracker.get_value()
            line.put_start_and_end_on(
                axes.c2p(0, curr_y0),
                axes.c2p(x_max, curr_y0 + curr_m * x_max),
            )

        line.add_updater(update_line)

        self.play(
            FadeIn(title, UP),
            ShowCreation(line),
        )
        self.wait()

        # Label inputs and outputs
        in_labels = VGroup(Text("Input"), Text("Square footage"))
        out_labels = VGroup(Text("Output"), Text("Price"))
        for in_label in in_labels:
            in_label.next_to(axes.x_axis, DOWN, buff=0.1, aligned_edge=RIGHT)
        for out_label in out_labels:
            out_label.rotate(90 * DEGREES)
            out_label.next_to(axes.y_axis, LEFT, aligned_edge=UP)

        self.play(LaggedStart(
            FadeIn(in_labels[0], lag_ratio=0.1),
            FadeIn(out_labels[0], lag_ratio=0.1),
            lag_ratio=0.5,
        ))
        self.wait()
        self.play(LaggedStart(
            FadeTransform(*in_labels),
            FadeTransform(*out_labels),
            lag_ratio=0.8,
        ))
        self.wait()

        # Emphasize line
        self.play(
            VShowPassingFlash(
                line.copy().set_stroke(BLUE, 8).scale(1.1).insert_n_curves(100),
                time_width=1.5,
                run_time=2
            ),
        )
        self.wait()

        # Add line parameter updaters
        words = ["slope", "y-intercept"]
        value_ranges = [(0, 2, 0.2), (-2, 3, 0.5)]
        m_label, y0_label = labels = VGroup(
            VGroup(
                Dial(value_range=value_range),
                Text(f"{text} = "),
                DecimalNumber(),
            )
            for text, value_range in zip(words, value_ranges)
        )
        for label, tracker in zip(labels, [m_tracker, y0_tracker]):
            label[0].set_height(2 * label[2].get_height())
            label.arrange(RIGHT)
            label[0].f_always.set_value(tracker.get_value)
            label[2].f_always.set_value(tracker.get_value)
        labels.arrange(DOWN, aligned_edge=LEFT)
        labels.next_to(axes.y_axis, RIGHT, buff=1.0)
        labels.to_edge(UP)

        self.play(
            FadeOut(title, UP),
            FadeIn(m_label, UP),
        )
        self.play(
            m_tracker.animate.set_value(1.5),
            run_time=2,
        )
        self.play(FadeIn(y0_label, UP))
        self.play(
            y0_tracker.animate.set_value(-2),
            run_time=2
        )
        self.wait()

        # Tweak line parameters
        for n in range(10):
            alpha = random.random()
            if alpha > 0.5:
                alpha += 1
            new_m = interpolate(m_tracker.get_value(), m, alpha)
            new_y0 = interpolate(y0_tracker.get_value(), y0, alpha)
            self.play(LaggedStart(
                m_tracker.animate.set_value(new_m),
                y0_tracker.animate.set_value(new_y0),
                run_time=1.5,
                lag_ratio=0.25,
            ))
            self.wait(0.5)

# Upstream: upstream/_2024/transformers/ml_basics.py:1174-1663
class ShowGPT3Numbers(InteractiveScene):
    def construct(self):
        # Title
        gpt3_label = Text("GPT-3", font="Consolas", font_size=72)
        openai_logo = SVGMobject("OpenAI.svg")
        openai_logo.set_fill(WHITE)
        openai_logo.set_height(2.0 * gpt3_label.get_height())
        title = VGroup(openai_logo, gpt3_label)
        title.arrange(RIGHT)
        title.to_edge(UP)

        self.add(title)

        # 175b weights
        n_param = 175_181_291_520
        weights_count = Integer(n_param, color=BLUE)
        weights_text = VGroup(Text("Total parameters:"), weights_count)
        weights_text.arrange(RIGHT, buff=MED_SMALL_BUFF)
        weights_text.next_to(title, DOWN, buff=1.0)
        weights_arrow = Arrow(weights_count, gpt3_label, stroke_width=6, buff=0.2)

        param_shape = (8, 24)
        pre_dials = Dial().get_grid(*param_shape)
        dial_matrix = MobjectMatrix(
            pre_dials, *param_shape,
            ellipses_row=-2,
            ellipses_col=-2,
        )
        dial_matrix.set_width(FRAME_WIDTH)
        dial_matrix.next_to(weights_text, DOWN, buff=MED_SMALL_BUFF)

        dials = dial_matrix.get_entries()
        dots = dial_matrix.get_ellipses()

        self.play(
            FadeIn(weights_text[:-1], time_span=(0, 3)),
            CountInFrom(weights_count, 0),
            GrowArrow(weights_arrow, time_span=(0, 3)),
            LaggedStartMap(FadeIn, pre_dials, scale=3, lag_ratio=0.1),
            run_time=10,
        )
        self.play(
            LaggedStart(
                (dial.animate_set_value(dial.get_random_value())
                for dial in dials),
                lag_ratio=1.0 / len(dials),
                run_time=5
            )
        )
        self.wait()

        # Change name to weights
        new_name = Text("Total weights: ")
        new_name.move_to(weights_text[0], RIGHT)

        self.play(
            Transform(weights_text[0]["Total"][0], new_name["Total"][0]),
            Transform(weights_text[0]["parameters:"][0], new_name["weights:"][0]),
        )
        self.wait()

        # Organize dials into matrices
        mat_text = Text("Organized into 27,938 matrices")
        mat_text["27,938"].set_color(TEAL)
        mat_text.next_to(weights_text, DOWN, buff=MED_SMALL_BUFF)
        mat_text.shift((weights_count.get_x(LEFT) - mat_text["27,938"].get_x(LEFT)) * RIGHT)

        mat_grid_shape = n, m = (3, 7)
        matrices = VGroup(
            WeightMatrix(shape=(5, 5))
            for n in range(np.product(mat_grid_shape))
        )
        matrices.arrange_in_grid(
            *mat_grid_shape,
            v_buff_ratio=0.3,
            h_buff_ratio=0.2,
        )
        matrices.set_width(FRAME_WIDTH - 1)
        mat_dots = VGroup(
            *(
                Tex(R"\dots").next_to(mat, RIGHT)
                for mat in matrices[m - 1::m]
            ),
            *(
                Tex(R"\vdots").next_to(mat, DOWN)
                for mat in matrices[-m:]
            )
        )
        matrices_group = VGroup(matrices, mat_dots)
        matrices_group.set_width(FRAME_WIDTH - 1)
        matrices_group.next_to(mat_text, DOWN, buff=0.5)
        matrices_group.set_x(0)
        all_entries = VGroup(
            entry
            for mat in matrices
            for row in mat.get_rows()
            for entry in row
        )

        pre_entries = []
        height = all_entries[0].get_height()
        for n, entry in enumerate(all_entries):
            index = n * len(dials) // len(all_entries)
            dial = dials[min(index, len(dials) - 1)].copy()
            dial.target = dial.generate_target()
            dial.target.set_height(height)
            dial.target.move_to(entry)
            pre_entries.append(dial)
        pre_entries = VGroup(*pre_entries)

        self.remove(dial_matrix)
        lag_ratio = 1 / len(all_entries)
        self.play(
            Write(mat_text),
            LaggedStartMap(MoveToTarget, pre_entries, lag_ratio=lag_ratio),
            TransformFromCopy(dots, mat_dots),
            *(FadeIn(mat.get_brackets()) for mat in matrices)
        )
        self.play(
            FadeOut(pre_entries, lag_ratio=0.2 * lag_ratio),
            FadeIn(all_entries, lag_ratio=0.2 * lag_ratio),
            run_time=2
        )
        self.add(matrices)
        self.wait()

        # Show 8 different categories
        count_text = VGroup(weights_text, mat_text)
        title_scale_factor = 0.75
        count_text.target = count_text.generate_target()
        count_text.target.scale(title_scale_factor)
        count_text.target.to_edge(UP, MED_SMALL_BUFF).to_edge(LEFT)
        h_line = Line(LEFT, RIGHT)
        h_line.set_width(FRAME_WIDTH)
        h_line.next_to(count_text.target, DOWN).set_x(0)
        h_line.insert_n_curves(10)
        h_line.set_stroke(width=[0, 3, 3, 3, 0])

        category_names = VGroup(*map(TexText, [
            "Embedding",
            "Key",
            "Query",
            # "Value",  # Dumb alignment hack
            # "Output",
            R"Value$_\downarrow$",
            R"Value$_\uparrow$",
            "Up-projection",
            "Down-projection",
            "Unembedding",
        ]))
        # category_names[3][-1].set_fill(BLACK)  # Dumb alignment hack
        category_names.arrange(DOWN, buff=MED_LARGE_BUFF, aligned_edge=LEFT)
        category_names.set_height(5.5)
        category_names.next_to(h_line, DOWN, buff=MED_LARGE_BUFF)
        category_names.to_edge(LEFT, buff=0.5)
        category_names.set_fill(border_width=0.2)

        mat_index = 0
        counts = [1, * 6 * [3], 1]
        mat_groups = VGroup()
        for name, count, dots in zip(category_names, counts, mat_dots):
            new_mat_index = mat_index + count
            mat_group = matrices[mat_index:new_mat_index]
            mat_index = new_mat_index

            mat_group.target = mat_group.generate_target()
            if len(mat_group) > 1:
                mat_group.target.add(*mat_group.copy())
            mat_group.target.arrange(RIGHT, buff=LARGE_BUFF)
            mat_group.target.set_height(0.25)
            mat_group.target.next_to(category_names, RIGHT)
            mat_group.target.match_y(name)

            dots.target = dots.generate_target()
            if dots.get_width() < dots.get_height():
                dots.target.rotate(90 * DEGREES)
            dots.target.next_to(mat_group.target, RIGHT)
            mat_groups.add(mat_group)
        mat_dots[0].target.set_opacity(0)
        mat_dots[7].target.set_opacity(0)

        n_groups = len(category_names)
        self.play(LaggedStart(
            MoveToTarget(count_text),
            title.animate.scale(title_scale_factor).next_to(count_text.target, RIGHT, LARGE_BUFF),
            FadeOut(weights_arrow),
            GrowFromCenter(h_line),
            FadeIn(category_names),
            LaggedStart(map(MoveToTarget, mat_groups), lag_ratio=0.05),
            LaggedStart(map(MoveToTarget, mat_dots[:n_groups]), lag_ratio=0.05),
            LaggedStart(map(FadeOut, mat_dots[n_groups:]), lag_ratio=0.05),
            FadeOut(matrices[sum(counts):]),
        ))

        # Add lines
        h_lines = Line(LEFT, RIGHT).set_width(13).replicate(n_groups)
        h_lines.set_stroke(WHITE, 1, 0.5)
        for name, line in zip(category_names, h_lines):
            line.next_to(name, DOWN, buff=0.1, aligned_edge=LEFT)
            name.line = line
        v_line = Line(
            mat_groups.get_corner(DL) + 0.5 * DOWN,
            mat_groups.get_corner(UL) + 0.25 * UP,
        )
        v_line.shift(SMALL_BUFF * LEFT)
        v_line.match_style(h_lines)

        self.play(
            Write(h_lines),
            Write(v_line),
        )
        self.wait()

        # Prepare expressions for parameter counts
        const_to_value = {
            "n_vocab": 50_257,
            "d_embed": 12_288,
            "d_query": 128,
            "d_value": 128,
            "n_heads": 96,
            "n_layers": 96,
            "n_neurons": 4 * 12_288,
        }
        const_lists = [
            ["d_embed", "n_vocab"],
            ["d_query", "d_embed", "n_heads", "n_layers",],
            ["d_query", "d_embed", "n_heads", "n_layers",],
            ["d_value", "d_embed", "n_heads", "n_layers",],
            ["d_embed", "d_value", "n_heads", "n_layers"],
            ["n_neurons", "d_embed", "n_layers"],
            ["d_embed", "n_neurons", "n_layers"],
            ["n_vocab", "d_embed"],
        ]

        def get_product_expression(category, consts, font_size=30, suffix=None):
            values = [const_to_value[const] for const in consts]
            result = np.product(values)
            result_str = "{:,}".format(result)
            expr = VGroup()
            expr = Text(
                " * ".join(consts) + " = " + result_str,
                font_size=font_size,
            )
            expr.next_to(v_line, RIGHT)
            expr.align_to(category.line, DOWN)
            expr.shift(0.25 * expr.get_height() * UP)
            expr.rhs = expr[result_str]
            expr.rhs.set_color(BLUE)

            counts = VGroup(
                Integer(
                    const_to_value[const],
                    font_size=0.8 * font_size,
                )
                for const in consts
            )
            counts.next_to(expr, UP, buff=0.05)
            for count, const in zip(counts, consts):
                count.match_x(expr[const])
            counts.set_fill(GREY_B)

            result = VGroup(expr, counts)

            if suffix is not None:
                label = Text(suffix)
                label.match_height(expr)
                label.next_to(expr, RIGHT, buff=MED_SMALL_BUFF)
                result.add(label)

            return result

        product_expressions = VGroup(
            get_product_expression(category, consts)
            for category, consts in zip(category_names, const_lists)
        )
        exprs = [pe[0] for pe in product_expressions]
        counts = [pe[1] for pe in product_expressions]

        # Embedding
        def highlight_category(*indices):
            category_names.target = category_names.generate_target()
            category_names.target.set_fill(opacity=0.15, border_width=0)
            for index in indices:
                category_names.target[index].set_fill(opacity=1, border_width=0.5)
            return MoveToTarget(category_names)

        self.play(
            FadeOut(mat_groups),
            FadeOut(mat_dots[1:7]),
            highlight_category(0)
        )
        self.play(
            FadeIn(exprs[0]),
            FadeIn(counts[0], 0.25 * UP),
        )
        self.wait()

        # Unembedding
        total = Integer(2 * 12_288 * 50_257)
        total.to_edge(RIGHT, buff=1.0)
        total.set_color(BLUE)
        total_box = SurroundingRectangle(total, buff=0.25)
        total_box.set_fill(BLACK, 1)
        total_box.set_stroke(WHITE, 2)
        lines = VGroup(*(Line(exprs[i].get_right(), total_box) for i in [0, 7]))
        lines.set_stroke(BLUE, 2)

        self.play(
            highlight_category(0, 7),
            TransformMatchingStrings(exprs[0].copy(), exprs[7]),
            TransformFromCopy(counts[0][0].copy(), counts[7][1]),
            TransformFromCopy(counts[0][1].copy(), counts[7][0]),
            run_time=2
        )
        self.wait()
        self.play(
            ShowCreation(lines, lag_ratio=0),
            FadeIn(total_box),
            FadeTransform(exprs[0][-11:].copy(), total),
            FadeTransform(exprs[7][-11:].copy(), total),
        )
        self.wait()
        self.play(FlashAround(weights_count, time_width=1.5, run_time=2))
        self.wait()
        self.play(
            FadeOut(lines),
            FadeOut(total_box),
            FadeOut(total),
        )
        self.wait()

        # Attention matrices
        covered_categories = [0, 7]
        att_categories = [1, 2, 3, 4]
        per_head_factors = [
            ["d_query", "d_embed"],
            ["d_query", "d_embed"],
            ["d_value", "d_embed"],
            ["d_embed", "d_value"],
        ]
        per_head_exprs = VGroup(
            get_product_expression(name, factors, suffix="per head")
            for name, factors in zip(category_names[1:5], per_head_factors)
        )
        per_layer_exprs = VGroup(
            get_product_expression(name, factors + ["n_heads"], suffix="per layer")
            for name, factors in zip(category_names[1:5], per_head_factors)
        )
        full_att_exprs = product_expressions[1:5]
        for group in [per_head_exprs, per_layer_exprs, full_att_exprs]:
            sum_box = SurroundingRectangle(
                VGroup(expr[0].rhs for expr in group)
            )
            sum_box.set_stroke(BLUE, 2)
            sum_label = Integer(sum(
                np.product(list(count.get_value() for count in expr[1]))
                for expr in group
            ))
            sum_label.set_color(BLUE)
            sum_label.next_to(sum_box, DOWN)
            sum_box.add(sum_label)
            group.sum_box = sum_box

        self.play(
            *(
                product_expressions[i].animate.set_fill(opacity=0.25, border_width=0)
                for i in covered_categories
            ),
            highlight_category(att_categories[0]),
            FadeIn(per_head_exprs[0], shift=0.5 * RIGHT)
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeIn, per_head_exprs[1:], shift=0.5 *DOWN, lag_ratio=0.5),
            highlight_category(*att_categories),
        )
        self.wait()
        self.play(FadeIn(per_head_exprs.sum_box, run_time=3, rate_func=there_and_back_with_pause))
        self.wait()
        self.play(
            FadeOut(per_head_exprs),
            FadeIn(per_layer_exprs),
        )
        self.wait()
        self.play(FadeIn(per_layer_exprs.sum_box, run_time=3, rate_func=there_and_back_with_pause))
        self.wait()
        self.play(
            FadeOut(per_layer_exprs),
            FadeIn(full_att_exprs),
        )
        self.wait()
        self.play(FadeIn(full_att_exprs.sum_box))
        self.wait()

        # Compare with total weights
        total_weights_rect = SurroundingRectangle(weights_count)
        total_weights_rect.set_stroke(BLUE_B, 2)
        box = full_att_exprs.sum_box.copy()
        box.remove(box.submobjects[0])
        self.play(Transform(box, total_weights_rect))
        self.wait()
        self.play(
            FadeOut(box),
            FadeOut(full_att_exprs.sum_box),
        )
        self.wait()

        # MLP matrices
        mlp_categories = [5, 6]
        mlp_exprs = product_expressions[5:7]
        per_layer_exprs = VGroup(
            get_product_expression(category_names[i], const_lists[i][:2], suffix="per layer")
            for i in mlp_categories
        )

        self.play(
            full_att_exprs.animate.set_fill(opacity=0.25, border_width=0),
            highlight_category(*mlp_categories),
        )
        self.wait()
        self.play(FadeIn(per_layer_exprs[0]))
        self.wait()
        self.play(
            TransformMatchingStrings(per_layer_exprs[0][0].copy(), per_layer_exprs[1][0]),
            TransformFromCopy(per_layer_exprs[0][1][0], per_layer_exprs[1][1][1]),
            TransformFromCopy(per_layer_exprs[0][1][1], per_layer_exprs[1][1][0]),
            TransformFromCopy(per_layer_exprs[0][2], per_layer_exprs[1][2]),
            run_time=1
        )
        self.wait()
        self.play(
            FadeOut(per_layer_exprs),
            FadeIn(mlp_exprs),
        )
        self.wait()

        # Sum up MLP right hand sides
        rhs_rect = SurroundingRectangle(VGroup(expr[0].rhs for expr in mlp_exprs))
        rhs_rect.set_stroke(BLUE, 2)
        rhs_rect.stretch(1.2, 1, about_edge=DOWN)
        c2v = const_to_value
        mlp_total = Integer(2 * c2v["n_neurons"] * c2v["d_embed"] * c2v["n_layers"])
        mlp_total.next_to(rhs_rect)
        mlp_total.set_color(BLUE)
        mlp_total_rect = BackgroundRectangle(mlp_total)
        mlp_total_rect.set_fill(BLACK, 1)

        self.play(
            FadeIn(rhs_rect),
            FadeIn(mlp_total_rect),
            FadeTransform(mlp_exprs[0][0].rhs.copy(), mlp_total),
            FadeTransform(mlp_exprs[1][0].rhs.copy(), mlp_total),
        )
        self.wait()

        # Align all right hand sides
        self.play(
            category_names.animate.set_fill(opacity=1, border_width=0.5),
            product_expressions.animate.set_fill(opacity=1, border_width=0.5),
        )

        all_rhss = VGroup(
            VGroup(expr[0]["="][0], expr[0].rhs)
            for expr in product_expressions
        )
        all_rhss.target = all_rhss.generate_target()
        for mob in all_rhss.target:
            mob.align_to(product_expressions, RIGHT)
            mob.shift(0.5 * RIGHT)
        all_rhss_rect = SurroundingRectangle(all_rhss.target)
        all_rhss_rect.match_style(rhs_rect)

        self.play(
            FadeOut(mlp_total_rect, RIGHT),
            FadeOut(mlp_total, RIGHT),
            ReplacementTransform(rhs_rect, all_rhss_rect),
            MoveToTarget(all_rhss)
        )
        self.wait()

        # Move weights count
        self.play(LaggedStart(
            h_line.animate.scale(0.5, about_edge=LEFT),
            weights_text.animate.arrange(DOWN).scale(1.5).next_to(all_rhss_rect, UP),
            FadeOut(mat_text, LEFT),
            title.animate.to_edge(LEFT, buff=2.5),
            lag_ratio=0.2,
            run_time=2
        ))
        self.wait()

# Upstream: upstream/_2024/transformers/ml_basics.py:1666-1811
class DistinguishWeightsAndData(InteractiveScene):
    def construct(self):
        # Set up titles
        weights_title, data_title = titles = VGroup(
            Text(word, font_size=60)
            for word in ["Weights", "Data"]
        )
        weights_title.set_color(BLUE)
        data_title.set_color(GREY_B)

        for title, sign in zip(titles, [-1, 1]):
            title.set_x(sign * FRAME_WIDTH / 4)
            title.to_edge(UP, buff=0.25)
            underline = Underline(title, stretch_factor=1.5)
            underline.match_color(title)
            underline.set_y(title[0].get_y(DOWN) - 0.1)
            title.add(underline)

        v_line = Line(UP, DOWN).set_height(4.5)
        v_line.to_edge(UP, buff=0)
        v_line.set_stroke(GREY_A, 2)

        # Set up matrices
        matrices = VGroup(
            WeightMatrix(
                shape=(6, 8),
                ellipses_row=None,
                ellipses_col=None,
            )
            for n in range(4)
        )
        matrices.arrange_in_grid(v_buff=1, h_buff=1)
        vectors = VGroup(
            NumericEmbedding(length=8, ellipses_row=None)
            for n in range(8)
        )
        vectors.arrange(RIGHT)

        tensors = VGroup(matrices, vectors)
        for group, title in zip(tensors, titles):
            group.set_height(2.5)
            group.next_to(title, DOWN, buff=0.5)

        # Mix up all the numbers
        mat_nums = VGroup(
            elem
            for matrix in matrices
            for elem in matrix.get_entries()
        )
        mat_braces = VGroup(
            brace
            for matrix in matrices
            for brace in matrix.get_brackets()
        )
        vec_nums = VGroup(
            elem
            for vector in vectors
            for elem in vector.get_entries()
        )
        vec_braces = VGroup(
            brace
            for vector in vectors
            for brace in vector.get_brackets()
        )

        def random_point(x_min, x_max, y_min, y_max):
            return np.array([
                random.uniform(x_min, x_max),
                random.uniform(y_min, y_max),
                0
            ])

        all_nums = VGroup(*mat_nums, *vec_nums)
        all_nums.shuffle()
        for num in all_nums:
            states = num.replicate(4)
            for state in states[1:]:
                state.set_height(0.15)
            sign = 1 if num in vec_nums else -1
            states[1].move_to(random_point(6.5 * sign, 1 * sign, 0, 3.5))
            states[2].move_to(random_point(-8, 8, -4, 4))
            states[3].move_to(random_point(-8, 8, -4, 4))
            states[3].set_opacity(0)
            num.states = states
            num.become(states[3])

        self.add(all_nums)

        # Animations
        lag_ratio = 1 / len(all_nums)
        self.play(
            LaggedStart(
                (Transform(num, num.states[2], path_arc=PI)
                for num in all_nums),
                lag_ratio=lag_ratio,
                run_time=3
            ),
        )
        self.wait()
        self.play(
            LaggedStart(
                (LaggedStart(
                    (Transform(num, num.states[1])
                    for num in group),
                    lag_ratio=lag_ratio,
                    run_time=2
                )
                for group in [mat_nums, vec_nums]),
                lag_ratio=0.5
            ),
            ShowCreation(v_line),
        )
        self.play(
            Write(weights_title),
            LaggedStart(
                (Transform(num, num.states[0])
                for num in mat_nums),
                lag_ratio=lag_ratio,
                run_time=2
            ),
            FadeIn(mat_braces, lag_ratio=0.1, time_span=(1, 2)),
        )
        self.play(
            Write(data_title),
            LaggedStart(
                (Transform(num, num.states[0])
                for num in vec_nums),
                lag_ratio=lag_ratio,
                run_time=2
            ),
            FadeIn(vec_braces, lag_ratio=0.1, time_span=(1, 2)),
        )
        self.wait()

        # Add subtitles
        subtitles = VGroup(
            Text("What defines the model", font_size=40),
            Text("What the model processes", font_size=40),
        )
        for subtitle, title, group in zip(subtitles, titles, tensors):
            subtitle.next_to(title, DOWN)
            self.play(
                FadeIn(subtitle, lag_ratio=0.1),
                group.animate.next_to(subtitle, DOWN, buff=0.5),
            )
            self.wait()

# Upstream: upstream/_2024/transformers/ml_basics.py:1814-2365
class SoftmaxBreakdown(InteractiveScene):
    def construct(self):
        # Show example probability distribution
        word_strs = ['Dumbledore', 'Flitwick', 'Mcgonagall', 'Quirrell', 'Snape', 'Sprout', 'Trelawney']
        words = VGroup(*(Text(word_str, font_size=30) for word_str in word_strs))
        values = np.array([-0.8, -5.0, 0.5, 1.5, 3.4, -2.3, 2.5])
        prob_values = softmax(values)
        chart = BarChart(prob_values, width=10)
        chart.bars.set_stroke(width=1)

        probs = VGroup(*(DecimalNumber(pv) for pv in prob_values))
        probs.arrange(DOWN, buff=0.25)
        probs.generate_target()
        for prob, bar in zip(probs.target, chart.bars):
            prob.scale(0.5)
            prob.next_to(bar, UP)

        for word, bar in zip(words, chart.bars):
            word.scale(0.75)
            height = word.get_height()
            word.move_to(bar.get_bottom(), LEFT)
            word.rotate(-45 * DEGREES, about_point=bar.get_bottom())
            word.shift(height * DOWN)

        chart.save_state()
        for bar in chart.bars:
            bar.stretch(0, 1, about_edge=DOWN)
        chart.set_opacity(0)

        seq_title = Text("Sequence of numbers", font_size=60)
        seq_title.next_to(probs, LEFT, buff=0.75)
        seq_title.set_color(YELLOW)
        prob_title = Text("Probability distribution", font_size=60)
        prob_title.set_color(chart.bars[3].get_color())
        prob_title.center().to_edge(UP)

        self.play(
            LaggedStartMap(FadeIn, probs, shift=0.25 * DOWN, lag_ratio=0.3),
            FadeIn(seq_title),
            run_time=1
        )
        self.wait()
        self.play(
            Restore(chart, lag_ratio=0.1),
            MoveToTarget(probs),
            FadeTransform(seq_title, prob_title),
        )
        self.wait()
        self.play(
            LaggedStartMap(FadeIn, words),
        )
        self.wait()

        # Show constraint between 0 and 1
        index = 3
        bar = chart.bars[index]
        bar.save_state()
        prob = probs[index]
        prob.bar = bar
        max_height = chart.y_axis.get_y(UP) - chart.x_axis.get_y()
        prob.f_always.set_value(lambda: prob.bar.get_height() / max_height)
        prob.always.match_height(probs[1])
        prob.always.next_to(prob.bar, UP)

        one_line = DashedLine(*chart.x_axis.get_start_and_end())
        one_line.set_stroke(RED, 2)
        one_line.align_to(chart.y_axis, UP)

        low_line = one_line.copy()
        low_line.set_stroke(PINK, 5)
        low_line.match_y(chart.x_axis)

        self.play(FadeIn(low_line), FadeIn(one_line), FadeOut(prob_title))
        self.play(low_line.animate.match_y(one_line))
        self.play(FadeOut(low_line))
        self.wait()

        self.play(
            FadeIn(one_line, time_span=(0, 1)),
            bar.animate.set_height(max_height, about_edge=DOWN, stretch=True),
            run_time=2,
        )
        self.play(
            bar.animate.set_height(1e-4, about_edge=DOWN, stretch=True),
            run_time=2,
        )
        self.play(Restore(bar))
        self.wait()
        prob.clear_updaters()

        # Show sum
        prob_copies = probs.copy()
        prob_copies.scale(1.5)
        prob_copies.arrange(RIGHT, buff=1.0)
        prob_copies.to_edge(UP)
        prob_copies.shift(LEFT)
        plusses = VGroup(*(
            Tex("+").move_to(VGroup(p1, p2))
            for p1, p2 in zip(prob_copies, prob_copies[1:])
        ))
        equals = Tex("=").next_to(prob_copies, RIGHT)
        rhs = DecimalNumber(1.00)
        rhs.next_to(equals, RIGHT)

        self.play(
            TransformFromCopy(probs, prob_copies),
            Write(plusses),
            Write(equals),
            FadeOut(one_line),
        )
        self.play(
            LaggedStart(*(
                FadeTransform(pc.copy(), rhs)
                for pc in prob_copies
            ), lag_ratio=0.07)
        )
        self.wait()

        sum_group = VGroup(*prob_copies, *plusses, equals, rhs)
        chart_group = VGroup(chart, probs, words)

        # Show example matrix vector output
        n = len(words)
        vector = NumericEmbedding(length=n, ellipses_row=None)
        in_values = np.array([e.get_value() for e in vector.elements])
        rows = []
        for value in values:
            row = np.random.uniform(-1, 1, len(in_values))
            row *= value / np.dot(row, in_values)
            rows.append(row)
        matrix_values = np.array(rows)

        matrix = WeightMatrix(
            values=matrix_values,
            ellipses_row=None,
            ellipses_col=None,
            num_decimal_places=2,
        )
        for mob in matrix, vector:
            mob.set_height(4)
        vector.to_edge(UP).set_x(2.5)
        matrix.next_to(vector, LEFT)

        self.play(LaggedStart(
            chart_group.animate.scale(0.35).to_corner(DL),
            FadeOut(sum_group, UP),
            FadeIn(matrix, UP),
            FadeIn(vector, UP),
        ))
        eq, rhs = show_matrix_vector_product(self, matrix, vector, x_max=9)
        self.wait()

        # Comment on output
        rhs_rect = SurroundingRectangle(rhs)
        rhs_words = Text("Not at all a\nprobability distribution!")
        rhs_words.next_to(rhs_rect, DOWN)

        neg_rects = VGroup(*(
            SurroundingRectangle(entry)
            for entry in rhs.get_entries()
            if entry.get_value() < 0
        ))
        gt1_rects = VGroup(*(
            SurroundingRectangle(entry)
            for entry in rhs.get_entries()
            if entry.get_value() > 1
        ))
        VGroup(rhs_rect, neg_rects).set_stroke(RED, 4)
        gt1_rects.set_stroke(BLUE, 4)

        for rect in (*neg_rects, *gt1_rects):
            neg = rect in neg_rects
            rect.word = Text("Negative" if neg else "> 1", font_size=36)
            rect.word.match_color(rect)
            rect.word.next_to(rhs, RIGHT)
            rect.word.match_y(rect)
        neg_words = VGroup(*(r.word for r in neg_rects))
        gt1_words = VGroup(*(r.word for r in gt1_rects))

        sum_arrow = Vector(DOWN).next_to(rhs, DOWN)
        sum_sym = Tex(R"\sum", font_size=36).next_to(sum_arrow, LEFT)
        sum_num = DecimalNumber(sum(e.get_value() for e in rhs.get_entries()))
        sum_num.next_to(sum_arrow, DOWN)

        self.play(
            ShowCreation(rhs_rect),
            FadeIn(rhs_words),
        )
        self.wait()
        self.play(
            ReplacementTransform(VGroup(rhs_rect), neg_rects),
            LaggedStart(*(FadeIn(rect.word, 0.5 * RIGHT) for rect in neg_rects)),
        )
        self.wait()
        self.play(
            ReplacementTransform(neg_rects, gt1_rects),
            FadeTransformPieces(neg_words, gt1_words),
        )
        self.wait()
        self.play(
            LaggedStart(
                FadeOut(rhs_words),
                FadeOut(gt1_rects),
                FadeOut(gt1_words),
            ),
            GrowArrow(sum_arrow),
            FadeIn(sum_num, DOWN),
            FadeIn(sum_sym),
        )
        self.wait()
        self.play(*map(FadeOut, [sum_arrow, sum_sym, sum_num]))

        # Preview softmax application
        rhs.generate_target()
        rhs.target.to_edge(LEFT, buff=1.5)
        rhs.target.set_y(0)

        softmax_box = Rectangle(width=5, height=6.5)
        softmax_box.set_stroke(BLUE, 2)
        softmax_box.set_fill(BLUE_E, 0.5)
        in_arrow, out_arrow = Vector(RIGHT).replicate(2)
        in_arrow.next_to(rhs.target, RIGHT)
        softmax_box.next_to(in_arrow, RIGHT)
        out_arrow.next_to(softmax_box, RIGHT)

        softmax_label = Text("softmax", font_size=60)
        softmax_label.move_to(softmax_box)

        rhs_values = np.array([e.get_value() for e in rhs.get_entries()])
        dist = softmax(rhs_values)
        output = DecimalMatrix(dist.reshape((dist.shape[0], 1)))
        output.match_height(rhs)
        output.next_to(out_arrow, RIGHT)

        bars = chart.bars.copy()
        for bar, entry in zip(bars, output.get_entries()):
            bar.rotate(-PI / 2)
            bar.stretch(2, 0)
            bar.next_to(output)
            bar.match_y(entry)

        self.play(LaggedStart(
            FadeOut(matrix, 2 * LEFT),
            FadeOut(vector, 3 * LEFT),
            FadeOut(eq, 3.5 * LEFT),
            FadeOut(chart_group, DL),
            GrowArrow(in_arrow),
            FadeIn(softmax_box, RIGHT),
            FadeIn(softmax_label, RIGHT),
            MoveToTarget(rhs),
            GrowArrow(out_arrow),
            FadeIn(output, RIGHT),
            TransformFromCopy(chart.bars, bars),
        ), lag_ratio=0.2, run_time=2)
        self.wait()

        # Highlight larger and smaller parts
        rhs_entries = rhs.get_entries()
        changer = VGroup(rhs_entries, output.get_entries(), bars)
        changer.save_state()
        for index in range(4, 0, -1):
            changer.target = changer.saved_state.copy()
            changer.target.set_fill(border_width=0)
            for group in changer.target:
                for j, elem in enumerate(group):
                    if j != index:
                        elem.fade(0.8)
            self.play(MoveToTarget(changer))
            self.wait()
        self.play(Restore(changer))
        self.remove(changer)
        self.add(rhs, output, bars)
        self.wait()

        # Swap out for variables
        variables = VGroup(*(
            Tex(f"x_{{{n}}}", font_size=48).move_to(elem)
            for n, elem in enumerate(rhs_entries, start=1)
        ))

        self.remove(rhs_entries)
        self.play(
            LaggedStart(*(
                TransformFromCopy(entry, variable, path_arc=PI / 2)
                for entry, variable in zip(rhs_entries, variables)
            ), lag_ratio=0.1, run_time=1.0)
        )
        self.wait()

        # Exponentiate each part
        exp_parts = VGroup(*(
            Tex(f"e^{{{var.get_tex()}}}", font_size=48).move_to(var)
            for var in variables
        ))
        exp_parts.align_to(softmax_box, LEFT)
        exp_parts.shift(0.75 * RIGHT)
        exp_parts.space_out_submobjects(1.5)
        gt0s = VGroup(
            Tex(R"> 0").next_to(exp_part, aligned_edge=DOWN)
            for exp_part in exp_parts
        )

        self.play(
            softmax_label.animate.next_to(softmax_box, UP, buff=0.15),
            LaggedStart(*(
                TransformMatchingStrings(var.copy(), exp_part)
                for var, exp_part in zip(variables, exp_parts)
            ), run_time=1, lag_ratio=0.01)
        )
        self.play(LaggedStartMap(FadeIn, gt0s, shift=0.5 * RIGHT, lag_ratio=0.25, run_time=1))
        self.wait()
        self.play(FadeOut(gt0s))

        # Compute the sum
        exp_sum = Tex(R"\sum_{n=0}^{N-1} e^{x_{n}}", font_size=42)
        exp_sum[R"e^{x_{n}}"].scale(1.5, about_edge=LEFT)
        exp_sum.next_to(softmax_box.get_right(), LEFT, buff=0.75)

        lines = VGroup(*(Line(exp_part.get_right(), exp_sum.get_left(), buff=0.1) for exp_part in exp_parts))
        lines.set_stroke(TEAL, 2)

        self.play(
            LaggedStart(*(
                FadeTransform(exp_part.copy(), exp_sum)
                for exp_part in exp_parts
            ), lag_ratio=0.01),
            LaggedStartMap(ShowCreation, lines, lag_ratio=0.01),
            run_time=1
        )
        self.wait()
        self.play(FadeOut(lines))

        # Divide each part by the sum
        lil_denoms = VGroup()
        for exp_part in exp_parts:
            slash = Tex("/").match_height(exp_sum)
            slash.next_to(exp_sum, LEFT, buff=0)
            denom = VGroup(slash, exp_sum).copy()
            denom.set_height(exp_part.get_height() * 1.5)
            denom.next_to(exp_part, RIGHT, buff=0)
            lil_denoms.add(denom)
        lil_denoms.align_to(softmax_box.get_center(), LEFT)

        lines = VGroup(*(Line(exp_sum.get_left(), denom.get_center()) for denom in lil_denoms))
        lines.set_stroke(TEAL, 1)

        self.remove(exp_sum)
        self.play(
            exp_parts.animate.next_to(lil_denoms, LEFT, buff=0),
            LaggedStart(*(
                FadeTransform(exp_sum.copy(), denom)
                for denom in lil_denoms
            ), lag_ratio=0.01),
        )
        self.wait()

        # Resize box
        sm_terms = VGroup(*(
            VGroup(exp_part, denom)
            for exp_part, denom in zip(exp_parts, lil_denoms)
        ))
        sm_terms.generate_target()

        target_height = 5.0
        full_output = Group(output, bars)
        full_output.generate_target()
        full_output.target.set_height(target_height, about_edge=RIGHT)
        full_output.target.shift(1.5 * LEFT)
        equals = Tex("=")
        equals.next_to(full_output.target, LEFT)

        softmax_box.generate_target()
        softmax_box.target.set_width(3.0, stretch=True)
        VGroup(softmax_box.target, sm_terms.target).set_height(target_height + 0.5).next_to(equals, LEFT)

        rhs.generate_target()
        rhs_entries.become(variables)
        self.remove(variables)
        rhs.target.set_height(target_height)
        rhs.target.next_to(softmax_box.target, LEFT, buff=1.5)

        self.play(
            softmax_label.animate.next_to(softmax_box.target, UP),
            MoveToTarget(softmax_box),
            MoveToTarget(sm_terms),
            MoveToTarget(full_output),
            MoveToTarget(rhs),
            FadeTransform(out_arrow, equals),
            in_arrow.animate.become(
                Arrow(rhs.target, softmax_box.target).match_style(in_arrow)
            ),
        )
        self.wait()

        # Set up updaters
        output_entries = output.get_entries()
        bar_width_ratio = bars.get_width() / max(o.get_value() for o in output_entries)
        temp_tracker = ValueTracker(1)

        def update_outs(output_entries):
            inputs = [entry.get_value() for entry in rhs_entries]
            outputs = softmax(inputs, temp_tracker.get_value())
            for entry, output in zip(output_entries, outputs):
                entry.set_value(output)

        def update_bars(bars):
            for bar, entry in zip(bars, output_entries):
                width = max(bar_width_ratio * entry.get_value(), 1e-3)
                bar.set_width(width, about_edge=LEFT, stretch=True)

        output_entries.clear_updaters().save_state()
        bars.clear_updaters().save_state()
        output_entries.add_updater(update_outs)
        bars.add_updater(update_bars)

        self.add(bars, output_entries)

        # Tweak values
        index_value_pairs = [
            (6, 4.0),
            (4, 4.2),
            (2, 4.0),
            (0, 6.0),
            (4, 9.9)
        ]
        # index_value_pairs = [  # For emphasizing a max
        #     (3, 8.5),
        #     (6, 8.0),
        #     (2, 8.1),
        #     (0, 9.0),
        # ]
        for index, value in index_value_pairs:
            entry = rhs_entries[index]
            rect = SurroundingRectangle(entry)
            rect.set_stroke(BLUE if value > entry.get_value() else RED, 3)
            self.play(
                ChangeDecimalToValue(entry, value),
                FadeIn(rect, time_span=(0, 1)),
                run_time=4
            )
            self.play(FadeOut(rect))

        # Add temperature
        frame = self.frame
        temp_color = RED
        new_title = Text("softmax with temperature")
        new_title["temperature"].set_color(temp_color)
        get_t = temp_tracker.get_value
        t_line = NumberLine(
            (0, 10, 0.2),
            tick_size=0.025,
            big_tick_spacing=1,
            longer_tick_multiple=2.0,
            width=4
        )
        t_line.set_stroke(width=1.5)
        t_line.next_to(softmax_box, UP)
        t_tri = ArrowTip(angle=-90 * DEGREES)
        t_tri.set_color(temp_color)
        t_tri.set_height(0.2)
        t_label = Tex("T = 0.00", font_size=36)
        t_label.rhs = t_label.make_number_changeable("0.00")
        t_label["T"].set_color(temp_color)
        t_tri.add_updater(lambda m: m.move_to(t_line.n2p(get_t()), DOWN))
        t_label.add_updater(lambda m: m.rhs.set_value(get_t()))
        t_label.add_updater(lambda m: m.next_to(t_tri, UP, buff=0.1, aligned_edge=LEFT))
        t_label.update()

        new_title.next_to(t_label, UP, buff=0.5).match_x(softmax_box)

        self.play(
            frame.animate.move_to(0.75 * UP),
            TransformMatchingStrings(softmax_label, new_title),
            FadeIn(t_line),
            FadeIn(t_tri),
            FadeIn(t_label),
            run_time=1
        )

        # Change formula
        template = Tex(R"e^{x_{0} / T} / \sum_{n=0}^{N - 1} e^{x_n / T}")
        template["T"].set_color(temp_color)
        template["/"][1].scale(1.9, about_edge=LEFT)
        template[R"\sum_{n=0}^{N - 1}"][0].scale(0.7, about_edge=RIGHT)
        index_part = template.make_number_changeable("0")

        new_sm_terms = VGroup()
        all_Ts = VGroup()
        for n, term in enumerate(sm_terms, start=1):
            template.replace(term, dim_to_match=1)
            index_part.set_value(n)
            new_term = template.copy()
            all_Ts.add(*new_term["T"])
            new_sm_terms.add(new_term)

        self.play(
            LaggedStart(*(
                FadeTransform(old_term, new_term)
                for old_term, new_term in zip(sm_terms, new_sm_terms)
            )),
            LaggedStart(*(
                TransformFromCopy(t_label[0], t_mob[0])
                for t_mob in all_Ts
            )),
        )
        self.wait()

        # Oscilate between values
        for value in [4, 10, 2]:
            self.play(temp_tracker.animate.set_value(value), run_time=8)
            self.wait()
        self.play(temp_tracker.animate.set_value(0), run_time=3)
        max_rects = VGroup(
            SurroundingRectangle(rhs.get_entries()[4]),
            SurroundingRectangle(VGroup(output.get_entries()[4], bars[4])),
        )
        self.play(LaggedStartMap(ShowCreationThenFadeOut, max_rects))
        self.wait()
        for value in [5, 1, 7]:
            self.play(temp_tracker.animate.set_value(value), run_time=4)
            self.wait()

        # Describe logits
        prob_arrows, logit_arrows = (
            VGroup(*(
                Vector(-vect).next_to(entry, vect, buff=0.25)
                for entry in matrix.get_entries()
            ))
            for matrix, vect in [(output, RIGHT), (rhs, LEFT)]
        )
        prob_arrows.next_to(bars, RIGHT)
        prob_rects = VGroup(*map(SurroundingRectangle, output.get_entries()))
        logit_rects = VGroup(*map(SurroundingRectangle, rhs.get_entries()))
        VGroup(prob_rects, logit_rects).set_stroke(width=1)

        prob_words = Text("Probabilities")
        prob_words.next_to(output, UP, buff=0.25)
        logit_words = Text("Logits")
        logit_words.next_to(rhs, UP, buff=0.25)

        logit_group = VGroup(logit_arrows, logit_words, logit_rects)
        logit_group.set_color(TEAL)
        prob_group = VGroup(prob_arrows, prob_words, prob_rects)
        prob_group.set_color(YELLOW)

        for arrows, word, rects in [prob_group, logit_group]:
            self.play(
                t_line.animate.set_y(3.35),
                Write(word),
                Write(rects, stroke_width=5, stroke_color=rects[0].get_stroke_color(), lag_ratio=0.3, run_time=3),
            )
            self.wait()

# Upstream: upstream/_2024/transformers/ml_basics.py:2368-2430
class CostFunction(InteractiveScene):
    def construct(self):
        # Add graph
        axes = Axes((0, 1, 0.1), (0, 5, 1), width=10, height=6)
        axes.center().to_edge(LEFT)
        axes.x_axis.add_numbers(num_decimal_places=1)
        axes.y_axis.add_numbers(num_decimal_places=0, direction=LEFT)
        x_label = Tex("p")
        x_label.next_to(axes.x_axis.get_right(), UR)
        axes.add(x_label)

        graph = axes.get_graph(lambda x: -np.log(x), x_range=(0.001, 10, 0.01))
        graph.set_color(RED)

        expr = Tex(R"\text{Cost} = -\log(p)", font_size=60)
        expr.next_to(axes.i2gp(0.1, graph), UR, buff=0.1)

        self.add(axes, graph, expr)

        # Add sample phrase
        phrase = Text("Watching 3Blue1Brown makes you smarter")
        phrase.scale(0.75)
        phrase.to_edge(UP)
        phrase.align_to(axes.c2p(0.1, 0), LEFT)
        pieces = break_into_tokens(phrase)
        pieces[-1].set_opacity(0.0)
        rects = get_piece_rectangles(pieces, leading_spaces=True, h_buff=0)

        self.add(rects, pieces)

        # Add predictions
        arrow = Vector(0.5 * DOWN)
        arrow.next_to(rects[-1], DOWN, SMALL_BUFF)
        index = 0

        tokens, probs = gpt3_predict_next_token(phrase.get_text()[:-len(" smarter")])
        bar_chart = next_token_bar_chart(
            tokens[:8], probs[:8],
            width_100p=7.0,
            bar_space_factor=1.0,
            use_percent=False,
        )
        bar_chart.next_to(arrow, DOWN)
        bar_chart.shift(1.25 * RIGHT)
        bar_chart.set_opacity(0.5)
        bar_chart[index].set_opacity(1.0)
        rect = SurroundingRectangle(bar_chart[index])

        self.add(arrow, bar_chart, rect)

        # Animate in graph
        self.play(
            ShowCreation(graph, run_time=3),
            Write(expr, run_time=2),
        )
        self.wait()

        # Show point on the graph
        line = axes.get_line_from_axis_to_point(0, axes.i2gp(probs[index], graph), line_func=Line)
        line.set_stroke(YELLOW)

        self.play(FadeTransform(rect.copy(), line))
        self.wait()

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
