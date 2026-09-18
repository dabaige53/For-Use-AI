"""Render the 38 upstream chm scenes independently, with resumable output."""

from pathlib import Path
import argparse
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent
B = set(
    "PredictTheNextWord LotsOfTextIntoTheMachine EvenMoreTextIntoMachine RiverBankProbParts PartialScript ShowMachineWithDials ShowSingleTrainingExample EnormousAmountOfTrainingText RLHFWorkers TrainingDataCHM DivyUpParameters".split()
)
C = set(
    "HoldUpThumbnail IsThisUsefulToShare AskAboutAttention FirthQuote BadChatBot RLHFWorker ThreeWordsToOne EndScreen".split()
)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quality", choices=["preview", "full"], default="full")
    ap.add_argument("--scenes", nargs="*", help="Scene names; default all 38")
    ap.add_argument("--list", action="store_true")
    ap.add_argument(
        "--force", action="store_true", help="Render even when a validated MP4 exists"
    )
    args = ap.parse_args()
    inventory = json.loads((ROOT / "scene-inventory.json").read_text())
    names = [x["scene"] for x in inventory]
    if args.list:
        print("\n".join(names))
        return
    selected = args.scenes or names
    if set(selected) - set(names):
        ap.error("Unknown scenes: " + ", ".join(set(selected) - set(names)))
    output = (
        ROOT
        / "generated"
        / ("all-original" if args.quality == "full" else "all-original-preview")
    )
    output.mkdir(parents=True, exist_ok=True)
    logs = ROOT / "logs" / "render-all"
    logs.mkdir(exist_ok=True)
    results = []
    for scene in selected:
        target = output / f"{scene}.mp4"
        group = "b" if scene in B else "c" if scene in C else "a"
        if target.exists() and not args.force:
            check = subprocess.run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-show_entries",
                    "format=duration",
                    "-of",
                    "csv=p=0",
                    str(target),
                ],
                capture_output=True,
                text=True,
            )
            try:
                valid = check.returncode == 0 and float(check.stdout) > 0
            except ValueError:
                valid = False
            if valid:
                results.append(
                    {"scene": scene, "status": "existing", "file": str(target)}
                )
                print(scene, "existing", flush=True)
                continue
        cmd = [
            str(ROOT / ".venv/bin/manimgl"),
            f"group_{group}.py",
            scene,
            "-w",
            "--hd" if args.quality == "full" else "-l",
            "--fps",
            "30" if args.quality == "full" else "15",
            "--video_dir",
            str(output),
            "--file_name",
            scene,
        ]
        print(scene, "rendering", flush=True)
        with (logs / f"{scene}-{args.quality}.log").open("w") as log:
            result = subprocess.run(cmd, cwd=ROOT, stdout=log, stderr=subprocess.STDOUT)
        success = result.returncode == 0 and target.exists()
        results.append(
            {
                "scene": scene,
                "status": "rendered" if success else "failed",
                "file": str(target),
                "exit_code": result.returncode,
            }
        )
        (logs / f"latest-{args.quality}.json").write_text(json.dumps(results, indent=2))
    if any(x["status"] == "failed" for x in results):
        sys.exit(1)


if __name__ == "__main__":
    main()
