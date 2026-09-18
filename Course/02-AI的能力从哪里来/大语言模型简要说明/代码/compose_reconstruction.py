"""Compose the audited 0–419s timeline from locally rendered scene layers.

New renders use 480p30. This reads source media and writes only its selected output
folder. No source-video pixels, audio, burned captions or subtitle streams enter
this reconstruction. Chinese display labels are part of the instructional image.
"""

from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
import av
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent
COURSE = ROOT.parent
FPS = 30
SIZE = (854, 480)
FONT = "/Users/w/Library/Fonts/NotoSansCJK.ttc"


def run(command: list[str]) -> None:
    subprocess.run(command, check=True, stdout=subprocess.DEVNULL)


def prepare(layer: dict, count: int, cache: Path) -> Path:
    source = Path(layer["source"])
    if not source.is_absolute():
        source = ROOT / source
    if not source.is_file():
        raise FileNotFoundError(source)
    start, end = layer.get("trim", [0, None])
    if end is None:
        info = json.loads(
            subprocess.check_output(
                ["ffprobe", "-v", "error", "-show_format", "-of", "json", str(source)]
            )
        )
        end = float(info["format"]["duration"])
    signature = json.dumps(
        [
            str(source),
            source.stat().st_mtime_ns,
            start,
            end,
            count,
            layer.get("crop"),
            layer.get("reverse"),
        ]
    )
    target = cache / (hashlib.sha256(signature.encode()).hexdigest()[:20] + ".mp4")
    if target.exists():
        with av.open(str(target)) as existing:
            if existing.streams.video and existing.streams.video[0].frames == count:
                return target
    duration = max(end - start, 1 / FPS)
    filters = [f"trim=duration={duration}", "setpts=PTS-STARTPTS"]
    if layer.get("crop"):
        filters.append("crop=" + ":".join(map(str, layer["crop"])))
    if layer.get("reverse"):
        filters.append("reverse")
    filters += [
        f"setpts={(count / FPS) / duration}*PTS",
        "scale=854:480:force_original_aspect_ratio=decrease",
        "pad=854:480:(ow-iw)/2:(oh-ih)/2",
        "setsar=1",
        "fps=30",
        f"tpad=stop_mode=clone:stop_duration={count / FPS + 2}",
        f"trim=end_frame={count}",
    ]
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-ss",
            str(start),
            "-i",
            str(source),
            "-vf",
            ",".join(filters),
            "-an",
            "-sn",
            "-frames:v",
            str(count),
            "-c:v",
            "libx264",
            "-preset",
            "fast",
            "-crf",
            "18",
            str(target),
        ]
    )
    return target


def font(size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONT, size, index=27)


