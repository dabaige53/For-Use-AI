"""Probe all original scenes; optionally decode and write the local viewing index."""

from pathlib import Path
import argparse
import json
import subprocess

ROOT = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--decode", action="store_true", help="Decode every completed video fully"
    )
    args = parser.parse_args()
    inventory = json.loads((ROOT / "scene-inventory.json").read_text())
    total = 0
    for item in inventory:
        path = ROOT / "generated/all-original" / f"{item['scene']}.mp4"
        item["status"] = "pending"
        if not path.exists():
            continue
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration:stream=width,height,r_frame_rate,codec_type",
                "-of",
                "json",
                str(path),
            ],
            capture_output=True,
            text=True,
        )
        duration = 0.0
        try:
            data = json.loads(result.stdout)
            duration = float(data["format"]["duration"])
            streams = data["streams"]
            valid = (
                duration > 0
                and len(streams) == 1
                and streams[0]
                == dict(
                    codec_type="video", width=1920, height=1080, r_frame_rate="30/1"
                )
            )
        except (ValueError, KeyError):
            valid = False
        if not valid:
            item["status"] = "invalid"
            continue
        item.update(status="probed", file=str(path), duration=duration)
        if args.decode:
            result = subprocess.run(
                ["ffmpeg", "-v", "error", "-i", str(path), "-f", "null", "-"],
                capture_output=True,
                text=True,
            )
            item["status"] = (
                "verified"
                if result.returncode == 0 and not result.stderr.strip()
                else "decode_failed"
            )
            if item["status"] == "decode_failed":
                item["error"] = result.stderr[-1000:]
        total += duration
    (ROOT / "scene-inventory.json").write_text(
        json.dumps(inventory, ensure_ascii=False, indent=2)
    )
    completed = sum(x["status"] in ("probed", "verified") for x in inventory)
    lines = [
        "# 原始动画分段索引",
        "",
        f"可播放 {completed}/38 段，共 {total:.1f} 秒；1080p、30fps、无音轨。",
        "",
        "按 chm.py 源码顺序排列，不代表原片最终剪辑顺序。缺失外部素材采用占位，预测采用固定假数据。保留原始场景结构，尚未认定视觉1:1。",
        "",
        "| 场景 | 时长 | 验证状态 |",
        "|---|---:|---|",
    ]
    for x in inventory:
        label = (
            f"[{x['scene']}]({x['file']})"
            if x["status"] in ("probed", "verified")
            else x["scene"]
        )
        duration = (
            f"{x['duration']:.2f} 秒" if x["status"] in ("probed", "verified") else "—"
        )
        lines.append(f"| {label} | {duration} | {x['status']} |")
    (ROOT / "SCENES.md").write_text("\n".join(lines) + "\n")
    print(f"{completed}/38 playable; {total:.1f}s")
    if completed != 38:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
