"""
Gas 费用分析工具
"""
import json
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import allure


class GasAnalyzer:
    """Gas 费用分析器"""

    def __init__(self):
        self.report_dir = Path("reports/gas")
        self.report_dir.mkdir(parents=True, exist_ok=True)
        self.gas_records = defaultdict(list)

    def record_transaction(self, function_name: str, gas_used: int, tx_hash: str = ""):
        """
        记录交易 Gas 消耗

        Args:
            function_name: 函数名称
            gas_used: Gas 消耗量
            tx_hash: 交易哈希
        """
        self.gas_records[function_name].append({
            "gas_used": gas_used,
            "tx_hash": tx_hash
        })

    def get_average_gas(self, function_name: str) -> Optional[float]:
        """获取函数平均 Gas 消耗"""
        if function_name not in self.gas_records:
            return None

        records = self.gas_records[function_name]
        return sum(r["gas_used"] for r in records) / len(records)

    def get_min_gas(self, function_name: str) -> Optional[int]:
        """获取函数最小 Gas 消耗"""
        if function_name not in self.gas_records:
            return None

        return min(r["gas_used"] for r in self.gas_records[function_name])

    def get_max_gas(self, function_name: str) -> Optional[int]:
        """获取函数最大 Gas 消耗"""
        if function_name not in self.gas_records:
            return None

        return max(r["gas_used"] for r in self.gas_records[function_name])

    def generate_report(self, contract_name: str = "Contract") -> str:
        """
        生成 Gas 费用报告

        Args:
            contract_name: 合约名称

        Returns:
            报告文本
        """
        report = ["=" * 100]
        report.append(f"Gas Report - {contract_name}")
        report.append("=" * 100)
        report.append("")
        report.append(f"{'Function':<40} {'Calls':<10} {'Min':<15} {'Avg':<15} {'Max':<15}")
        report.append("-" * 100)

        for function_name in sorted(self.gas_records.keys()):
            records = self.gas_records[function_name]
            calls = len(records)
            min_gas = self.get_min_gas(function_name)
            avg_gas = self.get_average_gas(function_name)
            max_gas = self.get_max_gas(function_name)

            report.append(
                f"{function_name:<40} {calls:<10} {min_gas:<15,} {avg_gas:<15,.0f} {max_gas:<15,}"
            )

        report.append("=" * 100)

        # 计算总 Gas 消耗
        total_gas = sum(
            sum(r["gas_used"] for r in records)
            for records in self.gas_records.values()
        )
        report.append(f"Total Gas Used: {total_gas:,}")

        return "\n".join(report)

    def save_report(self, contract_name: str = "Contract"):
        """保存报告到文件"""
        report_text = self.generate_report(contract_name)
        report_file = self.report_dir / f"gas-report-{contract_name}.txt"

        with open(report_file, "w") as f:
            f.write(report_text)

        # 保存 JSON 格式
        json_data = {
            "contract": contract_name,
            "functions": {
                func: {
                    "calls": len(records),
                    "min": self.get_min_gas(func),
                    "avg": self.get_average_gas(func),
                    "max": self.get_max_gas(func),
                    "records": records
                }
                for func, records in self.gas_records.items()
            }
        }

        json_file = self.report_dir / f"gas-report-{contract_name}.json"
        with open(json_file, "w") as f:
            json.dump(json_data, f, indent=2)

        # 附加到 Allure 报告
        allure.attach(
            report_text,
            name=f"Gas Report - {contract_name}",
            attachment_type=allure.attachment_type.TEXT
        )

        return report_file

    def compare_with_baseline(self, baseline_file: str, threshold: float = 0.1) -> Dict:
        """
        与基线对比

        Args:
            baseline_file: 基线文件路径
            threshold: 阈值（10% = 0.1）

        Returns:
            对比结果
        """
        with open(baseline_file, "r") as f:
            baseline = json.load(f)

        comparison = {
            "increased": [],
            "decreased": [],
            "new": [],
            "removed": []
        }

        baseline_functions = baseline.get("functions", {})

        for func_name in self.gas_records.keys():
            current_avg = self.get_average_gas(func_name)

            if func_name in baseline_functions:
                baseline_avg = baseline_functions[func_name]["avg"]
                diff_percent = (current_avg - baseline_avg) / baseline_avg

                if diff_percent > threshold:
                    comparison["increased"].append({
                        "function": func_name,
                        "baseline": baseline_avg,
                        "current": current_avg,
                        "diff_percent": diff_percent * 100
                    })
                elif diff_percent < -threshold:
                    comparison["decreased"].append({
                        "function": func_name,
                        "baseline": baseline_avg,
                        "current": current_avg,
                        "diff_percent": diff_percent * 100
                    })
            else:
                comparison["new"].append(func_name)

        for func_name in baseline_functions.keys():
            if func_name not in self.gas_records:
                comparison["removed"].append(func_name)

        return comparison

    def clear(self):
        """清空记录"""
        self.gas_records.clear()


class GasTracker:
    """Gas 追踪装饰器和上下文管理器"""

    def __init__(self, analyzer: GasAnalyzer, web3_client):
        self.analyzer = analyzer
        self.client = web3_client

    def track(self, function_name: str):
        """装饰器：自动追踪函数 Gas 消耗"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                result = func(*args, **kwargs)

                # 假设返回的是交易哈希或交易回执
                if isinstance(result, str):  # 交易哈希
                    receipt = self.client.w3.eth.get_transaction_receipt(result)
                    gas_used = receipt["gasUsed"]
                    tx_hash = result
                elif isinstance(result, dict) and "gasUsed" in result:  # 交易回执
                    gas_used = result["gasUsed"]
                    tx_hash = result.get("transactionHash", "")
                else:
                    return result

                self.analyzer.record_transaction(function_name, gas_used, tx_hash)
                return result

            return wrapper
        return decorator
