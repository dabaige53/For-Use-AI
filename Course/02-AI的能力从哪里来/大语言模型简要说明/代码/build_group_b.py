"""Build a standalone module for the assigned upstream chm.py scenes.

Top-level definitions are copied with ``ast.get_source_segment`` so scene bodies
remain the original source.  Imports which eagerly load optional ML libraries or
legacy API clients are intentionally replaced by lightweight standard imports.
"""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parent
TRANSFORMERS = ROOT / "upstream" / "_2024" / "transformers"
OUTPUT = ROOT / "group_b.py"

DEPENDENCY_FILES = ["helpers.py", "generation.py", "embedding.py", "ml_basics.py"]
TARGETS = [
    "PredictTheNextWord",
    "LotsOfTextIntoTheMachine",
    "EvenMoreTextIntoMachine",
    "RiverBankProbParts",
    "PartialScript",
    "ShowMachineWithDials",
    "ShowSingleTrainingExample",
    "EnormousAmountOfTrainingText",
    "RLHFWorkers",
    "TrainingDataCHM",
    "DivyUpParameters",
]


def definitions(path: Path, selected: set[str] | None = None) -> list[str]:
    source = path.read_text()
    tree = ast.parse(source, filename=str(path))
    result = []
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        if selected is not None and node.name not in selected:
            continue
        body = ast.get_source_segment(source, node)
        rel = path.relative_to(ROOT)
        result.append(f"# Upstream: {rel}:{node.lineno}-{node.end_lineno}\n{body}\n")
    return result


