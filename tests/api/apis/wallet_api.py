#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : wallet_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.utils.http_client import HTTPClient
from framework.core.config import config


class WalletAPI:
    """钱包业务单接口定义"""

    def __init__(self, client: HTTPClient = None):
        """
        初始化
        :param client: HTTP 客户端，如果不传则创建新的
        """
        self.client = client or HTTPClient(base_url=config.backend_api_url)

    def create_wallet(self, user_id: str, wallet_type: str = "ETH", **kwargs):
        """
        单接口：创建钱包
        :param user_id: 用户 ID
        :param wallet_type: 钱包类型
        :return: Response 对象
        """
        payload = {
            'user_id': user_id,
            'wallet_type': wallet_type,
            **kwargs
        }
        return self.client.post("/api/wallet/create", json=payload)

    def get_wallet_info(self, wallet_id: str):
        """
        单接口：获取钱包信息
        :param wallet_id: 钱包 ID
        :return: Response 对象
        """
        return self.client.get(f"/api/wallet/{wallet_id}")

    def get_balance(self, address: str):
        """
        单接口：查询余额
        :param address: 钱包地址
        :return: Response 对象
        """
        return self.client.get("/api/wallet/balance", params={'address': address})

    def get_wallet_list(self, user_id: str, page: int = 1, size: int = 10):
        """
        单接口：获取用户钱包列表
        :param user_id: 用户 ID
        :param page: 页码
        :param size: 每页数量
        :return: Response 对象
        """
        params = {'user_id': user_id, 'page': page, 'size': size}
        return self.client.get("/api/wallet/list", params=params)

    def delete_wallet(self, wallet_id: str):
        """
        单接口：删除钱包
        :param wallet_id: 钱包 ID
        :return: Response 对象
        """
        return self.client.delete(f"/api/wallet/{wallet_id}")
