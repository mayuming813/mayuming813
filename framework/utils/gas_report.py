"""
一键 Gas 分析工具 - 可指定具体合约测试
"""
import sys
import argparse
import subprocess
from pathlib import Path
import json
from typing import Optional


class GasReportGenerator:
    """Gas 报告生成器"""

    def __init__(self, output_dir: str = "reports/gas"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_gas_analysis(
        self,
        test_path: str,
        contract_name: Optional[str] = None,
        pytest_args: Optional[list] = None
    ) -> dict:
        """
        运行 Gas 分析

        Args:
            test_path: 测试文件或目录路径
            contract_name: 合约名称（用于报告命名）
            pytest_args: 额外的 pytest 参数

        Returns:
            分析结果
        """
        print(f"\n{'=' * 80}")
        print(f"Running Gas Analysis on: {test_path}")
        print(f"{'=' * 80}\n")

        # 构建 pytest 命令
        cmd = [
            "pytest",
            test_path,
            "-v",
            "--tb=short",
            f"--alluredir=allure-results"
        ]

        if pytest_args:
            cmd.extend(pytest_args)

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)

            print(result.stdout)
            if result.stderr:
                print(result.stderr)

            # 检查 Gas 报告
            self._check_gas_reports(contract_name)

            return {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr if result.returncode != 0 else None
            }

        except subprocess.TimeoutExpired:
            print("❌ Test execution timeout")
            return {"success": False, "error": "Timeout"}
        except FileNotFoundError:
            print("❌ pytest not found. Run: pip install pytest")
            return {"success": False, "error": "pytest not installed"}

    def _check_gas_reports(self, contract_name: Optional[str] = None):
        """检查并显示 Gas 报告"""
        if contract_name:
            pattern = f"gas-report-{contract_name}*.txt"
        else:
            pattern = "gas-report-*.txt"

        reports = list(self.output_dir.glob(pattern))

        if reports:
            print(f"\n{'=' * 80}")
            print("Gas Reports Generated")
            print(f"{'=' * 80}\n")

            for report in reports:
                print(f"📊 {report.name}")
                with open(report, "r") as f:
                    print(f.read())
                print()
        else:
            print("\n⚠️  No gas reports found. Make sure your tests use gas_analyzer fixture.")

    def compare_reports(self, baseline_file: str, current_file: str, threshold: float = 0.1):
        """
        对比 Gas 报告

        Args:
            baseline_file: 基线报告文件
            current_file: 当前报告文件
            threshold: 变化阈值（10% = 0.1）
        """
        print(f"\n{'=' * 80}")
        print("Gas Report Comparison")
        print(f"{'=' * 80}\n")

        try:
            with open(baseline_file, "r") as f:
                baseline = json.load(f)
            with open(current_file, "r") as f:
                current = json.load(f)

            baseline_funcs = baseline.get("functions", {})
            current_funcs = current.get("functions", {})

            print(f"{'Function':<40} {'Baseline':<15} {'Current':<15} {'Change':<15}")
            print("-" * 90)

            for func_name in sorted(set(baseline_funcs.keys()) | set(current_funcs.keys())):
                if func_name in baseline_funcs and func_name in current_funcs:
                    baseline_avg = baseline_funcs[func_name]["avg"]
                    current_avg = current_funcs[func_name]["avg"]
                    diff_percent = (current_avg - baseline_avg) / baseline_avg * 100

                    icon = "🔴" if diff_percent > threshold * 100 else "🟢" if diff_percent < -threshold * 100 else "⚪"
                    print(f"{func_name:<40} {baseline_avg:<15,.0f} {current_avg:<15,.0f} {icon} {diff_percent:>+6.2f}%")

                elif func_name in current_funcs:
                    print(f"{func_name:<40} {'N/A':<15} {current_funcs[func_name]['avg']:<15,.0f} {'🆕 NEW':<15}")
                else:
                    print(f"{func_name:<40} {baseline_funcs[func_name]['avg']:<15,.0f} {'N/A':<15} {'❌ REMOVED':<15}")

        except FileNotFoundError as e:
            print(f"❌ File not found: {e}")
        except json.JSONDecodeError:
            print("❌ Invalid JSON format")


def main():
    parser = argparse.ArgumentParser(
        description="Run Gas analysis on smart contract tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze specific test file
  python -m framework.utils.gas_report --test tests/nft_mint/scenarios/test_nft_scenario.py

  # Analyze all tests for a contract
  python -m framework.utils.gas_report --test tests/nft_mint/ --contract NFTMint

  # Compare with baseline
  python -m framework.utils.gas_report --compare --baseline reports/gas/baseline-NFTMint.json --current reports/gas/gas-report-NFTMint.json
        """
    )

    parser.add_argument(
        "--test",
        help="Test file or directory path"
    )
    parser.add_argument(
        "--contract",
        help="Contract name (for report filtering)"
    )
    parser.add_argument(
        "--output",
        default="reports/gas",
        help="Output directory for reports (default: reports/gas)"
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare gas reports"
    )
    parser.add_argument(
        "--baseline",
        help="Baseline report file (for comparison)"
    )
    parser.add_argument(
        "--current",
        help="Current report file (for comparison)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.1,
        help="Change threshold for comparison (default: 0.1 = 10%%)"
    )
    parser.add_argument(
        "--pytest-args",
        nargs=argparse.REMAINDER,
        help="Additional pytest arguments"
    )

    args = parser.parse_args()

    generator = GasReportGenerator(args.output)

    # 对比模式
    if args.compare:
        if not args.baseline or not args.current:
            print("❌ --baseline and --current are required for comparison")
            sys.exit(1)

        generator.compare_reports(args.baseline, args.current, args.threshold)
        sys.exit(0)

    # 分析模式
    if not args.test:
        print("❌ --test is required for gas analysis")
        parser.print_help()
        sys.exit(1)

    test_path = Path(args.test)
    if not test_path.exists():
        print(f"❌ Test path not found: {args.test}")
        sys.exit(1)

    result = generator.run_gas_analysis(
        args.test,
        contract_name=args.contract,
        pytest_args=args.pytest_args
    )

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
