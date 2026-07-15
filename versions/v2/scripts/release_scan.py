#!/usr/bin/env python3
"""Release Guardian V2 的无依赖本地基础扫描器。"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


EXCLUDED_DIRECTORIES = {
    ".git",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "target",
}
PLACEHOLDER_MARKERS = ("example", "placeholder", "your_", "xxxx", "changeme")
SECRET_PATTERNS = (
    re.compile(r"sk-proj-[A-Za-z0-9_-]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"),
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[A-Z0-9]{16}"),
    re.compile(r"AIza[A-Za-z0-9_-]{20,}"),
)
LOCAL_PATH_PATTERNS = (
    re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    re.compile(r"[A-Za-z]:\\Users\\[A-Za-z0-9._-]+\\"),
)


def masked(value: str) -> str:
    """只保留短前后缀，避免报告泄露完整秘密。"""
    if len(value) <= 8:
        return "***"
    return f"{value[:4]}...{value[-4:]}"


def iter_text_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED_DIRECTORIES for part in path.parts):
            continue
        try:
            content = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        yield path, content


def scan(root: Path) -> dict[str, object]:
    root = Path(root).resolve()
    findings: list[dict[str, object]] = []

    for path, content in iter_text_files(root):
        relative_path = str(path.relative_to(root))
        for line_number, line in enumerate(content.splitlines(), start=1):
            lowered = line.lower()
            for pattern in SECRET_PATTERNS:
                for match in pattern.finditer(line):
                    value = match.group(0)
                    if any(marker in lowered for marker in PLACEHOLDER_MARKERS):
                        continue
                    findings.append(
                        {
                            "rule_id": "RG-SEC-001",
                            "severity": "blocker",
                            "category": "security",
                            "path": relative_path,
                            "line": line_number,
                            "message": "发现疑似真实凭证，发布前需要移除并轮换。",
                            "masked_hint": masked(value),
                            "confidence": "high",
                        }
                    )
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        {
                            "rule_id": "RG-PRIV-002",
                            "severity": "warning",
                            "category": "privacy",
                            "path": relative_path,
                            "line": line_number,
                            "message": "发现本机用户绝对路径，建议改为相对路径或中性示例路径。",
                            "masked_hint": "本机用户路径",
                            "confidence": "high",
                        }
                    )

    summary = {
        "blockers": sum(item["severity"] == "blocker" for item in findings),
        "warnings": sum(item["severity"] == "warning" for item in findings),
        "notes": sum(item["severity"] == "note" for item in findings),
    }
    return {
        "schema_version": "1.0",
        "scan_root": str(root),
        "findings": findings,
        "summary": summary,
        "limitations": [
            "基础扫描仅分析可读取的 UTF-8 文本文件。",
            "未发现问题不代表不存在风险。",
        ],
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("用法：release_scan.py <检查路径>", file=sys.stderr)
        return 2
    root = Path(argv[1])
    if not root.is_dir():
        print("检查路径不是可读取目录。", file=sys.stderr)
        return 2
    print(json.dumps(scan(root), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
