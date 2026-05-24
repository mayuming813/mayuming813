#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : reconciliation_reporter.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import json
import allure
from typing import Dict, Any
from framework.reconciliation.reconciliation_engine import ReconciliationResult, ReconciliationStatus


class ReconciliationReporter:
    """对账报告生成器"""

    @staticmethod
    def attach_summary_to_allure(result: ReconciliationResult):
        """
        将对账汇总附加到 Allure 报告
        :param result: 对账结果
        """
        summary = result.get_summary()

        allure.attach(
            json.dumps(summary, indent=2, ensure_ascii=False),
            name="📊 对账汇总",
            attachment_type=allure.attachment_type.JSON
        )

    @staticmethod
    def attach_details_to_allure(result: ReconciliationResult, max_details: int = 100):
        """
        将对账明细附加到 Allure 报告
        :param result: 对账结果
        :param max_details: 最大明细数量
        """
        # 只附加不匹配的明细
        mismatched_details = [
            detail for detail in result.details
            if detail['status'] != ReconciliationStatus.MATCHED
        ]

        if mismatched_details:
            details_to_attach = mismatched_details[:max_details]
            allure.attach(
                json.dumps(details_to_attach, indent=2, ensure_ascii=False),
                name="❌ 对账差异明细",
                attachment_type=allure.attachment_type.JSON
            )

        # 如果全部匹配，附加成功信息
        if result.is_success():
            allure.attach(
                "所有数据对账一致",
                name="✅ 对账成功",
                attachment_type=allure.attachment_type.TEXT
            )

    @staticmethod
    def generate_text_report(result: ReconciliationResult) -> str:
        """
        生成文本格式报告
        :param result: 对账结果
        :return: 文本报告
        """
        summary = result.get_summary()

        report_lines = [
            "=" * 60,
            "对账报告",
            "=" * 60,
            f"总数量: {summary['total_count']}",
            f"匹配数量: {summary['matched_count']}",
            f"不匹配数量: {summary['mismatched_count']}",
            f"链上缺失: {summary['missing_onchain_count']}",
            f"链下缺失: {summary['missing_offchain_count']}",
            f"待确认: {summary['pending_count']}",
            f"匹配率: {summary['match_rate']}",
            f"耗时: {summary['duration_seconds']:.2f} 秒",
            f"开始时间: {summary['start_time']}",
            f"结束时间: {summary['end_time']}",
            "=" * 60
        ]

        # 添加差异明细
        if result.mismatched_count > 0:
            report_lines.append("\n差异明细:")
            report_lines.append("-" * 60)

            for detail in result.details:
                if detail['status'] != ReconciliationStatus.MATCHED:
                    report_lines.append(f"\n关键字: {detail['key']}")
                    report_lines.append(f"状态: {detail['status'].value}")
                    report_lines.append(f"消息: {detail['message']}")

                    if detail.get('differences'):
                        report_lines.append("差异字段:")
                        for diff in detail['differences']:
                            report_lines.append(
                                f"  - {diff['field']}: "
                                f"链上={diff['onchain_value']}, "
                                f"链下={diff['offchain_value']}"
                            )

        return "\n".join(report_lines)

    @staticmethod
    def save_to_file(result: ReconciliationResult, file_path: str, format: str = 'json'):
        """
        保存对账结果到文件
        :param result: 对账结果
        :param file_path: 文件路径
        :param format: 格式（json/text）
        """
        if format == 'json':
            report_data = {
                'summary': result.get_summary(),
                'details': [
                    {
                        'key': detail['key'],
                        'status': detail['status'].value,
                        'message': detail['message'],
                        'differences': detail.get('differences', []),
                        'timestamp': detail['timestamp']
                    }
                    for detail in result.details
                ]
            }

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, ensure_ascii=False, indent=2)

        elif format == 'text':
            report_text = ReconciliationReporter.generate_text_report(result)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_text)

    @staticmethod
    def print_summary(result: ReconciliationResult):
        """
        打印对账汇总
        :param result: 对账结果
        """
        print(ReconciliationReporter.generate_text_report(result))
