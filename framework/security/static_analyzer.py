"""
静态分析工具 - Slither 集成
"""
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import allure


class SlitherAnalyzer:
    """Slither 静态分析器"""

    def __init__(self, contracts_dir: str = "contracts"):
        self.contracts_dir = Path(contracts_dir)
        self.report_dir = Path("reports/security")
        self.report_dir.mkdir(parents=True, exist_ok=True)

    def analyze(self, contract_path: Optional[str] = None, detectors: Optional[List[str]] = None) -> Dict:
        """
        运行 Slither 静态分析

        Args:
            contract_path: 合约路径，None 表示分析所有合约
            detectors: 指定检测器列表，None 表示使用所有检测器

        Returns:
            分析结果字典
        """
        target = contract_path if contract_path else str(self.contracts_dir)

        cmd = ["slither", target, "--json", "-"]

        if detectors:
            cmd.extend(["--detect", ",".join(detectors)])

        with allure.step(f"运行 Slither 静态分析: {target}"):
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300
                )

                # Slither 即使发现问题也可能返回非零退出码
                if result.stdout:
                    analysis_result = json.loads(result.stdout)
                else:
                    analysis_result = {"success": False, "error": result.stderr}

                # 保存报告
                report_file = self.report_dir / "slither-report.json"
                with open(report_file, "w") as f:
                    json.dump(analysis_result, f, indent=2)

                allure.attach(
                    json.dumps(analysis_result, indent=2),
                    name="Slither Analysis Report",
                    attachment_type=allure.attachment_type.JSON
                )

                return analysis_result

            except subprocess.TimeoutExpired:
                return {"success": False, "error": "Analysis timeout"}
            except json.JSONDecodeError:
                return {"success": False, "error": "Failed to parse Slither output"}
            except FileNotFoundError:
                return {"success": False, "error": "Slither not installed. Run: pip install slither-analyzer"}

    def get_vulnerabilities(self, analysis_result: Dict) -> List[Dict]:
        """提取漏洞列表"""
        if not analysis_result.get("success", True):
            return []

        return analysis_result.get("results", {}).get("detectors", [])

    def get_high_severity_issues(self, analysis_result: Dict) -> List[Dict]:
        """获取高危漏洞"""
        vulnerabilities = self.get_vulnerabilities(analysis_result)
        return [v for v in vulnerabilities if v.get("impact") in ["High", "Critical"]]

    def generate_report(self, analysis_result: Dict) -> str:
        """生成可读报告"""
        vulnerabilities = self.get_vulnerabilities(analysis_result)

        report = ["=" * 80]
        report.append("Slither Static Analysis Report")
        report.append("=" * 80)
        report.append(f"Total Issues Found: {len(vulnerabilities)}")
        report.append("")

        # 按严重程度分组
        severity_groups = {}
        for vuln in vulnerabilities:
            severity = vuln.get("impact", "Unknown")
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(vuln)

        for severity in ["Critical", "High", "Medium", "Low", "Informational"]:
            if severity in severity_groups:
                report.append(f"\n{severity} Severity Issues ({len(severity_groups[severity])})")
                report.append("-" * 80)
                for vuln in severity_groups[severity]:
                    report.append(f"  - {vuln.get('check', 'Unknown')}: {vuln.get('description', 'No description')}")

        return "\n".join(report)
