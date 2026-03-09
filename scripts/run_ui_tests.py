#!/usr/bin/env python3
"""
执行 UI 测试（Playwright + MetaMask），结果写入 log/ui/，并生成失败/跳过摘要。
直接运行：python scripts/run_ui_tests.py
"""
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "log" / "ui"
sys.path.insert(0, str(ROOT))
_spec = importlib.util.spec_from_file_location("pytest_report", ROOT / "scripts" / "pytest_report.py")
_report = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_report)
write_summary = _report.write_summary


def main():
    import pytest
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    junit_path = LOG_DIR / "junit.xml"
    summary_path = LOG_DIR / "summary.txt"
    args = [
        str(ROOT / "tests" / "ui"),
        "-v", "-r", "a",
        "-m", "ui",
        "--junitxml", str(junit_path),
    ]
    exit_code = pytest.main(args)
    if junit_path.exists():
        print(f"\nUI 测试结果已写入: {junit_path}")
        write_summary(junit_path, summary_path, title="UI 测试报告")
        if summary_path.exists():
            print(f"测试摘要已写入: {summary_path}\n" + summary_path.read_text(encoding="utf-8"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
