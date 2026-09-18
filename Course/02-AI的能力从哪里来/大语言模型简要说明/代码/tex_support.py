"""Render original TeX with Tectonic and vector PDF->SVG; no formula substitution.

The source formulas/preamble are preserved. Each compilation has an isolated
working directory so concurrent scene workers cannot overwrite working.tex.
"""

from pathlib import Path
import hashlib
import subprocess
import tempfile
import functools
import os
import re
import manimlib.utils.tex_file_writing as tex
import xml.etree.ElementTree as ET


def expand_rule_strokes(svg):
    # PDF represents TeX rules as stroked lines. Brace stretches their geometry;
    # give axis-aligned rules their real filled outline before Manim imports them.
    root = ET.fromstring(svg)
    for node in root.iter():
        if not node.tag.endswith("path") or node.get("fill") != "none":
            continue
        match = re.fullmatch(
            r"M([\d.+-]+) ([\d.+-]+)([VH])([\d.+-]+)", node.get("d", "")
        )
        if not match or not node.get("stroke-width"):
            continue
        x, y, end = map(float, (match[1], match[2], match[4]))
        half = float(node.attrib["stroke-width"]) / 2
        if match[3] == "V":
            x0, x1, y0, y1 = x - half, x + half, min(y, end), max(y, end)
        else:
            x0, x1, y0, y1 = min(x, end), max(x, end), y - half, y + half
        node.set("d", f"M{x0} {y0} H{x1} V{y1} H{x0} Z")
        node.set("fill", node.get("stroke", "#000000"))
        for key in list(node.attrib):
            if key.startswith("stroke"):
                del node.attrib[key]
    return ET.tostring(root, encoding="unicode")


CACHE = Path(__file__).resolve().parent / "generated/tex-cache"
CACHE.mkdir(parents=True, exist_ok=True)


@functools.lru_cache(maxsize=1024)
def original_tex_to_svg(full_tex, compiler="latex", message=""):
    import pymupdf

    # microtype's DisableLigatures is pdfTeX-only; XeTeX rejects it.
    full_tex = re.sub(r"\\DisableLigatures\{[^}]*\}", "", full_tex)
    key = hashlib.sha256(full_tex.encode()).hexdigest()
    out = CACHE / f"{key}.svg"
    if out.exists():
        return expand_rule_strokes(out.read_text())
    with tempfile.TemporaryDirectory(prefix="tex-", dir=CACHE) as work:
        p = Path(work)
        (p / "formula.tex").write_text(full_tex)
        r = subprocess.run(
            ["tectonic", "--keep-logs", "--outdir", str(p), str(p / "formula.tex")],
            capture_output=True,
            text=True,
        )
        if r.returncode:
            raise RuntimeError(
                "Tectonic original formula compile failed: " + r.stderr[-2500:]
            )
        with pymupdf.open(p / "formula.pdf") as doc:
            svg = doc[0].get_svg_image(text_as_path=True)
        # Atomic cache write; parallel workers can compile the same expression.
        temp = CACHE / f"{key}.{os.getpid()}.tmp"
        temp.write_text(svg)
        temp.replace(out)
        return expand_rule_strokes(svg)


tex.full_tex_to_svg = original_tex_to_svg
