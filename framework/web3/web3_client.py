#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : web3_client.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Web3.py 直接调用封装
"""

from web3 import Web3
from web3.contract import Contract
from eth_account import Account
from typing import Optional, Dict, Any, List
from framework.core.logger import logger


class Web3Client:
    """Web3.py 直接调用封装"""

    def __init__(self, rpc_url: str):
        """
        初始化 Web3 客户端

        Args:
            rpc_url: RPC 节点地址
        """
        self.w3 = Web3(Web3.HTTPProvider(rpc_url))

        # 添加 POA 中间件
        try:
            from web3.middleware import geth_poa_middleware
        except ImportError:
            from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.w3.is_connected():
            raise ConnectionError(f"无法连接到 RPC: {rpc_url}")

        logger.info(f"Web3 客户端已连接: {rpc_url}")

    def get_block_number(self) -> int:
        """获取最新区块号"""
        return self.w3.eth.block_number

    def get_block(self, block_identifier: int | str, full_transactions: bool = False) -> Dict:
        """获取区块信息"""
        return dict(self.w3.eth.get_block(block_identifier, full_transactions))

    def get_transaction(self, tx_hash: str) -> Dict:
        """获取交易信息"""
        return dict(self.w3.eth.get_transaction(tx_hash))

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict]:
        """获取交易回执"""
        receipt = self.w3.eth.get_transaction_receipt(tx_hash)
        return dict(receipt) if receipt else None

    def get_balance(self, address: str) -> int:
        """获取账户余额（Wei）"""
        return self.w3.eth.get_balance(Web3.to_checksum_address(address))

    def get_balance_ether(self, address: str) -> float:
        """获取账户余额（Ether）"""
        balance_wei = self.get_balance(address)
        return float(self.w3.from_wei(balance_wei, 'ether'))

    def send_transaction(
        self,
        from_account: Account,
        to_address: str,
        value: int = 0,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None,
        data: str = "0x"
    ) -> str:
        """
        发送交易

        Args:
            from_account: 发送账户
            to_address: 接收地址
            value: 转账金额（Wei）
            gas: Gas 限制
            gas_price: Gas 价格
            data: 交易数据

        Returns:
            交易哈希
        """
        tx = {
            'from': from_account.address,
            'to': Web3.to_checksum_address(to_address),
            'value': value,
            'nonce': self.w3.eth.get_transaction_count(from_account.address),
            'data': data,
        }

        if gas:
            tx['gas'] = gas
        else:
            tx['gas'] = self.w3.eth.estimate_gas(tx)

        # Use maxFeePerGas and maxPriorityFeePerGas for EIP-1559 transactions
        if gas_price:
            tx['gasPrice'] = gas_price
        elif hasattr(self.w3.eth, 'max_priority_fee'):
            # EIP-1559 transaction
            tx['maxFeePerGas'] = self.w3.eth.gas_price
            tx['maxPriorityFeePerGas'] = self.w3.eth.max_priority_fee
        else:
            # Legacy transaction
            tx['gasPrice'] = self.w3.eth.gas_price

        signed_tx = self.w3.eth.account.sign_transaction(tx, from_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        logger.info(f"交易已发送: {tx_hash.hex()}")
        return tx_hash.hex()

    def wait_for_transaction_receipt(
        self,
        tx_hash: str,
        timeout: int = 120,
        poll_latency: float = 0.1
    ) -> Dict:
        """等待交易确认"""
        receipt = self.w3.eth.wait_for_transaction_receipt(
            tx_hash,
            timeout=timeout,
            poll_latency=poll_latency
        )
        return dict(receipt)

    def load_contract(self, address: str, abi: List[Dict]) -> Contract:
        """
        加载合约实例

        Args:
            address: 合约地址
            abi: 合约 ABI

        Returns:
            合约实例
        """
        return self.w3.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )

    def call_contract_function(
        self,
        contract: Contract,
        function_name: str,
        *args,
        **kwargs
    ) -> Any:
        """
        调用合约只读函数

        Args:
            contract: 合约实例
            function_name: 函数名
            *args: 函数参数
            **kwargs: 额外参数

        Returns:
            函数返回值
        """
        func = getattr(contract.functions, function_name)
        return func(*args).call(**kwargs)

    def send_contract_transaction(
        self,
        contract: Contract,
        function_name: str,
        from_account: Account,
        *args,
        value: int = 0,
        gas: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> str:
        """
        发送合约交易

        Args:
            contract: 合约实例
            function_name: 函数名
            from_account: 发送账户
            *args: 函数参数
            value: 转账金额（Wei）
            gas: Gas 限制
            gas_price: Gas 价格

        Returns:
            交易哈希
        """
        func = getattr(contract.functions, function_name)

        tx = func(*args).build_transaction({
            'from': from_account.address,
            'value': value,
            'nonce': self.w3.eth.get_transaction_count(from_account.address),
        })

        if gas:
            tx['gas'] = gas
        else:
            tx['gas'] = self.w3.eth.estimate_gas(tx)

        # Use maxFeePerGas and maxPriorityFeePerGas for EIP-1559 transactions
        if gas_price:
            tx['gasPrice'] = gas_price
        elif hasattr(self.w3.eth, 'max_priority_fee'):
            # EIP-1559 transaction
            tx['maxFeePerGas'] = self.w3.eth.gas_price
            tx['maxPriorityFeePerGas'] = self.w3.eth.max_priority_fee
        else:
            # Legacy transaction
            tx['gasPrice'] = self.w3.eth.gas_price

        signed_tx = self.w3.eth.account.sign_transaction(tx, from_account.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        logger.info(f"合约交易已发送: {function_name}, tx_hash: {tx_hash.hex()}")
        return tx_hash.hex()

    def estimate_gas(self, transaction: Dict) -> int:
        """估算 Gas"""
        return self.w3.eth.estimate_gas(transaction)

    def get_gas_price(self) -> int:
        """获取当前 Gas 价格"""
        return self.w3.eth.gas_price

    def to_wei(self, amount: float, unit: str = 'ether') -> int:
        """转换为 Wei"""
        return self.w3.to_wei(amount, unit)

    def from_wei(self, amount: int, unit: str = 'ether') -> float:
        """从 Wei 转换"""
        return float(self.w3.from_wei(amount, unit))

    def to_checksum_address(self, address: str) -> str:
        """转换为校验和地址"""
        return Web3.to_checksum_address(address)

    def is_address(self, address: str) -> bool:
        """验证地址格式"""
        return Web3.is_address(address)

    def keccak(self, data: bytes) -> bytes:
        """计算 Keccak256 哈希"""
        return self.w3.keccak(data)