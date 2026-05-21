#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : blockchain_rpc.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
from framework.utils.rpc_client import RPCClient
from framework.core.config import config


class BlockchainRPC:
    """区块链 RPC 单接口定义"""

    def __init__(self, client: RPCClient = None):
        self.client = client or RPCClient(rpc_url=config.rpc_url)

    def get_block_number(self):
        """单接口：获取最新区块号"""
        return self.client.call("eth_blockNumber")

    def get_block_by_number(self, block_number: str, full_tx: bool = False):
        """单接口：根据区块号获取区块"""
        return self.client.call("eth_getBlockByNumber", [block_number, full_tx])

    def get_balance(self, address: str, block: str = "latest"):
        """单接口：获取地址余额"""
        return self.client.call("eth_getBalance", [address, block])

    def get_transaction_count(self, address: str, block: str = "latest"):
        """单接口：获取地址交易数"""
        return self.client.call("eth_getTransactionCount", [address, block])

    def get_transaction_by_hash(self, tx_hash: str):
        """单接口：根据哈希获取交易"""
        return self.client.call("eth_getTransactionByHash", [tx_hash])

    def get_transaction_receipt(self, tx_hash: str):
        """单接口：获取交易回执"""
        return self.client.call("eth_getTransactionReceipt", [tx_hash])

    def send_raw_transaction(self, signed_tx: str):
        """单接口：发送原始交易"""
        return self.client.call("eth_sendRawTransaction", [signed_tx])

    def call(self, tx_object: dict, block: str = "latest"):
        """单接口：执行调用（不创建交易）"""
        return self.client.call("eth_call", [tx_object, block])

    def estimate_gas(self, tx_object: dict):
        """单接口：估算gas"""
        return self.client.call("eth_estimateGas", [tx_object])

    def get_gas_price(self):
        """单接口：获取gas价格"""
        return self.client.call("eth_gasPrice")
