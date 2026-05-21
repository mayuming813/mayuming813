#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : api_validator.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import requests
from typing import Any, List, Dict


class APIValidator:
    """API 响应验证原子能力"""

    @staticmethod
    def validate_status_code(response: requests.Response, expected: int) -> bool:
        """验证状态码（原子能力）"""
        return response.status_code == expected

    @staticmethod
    def validate_status_code_in(response: requests.Response, expected_list: List[int]) -> bool:
        """验证状态码在列表中（原子能力）"""
        return response.status_code in expected_list

    @staticmethod
    def validate_json_field(response: requests.Response, field: str, expected_value: Any = None) -> bool:
        """
        验证 JSON 响应字段（原子能力）
        :param response: 响应对象
        :param field: 字段路径，支持嵌套 "data.user.name"
        :param expected_value: 期望值，None 表示只验证字段存在
        :return: 验证结果
        """
        try:
            data = response.json()
            fields = field.split('.')

            # 逐层获取字段
            for f in fields:
                if isinstance(data, dict):
                    data = data.get(f)
                else:
                    return False

            # 如果只验证存在
            if expected_value is None:
                return data is not None

            # 验证值
            return data == expected_value
        except:
            return False

    @staticmethod
    def validate_json_schema(response: requests.Response, required_fields: List[str]) -> bool:
        """
        验证 JSON 响应包含必需字段（原子能力）
        :param response: 响应对象
        :param required_fields: 必需字段列表
        :return: 验证结果
        """
        try:
            data = response.json()
            for field in required_fields:
                if field not in data:
                    return False
            return True
        except:
            return False

    @staticmethod
    def extract_json_field(response: requests.Response, field: str) -> Any:
        """
        提取 JSON 响应字段（原子能力）
        :param response: 响应对象
        :param field: 字段路径，支持嵌套 "data.user.name"
        :return: 字段值
        """
        try:
            data = response.json()
            fields = field.split('.')

            for f in fields:
                if isinstance(data, dict):
                    data = data.get(f)
                else:
                    return None

            return data
        except:
            return None

    @staticmethod
    def validate_response_time(response: requests.Response, max_time: float) -> bool:
        """
        验证响应时间（原子能力）
        :param response: 响应对象
        :param max_time: 最大响应时间（秒）
        :return: 验证结果
        """
        return response.elapsed.total_seconds() <= max_time
