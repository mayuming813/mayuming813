#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : rpc_validator.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""


class RPCValidator:
    """JSON-RPC 验证器"""

    @staticmethod
    def validate_rpc_response(response, expected_status=200):
        """验证 RPC 响应"""
        return response.status_code == expected_status

    @staticmethod
    def extract_rpc_result(response):
        """提取 RPC 结果"""
        try:
            data = response.json()
            return data.get('result')
        except:
            return None

    @staticmethod
    def extract_rpc_error(response):
        """提取 RPC 错误"""
        try:
            data = response.json()
            return data.get('error')
        except:
            return None

    @staticmethod
    def has_rpc_error(response):
        """检查是否有 RPC 错误"""
        try:
            data = response.json()
            return 'error' in data
        except:
            return True
