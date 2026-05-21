#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : wallet_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 钱包签名和授权 API 封装
"""

from typing import Dict, Any
from eth_account import Account
from framework.web3 import Web3Client, WalletSigner
from framework.core.logger import logger


class WalletAPI:
    """钱包签名和授权 API 封装"""

    def __init__(self, web3_client: Web3Client, contract_address: str, abi: list):
        """
        初始化 Wallet API

        Args:
            web3_client: Web3 客户端
            contract_address: 合约地址
            abi: 合约 ABI
        """
        self.client = web3_client
        self.contract = web3_client.load_contract(contract_address, abi)
        self.address = contract_address
        logger.info(f"Wallet API 已初始化: {contract_address}")

    def name(self) -> str:
        """获取代币名称"""
        return self.client.call_contract_function(self.contract, "name")

    def nonces(self, address: str) -> int:
        """获取地址的 nonce"""
        return self.client.call_contract_function(self.contract, "nonces", address)

    def allowance(self, owner: str, spender: str) -> int:
        """获取授权额度"""
        return self.client.call_contract_function(self.contract, "allowance", owner, spender)

    def balance_of(self, address: str) -> int:
        """获取余额"""
        return self.client.call_contract_function(self.contract, "balanceOf", address)

    def approve(self, spender: str, amount: int, from_account: Account) -> str:
        """
        授权

        Args:
            spender: 被授权地址
            amount: 授权数量
            from_account: 授权账户

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

    def transfer(self, to: str, amount: int, from_account: Account) -> str:
        """
        转账

        Args:
            to: 接收地址
            amount: 转账数量
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

    def transfer_from(self, from_addr: str, to: str, amount: int, from_account: Account) -> str:
        """
        从授权地址转账

        Args:
            from_addr: 源地址
            to: 目标地址
            amount: 转账数量
            from_account: 执行账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "transferFrom",
            from_account,
            from_addr,
            to,
            amount
        )

    def permit(
        self,
        owner: str,
        spender: str,
        value: int,
        deadline: int,
        v: int,
        r: bytes,
        s: bytes,
        from_account: Account
    ) -> str:
        """
        使用签名授权 (EIP-2612)

        Args:
            owner: 所有者地址
            spender: 被授权地址
            value: 授权数量
            deadline: 截止时间
            v: 签名 v
            r: 签名 r
            s: 签名 s
            from_account: 执行账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "permit",
            from_account,
            owner,
            spender,
            value,
            deadline,
            v,
            r,
            s
        )

    def generate_permit_signature(
        self,
        owner_account: Account,
        spender: str,
        value: int,
        deadline: int,
        chain_id: int = 31337
    ) -> Dict[str, Any]:
        """
        生成 Permit 签名

        Args:
            owner_account: 所有者账户
            spender: 被授权地址
            value: 授权数量
            deadline: 截止时间
            chain_id: 链 ID

        Returns:
            签名数据 {v, r, s, signature}
        """
        signer = WalletSigner(owner_account)
        nonce = self.nonces(owner_account.address)

        return signer.sign_permit(
            token_address=self.address,
            token_name=self.name(),
            owner=owner_account.address,
            spender=spender,
            value=value,
            nonce=nonce,
            deadline=deadline,
            chain_id=chain_id
        )

    def sign_personal_message(self, account: Account, message: str) -> Dict[str, Any]:
        """
        签名个人消息

        Args:
            account: 签名账户
            message: 消息内容

        Returns:
            签名数据
        """
        signer = WalletSigner(account)
        return signer.sign_personal_message(message)

    def sign_typed_data(self, account: Account, typed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        签名结构化数据 (EIP-712)

        Args:
            account: 签名账户
            typed_data: 结构化数据

        Returns:
            签名数据
        """
        signer = WalletSigner(account)
        return signer.sign_typed_data(typed_data)

    def recover_signer(self, message: str, signature: str) -> str:
        """
        从签名恢复签名者地址

        Args:
            message: 原始消息
            signature: 签名

        Returns:
            签名者地址
        """
        signer = WalletSigner(Account.create())
        return signer.recover_signer(message, signature)
