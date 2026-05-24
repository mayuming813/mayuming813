#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : staking_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : Staking 合约 API 封装
"""

from typing import Dict, Tuple
from eth_account import Account
from framework.web3 import Web3Client
from framework.core.logger import logger


class StakingAPI:
    """Staking 合约 API 封装"""

    def __init__(self, web3_client: Web3Client, contract_address: str, abi: list):
        """
        初始化 Staking API

        Args:
            web3_client: Web3 客户端
            contract_address: 合约地址
            abi: 合约 ABI
        """
        self.client = web3_client
        self.contract = web3_client.load_contract(contract_address, abi)
        self.address = contract_address
        logger.info(f"Staking API 已初始化: {contract_address}")

    def staking_token(self) -> str:
        """获取质押代币地址"""
        return self.client.call_contract_function(self.contract, "stakingToken")

    def reward_token(self) -> str:
        """获取奖励代币地址"""
        return self.client.call_contract_function(self.contract, "rewardToken")

    def reward_rate(self) -> int:
        """获取奖励速率（每秒）"""
        return self.client.call_contract_function(self.contract, "rewardRate")

    def total_staked(self) -> int:
        """获取总质押量"""
        return self.client.call_contract_function(self.contract, "totalStaked")

    def lock_duration(self) -> int:
        """获取锁定时间（秒）"""
        return self.client.call_contract_function(self.contract, "lockDuration")

    def staked_balance(self, address: str) -> int:
        """
        获取质押余额

        Args:
            address: 地址

        Returns:
            质押余额
        """
        return self.client.call_contract_function(self.contract, "stakedBalance", address)

    def earned(self, address: str) -> int:
        """
        获取已赚取的奖励

        Args:
            address: 地址

        Returns:
            奖励数量
        """
        return self.client.call_contract_function(self.contract, "earned", address)

    def get_staking_info(self, address: str) -> Dict:
        """
        获取质押信息

        Args:
            address: 地址

        Returns:
            质押信息
        """
        info = self.client.call_contract_function(self.contract, "getStakingInfo", address)
        return {
            'staked': info[0],
            'earned_rewards': info[1],
            'lock_time_remaining': info[2]
        }

    def stake(self, amount: int, from_account: Account) -> str:
        """
        质押代币

        Args:
            amount: 质押数量
            from_account: 质押账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "stake",
            from_account,
            amount
        )

    def withdraw(self, amount: int, from_account: Account) -> str:
        """
        解押代币

        Args:
            amount: 解押数量
            from_account: 质押账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "withdraw",
            from_account,
            amount
        )

    def get_reward(self, from_account: Account) -> str:
        """
        领取奖励

        Args:
            from_account: 质押账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "getReward",
            from_account
        )

    def exit(self, from_account: Account) -> str:
        """
        退出（解押 + 领取奖励）

        Args:
            from_account: 质押账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "exit",
            from_account
        )

    def set_reward_rate(self, rate: int, from_account: Account) -> str:
        """
        设置奖励速率（Owner）

        Args:
            rate: 奖励速率
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "setRewardRate",
            from_account,
            rate
        )

    def set_lock_duration(self, duration: int, from_account: Account) -> str:
        """
        设置锁定时间（Owner）

        Args:
            duration: 锁定时间（秒）
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "setLockDuration",
            from_account,
            duration
        )

    def deposit_reward_tokens(self, amount: int, from_account: Account) -> str:
        """
        存入奖励代币（Owner）

        Args:
            amount: 数量
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "depositRewardTokens",
            from_account,
            amount
        )

    def owner(self) -> str:
        """获取合约所有者"""
        return self.client.call_contract_function(self.contract, "owner")
