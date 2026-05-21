#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_nft_mint_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : NFT Mint 场景测试
"""

import pytest
import allure
from framework.utils.test_data_factory import TestDataFactory


@allure.feature("NFT Mint")
@allure.story("NFT 基础功能")
class TestNFTBasicScenario:
    """NFT 基础功能测试"""

    @allure.title("场景：查询 NFT 合约信息")
    def test_query_nft_info_scenario(self, nft_api, nft_contract_deployed):
        """场景：查询 NFT 合约基本信息"""
        with allure.step("查询合约名称"):
            name = nft_api.name()
            assert name == nft_contract_deployed['name'], f"名称不匹配: {name}"

        with allure.step("查询合约符号"):
            symbol = nft_api.symbol()
            assert symbol == nft_contract_deployed['symbol'], f"符号不匹配: {symbol}"

        with allure.step("查询最大供应量"):
            max_supply = nft_api.max_supply()
            assert max_supply == nft_contract_deployed['max_supply'], f"最大供应量不匹配: {max_supply}"

        with allure.step("查询 Mint 价格"):
            mint_price = nft_api.mint_price()
            assert mint_price == nft_contract_deployed['mint_price'], f"Mint 价格不匹配: {mint_price}"

        with allure.step("查询总供应量"):
            total_supply = nft_api.total_supply()
            assert total_supply >= 0, f"总供应量异常: {total_supply}"

    @allure.title("场景：用户 Mint NFT 成功")
    def test_user_mint_nft_scenario(self, minted_nft, nft_api):
        """场景：用户支付费用 Mint NFT"""
        with allure.step("验证 NFT 所有者"):
            owner = nft_api.owner_of(minted_nft['token_id'])
            assert owner.lower() == minted_nft['owner'].lower(), "所有者不匹配"

        with allure.step("验证 Token URI"):
            token_uri = nft_api.token_uri(minted_nft['token_id'])
            assert token_uri == minted_nft['token_uri'], "Token URI 不匹配"

        with allure.step("验证用户余额"):
            balance = nft_api.balance_of(minted_nft['owner'])
            assert balance >= 1, "用户 NFT 余额不正确"

    @allure.title("场景：Owner 免费 Mint NFT")
    def test_owner_mint_nft_scenario(self, nft_api, owner, user1, web3_client):
        """场景：Owner 免费 Mint NFT"""
        with allure.step("准备 Token URI"):
            token_uri = f"ipfs://QmOwnerMint{TestDataFactory.unique_id()}"

        with allure.step("Owner Mint NFT"):
            tx_hash = nft_api.owner_mint(user1.address, token_uri, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "Owner Mint 失败"

        with allure.step("验证 NFT 信息"):
            token_id = nft_api.total_supply() - 1
            nft_owner = nft_api.owner_of(token_id)
            assert nft_owner.lower() == user1.address.lower(), "所有者不匹配"

            uri = nft_api.token_uri(token_id)
            assert uri == token_uri, "Token URI 不匹配"


@allure.feature("NFT Mint")
@allure.story("NFT 转账功能")
class TestNFTTransferScenario:
    """NFT 转账功能测试"""

    @allure.title("场景：转移 NFT")
    def test_transfer_nft_scenario(self, nft_api, minted_nft, user1, user2, web3_client):
        """场景：NFT 所有者转移 NFT"""
        token_id = minted_nft['token_id']

        with allure.step("转移前验证所有者"):
            owner_before = nft_api.owner_of(token_id)
            assert owner_before.lower() == user1.address.lower()

        with allure.step("转移 NFT"):
            tx_hash = nft_api.transfer_from(user1.address, user2.address, token_id, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "转移失败"

        with allure.step("转移后验证所有者"):
            owner_after = nft_api.owner_of(token_id)
            assert owner_after.lower() == user2.address.lower(), "转移后所有者不正确"

        with allure.step("验证余额变化"):
            balance_user1 = nft_api.balance_of(user1.address)
            balance_user2 = nft_api.balance_of(user2.address)
            assert balance_user2 >= 1, "接收者余额未增加"

    @allure.title("场景：授权后转移 NFT")
    def test_transfer_approved_nft_scenario(self, nft_api, nft_with_approval, user2, web3_client):
        """场景：被授权者转移 NFT"""
        token_id = nft_with_approval['token_id']
        original_owner = nft_with_approval['owner']

        with allure.step("被授权者转移 NFT"):
            tx_hash = nft_api.transfer_from(original_owner, user2.address, token_id, user2)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "转移失败"

        with allure.step("验证新所有者"):
            new_owner = nft_api.owner_of(token_id)
            assert new_owner.lower() == user2.address.lower(), "转移后所有者不正确"


@allure.feature("NFT Mint")
@allure.story("NFT 授权功能")
class TestNFTApprovalScenario:
    """NFT 授权功能测试"""

    @allure.title("场景：授权单个 NFT")
    def test_approve_nft_scenario(self, nft_with_approval, nft_api):
        """场景：授权单个 NFT 给其他地址"""
        with allure.step("验证授权地址"):
            approved = nft_api.get_approved(nft_with_approval['token_id'])
            assert approved.lower() == nft_with_approval['approved_to'].lower(), "授权地址不匹配"

    @allure.title("场景：设置操作员授权")
    def test_set_approval_for_all_scenario(self, nft_api, user1, user2, web3_client):
        """场景：设置操作员授权"""
        with allure.step("设置操作员授权"):
            tx_hash = nft_api.set_approval_for_all(user2.address, True, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "设置授权失败"

        with allure.step("验证操作员授权"):
            is_approved = nft_api.is_approved_for_all(user1.address, user2.address)
            assert is_approved is True, "操作员未被授权"

        with allure.step("取消操作员授权"):
            tx_hash = nft_api.set_approval_for_all(user2.address, False, user1)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "取消授权失败"

        with allure.step("验证授权已取消"):
            is_approved = nft_api.is_approved_for_all(user1.address, user2.address)
            assert is_approved is False, "操作员授权未取消"


@allure.feature("NFT Mint")
@allure.story("NFT 管理功能")
class TestNFTManagementScenario:
    """NFT 管理功能测试"""

    @allure.title("场景：暂停和恢复 Mint")
    def test_pause_and_unpause_scenario(self, nft_api, owner, user1, web3_client):
        """场景：Owner 暂停和恢复 Mint 功能"""
        with allure.step("暂停 Mint"):
            tx_hash = nft_api.set_paused(True, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "暂停失败"

        with allure.step("验证暂停状态"):
            assert nft_api.paused() is True, "合约未暂停"

        with allure.step("尝试 Mint（应失败）"):
            token_uri = f"ipfs://QmTest{TestDataFactory.unique_id()}"
            mint_price = nft_api.mint_price()
            try:
                nft_api.mint(user1.address, token_uri, user1, value=mint_price)
                assert False, "暂停期间 Mint 应该失败"
            except Exception as e:
                assert "paused" in str(e).lower() or "revert" in str(e).lower()

        with allure.step("恢复 Mint"):
            tx_hash = nft_api.set_paused(False, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "恢复失败"

        with allure.step("验证恢复状态"):
            assert nft_api.paused() is False, "合约未恢复"

    @allure.title("场景：修改 Mint 价格")
    def test_change_mint_price_scenario(self, nft_api, owner, web3_client):
        """场景：Owner 修改 Mint 价格"""
        with allure.step("获取原始价格"):
            original_price = nft_api.mint_price()

        with allure.step("修改 Mint 价格"):
            new_price = web3_client.to_wei(0.02, 'ether')
            tx_hash = nft_api.set_mint_price(new_price, owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "修改价格失败"

        with allure.step("验证新价格"):
            current_price = nft_api.mint_price()
            assert current_price == new_price, f"价格未更新: {current_price}"

        with allure.step("恢复原始价格"):
            tx_hash = nft_api.set_mint_price(original_price, owner)
            web3_client.wait_for_transaction_receipt(tx_hash)

    @allure.title("场景：提现合约余额")
    def test_withdraw_scenario(self, nft_api, nft_contract_with_balance, owner, web3_client):
        """场景：Owner 提现合约余额"""
        contract_address = nft_contract_with_balance['contract_address']
        contract_balance = nft_contract_with_balance['balance']

        with allure.step("获取 Owner 提现前余额"):
            owner_balance_before = web3_client.get_balance(owner.address)

        with allure.step("提现合约余额"):
            tx_hash = nft_api.withdraw(owner)
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "提现失败"

        with allure.step("验证合约余额为 0"):
            contract_balance_after = web3_client.get_balance(contract_address)
            assert contract_balance_after == 0, "合约余额未清空"

        with allure.step("验证 Owner 余额增加"):
            owner_balance_after = web3_client.get_balance(owner.address)
            # 考虑 Gas 费用，余额应该有所增加（但不是完全等于合约余额）
            assert owner_balance_after > owner_balance_before - contract_balance, "Owner 余额未增加"


@allure.feature("NFT Mint")
@allure.story("NFT 批量操作")
class TestNFTBatchScenario:
    """NFT 批量操作测试"""

    @allure.title("场景：批量 Mint NFT")
    def test_batch_mint_scenario(self, multiple_minted_nfts, nft_api):
        """场景：多个用户批量 Mint NFT"""
        with allure.step("验证 Mint 数量"):
            assert len(multiple_minted_nfts) == 5, "Mint 数量不正确"

        with allure.step("验证每个 NFT 的所有权"):
            for nft in multiple_minted_nfts:
                owner = nft_api.owner_of(nft['token_id'])
                assert owner.lower() == nft['owner'].lower(), f"Token {nft['token_id']} 所有者不匹配"

        with allure.step("验证总供应量"):
            total_supply = nft_api.total_supply()
            assert total_supply >= 5, "总供应量不正确"
