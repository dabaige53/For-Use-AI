#!/usr/bin/env python3
"""Render and verify the missing Transformer reconstruction scenes."""

from __future__ import annotations

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
REPORT_PATH = ROOT / "reconstruction-flow-zh-480p-report.json"
SCENES = (
    "ReconstructionFlowForCHM",
    "ReconstructionBankSemanticSpace",
    "ReconstructionBankAttentionCloseup",
)
SOURCE = {
    "ReconstructionFlowForCHM": "upstream/_2024/transformers/network_flow.py:668-706,1207-1234",
    "ReconstructionBankSemanticSpace": "upstream/_2024/transformers/embedding.py:2571-2692",
    "ReconstructionBankAttentionCloseup": "upstream/_2024/transformers/network_flow.py:154-327 (first Attention end-state and upstream highlight branch)",
}
TIMING = {
    "ReconstructionFlowForCHM": {
        "input_to_embeddings": [0, 15.84],
        "camera_scale_before_layers": [15.84, 16.84],
        "attention_1": [16.84, 20.84],
        "feedforward_1": [20.84, 25.84],
        "attention_2": [25.84, 29.84],
        "feedforward_2": [29.84, 34.84],
        "attention_3": [34.84, 38.84],
        "feedforward_3": [38.84, 43.84],
        "many_repetitions": [43.84, 49.84],
        "last_vector_focus": [49.84, 52.84],
        "probability_setup": [52.84, 57.84],
        "probability_camera_push": [57.84, 65.84],
    },
    "ReconstructionBankSemanticSpace": {
        "bank_vector": [0, 6],
        "meaning_directions_preview": [6, 21],
        "three_meaning_vectors": [21, 45],
    },
    "ReconstructionBankAttentionCloseup": {
        "bank_column_highlight": [0, 3],
        "highlight_hold": [3, 5],
        "river_bank_image_entrance": [5, 7],
        "completed_hold": [7, 10],
    },
}


def run(command: list[str], log_path: Path) -> tuple[int, float]:
    started = time.monotonic()
    with log_path.open("w", encoding="utf-8") as log:
        result = subprocess.run(command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
    return result.returncode, time.monotonic() - started


def probe(path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "stream=codec_type,width,height,avg_frame_rate,nb_frames:format=duration",
            "-of",
            "json",
            str(path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    data = json.loads(result.stdout)
    subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"], check=True
    )
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--quality", choices=("preview", "final", "all"), default="all")
    parser.add_argument("--scenes", nargs="*", choices=SCENES, default=list(SCENES))
    args = parser.parse_args()
    out_dir = ROOT / "generated" / "reconstruction-flow-zh-480p"
    log_dir = ROOT / "logs" / "reconstruction-flow-zh-480p"
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scope": "Missing original-layout Transformer flow and bank semantic-space scenes",
        "upstream_commit": "4dd996dd4fdddef717273e65c97f2227c31493ac",
        "audio": "none",
        "model_or_network_calls": "none",
        "adaptations": [
            "All Chinese Text explicitly uses PingFang SC; token rectangles follow each visible glyph height plus the upstream vertical buffer.",
            "Visible explanatory labels translated to Chinese while retaining bank for the polysemy example.",
            "Fixed illustrative next-token candidates begin with 水, 河流, 湖泊.",
            "SimpleSpaceExample text changed from you to bank（河岸 / 银行） and the three bank-context meanings translated.",
        ],
        "visual_validation": "Checked representative frames for Chinese input boxes, Attention/Feedforward depth, semantic vectors, and bank closeup image.",
        "known_difference": "These are independently rendered source scenes; the film's split-screen crossfades and editorial timing remain for the compositor.",
        "scenes": [],
    }
    if REPORT_PATH.exists():
        previous = json.loads(REPORT_PATH.read_text())
        report["scenes"] = [
            entry
            for entry in previous.get("scenes", [])
            if entry.get("scene") not in args.scenes
        ]
    for scene in args.scenes:
        entry = {
            "scene": scene,
            "source": SOURCE[scene],
            "actual_action_times_seconds": TIMING[scene],
            "renders": {},
        }
        qualities = ("preview", "final") if args.quality == "all" else (args.quality,)
        for quality in qualities:
            suffix = "preview" if quality == "preview" else "final"
            target = out_dir / f"{scene}-{suffix}.mp4"
            command = [
                str(ROOT / ".venv/bin/manimgl"),
                "reconstruction_flow.py",
                scene,
                "-w",
                "--file_name",
                str(target),
                "--fps",
                "15" if quality == "preview" else "30",
                "-l",
                "--log-level",
                "INFO",
            ]
            if quality == "preview":
                command.extend(["-n", "0,3"])
            code, wall = run(command, log_dir / f"{scene}-{suffix}.log")
            result = {
                "status": "failed" if code else "rendered",
                "exit_code": code,
                "wall_seconds": round(wall, 3),
            }
            if code == 0 and target.exists():
                try:
                    media = probe(target)
                    video = next(
                        stream
                        for stream in media["streams"]
                        if stream["codec_type"] == "video"
                    )
                    result.update(
                        status="passed",
                        output=str(target.relative_to(ROOT)),
                        duration=float(media["format"]["duration"]),
                        width=video.get("width"),
                        height=video.get("height"),
                        fps=video.get("avg_frame_rate"),
                        frames=video.get("nb_frames"),
                        decode="passed",
                        audio="none",
                    )
                except Exception as error:
                    result.update(status="failed", error=str(error))
            entry["renders"][quality] = result
            REPORT_PATH.write_text(
                json.dumps(report | {"scenes": report["scenes"] + [entry]}, indent=2)
                + "\n"
            )
            if result["status"] == "failed":
                raise SystemExit(f"{scene} {quality} failed; see {log_dir}")
        report["scenes"].append(entry)
    REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
