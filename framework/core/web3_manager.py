#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : web3_manager.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""

from web3 import Web3
try:
    # web3.py v6.x
    from web3.middleware import geth_poa_middleware
except ImportError:
    # web3.py v7.x
    from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
from eth_account import Account
from framework.core.config import config


class Web3Manager:
    """Web3 连接管理器"""

    _instance = None
    _w3 = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _init_web3(self):
        """初始化 Web3 连接"""
        if self._initialized:
            return

        rpc_url = config.rpc_url
        self._w3 = Web3(Web3.HTTPProvider(rpc_url))

        # 添加 POA 中间件（适用于某些测试网）
        self._w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self._w3.is_connected():
            raise ConnectionError(f"无法连接到 RPC: {rpc_url}")

        self._initialized = True

    @property
    def w3(self) -> Web3:
        """获取 Web3 实例"""
        if not self._initialized:
            self._init_web3()
        return self._w3

    def get_account(self, name: str):
        """获取账户对象"""
        account_config = config.get_account(name)
        if not account_config:
            raise ValueError(f"账户 {name} 未配置")

        private_key = account_config.get('private_key')
        if not private_key:
            raise ValueError(f"账户 {name} 缺少私钥")

        return Account.from_key(private_key)

    def load_contract(self, name: str):
        """加载合约实例"""
        contract_config = config.get_contract(name)
        if not contract_config:
            raise ValueError(f"合约 {name} 未配置")

        address = contract_config.get('address')
        abi_path = contract_config.get('abi_path')

        if not address or not abi_path:
            raise ValueError(f"合约 {name} 配置不完整")

        # 加载 ABI
        import json
        from pathlib import Path

        abi_file = Path(__file__).parent.parent.parent / abi_path
        with open(abi_file, 'r') as f:
            abi_data = json.load(f)
            abi = abi_data.get('abi', abi_data)

        return self._w3.eth.contract(address=Web3.to_checksum_address(address), abi=abi)


# 全局 Web3 管理器实例
web3_manager = Web3Manager()
