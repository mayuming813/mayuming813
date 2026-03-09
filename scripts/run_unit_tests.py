#!/usr/bin/env python3
"""
按建议顺序执行 SepoliaClaimFaucet 单元测试（01～15），结果写入 log/unit/。
直接运行：python scripts/run_unit_tests.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / "log" / "unit"
sys.path.insert(0, str(ROOT))

# 同目录下的报告模块
import importlib.util
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
        str(ROOT / "tests" / "unit" / "test_sepolia_claim_faucet.py"),
        "-v",
        "-m", "unit",
        "-r", "a",  # 输出所有 skip 原因
        "--junitxml", str(junit_path),
    ]
    exit_code = pytest.main(args)
    if junit_path.exists():
        print(f"\n单元测试结果已写入: {junit_path}")
        write_summary(junit_path, summary_path, title="单元测试报告")
        if summary_path.exists():
            print(f"测试摘要已写入: {summary_path}")
            print("\n" + summary_path.read_text(encoding="utf-8"))
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
