"""
合约大小检查工具
"""
import sys
import argparse
import subprocess
import json
from pathlib import Path
from typing import Dict, List


class ContractSizeChecker:
    """合约大小检查器"""

    MAX_CONTRACT_SIZE = 24576  # 24KB (EIP-170)

    def __init__(self, output_dir: str = "reports/contract-size"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def check_contract_sizes(self, artifacts_dir: str = "artifacts/contracts") -> Dict:
        """
        检查合约大小

        Args:
            artifacts_dir: 编译产物目录

        Returns:
            检查结果
        """
        print(f"\n{'=' * 80}")
        print("Contract Size Check")
        print(f"{'=' * 80}\n")

        artifacts_path = Path(artifacts_dir)
        if not artifacts_path.exists():
            print(f"❌ Artifacts directory not found: {artifacts_dir}")
            print("Run 'npm run compile' first to compile contracts")
            return {"success": False, "error": "Artifacts not found"}

        # 查找所有合约 JSON 文件
        contract_files = list(artifacts_path.glob("**/*.json"))
        contract_files = [f for f in contract_files if not f.name.endswith(".dbg.json")]

        if not contract_files:
            print(f"❌ No contract artifacts found in {artifacts_dir}")
            return {"success": False, "error": "No contracts found"}

        results = []
        oversized = []

        print(f"{'Contract':<40} {'Size (bytes)':<15} {'Size (KB)':<15} {'Status':<10}")
        print("-" * 85)

        for contract_file in sorted(contract_files):
            try:
                with open(contract_file, "r") as f:
                    data = json.load(f)

                bytecode = data.get("bytecode", "")
                if bytecode.startswith("0x"):
                    bytecode = bytecode[2:]

                size_bytes = len(bytecode) // 2
                size_kb = size_bytes / 1024
                percentage = (size_bytes / self.MAX_CONTRACT_SIZE) * 100

                contract_name = contract_file.stem
                status = "✅ OK" if size_bytes <= self.MAX_CONTRACT_SIZE else "❌ TOO LARGE"

                if size_bytes > self.MAX_CONTRACT_SIZE:
                    oversized.append({
                        "name": contract_name,
                        "size": size_bytes,
                        "excess": size_bytes - self.MAX_CONTRACT_SIZE
                    })

                results.append({
                    "name": contract_name,
                    "size_bytes": size_bytes,
                    "size_kb": size_kb,
                    "percentage": percentage,
                    "valid": size_bytes <= self.MAX_CONTRACT_SIZE
                })

                icon = "✅" if size_bytes <= self.MAX_CONTRACT_SIZE else "❌"
                print(f"{contract_name:<40} {size_bytes:<15,} {size_kb:<15.2f} {icon} {percentage:>5.1f}%")

            except Exception as e:
                print(f"⚠️  Failed to check {contract_file.name}: {e}")

        # 保存报告
        report_data = {
            "max_size": self.MAX_CONTRACT_SIZE,
            "contracts": results,
            "oversized": oversized
        }

        report_file = self.output_dir / "contract-size-report.json"
        with open(report_file, "w") as f:
            json.dump(report_data, f, indent=2)

        # 文本报告
        text_report = self._generate_text_report(report_data)
        text_file = self.output_dir / "contract-size-report.txt"
        with open(text_file, "w") as f:
            f.write(text_report)

        print(f"\n{'=' * 80}")
        print(f"Total contracts: {len(results)}")
        print(f"Oversized contracts: {len(oversized)}")
        print(f"Reports saved to: {self.output_dir}")
        print(f"{'=' * 80}")

        if oversized:
            print("\n⚠️  Oversized Contracts:")
            for contract in oversized:
                print(f"  - {contract['name']}: {contract['size']:,} bytes (exceeds by {contract['excess']:,} bytes)")

        return {
            "success": len(oversized) == 0,
            "total": len(results),
            "oversized": len(oversized),
            "contracts": results
        }

    def _generate_text_report(self, data: Dict) -> str:
        """生成文本报告"""
        lines = ["=" * 80]
        lines.append("Contract Size Report")
        lines.append("=" * 80)
        lines.append(f"Max Contract Size: {data['max_size']:,} bytes (24 KB)")
        lines.append("")
        lines.append(f"{'Contract':<40} {'Size (bytes)':<15} {'Size (KB)':<15} {'Usage %':<10}")
        lines.append("-" * 85)

        for contract in data["contracts"]:
            status = "✅" if contract["valid"] else "❌"
            lines.append(
                f"{contract['name']:<40} {contract['size_bytes']:<15,} "
                f"{contract['size_kb']:<15.2f} {status} {contract['percentage']:>5.1f}%"
            )

        lines.append("=" * 80)
        lines.append(f"Total Contracts: {len(data['contracts'])}")
        lines.append(f"Oversized Contracts: {len(data['oversized'])}")

        if data["oversized"]:
            lines.append("\n⚠️  Oversized Contracts:")
            for contract in data["oversized"]:
                lines.append(f"  - {contract['name']}: {contract['size']:,} bytes (exceeds by {contract['excess']:,} bytes)")

        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Check smart contract sizes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check all compiled contracts
  python -m framework.utils.contract_size

  # Specify custom artifacts directory
  python -m framework.utils.contract_size --artifacts artifacts/contracts

  # Compile and check
  npm run compile && python -m framework.utils.contract_size
        """
    )

    parser.add_argument(
        "--artifacts",
        default="artifacts/contracts",
        help="Artifacts directory (default: artifacts/contracts)"
    )
    parser.add_argument(
        "--output",
        default="reports/contract-size",
        help="Output directory for reports (default: reports/contract-size)"
    )
    parser.add_argument(
        "--compile",
        action="store_true",
        help="Compile contracts before checking"
    )

    args = parser.parse_args()

    # 编译合约
    if args.compile:
        print("Compiling contracts...")
        try:
            subprocess.run(["npm", "run", "compile"], check=True)
        except subprocess.CalledProcessError:
            print("❌ Compilation failed")
            sys.exit(1)

    checker = ContractSizeChecker(args.output)
    result = checker.check_contract_sizes(args.artifacts)

    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
