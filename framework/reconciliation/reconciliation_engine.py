#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : reconciliation_engine.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timedelta
from enum import Enum
import time


class ReconciliationMode(Enum):
    """对账模式"""
    REALTIME = "realtime"  # 实时对账
    T0 = "t0"  # T+0 对账（当日）
    T1 = "t1"  # T+1 对账（次日）


class ReconciliationStatus(Enum):
    """对账状态"""
    MATCHED = "matched"  # 匹配
    MISMATCHED = "mismatched"  # 不匹配
    MISSING_ONCHAIN = "missing_onchain"  # 链上缺失
    MISSING_OFFCHAIN = "missing_offchain"  # 链下缺失
    PENDING = "pending"  # 待确认


class ReconciliationResult:
    """对账结果"""

    def __init__(self):
        self.total_count = 0
        self.matched_count = 0
        self.mismatched_count = 0
        self.missing_onchain_count = 0
        self.missing_offchain_count = 0
        self.pending_count = 0
        self.details: List[Dict[str, Any]] = []
        self.start_time = None
        self.end_time = None

    def add_detail(self, detail: Dict[str, Any]):
        """添加对账明细"""
        self.details.append(detail)
        self.total_count += 1

        status = detail.get('status')
        if status == ReconciliationStatus.MATCHED:
            self.matched_count += 1
        elif status == ReconciliationStatus.MISMATCHED:
            self.mismatched_count += 1
        elif status == ReconciliationStatus.MISSING_ONCHAIN:
            self.missing_onchain_count += 1
        elif status == ReconciliationStatus.MISSING_OFFCHAIN:
            self.missing_offchain_count += 1
        elif status == ReconciliationStatus.PENDING:
            self.pending_count += 1

    def get_summary(self) -> Dict[str, Any]:
        """获取对账汇总"""
        duration = (self.end_time - self.start_time).total_seconds() if self.start_time and self.end_time else 0
        return {
            'total_count': self.total_count,
            'matched_count': self.matched_count,
            'mismatched_count': self.mismatched_count,
            'missing_onchain_count': self.missing_onchain_count,
            'missing_offchain_count': self.missing_offchain_count,
            'pending_count': self.pending_count,
            'match_rate': f"{(self.matched_count / self.total_count * 100):.2f}%" if self.total_count > 0 else "0%",
            'duration_seconds': duration,
            'start_time': self.start_time.strftime('%Y-%m-%d %H:%M:%S') if self.start_time else None,
            'end_time': self.end_time.strftime('%Y-%m-%d %H:%M:%S') if self.end_time else None
        }

    def is_success(self) -> bool:
        """判断对账是否成功（全部匹配）"""
        return self.total_count > 0 and self.matched_count == self.total_count


