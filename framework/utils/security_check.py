"""
一键安全检查工具 - 可指定具体合约
"""
import sys
import argparse
from pathlib import Path
from typing import Optional, List
import json


class SecurityChecker:
    """安全检查工具"""

    def __init__(self, output_dir: str = "reports/security"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run_slither(self, contract_path: str, detectors: Optional[List[str]] = None) -> dict:
        """
        运行 Slither 静态分析

        Args:
            contract_path: 合约路径（文件或目录）
            detectors: 指定检测器列表

        Returns:
            分析结果
        """
        import subprocess

        print(f"\n{'=' * 80}")
        print(f"Running Slither on: {contract_path}")
        print(f"{'=' * 80}\n")

        cmd = ["slither", contract_path, "--json", "-"]
        if detectors:
            cmd.extend(["--detect", ",".join(detectors)])

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)

            if result.stdout:
                data = json.loads(result.stdout)
            else:
                data = {"success": False, "error": result.stderr}

            # 保存报告
            contract_name = Path(contract_path).stem
            report_file = self.output_dir / f"slither-{contract_name}.json"
            with open(report_file, "w") as f:
                json.dump(data, f, indent=2)

            # 打印摘要
            self._print_slither_summary(data)

            return data

        except subprocess.TimeoutExpired:
            print("❌ Slither timeout")
            return {"success": False, "error": "Timeout"}
        except json.JSONDecodeError:
            print("❌ Failed to parse Slither output")
            return {"success": False, "error": "Parse error"}
        except FileNotFoundError:
            print("⚠️  Slither not installed. Using basic analysis...")
            print("   To install: pip install slither-analyzer\n")
            # 使用基本分析作为后备
            return self._run_basic_analysis(contract_path)

    def run_mythril(self, contract_path: str, max_depth: int = 22, timeout: int = 300) -> dict:
        """
        运行 Mythril 安全扫描

        Args:
            contract_path: 合约文件路径
            max_depth: 最大搜索深度
            timeout: 超时时间（秒）

        Returns:
            扫描结果
        """
        import subprocess

        print(f"\n{'=' * 80}")
        print(f"Running Mythril on: {contract_path}")
        print(f"{'=' * 80}\n")

        cmd = [
            "myth", "analyze", contract_path,
            "--max-depth", str(max_depth),
            "--execution-timeout", str(timeout),
            "-o", "json"
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout + 60)

            if result.stdout:
                data = json.loads(result.stdout)
            else:
                data = {"success": False, "error": result.stderr}

            # 保存报告
            contract_name = Path(contract_path).stem
            report_file = self.output_dir / f"mythril-{contract_name}.json"
            with open(report_file, "w") as f:
                json.dump(data, f, indent=2)

            # 打印摘要
            self._print_mythril_summary(data)

            return data

        except subprocess.TimeoutExpired:
            print("❌ Mythril timeout")
            return {"success": False, "error": "Timeout"}
        except json.JSONDecodeError:
            print("❌ Failed to parse Mythril output")
            return {"success": False, "error": "Parse error"}
        except FileNotFoundError:
            print("❌ Mythril not installed. Run: pip install mythril")
            return {"success": False, "error": "Not installed"}

    def _print_slither_summary(self, data: dict):
        """打印 Slither 摘要"""
        if not data.get("success", True):
            print(f"❌ Analysis failed: {data.get('error')}")
            return

        detectors = data.get("results", {}).get("detectors", [])

        # 按严重程度统计
        severity_count = {}
        for d in detectors:
            severity = d.get("impact", "Unknown")
            severity_count[severity] = severity_count.get(severity, 0) + 1

        print(f"Total issues: {len(detectors)}")
        for severity in ["Critical", "High", "Medium", "Low", "Informational"]:
            if severity in severity_count:
                icon = "🔴" if severity in ["Critical", "High"] else "🟡" if severity == "Medium" else "🟢"
                print(f"  {icon} {severity}: {severity_count[severity]}")

        # 显示高危问题
        high_issues = [d for d in detectors if d.get("impact") in ["Critical", "High"]]
        if high_issues:
            print(f"\n⚠️  High Severity Issues:")
            for issue in high_issues[:5]:  # 只显示前5个
                print(f"  - {issue.get('check')}: {issue.get('description', '')[:80]}")

    def _print_mythril_summary(self, data: dict):
        """打印 Mythril 摘要"""
        if not data.get("success", True):
            print(f"❌ Scan failed: {data.get('error')}")
            return

        issues = data.get("issues", [])

        # 按严重程度统计
        severity_count = {}
        for issue in issues:
            severity = issue.get("severity", "Unknown")
            severity_count[severity] = severity_count.get(severity, 0) + 1

        print(f"Total issues: {len(issues)}")
        for severity in ["Critical", "High", "Medium", "Low"]:
            if severity in severity_count:
                icon = "🔴" if severity in ["Critical", "High"] else "🟡" if severity == "Medium" else "🟢"
                print(f"  {icon} {severity}: {severity_count[severity]}")

        # 显示严重问题
        critical_issues = [i for i in issues if i.get("severity") in ["Critical", "High"]]
        if critical_issues:
            print(f"\n⚠️  Critical Issues:")
            for issue in critical_issues[:5]:
                print(f"  - {issue.get('title')}: {issue.get('description', '')[:80]}")

    def _run_basic_analysis(self, contract_path: str) -> dict:
        """运行基本分析（不依赖 Slither）"""
        from .mock_analyzer import quick_analyze

        path = Path(contract_path)

        if path.is_file():
            result = quick_analyze(str(path))
        else:
            # 分析目录中的所有合约
            all_issues = []
            for sol_file in path.glob("**/*.sol"):
                file_result = quick_analyze(str(sol_file))
                if file_result.get("success"):
                    all_issues.extend(file_result["results"]["detectors"])

            result = {
                "success": True,
                "results": {
                    "detectors": all_issues
                }
            }

        # 保存报告
        contract_name = path.stem if path.is_file() else "all"
        report_file = self.output_dir / f"basic-analysis-{contract_name}.json"
        with open(report_file, "w") as f:
            json.dump(result, f, indent=2)

        # 打印摘要
        self._print_slither_summary(result)

        return result