def render_shot(shot: dict, output: Path, cache: Path) -> None:
    count = shot["out_frame"] - shot["in_frame"]
    layers = []
    for spec in shot["layers"]:
        spec = dict(spec)
        start = round(spec.get("at", 0) * FPS)
        stop = round(spec.get("until", count / FPS) * FPS)
        spec.update(start=start, stop=min(count, stop))
        if spec.get("image"):
            spec["still"] = Image.open(ROOT / spec["image"]).convert("RGB")
        elif spec.get("source"):
            normalized = prepare(spec, stop - start, cache)
            container = av.open(str(normalized))
            spec.update(container=container, frames=iter(container.decode(video=0)))
        elif spec.get("text"):
            spec["font"] = font(spec.get("font_size", 28))
        layers.append(spec)
    with av.open(str(output), "w") as mux:
        stream = mux.add_stream("libx264", rate=FPS)
        stream.width, stream.height = SIZE
        stream.pix_fmt = "yuv420p"
        stream.options = {"crf": "18", "preset": "fast"}
        for n in range(count):
            canvas = Image.new("RGB", SIZE, shot.get("background", "black"))
            for spec in layers:
                if not spec["start"] <= n < spec["stop"]:
                    continue
                t = (n - spec["start"]) / FPS
                rect = spec.get("rect", [0, 0, 854, 480])
                if spec.get("move"):
                    move = spec["move"]
                    p = max(0, min(1, (t - move.get("at", 0)) / move["duration"]))
                    p = p * p * (3 - 2 * p)
                    rect = [a + (b - a) * p for a, b in zip(rect, move["to"])]
                x, y, w, h = map(round, rect)
                alpha = 1.0
                if spec.get("fade_in"):
                    alpha = min(1, t / spec["fade_in"])
                if spec.get("fade_out"):
                    alpha = min(alpha, (spec["stop"] - n) / FPS / spec["fade_out"])
                if spec.get("text"):
                    overlay = Image.new("RGBA", SIZE)
                    draw = ImageDraw.Draw(overlay)
                    draw.multiline_text(
                        (x, y),
                        spec["text"],
                        font=spec["font"],
                        fill=spec.get("color", "white"),
                        anchor=spec.get("anchor", "mm"),
                        align="center",
                        spacing=5,
                    )
                    canvas = Image.blend(
                        canvas,
                        Image.alpha_composite(canvas.convert("RGBA"), overlay).convert(
                            "RGB"
                        ),
                        alpha,
                    )
                else:
                    picture = spec.get("still")
                    if picture is None:
                        try:
                            picture = next(spec["frames"]).to_image()
                        except StopIteration as exc:
                            raise RuntimeError(
                                f"Short source layer in {shot['id']} at frame {n}: {spec['source']}"
                            ) from exc
                    if spec.get("display_crop"):
                        cx, cy, cw, ch = spec["display_crop"]
                        picture = picture.crop((cx, cy, cx + cw, cy + ch))
                    if spec.get("fit", True):
                        scale = min(w / picture.width, h / picture.height)
                        new_w, new_h = (
                            max(1, round(picture.width * scale)),
                            max(1, round(picture.height * scale)),
                        )
                        x += (w - new_w) // 2
                        y += (h - new_h) // 2
                        w, h = new_w, new_h
                    picture = picture.resize(
                        (max(1, w), max(1, h)), Image.Resampling.LANCZOS
                    )
                    if spec.get("key_black"):
                        import numpy as np

                        mask = Image.fromarray(
                            (
                                np.asarray(picture)
                                .max(axis=2)
                                .astype(float)
                                .clip(0, 32)
                                * 255
                                / 32
                            ).astype("uint8")
                        )
                        if alpha < 1:
                            mask = mask.point([round(v * alpha) for v in range(256)])
                        canvas.paste(picture, (x, y), mask)
                    elif alpha < 1:
                        mask = Image.new("L", picture.size, round(255 * alpha))
                        canvas.paste(picture, (x, y), mask)
                    else:
                        canvas.paste(picture, (x, y))
            if shot.get("divider"):
                draw = ImageDraw.Draw(canvas)
                draw.line(shot["divider"], fill="#666666", width=1)
            frame = av.VideoFrame.from_image(canvas)
            frame.pts = n
            frame.time_base = Fraction(1, FPS)
            for packet in stream.encode(frame):
                mux.mux(packet)
        for packet in stream.encode():
            mux.mux(packet)
    for spec in layers:
        if spec.get("container"):
            spec["container"].close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest", type=Path, default=COURSE / "时间线.json"
    )
    parser.add_argument("--output", type=Path, default=COURSE / "生成")
    parser.add_argument(
        "--shots", nargs="*", help="Render selected shot IDs only; do not concatenate."
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    cache = COURSE / "生成/cache"
    cache.mkdir(parents=True, exist_ok=True)
    parts = args.output / "镜头"
    parts.mkdir(parents=True, exist_ok=True)
    previous = 0
    for shot in manifest["shots"]:
        assert shot["in_frame"] == previous
        previous = shot["out_frame"]
        if args.shots and shot["id"] not in args.shots:
            continue
        output = parts / (shot["id"] + ".mp4")
        dependencies = [
            (str(ROOT / layer["source"]), (ROOT / layer["source"]).stat().st_mtime_ns)
            for layer in shot["layers"]
            if layer.get("source")
        ]
        fingerprint = hashlib.sha256(
            json.dumps(
                [shot, dependencies, Path(__file__).read_text()], sort_keys=True
            ).encode()
        ).hexdigest()
        marker = output.with_suffix(".json")
        if (
            args.force
            or not output.exists()
            or not marker.exists()
            or json.loads(marker.read_text()).get("fingerprint") != fingerprint
        ):
            print("Rendering", shot["id"], flush=True)
            render_shot(shot, output, cache)
            marker.write_text(
                json.dumps(
                    {
                        "fingerprint": fingerprint,
                        "frames": shot["out_frame"] - shot["in_frame"],
                    }
                )
            )
    assert previous == 12570
    if args.shots:
        return
    concat = args.output / "concat.txt"
    concat.write_text(
        "".join(
            "file '"
            + str((parts / (s["id"] + ".mp4")).resolve()).replace("'", "'\\''")
            + "'\n"
            for s in manifest["shots"]
        )
    )
    run(
        [
            "ffmpeg",
            "-v",
            "error",
            "-y",
            "-f",
            "concat",
            "-safe",
            "0",
            "-i",
            str(concat),
            "-map",
            "0:v:0",
            "-c",
            "copy",
            "-an",
            "-sn",
            "-video_track_timescale",
            "30",
            "-movflags",
            "+faststart",
            str(args.output / "mini-llm-zh-480p-0000-0659.mp4"),
        ]
    )
    print(
        "Exported 419 seconds, 480p30, silent; subtitles remain external.", flush=True
    )


if __name__ == "__main__":
    main()
