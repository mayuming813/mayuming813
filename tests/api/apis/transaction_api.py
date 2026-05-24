#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : transaction_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.utils.http_client import HTTPClient
from framework.core.config import config


class TransactionAPI:
    """交易业务单接口定义"""

    def __init__(self, client: HTTPClient = None):
        """
        初始化
        :param client: HTTP 客户端，如果不传则创建新的
        """
        self.client = client or HTTPClient(base_url=config.backend_api_url)

    def create_transaction(self, from_address: str, to_address: str, amount: str, **kwargs):
        """
        单接口：创建交易
        :param from_address: 发送地址
        :param to_address: 接收地址
        :param amount: 金额
        :return: Response 对象
        """
        payload = {
            'from_address': from_address,
            'to_address': to_address,
            'amount': amount,
            **kwargs
        }
        return self.client.post("/api/transaction/create", json=payload)

    def get_transaction(self, tx_hash: str):
        """
        单接口：获取交易详情
        :param tx_hash: 交易哈希
        :return: Response 对象
        """
        return self.client.get(f"/api/transaction/{tx_hash}")

    def get_transaction_list(self, address: str, page: int = 1, size: int = 10):
        """
        单接口：获取交易列表
        :param address: 钱包地址
        :param page: 页码
        :param size: 每页数量
        :return: Response 对象
        """
        params = {'address': address, 'page': page, 'size': size}
        return self.client.get("/api/transaction/list", params=params)

    def get_transaction_status(self, tx_hash: str):
        """
        单接口：查询交易状态
        :param tx_hash: 交易哈希
        :return: Response 对象
        """
        return self.client.get(f"/api/transaction/{tx_hash}/status")

    def cancel_transaction(self, tx_hash: str):
        """
        单接口：取消交易
        :param tx_hash: 交易哈希
        :return: Response 对象
        """
        return self.client.post(f"/api/transaction/{tx_hash}/cancel")
