#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : ethers_client.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Ethers.js 风格的 Python 封装（基于 Web3.py）
"""

from web3 import Web3
from web3.contract import Contract
from eth_account import Account
from typing import Optional, Dict, Any, List
from framework.core.logger import logger


class EthersClient:
    """Ethers.js 风格的调用封装"""

    def __init__(self, provider_url: str):
        """
        初始化 Ethers 客户端

        Args:
            provider_url: Provider URL
        """
        self.provider = Web3(Web3.HTTPProvider(provider_url))

        # 添加 POA 中间件
        try:
            from web3.middleware import geth_poa_middleware
        except ImportError:
            from web3.middleware import ExtraDataToPOAMiddleware as geth_poa_middleware
        self.provider.middleware_onion.inject(geth_poa_middleware, layer=0)

        if not self.provider.is_connected():
            raise ConnectionError(f"无法连接到 Provider: {provider_url}")

        logger.info(f"Ethers 客户端已连接: {provider_url}")

    def get_signer(self, private_key: str) -> Account:
        """
        获取签名者（类似 ethers.Wallet）

        Args:
            private_key: 私钥

        Returns:
            Account 对象
        """
        return Account.from_key(private_key)

    def get_contract(self, address: str, abi: List[Dict], signer: Optional[Account] = None) -> Contract:
        """
        获取合约实例（类似 ethers.Contract）

        Args:
            address: 合约地址
            abi: 合约 ABI
            signer: 签名者（可选）

        Returns:
            合约实例
        """
        contract = self.provider.eth.contract(
            address=Web3.to_checksum_address(address),
            abi=abi
        )

        # 如果提供了 signer，附加到合约实例
        if signer:
            contract.signer = signer

        return contract

    async def call(self, contract: Contract, method: str, *args) -> Any:
        """
        调用合约只读方法（类似 contract.method()）

        Args:
            contract: 合约实例
            method: 方法名
            *args: 方法参数

        Returns:
            方法返回值
        """
        func = getattr(contract.functions, method)
        return func(*args).call()

    async def send_transaction(
        self,
        contract: Contract,
        method: str,
        *args,
        value: int = 0,
        gas_limit: Optional[int] = None,
        gas_price: Optional[int] = None
    ) -> Dict:
        """
        发送合约交易（类似 contract.method().send()）

        Args:
            contract: 合约实例
            method: 方法名
            *args: 方法参数
            value: 转账金额（Wei）
            gas_limit: Gas 限制
            gas_price: Gas 价格

        Returns:
            交易回执
        """
        if not hasattr(contract, 'signer'):
            raise ValueError("合约实例未绑定 signer")

        signer = contract.signer
        func = getattr(contract.functions, method)

        tx = func(*args).build_transaction({
            'from': signer.address,
            'value': value,
            'nonce': self.provider.eth.get_transaction_count(signer.address),
        })

        if gas_limit:
            tx['gas'] = gas_limit
        else:
            tx['gas'] = self.provider.eth.estimate_gas(tx)

        if gas_price:
            tx['gasPrice'] = gas_price
        else:
            tx['gasPrice'] = self.provider.eth.gas_price

        signed_tx = self.provider.eth.account.sign_transaction(tx, signer.key)
        tx_hash = self.provider.eth.send_raw_transaction(signed_tx.raw_transaction)

        logger.info(f"交易已发送: {method}, tx_hash: {tx_hash.hex()}")

        # 等待交易确认
        receipt = self.provider.eth.wait_for_transaction_receipt(tx_hash)
        return dict(receipt)

    def parse_units(self, value: str, decimals: int = 18) -> int:
        """
        解析单位（类似 ethers.parseUnits）

        Args:
            value: 数值字符串
            decimals: 小数位数

        Returns:
            Wei 值
        """
        return int(float(value) * (10 ** decimals))

    def format_units(self, value: int, decimals: int = 18) -> str:
        """
        格式化单位（类似 ethers.formatUnits）

        Args:
            value: Wei 值
            decimals: 小数位数

        Returns:
            格式化后的字符串
        """
        return str(value / (10 ** decimals))

    def parse_ether(self, ether: str) -> int:
        """
        解析 Ether（类似 ethers.parseEther）

        Args:
            ether: Ether 数量

        Returns:
            Wei 值
        """
        return self.provider.to_wei(float(ether), 'ether')

    def format_ether(self, wei: int) -> str:
        """
        格式化 Ether（类似 ethers.formatEther）

        Args:
            wei: Wei 值

        Returns:
            Ether 字符串
        """
        return str(self.provider.from_wei(wei, 'ether'))

    def get_balance(self, address: str) -> int:
        """
        获取余额（类似 provider.getBalance）

        Args:
            address: 地址

        Returns:
            余额（Wei）
        """
        return self.provider.eth.get_balance(Web3.to_checksum_address(address))

    def get_transaction(self, tx_hash: str) -> Dict:
        """
        获取交易（类似 provider.getTransaction）

        Args:
            tx_hash: 交易哈希

        Returns:
            交易信息
        """
        return dict(self.provider.eth.get_transaction(tx_hash))

    def get_transaction_receipt(self, tx_hash: str) -> Optional[Dict]:
        """
        获取交易回执（类似 provider.getTransactionReceipt）

        Args:
            tx_hash: 交易哈希

        Returns:
            交易回执
        """
        receipt = self.provider.eth.get_transaction_receipt(tx_hash)
        return dict(receipt) if receipt else None

    def wait_for_transaction(self, tx_hash: str, timeout: int = 120) -> Dict:
        """
        等待交易确认（类似 provider.waitForTransaction）

        Args:
            tx_hash: 交易哈希
            timeout: 超时时间

        Returns:
            交易回执
        """
        receipt = self.provider.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        return dict(receipt)

    def get_block_number(self) -> int:
        """
        获取最新区块号（类似 provider.getBlockNumber）

        Returns:
            区块号
        """
        return self.provider.eth.block_number

    def get_block(self, block_number: int | str) -> Dict:
        """
        获取区块（类似 provider.getBlock）

        Args:
            block_number: 区块号或标识符

        Returns:
            区块信息
        """
        return dict(self.provider.eth.get_block(block_number))

    def get_gas_price(self) -> int:
        """
        获取 Gas 价格（类似 provider.getGasPrice）

        Returns:
            Gas 价格（Wei）
        """
        return self.provider.eth.gas_price

    def estimate_gas(self, transaction: Dict) -> int:
        """
        估算 Gas（类似 provider.estimateGas）

        Args:
            transaction: 交易对象

        Returns:
            Gas 估算值
        """
        return self.provider.eth.estimate_gas(transaction)
