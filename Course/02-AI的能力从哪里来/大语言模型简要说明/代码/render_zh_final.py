"""Render the consolidated, reviewed Chinese fixes at 480p30, then compose.

Existing 1080p source renders are read-only. Only the listed Chinese scenes need
new renders; already verified Chinese scenes and the three heavy English scenes
are reused. Run --check first to review the queue without rendering.
"""

from __future__ import annotations
import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
COURSE = ROOT.parent
JOBS = [
    (
        "reconstruction_core_zh.py",
        "core",
        ["PredictTheNextWord", "ChineseMachineFront", "ShowSingleTrainingExample"],
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Print queue only; do not render or compose.",
    )
    parser.add_argument("--skip-compose", action="store_true")
    args = parser.parse_args()
    logdir = ROOT / "logs/zh-final-batch"
    logdir.mkdir(parents=True, exist_ok=True)
    source_files = [ROOT / name for name, _, _ in JOBS]
    hashes = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in source_files}
    if args.check:
        print(
            json.dumps(
                {
                    "size": [854, 480],
                    "fps": 30,
                    "scenes": JOBS,
                    "source_sha256": hashes,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return
    (logdir / "source-freeze.json").write_text(json.dumps(hashes, indent=2) + "\n")
    records = []
    for module, group, scenes in JOBS:
        for scene in scenes:
            # Fail if code is edited during the consolidated rendering pass.
            for p in source_files:
                if hashlib.sha256(p.read_bytes()).hexdigest() != hashes[p.name]:
                    raise RuntimeError(f"Source changed during batch: {p}")
            output = ROOT / f"generated/reconstruction-{group}-zh-480p"
            command = [
                sys.executable,
                "-m",
                "manimlib",
                module,
                scene,
                "-w",
                "-l",
                "--fps",
                "30",
                "--video_dir",
                str(output),
            ]
            print("Rendering", scene, flush=True)
            with (logdir / (scene + ".log")).open("w") as log:
                subprocess.run(
                    command, cwd=ROOT, check=True, stdout=log, stderr=subprocess.STDOUT
                )
            video = output / (scene + ".mp4")
            info = json.loads(
                subprocess.check_output(
                    [
                        "ffprobe",
                        "-v",
                        "error",
                        "-show_streams",
                        "-of",
                        "json",
                        str(video),
                    ]
                )
            )
            streams = info["streams"]
            assert len(streams) == 1 and streams[0]["codec_type"] == "video"
            assert (
                streams[0]["width"],
                streams[0]["height"],
                streams[0]["avg_frame_rate"],
            ) == (854, 480, "30/1")
            subprocess.run(
                ["ffmpeg", "-v", "error", "-i", str(video), "-f", "null", "-"],
                check=True,
            )
            records.append(
                {
                    "scene": scene,
                    "source": module,
                    "source_sha256": hashes[module],
                    "output": str(video),
                    "stream": streams[0],
                    "decode": "passed",
                }
            )
            (logdir / "render-report.json").write_text(
                json.dumps(records, ensure_ascii=False, indent=2) + "\n"
            )
    if not args.skip_compose:
        subprocess.run(
            [sys.executable, str(ROOT / "compose_reconstruction.py")],
            cwd=ROOT,
            check=True,
        )


if __name__ == "__main__":
    main()
