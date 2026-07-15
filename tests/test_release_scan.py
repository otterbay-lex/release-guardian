import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCANNER_PATH = (
    Path(__file__).resolve().parents[1]
    / "versions"
    / "v2"
    / "scripts"
    / "release_scan.py"
)


def load_scanner():
    spec = importlib.util.spec_from_file_location("release_scan", SCANNER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("无法加载 release_scan.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ReleaseScanTests(unittest.TestCase):
    def scan_files(self, files):
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            for relative_path, content in files.items():
                target = root / relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(content, encoding="utf-8")
            return load_scanner().scan(root)

    def test_placeholder_key_does_not_block_release(self):
        result = self.scan_files({".env.example": "OPENAI_API_KEY=your_key_here\n"})

        self.assertEqual(result["summary"]["blockers"], 0)

    def test_real_looking_key_is_blocked_and_masked(self):
        raw_key = "sk-proj-1234567890abcdefghijklmnop"
        result = self.scan_files({"config.js": f'const key = "{raw_key}";\n'})

        rendered = json.dumps(result)
        self.assertNotIn(raw_key, rendered)
        self.assertEqual(result["summary"]["blockers"], 1)
        self.assertEqual(result["findings"][0]["rule_id"], "RG-SEC-001")
        self.assertEqual(result["findings"][0]["severity"], "blocker")

    def test_local_user_path_is_reported(self):
        result = self.scan_files(
            {"README.md": "打开 /Users/demo-user/Documents/project/output.txt\n"}
        )

        self.assertEqual(result["findings"][0]["rule_id"], "RG-PRIV-002")
        self.assertEqual(result["findings"][0]["severity"], "warning")


if __name__ == "__main__":
    unittest.main()