class ReconciliationEngine:
    """对账引擎"""

    def __init__(self, mode: ReconciliationMode = ReconciliationMode.REALTIME):
        """
        初始化
        :param mode: 对账模式
        """
        self.mode = mode
        self.result = ReconciliationResult()

    def reconcile(
        self,
        onchain_data: List[Dict[str, Any]],
        offchain_data: List[Dict[str, Any]],
        key_field: str = 'id',
        compare_fields: List[str] = None,
        custom_comparator: Callable = None
    ) -> ReconciliationResult:
        """
        执行对账
        :param onchain_data: 链上数据列表
        :param offchain_data: 链下数据列表
        :param key_field: 关联字段（用于匹配）
        :param compare_fields: 需要对比的字段列表
        :param custom_comparator: 自定义对比函数
        :return: 对账结果
        """
        self.result = ReconciliationResult()
        self.result.start_time = datetime.now()

        # 构建索引
        onchain_map = {item.get(key_field): item for item in onchain_data}
        offchain_map = {item.get(key_field): item for item in offchain_data}

        # 获取所有键
        all_keys = set(onchain_map.keys()) | set(offchain_map.keys())

        # 逐条对账
        for key in all_keys:
            onchain_item = onchain_map.get(key)
            offchain_item = offchain_map.get(key)

            detail = self._compare_item(
                key,
                onchain_item,
                offchain_item,
                compare_fields,
                custom_comparator
            )
            self.result.add_detail(detail)

        self.result.end_time = datetime.now()
        return self.result

    def _compare_item(
        self,
        key: Any,
        onchain_item: Optional[Dict[str, Any]],
        offchain_item: Optional[Dict[str, Any]],
        compare_fields: List[str] = None,
        custom_comparator: Callable = None
    ) -> Dict[str, Any]:
        """
        对比单条数据
        :param key: 关联键
        :param onchain_item: 链上数据
        :param offchain_item: 链下数据
        :param compare_fields: 对比字段
        :param custom_comparator: 自定义对比函数
        :return: 对账明细
        """
        detail = {
            'key': key,
            'onchain_data': onchain_item,
            'offchain_data': offchain_item,
            'differences': [],
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        # 缺失检查
        if onchain_item is None:
            detail['status'] = ReconciliationStatus.MISSING_ONCHAIN
            detail['message'] = '链上数据缺失'
            return detail

        if offchain_item is None:
            detail['status'] = ReconciliationStatus.MISSING_OFFCHAIN
            detail['message'] = '链下数据缺失'
            return detail

        # 使用自定义对比函数
        if custom_comparator:
            is_match, differences = custom_comparator(onchain_item, offchain_item)
            detail['differences'] = differences
            detail['status'] = ReconciliationStatus.MATCHED if is_match else ReconciliationStatus.MISMATCHED
            detail['message'] = '匹配' if is_match else '不匹配'
            return detail

        # 默认字段对比
        if compare_fields:
            differences = []
            for field in compare_fields:
                onchain_value = onchain_item.get(field)
                offchain_value = offchain_item.get(field)

                if onchain_value != offchain_value:
                    differences.append({
                        'field': field,
                        'onchain_value': onchain_value,
                        'offchain_value': offchain_value
                    })

            detail['differences'] = differences
            detail['status'] = ReconciliationStatus.MATCHED if len(differences) == 0 else ReconciliationStatus.MISMATCHED
            detail['message'] = '匹配' if len(differences) == 0 else f'不匹配（{len(differences)}个字段）'
        else:
            # 全字段对比
            detail['status'] = ReconciliationStatus.MATCHED if onchain_item == offchain_item else ReconciliationStatus.MISMATCHED
            detail['message'] = '匹配' if onchain_item == offchain_item else '不匹配'

        return detail

    def reconcile_with_retry(
        self,
        onchain_fetcher: Callable,
        offchain_fetcher: Callable,
        key_field: str = 'id',
        compare_fields: List[str] = None,
        max_retries: int = 3,
        retry_interval: int = 5,
        custom_comparator: Callable = None
    ) -> ReconciliationResult:
        """
        带重试的对账（处理链上异步数据）
        :param onchain_fetcher: 链上数据获取函数
        :param offchain_fetcher: 链下数据获取函数
        :param key_field: 关联字段
        :param compare_fields: 对比字段
        :param max_retries: 最大重试次数
        :param retry_interval: 重试间隔（秒）
        :param custom_comparator: 自定义对比函数
        :return: 对账结果
        """
        for attempt in range(max_retries + 1):
            # 获取数据
            onchain_data = onchain_fetcher()
            offchain_data = offchain_fetcher()

            # 执行对账
            result = self.reconcile(
                onchain_data,
                offchain_data,
                key_field,
                compare_fields,
                custom_comparator
            )

            # 如果全部匹配或无待确认项，返回结果
            if result.is_success() or result.pending_count == 0:
                return result

            # 如果还有重试机会，等待后重试
            if attempt < max_retries:
                time.sleep(retry_interval)

        return result

    def reconcile_by_time_range(
        self,
        onchain_data: List[Dict[str, Any]],
        offchain_data: List[Dict[str, Any]],
        time_field: str = 'timestamp',
        start_time: datetime = None,
        end_time: datetime = None,
        **kwargs
    ) -> ReconciliationResult:
        """
        按时间范围对账
        :param onchain_data: 链上数据
        :param offchain_data: 链下数据
        :param time_field: 时间字段
        :param start_time: 开始时间
        :param end_time: 结束时间
        :param kwargs: 其他对账参数
        :return: 对账结果
        """
        # 根据对账模式设置时间范围
        if self.mode == ReconciliationMode.T0:
            # T+0：当日数据
            start_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = datetime.now()
        elif self.mode == ReconciliationMode.T1:
            # T+1：前一日数据
            yesterday = datetime.now() - timedelta(days=1)
            start_time = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            end_time = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)

        # 过滤时间范围内的数据
        if start_time and end_time:
            onchain_filtered = [
                item for item in onchain_data
                if start_time <= self._parse_time(item.get(time_field)) <= end_time
            ]
            offchain_filtered = [
                item for item in offchain_data
                if start_time <= self._parse_time(item.get(time_field)) <= end_time
            ]
        else:
            onchain_filtered = onchain_data
            offchain_filtered = offchain_data

        return self.reconcile(onchain_filtered, offchain_filtered, **kwargs)

    @staticmethod
    def _parse_time(time_value: Any) -> datetime:
        """
        解析时间值
        :param time_value: 时间值（可能是时间戳、字符串等）
        :return: datetime 对象
        """
        if isinstance(time_value, datetime):
            return time_value
        elif isinstance(time_value, (int, float)):
            # 时间戳（秒或毫秒）
            if time_value > 10**10:  # 毫秒
                return datetime.fromtimestamp(time_value / 1000)
            else:  # 秒
                return datetime.fromtimestamp(time_value)
        elif isinstance(time_value, str):
            # 字符串格式
            try:
                return datetime.fromisoformat(time_value)
            except:
                return datetime.strptime(time_value, '%Y-%m-%d %H:%M:%S')
        else:
            return datetime.now()
