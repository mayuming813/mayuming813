#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : contract_rpc.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.utils.rpc_client import RPCClient
from framework.core.config import config


class ContractRPC:
    """合约 RPC 单接口定义"""

    def __init__(self, client: RPCClient = None):
        self.client = client or RPCClient(rpc_url=config.rpc_url)

    def get_code(self, address: str, block: str = "latest"):
        """单接口：获取合约代码"""
        return self.client.call("eth_getCode", [address, block])

    def get_storage_at(self, address: str, position: str, block: str = "latest"):
        """单接口：获取存储位置的值"""
        return self.client.call("eth_getStorageAt", [address, position, block])

    def call_contract(self, to: str, data: str, block: str = "latest"):
        """单接口：调用合约方法"""
        tx_object = {"to": to, "data": data}
        return self.client.call("eth_call", [tx_object, block])
