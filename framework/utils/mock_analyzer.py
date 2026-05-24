"""
模拟 Slither 分析器（用于测试）
当 Slither 未安装时，提供基本的合约检查
"""
import re
from pathlib import Path
from typing import Dict, List


class MockSlitherAnalyzer:
    """模拟 Slither 分析器"""

    def __init__(self):
        self.common_issues = {
            "reentrancy": {
                "impact": "High",
                "confidence": "Medium",
                "description": "Potential reentrancy vulnerability"
            },
            "unchecked-transfer": {
                "impact": "High",
                "confidence": "Medium",
                "description": "Return value of transfer not checked"
            },
            "tx-origin": {
                "impact": "Medium",
                "confidence": "High",
                "description": "Dangerous use of tx.origin"
            },
            "solc-version": {
                "impact": "Informational",
                "confidence": "High",
                "description": "Solidity version not locked"
            }
        }

    def analyze_file(self, contract_path: str) -> Dict:
        """分析单个合约文件"""
        try:
            with open(contract_path, "r") as f:
                content = f.read()

            issues = []

            # 检查 tx.origin
            if "tx.origin" in content:
                issues.append({
                    "check": "tx-origin",
                    "impact": "Medium",
                    "confidence": "High",
                    "description": "Dangerous use of tx.origin for authorization"
                })

            # 检查 Solidity 版本
            if "pragma solidity ^" in content:
                issues.append({
                    "check": "solc-version",
                    "impact": "Informational",
                    "confidence": "High",
                    "description": "Solidity version not locked (using ^)"
                })

            # 检查未检查的 transfer
            if re.search(r'\.transfer\([^)]+\);(?!\s*require)', content):
                issues.append({
                    "check": "unchecked-transfer",
                    "impact": "High",
                    "confidence": "Medium",
                    "description": "Return value of transfer not checked"
                })

            # 检查 selfdestruct
            if "selfdestruct" in content or "suicide" in content:
                issues.append({
                    "check": "suicidal",
                    "impact": "High",
                    "confidence": "High",
                    "description": "Contract can be destroyed"
                })

            return {
                "success": True,
                "results": {
                    "detectors": issues
                }
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def quick_analyze(contract_path: str) -> Dict:
    """快速分析（不依赖 Slither）"""
    analyzer = MockSlitherAnalyzer()
    return analyzer.analyze_file(contract_path)
