#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_reconciliation_examples.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from framework.reconciliation.reconciliation_engine import (
    ReconciliationEngine,
    ReconciliationMode,
    ReconciliationStatus
)
from framework.reconciliation.data_fetcher import (
    OnchainDataFetcher,
    OffchainDataFetcher,
    AsyncDataFetcher
)
from framework.reconciliation.reconciliation_reporter import ReconciliationReporter
from framework.utils.test_data_factory import TestDataFactory


@allure.feature("对账功能")
@allure.story("实时对账")
class TestRealtimeReconciliation:
    """实时对账示例"""

    @allure.title("示例：基础对账 - 交易数据")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("对比链上和链下的交易数据")
    def test_basic_reconciliation(self):
        """示例：基础对账"""
        # 模拟链上数据
        onchain_data = [
            {
                'tx_hash': '0x123',
                'from': '0xaaa',
                'to': '0xbbb',
                'value': 1000000000000000000,
                'timestamp': 1234567890
            },
            {
                'tx_hash': '0x456',
                'from': '0xbbb',
                'to': '0xccc',
                'value': 2000000000000000000,
                'timestamp': 1234567900
            }
        ]

        # 模拟链下数据
        offchain_data = [
            {
                'tx_hash': '0x123',
                'from': '0xaaa',
                'to': '0xbbb',
                'value': 1000000000000000000,
                'timestamp': 1234567890
            },
            {
                'tx_hash': '0x456',
                'from': '0xbbb',
                'to': '0xccc',
                'value': 2000000000000000000,
                'timestamp': 1234567900
            }
        ]

        # 执行对账
        engine = ReconciliationEngine(mode=ReconciliationMode.REALTIME)
        result = engine.reconcile(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            key_field='tx_hash',
            compare_fields=['from', 'to', 'value']
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.attach_details_to_allure(result)

        # 断言
        assert result.is_success(), "对账失败"
        assert result.matched_count == 2, "匹配数量不正确"

    @allure.title("示例：对账差异检测")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("检测链上和链下数据的差异")
    def test_reconciliation_with_differences(self):
        """示例：对账差异检测"""
        # 模拟链上数据
        onchain_data = [
            {'tx_hash': '0x123', 'value': 1000, 'status': 'success'},
            {'tx_hash': '0x456', 'value': 2000, 'status': 'success'},
        ]

        # 模拟链下数据（有差异）
        offchain_data = [
            {'tx_hash': '0x123', 'value': 1000, 'status': 'success'},
            {'tx_hash': '0x456', 'value': 2500, 'status': 'pending'},  # 金额和状态不同
        ]

        # 执行对账
        engine = ReconciliationEngine()
        result = engine.reconcile(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            key_field='tx_hash',
            compare_fields=['value', 'status']
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.attach_details_to_allure(result)
        ReconciliationReporter.print_summary(result)

        # 断言
        assert result.mismatched_count == 1, "应该有1条不匹配"
        assert result.matched_count == 1, "应该有1条匹配"

    @allure.title("示例：数据缺失检测")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("检测链上或链下数据缺失")
    def test_reconciliation_with_missing_data(self):
        """示例：数据缺失检测"""
        # 模拟链上数据
        onchain_data = [
            {'tx_hash': '0x123', 'value': 1000},
            {'tx_hash': '0x456', 'value': 2000},
            {'tx_hash': '0x789', 'value': 3000},  # 链下缺失
        ]

        # 模拟链下数据
        offchain_data = [
            {'tx_hash': '0x123', 'value': 1000},
            {'tx_hash': '0x456', 'value': 2000},
            {'tx_hash': '0xabc', 'value': 4000},  # 链上缺失
        ]

        # 执行对账
        engine = ReconciliationEngine()
        result = engine.reconcile(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            key_field='tx_hash'
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.attach_details_to_allure(result)

        # 断言
        assert result.matched_count == 2, "应该有2条匹配"
        assert result.missing_offchain_count == 1, "应该有1条链下缺失"
        assert result.missing_onchain_count == 1, "应该有1条链上缺失"


@allure.feature("对账功能")
@allure.story("自定义对比逻辑")
class TestCustomComparator:
    """自定义对比逻辑示例"""

    @allure.title("示例：自定义对比函数")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("使用自定义对比函数进行对账")
    def test_custom_comparator(self):
        """示例：自定义对比函数"""

        def custom_compare(onchain_item, offchain_item):
            """
            自定义对比函数
            :return: (是否匹配, 差异列表)
            """
            differences = []

            # 金额对比（允许误差）
            onchain_value = onchain_item.get('value', 0)
            offchain_value = offchain_item.get('value', 0)
            tolerance = 0.01  # 1% 误差

            if abs(onchain_value - offchain_value) > onchain_value * tolerance:
                differences.append({
                    'field': 'value',
                    'onchain_value': onchain_value,
                    'offchain_value': offchain_value,
                    'message': f'金额差异超过 {tolerance * 100}%'
                })

            # 状态对比（映射关系）
            status_mapping = {
                'success': 'completed',
                'pending': 'processing',
                'failed': 'failed'
            }

            onchain_status = onchain_item.get('status')
            offchain_status = offchain_item.get('status')
            expected_offchain_status = status_mapping.get(onchain_status)

            if expected_offchain_status != offchain_status:
                differences.append({
                    'field': 'status',
                    'onchain_value': onchain_status,
                    'offchain_value': offchain_status,
                    'message': '状态不匹配'
                })

            return len(differences) == 0, differences

        # 模拟数据
        onchain_data = [
            {'id': '1', 'value': 1000, 'status': 'success'},
            {'id': '2', 'value': 2000, 'status': 'pending'},
        ]

        offchain_data = [
            {'id': '1', 'value': 1005, 'status': 'completed'},  # 金额在误差范围内，状态映射正确
            {'id': '2', 'value': 2000, 'status': 'processing'},  # 状态映射正确
        ]

        # 执行对账
        engine = ReconciliationEngine()
        result = engine.reconcile(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            key_field='id',
            custom_comparator=custom_compare
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.print_summary(result)

        # 断言
        assert result.is_success(), "对账应该成功"


@allure.feature("对账功能")
@allure.story("异步数据对账")
class TestAsyncReconciliation:
    """异步数据对账示例"""

    @allure.title("示例：带重试的对账")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("处理链上异步数据，带重试机制")
    def test_reconciliation_with_retry(self):
        """示例：带重试的对账"""
        factory = TestDataFactory()

        # 模拟数据获取函数
        attempt_count = {'count': 0}

        def fetch_onchain_data():
            """模拟链上数据获取（第一次不完整，第二次完整）"""
            attempt_count['count'] += 1

            if attempt_count['count'] == 1:
                # 第一次：数据不完整
                return [
                    {'tx_hash': '0x123', 'value': 1000},
                ]
            else:
                # 第二次：数据完整
                return [
                    {'tx_hash': '0x123', 'value': 1000},
                    {'tx_hash': '0x456', 'value': 2000},
                ]

        def fetch_offchain_data():
            """模拟链下数据获取"""
            return [
                {'tx_hash': '0x123', 'value': 1000},
                {'tx_hash': '0x456', 'value': 2000},
            ]

        # 执行带重试的对账
        engine = ReconciliationEngine()
        result = engine.reconcile_with_retry(
            onchain_fetcher=fetch_onchain_data,
            offchain_fetcher=fetch_offchain_data,
            key_field='tx_hash',
            max_retries=3,
            retry_interval=1
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.print_summary(result)

        # 断言
        assert result.is_success(), "对账应该成功"
        assert attempt_count['count'] == 2, "应该重试了1次"


@allure.feature("对账功能")
@allure.story("T+0/T+1 对账")
class TestTimeBasedReconciliation:
    """时间范围对账示例"""

    @allure.title("示例：T+0 对账")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.description("对当日数据进行对账")
    def test_t0_reconciliation(self):
        """示例：T+0 对账"""
        import time

        current_timestamp = int(time.time())

        # 模拟当日数据
        onchain_data = [
            {'tx_hash': '0x123', 'value': 1000, 'timestamp': current_timestamp - 3600},
            {'tx_hash': '0x456', 'value': 2000, 'timestamp': current_timestamp - 7200},
        ]

        offchain_data = [
            {'tx_hash': '0x123', 'value': 1000, 'timestamp': current_timestamp - 3600},
            {'tx_hash': '0x456', 'value': 2000, 'timestamp': current_timestamp - 7200},
        ]

        # 执行 T+0 对账
        engine = ReconciliationEngine(mode=ReconciliationMode.T0)
        result = engine.reconcile_by_time_range(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            time_field='timestamp',
            key_field='tx_hash'
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.print_summary(result)

        # 断言
        assert result.is_success(), "T+0 对账应该成功"

    @allure.title("示例：T+1 对账")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("对前一日数据进行对账")
    def test_t1_reconciliation(self):
        """示例：T+1 对账"""
        import time
        from datetime import datetime, timedelta

        # 模拟前一日数据
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_timestamp = int(yesterday.timestamp())

        onchain_data = [
            {'tx_hash': '0x123', 'value': 1000, 'timestamp': yesterday_timestamp},
        ]

        offchain_data = [
            {'tx_hash': '0x123', 'value': 1000, 'timestamp': yesterday_timestamp},
        ]

        # 执行 T+1 对账
        engine = ReconciliationEngine(mode=ReconciliationMode.T1)
        result = engine.reconcile_by_time_range(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            time_field='timestamp',
            key_field='tx_hash'
        )

        # 生成报告
        ReconciliationReporter.attach_summary_to_allure(result)

        # 断言
        assert result.is_success(), "T+1 对账应该成功"


@allure.feature("对账功能")
@allure.story("报告生成")
class TestReportGeneration:
    """报告生成示例"""

    @allure.title("示例：生成并保存对账报告")
    @allure.severity(allure.severity_level.NORMAL)
    @allure.description("生成对账报告并保存到文件")
    def test_generate_report(self, tmp_path):
        """示例：生成并保存对账报告"""
        # 模拟对账数据
        onchain_data = [
            {'id': '1', 'value': 1000},
            {'id': '2', 'value': 2000},
        ]

        offchain_data = [
            {'id': '1', 'value': 1000},
            {'id': '2', 'value': 2500},  # 差异
        ]

        # 执行对账
        engine = ReconciliationEngine()
        result = engine.reconcile(
            onchain_data=onchain_data,
            offchain_data=offchain_data,
            key_field='id',
            compare_fields=['value']
        )

        # 保存 JSON 报告
        json_file = tmp_path / "reconciliation_report.json"
        ReconciliationReporter.save_to_file(result, str(json_file), format='json')
        assert json_file.exists(), "JSON 报告应该已生成"

        # 保存文本报告
        text_file = tmp_path / "reconciliation_report.txt"
        ReconciliationReporter.save_to_file(result, str(text_file), format='text')
        assert text_file.exists(), "文本报告应该已生成"

        # 附加到 Allure
        ReconciliationReporter.attach_summary_to_allure(result)
        ReconciliationReporter.attach_details_to_allure(result)
