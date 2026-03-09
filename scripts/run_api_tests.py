#!/usr/bin/env python3
"""
执行链上/接口测试，结果写入 log/api/，并生成失败/跳过摘要。
直接运行：python scripts/run_api_tests.py
"""
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "log" / "api"
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
        str(ROOT / "tests" / "api"),
        "-v", "-r", "a",
        "-m", "api",
        "--junitxml", str(junit_path),
    ]
    exit_code = pytest.main(args)
    if junit_path.exists():
        print(f"\n接口测试结果已写入: {junit_path}")
        write_summary(junit_path, summary_path, title="接口测试报告")
        if summary_path.exists():
            print(f"测试摘要已写入: {summary_path}\n" + summary_path.read_text(encoding="utf-8"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