def main():
    parser = argparse.ArgumentParser(
        description="Run security checks on smart contracts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check single contract with Slither
  python -m framework.utils.security_check --contract contracts/NFTMint.sol --slither

  # Check with Mythril (slower)
  python -m framework.utils.security_check --contract contracts/NFTMint.sol --mythril

  # Check all contracts in directory
  python -m framework.utils.security_check --contract contracts/ --slither

  # Full check (both tools)
  python -m framework.utils.security_check --contract contracts/NFTMint.sol --all
        """
    )

    parser.add_argument(
        "--contract",
        required=True,
        help="Contract file or directory path"
    )
    parser.add_argument(
        "--slither",
        action="store_true",
        help="Run Slither static analysis"
    )
    parser.add_argument(
        "--mythril",
        action="store_true",
        help="Run Mythril security scan"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all security checks"
    )
    parser.add_argument(
        "--output",
        default="reports/security",
        help="Output directory for reports (default: reports/security)"
    )
    parser.add_argument(
        "--max-depth",
        type=int,
        default=22,
        help="Mythril max depth (default: 22)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=300,
        help="Mythril timeout in seconds (default: 300)"
    )

    args = parser.parse_args()

    # 检查合约路径
    contract_path = Path(args.contract)
    if not contract_path.exists():
        print(f"❌ Contract path not found: {args.contract}")
        sys.exit(1)

    # 至少选择一个工具
    if not (args.slither or args.mythril or args.all):
        print("❌ Please specify at least one tool: --slither, --mythril, or --all")
        parser.print_help()
        sys.exit(1)

    checker = SecurityChecker(args.output)
    results = {}

    # 运行 Slither
    if args.slither or args.all:
        results["slither"] = checker.run_slither(args.contract)

    # 运行 Mythril
    if args.mythril or args.all:
        if contract_path.is_file():
            results["mythril"] = checker.run_mythril(
                args.contract,
                max_depth=args.max_depth,
                timeout=args.timeout
            )
        else:
            print("\n⚠️  Mythril only supports single file, skipping directory scan")

    # 总结
    print(f"\n{'=' * 80}")
    print("Summary")
    print(f"{'=' * 80}")

    all_passed = True
    for tool, result in results.items():
        if result.get("success", True):
            print(f"✅ {tool.capitalize()}: Completed")
        else:
            print(f"❌ {tool.capitalize()}: Failed - {result.get('error')}")
            all_passed = False

    print(f"\nReports saved to: {args.output}")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
