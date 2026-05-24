#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_data_consistency.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""

import pytest
import allure
import requests
from framework.fixtures.common import *
from framework.fixtures.contracts import *
from framework.core.config import config


@allure.feature("数据一致性")
@allure.story("链上与后端数据对比")
class TestDataConsistency:
    """数据一致性测试"""

    @allure.title("测试用户余额一致性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_balance_consistency(self, w3, token_contract, user1_account, test_logger):
        """验证链上余额与后端数据库余额一致"""
        # 1. 从链上获取余额
        onchain_balance = token_contract.functions.balanceOf(user1_account.address).call()
        test_logger.info(f"链上余额: {onchain_balance}")

        # 2. 从后端 API 获取余额
        base_url = config.backend_api_url
        response = requests.get(
            f"{base_url}/api/user/balance",
            params={'address': user1_account.address}
        )
        assert response.status_code == 200, "后端接口调用失败"

        backend_balance = response.json()['data']['balance']
        test_logger.info(f"后端余额: {backend_balance}")

        # 3. 对比数据
        assert onchain_balance == int(backend_balance), \
            f"余额不一致: 链上 {onchain_balance}, 后端 {backend_balance}"

    @allure.title("测试交易记录一致性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_transaction_history_consistency(self, w3, user1_account, test_logger):
        """验证链上交易记录与后端数据库一致"""
        # 1. 从链上获取最近的交易
        latest_block = w3.eth.block_number
        transactions = []

        for block_num in range(max(0, latest_block - 100), latest_block + 1):
            block = w3.eth.get_block(block_num, full_transactions=True)
            for tx in block['transactions']:
                if tx['from'] == user1_account.address or tx['to'] == user1_account.address:
                    transactions.append(tx['hash'].hex())

        test_logger.info(f"链上交易数量: {len(transactions)}")

        # 2. 从后端 API 获取交易记录
        base_url = config.backend_api_url
        response = requests.get(
            f"{base_url}/api/user/transactions",
            params={'address': user1_account.address}
        )
        assert response.status_code == 200, "后端接口调用失败"

        backend_txs = [tx['hash'] for tx in response.json()['data']]
        test_logger.info(f"后端交易数量: {len(backend_txs)}")

        # 3. 对比交易哈希
        missing_in_backend = set(transactions) - set(backend_txs)
        extra_in_backend = set(backend_txs) - set(transactions)

        if missing_in_backend:
            test_logger.warning(f"后端缺失的交易: {missing_in_backend}")
        if extra_in_backend:
            test_logger.warning(f"后端多余的交易: {extra_in_backend}")

        assert len(missing_in_backend) == 0, f"后端缺失 {len(missing_in_backend)} 条交易"

    @allure.title("测试 NFT 所有权一致性")
    @allure.severity(allure.severity_level.CRITICAL)
    def test_nft_ownership_consistency(self, nft_contract, user1_account, test_logger):
        """验证链上 NFT 所有权与后端数据库一致"""
        nft_id = 1

        # 1. 从链上获取 NFT 所有者
        onchain_owner = nft_contract.functions.ownerOf(nft_id).call()
        test_logger.info(f"链上 NFT#{nft_id} 所有者: {onchain_owner}")

        # 2. 从后端 API 获取 NFT 所有者
        base_url = config.backend_api_url
        response = requests.get(
            f"{base_url}/api/nft/{nft_id}/owner"
        )
        assert response.status_code == 200, "后端接口调用失败"

        backend_owner = response.json()['data']['owner']
        test_logger.info(f"后端 NFT#{nft_id} 所有者: {backend_owner}")

        # 3. 对比数据
        assert onchain_owner.lower() == backend_owner.lower(), \
            f"NFT 所有权不一致: 链上 {onchain_owner}, 后端 {backend_owner}"