def main() -> None:
    header = '''"""Generated upstream scene excerpts for render group B.

Regenerate with ``.venv/bin/python build_group_b.py``.  Scene and dependency
definitions below retain their upstream source text and source-line metadata.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
try:
    import tex_support  # Project-provided TeX compatibility, when available.
except ImportError:
    tex_support = None

from manimlib import *
if tex_support is not None:
    from manimlib.mobject.svg import tex_mobject as _tex_mobject
    from manimlib.mobject.svg import old_tex_mobject as _old_tex_mobject
    from manimlib.utils import tex_file_writing as _tex_file_writing
    _tex_mobject.latex_to_svg = _tex_file_writing.latex_to_svg
    _old_tex_mobject.latex_to_svg = _tex_file_writing.latex_to_svg
_ManimLaggedStartMap = LaggedStartMap
def LaggedStartMap(anim_func, group, *args, **kwargs):
    """Accept historical list/generator groups used by the 2024 source."""
    if not isinstance(group, Mobject):
        group = Group(*group)
    return _ManimLaggedStartMap(anim_func, group, *args, **kwargs)

_OriginalImageMobject = ImageMobject
_OriginalSVGMobject = SVGMobject
_OriginalTexturedSurface = TexturedSurface
_PLACEHOLDER_DIR = Path(__file__).parent / "logs" / "group-b" / "placeholders"
_PLACEHOLDER_DIR.mkdir(parents=True, exist_ok=True)

def _placeholder_png(name):
    from PIL import Image as _PILImage, ImageDraw as _ImageDraw
    path = _PLACEHOLDER_DIR / f"{name}.png"
    if not path.exists():
        image = _PILImage.new("RGB", (1200, 700), "#330b0b")
        draw = _ImageDraw.Draw(image)
        draw.rectangle((18, 18, 1182, 682), outline="#ff5555", width=16)
        draw.line((40, 40, 1160, 660), fill="#ff5555", width=12)
        draw.line((1160, 40, 40, 660), fill="#ff5555", width=12)
        draw.text((80, 315), f"[MISSING: {name}]", fill="white")
        image.save(path)
    return str(path)

def _placeholder_svg(name):
    path = _PLACEHOLDER_DIR / f"{name}.svg"
    if not path.exists():
        path.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 400">'
                        '<path d="M10 10H590V390H10Z M35 35L565 365 M565 35L35 365" '
                        'fill="none" stroke="#ff5555" stroke-width="16"/></svg>')
    return str(path)

def ImageMobject(filename, *args, **kwargs):
    try:
        return _OriginalImageMobject(filename, *args, **kwargs)
    except IOError:
        return _OriginalImageMobject(_placeholder_png(str(filename)), *args, **kwargs)

def SVGMobject(filename, *args, **kwargs):
    try:
        return _OriginalSVGMobject(filename, *args, **kwargs)
    except IOError:
        return _OriginalSVGMobject(_placeholder_svg(str(filename)), *args, **kwargs)

def TexturedSurface(surface, image_file, dark_image_file=None, *args, **kwargs):
    try:
        return _OriginalTexturedSurface(surface, image_file, dark_image_file, *args, **kwargs)
    except IOError:
        light = _placeholder_png(str(image_file))
        dark = _placeholder_png(str(dark_image_file or image_file))
        return _OriginalTexturedSurface(surface, light, dark, *args, **kwargs)
from typing import Optional
import itertools as it
import hashlib
import math
import random
import re
import warnings

DATA_DIR = Path(__file__).parent / "logs" / "group-b" / "data"
WORD_FILE = DATA_DIR / "OWL3_Dictionary.txt"

'''
    chunks = [header]
    for filename in DEPENDENCY_FILES:
        chunks.extend(definitions(TRANSFORMERS / filename))
    chunks.extend(definitions(TRANSFORMERS / "chm.py", set(TARGETS)))
    chunks.append(r'''
# Compatibility: user-authorized deterministic demonstration predictions.
# This replaces both historical remote GPT-3 and optional local GPT-2 inference;
# scene layouts and animation bodies remain the upstream definitions above.
_DEMO_TOKENS = (
    " the", " a", " in", " of", " and", " to", " was", " is",
    " with", " for", " that", " on", " from", " it", " city", " France",
)

def _demo_predict_next_token(text, n_shown=7, random_seed=0):
    digest = hashlib.sha256(f"{random_seed}:{text}".encode()).digest()
    offset = int.from_bytes(digest[:4], "big") % len(_DEMO_TOKENS)
    tokens = [_DEMO_TOKENS[(offset + index) % len(_DEMO_TOKENS)] for index in range(n_shown)]
    weights = np.exp(-0.42 * np.arange(n_shown, dtype=float))
    probs = weights / weights.sum()
    return tokens, probs

def gpt2_predict_next_token(text, n_shown=7):
    return _demo_predict_next_token(text, n_shown, random_seed=0)

def gpt3_predict_next_token(text, n_shown=10, random_seed=0):
    return _demo_predict_next_token(text, n_shown, random_seed=random_seed)

def _missing_pile_text(self):
    # Count is demonstration data: the original private file's row count is unknown.
    return ["[MISSING: pile_of_text.txt]"] * 80

LotsOfTextIntoTheMachine.get_text_snippets = _missing_pile_text
''')
    present = {node.name for node in ast.parse("\n".join(chunks)).body if isinstance(node, ast.ClassDef)}
    missing = sorted(set(TARGETS) - present)
    if missing:
        raise RuntimeError(f"Missing target definitions: {missing}")
    generated = "\n".join(chunks)
    # Upstream typo: this scene creates ``out_dots`` and later fades ``dots``.
    generated = generated.replace(
        "FadeOut(dots),\n            FadeOut(random_words)",
        "FadeOut(out_dots),\n            FadeOut(random_words)",
        1,
    )
    # Preserve all six streak rings while submitting them as one vector object.
    generated = generated.replace(
        '''        return AnimationGroup(
            self.animate.set_value(value).set_anim_args(path_arc=path_arc, **kwargs),
            *(
                VShowPassingFlash(diff_arc, time_width=1.5, **kwargs)
                for diff_arc in diff_arcs
            )
        )''',
        '''        return AnimationGroup(
            self.animate.set_value(value).set_anim_args(path_arc=path_arc, **kwargs),
            VShowPassingFlash(diff_arcs, time_width=1.5, **kwargs),
        )''',
        1,
    )
    # Add the same 81 screens only as the expanding camera reaches them.
    generated = generated.replace(
        '''        self.add(screens)

        # Add frame growth''',
        '''        inner_screens = screens[:25]
        self.add(*inner_screens)
        added_screens = set(inner_screens)
        def add_screens_visible_by(end_time):
            height = FRAME_HEIGHT * np.exp(0.2 * end_time)
            width = height * FRAME_WIDTH / FRAME_HEIGHT
            for screen in screens:
                if screen in added_screens:
                    continue
                if abs(screen.get_x()) <= 0.5 * (width + FRAME_WIDTH) and abs(screen.get_y()) <= 0.5 * (height + FRAME_HEIGHT):
                    self.add(screen)
                    added_screens.add(screen)
        add_screens_visible_by(self.time)

        # Add frame growth''',
        1,
    )
    generated = generated.replace(
        '''        # Show lots of new data
        inner_screens = screens[:25]
        n_examples = 20''',
        '''        # Show lots of new data
        n_examples = 20''',
        1,
    )
    generated = generated.replace(
        '''        for n in range(n_examples):
            self.play(LaggedStart(''',
        '''        for n in range(n_examples):
            add_screens_visible_by(self.time + 0.5)
            self.play(LaggedStart(''',
        1,
    )
    OUTPUT.write_text(generated)
    print(OUTPUT)


if __name__ == "__main__":
    main()
