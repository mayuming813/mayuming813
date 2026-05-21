"""
安全扫描工具 - Mythril 集成
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import allure


class MythrilScanner:
    """Mythril 安全扫描器"""

    def __init__(self, contracts_dir: str = "contracts"):
        self.contracts_dir = Path(contracts_dir)
        self.report_dir = Path("reports/security")
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def scan(
        self,
        contract_path: str,
        max_depth: int = 22,
        execution_timeout: int = 300
    ) -> Dict:
        """
        运行 Mythril 安全扫描

        Args:
            contract_path: 合约文件路径
            max_depth: 最大搜索深度
            execution_timeout: 执行超时时间（秒）

        Returns:
            扫描结果字典
        """
        cmd = [
            "myth",
            "analyze",
            contract_path,
            "--max-depth", str(max_depth),
            "--execution-timeout", str(execution_timeout),
            "-o", "json"
        ]

        with allure.step(f"运行 Mythril 安全扫描: {contract_path}"):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=execution_timeout + 60
                )

                if result.stdout:
                    scan_result = json.loads(result.stdout)
                else:
                    scan_result = {"success": False, "error": result.stderr}

                # 保存报告
                contract_name = Path(contract_path).stem
                report_file = self.report_dir / f"mythril-{contract_name}.json"
                with open(report_file, "w") as f:
                    json.dump(scan_result, f, indent=2)

                allure.attach(
                    json.dumps(scan_result, indent=2),
                    name=f"Mythril Scan Report - {contract_name}",
                    attachment_type=allure.attachment_type.JSON
                )

                return scan_result

            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Scan timeout"}
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse Mythril output"}
            except FileNotFoundError:
                return {"success": False, "error": "Mythril not installed. Run: pip install mythril"}

    def get_issues(self, scan_result: Dict) -> List[Dict]:
        """提取安全问题列表"""
        if not scan_result.get("success", True):
            return []

        return scan_result.get("issues", [])

    def get_critical_issues(self, scan_result: Dict) -> List[Dict]:
        """获取严重安全问题"""
        issues = self.get_issues(scan_result)
        return [i for i in issues if i.get("severity") in ["High", "Critical"]]

    def generate_report(self, scan_result: Dict) -> str:
        """生成可读报告"""
        issues = self.get_issues(scan_result)

        report = ["=" * 80]
        report.append("Mythril Security Scan Report")
        report.append("=" * 80)
        report.append(f"Total Issues Found: {len(issues)}")
        report.append("")

        # 按严重程度分组
        severity_groups = {}
        for issue in issues:
            severity = issue.get("severity", "Unknown")
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(issue)

        for severity in ["Critical", "High", "Medium", "Low"]:
            if severity in severity_groups:
                report.append(f"\n{severity} Severity Issues ({len(severity_groups[severity])})")
                report.append("-" * 80)
                for issue in severity_groups[severity]:
                    report.append(f"  Title: {issue.get('title', 'Unknown')}")
                    report.append(f"  Type: {issue.get('swc-id', 'Unknown')}")
                    report.append(f"  Description: {issue.get('description', 'No description')}")
                    report.append("")

        return "\n".join(report)