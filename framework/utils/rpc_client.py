#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : rpc_client.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import requests
from typing import Any, Optional


class RPCClient:
    """JSON-RPC 客户端"""

    def __init__(self, rpc_url: str):
        """
        初始化
        :param rpc_url: RPC 节点地址
        """
        self.rpc_url = rpc_url
        self.session = requests.Session()
        self.request_id = 0

    def call(self, method: str, params: list = None) -> requests.Response:
        """
        调用 JSON-RPC 方法
        :param method: RPC 方法名
        :param params: 参数列表
        :return: Response 对象
        """
        self.request_id += 1
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or [],
            "id": self.request_id
        }
        return self.session.post(self.rpc_url, json=payload, timeout=30)

    def close(self):
        """关闭会话"""
        self.session.close()
