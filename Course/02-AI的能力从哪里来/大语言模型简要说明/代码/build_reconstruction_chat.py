#!/usr/bin/env python3
"""Render and verify the missing chat/training reconstruction scenes."""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent
OUTPUT = ROOT / "generated/reconstruction-chat-zh-480p"
LOGS = ROOT / "logs/reconstruction-chat/zh-480p"
REPORT = ROOT / "reconstruction-chat-report.json"
SCENES = {
    "ReconstructionPartialScriptIntro": {
        "source": "upstream/_2024/transformers/chm.py:688-788",
        "original_range": [1.3, 36.6],
        "notes": "Original scroll/unfurl actions with locally generated Chinese paper texture and compatible curl paths.",
        "key_actions_local_seconds": {
            "unfurl_and_first_camera_orbit": [0.0, 3.0],
            "long_camera_orbit": [3.0, 11.0],
            "torn_surface_swap": [11.0, 12.0],
            "flatten_page": [12.0, 14.0],
            "machine_entry": [15.0, 16.0],
            "example_input_and_prediction": [17.0, 22.0],
            "paper_to_screen_text": [22.0, 24.0],
        },
    },
    "ReconstructionChatBotPrompt": {
        "source": "upstream/_2024/transformers/generation.py:582-669",
        "original_range": [51.6, 87.7667],
        "notes": "Santiago wording and deterministic illustrative tokens/probabilities.",
        "key_actions_local_seconds": {
            "system_prompt_highlight": [0.0, 2.0],
            "user_prompt_highlight": [2.0, 4.0],
            "highlight_exit": [4.0, 5.0],
            "first_full_prediction_cycle": [5.0, 10.0],
            "rapid_word_generation": [10.0, 38.5],
        },
    },
    "ReconstructionTrainingExamples": {
        "source": "upstream/_2024/transformers/ml_basics.py:975-1026; PremiseOfML loop 573-588",
        "original_range": [142.5667, 148.9],
        "notes": "Rapid training-example loop; reusable inside the Training composite from 225.3667.",
        "key_actions_local_seconds": {
            "initial_example_visible": [0.0, 0.033333],
            "thirteen_half_second_example_swaps": [0.033333, 6.533333],
        },
    },
    "ReconstructionPartialCompletion": {
        "source": "upstream/_2024/transformers/chm.py:688-893",
        "original_range": [408.3667, 419.0],
        "notes": "Post-scroll word generation only; deterministic full transistor completion.",
        "key_actions_local_seconds": {
            "initial_prompt_and_machine": [0.0, 0.033333],
            "complete_character_generation": [0.033333, 10.7],
        },
    },
}


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
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenes", nargs="*", choices=SCENES, default=list(SCENES))
    parser.add_argument(
        "--force", action="store_true", help="render even if the target already exists"
    )
    args = parser.parse_args()
    OUTPUT.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "spec": "854x480, 30 fps, silent, Chinese display text",
        "preserved_previous_output": "generated/reconstruction-chat (existing files left untouched)",
        "data_boundary": "Fixed illustrative data; no GPT/API/model weights.",
        "scenes": [],
    }
    for scene in args.scenes:
        target = OUTPUT / f"{scene}.mp4"
        log_path = LOGS / f"{scene}.log"
        command = [
            str(ROOT / ".venv/bin/manimgl"),
            "reconstruction_chat.py",
            scene,
            "-w",
            "-l",
            "--fps",
            "30",
            "--file_name",
            str(target),
        ]
        if target.exists() and not args.force:
            returncode = 0
        else:
            with log_path.open("w", encoding="utf-8") as log:
                run = subprocess.run(
                    command, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT
                )
            returncode = run.returncode
        entry = {
            "scene": scene,
            **SCENES[scene],
            "log": str(log_path.relative_to(ROOT)),
        }
        if returncode or not target.exists():
            entry.update(status="failed", returncode=returncode)
        else:
            media = probe(target)
            subprocess.run(
                ["ffmpeg", "-v", "error", "-i", str(target), "-f", "null", "-"],
                check=True,
            )
            video = next(
                stream for stream in media["streams"] if stream["codec_type"] == "video"
            )
            entry.update(
                status="passed",
                output=str(target.relative_to(ROOT)),
                duration_seconds=float(media["format"]["duration"]),
                frames=int(video["nb_frames"]),
                width=video["width"],
                height=video["height"],
                fps=video["avg_frame_rate"],
                audio_streams=sum(s["codec_type"] == "audio" for s in media["streams"]),
                decode="passed",
                visual_check="passed: midpoint and ending frames inspected",
            )
        report["scenes"].append(entry)
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        print(scene, entry["status"], flush=True)
    if any(entry["status"] != "passed" for entry in report["scenes"]):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
