"""Join all 38 verified scenes in source order, without adding pages or audio."""

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main():
    inventory = json.loads((ROOT / "scene-inventory.json").read_text())
    if len(inventory) != 38 or any(x["status"] != "verified" for x in inventory):
        raise SystemExit("All 38 scenes must pass verify_renders.py --decode first")
    output = ROOT / "output"
    output.mkdir(exist_ok=True)
    concat = output / "original-scenes-concat.txt"
    concat.write_text("".join(f"file '{x['file']}'\n" for x in inventory))
    metadata = [";FFMETADATA1", "title=Original scenes review - source order"]
    cursor = 0
    for item in inventory:
        end = cursor + round(item["duration"] * 1000)
        metadata.extend([
            "[CHAPTER]", "TIMEBASE=1/1000", f"START={cursor}",
            f"END={end}", f"title={item['scene']}",
        ])
        cursor = end
    chapters = output / "original-scenes-chapters.txt"
    chapters.write_text("\n".join(metadata) + "\n")
    target = output / "original-scenes-review.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat), "-i", str(chapters), "-map", "0:v:0",
        "-map_metadata", "1", "-map_chapters", "1", "-an", "-c:v", "copy",
        "-movflags", "+faststart", str(target),
    ], check=True)
    print(target)


if __name__ == "__main__":
    main()
