#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : nft_contract_api.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : NFT 合约 API 封装
"""

from typing import Dict, Any, Optional
from eth_account import Account
from framework.web3 import Web3Client
from framework.core.logger import logger


class NFTContractAPI:
    """NFT 合约 API 封装"""

    def __init__(self, web3_client: Web3Client, contract_address: str, abi: list):
        """
        初始化 NFT 合约 API

        Args:
            web3_client: Web3 客户端
            contract_address: 合约地址
            abi: 合约 ABI
        """
        self.client = web3_client
        self.contract = web3_client.load_contract(contract_address, abi)
        self.address = contract_address
        logger.info(f"NFT 合约 API 已初始化: {contract_address}")

    def name(self) -> str:
        """获取 NFT 名称"""
        return self.client.call_contract_function(self.contract, "name")

    def symbol(self) -> str:
        """获取 NFT 符号"""
        return self.client.call_contract_function(self.contract, "symbol")

    def total_supply(self) -> int:
        """获取总供应量"""
        return self.client.call_contract_function(self.contract, "totalSupply")

    def max_supply(self) -> int:
        """获取最大供应量"""
        return self.client.call_contract_function(self.contract, "maxSupply")

    def mint_price(self) -> int:
        """获取 Mint 价格（Wei）"""
        return self.client.call_contract_function(self.contract, "mintPrice")

    def paused(self) -> bool:
        """获取暂停状态"""
        return self.client.call_contract_function(self.contract, "paused")

    def owner(self) -> str:
        """获取合约所有者"""
        return self.client.call_contract_function(self.contract, "owner")

    def balance_of(self, address: str) -> int:
        """
        获取地址的 NFT 数量

        Args:
            address: 地址

        Returns:
            NFT 数量
        """
        return self.client.call_contract_function(self.contract, "balanceOf", address)

    def owner_of(self, token_id: int) -> str:
        """
        获取 NFT 所有者

        Args:
            token_id: Token ID

        Returns:
            所有者地址
        """
        return self.client.call_contract_function(self.contract, "ownerOf", token_id)

    def token_uri(self, token_id: int) -> str:
        """
        获取 Token URI

        Args:
            token_id: Token ID

        Returns:
            Token URI
        """
        return self.client.call_contract_function(self.contract, "tokenURI", token_id)

    def mint(
        self,
        to: str,
        uri: str,
        from_account: Account,
        value: Optional[int] = None
    ) -> str:
        """
        Mint NFT

        Args:
            to: 接收地址
            uri: Token URI
            from_account: 发送账户
            value: 支付金额（Wei），如果不提供则使用 mintPrice

        Returns:
            交易哈希
        """
        if value is None:
            value = self.mint_price()

        return self.client.send_contract_transaction(
            self.contract,
            "mint",
            from_account,
            to,
            uri,
            value=value
        )

    def owner_mint(
        self,
        to: str,
        uri: str,
        from_account: Account
    ) -> str:
        """
        Owner Mint（免费）

        Args:
            to: 接收地址
            uri: Token URI
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "ownerMint",
            from_account,
            to,
            uri
        )

    def set_paused(self, paused: bool, from_account: Account) -> str:
        """
        设置暂停状态

        Args:
            paused: 是否暂停
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "setPaused",
            from_account,
            paused
        )

    def set_mint_price(self, price: int, from_account: Account) -> str:
        """
        设置 Mint 价格

        Args:
            price: 价格（Wei）
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "setMintPrice",
            from_account,
            price
        )

    def withdraw(self, from_account: Account) -> str:
        """
        提现合约余额

        Args:
            from_account: Owner 账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "withdraw",
            from_account
        )

    def transfer_from(
        self,
        from_address: str,
        to_address: str,
        token_id: int,
        from_account: Account
    ) -> str:
        """
        转移 NFT

        Args:
            from_address: 发送地址
            to_address: 接收地址
            token_id: Token ID
            from_account: 签名账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "transferFrom",
            from_account,
            from_address,
            to_address,
            token_id
        )

    def approve(
        self,
        to: str,
        token_id: int,
        from_account: Account
    ) -> str:
        """
        授权 NFT

        Args:
            to: 授权地址
            token_id: Token ID
            from_account: 所有者账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "approve",
            from_account,
            to,
            token_id
        )

    def get_approved(self, token_id: int) -> str:
        """
        获取授权地址

        Args:
            token_id: Token ID

        Returns:
            授权地址
        """
        return self.client.call_contract_function(self.contract, "getApproved", token_id)

    def set_approval_for_all(
        self,
        operator: str,
        approved: bool,
        from_account: Account
    ) -> str:
        """
        设置操作员授权

        Args:
            operator: 操作员地址
            approved: 是否授权
            from_account: 所有者账户

        Returns:
            交易哈希
        """
        return self.client.send_contract_transaction(
            self.contract,
            "setApprovalForAll",
            from_account,
            operator,
            approved
        )

    def is_approved_for_all(self, owner: str, operator: str) -> bool:
        """
        检查操作员授权

        Args:
            owner: 所有者地址
            operator: 操作员地址

        Returns:
            是否已授权
        """
        return self.client.call_contract_function(
            self.contract,
            "isApprovedForAll",
            owner,
            operator
        )
