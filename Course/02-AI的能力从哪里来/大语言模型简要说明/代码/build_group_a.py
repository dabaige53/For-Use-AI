"""Build standalone upstream excerpts for render group A."""

from __future__ import annotations

import ast
from pathlib import Path


ROOT = Path(__file__).parent
TRANSFORMERS = ROOT / "upstream" / "_2024" / "transformers"
OUTPUT = ROOT / "group_a.py"
DEPENDENCY_FILES = ["helpers.py", "generation.py", "embedding.py", "ml_basics.py"]
TARGETS = [
    "WriteTransformer", "LabelVector", "AdjustingTheMachine",
    "DownByTheRiverHeader", "FourStepsWithParameters", "ChatbotFeedback",
    "ContrastWithEarlierFrame", "SequentialProcessing", "ParameterWeight",
    "LargeInLargeLanguageModel", "ThousandsOfWords", "WriteRLHF",
    "SerialProcessing", "ParallelProcessing", "ManyComputationsPerUnitTimeV2",
    "VectorLabel", "ParameterToVectorAnnotation", "ExamplePhraseHeader",
    "ShowPreviousVideos",
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
        assert body is not None, f"Missing source for {node.name} in {path}"
        if path.name == "chm.py" and node.name in {
            "DownByTheRiverHeader", "ContrastWithEarlierFrame",
            "ThousandsOfWords", "ExamplePhraseHeader",
        }:
            body += "\n        self.wait(1)"
        result.append(
            f"# Upstream: {path.relative_to(ROOT)}:{node.lineno}-{node.end_lineno}\n{body}\n"
        )
    return result


def main() -> None:
    header = '''"""Generated upstream scene excerpts for render group A.

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
    full_tex = full_tex.replace(r'\\DisableLigatures{encoding = *, family = *}', '')
    return _original_tex_renderer(full_tex, compiler, message)
_tex_writing.full_tex_to_svg = _group_a_tex_renderer

'''
    chunks = [header]
    for filename in DEPENDENCY_FILES:
        chunks.extend(definitions(TRANSFORMERS / filename))
    chunks.extend(definitions(TRANSFORMERS / "chm.py", set(TARGETS)))
    text = "\n".join(chunks)
    # Compatibility adapters: preserve the scene layout/actions while replacing
    # one author-local data path and seven URL-backed ImageMobjects.
    text = text.replace(
        'Path("/Users/grant/3Blue1Brown Dropbox/3Blue1Brown/videos/2024/transformers/data/tale_of_two_cities.txt")',
        'DATA_DIR / "tale_of_two_cities.txt"',
    )
    text = text.replace(
        'ImageMobject(f"https://img.youtube.com/vi/{slug}/maxresdefault.jpg", height=1)',
        'ImageMobject(ROOT / "assets" / "placeholders-a" / f"{slug}.jpg", height=1)',
    )
    # The retired GPT-3 endpoint is unavailable. Keep the eight feedback cycles,
    # but supply fixed display text through the same original animation methods.
    text = text.replace(
        'except IndexError:\n            return answer, True',
        'except Exception:\n            fallback = " The internet developed through several research networks and standards."\n            if fallback.strip() in answer:\n                return answer, True\n            return answer + fallback, False',
    )
    text = text.replace(
        'Checkmark().set_color(GREEN),\n            Exmark().set_color(RED),',
        'Text("✓", font_size=72).set_color(GREEN),\n            Text("✗", font_size=72).set_color(RED),',
    )
    text += '''

# Fixed illustrative prediction data: never calls a model or remote API.
def gpt3_predict_next_token(text):
    sample = " The internet developed through several research networks and standards."
    if sample.strip() in text:
        return ["<|endoftext|>"], [1.0]
    return [sample], [1.0]
'''
    tree = ast.parse(text)
    present = {node.name for node in tree.body if isinstance(node, ast.ClassDef)}
    missing = sorted(set(TARGETS) - present)
    if missing:
        raise RuntimeError(f"Missing target definitions: {missing}")
    OUTPUT.write_text(text)
    print(OUTPUT)


if __name__ == "__main__":
    main()
