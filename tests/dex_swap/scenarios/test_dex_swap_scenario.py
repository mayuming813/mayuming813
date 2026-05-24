#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@File    : test_dex_swap_scenario.py
@Author  : mayuming
@Project : web3-auto-test
@Desc    : DEX Swap 场景测试
"""

import pytest
import allure


@allure.feature("DEX Swap")
@allure.story("流动性池管理")
class TestDEXPoolScenario:
    """流动性池管理测试"""

    @allure.title("场景：创建流动性池")
    def test_create_pool_scenario(self, pool_created, dex_api):
        """场景：创建流动性池"""
        with allure.step("验证流动性池信息"):
            pool = dex_api.get_pool(pool_created['pool_id'])
            assert pool['tokenA'].lower() == pool_created['token_a'].lower() or \
                   pool['tokenA'].lower() == pool_created['token_b'].lower(), "Token A 不匹配"
            assert pool['tokenB'].lower() == pool_created['token_a'].lower() or \
                   pool['tokenB'].lower() == pool_created['token_b'].lower(), "Token B 不匹配"
            assert pool['reserveA'] == 0, "初始储备 A 应为 0"
            assert pool['reserveB'] == 0, "初始储备 B 应为 0"
            assert pool['totalLiquidity'] == 0, "初始流动性应为 0"

    @allure.title("场景：添加流动性")
    def test_add_liquidity_scenario(self, liquidity_added, dex_api):
        """场景：添加流动性到池子"""
        with allure.step("验证流动性池储备"):
            pool = dex_api.get_pool(liquidity_added['pool_id'])
            assert pool['reserveA'] > 0, "储备 A 应大于 0"
            assert pool['reserveB'] > 0, "储备 B 应大于 0"
            assert pool['totalLiquidity'] > 0, "总流动性应大于 0"

        with allure.step("验证用户流动性余额"):
            liquidity = dex_api.get_liquidity_balance(
                liquidity_added['pool_id'],
                liquidity_added['provider']
            )
            assert liquidity == liquidity_added['liquidity'], "流动性余额不匹配"

    @allure.title("场景：移除流动性")
    def test_remove_liquidity_scenario(
        self,
        liquidity_added,
        dex_api,
        token_a_api,
        token_b_api,
        user1,
        web3_client
    ):
        """场景：从池子移除流动性"""
        liquidity_to_remove = liquidity_added['liquidity'] // 2

        with allure.step("记录移除前余额"):
            balance_a_before = token_a_api.balance_of(user1.address)
            balance_b_before = token_b_api.balance_of(user1.address)

        with allure.step("移除流动性"):
            tx_hash = dex_api.remove_liquidity(
                liquidity_added['token_a'],
                liquidity_added['token_b'],
                liquidity_to_remove,
                user1
            )
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "移除流动性失败"

        with allure.step("验证余额增加"):
            balance_a_after = token_a_api.balance_of(user1.address)
            balance_b_after = token_b_api.balance_of(user1.address)
            assert balance_a_after > balance_a_before, "Token A 余额未增加"
            assert balance_b_after > balance_b_before, "Token B 余额未增加"

        with allure.step("验证流动性余额减少"):
            liquidity_after = dex_api.get_liquidity_balance(
                liquidity_added['pool_id'],
                user1.address
            )
            assert liquidity_after == liquidity_added['liquidity'] - liquidity_to_remove, \
                "流动性余额未正确减少"


@allure.feature("DEX Swap")
@allure.story("Swap 交易")
class TestDEXSwapScenario:
    """Swap 交易测试"""

    @allure.title("场景：Swap Token A 到 Token B")
    def test_swap_a_to_b_scenario(
        self,
        liquidity_added,
        dex_api,
        token_a_api,
        token_b_api,
        user2,
        user2_tokens_approved,
        tokens_minted,
        web3_client
    ):
        """场景：用户 Swap Token A 换取 Token B"""
        swap_amount = web3_client.to_wei(100, 'ether')

        with allure.step("计算预期输出"):
            expected_output = dex_api.get_amount_out(
                token_a_api.address,
                token_b_api.address,
                swap_amount
            )
            assert expected_output > 0, "预期输出应大于 0"

        with allure.step("记录 Swap 前余额"):
            balance_a_before = token_a_api.balance_of(user2.address)
            balance_b_before = token_b_api.balance_of(user2.address)

        with allure.step("执行 Swap"):
            min_output = int(expected_output * 0.95)  # 5% 滑点保护
            tx_hash = dex_api.swap(
                token_a_api.address,
                token_b_api.address,
                swap_amount,
                min_output,
                user2
            )
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "Swap 失败"

        with allure.step("验证余额变化"):
            balance_a_after = token_a_api.balance_of(user2.address)
            balance_b_after = token_b_api.balance_of(user2.address)

            assert balance_a_after == balance_a_before - swap_amount, "Token A 余额变化不正确"
            assert balance_b_after > balance_b_before, "Token B 余额未增加"

            actual_output = balance_b_after - balance_b_before
            assert actual_output >= min_output, "实际输出低于最小输出"

    @allure.title("场景：Swap Token B 到 Token A")
    def test_swap_b_to_a_scenario(
        self,
        liquidity_added,
        dex_api,
        token_a_api,
        token_b_api,
        user2,
        user2_tokens_approved,
        tokens_minted,
        web3_client
    ):
        """场景：用户 Swap Token B 换取 Token A"""
        swap_amount = web3_client.to_wei(200, 'ether')

        with allure.step("计算预期输出"):
            expected_output = dex_api.get_amount_out(
                token_b_api.address,
                token_a_api.address,
                swap_amount
            )
            assert expected_output > 0, "预期输出应大于 0"

        with allure.step("记录 Swap 前余额"):
            balance_a_before = token_a_api.balance_of(user2.address)
            balance_b_before = token_b_api.balance_of(user2.address)

        with allure.step("执行 Swap"):
            min_output = int(expected_output * 0.95)
            tx_hash = dex_api.swap(
                token_b_api.address,
                token_a_api.address,
                swap_amount,
                min_output,
                user2
            )
            receipt = web3_client.wait_for_transaction_receipt(tx_hash)
            assert receipt['status'] == 1, "Swap 失败"

        with allure.step("验证余额变化"):
            balance_a_after = token_a_api.balance_of(user2.address)
            balance_b_after = token_b_api.balance_of(user2.address)

            assert balance_b_after == balance_b_before - swap_amount, "Token B 余额变化不正确"
            assert balance_a_after > balance_a_before, "Token A 余额未增加"

    @allure.title("场景：多次 Swap 验证价格影响")
    def test_multiple_swaps_price_impact_scenario(
        self,
        liquidity_added,
        dex_api,
        token_a_api,
        token_b_api,
        user2,
        user2_tokens_approved,
        tokens_minted,
        web3_client
    ):
        """场景：多次 Swap 验证价格影响"""
        swap_amount = web3_client.to_wei(50, 'ether')

        with allure.step("第一次 Swap"):
            output1 = dex_api.get_amount_out(
                token_a_api.address,
                token_b_api.address,
                swap_amount
            )
            tx_hash = dex_api.swap(
                token_a_api.address,
                token_b_api.address,
                swap_amount,
                0,
                user2
            )
            web3_client.wait_for_transaction_receipt(tx_hash)

        with allure.step("第二次 Swap（相同输入）"):
            output2 = dex_api.get_amount_out(
                token_a_api.address,
                token_b_api.address,
                swap_amount
            )
            tx_hash = dex_api.swap(
                token_a_api.address,
                token_b_api.address,
                swap_amount,
                0,
                user2
            )
            web3_client.wait_for_transaction_receipt(tx_hash)

        with allure.step("验证价格影响"):
            assert output2 < output1, "第二次 Swap 输出应小于第一次（价格影响）"


@allure.feature("DEX Swap")
@allure.story("滑点保护")
class TestDEXSlippageScenario:
    """滑点保护测试"""

    @allure.title("场景：滑点过高导致交易失败")
    def test_slippage_protection_scenario(
        self,
        liquidity_added,
        dex_api,
        token_a_api,
        token_b_api,
        user2,
        user2_tokens_approved,
        tokens_minted,
        web3_client
    ):
        """场景：设置过高的最小输出导致交易失败"""
        swap_amount = web3_client.to_wei(100, 'ether')

        with allure.step("计算预期输出"):
            expected_output = dex_api.get_amount_out(
                token_a_api.address,
                token_b_api.address,
                swap_amount
            )

        with allure.step("设置过高的最小输出"):
            min_output = int(expected_output * 1.5)  # 要求 150% 的输出（不可能）

        with allure.step("执行 Swap（应失败）"):
            try:
                tx_hash = dex_api.swap(
                    token_a_api.address,
                    token_b_api.address,
                    swap_amount,
                    min_output,
                    user2
                )
                receipt = web3_client.wait_for_transaction_receipt(tx_hash)
                assert receipt['status'] == 0, "交易应该失败"
            except Exception as e:
                assert "slippage" in str(e).lower() or "revert" in str(e).lower(), \
                    "应该因滑点过高而失败"


@allure.feature("DEX Swap")
@allure.story("价格计算")
class TestDEXPriceCalculationScenario:
    """价格计算测试"""

    @allure.title("场景：验证价格计算准确性")
    def test_price_calculation_scenario(self, liquidity_added, dex_api, web3_client):
        """场景：验证 getAmountOut 计算准确性"""
        test_amounts = [
            web3_client.to_wei(10, 'ether'),
            web3_client.to_wei(50, 'ether'),
            web3_client.to_wei(100, 'ether'),
        ]

        for amount in test_amounts:
            with allure.step(f"计算 {web3_client.from_wei(amount, 'ether')} Token A 的输出"):
                output = dex_api.get_amount_out(
                    liquidity_added['token_a'],
                    liquidity_added['token_b'],
                    amount
                )

                # 验证输出大于 0
                assert output > 0, f"输出应大于 0: {output}"

                # 验证输出小于输入（考虑手续费）
                pool = dex_api.get_pool(liquidity_added['pool_id'])
                reserve_ratio = pool['reserveB'] / pool['reserveA']
                expected_max = int(amount * reserve_ratio)
                assert output < expected_max, "输出应小于理论最大值（考虑手续费）"
