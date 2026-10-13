"""Offline manifest loading checks: python -m unittest discover -s <this directory>."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import threading
import unittest
import urllib.request
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("preview", Path(__file__).with_name("mermaid-preview.py"))
assert spec is not None and spec.loader is not None
preview = importlib.util.module_from_spec(spec)
spec.loader.exec_module(preview)


class DetailsTests(unittest.TestCase):
    def test_move_root_and_keep_optional_materials_visible(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "original" / "Course"
            root.mkdir(parents=True)
            (root / "article.md").write_text("课程材料", encoding="utf-8")
            manifest = root / "节点材料.json"
            manifest.write_text(json.dumps({"nodes": {}, "assets": {
                "article": {"path": "article.md", "kind": "text"},
                "missing": {"path": "absent.png", "url": "/old", "download": "/old"},
            }}), encoding="utf-8")
            moved = Path(directory) / "moved"
            shutil.move(str(root.parent), moved)
            root = (moved / "Course").resolve()
            details, paths = preview.load_details(root / manifest.name, root)
            self.assertEqual(paths["article"], root / "article.md")
            self.assertTrue(details["assets"]["article"]["available"])
            self.assertEqual(details["assets"]["article"]["url"], "/materials/article.md")
            self.assertEqual(paths["article"].read_text(encoding="utf-8"), "课程材料")
            missing = details["assets"]["missing"]
            self.assertFalse(missing["available"])
            self.assertNotIn("missing", paths)
            self.assertNotIn("url", missing)
            self.assertNotIn("download", missing)

    def test_required_manifest_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            manifest = Path(directory) / "missing.json"
            with self.assertRaises(FileNotFoundError):
                preview.load_details(manifest)
            manifest.write_text("{broken", encoding="utf-8")
            with self.assertRaises(json.JSONDecodeError):
                preview.load_details(manifest)

    def test_default_root_serves_relative_materials_without_dependencies(self):
        case = self
        class SmokeServer(preview.ThreadingHTTPServer):
            def serve_forever(self):
                worker = threading.Thread(target=super().serve_forever, daemon=True)
                worker.start()
                try:
                    base = f"http://127.0.0.1:{self.server_port}"
                    with urllib.request.urlopen(base + "/details", timeout=5) as response:
                        details = json.load(response)
                    case.assertFalse(details["assets"]["missing"]["available"])
                    with urllib.request.urlopen(base + details["assets"]["article"]["url"], timeout=5) as response:
                        case.assertEqual(response.read().decode(), "课程材料")
                finally:
                    self.shutdown()
                    worker.join(timeout=5)

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "article.md").write_text("课程材料", encoding="utf-8")
            manifest = root / "details.json"
            manifest.write_text(json.dumps({"nodes": {}, "assets": {
                "article": {"path": "article.md", "kind": "text"},
                "missing": {"path": "absent.png", "kind": "image"},
            }}), encoding="utf-8")
            with patch.object(preview, "ThreadingHTTPServer", SmokeServer), \
                 patch.object(preview, "prepare_dependencies", return_value={}), \
                 patch.object(preview.sys, "argv", ["preview", "--port", "0", "--details", str(manifest)]):
                preview.main()

    def test_repository_manifest_has_relative_paths(self):
        manifest = Path(__file__).resolve().parent.parent / "交互/课程制作路径/节点材料.json"
        source = json.loads(manifest.read_text(encoding="utf-8"))
        self.assertEqual(len(source["assets"]), 29)
        self.assertTrue(all(not Path(a["path"]).is_absolute() for a in source["assets"].values()))
        details, paths = preview.load_details(manifest, manifest.parents[3])
        self.assertEqual(len(details["assets"]), 29)
        self.assertTrue(all(a["available"] == (key in paths) for key, a in details["assets"].items()))


if __name__ == "__main__":
    unittest.main()
