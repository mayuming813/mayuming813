#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_contract_interaction.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : 
"""
import pytest
import allure
from framework.fixtures.common import *
from framework.fixtures.contracts import *
from framework.utils.transaction_helper import TransactionHelper
from framework.utils.data_loader import DataLoader

@allure.feature("合约集成")
@allure.story("Token 与 NFT 交互")
class TestContractIntegration:
    """合约集成测试"""

    @allure.title("测试使用 Token 购买 NFT")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.parametrize("test_case", DataLoader.get_test_data("integration/nft_purchase.json"))
    def test_purchase_nft_with_token(self, w3, token_contract, nft_contract, user1_account, test_case, snapshot, test_logger):
        """使用 Token 购买 NFT"""
        token_amount = w3.to_wei(test_case['token_amount'], 'ether')
        nft_id = test_case['nft_id']

        test_logger.info(f"测试用例: {test_case['description']}")

        # 1. 授权 NFT 合约使用 Token
        receipt = TransactionHelper.call_contract_function(
            token_contract,
            'approve',
            user1_account,
            nft_contract.address,
            token_amount
        )
        assert receipt['status'] == 1, "授权失败"

        # 2. 购买 NFT
        receipt = TransactionHelper.call_contract_function(
            nft_contract,
            'purchase',
            user1_account,
            nft_id
        )
        assert receipt['status'] == 1, "购买失败"

        # 3. 验证 NFT 所有权
        owner = nft_contract.functions.ownerOf(nft_id).call()
        assert owner == user1_account.address, "NFT 所有权不正确"

        # 4. 验证事件
        logs = TransactionHelper.get_event_logs(w3, nft_contract, 'Transfer')
        assert len(logs) > 0, "Transfer 事件未触发"

        test_logger.info(f"测试通过: {test_case['description']}")