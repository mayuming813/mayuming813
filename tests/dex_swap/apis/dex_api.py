#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : dex_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : DEX 合约 API 封装
"""

from typing import Dict, Any, Tuple
from eth_account import Account
from framework.web3 import Web3Client
from framework.core.logger import logger


class DEXAPI:
    """DEX 合约 API 封装"""

    def __init__(self, web3_client: Web3Client, contract_address: str, abi: list):
        """
        初始化 DEX API

        Args:
            web3_client: Web3 客户端
            contract_address: 合约地址
            abi: 合约 ABI
        """
        self.client = web3_client
        self.contract = web3_client.load_contract(contract_address, abi)
        self.address = contract_address
        logger.info(f"DEX API 已初始化: {contract_address}")

    def get_pool_id(self, token_a: str, token_b: str) -> bytes:
        """
        获取流动性池 ID

        Args:
            token_a: Token A 地址
            token_b: Token B 地址

        Returns:
            Pool ID
        """
        return self.client.call_contract_function(self.contract, "getPoolId", token_a, token_b)

    def get_pool(self, pool_id: bytes) -> Dict:
        """
        获取流动性池信息

        Args:
            pool_id: Pool ID

        Returns:
            Pool 信息
        """
        pool = self.client.call_contract_function(self.contract, "pools", pool_id)
        return {
            'tokenA': pool[0],
            'tokenB': pool[1],
            'reserveA': pool[2],
            'reserveB': pool[3],
            'totalLiquidity': pool[4]
        }

    def get_liquidity_balance(self, pool_id: bytes, address: str) -> int:
        """
        获取流动性余额

        Args:
            pool_id: Pool ID
            address: 地址

        Returns:
            流动性余额
        """
        return self.client.call_contract_function(
            self.contract,
            "liquidityBalances",
            pool_id,
            address
        )

    def create_pool(
        self,
        token_a: str,
        token_b: str,
        from_account: Account
    ) -> str:
        """
        创建流动性池

        Args:
            token_a: Token A 地址
            token_b: Token B 地址
            from_account: 创建者账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "createPool",
            from_account,
            token_a,
            token_b
        )

    def add_liquidity(
        self,
        token_a: str,
        token_b: str,
        amount_a: int,
        amount_b: int,
        from_account: Account
    ) -> str:
        """
        添加流动性

        Args:
            token_a: Token A 地址
            token_b: Token B 地址
            amount_a: Token A 数量
            amount_b: Token B 数量
            from_account: 提供者账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "addLiquidity",
            from_account,
            token_a,
            token_b,
            amount_a,
            amount_b
        )

    def remove_liquidity(
        self,
        token_a: str,
        token_b: str,
        liquidity: int,
        from_account: Account
    ) -> str:
        """
        移除流动性

        Args:
            token_a: Token A 地址
            token_b: Token B 地址
            liquidity: 流动性数量
            from_account: 提供者账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "removeLiquidity",
            from_account,
            token_a,
            token_b,
            liquidity
        )

    def swap(
        self,
        token_in: str,
        token_out: str,
        amount_in: int,
        min_amount_out: int,
        from_account: Account
    ) -> str:
        """
        Swap 交易

        Args:
            token_in: 输入 Token 地址
            token_out: 输出 Token 地址
            amount_in: 输入数量
            min_amount_out: 最小输出数量（滑点保护）
            from_account: 交易账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "swap",
            from_account,
            token_in,
            token_out,
            amount_in,
            min_amount_out
        )

    def get_amount_out(
        self,
        token_in: str,
        token_out: str,
        amount_in: int
    ) -> int:
        """
        计算输出数量

        Args:
            token_in: 输入 Token 地址
            token_out: 输出 Token 地址
            amount_in: 输入数量

        Returns:
            预期输出数量
        """
        return self.client.call_contract_function(
            self.contract,
            "getAmountOut",
            token_in,
            token_out,
            amount_in
        )

    def owner(self) -> str:
        """获取合约所有者"""
        return self.client.call_contract_function(self.contract, "owner")


class ERC20API:
    """ERC20 Token API 封装"""

    def __init__(self, web3_client: Web3Client, contract_address: str, abi: list):
        """
        初始化 ERC20 API

        Args:
            web3_client: Web3 客户端
            contract_address: 合约地址
            abi: 合约 ABI
        """
        self.client = web3_client
        self.contract = web3_client.load_contract(contract_address, abi)
        self.address = contract_address

    def name(self) -> str:
        """获取 Token 名称"""
        return self.client.call_contract_function(self.contract, "name")

    def symbol(self) -> str:
        """获取 Token 符号"""
        return self.client.call_contract_function(self.contract, "symbol")

    def decimals(self) -> int:
        """获取 Token 小数位数"""
        return self.client.call_contract_function(self.contract, "decimals")

    def total_supply(self) -> int:
        """获取总供应量"""
        return self.client.call_contract_function(self.contract, "totalSupply")

    def balance_of(self, address: str) -> int:
        """
        获取余额

        Args:
            address: 地址

        Returns:
            余额
        """
        return self.client.call_contract_function(self.contract, "balanceOf", address)

    def allowance(self, owner: str, spender: str) -> int:
        """
        获取授权额度

        Args:
            owner: 所有者地址
            spender: 授权地址

        Returns:
            授权额度
        """
        return self.client.call_contract_function(self.contract, "allowance", owner, spender)

    def transfer(
        self,
        to: str,
        amount: int,
        from_account: Account
    ) -> str:
        """
        转账

        Args:
            to: 接收地址
            amount: 数量
            from_account: 发送账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "transfer",
            from_account,
            to,
            amount
        )

    def approve(
        self,
        spender: str,
        amount: int,
        from_account: Account
    ) -> str:
        """
        授权

        Args:
            spender: 授权地址
            amount: 授权数量
            from_account: 所有者账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "approve",
            from_account,
            spender,
            amount
        )

    def mint(
        self,
        to: str,
        amount: int,
        from_account: Account
    ) -> str:
        """
        Mint Token（仅 Owner）

        Args:
            to: 接收地址
            amount: 数量
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "mint",
            from_account,
            to,
            amount
        )
