#!/usr/bin/env python3
"""Render and verify the eight group-C original-layout scenes."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SCENES = [
    "HoldUpThumbnail", "IsThisUsefulToShare", "AskAboutAttention", "FirthQuote",
    "BadChatBot", "RLHFWorker", "ThreeWordsToOne", "EndScreen",
]
SOURCE_LINES = {
    "HoldUpThumbnail": "upstream/_2024/transformers/chm.py:10-29",
    "IsThisUsefulToShare": "upstream/_2024/transformers/chm.py:32-42",
    "AskAboutAttention": "upstream/_2024/transformers/chm.py:45-56",
    "FirthQuote": "upstream/_2024/transformers/chm.py:303-442",
    "BadChatBot": "upstream/_2024/transformers/chm.py:1350-1411",
    "RLHFWorker": "upstream/_2024/transformers/chm.py:1433-1449",
    "ThreeWordsToOne": "upstream/_2024/transformers/chm.py:1855-1918",
    "EndScreen": "upstream/_2024/transformers/chm.py:2156-2160",
}
PLACEHOLDERS = {
    "HoldUpThumbnail": ["Chapter5_TN3.png", "PiCreature modes (plain-shape fallback)"],
    "IsThisUsefulToShare": ["PiCreature modes (plain-shape fallback)"],
    "AskAboutAttention": ["PiCreature modes (plain-shape fallback)"],
    "FirthQuote": ["JohnRFirth portrait", "RiverBank image", "FederalReserve image"],
    "BadChatBot": ["Bot.svg"],
    "RLHFWorker": ["comp_worker.svg"],
    "ThreeWordsToOne": ["CHM_Exterior.jpeg", "GenericComputer.svg", "History.svg", "Museum.svg"],
    "EndScreen": ["PiCreature modes (plain-shape fallback)", "Patreon supporter data"],
}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=("preview", "final", "all"), default="all")
    parser.add_argument("--scenes", nargs="*", choices=SCENES, default=SCENES)
    return parser.parse_args()


def probe(path: Path) -> dict:
    result = subprocess.run([
        "ffprobe", "-v", "error", "-show_entries",
        "stream=codec_type,width,height,avg_frame_rate,nb_frames:format=duration",
        "-of", "json", str(path),
    ], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def decode(path: Path):
    subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True)


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def render(scene: str, quality: str, target: Path, log_path: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    command = [
        str(ROOT / ".venv/bin/manimgl"), "group_c.py", scene, "-w",
        "--file_name", str(target), "--fps", "15" if quality == "preview" else "30",
        "-l" if quality == "preview" else "--hd", "--log-level", "INFO",
    ]
    with log_path.open("w", encoding="utf-8") as log:
        completed = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT, text=True)
    if completed.returncode:
        return {"status": "failed", "returncode": completed.returncode, "log": str(log_path.relative_to(ROOT))}
    actual = target if target.exists() else target.with_suffix(".mp4")
    if not actual.exists():
        return {"status": "failed", "error": "renderer returned success but output is absent", "log": str(log_path.relative_to(ROOT))}
    try:
        media = probe(actual)
        decode(actual)
    except (subprocess.CalledProcessError, StopIteration, json.JSONDecodeError) as error:
        return {"status": "failed", "error": f"media verification failed: {error}", "log": str(log_path.relative_to(ROOT))}
    stream = next(stream for stream in media["streams"] if stream["codec_type"] == "video")
    return {
        "status": "passed", "output": display_path(actual),
        "width": stream.get("width"), "height": stream.get("height"),
        "fps": stream.get("avg_frame_rate"), "frames": stream.get("nb_frames"),
        "duration": float(media["format"]["duration"]), "decode": "passed",
        "visual_check": "not performed", "log": str(log_path.relative_to(ROOT)),
    }


def main():
    args = parse_args()
    log_dir = ROOT / "logs/group-c"
    log_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Group C original-layout silent scene renders",
        "adaptation": "Original construct order/layout retained; unavailable external assets replaced in place.",
        "scenes": [],
    }
    with tempfile.TemporaryDirectory(prefix="group-c-preview-") as preview_dir:
        for scene in args.scenes:
            entry = {
                "scene": scene, "source": SOURCE_LINES[scene],
                "compatibility": "Absolute asset paths redirected to local placeholders; upstream remains read-only.",
                "placeholders": PLACEHOLDERS[scene], "renders": {},
            }
            if args.quality in ("preview", "all"):
                preview = Path(preview_dir) / f"{scene}.mp4"
                entry["renders"]["preview"] = render(scene, "preview", preview, log_dir / f"{scene}-preview.log")
            if args.quality in ("final", "all"):
                final = ROOT / "generated/all-original" / f"{scene}.mp4"
                entry["renders"]["final"] = render(scene, "final", final, log_dir / f"{scene}-final.log")
            report["scenes"].append(entry)
            (ROOT / "group-c-report.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
            print(scene, entry["renders"])


if __name__ == "__main__":
    main()
