#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : contract_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.utils.http_client import HTTPClient
from framework.core.config import config


class ContractAPI:
    """合约业务单接口定义"""

    def __init__(self, client: HTTPClient = None):
        """
        初始化
        :param client: HTTP 客户端，如果不传则创建新的
        """
        self.client = client or HTTPClient(base_url=config.backend_api_url)

    def deploy_contract(self, contract_name: str, constructor_args: list = None, **kwargs):
        """
        单接口：部署合约
        :param contract_name: 合约名称
        :param constructor_args: 构造函数参数
        :return: Response 对象
        """
        payload = {
            'contract_name': contract_name,
            'constructor_args': constructor_args or [],
            **kwargs
        }
        return self.client.post("/api/contract/deploy", json=payload)

    def call_contract(self, contract_address: str, method: str, args: list = None):
        """
        单接口：调用合约方法（只读）
        :param contract_address: 合约地址
        :param method: 方法名
        :param args: 参数列表
        :return: Response 对象
        """
        payload = {
            'contract_address': contract_address,
            'method': method,
            'args': args or []
        }
        return self.client.post("/api/contract/call", json=payload)

    def send_transaction(self, contract_address: str, method: str, args: list = None, **kwargs):
        """
        单接口：发送合约交易（写入）
        :param contract_address: 合约地址
        :param method: 方法名
        :param args: 参数列表
        :return: Response 对象
        """
        payload = {
            'contract_address': contract_address,
            'method': method,
            'args': args or [],
            **kwargs
        }
        return self.client.post("/api/contract/send", json=payload)

    def get_contract_info(self, contract_address: str):
        """
        单接口：获取合约信息
        :param contract_address: 合约地址
        :return: Response 对象
        """
        return self.client.get(f"/api/contract/{contract_address}")

    def verify_contract(self, contract_address: str, source_code: str, **kwargs):
        """
        单接口：验证合约
        :param contract_address: 合约地址
        :param source_code: 源代码
        :return: Response 对象
        """
        payload = {
            'contract_address': contract_address,
            'source_code': source_code,
            **kwargs
        }
        return self.client.post("/api/contract/verify", json=payload)
