"""Burn an SRT into a silent, time-preserving review copy of a supplied video."""

import argparse
import json
import re
import subprocess
from fractions import Fraction
from pathlib import Path

import av
from PIL import Image, ImageDraw, ImageFont


def seconds(value: str) -> float:
    hours, minutes, secs, millis = map(int, re.split("[:,]", value))
    return hours * 3600 + minutes * 60 + secs + millis / 1000


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--subtitles", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--end", type=float, default=419)
    parser.add_argument("--font", type=Path)
    parser.add_argument("--font-index", type=int, default=0)
    args = parser.parse_args()
    if args.end <= 0 or args.input.resolve() == args.output.resolve():
        parser.error("Positive --end and distinct input/output paths are required")
    if args.font:
        font_path, font_index = str(args.font), args.font_index
    else:
        font_path, index_text = subprocess.check_output(
            ["fc-match", "-f", "%{file}\n%{index}", "Noto Sans CJK SC:style=Regular"],
            text=True,
        ).strip().splitlines()
        font_index = int(index_text)
    cues = []
    for block in re.split(r"\n\s*\n", args.subtitles.read_text().strip()):
        lines = block.splitlines()
        start, end = map(seconds, lines[1].split(" --> "))
        cues.append((start, end, "\n".join(lines[2:])))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    cue_index = 0
    cache: dict[str, Image.Image] = {}
    with av.open(str(args.input)) as source:
        video = source.streams.video[0]
        rate = video.average_rate
        if rate is None:
            raise ValueError("Input video has no declared frame rate")
        width, height = video.width, video.height
        font = ImageFont.truetype(
            font_path, max(16, round(height * 0.05)), index=font_index
        )
        with av.open(str(args.output), mode="w") as destination:
            stream = destination.add_stream("libx264", rate=rate)
            stream.width, stream.height = width, height
            stream.pix_fmt = "yuv420p"
            stream.options = {"crf": "18", "preset": "fast"}
            for frame in source.decode(video=0):
                timestamp = float(frame.time or 0)
                if timestamp >= args.end:
                    break
                while cue_index < len(cues) and timestamp >= cues[cue_index][1]:
                    cue_index += 1
                picture = frame.to_image().convert("RGBA")
                if cue_index < len(cues) and cues[cue_index][0] <= timestamp:
                    text = cues[cue_index][2]
                    if text not in cache:
                        overlay = Image.new("RGBA", (width, height))
                        draw = ImageDraw.Draw(overlay)
                        box = draw.multiline_textbbox((0, 0), text, font=font, spacing=3)
                        text_width, text_height = box[2] - box[0], box[3] - box[1]
                        if text_width > width - 20:
                            raise ValueError(f"Subtitle exceeds safe width: {text}")
                        x, y = (width - text_width) / 2, height - text_height - 9
                        draw.rounded_rectangle(
                            (x - 7, y - 5, x + text_width + 7, height - 4),
                            radius=3, fill=(0, 0, 0, 175),
                        )
                        draw.multiline_text(
                            (x - box[0], y - box[1]), text, font=font,
                            fill="white", spacing=3, align="center",
                            stroke_width=1, stroke_fill="black",
                        )
                        cache[text] = overlay
                    picture = Image.alpha_composite(picture, cache[text])
                rendered = av.VideoFrame.from_image(picture.convert("RGB"))
                rendered.pts = count
                rendered.time_base = Fraction(1, 1) / rate
                for packet in stream.encode(rendered):
                    destination.mux(packet)
                count += 1
            for packet in stream.encode():
                destination.mux(packet)
    args.output.with_suffix(".json").write_text(json.dumps({
        "purpose": "Original-video subtitle review, NOT reconstructed animation",
        "input": str(args.input.resolve()), "subtitles": str(args.subtitles.resolve()),
        "frames": count, "fps": str(rate), "end_seconds": args.end,
        "audio": False, "font": font_path, "font_index": font_index,
    }, ensure_ascii=False, indent=2) + "\n")
    print(f"Wrote {count} frames: {args.output}")


if __name__ == "__main__":
    main()
