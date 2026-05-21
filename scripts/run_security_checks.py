"""
一键执行所有安全和性能检查
"""
import sys
import argparse
from pathlib import Path
from framework.security import SlitherAnalyzer, MythrilScanner, GasAnalyzer
from framework.utils.logger import setup_logger

logger = setup_logger(__name__)


def run_static_analysis(contracts_dir: str = "contracts"):
    """运行静态分析"""
    logger.info("=" * 80)
    logger.info("Running Static Analysis (Slither)")
    logger.info("=" * 80)

    analyzer = SlitherAnalyzer(contracts_dir)
    result = analyzer.analyze()

    if result.get("success", True):
        report = analyzer.generate_report(result)
        print(report)

        high_severity = analyzer.get_high_severity_issues(result)
        if high_severity:
            logger.warning(f"Found {len(high_severity)} high severity issues!")
            return False
        else:
            logger.info("No high severity issues found.")
            return True
    else:
        logger.error(f"Static analysis failed: {result.get('error')}")
        return False


def run_security_scan(contracts_dir: str = "contracts"):
    """运行安全扫描"""
    logger.info("=" * 80)
    logger.info("Running Security Scan (Mythril)")
    logger.info("=" * 80)

    scanner = MythrilScanner(contracts_dir)
    contracts = list(Path(contracts_dir).glob("**/*.sol"))

    all_passed = True
    for contract in contracts:
        logger.info(f"Scanning {contract}...")
        result = scanner.scan(str(contract))

        if result.get("success", True):
            report = scanner.generate_report(result)
            print(report)

            critical_issues = scanner.get_critical_issues(result)
            if critical_issues:
                logger.warning(f"Found {len(critical_issues)} critical issues in {contract.name}!")
                all_passed = False
        else:
            logger.error(f"Security scan failed for {contract}: {result.get('error')}")
            all_passed = False

    return all_passed


def run_all_checks(contracts_dir: str = "contracts", skip_mythril: bool = False):
    """运行所有检查"""
    logger.info("=" * 80)
    logger.info("Starting Security and Performance Checks")
    logger.info("=" * 80)

    results = {}

    # 1. 静态分析
    results["static_analysis"] = run_static_analysis(contracts_dir)

    # 2. 安全扫描（可选，因为 Mythril 比较慢）
    if not skip_mythril:
        results["security_scan"] = run_security_scan(contracts_dir)
    else:
        logger.info("Skipping Mythril security scan (use --mythril to enable)")

    # 3. Gas 报告提示
    logger.info("=" * 80)
    logger.info("Gas Report")
    logger.info("=" * 80)
    logger.info("Gas reports are generated during test execution.")
    logger.info("Run tests with: pytest tests/ -v")
    logger.info("Check reports in: reports/gas/")

    # 总结
    logger.info("=" * 80)
    logger.info("Summary")
    logger.info("=" * 80)
    for check, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        logger.info(f"{check}: {status}")

    all_passed = all(results.values())
    if all_passed:
        logger.info("\n✓ All checks passed!")
        return 0
    else:
        logger.error("\n✗ Some checks failed!")
        return 1


def main():
    parser = argparse.ArgumentParser(description="Run security and performance checks")
    parser.add_argument(
        "--contracts-dir",
        default="contracts",
        help="Contracts directory (default: contracts)"
    )
    parser.add_argument(
        "--mythril",
        action="store_true",
        help="Enable Mythril security scan (slow)"
    )
    parser.add_argument(
        "--static-only",
        action="store_true",
        help="Run only static analysis"
    )

    args = parser.parse_args()

    if args.static_only:
        result = run_static_analysis(args.contracts_dir)
        sys.exit(0 if result else 1)
    else:
        sys.exit(run_all_checks(args.contracts_dir, skip_mythril=not args.mythril))


if __name__ == "__main__":
    main()
