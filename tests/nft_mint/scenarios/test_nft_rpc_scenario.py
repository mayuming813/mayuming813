#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_nft_rpc_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : NFT RPC 场景测试
"""

import pytest
import allure


@allure.feature("NFT Mint")
@allure.story("NFT RPC 调用")
class TestNFTRPCScenario:
    """NFT RPC 调用测试"""

    @allure.title("场景：通过 RPC 查询 NFT 余额")
    def test_query_nft_balance_via_rpc_scenario(self, nft_rpc, nft_contract_deployed, minted_nft):
        """场景：使用 RPC 查询 NFT 余额"""
        with allure.step("调用 RPC 查询余额"):
            response = nft_rpc.get_nft_balance(
                nft_contract_deployed['address'],
                minted_nft['owner']
            )

        with allure.step("验证 RPC 响应"):
            assert 'result' in response, "RPC 响应缺少 result"
            assert 'error' not in response, f"RPC 返回错误: {response.get('error')}"

        with allure.step("验证余额"):
            balance = int(response['result'], 16)
            assert balance >= 1, f"余额不正确: {balance}"

    @allure.title("场景：通过 RPC 查询 NFT 所有者")
    def test_query_nft_owner_via_rpc_scenario(self, nft_rpc, nft_contract_deployed, minted_nft):
        """场景：使用 RPC 查询 NFT 所有者"""
        with allure.step("调用 RPC 查询所有者"):
            response = nft_rpc.get_nft_owner(
                nft_contract_deployed['address'],
                minted_nft['token_id']
            )

        with allure.step("验证 RPC 响应"):
            assert 'result' in response, "RPC 响应缺少 result"
            assert 'error' not in response, f"RPC 返回错误: {response.get('error')}"

        with allure.step("验证所有者地址"):
            # 结果是 32 字节的十六进制，地址在最后 20 字节
            owner_hex = response['result']
            owner_address = "0x" + owner_hex[-40:]
            assert owner_address.lower() == minted_nft['owner'].lower(), "所有者地址不匹配"

    @allure.title("场景：通过 RPC 查询总供应量")
    def test_query_total_supply_via_rpc_scenario(self, nft_rpc, nft_contract_deployed, minted_nft):
        """场景：使用 RPC 查询总供应量"""
        with allure.step("调用 RPC 查询总供应量"):
            response = nft_rpc.get_total_supply(nft_contract_deployed['address'])

        with allure.step("验证 RPC 响应"):
            assert 'result' in response, "RPC 响应缺少 result"
            assert 'error' not in response, f"RPC 返回错误: {response.get('error')}"

        with allure.step("验证总供应量"):
            total_supply = int(response['result'], 16)
            assert total_supply >= 1, f"总供应量不正确: {total_supply}"

    @allure.title("场景：通过 RPC 查询 Transfer 事件")
    def test_query_transfer_events_via_rpc_scenario(self, nft_rpc, nft_contract_deployed, minted_nft):
        """场景：使用 RPC 查询 Transfer 事件"""
        with allure.step("调用 RPC 查询 Transfer 事件"):
            response = nft_rpc.get_nft_transfer_events(
                nft_contract_deployed['address'],
                from_block="0x0",
                to_block="latest"
            )

        with allure.step("验证 RPC 响应"):
            assert 'result' in response, "RPC 响应缺少 result"
            assert 'error' not in response, f"RPC 返回错误: {response.get('error')}"

        with allure.step("验证事件数量"):
            events = response['result']
            assert len(events) >= 1, "未找到 Transfer 事件"

    @allure.title("场景：通过 RPC 查询交易回执")
    def test_query_transaction_receipt_via_rpc_scenario(self, nft_rpc, minted_nft):
        """场景：使用 RPC 查询交易回执"""
        with allure.step("调用 RPC 查询交易回执"):
            response = nft_rpc.get_transaction_receipt(minted_nft['tx_hash'])

        with allure.step("验证 RPC 响应"):
            assert 'result' in response, "RPC 响应缺少 result"
            assert 'error' not in response, f"RPC 返回错误: {response.get('error')}"

        with allure.step("验证交易状态"):
            receipt = response['result']
            assert receipt is not None, "交易回执为空"
            assert receipt['status'] == '0x1', "交易失败"
