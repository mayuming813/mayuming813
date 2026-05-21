#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : nft_rpc.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : NFT RPC 调用封装
"""

from typing import Dict, Any, Optional
from framework.web3 import RPCClient
from framework.core.logger import logger


class NFTRPC:
    """NFT RPC 调用封装"""

    def __init__(self, rpc_client: RPCClient):
        """
        初始化 NFT RPC

        Args:
            rpc_client: RPC 客户端
        """
        self.client = rpc_client
        logger.info("NFT RPC 已初始化")

    def get_nft_balance(self, contract_address: str, owner_address: str, block: str = "latest") -> Dict:
        """
        获取 NFT 余额

        Args:
            contract_address: 合约地址
            owner_address: 所有者地址
            block: 区块标识

        Returns:
            RPC 响应
        """
        # balanceOf(address) 的函数签名
        function_signature = "0x70a08231"
        # 编码参数：地址需要填充到 32 字节
        padded_address = owner_address[2:].zfill(64)
        data = function_signature + padded_address

        return self.client.eth_call({
            "to": contract_address,
            "data": data
        }, block)

    def get_nft_owner(self, contract_address: str, token_id: int, block: str = "latest") -> Dict:
        """
        获取 NFT 所有者

        Args:
            contract_address: 合约地址
            token_id: Token ID
            block: 区块标识

        Returns:
            RPC 响应
        """
        # ownerOf(uint256) 的函数签名
        function_signature = "0x6352211e"
        # 编码参数：uint256 需要填充到 32 字节
        padded_token_id = hex(token_id)[2:].zfill(64)
        data = function_signature + padded_token_id

        return self.client.eth_call({
            "to": contract_address,
            "data": data
        }, block)

    def get_token_uri(self, contract_address: str, token_id: int, block: str = "latest") -> Dict:
        """
        获取 Token URI

        Args:
            contract_address: 合约地址
            token_id: Token ID
            block: 区块标识

        Returns:
            RPC 响应
        """
        # tokenURI(uint256) 的函数签名
        function_signature = "0xc87b56dd"
        padded_token_id = hex(token_id)[2:].zfill(64)
        data = function_signature + padded_token_id

        return self.client.eth_call({
            "to": contract_address,
            "data": data
        }, block)

    def get_total_supply(self, contract_address: str, block: str = "latest") -> Dict:
        """
        获取总供应量

        Args:
            contract_address: 合约地址
            block: 区块标识

        Returns:
            RPC 响应
        """
        # totalSupply() 的函数签名
        function_signature = "0x18160ddd"

        return self.client.eth_call({
            "to": contract_address,
            "data": function_signature
        }, block)

    def get_mint_price(self, contract_address: str, block: str = "latest") -> Dict:
        """
        获取 Mint 价格

        Args:
            contract_address: 合约地址
            block: 区块标识

        Returns:
            RPC 响应
        """
        # mintPrice() 的函数签名
        function_signature = "0x6817c76c"

        return self.client.eth_call({
            "to": contract_address,
            "data": function_signature
        }, block)

    def get_nft_transfer_events(
        self,
        contract_address: str,
        from_block: str = "earliest",
        to_block: str = "latest",
        from_address: Optional[str] = None,
        to_address: Optional[str] = None,
        token_id: Optional[int] = None
    ) -> Dict:
        """
        获取 NFT Transfer 事件

        Args:
            contract_address: 合约地址
            from_block: 起始区块
            to_block: 结束区块
            from_address: 发送地址（可选）
            to_address: 接收地址（可选）
            token_id: Token ID（可选）

        Returns:
            RPC 响应
        """
        # Transfer(address,address,uint256) 事件签名
        event_signature = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"

        topics = [event_signature]

        # 添加 from 地址过滤
        if from_address:
            topics.append("0x" + from_address[2:].zfill(64))
        else:
            topics.append(None)

        # 添加 to 地址过滤
        if to_address:
            topics.append("0x" + to_address[2:].zfill(64))
        else:
            topics.append(None)

        # 添加 token_id 过滤
        if token_id is not None:
            topics.append("0x" + hex(token_id)[2:].zfill(64))

        filter_params = {
            "address": contract_address,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": topics
        }

        return self.client.eth_get_logs(filter_params)

    def get_nft_minted_events(
        self,
        contract_address: str,
        from_block: str = "earliest",
        to_block: str = "latest"
    ) -> Dict:
        """
        获取 NFT Minted 事件

        Args:
            contract_address: 合约地址
            from_block: 起始区块
            to_block: 结束区块

        Returns:
            RPC 响应
        """
        # NFTMinted(address,uint256,string) 事件签名
        # 需要根据实际合约的事件签名计算
        event_signature = "0x" + "0" * 64  # 占位符，实际需要计算

        filter_params = {
            "address": contract_address,
            "fromBlock": from_block,
            "toBlock": to_block,
            "topics": [event_signature]
        }

        return self.client.eth_get_logs(filter_params)

    def estimate_mint_gas(
        self,
        contract_address: str,
        from_address: str,
        to_address: str,
        uri: str,
        value: int
    ) -> Dict:
        """
        估算 Mint Gas

        Args:
            contract_address: 合约地址
            from_address: 发送地址
            to_address: 接收地址
            uri: Token URI
            value: 支付金额

        Returns:
            RPC 响应
        """
        # mint(address,string) 的函数签名
        function_signature = "0xd0def521"

        # 编码参数（简化版，实际需要完整的 ABI 编码）
        # 这里仅作示例
        data = function_signature

        return self.client.eth_estimate_gas({
            "from": from_address,
            "to": contract_address,
            "value": hex(value),
            "data": data
        })

    def get_transaction_by_hash(self, tx_hash: str) -> Dict:
        """
        获取交易信息

        Args:
            tx_hash: 交易哈希

        Returns:
            RPC 响应
        """
        return self.client.eth_get_transaction_by_hash(tx_hash)

    def get_transaction_receipt(self, tx_hash: str) -> Dict:
        """
        获取交易回执

        Args:
            tx_hash: 交易哈希

        Returns:
            RPC 响应
        """
        return self.client.eth_get_transaction_receipt(tx_hash)
